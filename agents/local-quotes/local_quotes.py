#!/usr/bin/env python3
"""Local Services Quote agent: the agent behind NEAR build job 481516a5 (issue #76).

Takes a plain language service request (service, location, job details,
timing, budget limits), reads the published pages of candidate providers,
keeps only the providers whose own listing or site shows they offer that
service in that area, builds one structured quote request, drafts it for
each provider's published channels, follows up non responders through
their other published channels, and renders one comparison report.

Hard filter (issue #76 item 2): a provider is contacted only after its own
page shows both the service and the area. The verification evidence is
kept per provider as claims: the claim, its source link and the raw page
line directly beneath, verbatim (AGENT-BRIEF.md rule 3). A page silent on
the area is excluded as "not verified, not inferred"; a page that names
the service only to deny it ("we do not do plumbing") is not a match.

Channels (items 3 and 4): email, web form and directory messaging, each
read from the provider's own page and quoted. The first draft goes to the
first published channel in that order. A provider who has not replied
after the follow up interval gets a follow up drafted for the next
published channel not yet tried. A provider whose page publishes only a
phone number is flagged "phone only" and gets no written draft. After
the collection window, every non responder is reported as "no response
after" the attempts made, each with its channel and date.

Comparison (item 5): price, availability, requirements and what is
included, each tied to a provider reply (quoted, dated) or to published
pricing on the provider's page (quoted, with its line). Nothing is
totalled, estimated or filled in; a value nobody stated reads "not stated".

Outreach (item 3, limits): this build drafts and records only. Every draft
says it is sent on behalf of a customer by an automated assistant, asks for
a quote only, carries no customer contact details, and invites the provider
to ask us to stop. Under a real hire the operator sends each draft through
the provider's published channel and records it with `record-sent`, and
records answers with `record-reply`. The `send` command exists only to
refuse without a hire id and --execute; no live transport is part of this
build. The agent never books, accepts a quote or pays anything.

Fail closed: a request that does not validate, a store that cannot be read,
a page whose bytes differ from its recorded sha256, or a log entry for a
provider not in the store stops the program with exit 2 and no report.

Standard library only. Run from the repository root:

    python3 agents/local-quotes/local_quotes.py run \
        --request agents/local-quotes/tests/fixtures/request.json \
        --store agents/local-quotes/tests/fixtures \
        --log agents/local-quotes/tests/fixtures/outreach-log.json \
        --now 2026-11-05T09:00:00Z

    python3 agents/local-quotes/local_quotes.py draft --request R --store S --log L
    python3 agents/local-quotes/local_quotes.py follow-up --request R --store S --log L --now UTC
    python3 agents/local-quotes/local_quotes.py record-sent PROVIDER --log L --channel email --when UTC
    python3 agents/local-quotes/local_quotes.py record-reply PROVIDER --log L --when UTC --text "..."
    python3 agents/local-quotes/local_quotes.py capture URL --store S --id PROVIDER --name "..."

A store is a folder holding index.json (the candidate list), providers/<id>.html
(each provider page as captured) and provenance.json (url, retrieval time,
sha256 per page). The fixture store under tests/fixtures is SYNTHETIC: every
page was written by hand for the tests and is labelled so in the page and in
provenance.json. `capture` builds a real store from live pages.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

NOT_STATED = "not stated"
USER_AGENT = "tiny-ledger local-quotes/0.1"
TIMEOUT_SECONDS = 30
HIRE_ENV = "LOCAL_QUOTES_HIRE_ID"
WRITTEN_CHANNELS = ("email", "web_form", "directory_message")
CHANNEL_NAMES = {"email": "email", "web_form": "web form", "directory_message": "directory message", "phone": "phone"}
REQUEST_FIELDS = ("service", "location", "job_details", "timing", "response_deadline_utc")

# A service named in the request is matched on its own words plus these
# common phrasings. A service not listed here is matched on its own words.
SERVICE_TERMS = {
    "plumbing": ("plumbing", "plumber", "plumbers"),
    "electrical": ("electrical", "electrician", "electricians"),
    "house cleaning": ("house cleaning", "home cleaning", "residential cleaning", "maid service"),
    "lawn care": ("lawn care", "lawn mowing", "mowing", "yard maintenance"),
    "hvac": ("hvac", "heating and air", "air conditioning", "furnace"),
    "painting": ("painting", "painter", "painters"),
    "moving": ("moving", "movers", "moving company"),
    "roofing": ("roofing", "roofer", "roofers", "roof repair"),
    "pest control": ("pest control", "exterminator", "extermination"),
    "handyman": ("handyman", "handyman services"),
}

TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")
FORM_RE = re.compile(r"(?i)\b(?:web form|contact form|quote form|request a quote|request form|online form)\b")
DIRECTORY_RE = re.compile(r"(?i)\b(?:message us on|send us a message on|directory message|message (?:us )?through|via (?:our )?(?:profile|listing) on)\b")
MONEY_RE = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
PRICE_HINT_RE = re.compile(r"(?i)\b(?:per hour|/hour|an hour|hourly|flat|trip charge|service call|call[- ]out|starting|from|quote|total|fee)\b")
REQUIREMENT_RE = re.compile(r"(?i)\b(?:licen[cs]ed|insured|bonded|permit|requires?|required|access to|deposit|minimum|warranty)\b")
INCLUDED_RE = re.compile(r"(?i)\b(?:includ(?:es|ed|ing)|haul[- ]away|disposal|parts and labor|labor and parts)\b")
EXCLUDED_RE = re.compile(r"(?i)(?:\bnot included\b|\bdo(?:es)? not include\b|\bdoesn't include\b|\bexclud(?:es|ed|ing)\b|\b(?:are|is) extra\b|\bextra charge\b|\badditional charge\b|\bbilled separately\b|\bnot covered\b)")
SITE_VISIT_RE = re.compile(r"(?i)\b(?:site visit|in[- ]home (?:estimate|visit)|on[- ]?site|come out|come by|take a look|inspect(?:ion)?|assessment|see the job)\b")
FOR_RE = re.compile(r"(?i)\bfor (?:the |a |your )?(?!you\b|us\b)\w")
HOURLY_RE = re.compile(r"(?i)(?:per hour|/hour|\ban hour\b|\bhourly\b)")
ESTIMATE_RE = re.compile(r"(?i)\b(?:estimate[sd]?|approximately|approx|about|around|roughly|ballpark|range|starting|from \$|subject to|depending|depends)\b")
FIXED_RE = re.compile(r"(?i)\b(?:fixed|flat|total|firm|all[- ]in)\b")
# What a quote can cover. A quote is compared on an item only when a provider
# states it as included or excluded; silence is reported as "not stated".
COVERAGE_ITEMS = (
    ("parts", ("parts",)), ("materials", ("materials", "the new heater", "equipment")),
    ("labor", ("labor", "labour")), ("permit", ("permit",)),
    ("disposal of the old unit", ("haul-away", "haul away", "disposal", "removal of the old")),
    ("warranty", ("warranty",)), ("installation", ("install",)),
)
DECLINE_RE = re.compile(r"(?i)\b(?:not available|unavailable|fully booked|booked up|booked out|cannot|can't|unable to|no availability|we don't do|we do not do|decline|pass on)\b")
AVAILABLE_RE = re.compile(r"(?i)\b(?:available|we can do|we can come|can schedule|can be there|have an opening|openings?)\b")
TAG_RE = re.compile(r"<[^>]+>")
NEGATION_RE = r"\b(?:no|not|don't|do not|never|except|without)\b[^.;]{0,40}?"


class ConfigError(Exception):
    """Bad input: request, log or command. Exit 2, no report."""


class FetchError(Exception):
    """A store or page that cannot be read, or a live fetch that failed. Exit 2."""


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(text, what):
    if not isinstance(text, str) or not TIMESTAMP_RE.fullmatch(text):
        raise ConfigError("%s must be a UTC timestamp like 2026-11-04T17:00:00Z, got %r" % (what, text))
    fmt = "%Y-%m-%dT%H:%M:%SZ" if text.count(":") == 2 else "%Y-%m-%dT%H:%MZ"
    return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)


# ----------------------------------------------------------------- request

def load_request(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ConfigError("request %s could not be read as JSON: %s" % (path, err))
    return validate_request(data)


def validate_request(data):
    """The structured quote request. Required: service, location, job_details,
    timing, response_deadline_utc. Optional: budget_min_usd, budget_max_usd,
    follow_up_after_hours (default 48)."""
    if not isinstance(data, dict):
        raise ConfigError("the request must be a JSON object")
    for field in REQUEST_FIELDS:
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ConfigError("request field %s is required and must be non empty text" % field)
    parse_utc(data["response_deadline_utc"], "response_deadline_utc")
    for field in ("budget_min_usd", "budget_max_usd"):
        value = data.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0):
            raise ConfigError("request field %s must be a positive number when given" % field)
    if data.get("budget_min_usd") and data.get("budget_max_usd") and data["budget_min_usd"] > data["budget_max_usd"]:
        raise ConfigError("budget_min_usd is above budget_max_usd")
    hours = data.get("follow_up_after_hours", 48)
    if isinstance(hours, bool) or not isinstance(hours, (int, float)) or hours <= 0:
        raise ConfigError("follow_up_after_hours must be a positive number")
    out = {k: data[k].strip() for k in REQUEST_FIELDS}
    out.update({"budget_min_usd": data.get("budget_min_usd"), "budget_max_usd": data.get("budget_max_usd"),
                "follow_up_after_hours": hours})
    return out


def service_terms(service):
    key = service.strip().lower()
    return SERVICE_TERMS.get(key, (key,))


def location_tokens(location):
    """The place names a page must state: the city (before the comma) and any 5 digit ZIP."""
    city = location.split(",")[0].strip()
    zips = re.findall(r"\b\d{5}\b", location)
    return [t for t in [city] + zips if t]


# ----------------------------------------------------------------- store

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


class Page:
    def __init__(self, provider_id, name, url, retrieved, raw, label):
        self.provider_id = provider_id
        self.name = name
        self.url = url
        self.retrieved = retrieved
        self.raw = raw
        self.label = label
        self.lines = raw.splitlines()


def load_store(folder):
    """index.json, provenance.json and every provider page, each checked against
    its recorded sha256. An edited page is refused rather than quoted."""
    folder = Path(folder)
    try:
        index = json.loads((folder / "index.json").read_text(encoding="utf-8"))
        provenance = json.loads((folder / "provenance.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise FetchError("store %s: index.json or provenance.json could not be read as JSON: %s" % (folder, err))
    if not isinstance(index, dict) or not isinstance(index.get("providers"), list):
        raise FetchError("store %s: index.json must hold a providers list" % folder)
    pages, seen = [], set()
    for entry in index["providers"]:
        if not isinstance(entry, dict):
            raise FetchError("store %s: every index entry must be an object" % folder)
        pid, name, url = entry.get("id"), entry.get("name"), entry.get("url")
        if not all(isinstance(v, str) and v.strip() for v in (pid, name, url)):
            raise FetchError("store %s: index entry %r needs non empty id, name and url" % (folder, entry))
        if pid in seen:
            raise FetchError("store %s: duplicate provider id %s" % (folder, pid))
        seen.add(pid)
        rel = "providers/%s.html" % pid
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
        pages.append(Page(pid, name.strip(), url.strip(), str(record.get("retrieved_utc", "")),
                          data.decode("utf-8", "replace"), str(record.get("label", ""))))
    return {"source": index.get("source", {}), "pages": pages}


def fetch_page(url):
    """GET one page over HTTPS; (status_line, headers, body bytes). Raises FetchError."""
    if urllib.parse.urlsplit(url).scheme != "https":
        raise FetchError("only https URLs are captured; got %s" % url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return "HTTP %d %s" % (resp.status, resp.reason), list(resp.getheaders()), resp.read()
    except urllib.error.HTTPError as err:
        return "HTTP %d %s" % (err.code, err.reason), list(err.headers.items()), b""
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("transport failure for %s: %s" % (url, err))


def capture(url, store, provider_id, name, fetcher=fetch_page):
    """Fetch one live provider page into the store with provenance. Non 200 is refused."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", provider_id):
        raise ConfigError("provider id must be lower case letters, digits and hyphens")
    store = Path(store)
    status, headers, body = fetcher(url)
    if not status.startswith("HTTP 200"):
        raise FetchError("%s answered %s; not stored" % (url, status))
    (store / "providers").mkdir(parents=True, exist_ok=True)
    rel = "providers/%s.html" % provider_id
    (store / rel).write_bytes(body)
    retrieved = utc_now()
    index_path, prov_path = store / "index.json", store / "provenance.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"providers": []}
    prov = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.exists() else {}
    index["providers"] = [p for p in index.get("providers", []) if p.get("id") != provider_id]
    index["providers"].append({"id": provider_id, "name": name, "url": url})
    prov[rel] = {"url": url, "retrieved_utc": retrieved, "status_line": status,
                 "headers": ["%s: %s" % h for h in headers if h[0].lower() != "set-cookie"],
                 "sha256": sha256_bytes(body), "label": "captured live by local_quotes.py capture"}
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    prov_path.write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")
    return rel, retrieved


# ----------------------------------------------------------------- extraction

def plain(line):
    return " ".join(unescape(TAG_RE.sub(" ", line)).split())


def inline(value):
    text = json.dumps(value, ensure_ascii=False)
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", text)


class Claim:
    """One value read from a page line: the value, the source link and the raw line."""

    def __init__(self, field, value, page, line_no):
        self.field = field
        self.value = value
        self.url = page.url
        self.line_no = line_no
        self.excerpt = page.lines[line_no - 1]

    def lines(self):
        return ["- %s as shown: %s" % (self.field, inline(self.value)),
                "  Source: <%s> (line %d)" % (self.url, self.line_no),
                "  ```", "  " + self.excerpt, "  ```"]


def negated(text, term):
    return re.search(NEGATION_RE + re.escape(term), text, re.I) is not None


def name_only(page, line):
    """A title or heading line that only repeats the business name. A name is not
    the provider saying it offers a service or serves an area, so it never verifies."""
    text = plain(line)
    return "<title" in line.lower() or text.lower() == page.name.lower()


def find_line(page, terms, field):
    """The first line stating any term without denying it, as a Claim; else None.
    Lines that only repeat the business name are skipped."""
    for no, line in enumerate(page.lines, start=1):
        if name_only(page, line):
            continue
        text = plain(line)
        low = text.lower()
        for term in terms:
            if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(term.lower()), low) and not negated(low, term.lower()):
                return Claim(field, text, page, no)
    return None


def denies(page, terms):
    """A line that names a term only to deny it, as a Claim; else None."""
    for no, line in enumerate(page.lines, start=1):
        low = plain(line).lower()
        for term in terms:
            if term.lower() in low and negated(low, term.lower()):
                return Claim("Denial", plain(line), page, no)
    return None


def extract_channels(page):
    """Published contact channels, each a Claim, in the order the agent tries them."""
    found = {}
    for no, line in enumerate(page.lines, start=1):
        text = plain(line)
        if "email" not in found:
            m = EMAIL_RE.search(text)
            if m:
                found["email"] = Claim("Email (published)", m.group(0), page, no)
        if "web_form" not in found and FORM_RE.search(text):
            href = re.search(r'href="([^"]+)"', line)
            found["web_form"] = Claim("Web form (published)", href.group(1) if href else text, page, no)
        if "directory_message" not in found and DIRECTORY_RE.search(text):
            found["directory_message"] = Claim("Directory messaging (published)", text, page, no)
        if "phone" not in found:
            m = PHONE_RE.search(text)
            if m:
                found["phone"] = Claim("Phone (published)", m.group(0), page, no)
    return found


def extract_lines(page, pattern, field):
    out = []
    for no, line in enumerate(page.lines, start=1):
        text = plain(line)
        if text and pattern.search(text):
            out.append(Claim(field, text, page, no))
    return out


def published_pricing(page):
    """Lines stating a dollar amount in a pricing clause (rate, fee, starting price), quoted whole."""
    return [c for c in extract_lines(page, MONEY_RE, "Published pricing") if PRICE_HINT_RE.search(c.value)]


# ----------------------------------------------------------------- outreach log

def load_log(path):
    if path is None or not Path(path).exists():
        return {"hire_id": None, "providers": {}}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ConfigError("outreach log %s could not be read as JSON: %s" % (path, err))
    if not isinstance(data, dict) or not isinstance(data.get("providers"), dict):
        raise ConfigError("outreach log %s must hold a providers object" % path)
    return data


def save_log(path, log):
    Path(path).write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_log_against_store(log, store):
    unknown = sorted(set(log["providers"]) - {p.provider_id for p in store["pages"]})
    if unknown:
        raise ConfigError("outreach log names provider(s) not in this store: %s" % ", ".join(unknown))


def fmt_money(value):
    return ("%.2f" % value).rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def budget_text(request):
    lo, hi = request.get("budget_min_usd"), request.get("budget_max_usd")
    if lo and hi:
        return "between %s and %s USD" % (fmt_money(lo), fmt_money(hi))
    if hi:
        return "up to %s USD" % fmt_money(hi)
    if lo:
        return "from %s USD" % fmt_money(lo)
    return "not set by the customer"


def quote_request_text(request, page, channel_claim, follow_up_of=None):
    """The structured quote request. It says it is on behalf of a customer and
    sent by an automated assistant, asks for a quote only, carries no customer
    contact details, and invites the provider to ask us to stop."""
    opening = ("Following up on our %s of %s about the request below, in case it did not reach you."
               % (CHANNEL_NAMES[follow_up_of[0]], follow_up_of[1]) if follow_up_of else None)
    lines = [
        "Subject: Quote request: %s in %s" % (request["service"], request["location"]),
        "",
        "Hello %s," % page.name,
        "",
    ]
    if opening:
        lines += [opening, ""]
    lines += [
        "I am contacting you on behalf of a customer who needs %s in %s. This request is prepared and sent "
        "by an automated assistant; if you would rather not be contacted this way again, reply saying so and "
        "we will stop." % (request["service"], request["location"]),
        "",
        "The job: %s" % request["job_details"],
        "Timing: %s" % request["timing"],
        "Budget: %s" % budget_text(request),
        "",
        "Could you tell us:",
        "1. Your price for this job, and whether it is a fixed quote, an estimate or an hourly rate.",
        "2. Your earliest availability within the timing above.",
        "3. What the price includes (parts, materials, disposal, warranty).",
        "4. Anything you need from the customer (access, permits, a deposit, a site visit first).",
        "",
        "We are only collecting quotes at this stage; the customer decides on any booking. Please reply by %s."
        % request["response_deadline_utc"],
        "",
        "(Published channel used: %s: %s)" % (CHANNEL_NAMES[_channel_key(channel_claim)],
                                             channel_claim.value),
    ]
    return "\n".join(lines)


def _channel_key(claim):
    return {"Email (published)": "email", "Web form (published)": "web_form",
            "Directory messaging (published)": "directory_message", "Phone (published)": "phone"}[claim.field]


def written_channels(channels):
    return [c for c in WRITTEN_CHANNELS if c in channels]


def draft_initial(request, store, log, now):
    """Record a first draft for every verified provider with a written channel and
    no entry yet. Phone only providers get a flag, no draft. Sends nothing."""
    check_log_against_store(log, store)
    drafted = []
    for row in verified_rows(request, store):
        pid = row["page"].provider_id
        if pid in log["providers"]:
            continue
        written = written_channels(row["channels"])
        if not written:
            log["providers"][pid] = {"phone_only": True, "flagged_utc": now, "attempts": []}
            continue
        channel = written[0]
        log["providers"][pid] = {"attempts": [{
            "channel": channel, "drafted_utc": now,
            "text": quote_request_text(request, row["page"], row["channels"][channel])}]}
        drafted.append(pid)
    return drafted


def draft_follow_ups(request, store, log, now):
    """For each provider with a sent attempt older than follow_up_after_hours and no
    reply, draft the request for the next published written channel not yet tried.
    Nothing past the collection window; nothing for a provider who asked to stop."""
    check_log_against_store(log, store)
    now_dt = parse_utc(now, "--now")
    if now_dt >= parse_utc(request["response_deadline_utc"], "response_deadline_utc"):
        return []
    rows = {r["page"].provider_id: r for r in verified_rows(request, store)}
    drafted = []
    for pid, entry in log["providers"].items():
        row = rows.get(pid)
        if row is None or entry.get("reply") or entry.get("stop") or entry.get("phone_only"):
            continue
        attempts = entry.get("attempts", [])
        if any(not a.get("sent_utc") for a in attempts):
            continue  # a draft is still waiting to be sent
        sent = [a for a in attempts if a.get("sent_utc")]
        if not sent:
            continue
        last = max(parse_utc(a["sent_utc"], "sent_utc") for a in sent)
        if now_dt - last < timedelta(hours=request["follow_up_after_hours"]):
            continue
        tried = [a["channel"] for a in attempts]
        written = written_channels(row["channels"])
        remaining = [c for c in written if c not in tried]
        if not remaining and "email" in written and tried.count("email") == 1:
            remaining = ["email"]  # the proposal's "further email attempt at a different time"
        if not remaining:
            continue
        prev = sorted(sent, key=lambda a: a["sent_utc"])[-1]
        channel = remaining[0]
        attempts.append({"channel": channel, "drafted_utc": now, "follow_up": True,
                         "text": quote_request_text(request, row["page"], row["channels"][channel],
                                                    follow_up_of=(prev["channel"], prev["sent_utc"]))})
        drafted.append(pid)
    return drafted


def record_sent(log, pid, channel, when):
    entry = log["providers"].get(pid)
    if entry is None:
        raise ConfigError("record-sent: no draft exists for provider %s; draft first" % pid)
    parse_utc(when, "--when")
    pending = [a for a in entry.get("attempts", []) if a.get("channel") == channel and not a.get("sent_utc")]
    if not pending:
        raise ConfigError("record-sent: provider %s has no unsent %s draft" % (pid, CHANNEL_NAMES.get(channel, channel)))
    pending[0]["sent_utc"] = when


def reply_availability(text):
    if DECLINE_RE.search(text):
        return "declined"
    if AVAILABLE_RE.search(text):
        return "available as stated"
    return "not confirmed"


def record_reply(log, pid, when, text, stop=False):
    entry = log["providers"].get(pid)
    if entry is None or not any(a.get("sent_utc") for a in entry.get("attempts", [])):
        raise ConfigError("record-reply: provider %s has no recorded send; a reply cannot precede the request" % pid)
    parse_utc(when, "--when")
    if not isinstance(text, str) or not text.strip():
        raise ConfigError("record-reply: --text must not be blank")
    entry["reply"] = {"received_utc": when, "text": text, "availability": reply_availability(text)}
    if stop:
        entry["stop"] = True


# ----------------------------------------------------------------- compare

def verified_rows(request, store):
    return classify(request, store)[0]


def classify(request, store):
    """(verified rows, excluded [(page, reason, evidence claim or None)])."""
    terms = service_terms(request["service"])
    places = location_tokens(request["location"])
    verified, excluded = [], []
    for page in store["pages"]:
        service = find_line(page, terms, "Service offered")
        if service is None:
            denial = denies(page, terms)
            excluded.append((page, "service: no line on the page offers %s" % " or ".join(inline(t) for t in terms)
                             + ("; the page says it does not" if denial else ""), denial))
            continue
        area = find_line(page, places, "Area served")
        if area is None:
            excluded.append((page, "area: no line on the page names %s; not verified, not inferred"
                             % " or ".join(inline(t) for t in places), None))
            continue
        verified.append({"page": page, "service": service, "area": area, "channels": extract_channels(page)})
    return verified, excluded


def attempts_text(entry):
    sent = [a for a in entry.get("attempts", []) if a.get("sent_utc")]
    return "; ".join("%s sent %s" % (CHANNEL_NAMES[a["channel"]], a["sent_utc"]) for a in sent) or "none sent"


def status(entry, now_dt, deadline_dt):
    if entry is None:
        return "verified, no draft yet"
    if entry.get("phone_only"):
        return "phone only: no written channel published; not contacted by this agent"
    if entry.get("stop"):
        return "asked us to stop on %s; no further contact" % entry["reply"]["received_utc"]
    if entry.get("reply"):
        return "replied %s (after: %s)" % (entry["reply"]["received_utc"], attempts_text(entry))
    sent = [a for a in entry.get("attempts", []) if a.get("sent_utc")]
    if not sent:
        return "draft recorded, not sent"
    if now_dt >= deadline_dt:
        return "no response after: %s" % attempts_text(entry)
    return "awaiting reply (so far: %s)" % attempts_text(entry)


def sentences_of(text):
    return [s.strip() for s in re.split(r"(?<=[.;!?])\s+", text) if s.strip()]


def split_clauses(sentence):
    """A sentence split at semicolons and 'but', so 'X is included; Y is extra'
    is read as two statements."""
    return [c.strip() for c in re.split(r";|\bbut\b", sentence) if c.strip()]


def reply_claims(entry):
    """From a recorded reply: the price, included, excluded, site visit and
    requirement statements, each quoted exactly as written."""
    empty = {"price": [], "included": [], "excluded": [], "site_visit": [], "requirements": []}
    if not entry or not entry.get("reply"):
        return empty
    out = dict((k, []) for k in empty)
    for s in sentences_of(entry["reply"]["text"]):
        if MONEY_RE.search(s):
            out["price"].append(s)
        clauses = split_clauses(s)
        if any(EXCLUDED_RE.search(c) for c in clauses):
            out["excluded"].append(s)
        if any((INCLUDED_RE.search(c) or (MONEY_RE.search(c) and FOR_RE.search(c))) and not EXCLUDED_RE.search(c)
               for c in clauses):
            out["included"].append(s)  # "includes X", or a price stated "for X"
        if SITE_VISIT_RE.search(s):
            out["site_visit"].append(s)
        if REQUIREMENT_RE.search(s):
            out["requirements"].append(s)
    return out


def price_kind(text):
    """How the provider framed a price, from its own words."""
    if HOURLY_RE.search(text):
        return "hourly rate"
    if ESTIMATE_RE.search(text):
        return "estimate"
    if FIXED_RE.search(text):
        return "fixed or total, as stated"
    return "price, kind not stated"


def money_values(text):
    return [float(m.replace("$", "").replace(",", "").strip()) for m in MONEY_RE.findall(text)]


def against_budget(price_sentences, request, source):
    """Over-budget marking (the job's budget sample): a stated figure is compared
    with budget_max_usd only when it is a total, fixed price or estimate. An hourly
    rate is not comparable. Nothing is computed beyond reading the stated figure."""
    limit = request.get("budget_max_usd")
    if not price_sentences:
        return "no price stated"
    if not limit:
        return "no budget limit set"
    results = []
    for s in price_sentences:
        kind = price_kind(s)
        values = money_values(s)
        if not values:
            continue
        if kind == "hourly rate":
            results.append("hourly rate, not comparable to the budget limit")
            continue
        top = max(values)
        figure = "$" + ("{:,.2f}".format(top).rstrip("0").rstrip("."))
        if source == "published" and top <= limit:
            results.append("published price only (%s stated on the page), not a quote for this job" % figure)
            continue
        if top > limit:
            results.append("OVER the budget limit of %s USD: %s stated%s (%s)" % (
                fmt_money(limit), figure, " by the provider" if source == "reply" else " on the page", kind))
        else:
            results.append("not over the budget limit of %s USD: %s stated (%s)" % (fmt_money(limit), figure, kind))
    return " / ".join(results) or "no price stated"


def coverage(row):
    """Per item: included, excluded or not stated, from the reply (or, without a
    reply, the page's published lines). Only statements count; silence is 'not stated'."""
    if row["reply"]["price"] or row["reply"]["included"] or row["reply"]["excluded"]:
        inc, exc, source = row["reply"]["included"], row["reply"]["excluded"], "reply"
    else:
        inc = [c.value for c in row["page_included"]]
        exc = [c.value for c in row["page_excluded"]]
        source = "published"
    states = {}
    for item, terms in COVERAGE_ITEMS:
        def says(sentences, want_excluded):
            for s in sentences:
                for c in split_clauses(s):
                    if any(t in c.lower() for t in terms) and bool(EXCLUDED_RE.search(c)) == want_excluded:
                        return s
            return None
        e = says(exc, True)
        i = says(inc, False)
        states[item] = ("excluded", e, source) if e else ("included", i, source) if i else ("not stated", None, source)
    return states


def compare(request, store, log, now):
    check_log_against_store(log, store)
    now_dt = parse_utc(now, "--now")
    deadline_dt = parse_utc(request["response_deadline_utc"], "response_deadline_utc")
    verified, excluded = classify(request, store)
    rows = []
    for row in verified:
        entry = log["providers"].get(row["page"].provider_id)
        rows.append(dict(row, entry=entry, status=status(entry, now_dt, deadline_dt),
                         pricing=published_pricing(row["page"]),
                         page_included=[c for c in extract_lines(row["page"], INCLUDED_RE, "Included (published)")
                                        if not EXCLUDED_RE.search(c.value)],
                         page_excluded=extract_lines(row["page"], EXCLUDED_RE, "Not included (published)"),
                         page_site_visit=extract_lines(row["page"], SITE_VISIT_RE, "Site visit (published)"),
                         page_requirements=extract_lines(row["page"], REQUIREMENT_RE, "Requirement (published)"),
                         reply=reply_claims(entry)))
    return {"request": request, "now": now, "window_closed": now_dt >= deadline_dt, "rows": rows,
            "excluded": excluded, "source": store["source"], "checked": len(store["pages"])}


# ----------------------------------------------------------------- render

def fence(text):
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


PAGE_KEYS = {"price": "pricing", "included": "page_included", "excluded": "page_excluded",
             "site_visit": "page_site_visit", "requirements": "page_requirements"}


def summary_value(row, key):
    reply = row["reply"][key]
    if reply:
        return "reply: " + " / ".join(reply)
    page = row[PAGE_KEYS[key]]
    if page:
        return "published: " + " / ".join(c.value for c in page)
    return NOT_STATED


def price_cells(row):
    """(price as stated, kind, against budget), from the reply, else the page."""
    if row["reply"]["price"]:
        sentences, source = row["reply"]["price"], "reply"
    else:
        sentences, source = [c.value for c in row["pricing"]], "published"
    if not sentences:
        return NOT_STATED, NOT_STATED, against_budget([], row["request"], source)
    kinds = " / ".join(price_kind(x) for x in sentences)
    return summary_value(row, "price"), kinds, against_budget(sentences, row["request"], source)


def coverage_differences(rows):
    """The items on which the quotes differ (acceptance criterion 4): an item one
    provider states as included and another as excluded or does not mention."""
    priced = [r for r in rows if r["reply"]["price"]]
    tables = [(r, coverage(r)) for r in priced]
    out = []
    for item, _ in COVERAGE_ITEMS:
        states = [(r["page"].name, cov[item]) for r, cov in tables]
        kinds = {st[0] for _, st in states}
        if len(priced) > 1 and kinds != {"not stated"} and len(kinds) > 1:
            out.append((item, states))
    return priced, out


def availability(row):
    entry = row["entry"]
    if entry and entry.get("reply"):
        return entry["reply"]["availability"]
    return "not confirmed"


def render(result):
    req = result["request"]
    out = ["# Quote comparison: %s in %s" % (req["service"], req["location"]), "",
           "- Job: %s" % req["job_details"], "- Timing: %s" % req["timing"],
           "- Budget: %s" % budget_text(req),
           "- Collection window ends: %s (%s at this run)" % (req["response_deadline_utc"],
                                                              "closed" if result["window_closed"] else "open"),
           "- Report run: %s" % result["now"], ""]
    src = result["source"]
    if isinstance(src, dict) and src.get("label"):
        out += ["Candidate list: %s (%s)" % (src.get("description", ""), src["label"]), ""]
    rows = result["rows"]
    for r in rows:
        r["request"] = req
    replied = [r for r in rows if r["entry"] and r["entry"].get("reply")]
    contacted = sum(1 for r in rows if r["entry"] and any(a.get("sent_utc") for a in r["entry"].get("attempts", [])))
    out += ["Candidates checked: %d. Verified for the service and area: %d. Contacted: %d. Replied: %d. "
            "Phone only: %d. Excluded: %d." % (result["checked"], len(rows), contacted, len(replied),
                                               sum(1 for r in rows if r["entry"] and r["entry"].get("phone_only")),
                                               len(result["excluded"])), ""]
    out += ["## Comparison", "",
            "| Provider | Price as stated | Price type | Against budget | Availability | Site visit | Included | "
            "Not included | Requirements | Status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        price, kind, budget = price_cells(r)
        out.append("| %s |" % " | ".join(cell(x) for x in (
            r["page"].name, price, kind, budget, availability(r), summary_value(r, "site_visit"),
            summary_value(r, "included"), summary_value(r, "excluded"), summary_value(r, "requirements"), r["status"])))
    out += ["", "Every value above is quoted from the provider's reply (`reply:`) or its published page (`published:`); "
            "the evidence for each follows. Nothing is totalled or estimated, and a value nobody stated reads %s. "
            "A price is an estimate when the provider's own words say so, and firm prices often need a site visit."
            % inline(NOT_STATED), ""]
    priced, diffs = coverage_differences(rows)
    out += ["## What the quotes cover", ""]
    if len(priced) < 2:
        out.append("- Fewer than two providers quoted a price in a reply, so there is nothing to compare item by item.")
    elif not diffs:
        out.append("- The quotes do not differ on any item a provider stated.")
    else:
        out.append("The quotes cover different things; compare these items before comparing prices:")
        out.append("")
        for item, states in diffs:
            out.append("- **%s**: %s" % (item, "; ".join("%s by %s" % (st[0], name) for name, st in states)))
            for name, st in states:
                if st[1]:
                    out.append("  - %s (%s): %s" % (name, st[2], inline(st[1])))
    out.append("")
    for r in rows:
        page = r["page"]
        out += ["## %s" % page.name, "", "Page: <%s> (%s; retrieved: %s)" % (page.url, page.label or "captured",
                                                                           page.retrieved or "not recorded"), ""]
        out += ["Verification (service and area, from the provider's own page):", ""]
        out += r["service"].lines() + r["area"].lines() + [""]
        out += ["Published channels:", ""]
        if r["channels"]:
            for key in WRITTEN_CHANNELS + ("phone",):
                if key in r["channels"]:
                    out += r["channels"][key].lines()
        else:
            out.append("- No contact channel published on the page.")
        out.append("")
        for label, claims in (("Published pricing", r["pricing"]), ("Included (published)", r["page_included"]),
                              ("Requirements (published)", r["page_requirements"])):
            if claims:
                out += ["%s:" % label, ""]
                for c in claims:
                    out += c.lines()
                out.append("")
        entry = r["entry"]
        out += ["Outreach: %s" % r["status"], ""]
        if entry:
            for a in entry.get("attempts", []):
                out.append("- %s%s: drafted %s, %s" % (CHANNEL_NAMES[a["channel"]], " (follow up)" if a.get("follow_up") else "",
                                                       a["drafted_utc"], "sent %s" % a["sent_utc"] if a.get("sent_utc") else "not sent"))
            if entry.get("reply"):
                text = entry["reply"]["text"]
                f = fence(text)
                out += ["", "Reply received %s, quoted as recorded:" % entry["reply"]["received_utc"], "", f, text, f]
            out.append("")
    out += ["## No response after the attempts listed", ""]
    silent = [r for r in rows if r["status"].startswith("no response after")]
    out += ["- %s: %s" % (r["page"].name, r["status"]) for r in silent] or ["- None."]
    if not result["window_closed"]:
        out.append("- The collection window is still open; providers awaiting a reply are not listed here yet.")
    out += ["", "## Phone only", ""]
    phone = [r for r in rows if r["entry"] and r["entry"].get("phone_only")]
    out += ["- %s: only a phone number is published (%s); flagged for the customer, not contacted in writing."
            % (r["page"].name, r["channels"]["phone"].value) for r in phone] or ["- None."]
    out += ["", "## Checked and excluded", ""]
    for page, reason, claim in result["excluded"]:
        out.append("- %s <%s>: %s" % (page.name, page.url, reason))
        if claim:
            out += ["  " + l for l in claim.lines()]
    if not result["excluded"]:
        out.append("- None.")
    out += ["", "## Next steps for the buyer", "", "The agent books nothing and accepts no quote; these are for you to decide.", ""]
    steps = []
    for r in rows:
        name = r["page"].name
        if availability(r) == "available as stated":
            steps.append("- %s replied with a price and availability; if you want to proceed, contact them yourself "
                         "or approve sharing your details." % name)
        if r["reply"]["site_visit"]:
            steps.append("- %s needs a site visit before a firm price; arrange one if you want a firm quote." % name)
        if r["entry"] and r["entry"].get("phone_only"):
            steps.append("- %s publishes only a phone number (%s); call them if you want a quote from them."
                         % (name, r["channels"]["phone"].value))
    for r in rows:
        if "OVER the budget limit" in price_cells(r)[2]:
            steps.append("- %s's stated price is over your budget limit; see the comparison." % r["page"].name)
    if diffs:
        steps.append("- The quotes cover different things (see What the quotes cover); compare like for like.")
    if len(replied) < 2:
        steps.append("- Fewer than two providers replied; widening the area or the timing may bring more quotes.")
    out += steps or ["- No provider has replied yet."]
    out += ["", "## Drafts recorded (not sent by this agent)", ""]
    for r in rows:
        for a in (r["entry"] or {}).get("attempts", []):
            f = fence(a["text"])
            out += ["%s, %s:" % (r["page"].name, CHANNEL_NAMES[a["channel"]]), "", f, a["text"], f, ""]
    out += ["## Sources", ""]
    out += ["- %s: <%s>" % (r["page"].name, r["page"].url) for r in rows]
    out += ["- %s: <%s>" % (p.name, p.url) for p, _, _ in result["excluded"]]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------- cli

def build_parser():
    p = argparse.ArgumentParser(prog="agents/local-quotes/local_quotes.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="render the comparison report; sends nothing")
    run.add_argument("--request", required=True)
    run.add_argument("--store", required=True)
    run.add_argument("--log")
    run.add_argument("--now", help="the report time, UTC (default: now)")
    run.add_argument("--out")
    for name, helptext in (("draft", "record first drafts for verified providers; sends nothing"),
                           ("follow-up", "record follow up drafts on the next published channel; sends nothing")):
        d = sub.add_parser(name, help=helptext)
        d.add_argument("--request", required=True)
        d.add_argument("--store", required=True)
        d.add_argument("--log", required=True)
        d.add_argument("--now", help="UTC (default: now)")
    sent = sub.add_parser("record-sent", help="record that the operator sent a draft through the published channel")
    sent.add_argument("provider_id")
    sent.add_argument("--log", required=True)
    sent.add_argument("--channel", required=True, choices=WRITTEN_CHANNELS)
    sent.add_argument("--when", required=True)
    reply = sub.add_parser("record-reply", help="record the provider's answer, verbatim")
    reply.add_argument("provider_id")
    reply.add_argument("--log", required=True)
    reply.add_argument("--when", required=True)
    reply.add_argument("--text", required=True)
    reply.add_argument("--stop", action="store_true", help="the provider asked not to be contacted again")
    send = sub.add_parser("send", help="live sending: refused without --execute and a hire id; no transport in this build")
    send.add_argument("provider_id")
    send.add_argument("--log", required=True)
    send.add_argument("--hire-id")
    send.add_argument("--execute", action="store_true")
    cap = sub.add_parser("capture", help="fetch one live provider page into a store with provenance")
    cap.add_argument("url")
    cap.add_argument("--store", required=True)
    cap.add_argument("--id", required=True, dest="provider_id")
    cap.add_argument("--name", required=True)
    return p


def main(argv=None, env=None, stdout=None, stderr=None, fetcher=None):
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    env = os.environ if env is None else env
    args = build_parser().parse_args(argv)
    try:
        now = getattr(args, "now", None) or utc_now()
        if args.command == "run":
            parse_utc(now, "--now")
            text = render(compare(load_request(args.request), load_store(args.store), load_log(args.log), now))
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
                stdout.write("report written to %s\n" % args.out)
            else:
                stdout.write(text)
            return 0
        if args.command in ("draft", "follow-up"):
            parse_utc(now, "--now")
            request, store, log = load_request(args.request), load_store(args.store), load_log(args.log)
            fn = draft_initial if args.command == "draft" else draft_follow_ups
            done = fn(request, store, log, now)
            save_log(args.log, log)
            stdout.write("%s: %d draft(s) recorded, nothing sent: %s\n" % (args.command, len(done), ", ".join(done) or "(none)"))
            return 0
        if args.command == "record-sent":
            log = load_log(args.log)
            record_sent(log, args.provider_id, args.channel, args.when)
            save_log(args.log, log)
            stdout.write("recorded: %s %s sent %s\n" % (args.provider_id, args.channel, args.when))
            return 0
        if args.command == "record-reply":
            log = load_log(args.log)
            record_reply(log, args.provider_id, args.when, args.text, stop=args.stop)
            save_log(args.log, log)
            stdout.write("recorded: %s replied %s\n" % (args.provider_id, args.when))
            return 0
        if args.command == "send":
            hire = args.hire_id or env.get(HIRE_ENV, "").strip()
            if not args.execute or not hire:
                raise ConfigError("send: refused. Live sending needs --execute and a hire id (--hire-id or %s); "
                                  "this build drafts and records only" % HIRE_ENV)
            raise ConfigError("send: no live transport is part of this build; under hire %s the operator sends the "
                              "recorded draft through the provider's published channel and runs record-sent" % hire)
        if args.command == "capture":
            rel, retrieved = capture(args.url, args.store, args.provider_id, args.name, fetcher or fetch_page)
            stdout.write("captured %s as %s at %s\n" % (args.url, rel, retrieved))
            return 0
        raise ConfigError("unknown command %s" % args.command)
    except (ConfigError, FetchError) as err:
        stderr.write("error: %s. No report emitted.\n" % err)
        return 2


if __name__ == "__main__":
    sys.exit(main())
