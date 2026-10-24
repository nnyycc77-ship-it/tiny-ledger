#!/usr/bin/env python3
"""FDA enforcement recall check (issue #177, tool factory wave 2).

Given a product, device or firm name, searches the openFDA food and device
enforcement endpoints, keyless, and prints one Markdown report in the
delivery format from AGENT-BRIEF.md: the matching enforcement records with
their classification, status and dates verbatim, then for each query the
exact URL sent, the UTC retrieval time, each matched record as raw JSON,
and the complete raw response.

    python3 tools/fda_recall_check.py "peanut butter"
    python3 tools/fda_recall_check.py "Covidien" --field firm --category device

Source: GET https://api.fda.gov/{food,device}/enforcement.json with
search=<field>:"<term>" and limit. Grounding, all from the coordinator's
keyless captures and documentation excerpts on issue #177 (comments
6379963916 to 6379964994):
- The exact phrase form, search=product_description:%22peanut+butter%22,
  is the one the captures sent. limit is at most 1000 per the query
  parameters page; this tool caps it lower to keep reports readable.
- The record fields printed (recall_number, classification, status,
  product_description, recalling_firm, reason_for_recall,
  recall_initiation_date, report_date, center_classification_date,
  termination_date) are the ones the captured records carry. Ongoing
  recalls in the captures have no termination_date; that is shown as not
  in the record. Dates are printed exactly as returned (YYYYMMDD strings).
- Keyless: openFDA's authentication page, quoted on #177, gives "With no
  API key: 240 requests per minute, per IP address. 1,000 requests per day,
  per IP address." All four captures were made with no key. This tool never
  sends a key: the response's Link header echoes the query string, so a key
  sent as api_key could be printed back into a report.

Outcomes, as the captures prove them: 200 is a report of the records. 404
whose body's error code is NOT_FOUND ("No matches found!") is openFDA's
empty result and is reported with its complete raw response as the proof;
it is never a clearance. Any other status (the 500 SERVER_ERROR answer to a
malformed search, for example), a failed request, a redirect off
api.fda.gov, or a body not in the captured shape stops the run with exit 2
and no report, naming the source, the query and the reason.

Standard library only.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import Node, fenced, inline, skip_ws  # noqa: E402

API_URL = "https://api.fda.gov/{category}/enforcement.json"
HOST = "api.fda.gov"
CATEGORIES = ("food", "device")
FIELDS = {"product": "product_description", "firm": "recalling_firm"}
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
MIN_TERM_CHARS = 2
MAX_TERM_CHARS = 100
USER_AGENT = "tiny-ledger-fda-recall-check"
TIMEOUT_SECONDS = 30
RECORD_FIELDS = ("recall_number", "classification", "status", "product_description", "recalling_firm",
                 "reason_for_recall", "recall_initiation_date", "report_date")
OPTIONAL_FIELDS = ("center_classification_date", "termination_date")
NOT_A_CLEARANCE = ("This is the answer to this exact search only, not a clearance: other spellings, the other "
                   "search field, and recalls outside openFDA's enforcement reports are not covered.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, retrieved, status, status_line, headers, body):
        self.url = url
        self.retrieved = retrieved
        self.status = status
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        return "\n".join([self.status_line] + ["%s: %s" % kv for kv in self.headers] + ["", self.body])


# ----------------------------------------------------------------------
# Inputs and URLs
# ----------------------------------------------------------------------

def check_inputs(term, field="product", category="both", limit=DEFAULT_LIMIT):
    """(term, search field, [categories], limit), or ValueError."""
    text = " ".join((term or "").split())
    if not MIN_TERM_CHARS <= len(text) <= MAX_TERM_CHARS:
        raise ValueError("the name must be %d to %d characters" % (MIN_TERM_CHARS, MAX_TERM_CHARS))
    if '"' in text or "\\" in text:
        raise ValueError("the name may not contain a double quote or a backslash (it is sent as one quoted phrase)")
    if field not in FIELDS:
        raise ValueError("field must be one of %s" % ", ".join(FIELDS))
    if category not in CATEGORIES + ("both",):
        raise ValueError("category must be food, device or both")
    if not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be 1 to %d" % MAX_LIMIT)
    return text, FIELDS[field], list(CATEGORIES) if category == "both" else [category], limit


def search_url(category, search_field, term, limit):
    search = "%s:%s" % (search_field, urllib.parse.quote_plus('"%s"' % term))
    return "%s?search=%s&limit=%d" % (API_URL.format(category=category), search, limit)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200 and 404; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("openFDA request %s failed: %s; no report" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("openFDA request %s answered a body that could not be read: %s; no report" % (url, err))
    if urllib.parse.urlsplit(final_url).netloc != HOST:
        raise FetchError("openFDA request %s was redirected off %s; no report" % (url, HOST))
    capture = Capture(url, retrieved, status, status_line, headers, body)
    if status not in (200, 404):
        raise FetchError("openFDA request %s answered %s%s; no report" % (url, status_line, error_text(capture)))
    return capture


def error_text(capture):
    """': CODE: message (details)' from an openFDA error body, or ''."""
    try:
        err = json.loads(capture.body)["error"]
        parts = [str(err.get("code")), str(err.get("message"))] + ([str(err["details"])] if "details" in err else [])
        return ": " + "; ".join(parts)
    except (ValueError, KeyError, TypeError, AttributeError):
        return ""


# ----------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------

def root(capture):
    try:
        return Node(capture.body, skip_ws(capture.body, 0))
    except (ValueError, IndexError) as err:
        raise FetchError("openFDA request %s answered a body that is not a JSON object (%s); no report"
                         % (capture.url, err))


def is_empty_result(capture):
    """True for the captured empty shape: 404 with error code NOT_FOUND."""
    if capture.status != 404:
        return False
    node = root(capture)
    try:
        if node.child("error").value("code") == "NOT_FOUND":
            return True
    except (ValueError, IndexError, KeyError):
        pass
    raise FetchError("openFDA request %s answered %s without the NOT_FOUND error code%s; no report"
                     % (capture.url, capture.status_line, error_text(capture)))


def records(capture):
    """(total as shown, [record Nodes]). Raises FetchError when the body is not the captured shape."""
    node = root(capture)
    try:
        total = node.child("meta").child("results").value("total")
        out = node.children("results")
        for rec in out:
            missing = [f for f in RECORD_FIELDS if not rec.has(f)]
            if missing:
                raise ValueError("a record has no %s" % ", ".join(missing))
        if not isinstance(total, int) or isinstance(total, bool) or total < len(out):
            raise ValueError("meta.results.total is %r for %d records" % (total, len(out)))
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("openFDA request %s answered a body that is not the captured enforcement shape (%s); "
                         "no report" % (capture.url, err))
    return total, out


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def record_lines(i, rec):
    lines = ["#### %d. %s, %s" % (i, rec.value("recall_number"), rec.value("classification"))]
    for key in RECORD_FIELDS + OPTIONAL_FIELDS:
        lines.append("- %s: %s" % (key, inline(rec.literal(key)) if rec.has(key) else "not in the record"))
    return lines + [""]


def category_section(category, term, search_field, capture):
    title = "%s enforcement" % category.capitalize()
    lines = ["## %s: %s %s" % (title, search_field, inline('"%s"' % term)), ""]
    if is_empty_result(capture):
        lines += ["No %s enforcement record matched. openFDA answered %s with error code NOT_FOUND; the complete "
                  "raw response below is the proof. %s" % (category, capture.status_line, NOT_A_CLEARANCE), ""]
        recs = []
    else:
        total, recs = records(capture)
        lines += ["openFDA reports %d matching %s enforcement record%s (meta.results.total as shown); %s listed "
                  "below, in the order returned." % (total, category, "" if total == 1 else "s",
                                                     "all are" if len(recs) == total else "the first %d are" % len(recs)),
                  ""]
        for i, rec in enumerate(recs, 1):
            lines += record_lines(i, rec)
    lines += ["### Evidence", "", "Exact query: GET %s" % capture.url, "Sent keyless (no api_key).",
              "Retrieved (UTC): %s" % capture.retrieved, ""]
    if recs:
        lines += ["Matched records, raw from the response:"]
        lines += [fenced(rec.whole()) for rec in recs]
        lines.append("")
    lines += ["Source: <%s>" % capture.url, fenced(capture.transcript()), ""]
    return lines


def report(term, search_field, categories, limit, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    captures = [(c, fetcher(search_url(c, search_field, term, limit))) for c in categories]
    lines = ["# FDA enforcement recall check: %s" % term, "",
             "Observation only: this report records what the public openFDA enforcement endpoints returned for "
             "this search at the retrieval time stated below. openFDA's own disclaimer, as each response gives it, "
             "is in the raw responses.", ""]
    for category, capture in captures:
        lines += category_section(category, term, search_field, capture)
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Keyless openFDA food and device enforcement recall search.")
    p.add_argument("name", help="a product, device or firm name, searched as one quoted phrase")
    p.add_argument("--field", default="product", help="product (product_description, default) or firm "
                                                      "(recalling_firm)")
    p.add_argument("--category", default="both", help="food, device or both (default)")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="records per category, 1 to %d" % MAX_LIMIT)
    args = p.parse_args(argv)
    try:
        term, search_field, categories, limit = check_inputs(args.name, args.field, args.category, args.limit)
        lines = report(term, search_field, categories, limit, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
