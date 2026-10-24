"""Tests for tools/address_geocode_check.py and its GET /geocode route (issue #319). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_address_geocode_check.py' -v

Fixtures (fixtures/census-geocoder/, recorded in provenance.json): REAL
CAPTURES taken by H6 with the tool's own fetch() for issue #319, a match
(the White House) and a no match, verbatim. Variants built here say
DERIVED where they are built. Every test runs with urlopen replaced by a
function that fails the test, except the fetch tests, which replace it
with a fake.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import address_geocode_check as g  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "census-geocoder"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
WHITE_HOUSE = "1600 Pennsylvania Ave NW, Washington, DC 20500"
NO_SUCH = "99999 Zqxflorp Boulevard, Nowhere, ZZ 00000"


def body(name):
    return (FIX / name).read_text(encoding="utf-8")


def replay(module=g, bodies=None):
    """A fetcher answering each expected URL from a fixture. Any other URL fails the test."""
    table = {
        module.geocoder_url(WHITE_HOUSE): "white-house.body",
        module.geocoder_url(NO_SUCH): "no-match.body",
    }
    raw = dict(bodies or {})  # url: body text, built in the test
    seen = []

    def fetcher(url):
        if url not in table and url not in raw:
            raise AssertionError("unexpected url %s" % url)
        seen.append(url)
        text = raw[url] if url in raw else body(table[url])
        return module.Capture(url, "2026-10-24T12:20:00Z", "HTTP/1.1 200 OK",
                              [("Content-Type", "application/json")], text)
    fetcher.seen = seen
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("address_geocode_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = g.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name, entry in PROV.items():
            self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), entry["sha256"], name)
            self.assertTrue(entry["contents"].startswith(entry["kind"]), name)


class UrlTests(unittest.TestCase):
    def test_url_is_the_captured_one_with_benchmark_and_vintage_pinned(self):
        self.assertEqual(g.geocoder_url(WHITE_HOUSE), PROV["white-house.body"]["url"])
        self.assertEqual(g.geocoder_url(NO_SUCH), PROV["no-match.body"]["url"])
        self.assertIn("benchmark=Public_AR_Current", g.geocoder_url(WHITE_HOUSE))
        self.assertIn("vintage=Current_Current", g.geocoder_url(WHITE_HOUSE))


class ReportTests(unittest.TestCase):
    def test_a_match_reports_address_coordinates_and_county(self):
        fetcher = replay()
        code, out, err = run([WHITE_HOUSE], fetcher)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(fetcher.seen, [g.geocoder_url(WHITE_HOUSE)])
        self.assertLess(out.index("## Answer"), out.index("## Evidence"))
        self.assertIn('- Matched address (matchedAddress) as shown: `"1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20500"`',
                      out)
        self.assertIn("- Coordinates as shown: x (longitude) -77.035189204737, y (latitude) 38.898702605245", out)
        self.assertIn('- County (Counties geography) as shown: `"District of Columbia"` (GEOID `"11001"`)', out)
        self.assertIn('- Census tract (Census Tracts geography) GEOID as shown: `"11001980000"`', out)
        self.assertIn("- Address components as shown: city WASHINGTON, state DC, ZIP 20500", out)
        self.assertIn("interpolated along the matched address range", out)
        self.assertIn("Exact query URL: <%s>" % g.geocoder_url(WHITE_HOUSE), out)
        self.assertIn("Retrieved (UTC): 2026-10-24T12:20:00Z", out)
        self.assertIn(body("white-house.body"), out)

    def test_no_match_is_a_report_proven_by_the_raw_body(self):
        fetcher = replay()
        code, out, _ = run([NO_SUCH], fetcher)
        self.assertEqual(code, 0)
        self.assertEqual(fetcher.seen, [g.geocoder_url(NO_SUCH)])
        self.assertIn("The Census Geocoder matched no address for `%s`." % NO_SUCH, out)
        self.assertIn("not a statement that no such address exists", out)
        self.assertIn(body("no-match.body"), out)
        self.assertNotIn("Matched address", out)

    def test_several_matches_are_each_listed(self):
        # DERIVED: the captured match twice in one addressMatches array.
        data = json.loads(body("white-house.body"))
        data["result"]["addressMatches"] = data["result"]["addressMatches"] * 2
        two = json.dumps(data, separators=(",", ":"))
        _, out, _ = run([WHITE_HOUSE], replay(bodies={g.geocoder_url(WHITE_HOUSE): two}))
        self.assertIn("Match 1 of 2:", out)
        self.assertIn("Match 2 of 2:", out)
        self.assertEqual(out.count("Matched address (matchedAddress) as shown"), 2)


class FailClosedTests(unittest.TestCase):
    def test_bodies_without_the_documented_shape_exit_2_with_no_report(self):
        data = json.loads(body("white-house.body"))
        no_coords = json.loads(body("white-house.body"))
        del no_coords["result"]["addressMatches"][0]["coordinates"]
        no_county = json.loads(body("white-house.body"))
        no_county["result"]["addressMatches"][0]["geographies"]["Counties"] = []
        far_away = json.loads(body("white-house.body"))
        far_away["result"]["addressMatches"][0]["coordinates"] = {"x": -777.0, "y": 38.8}
        bad = ['{"SYNTHETIC": "no result member"}', '{"result": {}}', "<html>SYNTHETIC</html>", "",
               json.dumps(no_coords), json.dumps(no_county), json.dumps(far_away)]
        for text in bad:
            code, out, err = run([WHITE_HOUSE], replay(bodies={g.geocoder_url(WHITE_HOUSE): text}))
            self.assertEqual((code, out), (2, ""), text[:60])
            self.assertIn("no report", err)

    def test_a_failed_fetch_is_unknown_never_a_no_match(self):
        def broken(url):
            raise g.FetchError("request to %s failed: SYNTHETIC connection closed; no report" % url)
        code, out, err = run([WHITE_HOUSE], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection closed", err)
        self.assertNotIn("matched no address", err)

    def test_bad_inputs_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for argv in ([], [" "], ["a" * 201]):
            self.assertEqual(run(argv, must_not)[0], 2, argv)


class FetchTests(unittest.TestCase):
    class Answer:  # SYNTHETIC response object
        def __init__(self, status, data, url, headers=()):
            self.status, self.reason, self.version = status, "X", 11
            self._data, self._url, self.headers = data, url, dict(headers)

        def read(self):
            return self._data

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def test_200_is_captured_with_its_headers_and_set_cookie_is_not_printed(self):
        url = g.geocoder_url(WHITE_HOUSE)
        answer = self.Answer(200, b'{"result": {"addressMatches": []}}', url,
                             [("Content-Type", "application/json"), ("Set-Cookie", "SYNTHETIC=1")])
        with mock.patch("urllib.request.urlopen", lambda request, timeout=None: answer):
            cap = g.fetch(url)
        self.assertEqual(cap.status_line, "HTTP/1.1 200 X")
        self.assertIn("Content-Type: application/json", cap.transcript())
        self.assertNotIn("SYNTHETIC=1", cap.transcript())
        self.assertIn("(a Set-Cookie header was returned and is not printed)", cap.transcript())

    def test_errors_non_200_and_redirects_off_host_fail_closed(self):
        url = g.geocoder_url(WHITE_HOUSE)

        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "X", {}, io.BytesIO(b""))

        def closed(request, timeout=None):
            raise urllib.error.URLError("SYNTHETIC remote end closed connection without response")
        fakes = [http_error, closed,
                 lambda request, timeout=None: self.Answer(206, b"{}", url),
                 lambda request, timeout=None: self.Answer(200, b"{}", "https://example.invalid/x")]
        for fake in fakes:
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(g.FetchError):
                    g.fetch(url)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.address_geocode_check, its own module object.
        with mock.patch.object(endpoints.ag, "fetch", replay(endpoints.ag)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/geocode", qs, None)

    def test_route(self):
        qs = urllib.parse.urlencode({"address": WHITE_HOUSE})
        status, _, text = self.get(qs)
        self.assertEqual(status, "200 OK")
        text = text.decode() if isinstance(text, bytes) else text
        self.assertTrue(text.startswith("# Address geocode check: %s" % WHITE_HOUSE))
        self.assertIn('- County (Counties geography) as shown: `"District of Columbia"` (GEOID `"11001"`)', text)
        self.assertEqual(self.get(urllib.parse.urlencode({"address": NO_SUCH}))[0], "200 OK")
        for bad in ("", "address=", "address=a&address=b", "address=" + "a" * 201):
            self.assertEqual(self.get(bad)[0], "400 Bad Request", bad)
        self.assertEqual(endpoints.describe()["/geocode"]["sources"][0], g.API_URL)

    def test_route_maps_a_failure_to_502(self):
        def refused(url):
            raise endpoints.ag.FetchError("SYNTHETIC connection closed; no report")
        with mock.patch.object(endpoints.ag, "fetch", refused):
            qs = urllib.parse.urlencode({"address": WHITE_HOUSE})
            self.assertEqual(recall_api.handle("GET", "/geocode", qs, None)[0], "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
