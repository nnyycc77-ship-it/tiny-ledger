#!/usr/bin/env python3
"""CourtListener RECAP docket search fetcher.

Queries the public CourtListener search API (api/rest/v4/search, type d,
federal dockets from the RECAP archive) live for one subject company and
prints one Markdown section in the delivery format from AGENT-BRIEF.md:
the claim lines, then for every query its source link (the exact query
URL) with the complete raw HTTP response transcript printed verbatim
directly beneath it.

No key is needed for this source. The published litigation screen in
deliveries/ was produced with no API token. If the environment variable
COURTLISTENER_TOKEN is set, it is sent as the Authorization header to
lift the anonymous rate limit; it is never printed and never written to
any file. Standard library only. The only network calls are the GETs
to www.courtlistener.com.

Usage examples:

    python3 tools/courtlistener_recap.py --subject "Jabil Inc." \
        --party "Jabil Inc." --party "Jabil Inc" --party "Jabil" \
        --filed-after 2021-10-22

    python3 tools/courtlistener_recap.py --subject "Jabil Inc." \
        --party "Jabil Inc." --list 10 --docket-details \
        --exclude 69574962="the subject is a listed party but neither side of the caption"

What the output contains, in order:

1. The subject heading, the fixed scope line (index level only, not a
   legal opinion), and the method line naming the API, the filters and
   the ordering.
2. Searches: one line per party name variant with the exact query
   fields, the count the API returned, how many results the first page
   held, whether a next page cursor was returned, and the retrieval
   time in UTC. Only the first page of each query is fetched; the
   counts are reported per variant and never merged.
3. Cases: a table of the first --list results of the first variant's
   search, in the order returned, with the values as shown in the
   source. Role follows the caption rule the published delivery used
   (subject before " v. " is plaintiff, after it is defendant, a listed
   party on neither side is other), applied mechanically to the first
   variant's name with punctuation and case ignored; the rule is
   printed with the table. Status is open when dateTerminated is null,
   else the date shown. An empty suitNature or cause is "not shown".
   Cases named with --exclude are listed separately as checked and
   excluded with the operator's reason.
4. Totals: role and status counts with their arithmetic.
5. Sources: for each search, and for each docket record lookup when
   --docket-details is given, the query URL, the retrieval time, and
   the complete raw HTTP response transcript (status line, headers in
   the order returned, a blank line, then the body exactly as
   returned). An empty result is proven by that transcript.

A transport failure (no connection, blocked host, timeout) prints
nothing on stdout and exits 2: a failed fetch is never shown as an
empty result. An HTTP error status is not a failed fetch: its
transcript is printed and the claim lines say the result is not
determinable from that response. The tool never judges which results
concern the subject; --exclude carries the operator's reason and is
refused for a docket ID that is not in the listed results.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

SEARCH_URL = "https://www.courtlistener.com/api/rest/v4/search/"
DEFAULT_ORDER = "dateFiled desc"
TIMEOUT_SECONDS = 60
TOKEN_ENV = "COURTLISTENER_TOKEN"
SCOPE_LINE = "Index-level only; not a legal opinion."


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def party_query(variant):
    """party:("Jabil Inc.") as the delivery's queries are written."""
    variant = str(variant).strip()
    if not variant:
        raise ValueError("a party name variant must not be blank")
    if '"' in variant:
        raise ValueError("a party name variant must not contain a double quote: %r" % variant)
    return 'party:("%s")' % variant


def check_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("--filed-after needs YYYY-MM-DD, got %r" % value)
    return value


def default_filed_after(today=None):
    """Five years before today, the window the published delivery used
    (filed_after=2021-10-22 for a retrieval date of 2026-10-22)."""
    today = today or date.today()
    try:
        return today.replace(year=today.year - 5).isoformat()
    except ValueError:  # 29 February
        return today.replace(year=today.year - 5, day=28).isoformat()


def search_url(variant, filed_after, order_by=DEFAULT_ORDER):
    """The exact URL shape recorded in the published delivery: type, q,
    filed_after, order_by in that order, encoded with urlencode (spaces
    as +, ':' '(' '"' percent encoded)."""
    return SEARCH_URL + "?" + urllib.parse.urlencode([
        ("type", "d"),
        ("q", party_query(variant)),
        ("filed_after", check_date(filed_after)),
        ("order_by", order_by),
    ])


def docket_url(docket_id):
    """The docket record lookup recorded in the published delivery."""
    docket_id = str(docket_id).strip()
    if not docket_id.isdigit():
        raise ValueError("a docket ID is digits only, got %r" % docket_id)
    return SEARCH_URL + "?" + urllib.parse.urlencode([("type", "d"), ("q", "docket_id:%s" % docket_id)])


def describe_query(variant, filed_after, order_by=DEFAULT_ORDER):
    return "type=d, q=%s, filed_after=%s, order_by=%s" % (party_query(variant), filed_after, order_by)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
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
    def status_ok(self):
        return self.status_line.split(" ", 2)[1:2] == ["200"]


def fetch(url, token=None):
    """GET the URL and return a Capture. HTTP error statuses are captured
    rather than raised. Transport errors propagate. The token, if any,
    goes only into the request header and is never part of the
    transcript."""
    retrieved = utc_now_iso()
    headers = {"Accept": "application/json", "User-Agent": "tiny-ledger-courtlistener-fetcher"}
    if token:
        headers["Authorization"] = "Token %s" % token
    request = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        header_lines = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body = response.read().decode("utf-8")
    return Capture(url, retrieved, status_line, header_lines, body)


# ----------------------------------------------------------------------
# Response reading
# ----------------------------------------------------------------------

def parse_search(body):
    """The recorded responses are objects with count, next, previous and
    a results array of objects. Raises ValueError otherwise."""
    data = json.loads(body)
    if (not isinstance(data, dict) or not isinstance(data.get("results"), list)
            or "count" not in data or not all(isinstance(r, dict) for r in data["results"])):
        raise ValueError('response body is not a JSON object with "count" and a "results" array of objects')
    return data


def _norm(text):
    return " ".join(re.sub(r"[^0-9a-z]+", " ", str(text or "").lower()).split())


def caption_role(case_name, subject_variant):
    """The published delivery's caption rule, applied mechanically: the
    subject on the plaintiff side of ' v. ' is plaintiff, on the
    defendant side is defendant, otherwise other. Matching ignores case
    and punctuation. Returns (role, note)."""
    name = str(case_name or "")
    parts = re.split(r"\s+v\.?\s+", name, maxsplit=1, flags=re.IGNORECASE)
    subject = _norm(subject_variant)
    if len(parts) != 2:
        return "other", "no ' v. ' in the caption"
    left, right = _norm(parts[0]), _norm(parts[1])
    if subject and subject in left:
        return "plaintiff", ""
    if subject and subject in right:
        return "defendant", ""
    return "other", "a listed party on neither side of the caption"


def shown(value):
    if value is None or str(value) == "":
        return "not shown"
    return str(value)


def status_text(record):
    terminated = record.get("dateTerminated")
    return "open" if terminated in (None, "") else str(terminated)


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


# ----------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------

def parse_exclusions(values):
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError("--exclude needs the form DOCKET_ID=reason, got %r" % value)
        number, reason = value.split("=", 1)
        number = number.strip()
        reason = reason.strip().strip('"').strip("'")
        if not number.isdigit() or not reason:
            raise ValueError("--exclude needs a docket ID and a reason, got %r" % value)
        exclusions[number] = reason
    return exclusions


def source_block(heading, capture):
    lines = ["### Source. %s" % heading, "- Query URL: %s" % capture.url,
             "- Retrieved (UTC): %s" % capture.retrieved,
             "Excerpt (complete raw HTTP response transcript for the query above: "
             "status line, headers in the order returned, a blank line, then the "
             "complete body exactly as returned):"]
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines.append(fence)
    lines.extend(capture.transcript.split("\n"))
    lines.append(fence)
    return lines


def search_line(variant, label, filed_after, order_by, capture, data, error):
    head = '- Variant (%s): "%s" — query: %s' % (label, variant, describe_query(variant, filed_after, order_by))
    if not capture.status_ok:
        return head + " — HTTP status %s, not 200; the count is not determinable from this response (retrieved %s)" % (
            capture.status_line.split(" ", 1)[1], capture.retrieved)
    if error:
        return head + " — the response is not the expected JSON object (%s); the count is not determinable from it (retrieved %s)" % (
            error, capture.retrieved)
    n = len(data["results"])
    tail = " — result count in the window: %s — first page holds %d %s" % (
        json.dumps(data["count"]), n, "result" if n == 1 else "results")
    if data.get("next"):
        tail += "; a next page cursor was returned and not followed"
    if n == 0:
        tail += "; the results array is empty and the complete raw transcript is in the Sources section"
    return head + tail + " — retrieved %s" % capture.retrieved


def render_case_row(index, record, variant):
    role, note = caption_role(record.get("caseName"), variant)
    role_text = role if not note else "%s (%s)" % (role, note)
    return "| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        index, cell(shown(record.get("docketNumber"))), cell(shown(record.get("court"))),
        cell(shown(record.get("caseName"))), cell(shown(record.get("dateFiled"))),
        cell(shown(record.get("suitNature"))), cell(shown(record.get("cause"))),
        cell(role_text), cell(status_text(record)), cell(shown(record.get("docket_id"))))


TABLE_HEAD = [
    "| # | Docket number | Court | Case name | Date filed | Nature of suit | Cause | Role (caption rule) | Status | CourtListener docket ID |",
    "|---|---|---|---|---|---|---|---|---|---|",
]


def render_section(subject, variants, filed_after, order_by, searches, list_count,
                   exclusions=None, docket_captures=None):
    """searches: list of (variant, label, Capture). docket_captures: list
    of (docket_id, Capture) or None."""
    exclusions = dict(exclusions or {})
    lines = ["## Subject: %s" % subject, "", SCOPE_LINE, ""]
    lines.append(
        "Method: every search was run on the CourtListener RECAP docket search API "
        "(search type d, federal dockets) with a party-name filter, party:(\"<variant>\"), "
        "the window filter filed_after=%s, and ordering order_by=%s. Only the first "
        "page of each query was fetched. Counts are reported per variant and not merged, "
        "because shorter forms also match other parties that share a word. Every value in "
        "the body appears in a verbatim raw excerpt in the Sources section, printed "
        "directly under its query URL." % (filed_after, order_by)
    )
    lines.append("")
    lines.append("### Searches")
    lines.append("")
    parsed = []
    for variant, label, capture in searches:
        data, error = None, None
        if capture.status_ok:
            try:
                data = parse_search(capture.body)
            except ValueError as err:
                error = str(err)
        parsed.append((variant, label, capture, data, error))
        lines.append(search_line(variant, label, filed_after, order_by, capture, data, error))

    first_variant, _, first_capture, first_data, _ = parsed[0]
    lines.append("")
    lines.append("### Cases")
    lines.append("")
    if first_data is None:
        lines.append("No cases are listed: the first variant's search did not return a usable "
                     "response (see its line above and its transcript in the Sources section).")
        if exclusions:
            raise ValueError("exclusions given but the first search returned no usable response")
    else:
        results = first_data["results"]
        kept, excluded = [], []
        for record in results[:list_count]:
            key = str(record.get("docket_id", ""))
            if key in exclusions:
                excluded.append((record, exclusions.pop(key)))
            else:
                kept.append(record)
        if exclusions:
            raise ValueError("excluded docket ID(s) not among the listed results: %s" % ", ".join(sorted(exclusions)))
        n_page = len(results)
        n_shown = min(list_count, n_page)
        lines.append(
            "The first %d of %d results on the first page of the exact-name party search "
            '(variant "%s", result count %s in the window), in the order returned. Role is the '
            "caption rule applied mechanically to that variant's name, ignoring case and "
            "punctuation: before \" v. \" is plaintiff, after it is defendant, a listed party on "
            "neither side is other. Status is open when dateTerminated is null, else the date "
            "shown. An empty nature of suit or cause is \"not shown\"."
            % (n_shown, n_page, first_variant, json.dumps(first_data["count"]))
        )
        lines.append("")
        if kept:
            lines.extend(TABLE_HEAD)
            for i, record in enumerate(kept):
                lines.append(render_case_row(i + 1, record, first_variant))
        else:
            lines.append("No cases listed%s." % (" (every listed result is checked and excluded below)" if excluded else ""))
        if excluded:
            lines.append("")
            lines.append("Checked and excluded: %d %s among the listed results %s shown below with the reason each was excluded." % (
                len(excluded), "result" if len(excluded) == 1 else "results", "is" if len(excluded) == 1 else "are"))
            lines.append("")
            lines.extend(TABLE_HEAD)
            for i, (record, reason) in enumerate(excluded):
                lines.append(render_case_row(i + 1, record, first_variant))
            for record, reason in excluded:
                lines.append("- Docket ID %s checked and excluded because: %s" % (shown(record.get("docket_id")), reason))

        lines.append("")
        lines.append("### Totals")
        lines.append("")
        roles = {"plaintiff": [], "defendant": [], "other": []}
        opened, closed = [], []
        for i, record in enumerate(kept):
            roles[caption_role(record.get("caseName"), first_variant)[0]].append(i + 1)
            (opened if status_text(record) == "open" else closed).append(i + 1)

        def rows(ix):
            return ", ".join(str(i) for i in ix) if ix else "none"

        lines.append("- Listed cases: %d." % len(kept))
        lines.append("- As plaintiff: rows %s = %d." % (rows(roles["plaintiff"]), len(roles["plaintiff"])))
        lines.append("- As defendant: rows %s = %d." % (rows(roles["defendant"]), len(roles["defendant"])))
        lines.append("- As other: rows %s = %d." % (rows(roles["other"]), len(roles["other"])))
        lines.append("- Role arithmetic: %d + %d + %d = %d listed cases." % (
            len(roles["plaintiff"]), len(roles["defendant"]), len(roles["other"]), len(kept)))
        lines.append("- Open: rows %s = %d." % (rows(opened), len(opened)))
        lines.append("- Closed (a termination date is shown): rows %s = %d." % (rows(closed), len(closed)))
        lines.append("- Status arithmetic: %d + %d = %d listed cases." % (len(opened), len(closed), len(kept)))
        lines.append("- Total count found in the window (first variant's party search, as returned by the API): %s." % json.dumps(first_data["count"]))

    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for i, (variant, label, capture, data, error) in enumerate(parsed):
        lines.extend(source_block('Q%d. CourtListener RECAP docket search, %s, %s variant "%s"' % (i + 1, subject, label, variant), capture))
        lines.append("")
    for i, (docket_id, capture) in enumerate(docket_captures or []):
        lines.extend(source_block("D%d. CourtListener RECAP docket record, %s, docket ID %s" % (i + 1, subject, docket_id), capture))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

LABELS = ["exact name", "name without suffix", "common short form"]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Query the CourtListener RECAP docket search API and print one Markdown section in the delivery format.")
    parser.add_argument("--subject", help="subject company name for the heading; defaults to the first --party")
    parser.add_argument("--party", action="append", required=True, metavar="NAME",
                        help="party name variant to search; repeatable; the first is the exact name whose results are listed")
    parser.add_argument("--filed-after", help="filed_after YYYY-MM-DD; default five years before today")
    parser.add_argument("--order-by", default=DEFAULT_ORDER, help="order_by value; default '%s'" % DEFAULT_ORDER)
    parser.add_argument("--list", type=int, default=10, help="how many first-page results of the first variant to list; default 10")
    parser.add_argument("--docket-details", action="store_true",
                        help="also fetch each listed case's docket record (q=docket_id:N) as its own source")
    parser.add_argument("--exclude", action="append", metavar='DOCKET_ID="reason"',
                        help="list this docket ID among the listed results as checked and excluded, with the reason; repeatable")
    args = parser.parse_args(argv)

    try:
        exclusions = parse_exclusions(args.exclude)
        filed_after = check_date(args.filed_after) if args.filed_after else default_filed_after()
        if args.list < 0:
            raise ValueError("--list must be 0 or more")
        variants = []
        for v in args.party:
            party_query(v)
            if v not in variants:
                variants.append(v)
    except ValueError as err:
        parser.error(str(err))

    token = os.environ.get(TOKEN_ENV) or None
    subject = args.subject or variants[0]
    try:
        searches = []
        for i, variant in enumerate(variants):
            label = LABELS[i] if i < len(LABELS) else "variant %d" % (i + 1)
            searches.append((variant, label, fetch(search_url(variant, filed_after, args.order_by), token)))
        docket_captures = None
        if args.docket_details:
            docket_captures = []
            first = searches[0][2]
            if first.status_ok:
                try:
                    results = parse_search(first.body)["results"][:args.list]
                except ValueError:
                    results = []
                for record in results:
                    docket_id = record.get("docket_id")
                    if docket_id is not None and str(docket_id).isdigit():
                        docket_captures.append((str(docket_id), fetch(docket_url(docket_id), token)))
        lines = render_section(subject, variants, filed_after, args.order_by, searches,
                               args.list, exclusions, docket_captures)
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
