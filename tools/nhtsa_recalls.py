#!/usr/bin/env python3
"""NHTSA recalls fetcher.

Queries the public NHTSA recalls API (api.nhtsa.gov) live and prints one
Markdown section in the delivery format from AGENT-BRIEF.md: the claim
lines, the source link, and the complete raw HTTP response transcript
printed verbatim directly beneath the link.

No key is needed for this source and none is read. The only network
call is the one GET to api.nhtsa.gov. Standard library only.

Usage examples:

    python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
        --make Hyundai --model Elantra --model-year 2021

    python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
        --make Hyundai --model Elantra --model-year 2021 \
        --exclude 21V796000="replaced by 22V354000, which is listed" \
        --pretty

    python3 tools/nhtsa_recalls.py --endpoint recallsByVehicle \
        --param make=Hyundai --param model=Elantra --param modelYear=2021

The endpoint verified against a recorded live response is
recallsByVehicle (make, model, modelYear); the published delivery in
deliveries/ shows its query URL and response, and this tool reproduces
that query URL byte for byte. Any other path under /recalls/ that the
API accepts can be reached with --endpoint and --param; whatever it
returns is printed verbatim in the transcript, and campaign blocks are
rendered only for fields that are present.

What the output contains, in order:

1. A subject heading and the database named.
2. QUERY: the exact query fields, the campaign count, and the
   retrieval time in UTC.
3. RECALLS: one block per campaign with the values as shown in the
   source. Campaigns named with --exclude are listed separately as
   checked and excluded, with the reason given.
4. The source link (the exact query URL) and the retrieval time.
5. Directly beneath the link, the complete raw HTTP response
   transcript: status line, headers in the order returned, a blank
   line, then the body exactly as returned. An empty result is proven
   by that transcript, never asserted.
6. With --pretty, one pretty printed JSON excerpt per campaign after
   the transcript, in response order, values unchanged, the way the
   published deliveries in deliveries/ show records.

The tool never judges relevance. Deciding that a campaign is a near
match to exclude is the operator's call and the reason is the
operator's words; the tool only refuses to list an exclusion for a
campaign number that is not in the response.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://api.nhtsa.gov/recalls/"
DEFAULT_ENDPOINT = "recallsByVehicle"
SOURCE_HEADING = "NHTSA recalls API (api.nhtsa.gov %s)"
TIMEOUT_SECONDS = 60

MONTHS = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def build_url(endpoint, params):
    """Build the query URL. `params` is an ordered list of (key, value).

    Spaces and other reserved characters are percent encoded (%20, not
    +), matching the query URL recorded in the published delivery.
    """
    return BASE_URL + endpoint + "?" + urllib.parse.urlencode(
        list(params), quote_via=urllib.parse.quote
    )


def describe_query(params):
    """Render the query fields the way the delivery states them:
    make = Hyundai, model = Elantra, modelYear = 2021"""
    if not params:
        return "(no query fields)"
    return ", ".join("%s = %s" % (key, value) for key, value in params)


def database_line(endpoint, params):
    if endpoint == DEFAULT_ENDPOINT:
        return (
            "Database: NHTSA public recall data (recallsByVehicle API), "
            "queried by make, model, and model year."
        )
    return "Database: NHTSA public recall data (%s API), queried by %s." % (
        endpoint, ", ".join(key for key, _ in params) or "no fields"
    )


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
        url, headers={"Accept": "application/json", "User-Agent": "tiny-ledger-nhtsa-fetcher"}
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

def parse_response(body):
    """Parse the response body. Returns (count_as_shown, records).

    The recorded response is a JSON object with "Count", "Message" and
    a "results" array. Raises ValueError if the body is not an object
    with a "results" array; the caller then prints the transcript so
    the odd response is still on record.
    """
    data = json.loads(body)
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError('response body is not a JSON object with a "results" array')
    records = [r for r in data["results"] if isinstance(r, dict)]
    if len(records) != len(data["results"]):
        raise ValueError('"results" holds an entry that is not a JSON object')
    return data.get("Count"), records


def campaign_key(raw):
    """Normalise a campaign number for matching only: upper case, no
    dashes or spaces. '22v-354000' -> '22V354000'. Display always uses
    the value as shown in the source."""
    return str(raw or "").upper().replace("-", "").replace(" ", "")


def long_date(raw):
    """'28/04/2021' (day/month/year, as the API shows it) ->
    '28/04/2021 (April 28, 2021)'. Anything that does not parse is
    returned exactly as shown."""
    raw = str(raw or "")
    try:
        d = datetime.strptime(raw, "%d/%m/%Y")
    except ValueError:
        return raw
    return "%s (%s %d, %d)" % (raw, MONTHS[d.month - 1], d.day, d.year)


def _shown(record, key):
    if key in record and record[key] is not None and str(record[key]) != "":
        return str(record[key])
    return None


def _line(label, value):
    if value is None:
        return "- %s: (not present in the API record)" % label
    return "- %s: %s" % (label, value)


def units_keys(record):
    """Field names in the record that look like a unit count. The
    recorded responses carry none, so units are stated as not shown
    unless the API starts returning one."""
    return [k for k in record if "unit" in k.lower()]


def render_record(record):
    """Render one campaign as the delivery does under '#### Campaign NNNNNNNNN'."""
    number = _shown(record, "NHTSACampaignNumber")
    heading = number if number is not None else "(campaign number not present in the API record)"
    product_parts = [p for p in (_shown(record, "ModelYear"), _shown(record, "Make"), _shown(record, "Model")) if p]
    product = " ".join(product_parts) if product_parts else None

    lines = ["#### Campaign %s" % heading]
    lines.append(_line("NHTSA campaign number", number))
    lines.append(_line("Manufacturer as shown", _shown(record, "Manufacturer")))
    date = _shown(record, "ReportReceivedDate")
    lines.append(_line("Date as shown (ReportReceivedDate)", long_date(date) if date else None))
    if product is None:
        lines.append(_line("Product as shown", None))
    else:
        lines.append("- Product as shown: %s; Component as shown: %s" % (
            product, _shown(record, "Component") or "(not present in the API record)"))
    lines.append(_line("Summary as shown", _shown(record, "Summary")))
    lines.append(_line("Hazard as shown (Consequence)", _shown(record, "Consequence")))
    lines.append(_line("Remedy as shown", _shown(record, "Remedy")))
    lines.append(_line("Notes as shown", _shown(record, "Notes")))
    flags = [k for k in ("parkIt", "parkOutSide", "overTheAirUpdate") if k in record]
    if flags:
        lines.append("- Flags as shown: " + "; ".join(
            "%s = %s" % (k, json.dumps(record[k])) for k in flags))
    keys = units_keys(record)
    if keys:
        for k in keys:
            lines.append("- Units as shown (%s): %s" % (k, record[k]))
    else:
        lines.append("- Units: not shown")
    return lines


# ----------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------

def parse_exclusions(values):
    """--exclude 21V796000="reason" -> {'21V796000': 'reason'}."""
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError(
                "--exclude needs the form CAMPAIGN-NUMBER=reason, got %r" % value
            )
        number, reason = value.split("=", 1)
        number = campaign_key(number)
        reason = reason.strip().strip('"').strip("'")
        if not number or not reason:
            raise ValueError(
                "--exclude needs both a campaign number and a reason, got %r" % value
            )
        exclusions[number] = reason
    return exclusions


def render_section(subject, endpoint, params, url, retrieved, transcript, body,
                   exclusions=None, pretty=False):
    """Build the whole Markdown section as a list of lines."""
    exclusions = dict(exclusions or {})
    query_text = describe_query(params)
    lines = []
    lines.append("## Subject: %s" % subject)
    lines.append("")
    lines.append(database_line(endpoint, params))
    lines.append("")

    parse_error = None
    try:
        count_shown, records = parse_response(body)
    except ValueError as err:
        records = None
        parse_error = str(err)

    if records is None:
        lines.append(
            "QUERY: %s did not return the expected JSON object (retrieved %s). "
            "The complete raw HTTP response transcript is shown verbatim "
            "beneath the source link below; %s." % (query_text, retrieved, parse_error)
        )
        lines.append("")
        lines.append("RECALLS: not determinable from this response.")
    else:
        count = len(records)
        noun = "campaign" if count == 1 else "campaigns"
        query_line = "QUERY: %s returned %d %s (retrieved %s)." % (
            query_text, count, noun, retrieved)
        if count_shown is not None and count_shown != count:
            query_line += (
                ' The response\'s own "Count" field shows %s, which differs from '
                "the %d entries in its results array; both are in the transcript "
                "beneath the source link." % (json.dumps(count_shown), count)
            )
        if count == 0:
            query_line += (
                " The results array in the response was empty; the complete raw "
                "HTTP response transcript for this query, headers and body, is "
                "shown verbatim beneath the source link below."
            )
        elif not any(units_keys(r) for r in records):
            query_line += (
                " The API shows no unit counts for these campaigns, so units "
                "are stated as not shown."
            )
        lines.append(query_line)

        kept, excluded = [], []
        for record in records:
            key = campaign_key(record.get("NHTSACampaignNumber"))
            if key in exclusions:
                excluded.append((record, exclusions.pop(key)))
            else:
                kept.append(record)
        if exclusions:
            raise ValueError(
                "excluded campaign number(s) not in the response: %s"
                % ", ".join(sorted(exclusions))
            )

        lines.append("")
        if kept:
            n = len(kept)
            lines.append(
                "RECALLS: %d matching %s found." % (n, "campaign" if n == 1 else "campaigns")
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
                    "campaign" if len(excluded) == 1 else "campaigns",
                    "is" if len(excluded) == 1 else "are",
                )
            )
            for record, reason in excluded:
                lines.append("")
                lines.extend(render_record(record))
                lines.append("- Checked and excluded because: %s" % reason)

    lines.append("")
    lines.append("### Source. %s" % (SOURCE_HEADING % endpoint))
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
                "Excerpt (%s response, campaign %d of %d in response order, "
                "pretty printed, values unchanged):" % (query_text, i + 1, total)
            )
            lines.append("```")
            lines.extend(json.dumps(record, indent=2, ensure_ascii=False).split("\n"))
            lines.append("```")
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def build_query(args):
    """Return (endpoint, params) from the parsed arguments."""
    endpoint = args.endpoint or DEFAULT_ENDPOINT
    params = []
    if args.make:
        params.append(("make", args.make))
    if args.model:
        params.append(("model", args.model))
    if args.model_year:
        params.append(("modelYear", args.model_year))
    for raw in args.param or []:
        if "=" not in raw:
            raise ValueError("--param needs KEY=VALUE, got %r" % raw)
        key, value = raw.split("=", 1)
        params.append((key, value))
    if endpoint == DEFAULT_ENDPOINT:
        keys = [key for key, _ in params]
        missing = [k for k in ("make", "model", "modelYear") if k not in keys]
        if missing:
            raise ValueError(
                "recallsByVehicle needs make, model, and modelYear; missing: %s "
                "(give --make, --model, --model-year, or --param KEY=VALUE)"
                % ", ".join(missing)
            )
    elif not params:
        raise ValueError("give at least one --param KEY=VALUE for endpoint %s" % endpoint)
    if "/" in endpoint or "?" in endpoint:
        raise ValueError("--endpoint is one path segment under %s, got %r" % (BASE_URL, endpoint))
    return endpoint, params


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Query the NHTSA recalls API and print one Markdown "
        "section in the delivery format."
    )
    parser.add_argument("--subject", help="subject name for the heading; "
                        "defaults to the query fields")
    parser.add_argument("--make", help="make query field, e.g. Hyundai")
    parser.add_argument("--model", help="model query field, e.g. Elantra")
    parser.add_argument("--model-year", help="modelYear query field, e.g. 2021")
    parser.add_argument("--endpoint", help="path segment under %s; default %s"
                        % (BASE_URL, DEFAULT_ENDPOINT))
    parser.add_argument("--param", action="append", metavar="KEY=VALUE",
                        help="any other API query field, repeatable")
    parser.add_argument("--exclude", action="append", metavar='NNVNNNNNN="reason"',
                        help="list this campaign number from the response as "
                        "checked and excluded, with the reason; repeatable")
    parser.add_argument("--pretty", action="store_true",
                        help="also print one pretty printed excerpt per campaign")
    args = parser.parse_args(argv)

    try:
        endpoint, params = build_query(args)
        exclusions = parse_exclusions(args.exclude)
    except ValueError as err:
        parser.error(str(err))

    subject = args.subject or describe_query(params)
    url = build_url(endpoint, params)
    try:
        retrieved, transcript, body = fetch(url)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write(
            "fetch failed, nothing printed: %s\nquery URL: %s\n" % (err, url)
        )
        return 2

    try:
        lines = render_section(subject, endpoint, params, url, retrieved, transcript,
                               body, exclusions, args.pretty)
    except ValueError as err:
        sys.stderr.write("error: %s\nquery URL: %s\n" % (err, url))
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
