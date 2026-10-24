#!/usr/bin/env python3
"""FDA drug label check (issue #163, tool factory wave 1).

Looks up one drug by brand or generic name with the public openFDA drug
label endpoint (api.fda.gov/drug/label.json) live and prints one Markdown
section in the delivery format from AGENT-BRIEF.md: the claim lines, the
source link, and the complete raw HTTP response transcript printed
verbatim directly beneath the link.

No key is needed for this source and none is read. The only network
call is the one GET to api.fda.gov, made with the capture path of
tools/nhtsa_recalls.py. Standard library only.

Usage examples:

    python3 tools/fda_drug_check.py Lipitor
    python3 tools/fda_drug_check.py Tylenol
    python3 tools/fda_drug_check.py acetaminophen

The query is one search over the two name fields the endpoint indexes,
with a limit of one record:

    https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22<name>%22+OR+openfda.generic_name:%22<name>%22&limit=1

Many labels can share one name (the response's own meta.results.total
says how many matched). The facts below are the first returned record's,
and the report states the total as shown so the scope is never hidden.

What the output contains, in order:

1. A subject heading and the database named.
2. QUERY: the name searched, the HTTP status, the retrieval time in
   UTC, and the total matches the response itself reports.
3. LABEL: the first record's label facts as shown: brand and generic
   names, the maker (openfda.manufacturer_name), product type and
   route, which of the warning sections (boxed_warning, warnings,
   warnings_and_cautions) are present in the record, and the dosage
   form. openFDA label records carry no structured dosage form field:
   the tool prints the record's dosage_form when the record has one,
   else the text of its dosage_forms_and_strengths section, else it
   states plainly that the record carries neither. Nothing is filled
   in from outside the record.
4. The source link (the exact query URL) and the retrieval time.
5. Directly beneath the link, the complete raw HTTP response
   transcript: status line, headers in the order returned, a blank
   line, then the body exactly as returned.

A name no label matches is answered by openFDA itself with HTTP 404
and an error body (code NOT_FOUND, message "No matches found!"); the
report quotes that body and the transcript beneath the source link
proves it. A transport failure prints nothing on stdout and exits 2:
a failed fetch is never an empty result. This tool records what one
label says; it is not medical advice and it does not summarise or
rewrite the label's warning text.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import nhtsa_recalls as nr  # noqa: E402

BASE_URL = "https://api.fda.gov/drug/label.json"
SOURCE_HEADING = "openFDA drug label API (api.fda.gov/drug/label.json)"
WARNING_FIELDS = ("boxed_warning", "warnings", "warnings_and_cautions")
MAX_NAME_CHARS = 100


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_name(raw):
    """A drug brand or generic name for a quoted phrase search.

    The name goes inside double quotes in the search, so a double
    quote, a backslash or a control character is refused rather than
    escaped into a different query than the one the operator asked for.
    """
    name = str(raw or "").strip()
    if not name:
        raise ValueError("give a drug brand or generic name, for example Lipitor")
    if len(name) > MAX_NAME_CHARS:
        raise ValueError("name is at most %d characters, got %d" % (MAX_NAME_CHARS, len(name)))
    for ch in name:
        if ch in '"\\' or ord(ch) < 32:
            raise ValueError("name must not contain a double quote, a backslash or a control character")
    return name


def build_url(name):
    """The query URL: one phrase search over brand and generic names, limit 1."""
    quoted = urllib.parse.quote(name, safe="")
    return "%s?search=openfda.brand_name:%%22%s%%22+OR+openfda.generic_name:%%22%s%%22&limit=1" % (
        BASE_URL, quoted, quoted)


def describe_query(name):
    return 'search = openfda.brand_name:"%s" OR openfda.generic_name:"%s", limit = 1' % (name, name)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def fetch(url):
    """GET the URL; (retrieved_utc, transcript, body_text), as nhtsa_recalls.fetch."""
    return nr.fetch(url)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def status_of(transcript):
    return transcript.split("\n", 1)[0]


def parse_response(body):
    """The body as a JSON object. Raises ValueError when it is not one."""
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("response body is not a JSON object")
    return data


def _shown_list(record, key):
    """A record field that is a list of values, printed as shown, else None."""
    value = record.get(key)
    if isinstance(value, list) and value:
        return ", ".join(str(v) for v in value)
    if isinstance(value, str) and value:
        return value
    return None


def _line(label, value):
    if value is None:
        return "- %s: (not present in the API record)" % label
    return "- %s: %s" % (label, value)


def render_label(data, name):
    """The LABEL lines for a parsed body that carries results or an error."""
    error = data.get("error")
    if isinstance(error, dict):
        return ["LABEL: no drug label record matched %s. The body's error as shown: "
                "code %s, message %s. The complete raw HTTP response transcript is shown "
                "verbatim beneath the source link below." % (
                    json.dumps(name, ensure_ascii=False),
                    json.dumps(error.get("code"), ensure_ascii=False),
                    json.dumps(error.get("message"), ensure_ascii=False))]
    results = data.get("results")
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise ValueError('response body holds no "results" list with a record')
    record = results[0]
    openfda = record.get("openfda") if isinstance(record.get("openfda"), dict) else {}
    total = None
    meta = data.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("results"), dict):
        total = meta["results"].get("total")
    lines = []
    head = "LABEL: first returned record of %s matching label record(s) (total as shown in the response)." % (
        total if total is not None else "an unstated number of")
    lines.append(head)
    lines.append(_line("brand_name as shown", _shown_list(openfda, "brand_name")))
    lines.append(_line("generic_name as shown", _shown_list(openfda, "generic_name")))
    lines.append(_line("maker (openfda.manufacturer_name) as shown",
                       _shown_list(openfda, "manufacturer_name")))
    lines.append(_line("product_type as shown", _shown_list(openfda, "product_type")))
    lines.append(_line("route as shown", _shown_list(openfda, "route")))
    present = [field for field in WARNING_FIELDS
               if isinstance(record.get(field), list) and record[field]]
    if present:
        lines.append("- warnings present: the record carries %s." % ", ".join(present))
    else:
        lines.append("- warnings present: none of the warning sections this tool checks "
                     "(%s) is present in the record." % ", ".join(WARNING_FIELDS))
    lines.append("- warning sections checked: %s" % ", ".join(WARNING_FIELDS))
    dosage_form = _shown_list(record, "dosage_form")
    if dosage_form is not None:
        lines.append("- dosage form as shown: %s" % dosage_form)
    else:
        strengths = _shown_list(record, "dosage_forms_and_strengths")
        if strengths is not None:
            lines.append("- dosage form: the record carries no dosage_form field; its "
                         "dosage_forms_and_strengths section as shown: %s" % strengths)
        else:
            lines.append("- dosage form: (not present in the API record: the record carries "
                         "neither a dosage_form field nor a dosage_forms_and_strengths section)")
    lines.append(_line("effective_time as shown", _shown_list(record, "effective_time")))
    return lines


def render_section(name, url, retrieved, transcript, body):
    """Build the whole Markdown section as a list of lines."""
    lines = ["## Subject: %s" % name, "",
             "Database: openFDA drug label data (api.fda.gov/drug/label.json), queried by "
             "brand or generic name; the first matching label record is reported.", ""]
    lines.append("QUERY: %s answered %s (retrieved %s)." % (
        describe_query(name), status_of(transcript), retrieved))
    lines.append("")
    try:
        data = parse_response(body)
        lines.extend(render_label(data, name))
    except ValueError as err:
        lines.append("LABEL: not determinable from this response; %s. The complete raw HTTP "
                     "response transcript is shown verbatim beneath the source link below." % err)
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
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Look up one drug's FDA label facts with the openFDA drug label API and "
        "print one Markdown section in the delivery format.")
    parser.add_argument("name", help="the drug brand or generic name, e.g. Lipitor")
    args = parser.parse_args(argv)
    try:
        name = check_name(args.name)
    except ValueError as err:
        parser.error(str(err))
    url = build_url(name)
    try:
        retrieved, transcript, body = fetch(url)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\nquery URL: %s\n" % (err, url))
        return 2
    lines = render_section(name, url, retrieved, transcript, body)
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
