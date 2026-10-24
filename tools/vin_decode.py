#!/usr/bin/env python3
"""VIN decode check (issue #161, tool factory wave 1).

Decodes one VIN with the public NHTSA vPIC API (vpic.nhtsa.dot.gov) live
and prints one Markdown section in the delivery format from
AGENT-BRIEF.md: the claim lines, the source link, and the complete raw
HTTP response transcript printed verbatim directly beneath the link.

No key is needed for this source and none is read. The only network
call is the one GET to vpic.nhtsa.dot.gov, made with the capture path of
tools/nhtsa_recalls.py. Standard library only.

Usage examples:

    python3 tools/vin_decode.py 1HGCM82633A004352
    python3 tools/vin_decode.py "5UXWX7C5*BA" --model-year 2011 --pretty

The endpoint is DecodeVinValues, the flat format decode, with
format=json. The URL is built as the vPIC API page shows it
(https://vpic.nhtsa.dot.gov/api/, "Decode VIN (flat format)"):

    https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/<VIN>?format=json[&modelyear=<year>]

The page says partial VINs are accepted, with "*" for unavailable
characters, and that it is recommended to always send the model year;
--model-year adds it. The five recorded responses this tool is tested on
are in tools/tests/fixtures/vpic/ with their provenance.

What the output contains, in order:

1. A subject heading and the database named.
2. QUERY: the VIN and model year sent, the number of results, and the
   retrieval time in UTC.
3. VPIC STATUS: the response's own ErrorCode and ErrorText, quoted as
   shown. vPIC reports check digit, incomplete VIN and other problems
   there; this tool repeats them and does not compute its own.
4. DECODE: the vehicle as shown (model year, make, model, trim), then
   every field that has a value, in response order, as shown. Fields
   that came back empty are counted, and the response's own Message
   about missing values is quoted. When make, model and model year are
   all empty, the section says no vehicle was decoded.
5. The source link (the exact query URL) and the retrieval time.
6. Directly beneath the link, the complete raw HTTP response
   transcript: status line, headers in the order returned, a blank
   line, then the body exactly as returned. An empty result is proven
   by that transcript, never asserted.
7. With --pretty, the result object pretty printed after the
   transcript, values unchanged.

The tool never judges the vehicle. It adds no value vPIC did not return,
and does not say what an error code means beyond vPIC's own ErrorText.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import nhtsa_recalls as nr  # noqa: E402

BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"
SOURCE_HEADING = "NHTSA vPIC API (vpic.nhtsa.dot.gov DecodeVinValues)"
VIN_PATTERN = re.compile(r"^[A-Z0-9*]{1,17}$")
YEAR_PATTERN = re.compile(r"^\d{4}$")

# The vehicle line, in this order, from the fields vPIC returns.
VEHICLE_FIELDS = ("ModelYear", "Make", "Model", "Trim")
# Shown on the status line, so not repeated in the field list.
STATUS_FIELDS = ("ErrorCode", "ErrorText")


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_vin(raw):
    """Upper case, spaces removed; 1 to 17 letters, digits or '*'.

    Only the characters are checked here, so that the URL is one path
    segment. Whether the VIN is valid is vPIC's answer, in ErrorCode.
    """
    vin = "".join(str(raw or "").split()).upper()
    if not VIN_PATTERN.match(vin):
        raise ValueError("a VIN is 1 to 17 letters or digits, with * for an unknown "
                         "character, got %r" % raw)
    return vin


def check_year(raw):
    if raw is None or str(raw).strip() == "":
        return None
    year = str(raw).strip()
    if not YEAR_PATTERN.match(year):
        raise ValueError("model year is four digits, got %r" % raw)
    return year


def build_url(vin, model_year=None):
    """The query URL, with '*' left as is, as on the vPIC API page."""
    url = BASE_URL + urllib.parse.quote(vin, safe="*") + "?format=json"
    if model_year:
        url += "&modelyear=" + model_year
    return url


def describe_query(vin, model_year=None):
    text = "VIN = %s" % vin
    if model_year:
        text += ", modelyear = %s" % model_year
    return text


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def fetch(url):
    """GET the URL; (retrieved_utc, transcript, body_text), as nhtsa_recalls.fetch."""
    return nr.fetch(url)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def parse_response(body):
    """Parse the body. Returns (count_as_shown, message, results).

    The recorded responses are a JSON object with "Count", "Message",
    "SearchCriteria" and a "Results" array of flat objects. Raises
    ValueError otherwise; the caller then prints the transcript so the
    odd response is still on record.
    """
    data = json.loads(body)
    if not isinstance(data, dict) or not isinstance(data.get("Results"), list):
        raise ValueError('response body is not a JSON object with a "Results" array')
    results = data["Results"]
    if not all(isinstance(r, dict) for r in results):
        raise ValueError('"Results" holds an entry that is not a JSON object')
    return data.get("Count"), data.get("Message"), results


def _shown(record, key):
    value = record.get(key)
    if value is None or str(value).strip() == "":
        return None
    return str(value)


def render_result(record, message):
    """The status and decode lines for one result object."""
    lines = []
    code, text = _shown(record, "ErrorCode"), _shown(record, "ErrorText")
    lines.append("VPIC STATUS: ErrorCode as shown: %s; ErrorText as shown: %s" % (
        json.dumps(code) if code is not None else "(not present)",
        json.dumps(text, ensure_ascii=False) if text is not None else "(not present)"))
    extra = _shown(record, "AdditionalErrorText")
    if extra is not None:
        lines.append("- AdditionalErrorText as shown: %s" % extra)
    lines.append("")
    vehicle = [_shown(record, k) for k in VEHICLE_FIELDS]
    if not any(_shown(record, k) for k in ("ModelYear", "Make", "Model")):
        lines.append("DECODE: no vehicle decoded. Make, Model and ModelYear are empty in the "
                     "response; the complete raw HTTP response transcript is shown verbatim "
                     "beneath the source link below.")
    else:
        lines.append("DECODE: vehicle as shown: %s" % " ".join(v for v in vehicle if v))
    filled = [(k, v) for k, v in record.items()
              if k not in STATUS_FIELDS and k != "AdditionalErrorText" and _shown(record, k) is not None]
    empty = sum(1 for k in record if _shown(record, k) is None)
    lines.append("")
    lines.append("Fields with a value, in response order (%d):" % len(filled))
    for key, value in filled:
        lines.append("- %s: %s" % (key, value))
    if empty:
        note = ("%d other field%s came back empty." % (empty, "" if empty == 1 else "s"))
        if message:
            note += " The response's own Message says: %s" % json.dumps(message, ensure_ascii=False)
        lines.append("")
        lines.append(note)
    return lines


def render_section(vin, model_year, url, retrieved, transcript, body, pretty=False):
    """Build the whole Markdown section as a list of lines."""
    query_text = describe_query(vin, model_year)
    lines = ["## Subject: VIN %s" % vin, "",
             "Database: NHTSA vPIC API, DecodeVinValues "
             "(flat format), queried by VIN%s." % (" and model year" if model_year else ""), ""]
    try:
        count_shown, message, results = parse_response(body)
    except ValueError as err:
        results = None
        lines.append("QUERY: %s did not return the expected JSON object (retrieved %s). The "
                     "complete raw HTTP response transcript is shown verbatim beneath the source "
                     "link below; %s." % (query_text, retrieved, err))
        lines.append("")
        lines.append("DECODE: not determinable from this response.")
    else:
        n = len(results)
        query_line = "QUERY: %s returned %d result%s (retrieved %s)." % (
            query_text, n, "" if n == 1 else "s", retrieved)
        if count_shown is not None and count_shown != n:
            query_line += (' The response\'s own "Count" field shows %s, which differs from the %d '
                           "entries in its Results array; both are in the transcript beneath the "
                           "source link." % (json.dumps(count_shown), n))
        lines.append(query_line)
        lines.append("")
        if not results:
            lines.append("DECODE: no vehicle decoded. The Results array in the response was empty; "
                         "the complete raw HTTP response transcript is shown verbatim beneath the "
                         "source link below.")
        for i, record in enumerate(results):
            if n > 1:
                lines.append("### Result %d of %d" % (i + 1, n))
                lines.append("")
            lines.extend(render_result(record, message))
            lines.append("")
        if results:
            lines.pop()

    lines.append("")
    lines.append("### Source. %s" % SOURCE_HEADING)
    lines.append("- Query URL: %s" % url)
    lines.append("- Retrieved (UTC): %s" % retrieved)
    lines.append("Excerpt (complete raw HTTP response transcript for the query above: status "
                 "line, headers in the order returned, a blank line, then the complete body "
                 "exactly as returned):")
    lines.append("```")
    lines.extend(transcript.split("\n"))
    lines.append("```")
    if pretty and results:
        for i, record in enumerate(results):
            lines.append("Excerpt (%s response, result %d of %d, pretty printed, values unchanged):"
                         % (query_text, i + 1, len(results)))
            lines.append("```")
            lines.extend(json.dumps(record, indent=2, ensure_ascii=False).split("\n"))
            lines.append("```")
    return lines


def run(vin, model_year=None, pretty=False):
    """Validate, fetch once, render. Returns the section lines.
    Raises ValueError on a bad input (no fetch) and URLError/OSError on a
    failed fetch (no report)."""
    vin = check_vin(vin)
    model_year = check_year(model_year)
    url = build_url(vin, model_year)
    retrieved, transcript, body = fetch(url)
    return render_section(vin, model_year, url, retrieved, transcript, body, pretty)


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Decode a VIN with the NHTSA vPIC API and print one Markdown section "
        "in the delivery format.")
    parser.add_argument("vin", help="the VIN, 17 characters, or fewer with * for unknown ones")
    parser.add_argument("--model-year", help="modelyear query field, e.g. 2011 (vPIC recommends sending it)")
    parser.add_argument("--pretty", action="store_true",
                        help="also print the result object pretty printed")
    args = parser.parse_args(argv)
    try:
        vin = check_vin(args.vin)
        year = check_year(args.model_year)
    except ValueError as err:
        parser.error(str(err))
    url = build_url(vin, year)
    try:
        retrieved, transcript, body = fetch(url)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\nquery URL: %s\n" % (err, url))
        return 2
    lines = render_section(vin, year, url, retrieved, transcript, body, args.pretty)
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
