"""Offline tests for tools/weather_alert_check.py (issue #318). No network.

Run from the repository root: python3 -m unittest discover -s tools/tests -v

The two captures are LIVE CAPTUREs of the tool's own queries, made by H5
for this issue on 2026-10-24 with the tool's User-Agent, filed under
fixtures/weather-alerts/ next to a provenance.json that records each query
URL, retrieval time and SHA-256:

- alerts-miami-hit.http: the Miami, FL point (25.7617, -80.1918), a 200
  FeatureCollection with 3 active alerts: Coastal Flood Watch
  (Moderate), Coastal Flood Advisory (Minor), Rip Current Statement
  (Moderate), each with expires 2026-10-24T16:00:00-04:00.
- alerts-houston-empty.http: the Houston, TX point (29.7604, -95.3698), a
  200 FeatureCollection with an empty features array.

Failure bodies (a problem document, a reshaped collection, a feature
missing a field) are SYNTHETIC, derived in code below from the captures'
shape and labelled where they appear. The derived expiry case (expires
null, ends present) is built from the Miami capture in code and labelled
DERIVED. Bodies a test mutates at run time are never written back to the
fixture files.
"""

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import weather_alert_check as wa  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "weather-alerts"
RETRIEVED = "2026-10-24T12:30:00Z"
MIAMI = (25.7617, -80.1918)
HOUSTON = (29.7604, -95.3698)


def load_cap(name, url):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    status_line, rest = text.split("\n", 1)
    head, _, body = rest.partition("\n\n")
    headers = [tuple(line.split(": ", 1)) for line in head.split("\n")]
    return wa.Capture(url, RETRIEVED, status_line, headers, body)


def stub(caps):
    def fetch(url):
        if url not in caps:
            raise AssertionError("unexpected URL fetched: %s" % url)
        return caps[url]
    return fetch


MIAMI_CAP = load_cap("alerts-miami-hit.http", wa.alerts_url(*MIAMI))
HOUSTON_CAP = load_cap("alerts-houston-empty.http", wa.alerts_url(*HOUSTON))


def report_text(lat, lon, caps):
    return "\n".join(wa.report(lat, lon, fetcher=stub(caps)))


class UrlTests(unittest.TestCase):
    def test_alerts_url_is_the_documented_endpoint(self):
        self.assertEqual(wa.alerts_url(*MIAMI),
                         "https://api.weather.gov/alerts/active?point=25.7617,-80.1918")

    def test_check_point(self):
        self.assertEqual(wa.check_point("25.7617", "-80.1918"), MIAMI)
        for bad in [("north", "0"), ("91", "0"), ("0", "-181"), (None, "0")]:
            with self.assertRaises(ValueError):
                wa.check_point(*bad)


class MiamiHitTests(unittest.TestCase):
    """The live Miami capture: 3 active alerts, all fields as shown."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text(*MIAMI, {MIAMI_CAP.url: MIAMI_CAP})

    def test_header_and_observation(self):
        self.assertIn("# Weather alert check: 25.7617, -80.1918", self.text)
        self.assertIn("not a statement that conditions are safe", self.text)

    def test_collection_fields_as_shown(self):
        self.assertIn('`"Current watches, warnings, and advisories for 25.7617 N, 80.1918 W"`', self.text)
        self.assertIn('`"2026-10-24T12:05:07+00:00"`', self.text)

    def test_the_three_alerts(self):
        self.assertIn("3 active alert(s) at this point:", self.text)
        for event, severity in (("Coastal Flood Watch", "Moderate"),
                                ("Coastal Flood Advisory", "Minor"),
                                ("Rip Current Statement", "Moderate")):
            self.assertIn('- Event (event) as shown: `"%s"`' % event, self.text)
            self.assertIn('- Severity (severity) as shown: `"%s"`' % severity, self.text)
        self.assertEqual(self.text.count('- Expires (expires) as shown: `"2026-10-24T16:00:00-04:00"`'), 3)
        self.assertIn("Alert 1 of 3:", self.text)
        self.assertIn("Alert 3 of 3:", self.text)

    def test_evidence_complete(self):
        self.assertIn("Exact query URL: <https://api.weather.gov/alerts/active?point=25.7617,-80.1918>",
                      self.text)
        self.assertIn("UTC retrieval time: %s" % RETRIEVED, self.text)
        self.assertIn('"event": "Coastal Flood Watch"', self.text)  # verbatim fields block
        self.assertIn('"ends": "2026-10-26T20:00:00-04:00"', self.text)
        self.assertIn(MIAMI_CAP.body, self.text)  # complete raw response
        self.assertIn("HTTP/1.1 200 OK", self.text)

    def test_one_fetch_only(self):
        calls = []

        def counting(url):
            calls.append(url)
            return MIAMI_CAP

        wa.report(*MIAMI, fetcher=counting)
        self.assertEqual(calls, [MIAMI_CAP.url])


class HoustonEmptyTests(unittest.TestCase):
    """The live Houston capture: the proven empty features array."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text(*HOUSTON, {HOUSTON_CAP.url: HOUSTON_CAP})

    def test_no_active_alerts_proven_by_the_raw_response(self):
        self.assertIn("No active alerts at this point.", self.text)
        self.assertIn("the complete raw response below is the proof", self.text)
        self.assertIn('"features": []', self.text)  # the empty array, in the raw body
        self.assertIn(HOUSTON_CAP.body, self.text)
        self.assertNotIn("active alert(s) at this point:", self.text)


class ExpiryDerivedTests(unittest.TestCase):
    def test_expires_null_falls_back_to_ends(self):
        # DERIVED from the live Miami capture: the first alert's expires is
        # set to null in memory; its ends stays as captured.
        data = json.loads(MIAMI_CAP.body)
        data["features"][0]["properties"]["expires"] = None
        body = json.dumps(data, indent=4)
        cap = wa.Capture(MIAMI_CAP.url, RETRIEVED, MIAMI_CAP.status_line, MIAMI_CAP.headers, body)
        text = "\n".join(wa.report(*MIAMI, fetcher=stub({cap.url: cap})))
        self.assertIn("- Expires (expires) as shown: null; the alert's end (ends) as shown: "
                      '`"2026-10-26T20:00:00-04:00"`', text)
        self.assertEqual(text.count('- Expires (expires) as shown: `"2026-10-24T16:00:00-04:00"`'), 2)


class FailureTests(unittest.TestCase):
    """SYNTHETIC failure bodies: never a report, never a negative claim."""

    def body_cap(self, body, url=None):
        return wa.Capture(url or MIAMI_CAP.url, RETRIEVED, "HTTP/1.1 200 OK", [], body)

    def assert_no_report(self, cap):
        with self.assertRaises(wa.FetchError):
            wa.report(*MIAMI, fetcher=stub({cap.url: cap}))

    def test_problem_document_is_not_a_negative(self):
        problem = ('{"type": "https://api.weather.gov/problems/InvalidParameter", '
                   '"title": "Invalid Parameter", "status": 400, "detail": "point is out of coverage"}')
        self.assert_no_report(self.body_cap(problem))

    def test_features_not_an_array(self):
        self.assert_no_report(self.body_cap('{"type": "FeatureCollection", "features": {}}'))

    def test_feature_missing_severity(self):
        data = json.loads(MIAMI_CAP.body)
        del data["features"][0]["properties"]["severity"]
        self.assert_no_report(self.body_cap(json.dumps(data)))

    def test_feature_expires_wrong_type(self):
        data = json.loads(MIAMI_CAP.body)
        data["features"][0]["properties"]["expires"] = 1729879200
        self.assert_no_report(self.body_cap(json.dumps(data)))

    def test_not_json(self):
        self.assert_no_report(self.body_cap("<html>bad gateway</html>"))


class TransportTests(unittest.TestCase):
    """fetch() itself, with urlopen replaced: no network is touched."""

    def test_url_error_fails_closed(self):
        with mock.patch.object(wa.urllib.request, "urlopen",
                               side_effect=urllib.error.URLError("down")):
            with self.assertRaises(wa.FetchError):
                wa.fetch(MIAMI_CAP.url)

    def test_http_error_fails_closed(self):
        err = urllib.error.HTTPError(MIAMI_CAP.url, 404, "Not Found", {}, None)
        with mock.patch.object(wa.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(wa.FetchError) as ctx:
                wa.fetch(MIAMI_CAP.url)
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_request_carries_the_identifying_user_agent(self):
        seen = {}

        class FakeHeaders:
            def items(self):
                return [("Content-Type", "application/geo+json")]

        class Resp:
            status = 200
            reason = "OK"
            version = 11
            headers = FakeHeaders()

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return HOUSTON_CAP.body.encode()

            def geturl(self):
                return MIAMI_CAP.url

        def fake_urlopen(request, timeout=None):
            seen["ua"] = request.get_header("User-agent")
            seen["accept"] = request.get_header("Accept")
            return Resp()

        with mock.patch.object(wa.urllib.request, "urlopen", side_effect=fake_urlopen):
            cap = wa.fetch(MIAMI_CAP.url)
        self.assertEqual(seen["ua"], "tiny-ledger-weather-alert-check")
        self.assertEqual(seen["accept"], "application/geo+json")
        self.assertEqual(cap.status_line, "HTTP/1.1 200 OK")
        self.assertEqual(cap.body, HOUSTON_CAP.body)


class MainTests(unittest.TestCase):
    def run_main(self, argv, caps=None):
        out, err = io.StringIO(), io.StringIO()
        code = wa.main(argv, fetcher=stub(caps or {}), stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_hit_and_empty_exit_0(self):
        code, out, _ = self.run_main(["25.7617", "-80.1918"], {MIAMI_CAP.url: MIAMI_CAP})
        self.assertEqual(code, 0)
        self.assertIn("3 active alert(s)", out)
        code, out, _ = self.run_main(["29.7604", "-95.3698"], {HOUSTON_CAP.url: HOUSTON_CAP})
        self.assertEqual(code, 0)
        self.assertIn("No active alerts at this point.", out)

    def test_bad_arguments_exit_2_without_a_report(self):
        for argv in (["north", "0"], ["91", "0"], ["25.7617"], []):
            code, out, err = self.run_main(argv)
            self.assertEqual(code, 2, argv)
            self.assertNotIn("# Weather alert check", out)
            self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
