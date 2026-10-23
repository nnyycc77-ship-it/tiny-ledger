"""Tests for api/recall_api.py. No network.

Run from the repository root: python3 -m unittest discover -s api -v

The fetchers are patched to return recorded public responses that
already live in this repo with their provenance: the CPSC captures in
tools/tests/fixtures (verbatim HTTP captures, URLs and retrieval times
in provenance.json) and the NHTSA S24 excerpt from the published
recall delivery, as carried by tools/tests/test_nhtsa_recalls.py. No
recall data is invented here.
"""

import json
import os
import sys
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch
from wsgiref.simple_server import make_server, WSGIRequestHandler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import recall_api  # noqa: E402
from tools import cpsc_recalls, nhtsa_recalls  # noqa: E402
from tools.tests import test_nhtsa_recalls as nhtsa_fixtures  # noqa: E402

FIXTURES = ROOT / "tools" / "tests" / "fixtures"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text())
WALLET = "0x" + "ab" * 20


def captured(name):
    meta = PROVENANCE[name]
    return cpsc_recalls.Capture(meta["url"], meta["retrieved_utc"],
                                (FIXTURES / name).read_bytes().decode("utf-8"))


def fake_cpsc_fetch(product):
    """Serve the recorded capture whose query matches the product asked for."""
    for name, meta in PROVENANCE.items():
        if meta["url"] == cpsc_recalls.query_url(product):
            return captured(name)
    raise cpsc_recalls.FetchError("no recorded capture for %r" % product)


def fake_nhtsa_fetch(url):
    body = nhtsa_fixtures.S24_HEAD_CLOSED
    return nhtsa_fixtures.RETRIEVED, nhtsa_fixtures.transcript_for(body), body


class ConfigTests(unittest.TestCase):
    def test_unset_is_none(self):
        self.assertIsNone(recall_api.payout_wallet({}))
        self.assertIsNone(recall_api.payout_wallet({recall_api.PAYOUT_ENV: "   "}))

    def test_wellformed_address_is_returned(self):
        self.assertEqual(recall_api.payout_wallet({recall_api.PAYOUT_ENV: WALLET}), WALLET)

    def test_malformed_address_is_refused(self):
        for bad in ["abc", "0x1234", "0x" + "zz" * 20, WALLET + "0"]:
            with self.subTest(bad=bad):
                with self.assertRaises(recall_api.ConfigError):
                    recall_api.payout_wallet({recall_api.PAYOUT_ENV: bad})

    def test_descriptor_names_the_wallet_and_sources(self):
        doc = recall_api.descriptor(WALLET)
        self.assertEqual(doc["payout_wallet"], WALLET)
        self.assertEqual(doc["forms"]["product"]["source"], cpsc_recalls.ENDPOINT)
        self.assertTrue(doc["forms"]["vehicle"]["source"].startswith(nhtsa_recalls.BASE_URL))
        self.assertIsNone(recall_api.descriptor(None)["payout_wallet"])


class ProductFormTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(cpsc_recalls, "fetch", side_effect=fake_cpsc_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_empty_result_prints_the_full_raw_capture_beneath_the_link(self):
        status, headers, body = recall_api.handle("GET", "/recall", "product=Instant+Pot+Smart+WiFi", None)
        self.assertEqual(status, "200 OK")
        self.assertEqual(dict(headers)["Content-Type"], recall_api.TEXT_MD)
        text = body.decode("utf-8")
        cap = captured("smart-wifi.http")
        self.assertIn("# Recall check: Instant Pot Smart WiFi", text)
        self.assertIn("Exact query: GET " + cap.url, text)
        self.assertIn("Retrieved (UTC): " + cap.retrieved, text)
        self.assertIn("CPSC returned 0 record(s) for this query.", text)
        # The raw capture, CRLFs and all, sits directly beneath the source link.
        marker = "Source: <%s>\n```\n" % cap.url
        self.assertIn(marker, text)
        self.assertTrue(text.split(marker, 1)[1].startswith(cap.raw))
        self.assertTrue(cap.raw.endswith("\r\n\r\n[]"))

    def test_one_record_result_lists_the_candidate(self):
        status, _, body = recall_api.handle("GET", "/recall", "product=Instant+Pot", None)
        self.assertEqual(status, "200 OK")
        text = body.decode("utf-8")
        self.assertIn("CPSC returned 1 record(s) for this query.", text)
        self.assertIn("- Returned candidate: recall ", text)

    def test_near_match_is_checked_and_excluded_with_reason(self):
        qs = "product=Instant+Pot+Smart+WiFi&exact_name=Instant+Pot+Smart+WiFi&near=Instant+Pot"
        status, _, body = recall_api.handle("GET", "/recall", qs, None)
        self.assertEqual(status, "200 OK")
        text = body.decode("utf-8")
        self.assertIn("### Product query", text)
        self.assertIn("### Checked near-match query", text)
        self.assertIn("- Checked and excluded: recall ", text)
        self.assertIn("Reason: none of the returned product names equals", text)

    def test_near_without_exact_name_is_a_bad_request(self):
        status, _, body = recall_api.handle("GET", "/recall", "product=Instant+Pot&near=Instant+Pot", None)
        self.assertEqual(status, "400 Bad Request")
        self.assertIn("near requires exact_name", body.decode())

    def test_fetch_failure_is_502_with_no_report(self):
        with patch.object(cpsc_recalls, "fetch", side_effect=cpsc_recalls.FetchError("curl failed (exit 6); no recall conclusion")):
            status, _, body = recall_api.handle("GET", "/recall", "product=Instant+Pot", None)
        self.assertEqual(status, "502 Bad Gateway")
        text = body.decode()
        self.assertIn("no report emitted", text)
        self.assertNotIn("CPSC returned", text)


class VehicleFormTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(nhtsa_recalls, "fetch", side_effect=fake_nhtsa_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_vehicle_report_has_query_time_link_and_transcript(self):
        status, headers, body = recall_api.handle("GET", "/recall", "make=Hyundai&model=Elantra&year=2021", None)
        self.assertEqual(status, "200 OK")
        self.assertEqual(dict(headers)["Content-Type"], recall_api.TEXT_MD)
        text = body.decode("utf-8")
        self.assertIn("# Recall check: 2021 Hyundai Elantra", text)
        self.assertIn("## Subject: 2021 Hyundai Elantra", text)
        self.assertIn("- Query URL: " + nhtsa_fixtures.ELANTRA_URL, text)
        self.assertIn("- Retrieved (UTC): " + nhtsa_fixtures.RETRIEVED, text)
        self.assertIn("#### Campaign 21V796000", text)
        self.assertIn("HTTP/1.1 200 OK", text)
        self.assertLess(text.index("- Query URL: "), text.index("HTTP/1.1 200 OK"))

    def test_exclusion_is_listed_with_reason(self):
        qs = "make=Hyundai&model=Elantra&year=2021&exclude=21V796000%3Dreplaced+by+22V354000"
        status, _, body = recall_api.handle("GET", "/recall", qs, None)
        self.assertEqual(status, "200 OK")
        text = body.decode("utf-8")
        self.assertIn("Checked and excluded", text)
        self.assertIn("- Checked and excluded because: replaced by 22V354000", text)

    def test_exclusion_not_in_response_is_refused(self):
        qs = "make=Hyundai&model=Elantra&year=2021&exclude=99V000000%3Dnot+here"
        status, _, body = recall_api.handle("GET", "/recall", qs, None)
        self.assertEqual(status, "400 Bad Request")
        self.assertIn("not in the response", body.decode())

    def test_incomplete_vehicle_is_a_bad_request(self):
        status, _, body = recall_api.handle("GET", "/recall", "make=Hyundai&model=Elantra", None)
        self.assertEqual(status, "400 Bad Request")
        self.assertIn("missing: year", body.decode())

    def test_fetch_failure_is_502(self):
        import urllib.error
        with patch.object(nhtsa_recalls, "fetch", side_effect=urllib.error.URLError("name resolution failed")):
            status, _, body = recall_api.handle("GET", "/recall", "make=Hyundai&model=Elantra&year=2021", None)
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("no report emitted", body.decode())


class RoutingTests(unittest.TestCase):
    def test_root_descriptor(self):
        status, headers, body = recall_api.handle("GET", "/", "", WALLET)
        self.assertEqual(status, "200 OK")
        self.assertEqual(dict(headers)["Content-Type"], recall_api.APP_JSON)
        self.assertEqual(json.loads(body)["payout_wallet"], WALLET)
        self.assertEqual(dict(headers)["X-Payout-Wallet"], WALLET)

    def test_no_wallet_means_no_header(self):
        _, headers, _ = recall_api.handle("GET", "/", "", None)
        self.assertNotIn("X-Payout-Wallet", dict(headers))

    def test_missing_query_both_forms_and_unknown_path(self):
        self.assertEqual(recall_api.handle("GET", "/recall", "", None)[0], "400 Bad Request")
        self.assertEqual(recall_api.handle("GET", "/recall", "product=x&make=y", None)[0], "400 Bad Request")
        self.assertEqual(recall_api.handle("GET", "/nope", "", None)[0], "404 Not Found")
        self.assertEqual(recall_api.handle("POST", "/recall", "product=x", None)[0], "405 Method Not Allowed")


class _Quiet(WSGIRequestHandler):
    def log_message(self, *args):
        pass


class LocalRunTests(unittest.TestCase):
    """The WSGI app served by wsgiref, as `python3 api/recall_api.py` does."""

    @classmethod
    def setUpClass(cls):
        cls.server = make_server("127.0.0.1", 0, recall_api.app, handler_class=_Quiet)
        cls.base = "http://127.0.0.1:%d" % cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=10) as r:
                return r.status, dict(r.headers), r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read().decode("utf-8")

    def test_sample_product_query_over_http(self):
        with patch.object(cpsc_recalls, "fetch", side_effect=fake_cpsc_fetch), \
             patch.dict(os.environ, {recall_api.PAYOUT_ENV: WALLET}):
            status, headers, text = self.get("/recall?product=Instant+Pot+Smart+WiFi")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertEqual(headers["X-Payout-Wallet"], WALLET)
        cap = captured("smart-wifi.http")
        self.assertIn("Source: <%s>\n```\n%s" % (cap.url, cap.raw), text)
        self.assertIn("Retrieved (UTC): " + cap.retrieved, text)

    def test_runs_with_no_environment_set(self):
        with patch.object(nhtsa_recalls, "fetch", side_effect=fake_nhtsa_fetch), \
             patch.dict(os.environ, {}, clear=False):
            os.environ.pop(recall_api.PAYOUT_ENV, None)
            status, headers, text = self.get("/recall?make=Hyundai&model=Elantra&year=2021")
            root_status, _, root = self.get("/")
        self.assertEqual(status, 200)
        self.assertNotIn("X-Payout-Wallet", headers)
        self.assertIn("#### Campaign 21V796000", text)
        self.assertEqual(root_status, 200)
        self.assertIsNone(json.loads(root)["payout_wallet"])

    def test_malformed_wallet_is_a_500_not_a_report(self):
        with patch.dict(os.environ, {recall_api.PAYOUT_ENV: "0xnotawallet"}):
            status, _, text = self.get("/recall?product=Instant+Pot")
        self.assertEqual(status, 500)
        self.assertIn("misconfigured", text)


if __name__ == "__main__":
    unittest.main()
