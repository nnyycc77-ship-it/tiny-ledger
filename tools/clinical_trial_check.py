#!/usr/bin/env python3
"""Clinical trial check: trials matching a company, drug, or condition.

Task: issue #162 (tool factory wave 1, parent #158). Given one search
term, this tool asks the public ClinicalTrials.gov API v2 (keyless) for
the studies matching it and prints one Markdown section in the delivery
format from AGENT-BRIEF.md: the trial count and the top trials with
their status as claim lines, then the source link with the complete raw
HTTP response transcript printed verbatim beneath it.

The request names the fields the report prints, through the API's
`fields` parameter: NCTId, BriefTitle, OverallStatus, LeadSponsorName,
Condition, Phase. The captured responses in
tools/tests/fixtures/clinical-trials/ show the API answering with only
those fields, plus totalCount, the studies array, and a nextPageToken
when more results follow.

What the claim lines say, all read from the response as shown:

* totalCount as shown, and the number of studies in this response (the
  two differ whenever the count runs past one page; both are shown and
  never reconciled);
* per study, in response order: nctId, briefTitle, overallStatus,
  leadSponsor name, conditions, and phases, each as shown or
  "not shown" when the response omits that module or field; and
* whether the response carries a nextPageToken, as shown.

An empty result is a response with totalCount 0 and an empty studies
array; it is reported in those terms with the complete raw response
beneath, as the proof. Fail closed: a response that is not HTTP 200, a
body that is not a JSON object with an integer totalCount and a studies
array of objects, or a transport failure prints nothing on stdout and
exits 2. A failed fetch is never shown as an empty result.

Usage, with an example drug name:

    python3 tools/clinical_trial_check.py "Zolgensma"

Standard library only. No key, account, or environment value is needed.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

STUDIES_URL = "https://clinicaltrials.gov/api/v2/studies"
USER_AGENT = "tiny-ledger-clinical-trial-check"
TIMEOUT_SECONDS = 30
DEFAULT_LIMIT = 10
MAX_LIMIT = 100  # this tool's own cap on the page size it will ask for
FIELDS_PARAM = "NCTId,BriefTitle,OverallStatus,LeadSponsorName,Condition,Phase"
SCOPE_LINE = ("Observation only: the trials below are what the public ClinicalTrials.gov API v2 "
              "returned for this search at the stated time, in the order returned. Trial statuses "
              "and listings change; this is not a review of any trial, drug, or sponsor.")


class FetchError(Exception):
    """A response that cannot be reported. Never rendered as an empty result."""


# ----------------------------------------------------------------------
# Inputs and URL
# ----------------------------------------------------------------------

def check_inputs(term, limit=DEFAULT_LIMIT):
    term = " ".join(str(term or "").split())
    if not term:
        raise ValueError("give a company, drug, or condition to search for")
    if not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be between 1 and %d" % MAX_LIMIT)
    return term, limit


def search_url(term, limit=DEFAULT_LIMIT):
    return STUDIES_URL + "?" + urllib.parse.urlencode(
        [("query.term", term), ("countTotal", "true"), ("pageSize", limit),
         ("fields", FIELDS_PARAM), ("format", "json")])


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
    """One HTTP exchange: URL, UTC retrieval time, status line, headers in
    the order returned, body as returned."""

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
    def status(self):
        """The status code: the first three digit field of the status line."""
        m = re.search(r"(?:^|\s)(\d{3})(?:\s|$)", self.status_line)
        if not m:
            raise FetchError("%s: no status code in the status line %r" % (self.url, self.status_line))
        return int(m.group(1))

    @property
    def status_text(self):
        m = re.search(r"(?:^|\s)(\d{3}(?:\s.*)?)$", self.status_line)
        return m.group(1) if m else self.status_line


def fetch(url):
    """GET the studies URL. HTTP error statuses are captured, not raised;
    transport errors propagate."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body = response.read().decode("utf-8")
    return Capture(url, retrieved, status_line, headers, body)


# ----------------------------------------------------------------------
# Reading and rendering
# ----------------------------------------------------------------------

def parse(capture):
    """(totalCount, studies, nextPageToken) of a studies response; refuses
    anything but HTTP 200 with a JSON object holding an integer totalCount
    and a studies array of objects."""
    if capture.status != 200:
        raise FetchError("%s answered %s, not 200; no report" % (capture.url, capture.status_line))
    try:
        data = json.loads(capture.body)
    except ValueError as err:
        raise FetchError("%s body is not JSON (%s); no report" % (capture.url, err))
    if (not isinstance(data, dict) or not isinstance(data.get("totalCount"), int)
            or isinstance(data.get("totalCount"), bool)
            or not isinstance(data.get("studies"), list)
            or any(not isinstance(s, dict) for s in data["studies"])):
        raise FetchError("%s body is not an object with an integer totalCount and a studies array; "
                         "no report" % capture.url)
    return data["totalCount"], data["studies"], data.get("nextPageToken")


def module(study, name):
    section = study.get("protocolSection")
    if not isinstance(section, dict):
        return {}
    value = section.get(name)
    return value if isinstance(value, dict) else {}


def shown(value):
    if value is None or value == "" or value == []:
        return "not shown"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def inline(text):
    ticks = "``" if "`" in text else "`"
    pad = " " if ticks == "``" else ""
    return "%s%s%s%s%s" % (ticks, pad, text, pad, ticks)


TRIAL_FIELDS = [
    ("NCTId (identificationModule.nctId)", lambda s: module(s, "identificationModule").get("nctId")),
    ("Brief title (identificationModule.briefTitle)", lambda s: module(s, "identificationModule").get("briefTitle")),
    ("Overall status (statusModule.overallStatus)", lambda s: module(s, "statusModule").get("overallStatus")),
    ("Lead sponsor (sponsorCollaboratorsModule.leadSponsor.name)",
     lambda s: (module(s, "sponsorCollaboratorsModule").get("leadSponsor") or {}).get("name")
     if isinstance(module(s, "sponsorCollaboratorsModule").get("leadSponsor"), dict) else None),
    ("Conditions (conditionsModule.conditions)", lambda s: module(s, "conditionsModule").get("conditions")),
    ("Phases (designModule.phases)", lambda s: module(s, "designModule").get("phases")),
]


def render(term, limit, capture):
    count, studies, next_token = parse(capture)
    lines = ["## Clinical trial search: %s" % term, "", SCOPE_LINE, ""]
    lines.append("QUERY: ClinicalTrials.gov API v2 studies search, query.term = %s, countTotal = true, "
                 "pageSize = %d, fields = %s, format = json (retrieved %s; source S1). "
                 "HTTP status as returned: %s."
                 % (inline(term), limit, FIELDS_PARAM, capture.retrieved, capture.status_text))
    lines.append("Trial count (totalCount) as shown: %d. Studies in this response: %d." % (count, len(studies)))
    lines.append("")
    if not studies:
        lines += ["The search returned no trials. The complete raw response is in source S1; this is a "
                  "search observation, not proof that no matching trial exists.", ""]
    for i, study in enumerate(studies, 1):
        lines.append("### Trial %d of %d" % (i, len(studies)))
        lines.append("")
        for label, read in TRIAL_FIELDS:
            lines.append("- %s as shown: %s" % (label, inline(shown(read(study)))))
        lines.append("")
    if studies:
        lines += ["Trials shown are the first %d of the %d the count reports, in the order returned. "
                  "The response carries a nextPageToken: %s (source S1)."
                  % (len(studies), count, "yes" if next_token else "no"), ""]
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines += ["## Sources", "",
              "### Source. S1. ClinicalTrials.gov API v2 studies search, term %s" % inline(term),
              "- Request URL: %s" % capture.url,
              "- Retrieved (UTC): %s" % capture.retrieved,
              "Excerpt (complete raw HTTP response transcript for the request above: status line, headers in "
              "the order returned, a blank line, then the body exactly as returned):",
              fence] + capture.transcript.split("\n") + [fence]
    return lines


def run(term, limit=DEFAULT_LIMIT, fetcher=None):
    term, limit = check_inputs(term, limit)
    capture = (fetcher or fetch)(search_url(term, limit))
    return render(term, limit, capture)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clinical trials matching a company, drug, or condition, "
                                                 "in the delivery format.")
    parser.add_argument("term", help="company, drug, or condition to search for")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help="trials to ask for, 1 to %d; default %d" % (MAX_LIMIT, DEFAULT_LIMIT))
    args = parser.parse_args(argv)
    try:
        lines = run(args.term, args.limit)
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    except FetchError as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
