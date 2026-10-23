#!/usr/bin/env python3
"""ProPublica Nonprofit Explorer fetcher (API v2), for nonprofit diligence.

Given an organization name, one or more EINs, or both, queries the public
ProPublica Nonprofit Explorer API and prints one Markdown section in the
delivery format from AGENT-BRIEF.md. Per organization: legal name, EIN,
city and state, then the tax period, total revenue, total functional
expenses, total assets (end of year) and total liabilities (end of year)
of the most recent filing that carries extracted figures. Every claim
line is followed by the source link and, directly beneath it, the exact
raw "key":value text cut from the response body (never re-serialized).
Each query ends with its source link and the complete raw HTTP response
transcript (status line, headers in the order returned, a blank line,
then the body exactly as returned).

Key: none needed. Standard library only. The only network calls are GETs
to projects.propublica.org: one search per --name, one organization
lookup per EIN examined.

Usage examples (the EIN and name are the ones captured live for the
tests in tools/tests/fixtures/propublica/):

    python3 tools/propublica_nonprofits.py --ein 53-0196605
    python3 tools/propublica_nonprofits.py --name 'American Red Cross' \
        --ein 530196605 \
        --exclude 204801016="separate local club, not the national organization"

Which figures, from where (field names taken from real captures only):

* Identity comes from the organization block of
  /api/v2/organizations/<EIN>.json: name, ein, city, state.
* The figures come from filings_with_data, from the entry with the
  highest tax_prd (the tool does not assume the array order): tax_prd,
  totrevenue, totfuncexpns, totassetsend, totliabend. The response
  states no unit; the values are printed as shown.
* organization.tax_period and organization.revenue_amount describe a
  different record from the filing figures (in the captured response
  they differ: "2025-06-01" against tax_prd 202306). The tool prints
  organization.tax_period, labelled as such, and takes no figure from it.
* A filings_without_data entry with a later tax_prd than the one used is
  printed as a later filing listed without extracted figures, so the
  report never implies the figures are from the latest filing when a
  later one is listed.

Name search: the search results are listed as shown. The tool never
decides which result is the subject. A result is examined (its
organization record fetched) only when its EIN is given with --ein, or
when its name equals the --name text exactly, ignoring case and spacing.
Near matches the operator has checked and ruled out are listed with
--exclude EIN="reason", and an exclusion for an EIN that is not in the
search response is refused. An empty search (total_results 0, no
organizations) is proven by printing the complete raw response.

Fail closed: a transport failure, any HTTP status other than 200, a body
that is not JSON, or a response without the expected blocks prints
nothing on stdout, a diagnostic on stderr, and exits 2. The empty result
shape could not be observed when this tool was written, so a non-200
answer is never read as "nothing found".
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from datetime import datetime, timezone

API = "https://projects.propublica.org/nonprofits/api/v2"
TIMEOUT_SECONDS = 30
DECODER = json.JSONDecoder()

Capture = namedtuple("Capture", "url retrieved status_line status headers body")

FILING_FIELDS = [
    ("tax_prd", "Tax period of the filing"),
    ("totrevenue", "Total revenue"),
    ("totfuncexpns", "Total functional expenses"),
    ("totassetsend", "Total assets, end of year"),
    ("totliabend", "Total liabilities, end of year"),
]
IDENTITY_FIELDS = [
    ("name", "Legal name"),
    ("ein", "EIN"),
    ("city", "City"),
    ("state", "State"),
]


class FetchError(Exception):
    """A query that cannot be reported. Never rendered as an empty result."""


# ----------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------

def parser():
    p = argparse.ArgumentParser(description="ProPublica Nonprofit Explorer fetcher (API v2).")
    p.add_argument("--name", help="organization name to search for")
    p.add_argument("--ein", action="append", default=[], help="EIN to examine, 9 digits, dash optional; repeatable")
    p.add_argument("--exclude", action="append", default=[], metavar='EIN="reason"',
                   help="search result checked and ruled out by the operator; needs --name; repeatable")
    p.add_argument("--subject", help="report heading (default: the name or the EINs)")
    return p


def normalize_ein(text):
    digits = text.replace("-", "").strip()
    if not re.fullmatch(r"\d{9}", digits):
        raise ValueError("EIN must be 9 digits, with or without a dash: %r" % text)
    return digits


def exclusions(values):
    out = {}
    for value in values:
        ein, sep, reason = value.partition("=")
        reason = reason.strip()
        if not sep or not reason:
            raise ValueError('--exclude needs EIN="reason": %r' % value)
        out[normalize_ein(ein)] = reason
    return out


def search_url(name):
    return API + "/search.json?" + urllib.parse.urlencode({"q": name})


def organization_url(ein):
    return API + "/organizations/%s.json" % ein


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET the URL. Returns a Capture for a 200 answer; raises FetchError
    for anything else, so a failure can never be printed as a result."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "tiny-ledger-propublica-fetcher"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        snippet = err.read(300).decode("utf-8", "replace")
        raise FetchError("%s answered HTTP %s %s: %s" % (url, err.code, err.reason, snippet))
    except (urllib.error.URLError, OSError) as err:
        raise FetchError("%s could not be fetched: %s" % (url, err))
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        try:
            body = response.read().decode("utf-8")
        except UnicodeDecodeError as err:
            raise FetchError("%s body is not UTF-8: %s" % (url, err))
    if response.status != 200:
        raise FetchError("%s answered HTTP %s, not 200" % (url, response.status))
    return Capture(url, retrieved, status_line, response.status, headers, body)


# ----------------------------------------------------------------------
# Reading the raw body: spans, so excerpts are cut from the body itself
# ----------------------------------------------------------------------

def skip_ws(raw, i):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    return i


def members(raw, start):
    """Members of the JSON object starting at raw[start] == "{", as
    {key: (key_start, value_start, value_end)}."""
    if raw[start] != "{":
        raise ValueError("expected an object at offset %d" % start)
    out, i = {}, skip_ws(raw, start + 1)
    if raw[i] == "}":
        return out
    while True:
        key_start = i
        key, i = DECODER.raw_decode(raw, i)
        i = skip_ws(raw, i)
        if raw[i] != ":":
            raise ValueError("expected ':' at offset %d" % i)
        value_start = skip_ws(raw, i + 1)
        _, value_end = DECODER.raw_decode(raw, value_start)
        out[key] = (key_start, value_start, value_end)
        i = skip_ws(raw, value_end)
        if raw[i] == "}":
            return out
        if raw[i] != ",":
            raise ValueError("expected ',' at offset %d" % i)
        i = skip_ws(raw, i + 1)


def elements(raw, start):
    """Spans (start, end) of the elements of the JSON array at raw[start]."""
    if raw[start] != "[":
        raise ValueError("expected an array at offset %d" % start)
    out, i = [], skip_ws(raw, start + 1)
    if raw[i] == "]":
        return out
    while True:
        _, end = DECODER.raw_decode(raw, i)
        out.append((i, end))
        i = skip_ws(raw, end)
        if raw[i] == "]":
            return out
        if raw[i] != ",":
            raise ValueError("expected ',' at offset %d" % i)
        i = skip_ws(raw, i + 1)


class Node:
    """A JSON object in the raw body: parsed values plus raw excerpts."""

    def __init__(self, raw, start):
        self.raw, self.spans = raw, members(raw, start)
        self.start, self.end = start, DECODER.raw_decode(raw, start)[1]

    def whole(self):
        return self.raw[self.start:self.end]

    def has(self, key):
        return key in self.spans

    def value(self, key):
        _, vs, ve = self.spans[key]
        return json.loads(self.raw[vs:ve])

    def literal(self, key):
        _, vs, ve = self.spans[key]
        return self.raw[vs:ve]

    def excerpt(self, key):
        ks, _, ve = self.spans[key]
        return self.raw[ks:ve]

    def child(self, key):
        _, vs, _ = self.spans[key]
        return Node(self.raw, vs)

    def children(self, key):
        _, vs, _ = self.spans[key]
        if self.raw[vs] != "[":
            raise ValueError("%s is not an array" % key)
        return [Node(self.raw, s) for s, _ in elements(self.raw, vs) if self.raw[s] == "{"]


def root(capture):
    start = skip_ws(capture.body, 0)
    try:
        node = Node(capture.body, start)
        if skip_ws(capture.body, DECODER.raw_decode(capture.body, start)[1]) != len(capture.body):
            raise ValueError("trailing data after the JSON value")
    except (ValueError, IndexError) as err:
        raise FetchError("%s body is not a JSON object: %s" % (capture.url, err))
    return node


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def inline(text):
    ticks = "``" if "`" in text else "`"
    pad = " " if ticks == "``" else ""
    return "%s%s%s%s%s" % (ticks, pad, text, pad, ticks)


def transcript(capture):
    return "\n".join([capture.status_line] + capture.headers + ["", capture.body])


def claim(lines, label, node, key, url):
    if node.has(key):
        lines.append("- %s (%s) as shown: %s" % (label, key, inline(node.literal(key))))
        lines.append("  Source: <%s>" % url)
        lines.append("")
        lines.append(fenced(node.excerpt(key)))
    else:
        lines.append("- %s (%s): not shown in the response." % (label, key))
    lines.append("")


def query_lines(capture):
    return ["QUERY: GET %s" % capture.url, "Retrieved (UTC): %s" % capture.retrieved,
            "HTTP status: %s" % capture.status_line, ""]


def source_block(capture):
    return ["Source: <%s>" % capture.url, fenced(transcript(capture)), ""]


def tax_prd_of(node):
    try:
        return int(node.value("tax_prd")) if node.has("tax_prd") else None
    except (TypeError, ValueError):
        return None


def render_organization(capture, heading):
    data = root(capture)
    if not data.has("organization") or data.literal("organization")[:1] != "{":
        raise FetchError("%s has no organization object" % capture.url)
    if not data.has("filings_with_data") or data.literal("filings_with_data")[:1] != "[":
        raise FetchError("%s has no filings_with_data array" % capture.url)
    org = data.child("organization")
    url = capture.url
    lines = ["### %s" % heading, ""] + query_lines(capture)
    lines += ["Identity, from the organization block:", ""]
    for key, label in IDENTITY_FIELDS:
        claim(lines, label, org, key, url)

    filings = data.children("filings_with_data")
    dated = [f for f in filings if tax_prd_of(f) is not None]
    if not dated:
        lines += ["No filing with extracted figures is listed: filings_with_data holds %d entr%s with a "
                  "readable tax_prd. The complete raw response is below." % (len(dated), "y" if len(dated) == 1 else "ies"), ""]
    else:
        latest = max(dated, key=tax_prd_of)
        lines += ["Figures, from the filings_with_data entry with the highest tax_prd (%d of %d entries). "
                  "The response states no unit; values are as shown." % (tax_prd_of(latest), len(filings)), ""]
        for key, label in FILING_FIELDS:
            claim(lines, label, latest, key, url)
        later = []
        if data.has("filings_without_data") and data.literal("filings_without_data")[:1] == "[":
            later = [f for f in data.children("filings_without_data")
                     if tax_prd_of(f) is not None and tax_prd_of(f) > tax_prd_of(latest)]
        for f in sorted(later, key=tax_prd_of, reverse=True):
            lines.append("- A later filing is listed without extracted figures (filings_without_data), "
                         "tax_prd as shown: %s. No figure above comes from it." % inline(f.literal("tax_prd")))
            lines.append("  Source: <%s>" % url)
            lines.append("")
            lines.append(fenced(f.whole()))
            lines.append("")
    if org.has("tax_period"):
        lines.append("- Organization record tax_period as shown: %s. This is the organization block's field, "
                     "not the period of the figures above." % inline(org.literal("tax_period")))
        lines.append("  Source: <%s>" % url)
        lines.append("")
        lines.append(fenced(org.excerpt("tax_period")))
        lines.append("")
    return lines + source_block(capture)


def search_results(capture, excluded):
    """(root node, organization nodes, {EIN: node}) for a search capture.
    Refuses an exclusion for an EIN the response does not contain."""
    data = root(capture)
    if not data.has("organizations") or data.literal("organizations")[:1] != "[":
        raise FetchError("%s has no organizations array" % capture.url)
    orgs = data.children("organizations")
    found = {}
    for o in orgs:
        if o.has("ein"):
            found[str(o.value("ein")).zfill(9)] = o
    missing = sorted(set(excluded) - set(found))
    if missing:
        raise ValueError("exclusion for EIN(s) not in the search response: %s" % ", ".join(missing))
    return data, orgs, found


def render_search(capture, name, examined, excluded):
    data, orgs, found = search_results(capture, excluded)
    lines = ['### Search: "%s"' % name, ""] + query_lines(capture)
    total = data.literal("total_results") if data.has("total_results") else "not shown"
    pages = data.literal("num_pages") if data.has("num_pages") else "not shown"
    lines.append("total_results as shown: %s. Organizations on this page: %d. num_pages as shown: %s."
                 % (total, len(orgs), pages))
    if data.has("num_pages") and isinstance(data.value("num_pages"), int) and data.value("num_pages") > 1:
        lines.append("More pages are reported by the API; this section does not include them.")
    lines.append("")
    if not orgs:
        lines += ["The search returned no organizations. The complete raw response is below; "
                  "this is a search observation, not proof that no such organization exists.", ""]
    for ein, o in found.items():
        shown = ", ".join("%s %s" % (k, inline(o.literal(k))) for k in ("strein", "name", "city", "state") if o.has(k))
        if ein in excluded:
            status = "checked and excluded by the operator: %s" % excluded[ein]
        elif ein in examined:
            status = "examined below"
        else:
            status = "not examined"
        lines.append("- Result %s: %s. Status: %s." % (inline(o.literal("ein")), shown, status))
    if orgs:
        lines.append("")
    if excluded:
        lines += ["#### Checked and excluded", ""]
        for ein, reason in excluded.items():
            o = found[ein]
            lines.append("- Result %s %s, operator reason: %s" % (inline(o.literal("ein")),
                         inline(o.literal("name")) if o.has("name") else "", reason))
            lines.append("  Source: <%s>" % capture.url)
            lines.append("")
            lines.append(fenced(o.whole()))
            lines.append("")
    return lines + source_block(capture)


def exact_name_matches(found, name):
    want = " ".join(name.lower().split())
    return [ein for ein, o in found.items()
            if o.has("name") and isinstance(o.value("name"), str) and " ".join(o.value("name").lower().split()) == want]


def report(name, eins, excluded, subject, fetcher=fetch):
    lines = ["## ProPublica Nonprofit Explorer: %s" % subject, "",
             "Scope: the ProPublica Nonprofit Explorer API v2 as returned at the stated times; figures are "
             "the API's extracted Form 990 values as shown, not an audit, and not a full reading of the filing.",
             ""]
    examined = list(eins)
    if name:
        search = fetcher(search_url(name))
        found = search_results(search, excluded)[2]
        for ein in exact_name_matches(found, name):
            if ein not in examined and ein not in excluded:
                examined.append(ein)
        lines += render_search(search, name, examined, excluded)
        if not examined:
            lines += ["No search result's name equals the search text exactly and no EIN was given, so no "
                      "organization record was fetched. Rerun with --ein for the result to examine.", ""]
    for ein in examined:
        cap = fetcher(organization_url(ein))
        lines += render_organization(cap, "Organization: EIN %s" % ein)
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        eins = []
        for e in args.ein:
            n = normalize_ein(e)
            if n not in eins:
                eins.append(n)
        excluded = exclusions(args.exclude)
        if excluded and not args.name:
            raise ValueError("--exclude needs --name: exclusions are search results")
        if set(excluded) & set(eins):
            raise ValueError("an EIN cannot be both examined and excluded")
        if not args.name and not eins:
            raise ValueError("give --name, --ein, or both")
        subject = args.subject or args.name or ", ".join(eins)
        out = report(args.name, eins, excluded, subject)
    except ValueError as err:
        print("error: %s" % err, file=sys.stderr)
        return 2
    except FetchError as err:
        print("fetch failed, no report printed: %s" % err, file=sys.stderr)
        return 2
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
