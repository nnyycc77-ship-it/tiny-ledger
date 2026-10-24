#!/usr/bin/env python3
"""NHTSA model safety file (issue #176, tool factory wave 2).

For one make, model and model year, queries three public NHTSA APIs on
api.nhtsa.gov live and prints one combined Markdown safety file in the
delivery format from AGENT-BRIEF.md. Each section states only what its
own raw response shows, then gives its source link with the complete raw
HTTP response transcript directly beneath it.

    1. Safety ratings: /SafetyRatings/modelyear/<year>/make/<make>/model/<model>
       lists the rated variants; /SafetyRatings/VehicleId/<id> gives each
       variant's ratings.
    2. Recalls: /recalls/recallsByVehicle?make=&model=&modelYear=
    3. Complaints: /complaints/complaintsByVehicle?make=&model=&modelYear=

No key is needed and none is read. Every GET uses the capture path of
tools/nhtsa_recalls.py. Standard library only.

Usage:

    python3 tools/safety_file.py --make Hyundai --model Elantra --year 2021

The endpoint shapes are the ones the coordinator's live captures on
issue #176 show (tools/tests/fixtures/nhtsa-safety/, with provenance);
NHTSA's documentation page refused the capture, so none is cited.

Source failures. The captures show that these endpoints can answer HTTP
400 or 500 while the body still reads "Results returned successfully".
So the HTTP status is checked first: any status other than 200, or a body
that is not the JSON shape the endpoint returns, is a source failure. A
source failure is never an empty result. The tool prints no report, and
names each failed source, its exact query, its status and its body.

Empty results. A 200 response whose results are empty is an empty
result, stated as such and proven by its transcript. The recorded case is
safety ratings for an unknown model: HTTP 200, Count 0, Results [].

Counting. The recalls and complaints sections state the response's own
count field, the number of records in its results array, and counts the
tool makes by reading the records beneath (for example how many
complaints have crash set to true). Each such count is labelled as the
tool's own count of the records shown.
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

BASE_URL = "https://api.nhtsa.gov/"
MAX_VARIANTS = 6
LISTED_COMPLAINTS = 10
YEAR_PATTERN = re.compile(r"^\d{4}$")

# Rating fields shown, in this order, when the record carries them.
RATING_FIELDS = (
    "OverallRating", "OverallFrontCrashRating", "FrontCrashDriversideRating",
    "FrontCrashPassengersideRating", "OverallSideCrashRating", "SideCrashDriversideRating",
    "SideCrashPassengersideRating", "SidePoleCrashRating", "RolloverRating", "RolloverPossibility",
    "NHTSAElectronicStabilityControl", "NHTSAForwardCollisionWarning", "NHTSALaneDepartureWarning",
    "ComplaintsCount", "RecallsCount", "InvestigationCount",
)


class SourceFailed(Exception):
    """One or more sources answered with a failure. No report is produced."""

    def __init__(self, failures):
        self.failures = failures
        super().__init__("; ".join(
            "%s source failed: %s answered %s; body: %s" % (f["section"], f["url"], f["status"], f["body"])
            for f in failures))


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_query(make, model, year):
    """Validated (make, model, year). Raises ValueError."""
    make, model, year = (str(v or "").strip() for v in (make, model, year))
    for label, value in (("make", make), ("model", model)):
        if not value:
            raise ValueError("%s is required" % label)
        if "/" in value or "?" in value or "#" in value:
            raise ValueError("%s must not contain / ? or #, got %r" % (label, value))
    if not YEAR_PATTERN.match(year):
        raise ValueError("year is four digits, got %r" % year)
    return make, model, year


def _segment(value):
    return urllib.parse.quote(value, safe="")


def ratings_url(make, model, year):
    return BASE_URL + "SafetyRatings/modelyear/%s/make/%s/model/%s" % (_segment(year), _segment(make), _segment(model))


def vehicle_url(vehicle_id):
    return BASE_URL + "SafetyRatings/VehicleId/%s" % _segment(str(vehicle_id))


def _vehicle_query(make, model, year):
    return urllib.parse.urlencode([("make", make), ("model", model), ("modelYear", year)],
                                  quote_via=urllib.parse.quote)


def recalls_url(make, model, year):
    return BASE_URL + "recalls/recallsByVehicle?" + _vehicle_query(make, model, year)


def complaints_url(make, model, year):
    return BASE_URL + "complaints/complaintsByVehicle?" + _vehicle_query(make, model, year)


# ----------------------------------------------------------------------
# Fetching and checking
# ----------------------------------------------------------------------

def fetch(url):
    """GET the URL; (retrieved_utc, transcript, body_text), as nhtsa_recalls.fetch."""
    return nr.fetch(url)


def status_line(transcript):
    return transcript.split("\n", 1)[0]


def status_code(transcript):
    parts = status_line(transcript).split(" ")
    return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None


def checked(section, url, capture, results_key):
    """Return (capture, data) for a 200 JSON object holding a results list
    under `results_key`; anything else is a failure record."""
    retrieved, transcript, body = capture
    failure = {"section": section, "url": url, "status": status_line(transcript), "body": body}
    if status_code(transcript) != 200:
        return None, failure
    try:
        data = json.loads(body)
    except ValueError:
        return None, dict(failure, status=failure["status"] + " (body is not JSON)")
    if not isinstance(data, dict) or not isinstance(data.get(results_key), list) \
            or not all(isinstance(r, dict) for r in data[results_key]):
        return None, dict(failure, status=failure["status"] + ' (no "%s" array of objects)' % results_key)
    return data, None


def gather(make, model, year, max_variants=MAX_VARIANTS):
    """Fetch every source once. Returns the sections in order. Raises
    SourceFailed naming every failed source; nothing is reported then."""
    failures, sections = [], []

    url = ratings_url(make, model, year)
    cap = fetch(url)
    data, failure = checked("Safety ratings", url, cap, "Results")
    variants = []
    if failure:
        failures.append(failure)
    else:
        for variant in data["Results"][:max_variants]:
            vurl = vehicle_url(variant.get("VehicleId"))
            vcap = fetch(vurl)
            vdata, vfailure = checked("Safety ratings", vurl, vcap, "Results")
            if vfailure:
                failures.append(vfailure)
            else:
                variants.append((variant, vurl, vcap, vdata))
    sections.append(("ratings", url, cap, data, variants))

    for name, label, build in (("recalls", "Recalls", recalls_url), ("complaints", "Complaints", complaints_url)):
        url = build(make, model, year)
        cap = fetch(url)
        data, failure = checked(label, url, cap, "results")
        if failure:
            failures.append(failure)
        sections.append((name, url, cap, data, None))

    if failures:
        raise SourceFailed(failures)
    return sections


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def source_block(heading, url, capture):
    retrieved, transcript, _ = capture
    return ["", "#### Source. %s" % heading, "- Query URL: %s" % url, "- Retrieved (UTC): %s" % retrieved,
            "Excerpt (complete raw HTTP response transcript for the query above: status line, headers "
            "in the order returned, a blank line, then the complete body exactly as returned):",
            "```"] + transcript.split("\n") + ["```"]


def render_ratings(url, cap, data, variants, max_variants):
    count, results = data.get("Count"), data["Results"]
    lines = ["### 1. Safety ratings", ""]
    if not results:
        lines.append("RATINGS: none found. The variants query returned an empty Results array (Count as "
                     "shown: %s); the complete raw HTTP response transcript is shown verbatim beneath the "
                     "source link below." % json.dumps(count))
        return lines + source_block("NHTSA Safety Ratings API, variants for the model year", url, cap)
    lines.append("RATINGS: the variants query lists %d rated variant%s (Count as shown: %s)." % (
        len(results), "" if len(results) == 1 else "s", json.dumps(count)))
    for v in results:
        lines.append("- %s (VehicleId %s)" % (v.get("VehicleDescription"), v.get("VehicleId")))
    if len(results) > max_variants:
        lines.append("Only the first %d variants are fetched below; the others are listed above only."
                     % max_variants)
    lines += source_block("NHTSA Safety Ratings API, variants for the model year", url, cap)
    for variant, vurl, vcap, vdata in variants:
        lines += ["", "#### Ratings for %s (VehicleId %s)" % (variant.get("VehicleDescription"),
                                                            variant.get("VehicleId")), ""]
        if not vdata["Results"]:
            lines.append("No ratings record: the VehicleId query returned an empty Results array; "
                         "the transcript beneath the source link below shows it.")
        for record in vdata["Results"]:
            shown = [k for k in RATING_FIELDS if k in record]
            for key in shown:
                lines.append("- %s as shown: %s" % (key, record[key]))
            if not shown:
                lines.append("- The record carries none of the rating fields this tool lists; "
                             "the whole record is in the transcript below.")
        lines += source_block("NHTSA Safety Ratings API, VehicleId %s" % variant.get("VehicleId"), vurl, vcap)
    return lines


def render_recalls(url, cap, data):
    results = data["results"]
    lines = ["### 2. Recalls", ""]
    count_note = 'the response\'s own "Count" field shows %s' % json.dumps(data.get("Count"))
    if not results:
        lines.append("RECALLS: none found; the results array is empty (%s). The complete raw HTTP "
                     "response transcript is shown verbatim beneath the source link below." % count_note)
    else:
        lines.append("RECALLS: %d campaign%s in the results array (%s)." % (
            len(results), "" if len(results) == 1 else "s", count_note))
        for r in results:
            lines.append("- %s, ReportReceivedDate as shown %s, Component as shown: %s" % (
                r.get("NHTSACampaignNumber"), r.get("ReportReceivedDate"), r.get("Component")))
    return lines + source_block("NHTSA recalls API, recallsByVehicle", url, cap)


def render_complaints(url, cap, data, listed=LISTED_COMPLAINTS):
    results = data["results"]
    lines = ["### 3. Complaints", ""]
    count_note = 'the response\'s own "count" field shows %s' % json.dumps(data.get("count"))
    if not results:
        lines.append("COMPLAINTS: none found; the results array is empty (%s). The complete raw HTTP "
                     "response transcript is shown verbatim beneath the source link below." % count_note)
        return lines + source_block("NHTSA complaints API, complaintsByVehicle", url, cap)
    lines.append("COMPLAINTS: %d complaint record%s in the results array (%s)." % (
        len(results), "" if len(results) == 1 else "s", count_note))
    lines.append("This tool's own counts of the records beneath:")
    lines.append("- with crash = true: %d" % sum(1 for r in results if r.get("crash") is True))
    lines.append("- with fire = true: %d" % sum(1 for r in results if r.get("fire") is True))
    lines.append("- with numberOfInjuries above 0: %d" % sum(
        1 for r in results if isinstance(r.get("numberOfInjuries"), int) and r["numberOfInjuries"] > 0))
    lines.append("- with numberOfDeaths above 0: %d" % sum(
        1 for r in results if isinstance(r.get("numberOfDeaths"), int) and r["numberOfDeaths"] > 0))
    shown = results[:listed]
    lines.append("The first %d records in response order (odiNumber, dateComplaintFiled as shown, components "
                 "as shown):" % len(shown))
    for r in shown:
        lines.append("- %s, %s, %s" % (r.get("odiNumber"), r.get("dateComplaintFiled"), r.get("components")))
    return lines + source_block("NHTSA complaints API, complaintsByVehicle", url, cap)


def render(make, model, year, sections, max_variants=MAX_VARIANTS):
    lines = ["## Safety file: %s %s %s" % (year, make, model), "",
             "Database: NHTSA public APIs on api.nhtsa.gov (safety ratings, recalls, complaints), queried by "
             "model year, make and model. Each section states only what its own raw response, printed "
             "beneath its source link, shows.", ""]
    retrieved = sorted(s[2][0] for s in sections)
    lines.append("QUERY: make = %s, model = %s, modelYear = %s; %d source requests, retrieved %s to %s (UTC)." % (
        make, model, year, len(sections) + len(sections[0][4]), retrieved[0], retrieved[-1]))
    for name, url, cap, data, variants in sections:
        lines.append("")
        if name == "ratings":
            lines += render_ratings(url, cap, data, variants, max_variants)
        elif name == "recalls":
            lines += render_recalls(url, cap, data)
        else:
            lines += render_complaints(url, cap, data)
    ratings = [r for _, _, _, vdata in sections[0][4] for r in vdata["Results"]]
    cross = []
    for key, name in (("RecallsCount", "recalls"), ("ComplaintsCount", "complaints")):
        records = [s for s in sections if s[0] == name][0][3]["results"]
        for r in ratings:
            if key in r:
                cross.append("- %s as shown in the ratings record for VehicleId %s: %s; records in the %s "
                             "response: %d." % (key, r.get("VehicleId"), r[key], name, len(records)))
    if cross:
        lines += ["", "### Cross check", "", "The ratings records carry their own counts; both are shown, "
                  "neither is adjusted:"] + cross
    return lines


def run(make, model, year, max_variants=MAX_VARIANTS):
    make, model, year = check_query(make, model, year)
    return render(make, model, year, gather(make, model, year, max_variants), max_variants)


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build an NHTSA safety file (ratings, recalls, complaints) for one make, model and year.")
    parser.add_argument("--make", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--year", required=True, help="model year, four digits")
    args = parser.parse_args(argv)
    try:
        make, model, year = check_query(args.make, args.model, args.year)
    except ValueError as err:
        parser.error(str(err))
    try:
        lines = render(make, model, year, gather(make, model, year))
    except SourceFailed as err:
        sys.stderr.write("source failure, nothing printed:\n")
        for f in err.failures:
            sys.stderr.write("- %s: %s answered %s; body: %s\n" % (f["section"], f["url"], f["status"], f["body"]))
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
