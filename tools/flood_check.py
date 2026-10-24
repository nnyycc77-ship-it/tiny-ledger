#!/usr/bin/env python3
"""FEMA flood zone check (issue #175, tool factory wave 2).

Given a point (latitude and longitude) or a US street address, reads the
FEMA National Flood Hazard Layer (NFHL) at that point and prints one
Markdown report in the delivery format from AGENT-BRIEF.md: the answer
first (flood zone, zone subtype, SFHA, static BFE, FIRM panel and its
effective date, each as shown), then the evidence: every query's exact
URL, UTC retrieval time, the fields cut verbatim from the response, and
the complete raw response.

    python3 tools/flood_check.py 27.9235 -82.4515
    python3 tools/flood_check.py --address "1600 Pennsylvania Ave NW, Washington, DC"

Screening only: not a Standard Flood Hazard Determination and not
insurance advice.

Sources, both keyless:
- FEMA NFHL MapServer point queries, layer 28 (Flood Hazard Zones) and
  layer 3 (FIRM Panels). The query shape and the field names (FLD_ZONE,
  ZONE_SUBTY, SFHA_TF, STATIC_BFE, DFIRM_ID; FIRM_PAN, EFF_DATE,
  PANEL_TYP) are the ones recorded in the committed delivery
  deliveries/flood-screen-d4f252e4-8a3b-40dd-981e-befb2de63da0.md; the
  "features" array of objects each holding "attributes" is shown in
  deliveries/site-diligence-12164581-c517-4e51-8d25-76b4f7f58ecd-rev1.md
  (S6 to S11). As in those deliveries: SFHA is true when SFHA_TF is T and
  false when it is F; STATIC_BFE -9999 means none; EFF_DATE is epoch
  milliseconds, printed raw first with the UTC date after it.
- US Census Geocoder, locations/onelineaddress with
  benchmark=Public_AR_Current and format=json (documented at
  https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html;
  response shape from the coordinator captures on issue #175). Only for
  --address. coordinates.x is the longitude and coordinates.y the
  latitude, as the captured match shows (-77.03..., 38.89... for
  Washington, DC). The flood queries run only on exactly one match.

Outcomes: a point query with features is a report. An empty features
array is a report too, of no polygon on that layer at that point, with the
raw response as the proof; it is never shown as "not in a flood zone". An
address with no match, or with more than one, is a report of the
geocoder's answer with no flood query. A failed request, any status but
200, a redirect off the source host, or a body without the documented
shape (an ArcGIS error answer included) stops the run with exit 2 and no
report.

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

from propublica_nonprofits import Node, elements, fenced, inline, skip_ws  # noqa: E402

NFHL_URL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/{layer}/query"
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
BENCHMARK = "Public_AR_Current"
USER_AGENT = "tiny-ledger-flood-check"
TIMEOUT_SECONDS = 30
MAX_ADDRESS_CHARS = 200
NO_BFE = -9999
HIDDEN_HEADERS = ("set-cookie",)

ZONES = {"layer": 28, "name": "Flood Hazard Zones",
         "fields": ("FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE", "DFIRM_ID")}
PANELS = {"layer": 3, "name": "FIRM Panels", "fields": ("FIRM_PAN", "EFF_DATE", "PANEL_TYP")}

SCREENING = ("Screening only: not a Standard Flood Hazard Determination and not insurance advice. This report "
             "records what the public FEMA National Flood Hazard Layer returned at the retrieval time stated "
             "below.")


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

def check_point(lat, lon):
    """(lat, lon) as floats, or ValueError."""
    try:
        la, lo = float(lat), float(lon)
    except (TypeError, ValueError):
        raise ValueError("latitude and longitude must be numbers (got %r, %r)" % (lat, lon))
    if not -90 <= la <= 90 or not -180 <= lo <= 180:
        raise ValueError("latitude must be -90 to 90 and longitude -180 to 180 (got %r, %r)" % (lat, lon))
    return la, lo


def check_address(address):
    text = " ".join((address or "").split())
    if not text or len(text) > MAX_ADDRESS_CHARS:
        raise ValueError("address must be 1 to %d characters" % MAX_ADDRESS_CHARS)
    return text


def layer_url(layer, lat, lon):
    query = urllib.parse.urlencode([
        ("geometry", "%r,%r" % (lon, lat)), ("geometryType", "esriGeometryPoint"), ("inSR", "4326"),
        ("spatialRel", "esriSpatialRelIntersects"), ("outFields", "*"), ("returnGeometry", "false"), ("f", "json")])
    return "%s?%s" % (NFHL_URL.format(layer=layer), query)


def geocoder_url(address):
    query = urllib.parse.urlencode([("address", address), ("benchmark", BENCHMARK), ("format", "json")],
                                   quote_via=urllib.parse.quote)
    return "%s?%s" % (GEOCODER_URL, query)


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

def features(capture, layer):
    """The attributes Nodes of the features array. Raises FetchError when the
    body is not the documented shape (an ArcGIS error answer included)."""
    node = root(capture)
    try:
        if not node.has("features"):
            raise ValueError("no features array (members: %s)" % (", ".join(sorted(node.spans)) or "none"))
        _, start, _ = node.spans["features"]
        if node.raw[start] != "[":
            raise ValueError("features is not an array")
        out = []
        for s, _ in elements(node.raw, start):
            attrs = Node(node.raw, s).child("attributes")
            missing = [f for f in layer["fields"] if not attrs.has(f)]
            if missing:
                raise ValueError("a feature has no %s" % ", ".join(missing))
            out.append(attrs)
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented %s query shape (%s); no report"
                         % (capture.url, layer["name"], err))
    return out


def geocoder_matches(capture):
    """The addressMatches Nodes. Raises FetchError when the shape differs."""
    node = root(capture)
    try:
        result = node.child("result")
        matches = result.children("addressMatches")
        for m in matches:
            coords = m.child("coordinates")
            if not (m.has("matchedAddress") and coords.has("x") and coords.has("y")):
                raise ValueError("a match has no matchedAddress or coordinates x and y")
            check_point(coords.value("y"), coords.value("x"))
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented geocoder shape (%s); no report"
                         % (capture.url, err))
    return matches


def sfha(attrs):
    value = attrs.value("SFHA_TF")
    return {"T": "true", "F": "false"}.get(value, "neither T nor F as shown")


def bfe(attrs):
    value = attrs.value("STATIC_BFE")
    return "none (the service returns %s)" % attrs.literal("STATIC_BFE") if value == NO_BFE else attrs.literal("STATIC_BFE")


def eff_date(attrs):
    value = attrs.value("EFF_DATE")
    if isinstance(value, int) and not isinstance(value, bool):
        day = datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        return "%s (%s UTC, converted from epoch milliseconds)" % (attrs.literal("EFF_DATE"), day)
    return "%s (not epoch milliseconds; shown as returned)" % attrs.literal("EFF_DATE")


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def evidence(title, capture, attrs_list, layer=None):
    lines = ["### %s" % title, "", "Exact query URL: <%s>" % capture.url, "",
             "UTC retrieval time: %s" % capture.retrieved, ""]
    if layer and attrs_list:
        lines += ["Fields, verbatim from the response:",
                  fenced("\n\n".join("\n".join(a.excerpt(f) for f in layer["fields"]) for a in attrs_list)), ""]
    lines += ["Complete raw response:", fenced(capture.transcript()), ""]
    return lines


def flood_sections(lat, lon, zones_cap, panels_cap):
    """(answer lines, evidence lines) for one point."""
    zones, panels = features(zones_cap, ZONES), features(panels_cap, PANELS)
    answer = ["Point: latitude %r, longitude %r" % (lat, lon), ""]
    if zones:
        for i, a in enumerate(zones, 1):
            answer += ["Flood Hazard Zones feature %d of %d (layer 28):" % (i, len(zones)),
                       "- Flood zone (FLD_ZONE) as shown: %s" % inline(a.literal("FLD_ZONE")),
                       "- Zone subtype (ZONE_SUBTY) as shown: %s" % inline(a.literal("ZONE_SUBTY")),
                       "- SFHA: %s (SFHA_TF as shown: %s)" % (sfha(a), inline(a.literal("SFHA_TF"))),
                       "- Static BFE (STATIC_BFE): %s" % bfe(a),
                       "- DFIRM ID (DFIRM_ID) as shown: %s" % inline(a.literal("DFIRM_ID")), ""]
    else:
        answer += ["Flood Hazard Zones (layer 28): no polygon at this point. The layer returned an empty features "
                   "array; the complete raw response below is the proof. This is the layer's answer only, not a "
                   "statement that the point has no flood risk.", ""]
    if panels:
        for i, a in enumerate(panels, 1):
            answer += ["FIRM Panels feature %d of %d (layer 3):" % (i, len(panels)),
                       "- FIRM panel (FIRM_PAN) as shown: %s" % inline(a.literal("FIRM_PAN")),
                       "- Effective date (EFF_DATE): %s" % eff_date(a),
                       "- Panel type (PANEL_TYP) as shown: %s" % inline(a.literal("PANEL_TYP")), ""]
    else:
        answer += ["FIRM Panels (layer 3): no panel at this point. The layer returned an empty features array; the "
                   "complete raw response below is the proof.", ""]
    proof = (evidence("FEMA NFHL, %s layer (layer 28), point query" % ZONES["name"], zones_cap, zones, ZONES)
             + evidence("FEMA NFHL, %s layer (layer 3), point query" % PANELS["name"], panels_cap, panels, PANELS))
    return answer, proof


def run_point(lat, lon, fetcher):
    zones_cap = fetcher(layer_url(ZONES["layer"], lat, lon))
    panels_cap = fetcher(layer_url(PANELS["layer"], lat, lon))
    return flood_sections(lat, lon, zones_cap, panels_cap)


def report(lat=None, lon=None, address=None, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    head = ["# Flood zone check: %s" % (address if address is not None else "%r, %r" % (lat, lon)), "",
            SCREENING, ""]
    answer, proof = [], []
    if address is not None:
        geo = fetcher(geocoder_url(address))
        matches = geocoder_matches(geo)
        geo_proof = evidence("US Census Geocoder, onelineaddress (benchmark %s)" % BENCHMARK, geo, [])
        if len(matches) != 1:
            if matches:
                answer += ["The Census Geocoder returned %d matches for this address, so no flood query was run. "
                           "Give a more specific address. The matches, as shown:" % len(matches), ""]
                answer += ["- %s" % inline(m.literal("matchedAddress")) for m in matches] + [""]
            else:
                answer += ["The Census Geocoder matched no address for %s, so no flood query was run. Its empty "
                           "addressMatches array in the complete raw response below is the proof." % inline(address),
                           ""]
            return head + ["## Answer", ""] + answer + ["## Evidence", ""] + geo_proof
        m = matches[0]
        coords = m.child("coordinates")
        lat, lon = coords.value("y"), coords.value("x")
        answer += ["Matched address (matchedAddress) as shown: %s" % inline(m.literal("matchedAddress")),
                   "Coordinates as shown: x (longitude) %s, y (latitude) %s"
                   % (coords.literal("x"), coords.literal("y")), "",
                   "Census Geocoder excerpt, verbatim:", fenced("%s\n%s" % (m.excerpt("matchedAddress"),
                                                                           m.excerpt("coordinates"))), ""]
        proof += geo_proof
    flood_answer, flood_proof = run_point(lat, lon, fetcher)
    return head + ["## Answer", ""] + answer + flood_answer + ["## Evidence", ""] + proof + flood_proof


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="FEMA NFHL flood zone check for a point or a US address. Screening only.")
    p.add_argument("lat", nargs="?", help="latitude, decimal degrees")
    p.add_argument("lon", nargs="?", help="longitude, decimal degrees")
    p.add_argument("--address", help="a US street address, geocoded by the Census Geocoder")
    args = p.parse_args(argv)
    try:
        if args.address is not None:
            if args.lat is not None or args.lon is not None:
                raise ValueError("give a latitude and longitude, or --address, not both")
            lines = report(address=check_address(args.address), fetcher=fetcher)
        else:
            if args.lat is None or args.lon is None:
                raise ValueError("give a latitude and longitude, or --address")
            lat, lon = check_point(args.lat, args.lon)
            lines = report(lat, lon, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
