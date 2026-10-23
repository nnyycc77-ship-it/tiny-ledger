#!/usr/bin/env python3
"""PageSpeed Insights snapshot fetcher.

Measures up to five page URLs with the public Google PageSpeed Insights
API (v5 runPagespeed, which runs Lighthouse against the live page) and
prints one Markdown section in the delivery format from AGENT-BRIEF.md:
per page, the claim lines (category scores and the lab metrics behind the
performance score, each as shown in the response), then the source link
(the exact request URL) with the complete raw HTTP response transcript
printed verbatim directly beneath it. The report is a snapshot of the
moment it was run, not a permanent grade.

Key: this source needs a free API key for any real quota. A keyless
request from this environment was answered live on 2026-10-23 with
HTTP 429 and the body "Quota exceeded for quota metric 'Queries' and
limit 'Queries per day' ... quota_limit_value 0" (the capture is in
tools/tests/fixtures/pagespeed/ with its provenance). If the environment
variable PAGESPEED_API_KEY is set, its value is sent as the API's key
parameter. The key value is never printed: the recorded request URL
shows key=<redacted, supplied from the environment>, and if the value
ever appears in a response body it is replaced by a marker and the
section says so. No key is ever written to any file in this repo.
Standard library only. The only network calls are the GETs to
www.googleapis.com, one per page.

Usage examples:

    python3 tools/pagespeed_snapshot.py https://example.com/
    python3 tools/pagespeed_snapshot.py --strategy desktop \
        https://example.com/ https://example.com/about
    PAGESPEED_API_KEY=... python3 tools/pagespeed_snapshot.py \
        --subject "Example site" https://example.com/ \
        --exclude https://example.com/about="redirects to a login page; not a public page"

What the output contains, in order:

1. The subject heading, the fixed scope line (a snapshot of one run at
   a stated time, not a permanent grade), and the method line.
2. One section per page, in the order given: the QUERY line with the
   exact request (key redacted), the strategy, the UTC retrieval time
   and the HTTP status; then for a 200 JSON response the four category
   scores and the three lab metrics as shown, each with the field path
   it was read from; a field not present is "not shown". For any other
   status the section says the API could not measure the page, quotes
   the error fields as shown, and never drops the page.
3. Pages named with --exclude are fetched and printed the same way
   under "Checked and excluded", with the operator's reason.
4. Sources: one entry per page with the request URL, the UTC time and
   the complete raw HTTP response transcript (status line, headers in
   the order returned, a blank line, then the body exactly as returned).

A transport failure (no connection, blocked host, timeout) prints nothing
on stdout and exits 2: a failed fetch is never shown as a result. The
tool never judges relevance; --exclude carries the operator's reason and
is refused for a URL that is not among the pages given.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]
METRICS = [
    ("Largest Contentful Paint", "largest-contentful-paint"),
    ("Cumulative Layout Shift", "cumulative-layout-shift"),
    ("Total Blocking Time", "total-blocking-time"),
]
STRATEGIES = ("mobile", "desktop")
MAX_PAGES = 5
KEY_ENV = "PAGESPEED_API_KEY"
KEY_MARKER = "<redacted, supplied from the environment>"
TIMEOUT_SECONDS = 180
SCOPE_LINE = ("Snapshot only: the figures below are what the PageSpeed Insights API "
              "returned for each page at the stated time. Scores change from run to "
              "run; this is not a permanent grade, an audit, or a ranking prediction.")


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_url(value):
    value = str(value).strip()
    parts = urllib.parse.urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("a page URL must start with http:// or https:// and name a host, got %r" % value)
    return value


def request_params(page_url, strategy):
    if strategy not in STRATEGIES:
        raise ValueError("--strategy must be one of %s" % ", ".join(STRATEGIES))
    params = [("url", check_url(page_url)), ("strategy", strategy)]
    params.extend(("category", c) for c in CATEGORIES)
    return params


def request_url(page_url, strategy, key=None):
    params = request_params(page_url, strategy)
    if key:
        params.append(("key", key))
    return API_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def recorded_url(page_url, strategy, key_used):
    """The request URL as recorded in the report: identical to the one
    sent, except that a key value is replaced by the redaction marker."""
    url = request_url(page_url, strategy)
    if key_used:
        url += "&key=" + KEY_MARKER
    return url


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
    def __init__(self, url, retrieved, status_line, headers, body, redactions=0):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers
        self.body = body
        self.redactions = redactions

    @property
    def transcript(self):
        return "\n".join([self.status_line] + self.headers + ["", self.body])

    @property
    def status_ok(self):
        return self.status_line.split(" ", 2)[1:2] == ["200"]

    @property
    def status_text(self):
        return self.status_line.split(" ", 1)[1]


def fetch(url, key=None, recorded=None):
    """GET the URL and return a Capture. HTTP error statuses are captured
    rather than raised. Transport errors propagate. The key value, if
    any, is removed from the transcript wherever it appears and the
    Capture counts the removals."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "tiny-ledger-pagespeed-fetcher"}
    )
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body = response.read().decode("utf-8")
    redactions = 0
    if key:
        for text in (body, "\n".join(headers)):
            redactions += text.count(key)
        body = body.replace(key, "[key value redacted]")
        headers = [h.replace(key, "[key value redacted]") for h in headers]
    return Capture(recorded or url, retrieved, status_line, headers, body, redactions)


# ----------------------------------------------------------------------
# Response reading
# ----------------------------------------------------------------------

def parse_json(body):
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("response body is not a JSON object")
    return data


def dig(data, path):
    """Follow a dotted path through nested dicts. Returns (found, value)."""
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def shown(found, value):
    if not found or value is None:
        return "not shown"
    return json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value


def page_claims(data):
    """Claim lines for a 200 JSON response. Every value is read from a
    named field path and printed as shown; a missing path is 'not shown'.
    The paths follow the Lighthouse result shape the API returns under
    lighthouseResult; they are printed so a reader can check them against
    the transcript."""
    lines = []
    f, v = dig(data, "lighthouseResult.finalUrl")
    lines.append("- Final URL as shown (lighthouseResult.finalUrl): %s" % shown(f, v))
    f, v = dig(data, "lighthouseResult.fetchTime")
    lines.append("- Fetch time as shown (lighthouseResult.fetchTime): %s" % shown(f, v))
    f, v = dig(data, "lighthouseResult.lighthouseVersion")
    lines.append("- Lighthouse version as shown (lighthouseResult.lighthouseVersion): %s" % shown(f, v))
    lines.append("")
    lines.append("| Category | Score as shown in the response | Field path read |")
    lines.append("|---|---|---|")
    for cat in CATEGORIES:
        path = "lighthouseResult.categories.%s.score" % cat
        f, v = dig(data, path)
        lines.append("| %s | %s | `%s` |" % (cat, shown(f, v), path))
    lines.append("")
    lines.append("Scores are copied as the response shows them, in the response's own scale, with no rounding or conversion.")
    lines.append("")
    lines.append("| Metric | Display value as shown | Numeric value as shown | Numeric unit as shown | Field path read |")
    lines.append("|---|---|---|---|---|")
    for label, audit in METRICS:
        base = "lighthouseResult.audits.%s" % audit
        fd, vd = dig(data, base + ".displayValue")
        fn, vn = dig(data, base + ".numericValue")
        fu, vu = dig(data, base + ".numericUnit")
        lines.append("| %s | %s | %s | %s | `%s` |" % (label, shown(fd, vd), shown(fn, vn), shown(fu, vu), base))
    return lines


def error_claims(data):
    lines = []
    for label, path in [("Error code", "error.code"), ("Error status", "error.status"), ("Error message", "error.message")]:
        f, v = dig(data, path)
        lines.append("- %s as shown (%s): %s" % (label, path, shown(f, v)))
    return lines


# ----------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------

def parse_exclusions(values, pages):
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError("--exclude needs the form URL=reason, got %r" % value)
        url, reason = value.rsplit("=", 1) if value.count("=") == 1 else _split_url_reason(value)
        url = url.strip()
        reason = reason.strip().strip('"').strip("'")
        if not url or not reason:
            raise ValueError("--exclude needs both a URL and a reason, got %r" % value)
        if url not in pages:
            raise ValueError("--exclude names a URL that is not among the pages given: %s" % url)
        exclusions[url] = reason
    return exclusions


def _split_url_reason(value):
    """URLs can contain '='. Split at the first '=' that follows a quote
    or is the last one; the reason is the operator's text."""
    m = re.match(r'^(\S+?)=(["\'].*|[^=]*)$', value)
    if m:
        return m.group(1), m.group(2)
    url, reason = value.rsplit("=", 1)
    return url, reason


def source_block(index, page_url, capture):
    lines = ["### Source. S%d. PageSpeed Insights API, page %s" % (index, page_url),
             "- Request URL: %s" % capture.url,
             "- Retrieved (UTC): %s" % capture.retrieved]
    if capture.redactions:
        lines.append("- Note: the API key value appeared %d time(s) in the response and was replaced by "
                     "[key value redacted]; nothing else in the transcript was changed." % capture.redactions)
    lines.append("Excerpt (complete raw HTTP response transcript for the request above: status line, "
                 "headers in the order returned, a blank line, then the complete body exactly as returned):")
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines.append(fence)
    lines.extend(capture.transcript.split("\n"))
    lines.append(fence)
    return lines


def page_section(number, page_url, strategy, capture, source_index, heading="## Page"):
    lines = ["%s %d: %s" % (heading, number, page_url), ""]
    lines.append("QUERY: runPagespeed for url = %s with strategy = %s and the four categories "
                 "(retrieved %s; source S%d). HTTP status as returned: %s."
                 % (page_url, strategy, capture.retrieved, source_index, capture.status_text))
    data, error = None, None
    try:
        data = parse_json(capture.body)
    except ValueError as err:
        error = str(err)
    lines.append("")
    if not capture.status_ok:
        lines.append("The API could not measure this page: the response status is %s, not 200. The "
                     "complete raw response is printed in source S%d; nothing is claimed about the page."
                     % (capture.status_text, source_index))
        if data is not None:
            lines.append("")
            lines.extend(error_claims(data))
        elif error:
            lines.append("")
            lines.append("- The response body is not JSON (%s); read it in source S%d." % (error, source_index))
    elif data is None:
        lines.append("The response status is 200 but the body is not a JSON object (%s). Nothing is "
                     "claimed about the page; the complete raw response is printed in source S%d."
                     % (error, source_index))
    else:
        lines.extend(page_claims(data))
    return lines


def render_report(subject, pages, strategy, captures, exclusions=None):
    """pages: ordered list of URLs; captures: {url: Capture}."""
    exclusions = dict(exclusions or {})
    lines = ["## Subject: %s" % subject, "", SCOPE_LINE, ""]
    lines.append("Method: each page was measured once with the public Google PageSpeed Insights API "
                 "(v5 runPagespeed, which runs Lighthouse against the live page), strategy %s, "
                 "requesting the performance, accessibility, best-practices and seo categories. "
                 "Every figure below is copied from the response as shown, with the field path it "
                 "was read from, and the complete raw response of every request is printed in the "
                 "Sources section directly beneath its request URL. A page the API could not "
                 "measure keeps its section and its full error response." % strategy)
    lines.append("")
    kept = [p for p in pages if p not in exclusions]
    excluded = [p for p in pages if p in exclusions]
    source_index = {p: i + 1 for i, p in enumerate(pages)}
    for n, p in enumerate(kept, 1):
        lines.extend(page_section(n, p, strategy, captures[p], source_index[p]))
        lines.append("")
    if excluded:
        lines.append("## Checked and excluded")
        lines.append("")
        lines.append("%d page%s measured and listed here with the operator's reason instead of above. "
                     "The response is printed in full in the Sources section like any other."
                     % (len(excluded), " was" if len(excluded) == 1 else "s were"))
        lines.append("")
        for n, p in enumerate(excluded, 1):
            lines.extend(page_section(n, p, strategy, captures[p], source_index[p], heading="### Excluded page"))
            lines.append("- Checked and excluded because: %s" % exclusions[p])
            lines.append("")
    lines.append("## Sources")
    lines.append("")
    for p in pages:
        lines.extend(source_block(source_index[p], p, captures[p]))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure up to five pages with the PageSpeed Insights API and print one Markdown section in the delivery format.")
    parser.add_argument("pages", nargs="+", metavar="URL", help="page URL to measure (up to %d)" % MAX_PAGES)
    parser.add_argument("--subject", help="subject name for the heading; defaults to the first page's host")
    parser.add_argument("--strategy", default="mobile", choices=STRATEGIES, help="API strategy parameter; default mobile")
    parser.add_argument("--exclude", action="append", metavar='URL="reason"',
                        help="measure this page but list it as checked and excluded, with the reason; repeatable")
    args = parser.parse_args(argv)

    pages = []
    try:
        for p in args.pages:
            p = check_url(p)
            if p not in pages:
                pages.append(p)
        if len(pages) > MAX_PAGES:
            raise ValueError("at most %d pages per run, got %d" % (MAX_PAGES, len(pages)))
        exclusions = parse_exclusions(args.exclude, pages)
    except ValueError as err:
        parser.error(str(err))

    key = os.environ.get(KEY_ENV) or None
    subject = args.subject or urllib.parse.urlsplit(pages[0]).netloc
    try:
        captures = {}
        for p in pages:
            captures[p] = fetch(request_url(p, args.strategy, key), key, recorded_url(p, args.strategy, bool(key)))
        lines = render_report(subject, pages, args.strategy, captures, exclusions)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
