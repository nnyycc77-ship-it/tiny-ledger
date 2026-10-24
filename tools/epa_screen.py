#!/usr/bin/env python3
"""EPA facility compliance screen (issue #178, tool factory wave 2).

Does this facility show EPA violations or significant noncompliance? Asks
the public EPA ECHO facility search web service (echodata.epa.gov) live and
prints one Markdown section in the delivery format from AGENT-BRIEF.md:
the answer first, quoting the source's own status fields, then each
source link with the complete raw HTTP response transcript beneath it.

No key is needed and none is read. Every GET uses the capture path of
tools/nhtsa_recalls.py. Standard library only.

Usage:

    python3 tools/epa_screen.py --name "BAYTOWN OLEFINS" --city BAYTOWN --state TX
    python3 tools/epa_screen.py --name "BAYTOWN OLEFINS" --state TX --registry-id 110000463178

The facility search is two steps, as the coordinator's live captures on
issue #178 show (tools/tests/fixtures/epa-echo/, with provenance):

    1. echo_rest_services.get_facilities?output=JSON&p_fn=<name>[&p_cty=<city>]&p_st=<state>
       answers a summary with QueryRows and a QueryID;
    2. echo_rest_services.get_qid?output=JSON&qid=<QueryID>
       answers the facility rows.

Only the parameters those captured calls use are sent. ECHO's service
pages could not be captured, so nothing here relies on them. No single
facility route is verified (the captures show get_dfr answering HTTP 500,
and p_id on get_facilities acting as an unfiltered search), so a
--registry-id never replaces the search: it selects, from the rows the
search returns, the row with that RegistryID.

The answer quotes three row fields as shown and nothing else:
FacComplianceStatus, FacSNCFlg (significant noncompliance flag) and
FacQtrsWithNC. A null is shown as null. The tool does not total, score or
judge.

Source failures. The HTTP status is checked first: any status other than
200 is a source failure. So is a body that is not the JSON object the
service returns, or one whose Results carries an Error (the captures show
ECHO answering HTTP 200 with an Error body). A source failure prints no
report; it names the source, the query, the status and the body.

Empty results. A summary with QueryRows "0" is an empty result, proven by
its transcript. It shows only that the service answered zero rows for
these parameters: the captures show an invalid state code answering the
same way. It is never a finding that a facility is free of violations.
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

BASE_URL = "https://echodata.epa.gov/echo/echo_rest_services."
ANSWER_FIELDS = ("FacComplianceStatus", "FacSNCFlg", "FacQtrsWithNC")
STATE_PATTERN = re.compile(r"^[A-Z]{2}$")
REGISTRY_PATTERN = re.compile(r"^\d{1,15}$")


class SourceFailed(Exception):
    """A source answered with a failure. No report is produced."""

    def __init__(self, step, url, status, body):
        self.step, self.url, self.status, self.body = step, url, status, body
        super().__init__("%s failed: %s answered %s; body: %s" % (step, url, status, body))


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_query(name, state, city=None, registry_id=None):
    """Validated (name, state, city, registry_id). Raises ValueError."""
    name = " ".join(str(name or "").split())
    state = str(state or "").strip().upper()
    city = " ".join(str(city or "").split()) or None
    registry_id = str(registry_id or "").strip() or None
    if not name:
        raise ValueError("name is required (the facility name to search for)")
    if not STATE_PATTERN.match(state):
        raise ValueError("state is a two letter code such as TX, got %r" % state)
    if registry_id is not None and not REGISTRY_PATTERN.match(registry_id):
        raise ValueError("registry_id is the EPA RegistryID, digits only, got %r" % registry_id)
    return name, state, city, registry_id


def search_url(name, state, city=None):
    """Spaces in values are sent as + (urlencode's default), the form of
    the recorded search."""
    params = [("output", "JSON"), ("p_fn", name)]
    if city:
        params.append(("p_cty", city))
    params.append(("p_st", state))
    return BASE_URL + "get_facilities?" + urllib.parse.urlencode(params)


def rows_url(query_id):
    return BASE_URL + "get_qid?" + urllib.parse.urlencode([("output", "JSON"), ("qid", query_id)])


def describe_query(name, state, city=None, registry_id=None):
    text = "p_fn = %s" % name
    if city:
        text += ", p_cty = %s" % city
    text += ", p_st = %s" % state
    if registry_id:
        text += "; rows filtered to RegistryID %s" % registry_id
    return text


# ----------------------------------------------------------------------
# Fetching and checking
# ----------------------------------------------------------------------

def fetch(url):
    """GET the URL; (retrieved_utc, transcript, body_text), as nhtsa_recalls.fetch."""
    return nr.fetch(url)


def status_line(transcript):
    """The response's status line. A transcript recorded with curl through a
    proxy starts with the proxy's 'Connection Established' reply and uses
    CRLF line ends; both are skipped here."""
    for line in transcript.split("\n"):
        line = line.rstrip("\r")
        if line.startswith("HTTP/") and not line.endswith("Connection Established"):
            return line
    return transcript.split("\n", 1)[0].rstrip("\r")


def checked(step, url, capture):
    """The Results object of a 200 JSON answer without an Error, or SourceFailed."""
    _, transcript, body = capture
    status = status_line(transcript)
    parts = status.split(" ")
    if len(parts) < 2 or parts[1] != "200":
        raise SourceFailed(step, url, status, body)
    try:
        data = json.loads(body)
    except ValueError:
        raise SourceFailed(step, url, status + " (body is not JSON)", body)
    results = data.get("Results") if isinstance(data, dict) else None
    if not isinstance(results, dict):
        raise SourceFailed(step, url, status + ' (no "Results" object)', body)
    if "Error" in results:
        raise SourceFailed(step, url, status + " (Results carries an Error)", body)
    return results


def gather(name, state, city=None):
    """Fetch the summary, then the rows when there are any. Returns
    (search_url, search_capture, summary, rows_url, rows_capture, rows_results, rows);
    the rows fields are None (and rows []) when QueryRows is "0"."""
    surl = search_url(name, state, city)
    scap = fetch(surl)
    summary = checked("ECHO facility search (get_facilities)", surl, scap)
    if str(summary.get("QueryRows")) == "0":
        return surl, scap, summary, None, None, None, []
    qid = summary.get("QueryID")
    if not qid:
        raise SourceFailed("ECHO facility search (get_facilities)", surl,
                           status_line(scap[1]) + " (QueryRows is not 0 but no QueryID)", scap[2])
    rurl = rows_url(qid)
    rcap = fetch(rurl)
    results = checked("ECHO facility rows (get_qid)", rurl, rcap)
    rows = results.get("Facilities")
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise SourceFailed("ECHO facility rows (get_qid)", rurl,
                           status_line(rcap[1]) + ' (no "Facilities" array of objects)', rcap[2])
    return surl, scap, summary, rurl, rcap, results, rows


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def shown(value):
    return "null" if value is None else json.dumps(value, ensure_ascii=False)


def answer_line(row):
    place = ", ".join(str(row[k]) for k in ("FacCity", "FacState") if row.get(k))
    return "- %s (RegistryID %s%s): FacComplianceStatus %s; FacSNCFlg %s; FacQtrsWithNC %s" % (
        row.get("FacName"), row.get("RegistryID"), ", " + place if place else "",
        shown(row.get("FacComplianceStatus")), shown(row.get("FacSNCFlg")), shown(row.get("FacQtrsWithNC")))


def source_block(heading, url, capture):
    retrieved, transcript, _ = capture
    return ["", "### Source. %s" % heading, "- Query URL: %s" % url, "- Retrieved (UTC): %s" % retrieved,
            "Excerpt (complete raw HTTP response transcript for the query above: status line, headers in "
            "the order returned, a blank line, then the complete body exactly as returned):",
            "```"] + transcript.split("\n") + ["```"]


def render(name, state, city, registry_id, gathered):
    surl, scap, summary, rurl, rcap, rows_results, rows = gathered
    query_text = describe_query(name, state, city, registry_id)
    lines = ["## Subject: %s, %s%s" % (name, (city + ", ") if city else "", state), "",
             "Database: EPA ECHO facility search web service (echodata.epa.gov), searched by facility "
             "name%s and state." % (", city" if city else ""), ""]
    retrieved = scap[0] if rcap is None else "%s and %s" % (scap[0], rcap[0])
    lines.append("QUERY: %s. The search answered QueryRows %s (retrieved %s)." % (
        query_text, shown(summary.get("QueryRows")), retrieved))
    lines.append("")
    if not rows:
        lines.append("ANSWER: the service answered zero rows for these parameters (QueryRows \"0\" in the "
                     "summary beneath the source link below). That is all it shows: it is not a finding that "
                     "any facility is free of violations, and an unrecognised parameter can answer the same way.")
        return lines + source_block("EPA ECHO get_facilities", surl, scap)
    selected = rows if registry_id is None else [r for r in rows if str(r.get("RegistryID")) == registry_id]
    if not selected:
        lines.append("ANSWER: RegistryID %s is not among the %d rows the search returned, listed here as "
                     "returned:" % (registry_id, len(rows)))
        lines += [answer_line(r) for r in rows]
    else:
        lines.append("ANSWER, as the source states it (FacComplianceStatus, FacSNCFlg and FacQtrsWithNC "
                     "quoted from each row; null where the row carries none):")
        lines += [answer_line(r) for r in selected]
        if registry_id is None and len(rows) > 1:
            lines += ["", "These are %d different facility records returned for the search. Which one is the "
                      "facility meant is the caller's call; give a RegistryID to select one." % len(rows)]
    if str(summary.get("QueryRows")) != str(len(rows)):
        lines += ["", "The summary shows QueryRows %s; the rows response holds %d rows (PageNo %s)." % (
            shown(summary.get("QueryRows")), len(rows), shown(rows_results.get("PageNo")))]
    lines += source_block("EPA ECHO get_facilities (search summary)", surl, scap)
    lines += source_block("EPA ECHO get_qid (facility rows)", rurl, rcap)
    return lines


def run(name, state, city=None, registry_id=None):
    name, state, city, registry_id = check_query(name, state, city, registry_id)
    return render(name, state, city, registry_id, gather(name, state, city))


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Screen a facility in EPA ECHO and print one Markdown section in the delivery format.")
    parser.add_argument("--name", required=True, help="facility name to search for")
    parser.add_argument("--state", required=True, help="two letter state code, e.g. TX")
    parser.add_argument("--city", help="city, to narrow the search")
    parser.add_argument("--registry-id", help="EPA RegistryID: selects that row from the search results")
    args = parser.parse_args(argv)
    try:
        name, state, city, registry_id = check_query(args.name, args.state, args.city, args.registry_id)
    except ValueError as err:
        parser.error(str(err))
    try:
        lines = render(name, state, city, registry_id, gather(name, state, city))
    except SourceFailed as err:
        sys.stderr.write("source failure, nothing printed: %s\n" % err)
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
