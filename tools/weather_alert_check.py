#!/usr/bin/env python3
"""US National Weather Service active alert check (issue #318, tool factory wave 3).

Given a point (latitude and longitude), reads the active weather alerts
the US National Weather Service lists at that point and prints one
Markdown report in the delivery format from AGENT-BRIEF.md: the answer
first (each alert's event name, severity, and expiry, each as shown),
then the evidence: the query's exact URL, UTC retrieval time, the fields
cut verbatim from the response, and the complete raw response.

    python3 tools/weather_alert_check.py 25.7617 -80.1918

Source, keyless: the National Weather Service API's active alerts
endpoint, GET https://api.weather.gov/alerts/active?point={lat},{lon},
which answers a GeoJSON FeatureCollection. The response shape used here
is from the live captures made for this issue on 2026-10-24 (committed
under tools/tests/fixtures/weather-alerts/ with their provenance): the
collection carries "features", "title" and "updated"; each feature
carries a "properties" object with "event", "severity", "expires" and
"ends" (the two time fields are timestamps as shown, or null). The API
asks callers to send an identifying User-Agent; no key exists or is sent.

Outcomes: a collection with features is a report listing each alert. An
empty features array is a report too, of no active alerts at that point
at the retrieval time, with the complete raw response as the proof; it
is never shown as a statement that conditions are safe. A failed
request, any status but 200 (an out of coverage point is answered with
an error status and a problem document; 400 observed live on
2026-10-24 for a London point), a redirect off the source host, or a body
without the documented shape stops the run with exit 2 and no report:
a failed fetch is reported as unknown, never as a negative claim.

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

ALERTS_URL = "https://api.weather.gov/alerts/active"
USER_AGENT = "tiny-ledger-weather-alert-check"
TIMEOUT_SECONDS = 30
HIDDEN_HEADERS = ("set-cookie",)
FIELDS = ("event", "severity", "expires", "ends")

OBSERVATION = ("Observation only: this report records what the US National Weather Service API listed as "
               "active alerts at this point when read at the retrieval time below. No active alerts at "
               "that time is not a statement that conditions are safe or that no alert will be issued.")


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


def alerts_url(lat, lon):
    return "%s?point=%r,%r" % (ALERTS_URL, lat, lon)


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"})
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

def alerts(capture):
    """(collection Node, [properties Node per feature]). Raises FetchError
    when the body is not the documented FeatureCollection shape."""
    node = root(capture)
    try:
        if not node.has("features"):
            raise ValueError("no features array (members: %s)" % (", ".join(sorted(node.spans)) or "none"))
        _, start, _ = node.spans["features"]
        if node.raw[start] != "[":
            raise ValueError("features is not an array")
        out = []
        for s, _ in elements(node.raw, start):
            props = Node(node.raw, s).child("properties")
            missing = [f for f in FIELDS if not props.has(f)]
            if missing:
                raise ValueError("a feature's properties have no %s" % ", ".join(missing))
            for f in ("event", "severity"):
                if not isinstance(props.value(f), str):
                    raise ValueError("a feature's %s is not a string" % f)
            for f in ("expires", "ends"):
                if props.value(f) is not None and not isinstance(props.value(f), str):
                    raise ValueError("a feature's %s is neither a string nor null" % f)
            out.append(props)
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented alerts shape (%s); no report"
                         % (capture.url, err))
    return node, out


def expiry(props):
    """The expiry line for one alert: expires as shown, and when the
    service shows null there, the alert's ends as shown instead."""
    if props.value("expires") is not None:
        return "- Expires (expires) as shown: %s" % inline(props.literal("expires"))
    return ("- Expires (expires) as shown: null; the alert's end (ends) as shown: %s"
            % inline(props.literal("ends")))


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def report(lat, lon, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    capture = fetcher(alerts_url(lat, lon))
    collection, props_list = alerts(capture)
    lines = ["# Weather alert check: %r, %r" % (lat, lon), "", OBSERVATION, "",
             "## Answer", "", "Point: latitude %r, longitude %r" % (lat, lon), ""]
    for f in ("title", "updated"):
        if collection.has(f):
            lines += ["Collection %s as shown: %s" % (f, inline(collection.literal(f)))]
    if lines[-1] != "":
        lines += [""]
    if props_list:
        lines += ["%d active alert(s) at this point:" % len(props_list), ""]
        for i, props in enumerate(props_list, 1):
            lines += ["Alert %d of %d:" % (i, len(props_list)),
                      "- Event (event) as shown: %s" % inline(props.literal("event")),
                      "- Severity (severity) as shown: %s" % inline(props.literal("severity")),
                      expiry(props), ""]
    else:
        lines += ["No active alerts at this point. The service returned an empty features array; the "
                  "complete raw response below is the proof. This is the service's answer at the "
                  "retrieval time only.", ""]
    lines += ["## Evidence", "", "### National Weather Service, active alerts for the point", "",
              "Exact query URL: <%s>" % capture.url, "",
              "UTC retrieval time: %s" % capture.retrieved, ""]
    if props_list:
        lines += ["Fields, verbatim from the response:",
                  fenced("\n\n".join("\n".join(p.excerpt(f) for f in FIELDS) for p in props_list)), ""]
    lines += ["Complete raw response:", fenced(capture.transcript()), ""]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="US National Weather Service active alerts for a point.")
    p.add_argument("lat", nargs="?", help="latitude, decimal degrees")
    p.add_argument("lon", nargs="?", help="longitude, decimal degrees")
    args = p.parse_args(argv)
    try:
        if args.lat is None or args.lon is None:
            raise ValueError("give a latitude and longitude")
        lat, lon = check_point(args.lat, args.lon)
        lines = report(lat, lon, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
