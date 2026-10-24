#!/usr/bin/env python3
"""Bank check (issue #320, tool factory wave 3, tool 5).

Given the start of a US bank's name, reads the FDIC BankFind Institutions
API once, keyless, and prints one Markdown report in the delivery format
from AGENT-BRIEF.md: the matching institutions with FDIC certificate
number, city and state, and active status, each as shown, with the
complete raw response beneath the source link.

    python3 tools/bank_check.py "JPMorgan Chase Bank"

Source: GET https://banks.data.fdic.gov/api/Institutions, the FDIC
BankFind API. It answered full real data with no api_key at all in the
wave 3 source check (issue #305 research); an invalid key is refused
outright, so no key parameter is ever sent. Money fields are not
requested and never printed: FDIC reports money in thousands of dollars,
and this tool does not need them.

How the name search works, stated in every report: the API's NAME filter
is a prefix match on the whole name field (verified live on issue #320:
NAME:Chase* returns only names beginning with Chase, and the quoted
phrase NAME:"JPMorgan Chase Bank" returns total 0 for a bank that
exists, so the phrase form is never used). The tool therefore sends the
typed name's first word with a trailing wildcard (NAME:{first word}*),
with a page limit of 5000, and then keeps, locally, the institutions
whose normalised name begins with the whole typed name at a word
boundary. Normalising folds case, removes accents where Unicode
decomposition splits them off, and replaces every other non letter or
digit character with a space. So the name must be typed as FDIC lists
it, from its start: "JPMorgan Chase Bank" finds JPMorgan Chase Bank,
National Association, while "Chase Bank" alone cannot, and the report
says so.

Outcomes: a 200 answer is a report, including a proven no match (the
page total and the local rule are stated, and the full raw response is
the proof). If the page total exceeds the page the tool fetched, the
run stops instead: the page is not the whole candidate set, so a no
match could not be proven. Any other status, a failed request, or a
body that is not the documented shape also stops the run with exit 2
and no report: a failed fetch is unknown, never a negative claim.

Standard library only.
"""

import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

API_URL = "https://banks.data.fdic.gov/api/Institutions"
HOST = "banks.data.fdic.gov"
FINAL_HOSTS = (HOST, "api.fdic.gov")  # the API redirects to api.fdic.gov/banks/... as returned
USER_AGENT = "tiny-ledger-bank-check"
TIMEOUT_SECONDS = 60
FIELDS = "NAME,CERT,CITY,STNAME,ACTIVE"
PAGE_LIMIT = 5000
ROW_FIELDS = ("NAME", "CERT", "CITY", "STNAME", "ACTIVE")
FIRST_WORD_RE = re.compile(r"^[^\s*:?\"()\[\]{}]+$")
OBSERVATION = ("Observation only: this report records what the FDIC BankFind Institutions API returned "
               "for this name at the retrieval time stated below, without any API key.")
RULE = ("How the match works: the API's NAME filter is a prefix match on the whole name field, so the "
        "request below asks for every institution whose name begins with the typed name's first word; "
        "from that page, this report keeps the institutions whose name, after folding case and accents "
        "and replacing every other non letter or digit character with a space, begins with the whole "
        "typed name at a word boundary. Type the name as FDIC lists it, from its start.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, final_url, retrieved, status, status_line, headers, body):
        self.url = url
        self.final_url = final_url
        self.retrieved = retrieved
        self.status = status
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        return "\n".join([self.status_line] + ["%s: %s" % kv for kv in self.headers] + ["", self.body])


def fold_accents(text):
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalise(text):
    """Case and accents folded, every non letter or digit a single space, trimmed."""
    return " ".join(re.sub(r"[^0-9a-z]+", " ", fold_accents(text.casefold())).split())


def significant(text):
    return len(normalise(text).replace(" ", ""))


def check_name(value):
    text = (value or "").strip()
    if significant(text) < 3:
        raise ValueError("bank name must have at least 3 letters or digits (got %r)" % value)
    first = text.split()[0]
    if not FIRST_WORD_RE.match(first) or significant(first) < 2:
        raise ValueError("the name's first word %r cannot be used as the search prefix: it must have at "
                         "least 2 letters or digits and no filter characters (space, *, ?, \", :, "
                         "brackets)" % first)
    return text


def search_url(name):
    first = name.split()[0]
    params = {"filters": "NAME:%s*" % first, "fields": FIELDS, "format": "json",
              "limit": str(PAGE_LIMIT), "sort_by": "NAME", "sort_order": "ASC"}
    return API_URL + "?" + urllib.parse.urlencode(params)


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if urllib.parse.urlsplit(final_url).netloc not in FINAL_HOSTS:
        raise FetchError("%s was redirected to %s, which is not an FDIC host this tool accepts; "
                         "no report" % (url, urllib.parse.urlsplit(final_url).netloc))
    capture = Capture(url, final_url, retrieved, status, status_line, headers, body)
    if status != 200:
        raise FetchError("%s answered %s; no report, and this is not a no match" % (url, status_line))
    return capture


def parse_page(capture):
    """(meta, rows) from a 200 body, or FetchError when the shape is not the documented one."""
    try:
        doc = json.loads(capture.body)
        meta, rows, totals = doc["meta"], doc["data"], doc["totals"]
        total = meta["total"]
        if not isinstance(total, int) or not isinstance(rows, list) or totals.get("count") != total:
            raise ValueError("meta.total or totals.count is not the documented shape")
        index = meta["index"]
        index_name, index_built = index["name"], index["createTimestamp"]
    except (ValueError, KeyError, TypeError, AttributeError) as err:
        raise FetchError("%s answered a body that is not the documented Institutions shape (%s); "
                         "no report" % (capture.url, err))
    if total > len(rows):
        raise FetchError("the API reports %d institutions under this prefix but returned %d rows; the "
                         "page is not the whole candidate set, so no result can be proven; no report"
                         % (total, len(rows)))
    cleaned = []
    for entry in rows:
        try:
            row = entry["data"]
        except (KeyError, TypeError) as err:
            raise FetchError("%s answered a row without its data object (%s); no report" % (capture.url, err))
        cleaned.append(row)
    return (total, index_name, index_built), cleaned


def matches(name, rows):
    """Rows whose normalised NAME begins with the normalised typed name at a word boundary."""
    wanted = normalise(name)
    kept = []
    for row in rows:
        shown = row.get("NAME")
        if not isinstance(shown, str):
            raise FetchError("a returned row carries no NAME as shown; no report")
        norm = normalise(shown)
        if norm == wanted or norm.startswith(wanted + " "):
            kept.append(row)
    return kept


def render(name, capture):
    (total, index_name, index_built), rows = parse_page(capture)
    kept = matches(name, rows)
    for row in kept:
        missing = [f for f in ROW_FIELDS if f not in row]
        if missing:
            raise FetchError("a matching row is missing %s as shown; no report" % ", ".join(missing))
    lines = ["# Bank check: %s" % name, "", OBSERVATION, "",
             "Exact query: GET %s" % capture.url,
             "Sent with no api_key parameter (keyless).",
             "Retrieved (UTC): %s" % capture.retrieved] + (
             ["Answered from: %s (the API redirected the request)" % capture.final_url]
             if capture.final_url != capture.url else []) + [
             "FDIC index snapshot as returned: %s (createTimestamp %s)" % (index_name, index_built),
             "", RULE, "",
             "The prefix page holds %d institution(s); %d match the typed name under the rule above."
             % (total, len(kept)), ""]
    if not kept:
        lines += ["No institution in this FDIC index snapshot has a name beginning with \"%s\" under "
                  "that rule. The complete raw response below is the proof." % name, ""]
    for row in kept:
        active = row["ACTIVE"]
        reading = {1: "active", 0: "not active"}.get(active, "as shown")
        lines += ["## %s" % row["NAME"], "",
                  "- FDIC certificate number (CERT) as shown: %s" % json.dumps(row["CERT"]),
                  "- City (CITY) as shown: %s" % row["CITY"],
                  "- State (STNAME) as shown: %s" % row["STNAME"],
                  "- Active status (ACTIVE) as shown: %s (%s)" % (json.dumps(active), reading), ""]
    lines += ["Source: <%s>" % capture.url,
              "\n".join(["```", capture.transcript(), "```"])]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Keyless FDIC BankFind check: institutions whose FDIC name "
                                            "begins with the typed name, with certificate number, city, "
                                            "state and active status.")
    p.add_argument("name", help="the start of the bank's name as FDIC lists it, e.g. 'JPMorgan Chase Bank'")
    args = p.parse_args(argv)
    try:
        name = check_name(args.name)
        capture = (fetcher or fetch)(search_url(name))
        lines = render(name, capture)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
