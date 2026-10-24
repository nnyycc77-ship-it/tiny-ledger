"""Tests for tools/api_smoke.py. Standard library only, no network beyond 127.0.0.1.

Run:  python3 -m unittest discover -s tools/tests -p 'test_api_smoke.py' -v

Which data is which:

* REAL CAPTURE: fixtures/api_smoke/descriptor.http, recall-402.http and
  openapi.http are the transcripts tools/api_smoke.py fetch() received from
  the local gated server (python3 server.py, api.payment_gate:app) on main.
  provenance.json records the URLs, the UTC time, the server config and the
  SHA-256 of each, checked here. The payout address configured for that
  capture, 0x1111111111111111111111111111111111111111, is a SYNTHETIC
  placeholder, not any real wallet.
* REAL CAPTURE, ENDPOINTS: the seventeen endpoint fixtures added for issue
  #205 (app.http through vin.http) are transcripts from the same local
  gated server, captured with the same fetch(); sixteen at main 60a1bf3,
  and faa.http at main af3646c for the PR #209 fix round, after GET /faa
  merged in PR #195. Their provenance entries record the sample query in
  each URL, the server config (the same SYNTHETIC placeholder wallet, a
  labelled test EDGAR_CONTACT, and no PAGESPEED_API_KEY, so /pagespeed
  carries its documented keyless 429 quota report) and the SHA-256 of
  each.
* LIVE LOCAL: the live mode tests run the real api.payment_gate app
  in process on 127.0.0.1, configured with the same SYNTHETIC placeholder
  address. No X-PAYMENT header is ever sent, so the facilitator is never
  contacted.
* DERIVED: test inputs built from a real capture or the real api/openapi.json
  file with one stated change, labelled where they are built.
* SYNTHETIC: the closed port used for the transport failure test.

The offline fixtures were recaptured for issue #95 from main at 04ba970,
after issue #85 (PR #93) added the GET /openapi.json route, so offline mode
and the live tests both see all 20 assertions hold. The PR #81 capture,
which predates that route and answered 404, is replaced.
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from unittest import mock
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import api_smoke as smoke  # noqa: E402
from api import payment_gate  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "api_smoke"
PROVENANCE = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
SYNTHETIC_WALLET = "0x" + "1" * 40
OPENAPI_FILE = (ROOT / "api" / "openapi.json").read_text(encoding="utf-8")


def results_by_text(results):
    return {text: ok for text, ok in results}


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = smoke.main(argv)
    return code, out.getvalue(), err.getvalue()


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name, entry in PROVENANCE.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), entry["sha256"])

    def test_capture_used_the_synthetic_placeholder_wallet(self):
        caps = smoke.offline_captures()
        self.assertEqual(json.loads(caps["descriptor"].body)["payout_wallet"], SYNTHETIC_WALLET)


class OfflineMode(unittest.TestCase):
    def setUp(self):
        self.caps = smoke.offline_captures()

    def test_descriptor_and_402_shapes_hold_on_the_real_capture(self):
        self.assertTrue(all(ok for _, ok in smoke.check_descriptor(self.caps["descriptor"])))
        wallet = json.loads(self.caps["descriptor"].body)["payout_wallet"]
        results = smoke.check_payment(self.caps["payment"], wallet)
        self.assertEqual(len(results), 12)
        self.assertTrue(all(ok for _, ok in results), results)

    def test_openapi_route_holds_on_the_real_capture(self):
        # REAL CAPTURE: GET /openapi.json on main at 04ba970 answered 200.
        results = smoke.check_openapi(self.caps["openapi"])
        self.assertTrue(results)
        self.assertTrue(all(ok for _, ok in results), results)
        self.assertEqual(self.caps["openapi"].status, 200)

    def test_default_run_passes_all_124_with_the_raw_responses(self):
        # 20 original assertions, 17 endpoint sections of 5, and 19
        # coverage lines, one per GET path in api/openapi.json.
        code, out, err = run_main([])
        self.assertEqual(code, 0, err)
        self.assertIn("Result: PASS, every assertion held.", out)
        self.assertEqual(out.count("- PASS:"), 124)
        self.assertNotIn("- FAIL:", out)
        self.assertIn("Source: <http://127.0.0.1:8765/openapi.json>", out)
        self.assertIn("Retrieved (UTC): 2026-10-23T14:51:26Z", out)
        self.assertIn((FIX / "openapi.http").read_text(encoding="utf-8"), out)
        self.assertIn((FIX / "vin.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /vin has an offline check", out)
        self.assertIn("- PASS: GET /faa has an offline check", out)

    def test_a_failed_assertion_is_named_with_the_raw_response(self):
        # DERIVED: the real openapi capture with its status line changed to a 404,
        # to keep the failure path covered now that the capture itself passes.
        caps = smoke.offline_captures()
        caps["openapi"] = caps["openapi"]._replace(status_line="HTTP/1.0 404 Not Found", status=404)
        with mock.patch.object(smoke, "offline_captures", return_value=caps):
            code, out, err = run_main([])
        self.assertEqual(code, 1, err)
        self.assertIn("- 3. OpenAPI document: GET /openapi.json answers 200", out)
        self.assertIn("- FAIL: GET /openapi.json answers 200", out)
        self.assertIn("HTTP/1.0 404 Not Found", out)

    def test_tampered_fixture_is_an_error_not_a_result(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            data = bytearray((tmp / "recall-402.http").read_bytes())
            data[-5] ^= 0x01  # DERIVED: one byte of the real capture flipped
            (tmp / "recall-402.http").write_bytes(bytes(data))
            with self.assertRaises(smoke.SmokeError):
                smoke.offline_captures(tmp)
        finally:
            shutil.rmtree(tmp)

    def test_missing_endpoint_fixture_fails_closed_and_names_the_endpoint(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            (tmp / "vin.http").unlink()  # DERIVED: the real fixture set minus one file
            with self.assertRaises(smoke.SmokeError) as ctx:
                smoke.offline_captures(tmp)
            self.assertIn("/vin", str(ctx.exception))
        finally:
            shutil.rmtree(tmp)

    def test_missing_endpoint_provenance_fails_closed_and_names_the_endpoint(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            prov = json.loads((tmp / "provenance.json").read_text(encoding="utf-8"))
            del prov["drug.http"]  # DERIVED: the real provenance minus one entry
            (tmp / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")
            with self.assertRaises(smoke.SmokeError) as ctx:
                smoke.offline_captures(tmp)
            self.assertIn("/drug", str(ctx.exception))
        finally:
            shutil.rmtree(tmp)

    def test_uncovered_endpoint_fails_the_run_and_is_named(self):
        # DERIVED: the real captures with one invented path added to the
        # coverage denominator, as if openapi.json had gained an endpoint
        # with no fixture.
        caps = smoke.offline_captures()
        caps["coverage_paths"] = list(caps["coverage_paths"]) + ["/zzz"]
        with mock.patch.object(smoke, "offline_captures", return_value=caps):
            code, out, err = run_main([])
        self.assertEqual(code, 1, err)
        self.assertIn("- FAIL: GET /zzz has an offline check", out)
        self.assertIn("Endpoint coverage: GET /zzz has an offline check", out)

    def test_endpoint_shape_failure_is_named(self):
        # DERIVED: the real /fx capture with its status changed to a 502.
        caps = smoke.offline_captures()
        caps["endpoints"]["/fx"] = caps["endpoints"]["/fx"]._replace(
            status_line="HTTP/1.0 502 Bad Gateway", status=502)
        report, ok = smoke.run_checks(caps, "offline: derived")
        self.assertFalse(ok)
        self.assertIn("- FAIL: GET /fx answers 200", report)


class CoverageTable(unittest.TestCase):
    def test_every_get_path_in_the_repo_openapi_has_a_fixture_entry(self):
        from api import endpoints as api_endpoints
        doc = json.loads(OPENAPI_FILE)
        get_paths = [p for p, ops in doc["paths"].items() if "get" in ops]
        self.assertEqual(set(smoke.repo_openapi_get_paths()), set(get_paths))
        for path in get_paths:
            with self.subTest(path=path):
                if path in ("/", "/recall"):
                    continue  # the descriptor and payment checks
                self.assertIn(path, smoke.ENDPOINT_FIXTURES)
                name, tool = smoke.ENDPOINT_FIXTURES[path]
                self.assertIn(name, PROVENANCE)
                self.assertEqual(api_endpoints.DESCRIPTIONS[path]["tool"], "tools/" + tool)


class Assertions(unittest.TestCase):
    def setUp(self):
        self.caps = smoke.offline_captures()

    def derive_payment(self, change):
        # DERIVED from the real 402 capture: the body re-encoded after `change`.
        cap = self.caps["payment"]
        doc = json.loads(cap.body)
        change(doc)
        return cap._replace(body=json.dumps(doc))

    def test_payto_must_equal_the_descriptor_wallet(self):
        results = results_by_text(smoke.check_payment(self.caps["payment"], "0x" + "2" * 40))
        self.assertFalse(results["accepts[0].payTo equals the descriptor payout_wallet"])

    def test_long_description_fails(self):
        cap = self.derive_payment(lambda d: d["accepts"][0].update(description="x" * 501))
        results = results_by_text(smoke.check_payment(cap, SYNTHETIC_WALLET))
        self.assertFalse(results["accepts[0].description is present and at most 500 characters"])

    def test_non_numeric_amount_and_wrong_network_fail(self):
        def change(d):
            d["accepts"][0]["maxAmountRequired"] = "0.05"
            d["accepts"][0]["network"] = "base-sepolia"
        results = results_by_text(smoke.check_payment(self.derive_payment(change), SYNTHETIC_WALLET))
        self.assertFalse(results["accepts[0].maxAmountRequired is numeric"])
        self.assertFalse(results['accepts[0].network is "base"'])

    def test_the_repo_openapi_document_itself_passes_the_shape(self):
        # DERIVED: the real api/openapi.json file wrapped in a 200 transcript.
        cap = smoke.Capture("file:api/openapi.json", "-", "HTTP/1.1 200 OK", 200, [], OPENAPI_FILE)
        self.assertTrue(all(ok for _, ok in smoke.check_openapi(cap)))


class Recorder(WSGIRequestHandler):
    seen = []

    def log_message(self, *args):
        pass

    def get_environ(self):
        env = super().get_environ()
        Recorder.seen.append(dict((k, v) for k, v in env.items() if k.startswith("HTTP_")))
        return env


def serve(app):
    server = make_server("127.0.0.1", 0, app, handler_class=Recorder)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class LiveMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The gate and the wrapped recall_api.app both read the payout address
        # from os.environ in a real deployment (server.py), so set it there.
        cls.env = mock.patch.dict(os.environ, {"PAYOUT_WALLET_ADDRESS": SYNTHETIC_WALLET})
        cls.env.start()
        cls.gated = serve(payment_gate.build_app())

    @classmethod
    def tearDownClass(cls):
        cls.gated.shutdown()
        cls.gated.server_close()
        cls.env.stop()

    def base(self, server):
        return "http://127.0.0.1:%d" % server.server_port

    def test_live_against_the_gated_app_all_pass(self):
        # The real gated app serves GET /openapi.json since issue #85, so all 20 hold.
        Recorder.seen = []
        code, out, err = run_main(["--live", self.base(self.gated), "--product", "Instant Pot"])
        self.assertEqual(code, 0, err)
        self.assertIn("Result: PASS, every assertion held.", out)
        self.assertEqual(out.count("- PASS:"), 20)
        self.assertNotIn("- FAIL:", out)
        self.assertEqual(len(Recorder.seen), 3)
        for headers in Recorder.seen:
            self.assertNotIn("HTTP_X_PAYMENT", headers)

    def test_transport_failure_fails_closed(self):
        code, out, err = run_main(["--live", "http://127.0.0.1:9"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("could not run, no result", err)

    def test_bad_live_url_is_refused(self):
        code, out, _ = run_main(["--live", "ftp://example.invalid"])
        self.assertEqual((code, out), (2, ""))


if __name__ == "__main__":
    unittest.main()
