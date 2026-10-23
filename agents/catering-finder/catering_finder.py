#!/usr/bin/env python3
"""Catering & Group Dining finder: the agent behind NEAR build job f2a6a33d (issue #75).

Takes an event brief (date, location, headcount, budget, dietary needs,
service style), reads the published pages of candidate vendors, keeps the
vendors whose own page verifies the service style and the area, extracts
menus, capacity and pricing from what each vendor publishes, drafts the
vendor questions (availability, menu, price, and the exact dietary needs
from the brief), and renders one comparison report.

Evidence rule (AGENT-BRIEF.md rule 3): every extracted value is a claim
printed with its source link and the raw page line it came from directly
beneath, verbatim. A value the page does not state is reported as not
published, never filled in.

Dietary rule (the bid proposal for job f2a6a33d, quoted on issue #75):
coverage is never inferred from silence. A vendor shows as covering a
dietary need only when
  confirmed      the vendor's own published material says so (page line quoted), or
  stated         the vendor answered the question (the recorded answer quoted, dated);
otherwise the row reads
  not confirmed  with the question's status: drafted and not sent, asked on a
                 date with no reply yet, or answered without addressing it.
"not confirmed" is the wording of the job's acceptance criterion 3.

Availability (acceptance criterion 4): a vendor shows as available for the
date only when its recorded answer says so; the report separates confirmed,
declined and not confirmed, and keeps vendors who did not reply or declined
(criterion 5). Prices, minimum spend, deposit and cancellation terms are
printed exactly as the vendor's page or answer states them, never totalled
or estimated (criterion 2); a price whose clause says "from" or "starting
at" is marked a starting point. The brief's budget per head is the buyer's
own number (budget divided by headcount) and is labelled so.

Outreach (issue #75 item 3, job rules): every draft says it is sent on
behalf of a customer by an automated assistant, asks only for a quote,
shares no buyer contact details, and tells the vendor they can ask us to
stop. This build drafts the questions and records them in an outreach
log. Nothing is sent by this program. Under a real hire the operator sends
each draft through the vendor's published channel and records the send and
the reply with `record-sent` and `record-reply` (`--stop` records a vendor
who asked not to be contacted again; no further draft is made for them);
the `send` command exists only to refuse without a hire id and an explicit
--execute, and no live transport is part of this build. The agent never
books, accepts a quote or pays a deposit.

Fail closed, as every tool in this repo does: a brief that does not
validate, a store that cannot be read, a page that is missing, or a log
entry for a vendor that is not in the run stops the program with the
failure on stderr and exit 2. No report is rendered from input that was
not understood.

Standard library only. Run from the repository root:

    python3 agents/catering-finder/catering_finder.py run \
        --brief agents/catering-finder/tests/fixtures/brief.json \
        --store agents/catering-finder/tests/fixtures \
        --log agents/catering-finder/tests/fixtures/outreach-log.json

    python3 agents/catering-finder/catering_finder.py draft --brief B --store S --log L
    python3 agents/catering-finder/catering_finder.py record-sent VENDOR --log L --when 2026-11-01T15:00:00Z
    python3 agents/catering-finder/catering_finder.py record-reply VENDOR --log L --when ... --text "..."
    python3 agents/catering-finder/catering_finder.py capture URL --store S --id VENDOR --name "..."

A store is a folder holding index.json (the candidate list), vendors/<id>.html
(each vendor's page as captured) and provenance.json (url, retrieval time and
sha256 per page). The fixture store under tests/fixtures is SYNTHETIC: every
page in it was written by hand for the tests and is labelled so in the file
and in provenance.json; `capture` builds a real store from live pages.
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

NOT_PUBLISHED = "not published on the vendor page"
USER_AGENT = "tiny-ledger catering-finder/0.1"
TIMEOUT_SECONDS = 30
HIRE_ENV = "CATERING_FINDER_HIRE_ID"

BRIEF_FIELDS = ("date", "location", "headcount", "budget_usd", "dietary_needs", "service_style")

# Service styles the finder recognises, with the phrases a vendor page may use.
# A page phrase outside this table is not a style match; the brief may still
# name a free text style, matched on that exact phrase.
SERVICE_STYLES = {
    "buffet": ("buffet",),
    "plated": ("plated", "seated dinner", "sit-down dinner", "sit down dinner"),
    "family style": ("family style", "family-style"),
    "drop-off": ("drop-off", "drop off", "drop-off catering", "drop off catering", "delivered trays"),
    "private dining room": ("private dining room", "private dining", "private room"),
    "food truck": ("food truck",),
    "boxed": ("boxed lunch", "boxed lunches", "boxed meals", "box lunch"),
}

# Dietary needs the finder recognises, with the phrases a vendor page or a
# vendor's answer may use to say it covers them. A need outside this table is
# matched on its own exact wording.
DIETARY_TERMS = {
    "vegan": ("vegan",),
    "vegetarian": ("vegetarian",),
    "gluten-free": ("gluten-free", "gluten free"),
    "dairy-free": ("dairy-free", "dairy free"),
    "nut-free": ("nut-free", "nut free", "nut allergy", "nut allergies", "no nuts", "peanut-free", "tree nut"),
    "halal": ("halal",),
    "kosher": ("kosher",),
}

CAPACITY_RE = re.compile(
    r"(?i)(?:up to|maximum of|max(?:imum)?|capacity of|serve(?:s)? up to|groups? of up to)\s+(\d{1,3}(?:,\d{3})*)\s+(?:guests|people|persons|diners)")
PRICE_RE = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per person|/person|per guest|/guest|per head|pp\b)", re.I)
MINIMUM_RE = re.compile(r"(?i)\bminimum\b")
DEPOSIT_RE = re.compile(r"(?i)\bdeposit\b")
CANCEL_RE = re.compile(r"(?i)\bcancel")
STARTING_RE = re.compile(r"(?i)\b(?:from|starts? at|starting at|starting)\b")
DECLINE_RE = re.compile(r"(?i)\b(?:not available|unavailable|fully booked|booked up|booked out|cannot|can't|unable to|no availability|decline)\b")
AVAILABLE_RE = re.compile(r"(?i)\b(?:available|we are open|we're open|open on|happy to|we can do|we can cater|can accommodate|yes)\b")
TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")
TAG_RE = re.compile(r"<[^>]+>")
NEGATION_RE = r"\b(?:no|not|without|never|except)\b[^.;]{0,40}?"


class ConfigError(Exception):
    """The input is not usable. Nothing was rendered."""


class FetchError(Exception):
    """A page or a store could not be read or understood. Nothing is concluded."""


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ----------------------------------------------------------------- brief

def canonical_need(need):
    """The table key for a dietary need, or the need's own wording when the table has no row."""
    text = " ".join(str(need).split()).casefold()
    for key, terms in DIETARY_TERMS.items():
        if text == key or any(term in text for term in terms):
            return key
    return text


def need_terms(need):
    key = canonical_need(need)
    return DIETARY_TERMS.get(key, (key,))


def canonical_style(style):
    text = " ".join(str(style).split()).casefold()
    for key, terms in SERVICE_STYLES.items():
        if text == key or text in terms:
            return key
    return text


def style_terms(style):
    key = canonical_style(style)
    return SERVICE_STYLES.get(key, (key,))


def load_brief(path):
    """Read and validate the event brief. Raises ConfigError on any gap."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ConfigError("brief %s could not be read as JSON: %s" % (path, err))
    return validate_brief(data)


def validate_brief(data):
    if not isinstance(data, dict):
        raise ConfigError("brief must be a JSON object")
    missing = [f for f in BRIEF_FIELDS if f not in data]
    if missing:
        raise ConfigError("brief is missing field(s): %s" % ", ".join(missing))
    date = data["date"]
    if not isinstance(date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ConfigError("brief date must be YYYY-MM-DD")
    try:
        time.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ConfigError("brief date %s is not a calendar date" % date)
    location = data["location"]
    if not isinstance(location, str) or not location.strip():
        raise ConfigError("brief location must be a non empty string")
    headcount = data["headcount"]
    if not isinstance(headcount, int) or isinstance(headcount, bool) or headcount < 1:
        raise ConfigError("brief headcount must be a positive integer")
    budget = data["budget_usd"]
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
        raise ConfigError("brief budget_usd must be a positive number")
    needs = data["dietary_needs"]
    if not isinstance(needs, list) or any(not isinstance(n, str) or not n.strip() for n in needs):
        raise ConfigError("brief dietary_needs must be a list of non empty strings (empty list allowed)")
    style = data["service_style"]
    if not isinstance(style, str) or not style.strip():
        raise ConfigError("brief service_style must be a non empty string")
    event_time = data.get("time")
    if event_time is not None and (not isinstance(event_time, str) or not re.fullmatch(r"[0-2]\d:[0-5]\d", event_time)):
        raise ConfigError("brief time, when given, must be HH:MM")
    deadline = data.get("response_deadline_utc")
    if deadline is not None and (not isinstance(deadline, str) or not TIMESTAMP_RE.fullmatch(deadline)):
        raise ConfigError("brief response_deadline_utc, when given, must be a UTC timestamp like 2026-11-10T17:00:00Z")
    return {
        "date": date,
        "time": event_time,
        "location": location.strip(),
        "headcount": headcount,
        "budget_usd": budget,
        "budget_per_head": budget / headcount,
        "dietary_needs": [" ".join(n.split()) for n in needs],
        "service_style": " ".join(style.split()),
        "response_deadline_utc": deadline,
    }


def location_tokens(location):
    """Place names from the brief location: 'Austin, TX' -> ['Austin', 'TX']."""
    return [t.strip() for t in re.split(r"[,;/]", location) if t.strip()]


# ----------------------------------------------------------------- store

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


class Page:
    def __init__(self, vendor_id, name, url, retrieved, raw, label):
        self.vendor_id = vendor_id
        self.name = name
        self.url = url
        self.retrieved = retrieved
        self.raw = raw            # the page as captured, text
        self.label = label        # provenance label, e.g. SYNTHETIC or captured
        self.lines = raw.splitlines()


def load_store(folder):
    """Read index.json, provenance.json and every vendor page. Raises FetchError.

    Every index entry needs id, name and url; every page needs a provenance
    entry whose sha256 matches the file bytes, so an edited capture is
    refused rather than quoted."""
    folder = Path(folder)
    try:
        index = json.loads((folder / "index.json").read_text(encoding="utf-8"))
        provenance = json.loads((folder / "provenance.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise FetchError("store %s: index.json or provenance.json could not be read as JSON: %s" % (folder, err))
    if not isinstance(index, dict) or not isinstance(index.get("vendors"), list):
        raise FetchError("store %s: index.json must hold a vendors list" % folder)
    pages = []
    seen = set()
    for entry in index["vendors"]:
        if not isinstance(entry, dict):
            raise FetchError("store %s: every index entry must be an object" % folder)
        vendor_id, name, url = entry.get("id"), entry.get("name"), entry.get("url")
        if not all(isinstance(v, str) and v.strip() for v in (vendor_id, name, url)):
            raise FetchError("store %s: index entry %r needs non empty id, name and url" % (folder, entry))
        if vendor_id in seen:
            raise FetchError("store %s: duplicate vendor id %s" % (folder, vendor_id))
        seen.add(vendor_id)
        rel = "vendors/%s.html" % vendor_id
        record = provenance.get(rel)
        if not isinstance(record, dict) or not isinstance(record.get("sha256"), str):
            raise FetchError("store %s: no provenance record with a sha256 for %s" % (folder, rel))
        try:
            data = (folder / rel).read_bytes()
        except OSError as err:
            raise FetchError("store %s: page %s is missing (%s)" % (folder, rel, err))
        if sha256_bytes(data) != record["sha256"].lower():
            raise FetchError("store %s: %s does not match its recorded sha256; refusing to quote an edited page" % (folder, rel))
        if record.get("url") != url:
            raise FetchError("store %s: %s provenance url %r differs from the index url %r" % (folder, rel, record.get("url"), url))
        pages.append(Page(vendor_id, name.strip(), url.strip(), str(record.get("retrieved_utc", "")),
                          data.decode("utf-8", "replace"), str(record.get("label", ""))))
    return {"source": index.get("source", {}), "pages": pages}


# ----------------------------------------------------------------- capture (live)

def fetch_page(url):
    """GET one page over HTTPS; return (status_line, headers list, body bytes). Raises FetchError."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise FetchError("only https URLs are captured; got %s" % url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return "HTTP %d %s" % (resp.status, resp.reason), list(resp.getheaders()), resp.read()
    except urllib.error.HTTPError as err:
        return "HTTP %d %s" % (err.code, err.reason), list(err.headers.items()), err.read()
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("transport failure for %s: %s" % (url, err))


def capture(url, store, vendor_id, name, fetcher=fetch_page):
    """Fetch a live vendor page into the store with provenance. Non 200 is refused."""
    store = Path(store)
    status, headers, body = fetcher(url)
    if not status.startswith("HTTP 200"):
        raise FetchError("%s answered %s; not stored" % (url, status))
    (store / "vendors").mkdir(parents=True, exist_ok=True)
    rel = "vendors/%s.html" % vendor_id
    (store / rel).write_bytes(body)
    retrieved = utc_now()
    index_path, prov_path = store / "index.json", store / "provenance.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"vendors": []}
    prov = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.exists() else {}
    index["vendors"] = [v for v in index.get("vendors", []) if v.get("id") != vendor_id]
    index["vendors"].append({"id": vendor_id, "name": name, "url": url})
    prov[rel] = {"url": url, "retrieved_utc": retrieved, "status_line": status,
                 "headers": ["%s: %s" % h for h in headers], "sha256": sha256_bytes(body),
                 "label": "captured live by catering_finder.py capture"}
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    prov_path.write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")
    return rel, retrieved


# ----------------------------------------------------------------- extraction

def plain(line):
    """A page line with tags removed and entities decoded, for matching only."""
    return " ".join(unescape(TAG_RE.sub(" ", line)).split())


class Claim:
    """One value read from a page: what it is, where, and the raw line beneath it."""

    def __init__(self, field, value, page, line_no):
        self.field = field
        self.value = value
        self.url = page.url
        self.line_no = line_no          # 1-based line in the captured page
        self.excerpt = page.lines[line_no - 1]

    def lines(self, label=None):
        """Markdown: the claim, the source link, the raw excerpt directly beneath."""
        head = "- %s as shown: %s" % (label or self.field, inline(self.value))
        return [head, "  Source: <%s> (line %d)" % (self.url, self.line_no), "  ```", "  " + self.excerpt, "  ```"]


def inline(value):
    text = json.dumps(value, ensure_ascii=False)
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", text)


def negated(text, term):
    """True when the term's mention on this line is denied: 'no buffet service', 'not vegan'."""
    return re.search(NEGATION_RE + re.escape(term), text) is not None


def find_line(page, terms):
    """(line_no, matched term) of the first page line that states any term, case folded, else None.

    A line that mentions the term only to deny it ("No buffet or table
    service") is not a match: the finder never reads a denial as coverage."""
    folded = [t.casefold() for t in terms]
    for no, line in enumerate(page.lines, 1):
        text = plain(line).casefold()
        for term in folded:
            if term and term in text and not negated(text, term):
                return no, term
    return None


def extract_style(page, style):
    hit = find_line(page, style_terms(style))
    return Claim("service style", plain(page.lines[hit[0] - 1]), page, hit[0]) if hit else None


def extract_area(page, location):
    """A page line naming the brief's place. Silence means unverified, not excluded as out of area."""
    for token in location_tokens(location):
        hit = find_line(page, (token,))
        if hit:
            return Claim("service area", plain(page.lines[hit[0] - 1]), page, hit[0])
    return None


def extract_capacity(page):
    for no, line in enumerate(page.lines, 1):
        m = CAPACITY_RE.search(plain(line))
        if m:
            return Claim("capacity", int(m.group(1).replace(",", "")), page, no)
    return None


def price_context(text, start):
    """The clause of a line a price sits in: the text between the nearest clause breaks."""
    left = max(text.rfind(ch, 0, start) for ch in (";", ".", ","))
    left = max(left, text.rfind(" and ", 0, start) + 4 if text.rfind(" and ", 0, start) >= 0 else -1)
    right_candidates = [i for i in (text.find(ch, start) for ch in (";", ".", ",")) if i >= 0]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1:right].strip()


def extract_prices(page):
    """Every per person price on the page, each with the clause it sits in and the
    service style that clause names, when it names one. A clause naming no
    style is kept with style None; the renderer never assigns one to it."""
    out = []
    for no, line in enumerate(page.lines, 1):
        text = plain(line)
        for m in PRICE_RE.finditer(text):
            claim = Claim("price per person (USD)", float(m.group(1).replace(",", "")), page, no)
            claim.context = price_context(text, m.start())
            claim.starting = STARTING_RE.search(claim.context) is not None
            claim.style = None
            for key, terms in SERVICE_STYLES.items():
                if any(t in claim.context.casefold() for t in (key,) + terms):
                    claim.style = key
                    break
            out.append(claim)
    return out


def prices_for_style(prices, style):
    """Prices whose clause names the brief's style; if no clause names any style, all of them."""
    key = canonical_style(style)
    tagged = [c for c in prices if c.style == key]
    if tagged:
        return tagged
    if any(c.style for c in prices):
        return []
    return prices


def extract_dietary(page, need):
    hit = find_line(page, need_terms(need))
    return Claim("dietary: %s" % canonical_need(need), plain(page.lines[hit[0] - 1]), page, hit[0]) if hit else None


def extract_terms(page):
    """Lines stating a minimum, a deposit or cancellation terms, as shown; empty when none."""
    out = []
    for no, line in enumerate(page.lines, 1):
        text = plain(line)
        # One label per line: a cancellation line that mentions the deposit is cancellation terms.
        if CANCEL_RE.search(text):
            out.append(Claim("cancellation terms", text, page, no))
        elif MINIMUM_RE.search(text):
            out.append(Claim("minimum spend or order", text, page, no))
        elif DEPOSIT_RE.search(text):
            out.append(Claim("deposit terms", text, page, no))
    return out


def extract_contact(page):
    for no, line in enumerate(page.lines, 1):
        text = plain(line)
        m = EMAIL_RE.search(text)
        if m:
            return Claim("contact channel", m.group(0), page, no)
    for no, line in enumerate(page.lines, 1):
        if "contact" in plain(line).casefold() and "href" in line:
            return Claim("contact channel", plain(line), page, no)
    for no, line in enumerate(page.lines, 1):
        m = PHONE_RE.search(plain(line))
        if m:
            return Claim("contact channel", m.group(0), page, no)
    return None


def extract_menu(page):
    """Lines under a heading that mentions menu, as shown, up to the next heading; empty when none."""
    claims, inside = [], False
    for no, line in enumerate(page.lines, 1):
        is_heading = bool(re.match(r"\s*<h[1-6]", line, re.I))
        if is_heading:
            inside = "menu" in plain(line).casefold()
            continue
        if inside and plain(line):
            claims.append(Claim("menu item", plain(line), page, no))
    return claims


# ----------------------------------------------------------------- outreach log

def load_log(path):
    if path is None:
        return {"hire_id": None, "drafts": {}}
    path = Path(path)
    if not path.exists():
        return {"hire_id": None, "drafts": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ConfigError("outreach log %s could not be read as JSON: %s" % (path, err))
    if not isinstance(data, dict) or not isinstance(data.get("drafts"), dict):
        raise ConfigError("outreach log %s must hold a drafts object" % path)
    return data


def save_log(path, log):
    Path(path).write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def draft_message(brief, page, unconfirmed_needs, contact):
    """The vendor question draft. Per the job rules it says it is on behalf of a
    customer and sent by an automated assistant, asks for a quote only, carries
    no buyer contact details, and invites the vendor to ask us to stop."""
    needs = "; ".join(unconfirmed_needs) if unconfirmed_needs else "none beyond the menu"
    when = brief["date"] + (" at %s" % brief["time"] if brief.get("time") else "")
    return "\n".join([
        "Subject: Group %s enquiry for %s, %d guests, %s" % (brief["service_style"], when, brief["headcount"], brief["location"]),
        "",
        "Hello %s," % page.name,
        "",
        "I am contacting you on behalf of a customer who is planning a %s event on %s in %s for %d guests, "
        "with a budget of %s USD in total. This enquiry is prepared and sent by an automated assistant; "
        "if you would rather not be contacted this way again, reply saying so and we will stop."
        % (brief["service_style"], when, brief["location"], brief["headcount"], fmt_money(brief["budget_usd"])),
        "Could you tell us:",
        "1. Are you available on %s for a group of %d?" % (when, brief["headcount"]),
        "2. Which %s menu options would you suggest for this group?" % brief["service_style"],
        "3. What is the price per person and the total for %d, and what does it include?" % brief["headcount"],
        "4. Is there a minimum spend, a deposit, or cancellation terms we should know about?",
        "5. Can you cover these dietary needs, and how: %s?" % needs,
        "",
        "We are only collecting quotes at this stage; the customer decides on any booking. Thank you.",
        "",
        "(Contact channel as published: %s)" % (contact.value if contact else NOT_PUBLISHED),
    ])


def fmt_money(value):
    return ("%.2f" % value).rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def draft_all(brief, store, log):
    """Add a draft for every vendor still in the comparison that lacks one. Returns the ids drafted."""
    drafted = []
    for page in store["pages"]:
        if page.vendor_id in log["drafts"]:
            continue
        if page.vendor_id in log.get("stopped", []):
            continue
        if extract_style(page, brief["service_style"]) is None or extract_area(page, brief["location"]) is None:
            continue
        unconfirmed = [n for n in brief["dietary_needs"] if extract_dietary(page, n) is None]
        contact = extract_contact(page)
        log["drafts"][page.vendor_id] = {
            "vendor": page.name,
            "channel": contact.value if contact else NOT_PUBLISHED,
            "channel_source": {"url": contact.url, "line": contact.line_no} if contact else None,
            "drafted_utc": utc_now(),
            "message": draft_message(brief, page, unconfirmed, contact),
            "sent_utc": None,
            "reply": None,
        }
        drafted.append(page.vendor_id)
    return drafted


def record_sent(log, vendor_id, when):
    entry = log["drafts"].get(vendor_id)
    if entry is None:
        raise ConfigError("record-sent: no draft exists for vendor %s; draft first" % vendor_id)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z", when):
        raise ConfigError("record-sent: --when must be a UTC timestamp like 2026-11-01T15:00:00Z")
    entry["sent_utc"] = when


def reply_availability(text):
    """confirmed, declined or not confirmed, read from the answer's own words; the
    operator's --available flag overrides this when the words are ambiguous."""
    if DECLINE_RE.search(text):
        return "declined"
    if AVAILABLE_RE.search(text):
        return "confirmed"
    return "not confirmed"


def record_reply(log, vendor_id, when, text, available=None, stop=False):
    entry = log["drafts"].get(vendor_id)
    if entry is None:
        raise ConfigError("record-reply: no draft exists for vendor %s" % vendor_id)
    if not entry.get("sent_utc"):
        raise ConfigError("record-reply: vendor %s has no recorded send; a reply cannot precede the question" % vendor_id)
    if not TIMESTAMP_RE.fullmatch(when):
        raise ConfigError("record-reply: --when must be a UTC timestamp like 2026-11-02T09:30:00Z")
    if not isinstance(text, str) or not text.strip():
        raise ConfigError("record-reply: --text must not be blank")
    if available not in (None, "yes", "no"):
        raise ConfigError("record-reply: --available must be yes or no")
    availability = {"yes": "confirmed", "no": "declined"}.get(available) or reply_availability(text)
    entry["reply"] = {"received_utc": when, "text": text, "availability": availability}
    if stop:
        entry["stop"] = True
        log.setdefault("stopped", [])
        if vendor_id not in log["stopped"]:
            log["stopped"].append(vendor_id)


def check_log_against_store(log, store):
    known = {p.vendor_id for p in store["pages"]}
    unknown = sorted(set(log["drafts"]) - known)
    if unknown:
        raise ConfigError("outreach log names vendor(s) not in this store: %s" % ", ".join(unknown))


# ----------------------------------------------------------------- dietary state

def dietary_state(page, need, entry, run_utc):
    """(state, detail) for one vendor and one need. Silence is never coverage."""
    claim = extract_dietary(page, need)
    if claim is not None:
        return "confirmed", claim
    reply = (entry or {}).get("reply")
    if reply:
        text = reply.get("text", "")
        if any(t in text.casefold() for t in need_terms(need)):
            return "stated", reply
    if entry is None:
        return "not confirmed", "question not yet drafted"
    if not entry.get("sent_utc"):
        return "not confirmed", "question drafted %s, not sent" % entry.get("drafted_utc", "")
    if reply:
        return "not confirmed", "question asked %s; the reply of %s does not address it" % (entry["sent_utc"], reply.get("received_utc", ""))
    return "not confirmed", "question asked %s, no reply as of %s" % (entry["sent_utc"], run_utc)


def availability_state(entry):
    """confirmed / declined / not confirmed for the brief's date, from the recorded answer only."""
    reply = (entry or {}).get("reply")
    if not reply:
        return "not confirmed"
    return reply.get("availability") or reply_availability(reply.get("text", ""))


def reply_prices(entry):
    """Per person prices the vendor's answer states, as (value, clause) pairs; empty when none."""
    text = ((entry or {}).get("reply") or {}).get("text", "")
    return [(float(m.group(1).replace(",", "")), price_context(text, m.start())) for m in PRICE_RE.finditer(text)]


# ----------------------------------------------------------------- report

def compare(brief, store, log, run_utc=None):
    """Classify every vendor and gather its claims. Returns a dict the renderer prints."""
    run_utc = run_utc or utc_now()
    check_log_against_store(log, store)
    compared, excluded = [], []
    for page in store["pages"]:
        style = extract_style(page, brief["service_style"])
        area = extract_area(page, brief["location"])
        if style is None:
            excluded.append((page, "service style: no line on the page names %s" % inline(brief["service_style"])))
            continue
        if area is None:
            excluded.append((page, "area: no line on the page names %s; not verified, not inferred"
                             % " or ".join(inline(t) for t in location_tokens(brief["location"]))))
            continue
        entry = log["drafts"].get(page.vendor_id)
        row = {
            "page": page, "style": style, "area": area,
            "capacity": extract_capacity(page), "prices": extract_prices(page),
            "terms": extract_terms(page),
            "menu": extract_menu(page), "contact": extract_contact(page),
            "dietary": [(need, dietary_state(page, need, entry, run_utc)) for need in brief["dietary_needs"]],
            "outreach": entry,
            "availability": availability_state(entry),
            "reply_prices": reply_prices(entry),
        }
        compared.append(row)
    return {"brief": brief, "run_utc": run_utc, "source": store["source"], "compared": compared, "excluded": excluded}


def outreach_status(entry, run_utc):
    if entry is None:
        return "no draft yet"
    if entry.get("stop"):
        return "asked us to stop on %s; no further contact" % entry.get("reply", {}).get("received_utc", "")
    if not entry.get("sent_utc"):
        return "draft recorded %s, not sent" % entry.get("drafted_utc", "")
    if entry.get("reply"):
        return "asked %s, replied %s" % (entry["sent_utc"], entry["reply"].get("received_utc", ""))
    return "contacted %s, no reply as of %s" % (entry["sent_utc"], run_utc)


def fence_for(text):
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def render(result):
    brief, run_utc = result["brief"], result["run_utc"]
    needs = brief["dietary_needs"]
    L = []
    L.append("# Catering comparison: %s, %s, %d guests" % (brief["location"], brief["date"], brief["headcount"]))
    L.append("")
    L.append("Brief: %s%s; service style %s; budget %s USD in total, %s USD per head (the brief's budget divided by its headcount); dietary needs: %s."
             % (brief["date"], (" at %s" % brief["time"]) if brief.get("time") else "", inline(brief["service_style"]),
                fmt_money(brief["budget_usd"]), fmt_money(round(brief["budget_per_head"], 2)),
                "; ".join(inline(n) for n in needs) if needs else "none stated"))
    L.append("Run (UTC): %s. Collection window: %s." % (
        run_utc, ("ends %s" % brief["response_deadline_utc"]) if brief.get("response_deadline_utc") else "no deadline set in the brief"))
    L.append("Every value below is quoted from the vendor's own page or recorded answer with the raw text beneath its source; "
             "a value the vendor did not state is marked %s. No price is totalled or estimated. "
             "Dietary coverage and availability are never inferred from silence." % NOT_PUBLISHED)
    src = result["source"] or {}
    if src:
        L.append("Candidate list: %s (%s)" % (src.get("description", "index.json"), src.get("label", "")))
    L.append("")
    L.append("## Summary")
    L.append("")
    header = ["Vendor", "Style", "Area", "Capacity", "Price per person (as stated)", "Against budget per head", "Availability for %s" % brief["date"]] + \
             ["Dietary: %s" % canonical_need(n) for n in needs] + ["Outreach"]
    L.append("| " + " | ".join(header) + " |")
    L.append("|" + " --- |" * len(header))
    for row in result["compared"]:
        cap = row["capacity"]
        prices = prices_for_style(row["prices"], brief["service_style"])
        stated = [v for v, _ in row["reply_prices"]]
        if stated:
            price_cell = "%s (stated in the vendor's answer)" % ", ".join(fmt_money(v) for v in stated)
            compared_prices = stated
        elif prices:
            price_cell = ", ".join(fmt_money(c.value) + (" (starting point)" if c.starting else "") for c in prices) + " (page)"
            compared_prices = [c.value for c in prices]
        elif row["prices"]:
            price_cell = "no %s price published (other styles priced)" % inline(brief["service_style"])
            compared_prices = []
        else:
            price_cell = NOT_PUBLISHED
            compared_prices = []
        if compared_prices:
            lowest = min(compared_prices)
            budget_cell = ("over budget: %s stated vs %s per head in the brief" if lowest > brief["budget_per_head"]
                           else "within budget per head (%s stated vs %s)") % (fmt_money(lowest), fmt_money(round(brief["budget_per_head"], 2)))
        else:
            budget_cell = "no stated price to compare"
        cells = [row["page"].name, "yes", "yes",
                 (str(cap.value) + (" (fits)" if cap.value >= brief["headcount"] else " (below headcount)")) if cap else NOT_PUBLISHED,
                 price_cell, budget_cell, row["availability"]]
        for need, (state, _) in row["dietary"]:
            cells.append(state)
        cells.append(outreach_status(row["outreach"], run_utc))
        L.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    if not result["compared"]:
        L.append("| (no vendor passed the style and area check; see Checked and excluded) |" + " |" * (len(header) - 1))
    comp = result["compared"]
    contacted = [r for r in comp if r["outreach"] and r["outreach"].get("sent_utc")]
    L.append("")
    L.append("Counts: %d vendor(s) compared; %d state a capacity of at least %d on their page; %d contacted; %d replied; "
             "%d confirmed availability for %s; %d declined; %d asked us to stop."
             % (len(comp), sum(1 for r in comp if r["capacity"] and r["capacity"].value >= brief["headcount"]), brief["headcount"],
                len(contacted), sum(1 for r in contacted if r["outreach"].get("reply")),
                sum(1 for r in comp if r["availability"] == "confirmed"), brief["date"],
                sum(1 for r in comp if r["availability"] == "declined"),
                sum(1 for r in comp if (r["outreach"] or {}).get("stop"))))
    L.append("")
    L.append("## Availability for %s" % brief["date"])
    for state, title in (("confirmed", "Confirmed by the vendor's answer"), ("declined", "Declined or not available"),
                         ("not confirmed", "Not confirmed (no answer, or the answer does not say)")):
        names = [r["page"].name for r in comp if r["availability"] == state]
        L.append("- %s: %s" % (title, ", ".join(names) if names else "none"))
    L.append("")
    L.append("## Vendors compared")
    for row in result["compared"]:
        page = row["page"]
        L.append("")
        L.append("### %s" % page.name)
        L.append("Page: <%s>, retrieved %s%s" % (page.url, page.retrieved or "(no retrieval time recorded)",
                                                  (" [%s]" % page.label) if page.label else ""))
        L.extend(row["style"].lines("Service style match"))
        L.extend(row["area"].lines("Area match"))
        if row["capacity"]:
            L.extend(row["capacity"].lines("Capacity"))
        else:
            L.append("- Capacity: %s" % NOT_PUBLISHED)
        if row["prices"]:
            for c in row["prices"]:
                label = "Price per person (USD)%s, clause %s%s" % (" (starting point as stated)" if c.starting else "",
                                                                  inline(c.context), (", %s" % c.style) if c.style else ", no style named")
                L.extend(c.lines(label))
        else:
            L.append("- Price per person: %s" % NOT_PUBLISHED)
        if row["terms"]:
            for c in row["terms"]:
                L.extend(c.lines(c.field[0].upper() + c.field[1:]))
        else:
            L.append("- Minimum spend, deposit and cancellation terms: %s" % NOT_PUBLISHED)
        reply = (row["outreach"] or {}).get("reply")
        if reply:
            L.append("- Availability for %s: %s, from the vendor's answer received %s" % (brief["date"], row["availability"].upper(), reply.get("received_utc", "")))
            for value, clause in row["reply_prices"]:
                L.append("- Price per person (USD) stated in the answer: %s, clause %s" % (fmt_money(value), inline(clause)))
            L.append("  Source: vendor reply recorded in the outreach log")
            f = fence_for(reply.get("text", ""))
            L.extend(["  " + f, "  " + reply.get("text", "").replace("\n", "\n  "), "  " + f])
        else:
            L.append("- Availability for %s: NOT CONFIRMED (no answer recorded)" % brief["date"])
        if row["menu"]:
            for c in row["menu"]:
                L.extend(c.lines("Menu"))
        else:
            L.append("- Menu: no menu section found on the page")
        for need, (state, detail) in row["dietary"]:
            label = "Dietary, %s" % canonical_need(need)
            if state == "confirmed":
                L.extend(detail.lines(label + ": CONFIRMED by the vendor's page"))
            elif state == "stated":
                L.append("- %s: STATED by the vendor's answer received %s" % (label, detail.get("received_utc", "")))
                L.append("  Source: vendor reply recorded in the outreach log")
                f = fence_for(detail.get("text", ""))
                L.extend(["  " + f, "  " + detail.get("text", "").replace("\n", "\n  "), "  " + f])
            else:
                L.append("- %s: NOT CONFIRMED (%s)" % (label, detail))
        if row["contact"]:
            L.extend(row["contact"].lines("Contact channel"))
        else:
            L.append("- Contact channel: %s" % NOT_PUBLISHED)
        L.append("- Outreach: %s" % outreach_status(row["outreach"], run_utc))
    no_reply = [r for r in result["compared"] if r["outreach"] and r["outreach"].get("sent_utc") and not r["outreach"].get("reply")]
    L.append("")
    L.append("## Contacted with no reply")
    if no_reply:
        for r in no_reply:
            L.append("- %s: contacted %s via %s; no reply as of %s"
                     % (r["page"].name, r["outreach"]["sent_utc"], inline(r["outreach"].get("channel", "")), run_utc))
    else:
        L.append("- none")
    declined = [r for r in comp if r["availability"] == "declined"]
    L.append("")
    L.append("## Declined")
    if declined:
        for r in declined:
            L.append("- %s: answer received %s (quoted in its section above)" % (r["page"].name, r["outreach"]["reply"].get("received_utc", "")))
    else:
        L.append("- none")
    L.append("")
    L.append("## Checked and excluded")
    if result["excluded"]:
        for page, reason in result["excluded"]:
            L.append("- %s (<%s>): %s" % (page.name, page.url, reason))
    else:
        L.append("- none")
    L.append("")
    L.append("## Outreach drafts")
    drafts = [r for r in result["compared"] if r["outreach"]]
    if drafts:
        L.append("Drafts are recorded, not sent. Under a hire the operator sends each one through the vendor's published channel and records the send and the reply. "
                 "Every draft states it is on behalf of a customer and sent by an automated assistant, asks for a quote only, and carries no buyer contact details.")
        for r in drafts:
            e = r["outreach"]
            L.append("")
            L.append("#### %s (%s)" % (r["page"].name, outreach_status(e, run_utc)))
            f = fence_for(e.get("message", ""))
            L.extend([f, e.get("message", ""), f])
    else:
        L.append("- no drafts recorded for this run (run `draft` to create them)")
    L.append("")
    L.append("## Sources")
    for row in result["compared"]:
        L.append("- %s: <%s> retrieved %s" % (row["page"].name, row["page"].url, row["page"].retrieved))
    for page, _ in result["excluded"]:
        L.append("- %s: <%s> retrieved %s (excluded)" % (page.name, page.url, page.retrieved))
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(prog="agents/catering-finder/catering_finder.py",
                                description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="render the comparison report from a brief, a store and an optional outreach log")
    run.add_argument("--brief", required=True)
    run.add_argument("--store", required=True)
    run.add_argument("--log")
    run.add_argument("--out", help="write the report here instead of stdout")

    draft = sub.add_parser("draft", help="record a question draft for every compared vendor without one; sends nothing")
    draft.add_argument("--brief", required=True)
    draft.add_argument("--store", required=True)
    draft.add_argument("--log", required=True)

    sent = sub.add_parser("record-sent", help="record that the operator sent a draft through the published channel")
    sent.add_argument("vendor_id")
    sent.add_argument("--log", required=True)
    sent.add_argument("--when", required=True)

    reply = sub.add_parser("record-reply", help="record the vendor's answer, verbatim")
    reply.add_argument("vendor_id")
    reply.add_argument("--log", required=True)
    reply.add_argument("--when", required=True)
    reply.add_argument("--text", required=True)
    reply.add_argument("--available", choices=("yes", "no"), help="override the availability read from the answer's words")
    reply.add_argument("--stop", action="store_true", help="the vendor asked not to be contacted again")

    send = sub.add_parser("send", help="live sending: refused without --execute and a hire id; no transport in this build")
    send.add_argument("vendor_id")
    send.add_argument("--log", required=True)
    send.add_argument("--hire-id")
    send.add_argument("--execute", action="store_true")

    cap = sub.add_parser("capture", help="fetch one live vendor page into a store with provenance")
    cap.add_argument("url")
    cap.add_argument("--store", required=True)
    cap.add_argument("--id", required=True, dest="vendor_id")
    cap.add_argument("--name", required=True)
    return p


def main(argv=None, env=None, stdout=None, stderr=None, fetcher=None):
    import os
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    env = os.environ if env is None else env
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            brief, store, log = load_brief(args.brief), load_store(args.store), load_log(args.log)
            text = render(compare(brief, store, log))
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
                stdout.write("report written to %s\n" % args.out)
            else:
                stdout.write(text)
            return 0
        if args.command == "draft":
            brief, store, log = load_brief(args.brief), load_store(args.store), load_log(args.log)
            check_log_against_store(log, store)
            drafted = draft_all(brief, store, log)
            save_log(args.log, log)
            stdout.write("drafted %d question(s), nothing sent: %s\n" % (len(drafted), ", ".join(drafted) or "(none new)"))
            return 0
        if args.command == "record-sent":
            log = load_log(args.log)
            record_sent(log, args.vendor_id, args.when)
            save_log(args.log, log)
            stdout.write("recorded: %s sent %s\n" % (args.vendor_id, args.when))
            return 0
        if args.command == "record-reply":
            log = load_log(args.log)
            record_reply(log, args.vendor_id, args.when, args.text, available=args.available, stop=args.stop)
            save_log(args.log, log)
            stdout.write("recorded: %s replied %s\n" % (args.vendor_id, args.when))
            return 0
        if args.command == "send":
            hire = args.hire_id or env.get(HIRE_ENV, "").strip()
            if not args.execute or not hire:
                raise ConfigError("send: refused. Live sending needs --execute and a hire id (--hire-id or %s); "
                                  "this build drafts and records only" % HIRE_ENV)
            raise ConfigError("send: no live transport is part of this build; under hire %s the operator sends the "
                              "recorded draft through the vendor's published channel and runs record-sent" % hire)
        if args.command == "capture":
            rel, retrieved = capture(args.url, args.store, args.vendor_id, args.name, fetcher or fetch_page)
            stdout.write("captured %s as %s at %s\n" % (args.url, rel, retrieved))
            return 0
        raise ConfigError("unknown command %s" % args.command)
    except (ConfigError, FetchError) as err:
        stderr.write("error: %s. No report emitted.\n" % err)
        return 2


if __name__ == "__main__":
    sys.exit(main())
