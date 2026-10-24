#!/usr/bin/env python3
"""Meta tag check (issue #165, tool factory wave 1).

Given a page URL, fetches the page itself once, with the standard library
only and no key, and prints one Markdown report in the delivery format
from AGENT-BRIEF.md: whether the page title, the meta description and the
checked Open Graph tags are present or missing, with the values as shown,
the head of the page cut verbatim beneath the claims, and the complete
raw response beneath the source link.

    python3 tools/meta_tag_check.py https://ogp.me/

Source: the page itself, at the exact URL given. There is no API and no
key; the only input is the URL. Redirects are followed the way a browser
follows them, and the URL that finally answered is printed in the report.

Checked tags:
- the <title> element;
- the meta description: <meta name="description">;
- the Open Graph tags og:title, og:type, og:url, og:image and
  og:description (the basic set named by the Open Graph protocol, at
  https://ogp.me/). Any further og:* tags the page carries are listed as
  also present, in the order the page prints them.

A page where every checked tag is missing is a report, not an error: the
missing lines are the claim and the complete raw response beneath the
source link is the proof. Anything else that goes wrong is not a report:
a failed request, a status other than 200, an answer that is not HTML,
a body that cannot be decoded, or a body over the size cap stops the run
with exit 2 and no report, so a source failure is never shown as a page
with no tags.

Standard library only.
"""

import argparse
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

USER_AGENT = "tiny-ledger-meta-tag-check"
TIMEOUT_SECONDS = 30
MAX_BODY_BYTES = 5_000_000
HTML_TYPES = ("text/html", "application/xhtml+xml")
CHECKED_OG = ("og:title", "og:type", "og:url", "og:image", "og:description")
OBSERVATION = ("Observation only: this report records what the page at the URL below printed in its "
               "own HTML at the retrieval time stated below; present and missing mean present or "
               "absent in that HTML, nothing more.")


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
        self.body = body  # text, decoded with the charset the answer declared

    def header(self, name):
        for k, v in self.headers:
            if k.lower() == name.lower():
                return v
        return None

    def transcript(self):
        return "\n".join([self.status_line] + ["%s: %s" % kv for kv in self.headers] + ["", self.body])


def check_url(value):
    text = (value or "").strip()
    if not text or any(c.isspace() for c in text) or len(text) > 2048:
        raise ValueError("url must be one http or https URL of at most 2048 characters (got %r)" % (value,))
    parts = urllib.parse.urlsplit(text)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("url must be an http or https URL with a host (got %r)" % (value,))
    return text


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decode_body(raw, content_type):
    charset = "utf-8"
    for part in (content_type or "").split(";"):
        part = part.strip()
        if part.lower().startswith("charset="):
            charset = part.split("=", 1)[1].strip().strip('"') or charset
    try:
        return raw.decode(charset)
    except (UnicodeDecodeError, LookupError, OSError) as err:
        raise FetchError("the answer body could not be decoded as %s: %s; no report" % (charset, err))


def fetch(url):
    """One GET of the page itself. Returns a Capture for a 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                     "Accept": "text/html,application/xhtml+xml"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        raise FetchError("%s answered %s %s; no report" % (url, err.code, err.reason))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        raw = response.read(MAX_BODY_BYTES + 1)
    if status != 200:
        raise FetchError("%s answered %s; no report" % (url, status_line))
    if urllib.parse.urlsplit(final_url).scheme not in ("http", "https"):
        raise FetchError("%s was redirected to a non http answer at %s; no report" % (url, final_url))
    if len(raw) > MAX_BODY_BYTES:
        raise FetchError("%s answered a body over the %d byte cap; no report" % (url, MAX_BODY_BYTES))
    capture = Capture(url, final_url, retrieved, status, status_line, headers, None)
    capture.body = decode_body(raw, capture.header("Content-Type"))
    return capture


class HeadParser(HTMLParser):
    """Collects the title text and the meta tags, in the order printed."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.title_seen = False
        self.metas = []  # [(kind, key, content)] kind is "name" or "property", in document order

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
            self.title_seen = True
        elif tag == "meta":
            values = {k.lower(): (v if v is not None else "") for k, v in attrs}
            if "property" in values:
                self.metas.append(("property", values["property"].strip().lower(), values.get("content", "")))
            elif "name" in values:
                self.metas.append(("name", values["name"].strip().lower(), values.get("content", "")))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)


def parse_page(body):
    parser = HeadParser()
    parser.feed(body)
    parser.close()
    title = "".join(parser.title_parts).strip() if parser.title_seen else None
    if title is not None and not title:
        title = None  # a <title> element with no text carries no title
    description = None
    og = {}
    og_extra = []
    for kind, key, content in parser.metas:
        if kind == "name" and key == "description" and description is None:
            description = content
        elif kind == "property" and key.startswith("og:"):
            if key in CHECKED_OG:
                if key not in og:
                    og[key] = content
            else:
                og_extra.append((key, content))
    return title, description, og, og_extra


def head_excerpt(body):
    """The page from its start through </head>, verbatim; the whole body when there is no </head>."""
    idx = body.lower().find("</head>")
    if idx == -1:
        return body
    return body[:idx + len("</head>")]


def _shown(value):
    return "present, as shown: %s" % value if value is not None else "missing"


def render(url, capture):
    """The report lines. Raises FetchError when the answer is not an HTML page."""
    content_type = capture.header("Content-Type")
    media = (content_type or "").split(";")[0].strip().lower()
    if media not in HTML_TYPES:
        raise FetchError("%s answered Content-Type %s, not an HTML page; no report"
                         % (url, content_type if content_type else "(none returned)"))
    title, description, og, og_extra = parse_page(capture.body)
    lines = ["# Meta tag check: %s" % url, "", OBSERVATION, "",
             "Exact query: GET %s" % capture.url,
             "Retrieved (UTC): %s" % capture.retrieved]
    if capture.final_url != capture.url:
        lines.append("Answered from: %s (the request was redirected)" % capture.final_url)
    lines += ["",
              "- Title: %s" % _shown(title),
              "- Description (meta name=\"description\"): %s" % _shown(description),
              "- Open Graph tags checked:"]
    for key in CHECKED_OG:
        lines.append("  - %s: %s" % (key, _shown(og.get(key))))
    if og_extra:
        lines.append("- Further Open Graph tags also present, in the order printed:")
        for key, content in og_extra:
            lines.append("  - %s: %s" % (key, content))
    else:
        lines.append("- Further Open Graph tags: none present")
    if title is None and description is None and not og and not og_extra:
        lines += ["", "None of the checked tags are present on this page. "
                  "The complete raw response below is the proof."]
    lines += ["", "The head of the page, verbatim:", fenced(head_excerpt(capture.body)), "",
              "Source: <%s>" % capture.url, fenced(capture.transcript())]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Meta tag check: title, description and Open Graph tags "
                                            "present or missing on one page.")
    p.add_argument("url")
    args = p.parse_args(argv)
    try:
        url = check_url(args.url)
        capture = (fetcher or fetch)(url)
        lines = render(url, capture)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
