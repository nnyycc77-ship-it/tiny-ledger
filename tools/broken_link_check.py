#!/usr/bin/env python3
"""Broken link check (issue #164, tool factory wave 1).

Given a page URL, fetches the page once, reads every link on it, checks
each HTTP or HTTPS target once, and prints one Markdown report in the
delivery format from AGENT-BRIEF.md: the claim lines, the dead links
with their status codes, every checked link with the status line it
answered, the source link (the page itself), and the complete raw
response of the page printed verbatim directly beneath the link.

Usage example:

    python3 tools/broken_link_check.py https://example.com/

Source: the page itself, and then each link target on it. There is no
API and no key; the only network calls are plain GETs made with the
standard library. Links are the href targets of <a>, <area> and <link>
elements, in page order. A page <base> element is not applied. Each
href is resolved against the page's final URL (after any redirect of
the page fetch), its fragment is removed, and duplicates are checked
once and counted. Three kinds of link are not fetched, and the report
lists each of them so every link on the page is accounted for: same
page anchors (the resolved target is the page itself), non HTTP links
(mailto:, tel:, and the like), and unique targets past the cap of
MAX_LINKS checked per page.

A link is dead when its final answer, after redirects, is a status of
400 or above; the status line printed is that final answer's, with the
final URL named when a redirect moved it. A link whose request itself
fails (no answer at all) is listed as a check failure with the error,
never as dead: a failure to ask is not an answer. Statuses are the
servers' own; this tool does no scoring of its own.

The page fetch fails closed: a failed request, an unreadable body, or
a page status other than 200 stops the run with exit 2 and no report,
because there is no page whose links could be checked. A page with no
links is a report, and the complete raw page response printed beneath
the source link is the proof.

Standard library only.
"""

import argparse
import hashlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import fenced  # noqa: E402

USER_AGENT = "tiny-ledger-broken-link-check"
TIMEOUT_SECONDS = 30
MAX_LINKS = 100
LINK_BODY_READ = 4096  # a link check reads the status, not the page; this bounds the drain
OBSERVATION = ("Observation only: this report records what the page named below and each link target on it "
               "returned at the retrieval time stated below. A status is the server's own answer at that "
               "moment; a target that answers later may answer differently.")


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


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_page_url(raw):
    """A page URL: http or https, with a host. Anything else is the caller's error."""
    text = (raw or "").strip()
    parts = urllib.parse.urlsplit(text)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("page URL must be an http or https URL with a host, got %r" % raw)
    return text


def fetch(url, want_body=True):
    """One GET. Returns a Capture for any HTTP status; raises FetchError when the
    request itself fails or the body cannot be read. With want_body False (a link
    check) the body is drained only far enough to free the connection and is not
    kept: a link check records the status, not the target page."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no answer" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            raw = response.read() if want_body else response.read(LINK_BODY_READ)
        except OSError as err:
            raise FetchError("%s answered a body that could not be read: %s; no answer" % (url, err))
    if want_body:
        try:
            body = raw.decode("utf-8")
        except UnicodeDecodeError as err:
            raise FetchError("%s answered a body that is not UTF-8 text (%s); no report" % (url, err))
    else:
        body = ""
    return Capture(url, final_url, retrieved, status, status_line, headers, body)


class LinkHarvest(HTMLParser):
    """The href targets of <a>, <area> and <link>, in page order, as written."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "area", "link"):
            for name, value in attrs:
                if name == "href" and value is not None:
                    self.hrefs.append(value)


def harvest_links(body):
    parser = LinkHarvest()
    parser.feed(body)
    parser.close()
    return parser.hrefs


def split_links(page_final_url, hrefs):
    """(targets, anchors, non_http): targets is an ordered dict of resolved URL ->
    {raw, count}; anchors and non_http are the raw hrefs, in page order."""
    targets, anchors, non_http = {}, [], []
    for raw in hrefs:
        href = raw.strip()
        resolved = urllib.parse.urldefrag(urllib.parse.urljoin(page_final_url, href))[0]
        scheme = urllib.parse.urlsplit(resolved).scheme
        if scheme not in ("http", "https"):
            non_http.append(raw)
        elif resolved == page_final_url:
            anchors.append(raw)
        elif resolved in targets:
            targets[resolved]["count"] += 1
        else:
            targets[resolved] = {"raw": raw, "count": 1}
    return targets, anchors, non_http


def check_page(page_url, fetcher):
    """Fetch the page and check its links. Returns (capture, results, failures,
    unchecked, anchors, non_http, found) where results is [(url, Capture, count)]
    in page order. Raises FetchError when the page itself cannot be read."""
    capture = fetcher(page_url, want_body=True)
    if capture.status != 200:
        raise FetchError("%s answered %s; a page that does not answer 200 has no links to check, "
                         "and this is not an empty result" % (page_url, capture.status_line))
    hrefs = harvest_links(capture.body)
    targets, anchors, non_http = split_links(capture.final_url, hrefs)
    ordered = list(targets.items())
    to_check, unchecked = ordered[:MAX_LINKS], ordered[MAX_LINKS:]
    results, failures = [], []
    for url, info in to_check:
        try:
            answer = fetcher(url, want_body=False)
        except FetchError as err:
            failures.append((url, str(err), info["count"]))
        else:
            results.append((url, answer, info["count"]))
    return capture, results, failures, unchecked, anchors, non_http, len(hrefs)


def render(page_url, capture, results, failures, unchecked, anchors, non_http, found):
    lines = ["# Broken link check: %s" % page_url, "", OBSERVATION, "",
             "Exact query: GET %s" % page_url,
             "Retrieved (UTC): %s" % capture.retrieved]
    if capture.final_url != capture.url:
        lines.append("Answered from: %s (the page request was redirected)" % capture.final_url)
    body_bytes = capture.body.encode("utf-8")
    lines += ["",
              "PAGE: %s answered %s; body %d bytes, sha256 %s." % (capture.final_url, capture.status_line,
                                                                   len(body_bytes),
                                                                   hashlib.sha256(body_bytes).hexdigest()),
              "LINKS: %d link(s) on the page; %d unique HTTP target(s) checked, %d same page anchor(s) "
              "not fetched, %d non HTTP link(s) not fetched, %d target(s) past the cap of %d not checked."
              % (found, len(results) + len(failures), len(anchors), len(non_http), len(unchecked), MAX_LINKS),
              ""]
    dead = [(url, ans, n) for url, ans, n in results if ans.status >= 400]
    lines.append("Dead links (final status 400 or above): %d" % len(dead))
    if dead:
        for url, ans, n in dead:
            extra = " (redirected to %s)" % ans.final_url if ans.final_url != url else ""
            lines.append("- %s -> %s%s" % (url, ans.status_line, extra))
    else:
        lines.append("- None. Every checked link answered below 400, and the per link results below "
                     "are the proof.")
    lines += ["", "Every checked link, with the status line it answered:"]
    if results:
        for url, ans, n in results:
            extra = " (redirected to %s)" % ans.final_url if ans.final_url != url else ""
            mark = " [dead]" if ans.status >= 400 else ""
            lines.append("- %s -> %s%s%s" % (url, ans.status_line, extra, mark))
    else:
        lines.append("- None were checked; the page holds no HTTP link target, and the complete raw "
                     "page response beneath the source link below is the proof.")
    if failures:
        lines += ["", "Check failures (the request itself failed; not counted as dead): %d" % len(failures)]
        for url, err, n in failures:
            lines.append("- %s -> %s" % (url, err))
    if unchecked:
        lines += ["", "Not checked, past the cap of %d unique targets: %d" % (MAX_LINKS, len(unchecked))]
        for url, info in unchecked:
            lines.append("- %s" % url)
    if anchors:
        lines += ["", "Same page anchors, not fetched: %s" % ", ".join(repr(a) for a in anchors)]
    if non_http:
        lines += ["", "Non HTTP links, not fetched: %s" % ", ".join(repr(a) for a in non_http)]
    lines += ["", "Source: <%s>" % capture.url, fenced(capture.transcript())]
    return lines


def report_lines(page_url, fetcher=None):
    """The whole report for one page URL. Raises FetchError (page unreadable) or
    ValueError (bad URL). Used by the command line and by GET /links."""
    url = check_page_url(page_url)
    return render(url, *check_page(url, fetcher or fetch))


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Check every link on one page and list the dead ones with "
                                            "their status codes.")
    p.add_argument("url", help="the page URL, http or https")
    args = p.parse_args(argv)
    try:
        lines = report_lines(args.url, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
