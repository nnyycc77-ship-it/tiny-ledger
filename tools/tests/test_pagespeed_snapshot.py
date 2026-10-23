"""Tests for tools/pagespeed_snapshot.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_pagespeed_snapshot.py' -v

Fixtures:

* fixtures/pagespeed/keyless-429.http is a real capture: the complete
  transcript the tool's own fetch() received from the live PageSpeed
  Insights API for a keyless request, saved unmodified. Its request URL,
  UTC retrieval time and SHA-256 are in fixtures/pagespeed/provenance.json
  and the hash is checked here.
* SYNTHETIC_200 below is NOT a capture. No successful (keyed) live
  response was available when these tests were written, so the parser is
  exercised on a hand built object that carries only the field names the
  tool reads (lighthouseResult.categories.<name>.score and
  lighthouseResult.audits.<id>.displayValue / numericValue / numericUnit)
  with placeholder values; it is labelled synthetic at the place it is
  used and nothing in it is presented as a measurement.
* The fetch tests use a local HTTP server on 127.0.0.1 and nothing else.
"""

import hashlib
import http.server
import io
import json
import os
import sys
import threading
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pagespeed_snapshot as ps  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "pagespeed"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
KEYLESS_429 = (FIXTURES / "keyless-429.http").read_text(encoding="utf-8")
PAGE = "https://example.com/"

# SYNTHETIC: a hand built structure for the parser, not a capture. Values are
# placeholders chosen to be recognisable as such; nothing here is a measurement.
SYNTHETIC_200 = {
    "lighthouseResult": {
        "finalUrl": "https://synthetic.invalid/",
        "fetchTime": "SYNTHETIC-FETCH-TIME",
        "lighthouseVersion": "SYNTHETIC-VERSION",
        "categories": {
            "performance": {"score": 0.5},
            "accessibility": {"score": 0.5},
            "best-practices": {"score": 0.5},
            # "seo" deliberately absent: the tool must print "not shown"
        },
        "audits": {
            "largest-contentful-paint": {"displayValue": "SYNTHETIC-LCP", "numericValue": 1, "numericUnit": "millisecond"},
            "cumulative-layout-shift": {"displayValue": "SYNTHETIC-CLS", "numericValue": 0, "numericUnit": "unitless"},
            # "total-blocking-time" deliberately absent
        },
    }
}


def capture_from_transcript(url, transcript, retrieved="2026-10-23T00:00:00Z"):
    head, body = transcript.split("\n\n", 1)
    lines = head.split("\n")
    return ps.Capture(url, retrieved, lines[0], lines[1:], body)


class FixtureTests(unittest.TestCase):
    def test_capture_integrity_and_provenance(self):
        meta = PROVENANCE["keyless-429.http"]
        self.assertEqual(hashlib.sha256((FIXTURES / "keyless-429.http").read_bytes()).hexdigest(), meta["sha256"])
        self.assertEqual(meta["url"], ps.request_url(PAGE, "mobile"))
        self.assertRegex(meta["retrieved_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertTrue(KEYLESS_429.startswith("HTTP/1.1 429 Too Many Requests\n"))
        body = KEYLESS_429.split("\n\n", 1)[1]
        data = json.loads(body)
        self.assertEqual(data["error"]["code"], 429)
        self.assertEqual(data["error"]["status"], "RESOURCE_EXHAUSTED")
        self.assertIn("Queries per day", data["error"]["message"])


class QueryBuildingTests(unittest.TestCase):
    def test_request_url_shape(self):
        self.assertEqual(
            ps.request_url("https://example.com/", "mobile"),
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2Fexample.com%2F"
            "&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo",
        )

    def test_key_goes_in_the_request_but_is_redacted_in_the_record(self):
        sent = ps.request_url(PAGE, "desktop", key="not-a-real-key")
        self.assertTrue(sent.endswith("&key=not-a-real-key"))
        recorded = ps.recorded_url(PAGE, "desktop", True)
        self.assertNotIn("not-a-real-key", recorded)
        self.assertTrue(recorded.endswith("&key=" + ps.KEY_MARKER))
        self.assertEqual(ps.recorded_url(PAGE, "desktop", False), ps.request_url(PAGE, "desktop"))

    def test_url_and_strategy_validation(self):
        with self.assertRaises(ValueError):
            ps.check_url("example.com")
        with self.assertRaises(ValueError):
            ps.check_url("ftp://example.com/")
        with self.assertRaises(ValueError):
            ps.request_params(PAGE, "tablet")

    def test_exclusions_must_name_a_given_page(self):
        pages = [PAGE, "https://example.com/about?x=1"]
        self.assertEqual(ps.parse_exclusions(['https://example.com/about?x=1="not public"'], pages),
                         {"https://example.com/about?x=1": "not public"})
        with self.assertRaises(ValueError):
            ps.parse_exclusions(["https://example.com/other=reason"], pages)
        with self.assertRaises(ValueError):
            ps.parse_exclusions([PAGE], pages)


class ErrorPathTests(unittest.TestCase):
    def setUp(self):
        self.cap = capture_from_transcript(ps.request_url(PAGE, "mobile"), KEYLESS_429, PROVENANCE["keyless-429.http"]["retrieved_utc"])

    def test_page_the_api_could_not_measure_is_kept_with_full_error(self):
        lines = ps.render_report("example.com", [PAGE], "mobile", {PAGE: self.cap})
        text = "\n".join(lines)
        self.assertIn("## Page 1: https://example.com/", text)
        self.assertIn("HTTP status as returned: 429 Too Many Requests.", text)
        self.assertIn("The API could not measure this page: the response status is 429 Too Many Requests, not 200.", text)
        self.assertIn("- Error code as shown (error.code): 429", text)
        self.assertIn("- Error status as shown (error.status): RESOURCE_EXHAUSTED", text)
        self.assertIn("- Error message as shown (error.message): Quota exceeded for quota metric 'Queries'", text)
        self.assertNotIn("| performance |", text)  # no score table for an unmeasured page
        # The complete transcript sits directly beneath the request URL in Sources.
        link = lines.index("- Request URL: " + self.cap.url)
        self.assertEqual(lines[link + 1], "- Retrieved (UTC): " + self.cap.retrieved)
        self.assertTrue(lines[link + 2].startswith("Excerpt ("))
        self.assertEqual(lines[link + 3], "```")
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual("\n".join(lines[link + 4:fence_end]), KEYLESS_429)

    def test_non_json_error_body_is_still_printed(self):
        cap = ps.Capture(ps.request_url(PAGE, "mobile"), "2026-10-23T00:00:00Z", "HTTP/1.1 503 Service Unavailable",
                         ["Content-Type: text/html"], "<html>busy</html>")
        text = "\n".join(ps.render_report("x", [PAGE], "mobile", {PAGE: cap}))
        self.assertIn("The API could not measure this page: the response status is 503 Service Unavailable, not 200.", text)
        self.assertIn("- The response body is not JSON", text)
        self.assertIn("<html>busy</html>", text)


class SuccessPathTests(unittest.TestCase):
    """Parser tests on SYNTHETIC_200, a hand built structure, not a capture."""

    def setUp(self):
        body = json.dumps(SYNTHETIC_200)
        self.cap = ps.Capture(ps.request_url(PAGE, "mobile"), "2026-10-23T00:00:00Z", "HTTP/1.1 200 OK",
                              ["Content-Type: application/json; charset=UTF-8"], body)

    def test_scores_and_metrics_as_shown_with_field_paths(self):
        text = "\n".join(ps.render_report("x", [PAGE], "mobile", {PAGE: self.cap}))
        self.assertIn("- Final URL as shown (lighthouseResult.finalUrl): https://synthetic.invalid/", text)
        self.assertIn("| performance | 0.5 | `lighthouseResult.categories.performance.score` |", text)
        self.assertIn("| seo | not shown | `lighthouseResult.categories.seo.score` |", text)
        self.assertIn("| Largest Contentful Paint | SYNTHETIC-LCP | 1 | millisecond | `lighthouseResult.audits.largest-contentful-paint` |", text)
        self.assertIn("| Total Blocking Time | not shown | not shown | not shown | `lighthouseResult.audits.total-blocking-time` |", text)
        self.assertNotIn("The API could not measure this page", text)

    def test_200_with_non_object_body_claims_nothing(self):
        cap = ps.Capture(ps.request_url(PAGE, "mobile"), "2026-10-23T00:00:00Z", "HTTP/1.1 200 OK", [], "[]")
        text = "\n".join(ps.render_report("x", [PAGE], "mobile", {PAGE: cap}))
        self.assertIn("the body is not a JSON object", text)
        self.assertNotIn("| performance |", text)

    def test_exclusion_and_source_order(self):
        other = "https://example.com/about"
        caps = {PAGE: self.cap, other: capture_from_transcript(ps.request_url(other, "mobile"), KEYLESS_429)}
        lines = ps.render_report("x", [PAGE, other], "mobile", caps, {other: "redirects to a login page"})
        text = "\n".join(lines)
        self.assertIn("## Page 1: https://example.com/", text)
        self.assertNotIn("## Page 2:", text)
        self.assertIn("## Checked and excluded", text)
        self.assertIn("### Excluded page 1: https://example.com/about", text)
        self.assertIn("- Checked and excluded because: redirects to a login page", text)
        self.assertLess(text.index("## Checked and excluded"), text.index("## Sources"))
        self.assertLess(text.index("### Source. S1. PageSpeed Insights API, page https://example.com/"),
                        text.index("### Source. S2. PageSpeed Insights API, page https://example.com/about"))
        self.assertIn("source S2", text.split("### Excluded page 1")[1].split("## Sources")[0])


class _Handler(http.server.BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        status, body = self.routes.get(self.path, (404, b"not found"))
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.send_header("X-Test-Order", "second")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


LIVE_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class FetchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d/run" % cls.server.server_port
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _path(self, url):
        return url[url.index("/run"):]

    def test_transcript_shape_and_header_order(self):
        body = KEYLESS_429.split("\n\n", 1)[1]
        _Handler.routes = {"/run?a=1": (429, body.encode("utf-8"))}
        cap = ps.fetch(self.base + "?a=1")
        self.assertRegex(cap.retrieved, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertFalse(cap.status_ok)
        lines = cap.transcript.split("\n")
        self.assertEqual(lines[0], "HTTP/1.0 429 Too Many Requests")
        self.assertTrue(lines[1].startswith("Server: "))
        self.assertLess(lines.index("Content-Type: application/json; charset=UTF-8"), lines.index("X-Test-Order: second"))
        self.assertTrue(cap.transcript.endswith("\n\n" + body))

    def test_key_value_is_redacted_from_transcript_and_counted(self):
        _Handler.routes = {"/run?k=1": (200, b'{"echo": "not-a-real-key"}')}
        cap = ps.fetch(self.base + "?k=1", key="not-a-real-key", recorded=self.base + "?k=1&key=" + ps.KEY_MARKER)
        self.assertNotIn("not-a-real-key", cap.transcript)
        self.assertIn("[key value redacted]", cap.body)
        self.assertEqual(cap.redactions, 1)
        self.assertEqual(cap.url, self.base + "?k=1&key=" + ps.KEY_MARKER)

    def _run_main(self, argv, env_key=None):
        ps.API_URL = self.base
        saved = os.environ.pop(ps.KEY_ENV, None)
        if env_key:
            os.environ[ps.KEY_ENV] = env_key
        out, err = io.StringIO(), io.StringIO()
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = ps.main(argv)
        finally:
            sys.stdout, sys.stderr = stdout, stderr
            ps.API_URL = LIVE_API_URL
            os.environ.pop(ps.KEY_ENV, None)
            if saved is not None:
                os.environ[ps.KEY_ENV] = saved
        return code, out.getvalue(), err.getvalue()

    def test_main_end_to_end_with_key_never_printed(self):
        ps.API_URL = self.base
        try:
            u1 = self._path(ps.request_url(PAGE, "mobile", key="not-a-real-key"))
            u2 = self._path(ps.request_url("https://example.com/about", "mobile", key="not-a-real-key"))
        finally:
            ps.API_URL = LIVE_API_URL
        _Handler.routes = {
            u1: (200, json.dumps(SYNTHETIC_200).encode("utf-8")),
            u2: (429, KEYLESS_429.split("\n\n", 1)[1].encode("utf-8")),
        }
        code, out, err = self._run_main(["--subject", "Example site", PAGE, "https://example.com/about"], env_key="not-a-real-key")
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("## Subject: Example site\n"))
        self.assertIn(ps.SCOPE_LINE, out)
        self.assertIn("## Page 1: https://example.com/", out)
        self.assertIn("| performance | 0.5 |", out)
        self.assertIn("## Page 2: https://example.com/about", out)
        self.assertIn("could not measure this page: the response status is 429 Too Many Requests", out)
        self.assertNotIn("not-a-real-key", out)
        self.assertIn("&key=" + ps.KEY_MARKER, out)
        self.assertEqual(out.count("- Request URL: "), 2)

    def test_main_transport_failure_prints_nothing(self):
        self.server.shutdown()
        self.server.server_close()
        try:
            code, out, err = self._run_main([PAGE])
        finally:
            type(self).server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
            type(self).thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            type(self).base = "http://127.0.0.1:%d/run" % self.server.server_port
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)

    def test_main_argument_rules(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                ps.main([])
            with self.assertRaises(SystemExit):
                ps.main(["example.com"])
            with self.assertRaises(SystemExit):
                ps.main([PAGE, "--strategy", "tablet"])
            with self.assertRaises(SystemExit):
                ps.main(["https://a.test/1", "https://a.test/2", "https://a.test/3", "https://a.test/4", "https://a.test/5", "https://a.test/6"])
            with self.assertRaises(SystemExit):
                ps.main([PAGE, "--exclude", "https://other.test/=reason"])


if __name__ == "__main__":
    unittest.main()
