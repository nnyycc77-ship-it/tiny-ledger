#!/usr/bin/env python3
"""Disaster history check (issue #312, tool factory wave 3, tool 1).

Lists the FEMA disaster declarations recorded for one US state, or one
designated area (county) in it, from the public OpenFEMA API live, and
prints one Markdown section in the delivery format from AGENT-BRIEF.md:
the claim lines, the source link, and the complete raw HTTP response
transcript printed verbatim directly beneath the link.

No key is needed for this source and none is read. The only network call
is one GET to www.fema.gov. Standard library only.

Usage examples:

    python3 tools/disaster_history_check.py RI
    python3 tools/disaster_history_check.py RI --county "Kent (County)" --limit 10

Source (dataset page https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2,
API page https://www.fema.gov/about/openfema/api, both as quoted by the
coordinator on issue #312):

    https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries
        ?$filter=state eq '<ST>'[ and designatedArea eq '<area>']
        &$orderby=declarationDate desc&$top=<limit>&$count=true

The query values are sent form encoded, as in the recorded responses'
own metadata.url. Two facts from the recorded responses shape the
report:

- One disaster appears once per designated area. Rows are not
  disasters: the report counts distinct disasterNumber values, among the
  rows returned, and lists each disaster once with the areas it names.
- The metadata "count" is the total of all matching rows only when
  $count=true is sent; without it, in the API page's words, the count
  "will appear as 0". This tool always sends $count=true, and states the
  total only when the response's own metadata.url shows that it was
  requested.

A county is matched as the exact designatedArea string, which is not
always a plain county name (the recorded values include "Kent (County)"
and "Newport (County)(in PMSA 2480,6480)"). An empty result is reported
as exactly that: no rows with that exact designatedArea in that state,
proven by the raw response. It is never reported as "no disasters".

Fail closed: a failed or timed out fetch, a status other than 200 (the
recorded malformed query answers 400 with an OData Query Parser Error),
or a body that is not the recorded shape stops with exit 2 and no report.
The answer is then unknown, never a negative claim.

The tool adds no value FEMA did not return. Field values are quoted as
shown in the response.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
ENTITY = "DisasterDeclarationsSummaries"
SOURCE_HEADING = "OpenFEMA API v2, DisasterDeclarationsSummaries (www.fema.gov)"
USER_AGENT = "tiny-ledger-disaster-history-check"
TIMEOUT_SECONDS = 30

DEFAULT_LIMIT = 50
MAX_LIMIT = 1000

STATE_PATTERN = re.compile(r"^[A-Za-z]{2}$")
# Letters, digits, spaces and the punctuation seen in recorded designatedArea
# values. An apostrophe would need OData quoting this tool has not seen
# verified against the API, so it is refused rather than guessed.
AREA_PATTERN = re.compile(r"^[A-Za-z0-9 ().,\-&/]{2,120}$")


class SourceFailed(Exception):
    """The fetch failed, answered a status other than 200, or returned a body
    this tool cannot read. No report is produced; the answer is unknown."""


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_state(raw):
    """Two letters, upper cased. Whether FEMA holds rows for it is FEMA's answer."""
    state = str(raw or "").strip()
    if not STATE_PATTERN.match(state):
        raise ValueError("state is a two letter code as FEMA records it (for example RI), got %r" % raw)
    return state.upper()


def check_area(raw):
    """None, or the designatedArea string exactly as given (spaces trimmed)."""
    if raw is None or str(raw).strip() == "":
        return None
    area = " ".join(str(raw).split())
    if "'" in area:
        raise ValueError("a county name with an apostrophe is not supported: its OData quoting has "
                         "not been verified against the API")
    if not AREA_PATTERN.match(area):
        raise ValueError("county is the designatedArea as FEMA writes it, for example 'Kent (County)': "
                         "2 to 120 letters, digits, spaces or ( ) . , - & /, got %r" % raw)
    return area


def check_limit(raw):
    if raw is None or str(raw).strip() == "":
        return DEFAULT_LIMIT
    try:
        limit = int(str(raw).strip())
    except ValueError:
        raise ValueError("limit must be an integer, got %r" % raw)
    if not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be 1 to %d, got %d" % (MAX_LIMIT, limit))
    return limit


def odata_filter(state, area=None):
    text = "state eq '%s'" % state
    if area:
        text += " and designatedArea eq '%s'" % area
    return text


def build_url(state, area=None, limit=DEFAULT_LIMIT):
    """The query URL, values form encoded as in the recorded metadata.url."""
    params = [("$filter", odata_filter(state, area)),
              ("$orderby", "declarationDate desc"),
              ("$top", str(limit)),
              ("$count", "true")]
    return BASE_URL + "?" + "&".join("%s=%s" % (k, urllib.parse.quote_plus(v)) for k, v in params)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET the URL; (retrieved_utc, status, transcript, body_text).

    The transcript is the complete raw HTTP response: status line, the
    headers in the order returned, a blank line, then the body exactly as
    returned. An HTTP error status is returned the same way, so the caller
    can name it; a transport failure raises SourceFailed.
    """
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError) as err:
        raise SourceFailed("%s: fetch failed: %s" % (url, err))
    try:
        with response:
            version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
            status_line = "%s %s %s" % (version, response.status, response.reason)
            header_lines = ["%s: %s" % (k, v) for k, v in response.headers.items()]
            body = response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as err:
        raise SourceFailed("%s: reading the response failed: %s" % (url, err))
    transcript = "\n".join([status_line] + header_lines + ["", body])
    return retrieved, response.status, transcript, body


# ----------------------------------------------------------------------
# Reading the response
# ----------------------------------------------------------------------

def parse_response(body):
    """(metadata, rows) from a 200 body in the recorded shape, else SourceFailed."""
    try:
        data = json.loads(body)
    except ValueError as err:
        raise SourceFailed("the response body is not JSON: %s" % err)
    if not isinstance(data, dict) or not isinstance(data.get("metadata"), dict) \
            or not isinstance(data.get(ENTITY), list):
        raise SourceFailed('the response body is not a JSON object with "metadata" and a "%s" array' % ENTITY)
    rows = data[ENTITY]
    if not all(isinstance(r, dict) for r in rows):
        raise SourceFailed('"%s" holds an entry that is not a JSON object' % ENTITY)
    return data["metadata"], rows


def total_as_shown(metadata):
    """FEMA's total of matching rows, or None when $count=true was not requested."""
    if "$count=true" not in str(metadata.get("url", "")):
        return None
    count = metadata.get("count")
    return count if isinstance(count, int) and not isinstance(count, bool) else None


def disasters(rows):
    """Distinct disasterNumber values in row order, each with its rows."""
    order, grouped = [], {}
    for row in rows:
        key = row.get("disasterNumber")
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(row)
    return [(key, grouped[key]) for key in order]


def _shown(value):
    return "(not present)" if value is None else str(value)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def render_section(state, area, limit, url, retrieved, transcript, body):
    """The whole Markdown section as a list of lines (body already checked as 200)."""
    metadata, rows = parse_response(body)
    place = "designatedArea %s in state %s" % (json.dumps(area), state) if area else "state %s" % state
    lines = ["## Subject: FEMA disaster declarations, %s" % place, "",
             "Database: OpenFEMA API v2, DisasterDeclarationsSummaries, queried by %s, newest "
             "declaration first." % ("state and exact designatedArea" if area else "state"), ""]
    n = len(rows)
    total = total_as_shown(metadata)
    query = "QUERY: $filter %s, $top %d: %d row%s returned (retrieved %s)." % (
        json.dumps(odata_filter(state, area)), limit, n, "" if n == 1 else "s", retrieved)
    if total is None:
        query += (" FEMA's total was not requested for this response ($count=true is not in its "
                  "metadata.url), so no total is stated; without it the metadata count reads 0 by "
                  "the API's rule.")
    else:
        query += " FEMA's total of matching rows (metadata count, $count=true) as shown: %d." % total
        if total > n:
            query += (" More rows match than this response returns; the disasters below are those in "
                      "the %d rows returned, not the full history." % n)
    lines.append(query)
    lines.append("")
    if not rows:
        lines.append("NO ROWS: the %s array in the response is empty for this exact filter. This "
                     "says only that no declaration row has %s; designatedArea is matched as the exact "
                     "string, and the complete raw HTTP response transcript is shown verbatim beneath "
                     "the source link below." % (ENTITY, (
                         "state %s and designatedArea exactly %s" % (state, json.dumps(area))) if area
                         else "state %s" % state))
    else:
        groups = disasters(rows)
        lines.append("DISASTERS: %d distinct disasterNumber value%s among the %d row%s returned (one "
                     "disaster appears once per designated area, so rows are not disasters):" % (
                         len(groups), "" if len(groups) == 1 else "s", n, "" if n == 1 else "s"))
        lines.append("")
        for number, group in groups:
            first = group[0]
            lines.append("- disasterNumber %s (femaDeclarationString as shown: %s): declarationType %s, "
                         "incidentType %s, declarationDate %s, declarationTitle %s" % (
                             _shown(number), _shown(first.get("femaDeclarationString")),
                             _shown(first.get("declarationType")), json.dumps(first.get("incidentType")),
                             _shown(first.get("declarationDate")),
                             json.dumps(first.get("declarationTitle"), ensure_ascii=False)))
            areas = [str(r.get("designatedArea")) for r in group]
            lines.append("  - designatedArea in the %d row%s returned: %s" % (
                len(group), "" if len(group) == 1 else "s", "; ".join(areas)))
    lines.append("")
    lines.append("### Source. %s" % SOURCE_HEADING)
    lines.append("- Query URL: %s" % url)
    lines.append("- Retrieved (UTC): %s" % retrieved)
    lines.append("Excerpt (complete raw HTTP response transcript for the query above: status line, "
                 "headers in the order returned, a blank line, then the complete body exactly as "
                 "returned):")
    lines.append("```")
    lines.extend(transcript.split("\n"))
    lines.append("```")
    return lines


def run(state, area=None, limit=None, fetcher=None):
    """Validate, fetch once, render. Raises ValueError on a bad input (no
    fetch) and SourceFailed when the answer is unknown (no report)."""
    state, area, limit = check_state(state), check_area(area), check_limit(limit)
    url = build_url(state, area, limit)
    retrieved, status, transcript, body = (fetcher or fetch)(url)
    if status != 200:
        raise SourceFailed("%s answered %s; the answer is unknown: %s" % (
            url, transcript.split("\n", 1)[0], body[:500]))
    return render_section(state, area, limit, url, retrieved, transcript, body)


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="FEMA disaster declarations for a US state or one designated area, from the "
        "OpenFEMA API, in the delivery format.")
    parser.add_argument("state", help="two letter state code as FEMA records it, e.g. RI")
    parser.add_argument("--county", help="exact designatedArea as FEMA writes it, e.g. 'Kent (County)'")
    parser.add_argument("--limit", help="rows to ask for, 1 to %d; default %d" % (MAX_LIMIT, DEFAULT_LIMIT))
    args = parser.parse_args(argv)
    try:
        lines = run(args.state, args.county, args.limit)
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    except SourceFailed as err:
        sys.stderr.write("source failure, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
