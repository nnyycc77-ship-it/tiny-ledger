"""Tests for tools/earthquake_check.py and its GET /earthquake route (issue #317). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_earthquake_check.py' -v

Fixtures (fixtures/earthquake/, recorded in provenance.json): every *.body
is a REAL CAPTURE, the response body verbatim from the coordinator's USGS
captures on issue #317 (comments 6384169097 to 6384170740), each with its
status line and headers as posted; their SHA-256 match the ones posted.
The captures were taken with the window 2016-10-24T00:00:00 to
2026-10-24T00:00:00, so the tests fix the call's moment at
2026-10-24T00:00:00Z. Variants built here say DERIVED or SYNTHETIC where
they are built. Every test runs with urlopen replaced by a function that
fails the test, except the fetch tests, which replace it with a fake.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import earthquake_check as e  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "earthquake"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
NOW = datetime(2026, 10, 24, tzinfo=timezone.utc)  # the captures' window end
LA = (34.0522, -118.2437, 25.0)
ORLANDO = (28.5383, -81.3792, 10.0)
START, END = "2016-10-24T00:00:00", "2026-10-24T00:00:00"


def body(name):
    return (FIX / name).read_text(encoding="utf-8")


def capture(name, url=None, text=None):
    entry = PROV[name]
    headers = [tuple(h.split(": ", 1)) for h in entry["headers"]]
    return e.Capture(url or entry["url"], "2026-10-24T12:22:16Z", entry["status_line"], headers,
                     body(name) if text is None else text)


def replay(bodies=None):
    """A fetcher answering each captured URL from its fixture. Any other URL fails the test.
    `bodies` maps a fixture name to replacement text, built in the test."""
    by_url = {entry["url"]: name for name, entry in PROV.items()}
    bodies = bodies or {}

    def fetcher(url):
        if url not in by_url:
            raise AssertionError("unexpected URL %s" % url)
        name = by_url[url]
        return capture(name, text=bodies.get(name))
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("the test tried to reach the network")


class OfflineCase(unittest.TestCase):
    def setUp(self):
        p = mock.patch("urllib.request.urlopen", no_network)
        p.start()
        self.addCleanup(p.stop)


class FixtureTests(unittest.TestCase):
    def test_every_fixture_matches_its_recorded_hash_and_size(self):
        for name, entry in PROV.items():
            with self.subTest(name=name):
                data = (FIX / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["bytes"])
                self.assertEqual(entry["kind"], "REAL CAPTURE")


class InputTests(unittest.TestCase):
    def test_point_and_radius_rules(self):
        self.assertEqual(e.check_point("34.0522", "-118.2437"), (34.0522, -118.2437))
        self.assertEqual(e.check_radius("25"), 25.0)
        for lat, lon in (("x", "0"), ("91", "0"), ("0", "-181"), (None, "0")):
            with self.assertRaises(ValueError):
                e.check_point(lat, lon)
        for r in ("0", "0.5", "501", "abc", None):
            with self.assertRaises(ValueError):
                e.check_radius(r)
        self.assertEqual(e.check_radius("1"), 1.0)
        self.assertEqual(e.check_radius("500"), 500.0)

    def test_window_is_ten_years_to_the_moment(self):
        self.assertEqual(e.window(NOW), (START, END))
        leap = datetime(2028, 2, 29, 12, 30, 5, tzinfo=timezone.utc)
        self.assertEqual(e.window(leap), ("2018-02-28T12:30:05", "2028-02-29T12:30:05"))

    def test_urls_are_the_captured_urls(self):
        self.assertEqual(e.count_url(*LA, START, END), PROV["la-count.body"]["url"])
        self.assertEqual(e.query_url(*LA, START, END), PROV["la-query.body"]["url"])
        self.assertEqual(e.count_url(*ORLANDO, START, END), PROV["orlando-count.body"]["url"])
        self.assertEqual(e.query_url(*ORLANDO, START, END), PROV["orlando-query.body"]["url"])


class ReportTests(OfflineCase):
    def test_populated_point_states_the_count_and_the_ten_largest(self):
        text = "\n".join(e.report(*LA, fetcher=replay(), now=NOW))
        self.assertIn("Events the USGS earthquake catalog lists inside this circle in this window: 1692", text)
        self.assertIn('"count":1692', text)
        self.assertIn("Window: 2016-10-24T00:00:00 to 2026-10-24T00:00:00 UTC", text)
        self.assertIn("The 10 largest by magnitude", text)
        # REAL CAPTURE values, first and last listed events, cut verbatim.
        self.assertIn('1. Magnitude 4.54 (magType `"mw"`), `"3km WSW of South El Monte, CA"`', text)
        self.assertIn("Time: 1600497526930 (2020-09-19 06:38:46 UTC, converted from epoch milliseconds)", text)
        self.assertIn('event id: `"ci38695658"`', text)
        self.assertIn('10. Magnitude 3.52 (magType `"ml"`), `"2km W of Willowbrook, CA"`', text)
        self.assertEqual(text.count('"type":"earthquake"\n"id":'), 10)
        # Both complete raw responses, with their headers, are the transcript.
        self.assertIn(body("la-count.body"), text)
        self.assertIn(body("la-query.body"), text)
        self.assertIn("X-Cache: Miss from cloudfront", text)
        self.assertIn("Exact query URL: <%s>" % PROV["la-query.body"]["url"], text)

    def test_empty_point_is_proven_by_both_raw_responses(self):
        text = "\n".join(e.report(*ORLANDO, fetcher=replay(), now=NOW))
        self.assertIn("lists no event inside this circle in this window", text)
        self.assertIn("not a statement that no earthquake can occur here", text)
        self.assertIn('"count":0', text)
        self.assertIn(body("orlando-count.body"), text)
        self.assertIn(body("orlando-query.body"), text)
        self.assertNotIn("largest by magnitude, in the order", text)

    def test_disagreeing_answers_are_unknown_never_a_report(self):
        # DERIVED: the real Los Angeles count paired with the real empty Orlando
        # features array, and the real Orlando count paired with the real Los
        # Angeles events.
        with self.assertRaisesRegex(e.FetchError, "disagree"):
            e.report(*LA, fetcher=replay({"la-query.body": body("orlando-query.body")}), now=NOW)
        with self.assertRaisesRegex(e.FetchError, "disagree"):
            e.report(*LA, fetcher=replay({"la-count.body": body("orlando-count.body")}), now=NOW)

    def test_misshapen_bodies_give_no_report(self):
        bad = {
            "la-count.body": ['{"maxAllowed":20000}', '{"count":-1}', '{"count":"1692"}', '{"count":true}',
                              "Error 400: Bad Request"],
            "la-query.body": ['{"type":"Feature","features":[]}', '{"type":"FeatureCollection"}',
                              '{"type":"FeatureCollection","features":{}}',
                              body("la-query.body").replace('"magType":"mw",', "", 1),
                              body("la-query.body").replace('"id":"ci38695658"', '"idx":"ci38695658"', 1),
                              body("bad-latitude.body")],
        }
        for name, texts in bad.items():
            for text in texts:  # SYNTHETIC or DERIVED from the real bodies, as written above
                with self.subTest(name=name, text=text[:40]):
                    with self.assertRaisesRegex(e.FetchError, "not a JSON object|not the documented"):
                        e.report(*LA, fetcher=replay({name: text}), now=NOW)

    def test_an_event_missing_any_cut_field_is_misshapen(self):
        # DERIVED: the real Los Angeles body with one member of its first event removed.
        raw = body("la-query.body")
        members = {"mag": '"mag":4.54,', "magType": '"magType":"mw",', "time": '"time":1600497526930,',
                   "place": '"place":"3km WSW of South El Monte, CA",', "type": '"type":"earthquake",',
                   "id": ',"id":"ci38695658"'}
        self.assertEqual(sorted(members), sorted(e.EVENT_FIELDS + ("id",)))
        for field, member in members.items():
            with self.subTest(field=field):
                self.assertLess(raw.index(member), raw.index(',\n{"type":"Feature"'))  # in the first event
                derived = raw.replace(member, "", 1)
                with self.assertRaisesRegex(e.FetchError, "an event has no %s" % field):
                    e.report(*LA, fetcher=replay({"la-query.body": derived}), now=NOW)

    def test_more_events_than_the_limit_is_misshapen(self):
        # DERIVED: the real features array with its first event repeated once more.
        raw = body("la-query.body")
        first = raw[raw.index('{"type":"Feature"'):raw.index(',\n{"type":"Feature"')]
        eleven = raw.replace('"features":[', '"features":[' + first + ",\n", 1)
        with self.assertRaisesRegex(e.FetchError, "more than the limit"):
            e.report(*LA, fetcher=replay({"la-query.body": eleven}), now=NOW)


class FetchTests(unittest.TestCase):
    def fake_response(self, status=200, text="{}", url=None):
        response = mock.MagicMock()
        response.status, response.version, response.reason = status, 11, "OK"
        response.headers.items.return_value = [("Content-Type", "application/json")]
        response.geturl.return_value = url
        response.read.return_value = text.encode("utf-8")
        response.__enter__.return_value = response
        return response

    def test_the_sources_400_is_a_failure_naming_its_reason(self):
        # REAL CAPTURE: the coordinator's latitude out of range answer, as the HTTP error body.
        url = PROV["bad-latitude.body"]["url"]
        err = urllib.error.HTTPError(url, 400, "Bad Request", {}, io.BytesIO((FIX / "bad-latitude.body").read_bytes()))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(e.FetchError) as caught:
                e.fetch(url)
        self.assertIn("answered HTTP 400", str(caught.exception))
        self.assertIn('Bad latitude value "200"', str(caught.exception))
        self.assertIn("the answer is unknown", str(caught.exception))

    def test_transport_failure_and_redirect_give_no_report(self):
        url = PROV["la-count.body"]["url"]
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
            with self.assertRaisesRegex(e.FetchError, "failed: .*timed out"):
                e.fetch(url)
        with mock.patch("urllib.request.urlopen", return_value=self.fake_response(url="https://example.org/x")):
            with self.assertRaisesRegex(e.FetchError, "redirected off its host"):
                e.fetch(url)

    def test_a_status_other_than_200_gives_no_report(self):
        # SYNTHETIC: a 204 No Content answer, which urlopen does not raise for.
        url = PROV["la-count.body"]["url"]
        with mock.patch("urllib.request.urlopen", return_value=self.fake_response(status=204, text="", url=url)):
            with self.assertRaisesRegex(e.FetchError, "answered HTTP/1.1 204"):
                e.fetch(url)

    def test_a_200_is_a_capture_with_its_headers(self):
        url = PROV["la-count.body"]["url"]
        with mock.patch("urllib.request.urlopen",
                        return_value=self.fake_response(text=body("la-count.body"), url=url)) as opened:
            cap = e.fetch(url)
        self.assertEqual(cap.body, body("la-count.body"))
        self.assertEqual(cap.status_line, "HTTP/1.1 200 OK")
        request = opened.call_args[0][0]
        self.assertEqual(request.full_url, url)
        self.assertNotIn("api_key", request.full_url.lower())


class CliTests(OfflineCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        code = e.main(argv, fetcher=replay(), stdout=out, stderr=err, now=NOW)
        return code, out.getvalue(), err.getvalue()

    def test_report_and_exit_codes(self):
        code, out, _ = self.run_main(["34.0522", "-118.2437", "25"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("# Earthquake check: 34.0522, -118.2437, radius 25 km"))
        code, _, err = self.run_main(["34.0522", "-118.2437", "900"])
        self.assertEqual(code, 2)
        self.assertIn("radius_km must be 1 to 500", err)

    def test_a_failed_fetch_exits_2_with_no_report(self):
        out, err = io.StringIO(), io.StringIO()

        def failing(url):
            raise e.FetchError("request to %s failed: SYNTHETIC; no report, the answer is unknown" % url)
        code = e.main(["34.0522", "-118.2437", "25"], fetcher=failing, stdout=out, stderr=err, now=NOW)
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("the answer is unknown", err.getvalue())


class RouteTests(OfflineCase):
    def get(self, qs):
        status, _headers, body_bytes = recall_api.handle("GET", "/earthquake", qs, None)[:3]
        return status, body_bytes.decode("utf-8")

    def test_route_serves_the_tools_own_report(self):
        with mock.patch.object(endpoints.eq, "utc_now", return_value=NOW), \
                mock.patch.object(endpoints.eq, "fetch", replay()):
            status, text = self.get("lat=34.0522&lon=-118.2437&radius_km=25")
        self.assertEqual(status, "200 OK")
        self.assertEqual(text.rstrip("\n").split("\n")[0], "# Earthquake check: 34.0522, -118.2437, radius 25 km")
        expected = "\n".join(e.report(*LA, fetcher=replay(), now=NOW))
        self.assertIn(expected.rstrip("\n"), text)

    def test_bad_queries_are_400_with_no_fetch(self):
        with mock.patch.object(endpoints.eq, "fetch", side_effect=AssertionError("no fetch expected")):
            for qs in ("", "lat=34&lon=-118", "lat=34&radius_km=5", "lat=x&lon=0&radius_km=5",
                       "lat=34&lon=-118&radius_km=0", "lat=34&lon=-118&radius_km=501",
                       "lat=1&lat=2&lon=0&radius_km=5"):
                with self.subTest(qs=qs):
                    status, text = self.get(qs)
                    self.assertEqual(status, "400 Bad Request", text)
                    self.assertTrue(text.startswith("Bad request: "))

    def test_a_failed_fetch_is_502_with_no_report(self):
        with mock.patch.object(endpoints.eq, "fetch",
                               side_effect=endpoints.eq.FetchError("SYNTHETIC failure; no report")):
            status, text = self.get("lat=34.0522&lon=-118.2437&radius_km=25")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("# Earthquake check", text)


if __name__ == "__main__":
    unittest.main()
