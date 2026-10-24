"""Tests for tools/flood_check.py and its GET /flood route (issue #175). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_flood_check.py' -v

Fixtures (fixtures/flood/, recorded in provenance.json):
- geocoder-*.body: REAL CAPTURES, the coordinator's Census Geocoder bodies
  on issue #175 (comment 6379402122), verbatim; their SHA-256 match the ones
  posted.
- derived-*.body: DERIVED, interim. The NFHL attributes lines are verbatim
  from the excerpts in the committed Tampa flood delivery; the wrapper is
  SYNTHETIC. synthetic-empty.body is SYNTHETIC. All are to be replaced by
  the coordinator's complete raw NFHL captures, which are owed on #175.
Variants built here say DERIVED or SYNTHETIC where they are built. Every
test runs with urlopen replaced by a function that fails the test, except
the fetch tests, which replace it with a fake.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import flood_check as f  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "flood"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
DELIVERY = ROOT / "deliveries" / "flood-screen-d4f252e4-8a3b-40dd-981e-befb2de63da0.md"
TAMPA2 = (27.9235, -82.4515)  # AE, SFHA_TF T in the delivery
TAMPA1 = (27.9506, -82.4572)  # X, SFHA_TF F, STATIC_BFE -9999.0
WHITE_HOUSE = "1600 Pennsylvania Ave NW, Washington, DC"
NO_SUCH = "99999 Zqxflorp Nonexistent Street, Nowhere, ZZ"


def body(name):
    return (FIX / name).read_text(encoding="utf-8")


def replay(module=f, bodies=None):
    """A fetcher answering each expected URL from a fixture. Any other URL fails the test."""
    table = {
        module.layer_url(28, *TAMPA2): "derived-tampa2-layer28.body",
        module.layer_url(3, *TAMPA2): "derived-tampa2-layer3.body",
        module.layer_url(28, *TAMPA1): "derived-tampa1-layer28.body",
        module.layer_url(3, *TAMPA1): "derived-tampa1-layer3.body",
        module.layer_url(28, 30.0, -70.0): "synthetic-empty.body",
        module.layer_url(3, 30.0, -70.0): "synthetic-empty.body",
        module.layer_url(28, 38.898702605245, -77.035189204737): "synthetic-empty.body",
        module.layer_url(3, 38.898702605245, -77.035189204737): "synthetic-empty.body",
        module.geocoder_url(WHITE_HOUSE): "geocoder-matched.body",
        module.geocoder_url(NO_SUCH): "geocoder-no-match.body",
    }
    raw = dict(bodies or {})  # url: body text, built in the test
    seen = []

    def fetcher(url):
        if url not in table and url not in raw:
            raise AssertionError("unexpected url %s" % url)
        seen.append(url)
        text = raw[url] if url in raw else body(table[url])
        return module.Capture(url, "2026-10-24T04:00:00Z", "HTTP/1.1 200 OK",
                              [("Content-Type", "application/json")], text)
    fetcher.seen = seen
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("flood_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = f.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_and_the_geocoder_bodies_are_the_posted_ones(self):
        # Body sha256 values exactly as the coordinator posted them on issue #175 (comment 6379402122).
        posted_sha256 = {
            "geocoder-matched body sha256": "a67be26972c35c8a327de6efae1ab4961fa386db5d75b82685d6b77e4a09a05a",
            "geocoder-no-match body sha256": "6a7b12d09e844074aa252189696de7a2de1c3024dcbf6e763d108abe63ea199f",
        }
        for key, sha in posted_sha256.items():
            self.assertEqual(PROV[key.replace(" body sha256", ".body")]["sha256"], sha)
        for name, entry in PROV.items():
            self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), entry["sha256"], name)
            self.assertTrue(entry["contents"].startswith(entry["kind"]), name)

    def test_derived_attribute_lines_are_verbatim_from_the_delivery(self):
        delivery = DELIVERY.read_text(encoding="utf-8")
        delivery_lines = set(delivery.split("\n"))
        for name, entry in PROV.items():
            if entry["kind"] != "DERIVED":
                continue
            self.assertIn("Exact query URL: %s" % entry["url"], delivery)
            attrs = body(name).split("\n")[3:-4]
            self.assertEqual(attrs[0], '      "attributes": {')
            for line in attrs[:-1]:
                self.assertIn(line, delivery_lines, name)
            self.assertIn(attrs[-1] + ",", delivery_lines, name)  # the one comma dropped, as provenance says


class UrlTests(unittest.TestCase):
    def test_urls_are_the_grounded_ones_byte_for_byte(self):
        delivery = DELIVERY.read_text(encoding="utf-8")
        self.assertIn(f.layer_url(28, *TAMPA2), delivery)
        self.assertIn(f.layer_url(3, 27.9325, -82.4850), delivery)  # -82.485 as the delivery writes it
        self.assertEqual(f.geocoder_url(WHITE_HOUSE), PROV["geocoder-matched.body"]["url"])
        self.assertEqual(f.geocoder_url(NO_SUCH), PROV["geocoder-no-match.body"]["url"])


class PointTests(unittest.TestCase):
    def test_hit_in_a_special_flood_hazard_area(self):
        code, out, err = run([str(TAMPA2[0]), str(TAMPA2[1])])
        self.assertEqual((code, err), (0, ""))
        self.assertLess(out.index("## Answer"), out.index("## Evidence"))
        self.assertIn('- Flood zone (FLD_ZONE) as shown: `"AE"`', out)
        self.assertIn('- Zone subtype (ZONE_SUBTY) as shown: `"COASTAL FLOODPLAIN"`', out)
        self.assertIn('- SFHA: true (SFHA_TF as shown: `"T"`)', out)
        self.assertIn("- Static BFE (STATIC_BFE): 11.0", out)
        self.assertIn('- FIRM panel (FIRM_PAN) as shown: `"12057C0362J"`', out)
        self.assertIn("- Effective date (EFF_DATE): 1633564800000 (2021-10-07 UTC, converted from epoch milliseconds)",
                      out)
        self.assertIn('"FLD_ZONE": "AE"\n"ZONE_SUBTY": "COASTAL FLOODPLAIN"\n"SFHA_TF": "T"', out)
        self.assertIn(body("derived-tampa2-layer28.body"), out)
        self.assertIn(body("derived-tampa2-layer3.body"), out)
        self.assertIn("Exact query URL: <%s>" % f.layer_url(28, *TAMPA2), out)
        self.assertIn("Screening only: not a Standard Flood Hazard Determination", out)

    def test_minimal_hazard_shows_false_and_no_bfe(self):
        _, out, _ = run([str(TAMPA1[0]), str(TAMPA1[1])])
        self.assertIn('- Flood zone (FLD_ZONE) as shown: `"X"`', out)
        self.assertIn('- SFHA: false (SFHA_TF as shown: `"F"`)', out)
        self.assertIn("- Static BFE (STATIC_BFE): none (the service returns -9999.0)", out)

    def test_empty_result_is_proven_by_the_raw_body_never_a_clean_bill(self):
        code, out, _ = run(["30", "-70"])
        self.assertEqual(code, 0)
        self.assertIn("Flood Hazard Zones (layer 28): no polygon at this point. The layer returned an empty features "
                      "array", out)
        self.assertIn("not a statement that the point has no flood risk", out)
        self.assertIn("FIRM Panels (layer 3): no panel at this point.", out)
        self.assertEqual(out.count('\n{"features":[]}\n'), 2)
        self.assertNotIn("SFHA: false", out)

    def test_several_features_are_all_listed(self):
        # DERIVED: the Tampa point 2 panel attributes twice, as the delivery's point 5 had two panels.
        one = body("derived-tampa2-layer3.body")
        attrs = one[one.index('      "attributes"'):one.rindex("    }")]
        two = one.replace(attrs, attrs + "    },\n    {\n" + attrs)
        _, out, _ = run([str(TAMPA2[0]), str(TAMPA2[1])], replay(bodies={f.layer_url(3, *TAMPA2): two}))
        self.assertIn("FIRM Panels feature 1 of 2 (layer 3):", out)
        self.assertIn("FIRM Panels feature 2 of 2 (layer 3):", out)


class AddressTests(unittest.TestCase):
    def test_one_match_runs_the_flood_queries_at_its_coordinates(self):
        fetcher = replay()
        code, out, _ = run(["--address", WHITE_HOUSE], fetcher)
        self.assertEqual(code, 0)
        self.assertEqual(fetcher.seen, [f.geocoder_url(WHITE_HOUSE), f.layer_url(28, 38.898702605245, -77.035189204737),
                                        f.layer_url(3, 38.898702605245, -77.035189204737)])
        self.assertIn('Matched address (matchedAddress) as shown: `"1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20500"`',
                      out)
        self.assertIn("Coordinates as shown: x (longitude) -77.035189204737, y (latitude) 38.898702605245", out)
        self.assertIn(body("geocoder-matched.body"), out)

    def test_no_match_is_a_report_with_no_flood_query(self):
        fetcher = replay()
        code, out, _ = run(["--address", NO_SUCH], fetcher)
        self.assertEqual(code, 0)
        self.assertEqual(fetcher.seen, [f.geocoder_url(NO_SUCH)])
        self.assertIn("The Census Geocoder matched no address", out)
        self.assertIn(body("geocoder-no-match.body"), out)
        self.assertNotIn("Flood Hazard Zones", out)

    def test_several_matches_are_listed_with_no_flood_query(self):
        # DERIVED: the captured match twice.
        one = body("geocoder-matched.body")
        match = one[one.index('[{"tigerLine"') + 1:one.rindex("]")]
        two = one.replace(match, match + "," + match)
        fetcher = replay(bodies={f.geocoder_url(WHITE_HOUSE): two})
        _, out, _ = run(["--address", WHITE_HOUSE], fetcher)
        self.assertEqual(len(fetcher.seen), 1)
        self.assertIn("The Census Geocoder returned 2 matches for this address, so no flood query was run.", out)


class FailClosedTests(unittest.TestCase):
    def test_bodies_without_the_documented_shape_exit_2_with_no_report(self):
        bad = ['{"SYNTHETIC": "no features member"}', '{"features": {}}', '{"features": [1]}',
               '{"features": [{"attributes": {"FLD_ZONE": "AE"}}]}', "<html>SYNTHETIC</html>", ""]
        for text in bad:
            code, out, err = run([str(TAMPA2[0]), str(TAMPA2[1])], replay(bodies={f.layer_url(28, *TAMPA2): text}))
            self.assertEqual((code, out), (2, ""), text)
            self.assertIn("no report", err)

    def test_a_geocoder_body_without_the_documented_shape_exits_2(self):
        for text in ('{"result": {}}', '{"result": {"addressMatches": [{"matchedAddress": "SYNTHETIC"}]}}'):
            code, out, _ = run(["--address", WHITE_HOUSE], replay(bodies={f.geocoder_url(WHITE_HOUSE): text}))
            self.assertEqual((code, out), (2, ""), text)

    def test_a_failed_fetch_is_never_an_empty_result(self):
        def broken(url):
            raise f.FetchError("request to %s failed: SYNTHETIC connection closed; no report" % url)
        code, out, err = run([str(TAMPA2[0]), str(TAMPA2[1])], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection closed", err)

    def test_bad_inputs_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for argv in ([], ["27.9"], ["91", "0"], ["0", "181"], ["nan", "0"], ["x", "y"], ["--address", " "],
                     ["--address", "a" * 201], ["1", "2", "--address", WHITE_HOUSE]):
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
        url = f.layer_url(28, *TAMPA2)
        answer = self.Answer(200, b'{"features":[]}', url, [("Content-Type", "application/json"),
                                                            ("Set-Cookie", "SYNTHETIC=1")])
        with mock.patch("urllib.request.urlopen", lambda request, timeout=None: answer):
            cap = f.fetch(url)
        self.assertEqual(cap.status_line, "HTTP/1.1 200 X")
        self.assertIn("Content-Type: application/json", cap.transcript())
        self.assertNotIn("SYNTHETIC=1", cap.transcript())
        self.assertIn("(a Set-Cookie header was returned and is not printed)", cap.transcript())

    def test_errors_non_200_and_redirects_off_host_fail_closed(self):
        url = f.layer_url(28, *TAMPA2)

        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "X", {}, io.BytesIO(b""))

        def closed(request, timeout=None):
            raise urllib.error.URLError("SYNTHETIC remote end closed connection without response")
        fakes = [http_error, closed,
                 lambda request, timeout=None: self.Answer(206, b"{}", url),
                 lambda request, timeout=None: self.Answer(200, b"{}", "https://example.invalid/x")]
        for fake in fakes:
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(f.FetchError):
                    f.fetch(url)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.flood_check, its own module object.
        with mock.patch.object(endpoints.fl, "fetch", replay(endpoints.fl)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/flood", qs, None)

    def test_route(self):
        status, _, text = self.get("lat=27.9235&lon=-82.4515")
        self.assertEqual(status, "200 OK")
        text = text.decode() if isinstance(text, bytes) else text
        self.assertIn('- SFHA: true (SFHA_TF as shown: `"T"`)', text)
        self.assertEqual(self.get("address=" + NO_SUCH.replace(" ", "+").replace(",", "%2C"))[0], "200 OK")
        for qs in ("", "lat=27.9", "lat=95&lon=0", "lat=1&lon=2&address=x", "address="):
            self.assertEqual(self.get(qs)[0], "400 Bad Request", qs)
        self.assertEqual(endpoints.describe()["/flood"]["sources"][2], f.GEOCODER_URL)

    def test_route_maps_a_failure_to_502(self):
        def refused(url):
            raise endpoints.fl.FetchError("SYNTHETIC connection closed; no report")
        with mock.patch.object(endpoints.fl, "fetch", refused):
            self.assertEqual(recall_api.handle("GET", "/flood", "lat=27.9235&lon=-82.4515", None)[0],
                             "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
