#!/usr/bin/env python3
"""USGS earthquake catalog check (issue #317, tool factory wave 3, tool 2).

Given a point (latitude and longitude) and a radius in kilometres, asks the
USGS earthquake catalog (FDSN event web service) how many earthquakes it
lists inside that circle in the past 10 years, and which are the largest,
and prints one Markdown report in the delivery format from AGENT-BRIEF.md:
the answer first, then the evidence: each query's exact URL, UTC retrieval
time, the fields cut verbatim from the response, and the complete raw
response.

    python3 tools/earthquake_check.py 34.0522 -118.2437 25

Source, keyless: the USGS FDSN event web service,
https://earthquake.usgs.gov/fdsnws/event/1/, two calls with the same
point, radius and window:
- count?format=geojson&... answers {"count":N,"maxAllowed":20000}; N is
  the total the report states.
- query?format=geojson&...&orderby=magnitude&limit=10 answers a GeoJSON
  FeatureCollection whose features array holds the largest events. For
  each, properties.mag, properties.magType, properties.time (epoch
  milliseconds, printed raw first with the UTC time after it),
  properties.place, properties.type and the feature id are cut verbatim.
The shapes are the coordinator's captures on issue #317 (comments
6384169097 to 6384170740), held as fixtures in
tools/tests/fixtures/earthquake/. No eventtype or minmagnitude filter is
sent, so the count covers every event the catalog lists in the circle;
each listed event's type is shown as returned.

The window is the 10 years up to the moment of the call, computed once and
sent identically on both requests, and printed in the report.

Outcomes: a count of 0 with an empty features array is a report of no
event listed, with both raw responses as the proof; it is never shown as
"no earthquake risk". A failed request, any status but 200 (the source
answers bad input with HTTP 400 and a plain text body), a redirect off
the source host, a body without the documented shape, or two answers that
disagree (a count of 0 with events listed, or the reverse) stops the run
with exit 2 and no report: the answer is unknown.

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

BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/"
COUNT_URL = BASE_URL + "count"
QUERY_URL = BASE_URL + "query"
USER_AGENT = "tiny-ledger-earthquake-check"
TIMEOUT_SECONDS = 30
YEARS = 10
MIN_RADIUS_KM = 1
MAX_RADIUS_KM = 500
LARGEST = 10
HIDDEN_HEADERS = ("set-cookie",)


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
# Inputs, window and URLs
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


def check_radius(radius_km):
    """The radius in kilometres as a float, or ValueError."""
    try:
        r = float(radius_km)
    except (TypeError, ValueError):
        raise ValueError("radius_km must be a number (got %r)" % (radius_km,))
    if not MIN_RADIUS_KM <= r <= MAX_RADIUS_KM:
        raise ValueError("radius_km must be %d to %d (got %r)" % (MIN_RADIUS_KM, MAX_RADIUS_KM, radius_km))
    return r


def window(now):
    """(starttime, endtime) strings for the YEARS years up to `now` (an aware UTC datetime)."""
    try:
        start = now.replace(year=now.year - YEARS)
    except ValueError:  # 29 February, with no such day YEARS years earlier
        start = now.replace(year=now.year - YEARS, day=28)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return start.strftime(fmt), now.strftime(fmt)


def number(x):
    """A float as sent: 25.0 as 25, 34.0522 as 34.0522."""
    return "%d" % x if x == int(x) else repr(x)


def params(lat, lon, radius_km, start, end):
    return [("format", "geojson"), ("latitude", number(lat)), ("longitude", number(lon)),
            ("maxradiuskm", number(radius_km)), ("starttime", start), ("endtime", end)]


def count_url(lat, lon, radius_km, start, end):
    return "%s?%s" % (COUNT_URL, urllib.parse.urlencode(params(lat, lon, radius_km, start, end), safe=":"))


def query_url(lat, lon, radius_km, start, end):
    extra = [("orderby", "magnitude"), ("limit", str(LARGEST))]
    return "%s?%s" % (QUERY_URL, urllib.parse.urlencode(params(lat, lon, radius_km, start, end) + extra,
                                                         safe=":"))


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def utc_now_iso():
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def reason(err):
    """The source's own reason line from an error body, when it gives one."""
    try:
        text = err.read(2000).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 (the reason is only a courtesy)
        return ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if not ln.startswith("Error ")]
    return " (%s)" % lines[0] if lines else ""


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        raise FetchError("%s answered HTTP %s%s; no report, the answer is unknown" % (url, err.code, reason(err)))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report, the answer is unknown" % (url, err))
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

EVENT_FIELDS = ("mag", "magType", "time", "place", "type")


def read_count(capture):
    """(node, count). Raises FetchError unless the body holds a whole number count."""
    node = root(capture)
    try:
        value = node.value("count") if node.has("count") else None
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError("no whole number count (members: %s)" % (", ".join(sorted(node.spans)) or "none"))
    except ValueError as err:
        raise FetchError("%s answered a body that is not the documented count shape (%s); no report"
                         % (capture.url, err))
    return node, value


def read_events(capture):
    """[(feature, properties)] in the order returned. Raises FetchError when the
    body is not the documented FeatureCollection shape."""
    node = root(capture)
    try:
        if not node.has("type") or node.value("type") != "FeatureCollection":
            raise ValueError("not a FeatureCollection")
        if not node.has("features"):
            raise ValueError("no features array")
        _, start, _ = node.spans["features"]
        if node.raw[start] != "[":
            raise ValueError("features is not an array")
        out = []
        for s, _ in elements(node.raw, start):
            feature = Node(node.raw, s)
            props = feature.child("properties")
            missing = [f for f in EVENT_FIELDS if not props.has(f)] + ([] if feature.has("id") else ["id"])
            if missing:
                raise ValueError("an event has no %s" % ", ".join(missing))
            out.append((feature, props))
        if len(out) > LARGEST:
            raise ValueError("%d events listed, more than the limit of %d sent" % (len(out), LARGEST))
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented GeoJSON query shape (%s); no report"
                         % (capture.url, err))
    return out


def event_time(props):
    value = props.value("time")
    if isinstance(value, int) and not isinstance(value, bool):
        moment = datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return "%s (%s UTC, converted from epoch milliseconds)" % (props.literal("time"), moment)
    return "%s (not epoch milliseconds; shown as returned)" % props.literal("time")


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

SCOPE = ("This report records what the public USGS earthquake catalog returned for the circle and window "
         "stated below, at the retrieval times stated. It is not a seismic hazard assessment.")


def evidence(title, capture):
    return ["### %s" % title, "", "Exact query URL: <%s>" % capture.url, "",
            "UTC retrieval time: %s" % capture.retrieved, "",
            "Complete raw response:", fenced(capture.transcript()), ""]


def report(lat, lon, radius_km, fetcher=None, now=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    start, end = window(now or utc_now())
    count_cap = fetcher(count_url(lat, lon, radius_km, start, end))
    count_node, count = read_count(count_cap)
    query_cap = fetcher(query_url(lat, lon, radius_km, start, end))
    events = read_events(query_cap)
    if (count == 0) != (not events):
        raise FetchError("the two answers disagree: the count call answered %d and the query call listed %d "
                         "event(s); no report, the answer is unknown" % (count, len(events)))
    head = ["# Earthquake check: %s, %s, radius %s km" % (number(lat), number(lon), number(radius_km)), "",
            SCOPE, "", "## Answer", "",
            "Point: latitude %s, longitude %s. Radius: %s km. Window: %s to %s UTC (the %d years up to the call)."
            % (number(lat), number(lon), number(radius_km), start, end, YEARS), ""]
    if count == 0:
        answer = ["The USGS earthquake catalog lists no event inside this circle in this window. The count call "
                  "answered 0 and the query call an empty features array; both complete raw responses below are "
                  "the proof. This is the catalog's answer for this circle and window only, not a statement "
                  "that no earthquake can occur here.", "",
                  "Count, as returned:", "Source: <%s>" % count_cap.url, "", fenced(count_node.excerpt("count")),
                  ""]
    else:
        answer = ["Events the USGS earthquake catalog lists inside this circle in this window: %d (every event "
                  "type; no type or magnitude filter was sent)." % count, "",
                  "Count, as returned:", "Source: <%s>" % count_cap.url, "", fenced(count_node.excerpt("count")),
                  "",
                  "The %d largest by magnitude, in the order the source returned them (orderby=magnitude, "
                  "limit=%d):" % (len(events), LARGEST), ""]
        for i, (feature, props) in enumerate(events, 1):
            answer += ["%d. Magnitude %s (magType %s), %s" % (i, props.literal("mag"), inline(props.literal("magType")),
                                                            inline(props.literal("place"))),
                       "   - Time: %s" % event_time(props),
                       "   - Event type as shown: %s; event id: %s" % (inline(props.literal("type")),
                                                                      inline(feature.literal("id"))),
                       "   - Source: <%s>" % query_cap.url, "",
                       fenced("\n".join([props.excerpt(f) for f in EVENT_FIELDS] + [feature.excerpt("id")])), ""]
    proof = (evidence("USGS earthquake catalog, count call", count_cap)
             + evidence("USGS earthquake catalog, query call (largest by magnitude)", query_cap))
    return head + answer + ["## Evidence", ""] + proof


def main(argv=None, fetcher=None, stdout=None, stderr=None, now=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="USGS earthquake catalog check: events in the past %d years inside "
                                            "a circle around a point." % YEARS)
    p.add_argument("lat", help="latitude, decimal degrees")
    p.add_argument("lon", help="longitude, decimal degrees")
    p.add_argument("radius_km", help="radius in kilometres, %d to %d" % (MIN_RADIUS_KM, MAX_RADIUS_KM))
    args = p.parse_args(argv)
    try:
        lat, lon = check_point(args.lat, args.lon)
        radius = check_radius(args.radius_km)
        lines = report(lat, lon, radius, fetcher=fetcher, now=now)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
