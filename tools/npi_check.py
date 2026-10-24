#!/usr/bin/env python3
"""CMS NPI Registry check (issue #326, tool factory wave 3).

Given a US healthcare provider name or a 10 digit NPI number, reads the
CMS NPI Registry (NPPES) and prints one Markdown report in the delivery
format from AGENT-BRIEF.md: the answer first (each matching provider's
NPI number, name, status, taxonomies, and practice state, each as
shown), then the evidence: every query page's exact URL, UTC retrieval
time, the fields cut verbatim from the response, and the complete raw
response.

    python3 tools/npi_check.py 1740584747
    python3 tools/npi_check.py "Brian Aalbers"

Source, keyless: the NPPES NPI Registry API at
https://npiregistry.cms.hhs.gov/api/ with version=2.1 (required). The
response shape used here is from the live captures made for this issue
on 2026-10-24 (committed under tools/tests/fixtures/npi/ with their
provenance): an object with "result_count" and "results"; each result
carries "number", "enumeration_type", a "basic" object (name parts,
credential, status), an "addresses" array (each tagged
"address_purpose", LOCATION or MAILING) and a "taxonomies" array
("desc", "code", "primary" among them). Three traps from the wave 3
source check are handled in the open:

- The registry answers some refusals at HTTP 200 with an "Errors"
  document instead of results (an unsupported version is one). That
  shape is refused here, never read as an empty result.
- "result_count" is capped by the page limit requested (200 here), so
  it is never a total. Name searches page with skip until a short page
  arrives, up to a stated cap of 5 pages per interpretation; the count
  this report gives is the number of records actually returned across
  those pages, with the cap named when it is hit.
- A record can list several taxonomies with none flagged primary, and
  addresses of both purposes. The stated rules here: every taxonomy is
  listed with its primary flag as shown, and the practice state is the
  state of the first LOCATION address, or of the first MAILING address
  when the record shows no LOCATION address, labelled either way.

A name is read two ways, and both are reported: as an individual
(first name is the first word, last name is the last word; a single
word is read as a last name) and as an organization (the whole name).
An NPI number is queried as a number only.

Outcomes: records returned are a report. A proven no match (every
interpretation's pages end with result_count 0 and an empty results
array) is a report too, with the complete raw responses as the proof;
it is the registry's answer at the retrieval time only. A failed
request, any status but 200, a redirect off the source host, an Errors
document, or a body without the documented shape stops the run with
exit 2 and no report: a failed fetch is reported as unknown, never as
a negative claim.

Standard library only.
"""

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import Node, elements, fenced, inline, skip_ws  # noqa: E402

API_URL = "https://npiregistry.cms.hhs.gov/api/"
VERSION = "2.1"
USER_AGENT = "tiny-ledger-npi-check"
TIMEOUT_SECONDS = 30
PAGE_LIMIT = 200
MAX_PAGES = 5
MIN_NAME_CHARS = 2
MAX_NAME_CHARS = 80
HIDDEN_HEADERS = ("set-cookie",)
NAME_PUNCT = " -'.,"

OBSERVATION = ("Observation only: this report records what the CMS NPI Registry returned for this query at "
               "the retrieval times below. The registry is maintained on its own clock; another source "
               "naming the same provider can differ, and this report does not merge sources. No match is "
               "the registry's answer at the retrieval time only.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, retrieved, status_line, headers, body):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        shown = [kv for kv in self.headers if kv[0].lower() not in HIDDEN_HEADERS]
        lines = [self.status_line] + ["%s: %s" % kv for kv in shown]
        if len(shown) != len(self.headers):
            lines.append("(a Set-Cookie header was returned and is not printed)")
        return "\n".join(lines + ["", self.body])


# ----------------------------------------------------------------------
# Inputs and URLs
# ----------------------------------------------------------------------

def check_query(query):
    """("npi", digits) or ("name", text), or ValueError."""
    text = " ".join((query or "").split())
    if not text:
        raise ValueError("give an NPI number (10 digits) or a provider name")
    if text.isdigit():
        if len(text) != 10:
            raise ValueError("an NPI number is exactly 10 digits (got %d)" % len(text))
        return "npi", text
    if any(ch.isdigit() for ch in text):
        raise ValueError("a name contains no digits; an NPI number is exactly 10 digits (got %r)" % text)
    if not MIN_NAME_CHARS <= len(text) <= MAX_NAME_CHARS:
        raise ValueError("a name must be %d to %d characters" % (MIN_NAME_CHARS, MAX_NAME_CHARS))
    if any(not (ch.isalpha() or ch in NAME_PUNCT) for ch in text):
        raise ValueError("a name may contain letters, spaces, and %s only" % NAME_PUNCT.strip())
    return "name", text


def interpretations(kind, text):
    """[(label, [(param, value), ...]), ...] in report order."""
    if kind == "npi":
        return [("NPI number", [("number", text)])]
    words = text.split()
    if len(words) == 1:
        individual = [("last_name", words[0])]
    else:
        individual = [("first_name", words[0]), ("last_name", words[-1])]
    return [("Individual name (first word as first_name, last word as last_name)", individual),
            ("Organization name (the whole name as organization_name)", [("organization_name", text)])]


def page_url(params, skip):
    query = urllib.parse.urlencode([("version", VERSION)] + params
                                   + [("limit", str(PAGE_LIMIT)), ("skip", str(skip))],
                                   quote_via=urllib.parse.quote)
    return "%s?%s" % (API_URL, query)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        raise FetchError("%s answered HTTP %s; no report" % (url, err.code))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, getattr(response, "reason", ""))
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("%s answered %s; no report" % (url, status_line))
    if urllib.parse.urlsplit(final_url).netloc != urllib.parse.urlsplit(url).netloc:
        raise FetchError("%s was redirected off its host; no report" % url)
    return Capture(url, retrieved, status_line, headers, body)


def root(capture):
    try:
        return Node(capture.body, skip_ws(capture.body, 0))
    except (ValueError, IndexError) as err:
        raise FetchError("%s answered a body that is not a JSON object (%s); no report" % (capture.url, err))


# ----------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------

def page_results(capture):
    """The result Nodes of one page. Raises FetchError on an Errors
    document or any body that is not the documented shape."""
    node = root(capture)
    try:
        if node.has("Errors"):
            raise FetchError("%s answered an Errors document, not results; no report" % capture.url)
        if not node.has("result_count") or not node.has("results"):
            raise ValueError("no result_count or results (members: %s)" % (", ".join(sorted(node.spans)) or "none"))
        count = node.value("result_count")
        if not isinstance(count, int) or isinstance(count, bool):
            raise ValueError("result_count is not an integer")
        _, start, _ = node.spans["results"]
        if node.raw[start] != "[":
            raise ValueError("results is not an array")
        out = []
        for s, _ in elements(node.raw, start):
            result = Node(node.raw, s)
            for field in ("number", "enumeration_type"):
                if not result.has(field):
                    raise ValueError("a result has no %s" % field)
            basic = result.child("basic")
            if not (basic.has("last_name") or basic.has("organization_name")):
                raise ValueError("a result's basic has neither last_name nor organization_name")
            for field in ("taxonomies", "addresses"):
                _, fs, _ = result.spans[field]
                if result.raw[fs] != "[":
                    raise ValueError("a result's %s is not an array" % field)
            out.append(result)
        if count != len(out):
            raise ValueError("result_count %d does not match the %d results on the page" % (count, len(out)))
    except (ValueError, IndexError, KeyError) as err:
        if isinstance(err, FetchError):
            raise
        raise FetchError("%s answered a body that is not the documented registry shape (%s); no report"
                         % (capture.url, err))
    return out


def collect(params, fetcher):
    """(result Nodes across pages, [Capture per page], capped flag). Pages
    until a short page (fewer than PAGE_LIMIT results) or MAX_PAGES."""
    results, captures, capped = [], [], False
    skip = 0
    while True:
        capture = fetcher(page_url(params, skip))
        captures.append(capture)
        page = page_results(capture)
        results += page
        if len(page) < PAGE_LIMIT:
            break
        if len(captures) >= MAX_PAGES:
            capped = True
            break
        skip += PAGE_LIMIT
    return results, captures, capped


def children(node, field):
    _, start, _ = node.spans[field]
    return [Node(node.raw, s) for s, _ in elements(node.raw, start)]


def shown_name(basic):
    """The provider's name from its basic parts, each as shown."""
    if basic.has("organization_name"):
        return inline(basic.literal("organization_name"))
    parts = [basic.literal(f) for f in ("first_name", "middle_name", "last_name") if basic.has(f)]
    return " ".join(inline(p) for p in parts)


def practice_state(result):
    """(line) by the stated rule: first LOCATION address's state, else
    first MAILING address's state labelled, else no address shown."""
    addresses = children(result, "addresses")
    for purpose in ("LOCATION", "MAILING"):
        for address in addresses:
            if address.has("address_purpose") and address.value("address_purpose") == purpose \
                    and address.has("state"):
                return ("- Practice state: %s (state as shown, of the %s address; address_purpose as shown: %s)"
                        % (inline(address.literal("state")), purpose, inline(address.literal("address_purpose"))))
    return "- Practice state: no address with a state is shown in this record"


def provider_lines(result, index, total):
    basic = result.child("basic")
    lines = ["Provider %d of %d:" % (index, total),
             "- NPI number (number) as shown: %s" % result.literal("number"),
             "- Enumeration type (enumeration_type) as shown: %s" % inline(result.literal("enumeration_type")),
             "- Name as shown: %s" % shown_name(basic)]
    if basic.has("credential"):
        lines.append("- Credential (credential) as shown: %s" % inline(basic.literal("credential")))
    if basic.has("status"):
        lines.append("- Status (status) as shown: %s" % inline(basic.literal("status")))
    taxonomies = children(result, "taxonomies")
    if taxonomies:
        any_primary = any(t.has("primary") and t.value("primary") is True for t in taxonomies)
        for t in taxonomies:
            primary = inline(t.literal("primary")) if t.has("primary") else "not shown"
            lines.append("- Taxonomy as shown: %s (code %s), primary: %s"
                         % (inline(t.literal("desc")) if t.has("desc") else "not shown",
                            inline(t.literal("code")) if t.has("code") else "not shown", primary))
        if not any_primary:
            lines.append("- No taxonomy in this record is flagged primary.")
    else:
        lines.append("- Taxonomies: none shown in this record.")
    lines.append(practice_state(result))
    return lines


def fields_excerpt(result):
    basic = result.child("basic")
    parts = [result.excerpt("number"), result.excerpt("enumeration_type")]
    parts += [basic.excerpt(f) for f in ("first_name", "middle_name", "last_name", "organization_name",
                                         "credential", "status") if basic.has(f)]
    for t in children(result, "taxonomies"):
        parts += [t.excerpt(f) for f in ("desc", "code", "primary") if t.has(f)]
    for a in children(result, "addresses"):
        parts += [a.excerpt(f) for f in ("address_purpose", "state") if a.has(f)]
    return "\n".join(parts)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def report(query, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    kind, text = check_query(query)
    lines = ["# NPI Registry check: %s" % text, "", OBSERVATION, "", "## Answer", ""]
    proof = ["## Evidence", ""]
    any_records = False
    for label, params in interpretations(kind, text):
        results, captures, capped = collect(params, fetcher)
        lines += ["Interpretation: %s" % label, ""]
        if results:
            any_records = True
            lines += ["The registry returned %d record(s) for this interpretation across %d page(s)%s:"
                      % (len(results), len(captures),
                         ", and the page cap of %d was reached with a full last page, so more records may "
                         "exist beyond it" % MAX_PAGES if capped else ""), ""]
            for i, result in enumerate(results, 1):
                lines += provider_lines(result, i, len(results)) + [""]
        else:
            lines += ["No match under this interpretation. The registry returned result_count 0 with an "
                      "empty results array; the complete raw response below is the proof.", ""]
        for page_no, capture in enumerate(captures, 1):
            proof += ["### CMS NPI Registry, %s, page %d" % (label, page_no), "",
                      "Exact query URL: <%s>" % capture.url, "",
                      "UTC retrieval time: %s" % capture.retrieved, ""]
            page = page_results(capture)
            if page:
                proof += ["Fields, verbatim from the response:",
                          fenced("\n\n".join(fields_excerpt(r) for r in page)), ""]
            proof += ["Complete raw response:", fenced(capture.transcript()), ""]
    if not any_records:
        lines += ["No matching provider under any interpretation. Every interpretation's empty results "
                  "array in the complete raw responses below is the proof. This is the registry's answer "
                  "at the retrieval times stated, not a statement that the provider does not exist.", ""]
    return lines + proof


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="CMS NPI Registry check for an NPI number or a provider name.")
    p.add_argument("query", nargs="?", help="an NPI number (10 digits) or a provider name")
    args = p.parse_args(argv)
    try:
        if args.query is None:
            raise ValueError("give an NPI number (10 digits) or a provider name")
        lines = report(args.query, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
