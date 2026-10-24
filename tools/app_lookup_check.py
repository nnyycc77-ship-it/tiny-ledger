#!/usr/bin/env python3
"""App lookup check: App Store apps matching a name.

Task: issue #167 (tool factory wave 1, parent #158). Given an app name,
this tool asks the public Apple iTunes Search API (keyless) for software
matching it and prints one Markdown section in the delivery format from
AGENT-BRIEF.md: claim lines for each returned app, then the source link
with the complete raw HTTP response transcript printed verbatim beneath
it.

What the claim lines say, all read from the response as shown:

* resultCount as shown, and the number of entries in the results array
  (a difference between the two is stated, never reconciled);
* per app, in response order: trackName, sellerName, averageUserRating
  and userRatingCount, and trackViewUrl (the store link), each as shown
  or "not shown" (numbers keep their literal text from the body); and
  whether trackName equals the searched name, ignoring case and spacing.
  The tool never decides which app the buyer means; the exact-name mark
  is a mechanical comparison only.

The search matches loosely: on #167 an invented name returned five
unrelated apps, not an empty list. So the "nothing found" case of this
tool is zero exact name matches, said in those terms with the complete
raw response beneath; a response with no results at all is printed the
same way. Neither is ever claimed as proof that no such app exists. Fail closed: a
response that is not HTTP 200, a body that is not a JSON object with
resultCount and a results array, or a transport failure prints nothing on
stdout and exits 2.

Usage, with an example app name:

    python3 tools/app_lookup_check.py "Nike"

Standard library only. No key, account, or environment value is needed.
"""

import argparse
import decimal
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SEARCH_URL = "https://itunes.apple.com/search"
USER_AGENT = "tiny-ledger-app-lookup-check"
TIMEOUT_SECONDS = 30
DEFAULT_COUNTRY = "us"
DEFAULT_LIMIT = 10
MAX_LIMIT = 200  # "Values: 1 to 200", Apple's Searching page, as captured on #167
FIELDS = [("trackName", "App name"), ("sellerName", "Seller"), ("averageUserRating", "Average user rating"),
          ("userRatingCount", "User rating count"), ("trackViewUrl", "Store link")]
SCOPE_LINE = ("Observation only: the apps below are what the public iTunes Search API returned for "
              "this search at the stated time, in the order returned. Ratings and listings change; "
              "this is not a review of any app.")


class FetchError(Exception):
    """A response that cannot be reported. Never rendered as an empty result."""


# ----------------------------------------------------------------------
# Inputs and URL
# ----------------------------------------------------------------------

def check_inputs(term, country=DEFAULT_COUNTRY, limit=DEFAULT_LIMIT):
    term = " ".join(str(term or "").split())
    if not term:
        raise ValueError("give an app name to search for")
    country = str(country or "").strip().lower()
    if not re.fullmatch(r"[a-z]{2}", country):
        raise ValueError("country must be a two letter store code, got %r" % country)
    if not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be between 1 and %d" % MAX_LIMIT)
    return term, country, limit


def search_url(term, country=DEFAULT_COUNTRY, limit=DEFAULT_LIMIT):
    return SEARCH_URL + "?" + urllib.parse.urlencode(
        [("term", term), ("country", country), ("entity", "software"), ("limit", limit)])


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
    """One HTTP exchange: URL, UTC retrieval time, status line, headers in
    the order returned, body as returned."""

    def __init__(self, url, retrieved, status_line, headers, body):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers
        self.body = body

    @property
    def transcript(self):
        return "\n".join([self.status_line] + self.headers + ["", self.body])

    @property
    def status(self):
        """The status code: the first three digit field of the status line.
        (A capture on #167 carries the line "HTTP/1.1 HTTP/1.1 200 OK" as
        posted, so the code is not always the second field.)"""
        m = re.search(r"(?:^|\s)(\d{3})(?:\s|$)", self.status_line)
        if not m:
            raise FetchError("%s: no status code in the status line %r" % (self.url, self.status_line))
        return int(m.group(1))

    @property
    def status_text(self):
        m = re.search(r"(?:^|\s)(\d{3}(?:\s.*)?)$", self.status_line)
        return m.group(1) if m else self.status_line


def fetch(url):
    """GET the search URL. HTTP error statuses are captured, not raised;
    transport errors propagate."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body = response.read().decode("utf-8")
    return Capture(url, retrieved, status_line, headers, body)


# ----------------------------------------------------------------------
# Reading and rendering
# ----------------------------------------------------------------------

def parse(capture):
    """(resultCount, results) of a search response; refuses anything but
    HTTP 200 with a JSON object holding resultCount and a results array of
    objects."""
    if capture.status != 200:
        raise FetchError("%s answered %s, not 200; no report" % (capture.url, capture.status_line))
    try:
        # Numbers are kept as their literal text (a rating such as
        # 4.8885600000000000164845914696343243122100830078125 prints as shown).
        data = json.loads(capture.body, parse_float=decimal.Decimal)
    except ValueError as err:
        raise FetchError("%s body is not JSON (%s); no report" % (capture.url, err))
    if (not isinstance(data, dict) or "resultCount" not in data or not isinstance(data.get("results"), list)
            or any(not isinstance(r, dict) for r in data["results"])):
        raise FetchError("%s body is not an object with resultCount and a results array; no report" % capture.url)
    return data["resultCount"], data["results"]


def shown(record, key):
    if key not in record or record[key] is None or record[key] == "":
        return "not shown"
    value = record[key]
    if isinstance(value, str):
        return value
    if isinstance(value, decimal.Decimal):
        return str(value)
    return json.dumps(value)


def inline(text):
    ticks = "``" if "`" in text else "`"
    pad = " " if ticks == "``" else ""
    return "%s%s%s%s%s" % (ticks, pad, text, pad, ticks)


def norm(text):
    return " ".join(str(text or "").lower().split())


def render(term, country, limit, capture):
    count, results = parse(capture)
    lines = ["## App search: %s" % term, "", SCOPE_LINE, ""]
    lines.append("QUERY: iTunes Search API, term = %s, country = %s, entity = software, limit = %d "
                 "(retrieved %s; source S1). HTTP status as returned: %s."
                 % (inline(term), country, limit, capture.retrieved, capture.status_text))
    line = "resultCount as shown: %s. Entries in the results array: %d." % (json.dumps(count), len(results))
    if count != len(results):
        line += " The two differ; both are shown as returned."
    lines += [line, ""]
    if not results:
        lines += ["The search returned no apps. The complete raw response is in source S1; this is a search "
                  "observation, not proof that no such app exists.", ""]
    exact = 0
    for i, record in enumerate(results, 1):
        match = norm(record.get("trackName")) == norm(term)
        exact += match
        lines.append("### App %d of %d" % (i, len(results)))
        lines.append("")
        for key, label in FIELDS:
            lines.append("- %s (%s) as shown: %s" % (label, key, inline(shown(record, key))))
        lines.append("- trackName equals the searched name, ignoring case and spacing: %s." % ("yes" if match else "no"))
        lines.append("")
    if results:
        lines += ["Exact name matches among the returned apps: %d of %d (source S1)." % (exact, len(results)), ""]
        if not exact:
            lines += ["No returned app is named %s, ignoring case and spacing. The search matches loosely: "
                      "it returned %d app%s, and none of them carries the searched name (source S1). This is "
                      "a search observation, not proof that no such app exists."
                      % (inline(term), len(results), "" if len(results) == 1 else "s"), ""]
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines += ["## Sources", "",
              "### Source. S1. iTunes Search API, term %s" % inline(term),
              "- Request URL: %s" % capture.url,
              "- Retrieved (UTC): %s" % capture.retrieved,
              "Excerpt (complete raw HTTP response transcript for the request above: status line, headers in "
              "the order returned, a blank line, then the body exactly as returned):",
              fence] + capture.transcript.split("\n") + [fence]
    return lines


def run(term, country=DEFAULT_COUNTRY, limit=DEFAULT_LIMIT, fetcher=None):
    term, country, limit = check_inputs(term, country, limit)
    capture = (fetcher or fetch)(search_url(term, country, limit))
    return render(term, country, limit, capture)


def main(argv=None):
    parser = argparse.ArgumentParser(description="App Store apps matching a name, in the delivery format.")
    parser.add_argument("name", help="app name to search for")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="two letter store code; default us")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="results to ask for, 1 to %d; default %d" % (MAX_LIMIT, DEFAULT_LIMIT))
    args = parser.parse_args(argv)
    try:
        lines = run(args.name, args.country, args.limit)
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    except FetchError as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
