#!/usr/bin/env python3
"""CPSC SaferProducts recall fetcher.

Queries the public CPSC recall API (SaferProducts.gov RestWebServices)
live and prints one Markdown section in the delivery format from
AGENT-BRIEF.md: the claim lines, the source link, and the complete raw
HTTP response transcript printed verbatim directly beneath the link.

No key is needed for this source and none is read. The only network
call is the one GET to www.saferproducts.gov. Standard library only.

Usage examples:

    python3 tools/cpsc_recalls.py --subject "Vornado VH101 heater" \
        --product-name VH101

    python3 tools/cpsc_recalls.py --subject "Peloton Tread+ treadmill" \
        --recall-title Peloton \
        --exclude 21-129="names the Peloton Tread, not the Tread+" \
        --exclude 23-201="names the Peloton Bike"

    python3 tools/cpsc_recalls.py --subject "Samsung top-load washer" \
        --product-name "Top-Load Washing Machines" \
        --date-start 2018-01-01 --date-end 2023-12-31

    python3 tools/cpsc_recalls.py --recall-number 18-136 --pretty

What the output contains, in order:

1. A subject heading and the database named.
2. QUERY: the exact query fields, the record count, and the retrieval
   time in UTC.
3. RECALLS: one block per record with the values as shown in the
   source. Records named with --exclude are listed separately as
   checked and excluded, with the reason given.
4. The source link (the exact query URL) and the retrieval time.
5. Directly beneath the link, the complete raw HTTP response
   transcript: status line, headers in the order returned, a blank
   line, then the body exactly as returned. An empty result is proven
   by that transcript (its body is the empty array), never asserted.
6. With --pretty, one pretty printed JSON excerpt per record after the
   transcript, values unchanged, the way the published deliveries in
   deliveries/ show records.

The tool never judges relevance. Deciding that a record is a near match
to exclude is the operator's call and the reason is the operator's
words; the tool only refuses to list an exclusion for a recall number
that is not in the response.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://www.saferproducts.gov/RestWebServices/Recall"
DATABASE_LINE = (
    "Database: CPSC public recall data (SaferProducts.gov RestWebServices API)."
)
SOURCE_HEADING = "CPSC public recall API (SaferProducts.gov RestWebServices)"
TIMEOUT_SECONDS = 60

MONTHS = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def build_url(params):
    """Build the query URL. `params` is an ordered list of (key, value).

    Spaces and other reserved characters are percent encoded (%20, not
    +), matching the query URLs recorded in the published deliveries.
    """
    query = [("format", "json")] + list(params)
    return BASE_URL + "?" + urllib.parse.urlencode(
        query, quote_via=urllib.parse.quote
    )


def describe_query(params):
    """Render the query fields the way the deliveries state them:
    ProductName = "VH101" with RecallDateStart = 2018-01-01 ..."""
    parts = []
    for key, value in params:
        if key in ("RecallDateStart", "RecallDateEnd"):
            parts.append("%s = %s" % (key, value))
        else:
            parts.append('%s = "%s"' % (key, value))
    if not parts:
        return "(no query fields)"
    if len(parts) == 1:
        return parts[0]
    return parts[0] + " with " + " and ".join(parts[1:])


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET the URL and return (retrieved_utc, transcript, body_text).

    The transcript is the complete raw HTTP response: status line, the
    headers in the order returned, a blank line, then the body decoded
    as UTF-8 exactly as returned. HTTP error statuses are captured the
    same way rather than raised, so a failed query is still shown
    verbatim.
    """
    retrieved = utc_now_iso()
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "tiny-ledger-cpsc-fetcher"}
    )
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(
            getattr(response, "version", 11), "HTTP/1.1"
        )
        status_line = "%s %s %s" % (version, response.status, response.reason)
        header_lines = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body = response.read().decode("utf-8")
    transcript = "\n".join([status_line] + header_lines + ["", body])
    return retrieved, transcript, body


# ----------------------------------------------------------------------
# Record rendering
# ----------------------------------------------------------------------

def parse_records(body):
    """Parse the response body. Returns a list of records.

    Raises ValueError if the body is not a JSON array; the caller then
    prints the transcript so the odd response is still on record.
    """
    data = json.loads(body)
    if not isinstance(data, list):
        raise ValueError("response body is not a JSON array")
    return data


def dash_recall_number(raw):
    """'18136' -> '18-136'. Numbers that are not five digits are
    returned as shown, since the source form is the only honest one."""
    raw = str(raw or "")
    if len(raw) == 5 and raw.isdigit():
        return raw[:2] + "-" + raw[2:]
    return raw


def long_date(raw):
    """'2018-04-04T00:00:00' -> 'April 4, 2018'. Anything that does not
    parse is returned exactly as shown."""
    try:
        d = datetime.strptime(str(raw)[:10], "%Y-%m-%d")
    except ValueError:
        return str(raw)
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def _names(items, key):
    out = []
    for item in items or []:
        if isinstance(item, dict):
            out.append(str(item.get(key, "")))
    return out


def _numbered(label, values):
    """One line per value. A single value gets the plain label; several
    get '(1 of N)' suffixes so none is silently dropped or merged."""
    if not values:
        return ["- %s: (not present in the API record)" % label]
    if len(values) == 1:
        return ["- %s: %s" % (label, values[0])]
    return [
        "- %s (%d of %d): %s" % (label, i + 1, len(values), v)
        for i, v in enumerate(values)
    ]


def render_record(record):
    """Render one record as the deliveries do under '#### Recall NN-NNN'."""
    number = dash_recall_number(record.get("RecallNumber"))
    products = record.get("Products") or []
    hazards = _names(record.get("Hazards"), "Name")
    remedies = _names(record.get("Remedies"), "Name")
    options = _names(record.get("RemedyOptions"), "Option")

    lines = ["#### Recall %s" % number]
    lines.append("- Recall number: %s" % number)
    lines.append("- Announcement date: %s" % long_date(record.get("RecallDate")))
    lines.append("- Title as shown: %s" % record.get("Title", ""))
    lines.extend(_numbered("Product as shown", _names(products, "Name")))
    lines.extend(_numbered("Hazard as shown", hazards))
    lines.extend(_numbered("Remedy as shown", remedies))
    lines.extend(_numbered("Units as shown", _names(products, "NumberOfUnits")))
    if options:
        lines.append("- Remedy options as shown in the API record: %s" % "; ".join(options))
    lines.append("- CPSC recall page as shown: %s" % record.get("URL", ""))
    if hazards and remedies and hazards == remedies:
        lines.append(
            "- Note: in the API record for %s, the remedy text field repeats "
            "the hazard text word for word. Read the remedy from the CPSC "
            "recall page linked above and quote that page as its own source." % number
        )
    return lines


# ----------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------

def parse_exclusions(values):
    """--exclude 18-199="reason" -> {'18-199': 'reason'}."""
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError(
                "--exclude needs the form RECALL-NUMBER=reason, got %r" % value
            )
        number, reason = value.split("=", 1)
        number = number.strip()
        reason = reason.strip().strip('"').strip("'")
        if not number or not reason:
            raise ValueError(
                "--exclude needs both a recall number and a reason, got %r" % value
            )
        exclusions[dash_recall_number(number.replace("-", ""))] = reason
    return exclusions


def render_section(subject, params, url, retrieved, transcript, body,
                   exclusions=None, pretty=False):
    """Build the whole Markdown section as a list of lines."""
    exclusions = dict(exclusions or {})
    query_text = describe_query(params)
    lines = []
    lines.append("## Subject: %s" % subject)
    lines.append("")
    lines.append(DATABASE_LINE)
    lines.append("")

    parse_error = None
    try:
        records = parse_records(body)
    except ValueError as err:
        records = None
        parse_error = str(err)

    if records is None:
        lines.append(
            "QUERY: %s did not return a JSON array (retrieved %s). The "
            "complete raw HTTP response transcript is shown verbatim beneath "
            "the source link below; %s." % (query_text, retrieved, parse_error)
        )
        lines.append("")
        lines.append("RECALLS: not determinable from this response.")
    else:
        count = len(records)
        noun = "record" if count == 1 else "records"
        lines.append(
            "QUERY: %s returned %d %s (retrieved %s)." % (query_text, count, noun, retrieved)
        )
        if count == 0:
            lines[-1] += (
                " The complete body of the response was an empty array; the "
                "complete raw HTTP response transcript for this query, headers "
                "and body, is shown verbatim beneath the source link below."
            )

        kept, excluded = [], []
        for record in records:
            number = dash_recall_number(record.get("RecallNumber"))
            if number in exclusions:
                excluded.append((record, exclusions.pop(number)))
            else:
                kept.append(record)
        if exclusions:
            raise ValueError(
                "excluded recall number(s) not in the response: %s"
                % ", ".join(sorted(exclusions))
            )

        lines.append("")
        if kept:
            n = len(kept)
            lines.append(
                "RECALLS: %d matching %s found." % (n, "recall" if n == 1 else "recalls")
            )
            for record in kept:
                lines.append("")
                lines.extend(render_record(record))
        else:
            lines.append("RECALLS: none found for %s." % subject)

        if excluded:
            lines.append("")
            lines.append(
                "Checked and excluded: %d %s in the same response %s listed "
                "below with the reason each was excluded."
                % (
                    len(excluded),
                    "record" if len(excluded) == 1 else "records",
                    "is" if len(excluded) == 1 else "are",
                )
            )
            for record, reason in excluded:
                lines.append("")
                lines.extend(render_record(record))
                lines.append("- Checked and excluded because: %s" % reason)

    lines.append("")
    lines.append("### Source. %s" % SOURCE_HEADING)
    lines.append("- Query URL: %s" % url)
    lines.append("- Retrieved (UTC): %s" % retrieved)
    lines.append(
        "Excerpt (complete raw HTTP response transcript for the query above: "
        "status line, headers in the order returned, a blank line, then the "
        "complete body exactly as returned):"
    )
    lines.append("```")
    lines.extend(transcript.split("\n"))
    lines.append("```")

    if pretty and records:
        total = len(records)
        for i, record in enumerate(records):
            lines.append(
                "Excerpt (%s response, record %d of %d, pretty printed, values unchanged):"
                % (query_text, i + 1, total)
            )
            lines.append("```")
            lines.extend(json.dumps(record, indent=2, ensure_ascii=False).split("\n"))
            lines.append("```")
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def build_params(args):
    params = []
    if args.recall_number:
        params.append(("RecallNumber", args.recall_number))
    if args.recall_title:
        params.append(("RecallTitle", args.recall_title))
    if args.product_name:
        params.append(("ProductName", args.product_name))
    if args.date_start:
        params.append(("RecallDateStart", args.date_start))
    if args.date_end:
        params.append(("RecallDateEnd", args.date_end))
    for raw in args.param or []:
        if "=" not in raw:
            raise ValueError("--param needs KEY=VALUE, got %r" % raw)
        key, value = raw.split("=", 1)
        params.append((key, value))
    if not params:
        raise ValueError(
            "give at least one query field (--product-name, --recall-title, "
            "--recall-number, --date-start/--date-end, or --param KEY=VALUE)"
        )
    return params


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Query the CPSC SaferProducts recall API and print one "
        "Markdown section in the delivery format."
    )
    parser.add_argument("--subject", help="subject name for the heading; "
                        "defaults to the query fields")
    parser.add_argument("--product-name", help="ProductName query field")
    parser.add_argument("--recall-title", help="RecallTitle query field")
    parser.add_argument("--recall-number", help="RecallNumber query field, e.g. 18-136")
    parser.add_argument("--date-start", help="RecallDateStart, YYYY-MM-DD")
    parser.add_argument("--date-end", help="RecallDateEnd, YYYY-MM-DD")
    parser.add_argument("--param", action="append", metavar="KEY=VALUE",
                        help="any other API query field, repeatable")
    parser.add_argument("--exclude", action="append", metavar='NN-NNN="reason"',
                        help="list this recall number from the response as "
                        "checked and excluded, with the reason; repeatable")
    parser.add_argument("--pretty", action="store_true",
                        help="also print one pretty printed excerpt per record")
    args = parser.parse_args(argv)

    try:
        params = build_params(args)
        exclusions = parse_exclusions(args.exclude)
    except ValueError as err:
        parser.error(str(err))

    subject = args.subject or describe_query(params)
    url = build_url(params)
    try:
        retrieved, transcript, body = fetch(url)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write(
            "fetch failed, nothing printed: %s\nquery URL: %s\n" % (err, url)
        )
        return 2

    try:
        lines = render_section(subject, params, url, retrieved, transcript,
                               body, exclusions, args.pretty)
    except ValueError as err:
        sys.stderr.write("error: %s\nquery URL: %s\n" % (err, url))
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
