#!/usr/bin/env python3
"""US address geocode check (issue #319, tool factory wave 3).

Given one US street address, reads the US Census Bureau geocoder and
prints one Markdown report in the delivery format from AGENT-BRIEF.md:
the answer first (the matched address, its coordinates, and its county,
each as shown), then the evidence: the query's exact URL, UTC retrieval
time, the fields cut verbatim from the response, and the complete raw
response.

    python3 tools/address_geocode_check.py 1600 Pennsylvania Ave NW, Washington, DC 20500

Source, keyless: the Census Geocoder, geographies/onelineaddress with
benchmark=Public_AR_Current and vintage=Current_Current, both pinned
because an unpinned benchmark or vintage drifts silently as the Census
Bureau republishes (documented at
https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html;
the response shape, the geography layer names "Counties" and "Census
Tracts", and the field names matchedAddress, coordinates,
addressComponents and GEOID are from the live captures recorded in
tools/tests/fixtures/census-geocoder/provenance.json). coordinates.x is
the longitude and coordinates.y the latitude (-77.03..., 38.89... for
the Washington, DC capture). The geographies endpoint is used rather
than locations/onelineaddress because it returns the county (and the
census tract) with the match.

Outcomes: one or more matches is a report listing each match. An empty
addressMatches array is a report too, of no match, with the raw
response as the proof; it is never shown as a statement that the
address does not exist. A failed or timed out request, any status but
200, a redirect off the source host, or a body without the documented
shape stops the run with exit 2 and no report: a failed fetch is
unknown, never a no match.

Standard library only.
"""

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import Node, fenced, inline, skip_ws  # noqa: E402

API_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
BENCHMARK = "Public_AR_Current"
VINTAGE = "Current_Current"
USER_AGENT = "tiny-ledger-address-geocode-check"
TIMEOUT_SECONDS = 30
MAX_ADDRESS_CHARS = 200
HIDDEN_HEADERS = ("set-cookie",)

NOTE = ("Coordinates are interpolated along the matched address range by the Census Geocoder; they are not a "
        "rooftop or parcel point. This report records what the public US Census Bureau geocoder returned at "
        "the retrieval time stated below.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, retrieved, status_line, headers, body):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        shown = [kv for kv in self.headers if kv[0].lower() not in HIDDEN_HEADERS]
        lines = [self.status_line] + ["%s: %s" % kv for kv in shown]
        if len(shown) != len(self.headers):
            lines.append("(a Set-Cookie header was returned and is not printed)")
        return "\n".join(lines + ["", self.body])


# ----------------------------------------------------------------------
# Inputs and URLs
# ----------------------------------------------------------------------

def check_address(address):
    text = " ".join((address or "").split())
    if not text or len(text) > MAX_ADDRESS_CHARS:
        raise ValueError("address must be 1 to %d characters" % MAX_ADDRESS_CHARS)
    return text


def geocoder_url(address):
    query = urllib.parse.urlencode([("address", address), ("benchmark", BENCHMARK), ("vintage", VINTAGE),
                                    ("format", "json")], quote_via=urllib.parse.quote)
    return "%s?%s" % (API_URL, query)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        raise FetchError("%s answered HTTP %s; no report" % (url, err.code))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, getattr(response, "reason", ""))
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("%s answered %s; no report" % (url, status_line))
    if urllib.parse.urlsplit(final_url).netloc != urllib.parse.urlsplit(url).netloc:
        raise FetchError("%s was redirected off its host; no report" % url)
    return Capture(url, retrieved, status_line, headers, body)


def root(capture):
    try:
        return Node(capture.body, skip_ws(capture.body, 0))
    except (ValueError, IndexError) as err:
        raise FetchError("%s answered a body that is not a JSON object (%s); no report" % (capture.url, err))


# ----------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------

def county_of(match):
    """The first Counties geography Node of a match. Raises ValueError when
    the geographies carry no county, which the documented shape always has."""
    geographies = match.child("geographies")
    counties = geographies.children("Counties")
    if not counties:
        raise ValueError("a match has no Counties geography")
    county = counties[0]
    if not (county.has("NAME") and county.has("GEOID")):
        raise ValueError("a county has no NAME or GEOID")
    return county


def tract_of(match):
    """The first Census Tracts geography Node of a match, or None when the
    layer is absent or empty (the tract is reported only when returned)."""
    try:
        tracts = match.child("geographies").children("Census Tracts")
    except (ValueError, IndexError, KeyError):
        return None
    if tracts and tracts[0].has("GEOID"):
        return tracts[0]
    return None


def matches(capture):
    """The validated addressMatches Nodes. Raises FetchError when the body
    is not the documented geocoder shape."""
    node = root(capture)
    try:
        found = node.child("result").children("addressMatches")
        for m in found:
            coords = m.child("coordinates")
            if not (m.has("matchedAddress") and coords.has("x") and coords.has("y")):
                raise ValueError("a match has no matchedAddress or coordinates x and y")
            x, y = coords.value("x"), coords.value("y")
            if isinstance(x, bool) or isinstance(y, bool) \
                    or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError("a match has coordinates that are not numbers")
            if not -180 <= x <= 180 or not -90 <= y <= 90:
                raise ValueError("a match has coordinates out of range (x %r, y %r)" % (x, y))
            components = m.child("addressComponents")
            if not all(components.has(k) for k in ("city", "state", "zip")):
                raise ValueError("a match has addressComponents without city, state and zip")
            county_of(m)
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented geocoder shape (%s); no report"
                         % (capture.url, err))
    return found


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def match_answer(match, index, total):
    coords = match.child("coordinates")
    county = county_of(match)
    components = match.child("addressComponents")
    lines = []
    if total > 1:
        lines += ["Match %d of %d:" % (index, total)]
    lines += ["- Matched address (matchedAddress) as shown: %s" % inline(match.literal("matchedAddress")),
              "- Coordinates as shown: x (longitude) %s, y (latitude) %s"
              % (coords.literal("x"), coords.literal("y")),
              "- County (Counties geography) as shown: %s (GEOID %s)"
              % (inline(county.literal("NAME")), inline(county.literal("GEOID")))]
    tract = tract_of(match)
    if tract is not None:
        lines += ["- Census tract (Census Tracts geography) GEOID as shown: %s" % inline(tract.literal("GEOID"))]
    lines += ["- Address components as shown: city %s, state %s, ZIP %s"
              % (components.value("city"), components.value("state"), components.value("zip")), ""]
    return lines


def evidence(capture, found):
    lines = ["### US Census Geocoder, geographies/onelineaddress (benchmark %s, vintage %s)"
             % (BENCHMARK, VINTAGE), "",
             "Exact query URL: <%s>" % capture.url, "",
             "Retrieved (UTC): %s" % capture.retrieved, ""]
    if found:
        cut = []
        for m in found:
            fields = [m.excerpt("matchedAddress"), m.excerpt("coordinates"),
                      county_of(m).excerpt("NAME"), county_of(m).excerpt("GEOID")]
            tract = tract_of(m)
            if tract is not None:
                fields.append(tract.excerpt("GEOID"))
            cut.append("\n".join(fields))
        lines += ["Fields, verbatim from the response:", fenced("\n\n".join(cut)), ""]
    lines += ["Complete raw response:", fenced(capture.transcript()), ""]
    return lines


def report(address, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    capture = fetcher(geocoder_url(address))
    found = matches(capture)
    head = ["# Address geocode check: %s" % address, "", NOTE, ""]
    if found:
        answer = []
        for i, m in enumerate(found, 1):
            answer += match_answer(m, i, len(found))
    else:
        answer = ["The Census Geocoder matched no address for %s. Its empty addressMatches array in the "
                  "complete raw response below is the proof. This is the geocoder's answer for this input, "
                  "not a statement that no such address exists." % inline(address), ""]
    return head + ["## Answer", ""] + answer + ["## Evidence", ""] + evidence(capture, found)


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="US Census Bureau geocoder check for one US street address.")
    p.add_argument("address", nargs="*", help="a US street address, in one line")
    args = p.parse_args(argv)
    try:
        lines = report(check_address(" ".join(args.address)), fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
