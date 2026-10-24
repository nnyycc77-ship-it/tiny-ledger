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
* REAL CAPTURE, 400 SHAPES: the seventeen bad query fixtures added for
  issue #225 (<endpoint>-400.http) are transcripts from the same local
  gated server at main b90de2e, each the bare endpoint path with no
  query string, answered 400 before any source fetch. Their provenance
  entries record the server config (the same SYNTHETIC placeholder
  wallet and labelled test EDGAR_CONTACT, which /formd checks before
  its query) and the SHA-256 of each.
* REPLAYED CAPTURE, 502 SHAPES: the seventeen source failure fixtures
  added for issue #235 (<endpoint>-502.http) are transcripts from the
  same local gated server at main a92012c, run with its proxy settings
  pointed at a closed local port so every source fetch failed at
  transport and each endpoint answered its own 502 to a valid sample
  query. Their provenance entries record that replay config in full
  (including the empty tool cache folder used so /faa attempted its
  archive download) and the SHA-256 of each.
* REPLAYED CAPTURE, 503 SHAPE: the formd-503.http fixture added for
  issue #245 is a transcript from the same local gated server at main
  1784d43 run without EDGAR_CONTACT, so the endpoint answered 503 to
  a valid sample query before fetching anything. Its provenance entry
  records the missing contact as the capture config and the SHA-256.
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

    def test_default_run_passes_all_440_with_the_raw_responses(self):
        # 20 original assertions, 18 endpoint sections of 5, 26 bad
        # query sections of 4, 28 bad query accounting lines, 26 source
        # failure sections of 4, 28 source failure accounting lines,
        # two unavailable sections of 5 (/formd and /insider), 28
        # unavailable accounting lines, and 28 coverage lines, one per
        # GET path in api/openapi.json (seven paths added by issue #243,
        # with 400 and 502 captures, a 503 capture for /insider, and a
        # reasoned entry in NO_ENDPOINT_CAPTURE; /bank added by issue #320
        # with 200, 400 and 502 captures; /disaster added by issue #312
        # with 400 and 502 captures and a reasoned 200, with no 503).
        code, out, err = run_main([])
        self.assertEqual(code, 0, err)
        self.assertIn("Result: PASS, every assertion held.", out)
        self.assertEqual(out.count("- PASS:"), 440)
        self.assertNotIn("- FAIL:", out)
        self.assertIn("Source: <http://127.0.0.1:8765/openapi.json>", out)
        self.assertIn("Retrieved (UTC): 2026-10-23T14:51:26Z", out)
        self.assertIn((FIX / "openapi.http").read_text(encoding="utf-8"), out)
        self.assertIn((FIX / "vin.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /vin has an offline check", out)
        self.assertIn("- PASS: GET /faa has an offline check", out)
        self.assertIn("- PASS: GET /epa with no valid input answers 400", out)
        self.assertIn("- PASS: GET /recall 400 shape not capturable offline:", out)
        self.assertIn((FIX / "epa-400.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /csl with its source failing answers 502", out)
        self.assertIn("- PASS: GET /oig with its source failing answers 502", out)
        self.assertIn("- PASS: GET /insider with no valid input answers 400", out)
        self.assertIn("- PASS: GET /flood has no captured 200 yet: the capture for issue #243 ran in a container "
                      "whose network policy refuses hazards.fema.gov", out)
        self.assertIn((FIX / "oig-502.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /recall 502 shape not capturable offline:", out)
        self.assertIn((FIX / "csl-502.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /formd unconfigured on the server answers 503", out)
        self.assertIn("- PASS: GET /formd 503 shape captured in formd-503.http", out)
        self.assertIn("- PASS: GET /recall 503 shape not capturable offline:", out)
        self.assertIn((FIX / "formd-503.http").read_text(encoding="utf-8"), out)
        self.assertIn("- PASS: GET /insider 503 shape captured in insider-503.http", out)
        self.assertIn((FIX / "insider-503.http").read_text(encoding="utf-8"), out)

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
        self.assertIn("- FAIL: GET /zzz coverage is not accounted for exactly once", out)
        self.assertIn("Endpoint coverage: GET /zzz coverage is not accounted for exactly once", out)

    def test_a_path_both_checked_and_reasoned_fails_coverage(self):
        # DERIVED: the real captures, with /vin (which has a 200 fixture) also given a reason.
        caps = smoke.offline_captures()
        with mock.patch.dict(smoke.NO_ENDPOINT_CAPTURE, {"/vin": "SYNTHETIC reason"}):
            lines = smoke.check_coverage(caps)
        self.assertIn(("GET /vin coverage is not accounted for exactly once", False), lines)

    def test_a_reasoned_path_passes_coverage_with_its_reason(self):
        lines = dict(smoke.check_coverage(smoke.offline_captures()))
        self.assertTrue(lines["GET /github has no captured 200 yet: " + smoke.NO_ENDPOINT_CAPTURE["/github"]])
        self.assertNotIn("GET /github has an offline check", lines)

    def test_endpoint_shape_failure_is_named(self):
        # DERIVED: the real /fx capture with its status changed to a 502.
        caps = smoke.offline_captures()
        caps["endpoints"]["/fx"] = caps["endpoints"]["/fx"]._replace(
            status_line="HTTP/1.0 502 Bad Gateway", status=502)
        report, ok = smoke.run_checks(caps, "offline: derived")
        self.assertFalse(ok)
        self.assertIn("- FAIL: GET /fx answers 200", report)

    def test_missing_bad_query_fixture_fails_closed_and_names_the_endpoint(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            (tmp / "epa-400.http").unlink()  # DERIVED: the real fixture set minus one 400 file
            with self.assertRaises(smoke.SmokeError) as ctx:
                smoke.offline_captures(tmp)
            self.assertIn("/epa", str(ctx.exception))
        finally:
            shutil.rmtree(tmp)

    def test_unaccounted_400_shape_fails_the_run_and_is_named(self):
        # DERIVED: the real captures with one invented path in the
        # coverage denominator, in neither 400 table.
        caps = smoke.offline_captures()
        caps["coverage_paths"] = list(caps["coverage_paths"]) + ["/zzz"]
        with mock.patch.object(smoke, "offline_captures", return_value=caps):
            code, out, err = run_main([])
        self.assertEqual(code, 1, err)
        self.assertIn("- FAIL: GET /zzz 400 shape is not accounted for exactly once", out)

    def test_bad_query_shape_failure_is_named(self):
        # DERIVED: the real /epa 400 capture with its status changed to a 200.
        caps = smoke.offline_captures()
        caps["bad_queries"]["/epa"] = caps["bad_queries"]["/epa"]._replace(
            status_line="HTTP/1.0 200 OK", status=200)
        report, ok = smoke.run_checks(caps, "offline: derived")
        self.assertFalse(ok)
        self.assertIn("- FAIL: GET /epa with no valid input answers 400", report)

    def test_missing_source_failure_fixture_fails_closed_and_names_the_endpoint(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            (tmp / "vin-502.http").unlink()  # DERIVED: the real fixture set minus one 502 file
            with self.assertRaises(smoke.SmokeError) as ctx:
                smoke.offline_captures(tmp)
            self.assertIn("/vin", str(ctx.exception))
        finally:
            shutil.rmtree(tmp)

    def test_unaccounted_502_shape_fails_the_run_and_is_named(self):
        # DERIVED: the real captures with one invented path in the
        # coverage denominator, in neither 502 table.
        caps = smoke.offline_captures()
        caps["coverage_paths"] = list(caps["coverage_paths"]) + ["/zzz"]
        with mock.patch.object(smoke, "offline_captures", return_value=caps):
            code, out, err = run_main([])
        self.assertEqual(code, 1, err)
        self.assertIn("- FAIL: GET /zzz 502 shape is not accounted for exactly once", out)

    def test_source_failure_shape_failure_is_named(self):
        # DERIVED: the real /vin 502 capture with its status changed to a 200.
        caps = smoke.offline_captures()
        caps["source_failures"]["/vin"] = caps["source_failures"]["/vin"]._replace(
            status_line="HTTP/1.0 200 OK", status=200)
        report, ok = smoke.run_checks(caps, "offline: derived")
        self.assertFalse(ok)
        self.assertIn("- FAIL: GET /vin with its source failing answers 502", report)

    def test_missing_unavailable_fixture_fails_closed_and_names_the_endpoint(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in FIX.iterdir():
                shutil.copy(f, tmp / f.name)
            (tmp / "formd-503.http").unlink()  # DERIVED: the real fixture set minus the 503 file
            with self.assertRaises(smoke.SmokeError) as ctx:
                smoke.offline_captures(tmp)
            self.assertIn("/formd", str(ctx.exception))
        finally:
            shutil.rmtree(tmp)

    def test_declared_503_without_a_capture_fails_the_accounting_and_is_named(self):
        # DERIVED: the real captures with the /formd 503 capture dropped,
        # so a declared 503 endpoint has no capture in the run.
        caps = smoke.offline_captures()
        caps["unavailable"] = {}
        with mock.patch.object(smoke, "offline_captures", return_value=caps):
            code, out, err = run_main([])
        self.assertEqual(code, 1, err)
        self.assertIn("- FAIL: GET /formd 503 shape is not accounted for exactly once", out)

    def test_unavailable_shape_failure_is_named(self):
        # DERIVED: the real 503 capture with its status changed to a 200.
        caps = smoke.offline_captures()
        caps["unavailable"]["/formd"] = caps["unavailable"]["/formd"]._replace(
            status_line="HTTP/1.0 200 OK", status=200)
        report, ok = smoke.run_checks(caps, "offline: derived")
        self.assertFalse(ok)
        self.assertIn("- FAIL: GET /formd unconfigured on the server answers 503", report)


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
                captured = path in smoke.ENDPOINT_FIXTURES
                reasoned = path in smoke.NO_ENDPOINT_CAPTURE
                self.assertNotEqual(captured, reasoned, path)  # exactly one of the two
                self.assertIn(path, api_endpoints.ROUTES)
                if captured:
                    name, tool = smoke.ENDPOINT_FIXTURES[path]
                    self.assertIn(name, PROVENANCE)
                    self.assertEqual(api_endpoints.DESCRIPTIONS[path]["tool"], "tools/" + tool)
                else:
                    self.assertTrue(smoke.NO_ENDPOINT_CAPTURE[path])

    def test_every_get_path_400_shape_is_captured_or_reasoned_exactly_once(self):
        doc = json.loads(OPENAPI_FILE)
        get_paths = [p for p, ops in doc["paths"].items() if "get" in ops]
        for path in get_paths:
            with self.subTest(path=path):
                captured = path in smoke.BAD_QUERY_FIXTURES
                reasoned = path in smoke.NO_400_CAPTURE
                self.assertNotEqual(captured, reasoned, path)  # exactly one of the two
                if captured:
                    self.assertIn(smoke.BAD_QUERY_FIXTURES[path], PROVENANCE)
                    self.assertTrue(path in smoke.ENDPOINT_FIXTURES or path in smoke.NO_ENDPOINT_CAPTURE, path)
                if reasoned:
                    self.assertTrue(smoke.NO_400_CAPTURE[path])

    def test_every_get_path_502_shape_is_captured_or_reasoned_exactly_once(self):
        doc = json.loads(OPENAPI_FILE)
        get_paths = [p for p, ops in doc["paths"].items() if "get" in ops]
        for path in get_paths:
            with self.subTest(path=path):
                captured = path in smoke.SOURCE_FAILURE_FIXTURES
                reasoned = path in smoke.NO_502_CAPTURE
                self.assertNotEqual(captured, reasoned, path)  # exactly one of the two
                if captured:
                    self.assertIn(smoke.SOURCE_FAILURE_FIXTURES[path], PROVENANCE)
                    self.assertTrue(path in smoke.ENDPOINT_FIXTURES or path in smoke.NO_ENDPOINT_CAPTURE, path)
                if reasoned:
                    self.assertTrue(smoke.NO_502_CAPTURE[path])

    def test_503_captures_match_the_paths_declaring_503_exactly(self):
        # The capturable set is read off the document itself: every GET
        # path whose entry declares a 503 has a fixture in provenance,
        # and no other path has one.
        declared = smoke.repo_openapi_503_paths()
        self.assertEqual(sorted(declared), sorted(smoke.UNAVAILABLE_FIXTURES))
        for path in declared:
            self.assertIn(smoke.UNAVAILABLE_FIXTURES[path], PROVENANCE)
            self.assertTrue(path in smoke.ENDPOINT_FIXTURES or path in smoke.NO_ENDPOINT_CAPTURE, path)


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
