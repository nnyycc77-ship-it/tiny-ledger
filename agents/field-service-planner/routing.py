#!/usr/bin/env python3
"""Geocoding and drive times behind one interface (issue #73, item 2).

The planner never places an address itself and never estimates a drive
time itself. It asks a Provider:

    provider.geocode(address) -> Place or None
    provider.matrix(places)   -> list of lists of drive seconds

Two providers live here:

  FixtureProvider   reads a JSON file of places and a travel rule. Used by
                    the tests and by offline dry runs. Makes no network
                    request. The repo's fixture file is synthetic and says
                    so in its own "label" field.
  LiveProvider      open routing services: Nominatim for geocoding and the
                    public OSRM demo server for the drive time matrix, over
                    HTTPS only, hosts pinned, redirects refused, one request
                    per second to Nominatim as its usage policy asks, with
                    the operator's contact in the User-Agent (required by
                    that policy; read from the environment variable
                    FIELD_PLANNER_CONTACT, never from a file here). A keyed
                    provider replaces this class without touching the
                    planner: implement the two methods.

Fail closed: a transport failure, a non 2xx status, a body that is not
JSON, or a response shape this module does not recognise raises
RoutingError and the run stops. An address the geocoder does not place is
returned as None, which the planner reports as a data problem; it is never
guessed, never filled from a neighbour, never defaulted.

The request and response shapes used by LiveProvider are written from the
public documentation of those two services as known when this was written
and are marked "to confirm against the current docs before a live run" in
README.md: this folder was built in an environment that cannot reach either
host, so no live call has been made from here. Standard library only.
"""

import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request

CONTACT_ENV = "FIELD_PLANNER_CONTACT"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_TABLE_URL = "https://router.project-osrm.org/table/v1/driving/"
ALLOWED_HOSTS = ("nominatim.openstreetmap.org", "router.project-osrm.org")
TIMEOUT_SECONDS = 60
NOMINATIM_MIN_INTERVAL = 1.0  # seconds between requests, per the usage policy
CONFIDENCE_LEVELS = ("high", "medium", "low")


class RoutingError(Exception):
    """A provider call failed or answered something not understood. Nothing is concluded."""


class ConfigError(Exception):
    """The provider cannot be built from the environment. Nothing was sent."""


class Place(object):
    """A placed address."""

    def __init__(self, lat, lon, confidence, source):
        self.lat = float(lat)
        self.lon = float(lon)
        if confidence not in CONFIDENCE_LEVELS:
            raise RoutingError("confidence must be one of %s, got %r" % (", ".join(CONFIDENCE_LEVELS), confidence))
        self.confidence = confidence
        self.source = source

    def key(self):
        return (self.lat, self.lon)

    def __repr__(self):
        return "Place(%r, %r, %r, %r)" % (self.lat, self.lon, self.confidence, self.source)


def haversine_km(a, b):
    """Great circle distance in kilometres between two Places."""
    r = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


# ------------------------------------------------------------ fixture provider

class FixtureProvider(object):
    """Places and drive times from a JSON file; no network.

    File shape:
        {
          "label": "...",                          free text; the repo file says synthetic
          "places": {"<address>": {"lat": .., "lon": .., "confidence": "high"} | null, ...},
          "travel": {"method": "haversine", "speed_kmh": 40.0,
                     "overrides": {"<address A>|<address B>": <seconds>, ...}}
        }
    An address missing from "places" or mapped to null is not placed (None).
    Drive seconds are great circle distance at the stated speed, except for
    pairs listed in overrides (directional, A to B).
    """

    name = "fixture"

    def __init__(self, path):
        self.path = path
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            raise RoutingError("cannot read places file %s: %s" % (path, exc))
        if not isinstance(data, dict) or not isinstance(data.get("places"), dict):
            raise RoutingError("places file %s needs an object with a \"places\" object" % path)
        self.label = str(data.get("label", ""))
        self.places = {}
        self.by_key = {}
        for address, entry in data["places"].items():
            if entry is None:
                self.places[address] = None
                continue
            try:
                place = Place(entry["lat"], entry["lon"], entry.get("confidence", "high"), "fixture:" + os.path.basename(path))
            except (KeyError, TypeError, ValueError) as exc:
                raise RoutingError("places file %s: bad entry for %r: %s" % (path, address, exc))
            self.places[address] = place
            self.by_key[place.key()] = address
        travel = data.get("travel") or {}
        if travel.get("method", "haversine") != "haversine":
            raise RoutingError("places file %s: travel method %r is not supported" % (path, travel.get("method")))
        try:
            self.speed_kmh = float(travel.get("speed_kmh", 40.0))
        except (TypeError, ValueError):
            raise RoutingError("places file %s: speed_kmh must be a number" % path)
        if self.speed_kmh <= 0:
            raise RoutingError("places file %s: speed_kmh must be positive" % path)
        self.overrides = {}
        for pair, seconds in (travel.get("overrides") or {}).items():
            if "|" not in pair:
                raise RoutingError("places file %s: override key %r needs the form A|B" % (path, pair))
            self.overrides[tuple(pair.split("|", 1))] = float(seconds)
        self.describe = ("fixture places file %s (%s); drive times are great circle distance at %.0f km/h"
                         % (os.path.basename(path), self.label or "no label", self.speed_kmh))

    def geocode(self, address):
        return self.places.get(address)

    def matrix(self, places):
        out = []
        for a in places:
            row = []
            for b in places:
                pair = (self.by_key.get(a.key()), self.by_key.get(b.key()))
                if pair in self.overrides:
                    row.append(self.overrides[pair])
                elif a.key() == b.key():
                    row.append(0.0)
                else:
                    row.append(round(haversine_km(a, b) / self.speed_kmh * 3600.0))
            out.append(row)
        return out


# --------------------------------------------------------------- live provider

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RoutingError("redirect to %s refused" % newurl)


class UrllibTransport(object):
    """GET a pinned HTTPS URL; return (status, body bytes)."""

    def __init__(self):
        self.opener = urllib.request.build_opener(_NoRedirect())

    def get(self, url, headers):
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
            raise RoutingError("refusing to contact %s://%s; only HTTPS to %s" % (parts.scheme, parts.hostname, ", ".join(ALLOWED_HOSTS)))
        req = urllib.request.Request(url, headers=dict(headers), method="GET")
        try:
            with self.opener.open(req, timeout=TIMEOUT_SECONDS) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except (urllib.error.URLError, OSError) as exc:
            raise RoutingError("transport failure for %s: %s" % (url, exc))


class LiveProvider(object):
    """Nominatim geocoding plus OSRM table drive times. See the module docstring."""

    name = "live"

    def __init__(self, contact, transport=None, sleep=time.sleep, clock=time.monotonic):
        contact = (contact or "").strip()
        if not contact:
            raise ConfigError("%s is not set; the live provider needs the operator's contact for the User-Agent "
                              "(Nominatim usage policy) and refuses to run without it" % CONTACT_ENV)
        self.user_agent = "tiny-ledger field-service-planner (%s)" % contact
        self.transport = transport or UrllibTransport()
        self.sleep = sleep
        self.clock = clock
        self.last_nominatim = None
        self.describe = ("live: Nominatim (%s) for geocoding, OSRM table service (%s) for drive times"
                         % (NOMINATIM_URL, OSRM_TABLE_URL))

    @classmethod
    def from_env(cls, env=None, transport=None):
        env = os.environ if env is None else env
        return cls(env.get(CONTACT_ENV, ""), transport=transport)

    def _headers(self):
        return [("Accept", "application/json"), ("User-Agent", self.user_agent)]

    def _json(self, url):
        status, body = self.transport.get(url, self._headers())
        if not 200 <= status < 300:
            raise RoutingError("%s answered HTTP %s; no result is concluded" % (url, status))
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise RoutingError("%s answered a body that is not JSON: %s" % (url, exc))

    def geocode_url(self, address):
        return NOMINATIM_URL + "?" + urllib.parse.urlencode([("q", address), ("format", "jsonv2"), ("limit", "1")])

    def geocode(self, address):
        if self.last_nominatim is not None:
            wait = NOMINATIM_MIN_INTERVAL - (self.clock() - self.last_nominatim)
            if wait > 0:
                self.sleep(wait)
        self.last_nominatim = self.clock()
        url = self.geocode_url(address)
        data = self._json(url)
        if not isinstance(data, list):
            raise RoutingError("%s: expected a JSON array of results, got %s" % (url, type(data).__name__))
        if not data:
            return None  # not placed; the planner reports it, nothing is guessed
        first = data[0]
        try:
            return Place(float(first["lat"]), float(first["lon"]), "medium", "nominatim:" + url)
        except (KeyError, TypeError, ValueError) as exc:
            raise RoutingError("%s: first result lacks numeric lat/lon: %s" % (url, exc))

    def matrix_url(self, places):
        coords = ";".join("%.6f,%.6f" % (p.lon, p.lat) for p in places)
        return OSRM_TABLE_URL + coords + "?annotations=duration"

    def matrix(self, places):
        if not places:
            return []
        url = self.matrix_url(places)
        data = self._json(url)
        if not isinstance(data, dict) or data.get("code") != "Ok" or not isinstance(data.get("durations"), list):
            raise RoutingError("%s: expected {\"code\": \"Ok\", \"durations\": [[...]]}, got %s"
                               % (url, json.dumps(data)[:200] if isinstance(data, (dict, list)) else type(data).__name__))
        rows = data["durations"]
        if len(rows) != len(places) or any(not isinstance(r, list) or len(r) != len(places) for r in rows):
            raise RoutingError("%s: durations is not a %d by %d table" % (url, len(places), len(places)))
        out = []
        for r in rows:
            row = []
            for v in r:
                if v is None:
                    raise RoutingError("%s: a pair has no route (null duration); refusing to guess a drive time" % url)
                row.append(float(v))
            out.append(row)
        return out
