"""Offline tests for tools/upc_lookup.py (issue #343).

The found, zero padded, blank fields and not found fixtures under
fixtures/openfoodfacts/ are REAL CAPTURES from the Open Food Facts API,
taken live for this issue with the tool's own fetch(); their provenance
(url, UTC retrieval time, HTTP status, sha256) is recorded beside them
and rechecked here. The not found capture arrived with HTTP 404
carrying the API's status 0 document; its status line comes from the
provenance record.

Derived bodies (a returned code that does not match the request, an
unknown status, a found document without a product) are labelled
DERIVED wherever they appear; documents with invented contents are
labelled SYNTHETIC. Fetch failure tests use fakes, so nothing here
touches the network.
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import upc_lookup as ul  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "openfoodfacts")
NUTELLA = "3017620422003"
UPC = "036000291452"
BLANK = "2000000000008"
NOT_FOUND = "5098765432100"


def _load(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as handle:
        return handle.read()


def _provenance():
    return json.loads(_load("provenance.json"))


def _replay(name):
    entry = _provenance()[name]
    return ul.Capture(entry["url"], entry["retrieved_utc"],
                      entry["status_line"], [], _load(name))


def _capture(body, status_line="HTTP/1.1 200 OK", url=None):
    return ul.Capture(url or ul.product_url(NUTELLA),
                      "2026-10-24T00:00:00Z", status_line, [], body)


class FixtureTests(unittest.TestCase):
    def test_fixtures_match_their_recorded_hashes(self):
        prov = _provenance()
        self.assertEqual(len(prov), 4)
        for name, entry in sorted(prov.items()):
            body = _load(name)
            self.assertEqual(
                hashlib.sha256(body.encode("utf-8")).hexdigest(),
                entry["sha256"], name)
            self.assertTrue(entry["url"].startswith("https://api.openfoodfacts.org/"), name)


class CheckCodeTests(unittest.TestCase):
    def test_check_digit_matches_the_gtin_rule(self):
        self.assertEqual(ul.check_digit("301762042200"), 3)
        self.assertEqual(ul.check_digit("03600029145"), 2)
        self.assertEqual(ul.check_digit("400638133393"), 1)

    def test_valid_codes_pass(self):
        for code in (NUTELLA, UPC, BLANK, NOT_FOUND, "4006381333931"):
            self.assertEqual(ul.check_code(code), code)
        self.assertEqual(ul.check_code("  %s " % NUTELLA), NUTELLA)

    def test_invalid_codes_are_refused_before_any_fetch(self):
        for bad in ("", "12345", "12345678901", "123456789012345",
                    "301762042200a", NUTELLA[:-1] + "4", None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                ul.check_code(bad)


class UrlTests(unittest.TestCase):
    def test_product_url_pins_the_host_the_path_and_the_fields(self):
        self.assertEqual(
            ul.product_url(NUTELLA),
            "https://api.openfoodfacts.org/api/v2/product/3017620422003.json"
            "?fields=product_name,brands,categories")
        self.assertEqual(ul.product_url(NUTELLA),
                         _provenance()["nutella-hit.body"]["url"])


class ReportTests(unittest.TestCase):
    def test_found_fixture_report(self):
        text = "\n".join(ul.report(NUTELLA, fetcher=lambda url: _replay("nutella-hit.body")))
        self.assertIn("# UPC lookup: 3017620422003", text)
        self.assertIn("- Code as shown: `3017620422003`", text)
        self.assertIn("- Product name (product_name) as listed: `Nutella`", text)
        self.assertIn("- Brand (brands) as listed: `Nutella, Ferrero`", text)
        self.assertIn("- Category (categories) as listed: `Confectionary", text)
        self.assertIn("Retrieved (UTC): " + _provenance()["nutella-hit.body"]["retrieved_utc"], text)
        self.assertIn(_load("nutella-hit.body"), text)

    def test_zero_padded_upc_is_the_same_code_stated_plainly(self):
        text = "\n".join(ul.report(UPC, fetcher=lambda url: _replay("upc-padded-hit.body")))
        self.assertIn("- The API returned the code zero padded as `0036000291452`", text)
        self.assertIn("- Code as shown: `0036000291452`", text)
        self.assertIn("`Alaska Peanut Butter - Creamy`", text)

    def test_blank_fields_are_reported_as_not_listed(self):
        text = "\n".join(ul.report(BLANK, fetcher=lambda url: _replay("blank-fields-hit.body")))
        self.assertIn("- Product name (product_name) as listed: `Pecorino biologico`", text)
        self.assertIn("- Brand (brands): not listed in the response", text)
        self.assertIn("- Category (categories): not listed in the response", text)

    def test_not_found_fixture_report(self):
        text = "\n".join(ul.report(NOT_FOUND, fetcher=lambda url: _replay("not-found.body")))
        self.assertIn("holds no product for barcode 5098765432100", text)
        self.assertIn(_load("not-found.body"), text)
        self.assertIn("HTTP/1.1 404 Not Found", text)

    def test_main_prints_the_not_found_report_and_exits_zero(self):
        out = io.StringIO()
        with mock.patch.object(ul, "fetch", return_value=_replay("not-found.body")):
            with contextlib.redirect_stdout(out):
                code = ul.main([NOT_FOUND])
        self.assertEqual(code, 0)
        self.assertIn("holds no product for barcode 5098765432100", out.getvalue())


class FailClosedTests(unittest.TestCase):
    # DERIVED bodies: the real Nutella and not found captures with the
    # returned code replaced by another valid barcode's code, so the
    # answer is about a different product than the one requested.
    def test_a_found_answer_for_a_different_code_is_refused(self):
        body = _load("nutella-hit.body").replace("3017620422003", "4006381333931")
        with self.assertRaises(ul.FetchError):
            ul.report(NUTELLA, fetcher=lambda url: _capture(body))

    def test_a_not_found_answer_for_a_different_code_is_refused(self):
        body = _load("not-found.body").replace("5098765432100", "6198765432106")
        with self.assertRaises(ul.FetchError):
            ul.report(NOT_FOUND, fetcher=lambda url: _capture(
                body, "HTTP/1.1 404 Not Found", ul.product_url(NOT_FOUND)))

    # SYNTHETIC documents, invented to pin the shape gates.
    def test_unknown_status_is_refused(self):
        body = '{"code":"3017620422003","status":2,"status_verbose":"?"}'
        with self.assertRaises(ul.FetchError):
            ul.report(NUTELLA, fetcher=lambda url: _capture(body))

    def test_found_document_without_a_product_is_refused(self):
        body = '{"code":"3017620422003","status":1,"status_verbose":"product found"}'
        with self.assertRaises(ul.FetchError):
            ul.report(NUTELLA, fetcher=lambda url: _capture(body))

    def test_found_document_on_a_404_is_refused(self):
        with self.assertRaises(ul.FetchError):
            ul.report(NUTELLA, fetcher=lambda url: _capture(
                _load("nutella-hit.body"), "HTTP/1.1 404 Not Found"))

    def test_non_json_is_refused(self):
        with self.assertRaises(ul.FetchError):
            ul.report(NUTELLA, fetcher=lambda url: _capture("not json"))

    def test_failed_fetch_exits_two_and_never_claims_not_found(self):
        def boom(url):
            raise ul.FetchError("fetch failed for %s" % (url,))

        err = io.StringIO()
        with mock.patch.object(ul, "fetch", side_effect=boom):
            with contextlib.redirect_stderr(err):
                code = ul.main([NOT_FOUND])
        self.assertEqual(code, 2)
        self.assertNotIn("holds no product", err.getvalue())


class _Answer:
    """A fake urllib response for fetch tests."""

    def __init__(self, body, status=200, reason="OK", final_url=None):
        self._body = body.encode("utf-8")
        self.status = status
        self.reason = reason
        self.version = 11
        self.headers = {"Content-Type": "application/json"}
        self._final_url = final_url

    def read(self):
        return self._body

    def geturl(self):
        return self._final_url

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _Opener:
    def __init__(self, behavior):
        self._behavior = behavior

    def open(self, request, timeout=None):
        return self._behavior(request)


class FetchTests(unittest.TestCase):
    def _fetch_with(self, behavior):
        opener = _Opener(behavior)
        with mock.patch.object(ul.urllib.request, "build_opener", return_value=opener):
            return ul.fetch(ul.product_url(NUTELLA))

    def test_200_is_captured_whole(self):
        cap = self._fetch_with(lambda req: _Answer('{"status": 1}', final_url=req.full_url))
        self.assertEqual(cap.status, 200)
        self.assertEqual(cap.body, '{"status": 1}')
        self.assertIn("HTTP/1.1 200 OK", cap.transcript())

    def test_404_is_captured_for_the_reader_to_judge(self):
        def behavior(req):
            raise urllib.error.HTTPError(
                req.full_url, 404, "Not Found",
                {"Content-Type": "application/json"},
                io.BytesIO(b'{"code":"3017620422003","status":0}'))

        cap = self._fetch_with(behavior)
        self.assertEqual(cap.status, 404)
        self.assertIn('"status":0', cap.body)

    def test_other_http_errors_are_fatal(self):
        def behavior(req):
            raise urllib.error.HTTPError(
                req.full_url, 500, "Server Error", {}, io.BytesIO(b""))

        with self.assertRaises(ul.FetchError):
            self._fetch_with(behavior)

    def test_transport_failure_is_fatal(self):
        def behavior(req):
            raise urllib.error.URLError("no route")

        with self.assertRaises(ul.FetchError):
            self._fetch_with(behavior)

    # SYNTHETIC redirect targets: the example.net URLs below are
    # invented to pin the off host refusal; no request is made to them.
    def test_redirect_off_the_host_is_refused(self):
        handler = ul._NoRedirect()
        with self.assertRaises(ul.FetchError):
            handler.redirect_request(None, None, 302, "Found", {},
                                     "https://example.net/api/v2/product/x.json")  # SYNTHETIC example host

    def test_a_final_url_off_the_host_is_refused(self):
        with self.assertRaises(ul.FetchError):
            self._fetch_with(lambda req: _Answer("{}", final_url="https://example.net/x"))  # SYNTHETIC example host


class RouteTests(unittest.TestCase):
    def setUp(self):
        from api import endpoints, recall_api
        self.endpoints = endpoints
        self.recall_api = recall_api

    def _get(self, qs, fetch_impl):
        # api/endpoints.py imports the tool as tools.upc_lookup, its own
        # module object, so the patch lands on endpoints.ul.
        with mock.patch.object(self.endpoints.ul, "fetch", fetch_impl):
            return self.recall_api.handle("GET", "/upc", qs, None)

    @staticmethod
    def _text(body):
        return body.decode() if isinstance(body, bytes) else body

    def test_route_reports_the_found_fixture(self):
        status, _, body = self._get(
            "code=3017620422003", lambda url: _replay("nutella-hit.body"))
        self.assertEqual(status, "200 OK")
        self.assertIn("# UPC lookup: 3017620422003", self._text(body))
        self.assertIn("`Nutella`", self._text(body))

    def test_route_reports_the_not_found_fixture_as_a_200(self):
        status, _, body = self._get(
            "code=5098765432100", lambda url: _replay("not-found.body"))
        self.assertEqual(status, "200 OK")
        self.assertIn("holds no product for barcode 5098765432100", self._text(body))

    def test_route_answers_400_for_bad_queries_without_fetching(self):
        def no_fetch(url):
            raise AssertionError("no fetch expected")

        for query in ("", "code=", "code=12345", "code=3017620422004",
                      "code=3017620422003&code=036000291452"):
            status, _, body = self._get(query, no_fetch)
            self.assertEqual(status, "400 Bad Request", query)
            self.assertIn("Bad request", self._text(body))

    def test_route_answers_502_when_the_fetch_fails(self):
        def boom(url):
            raise self.endpoints.ul.FetchError("fetch failed")

        status, _, _ = self._get("code=3017620422003", boom)
        self.assertEqual(status, "502 Bad Gateway")

    def test_descriptor(self):
        desc = self.endpoints.describe()["/upc"]
        self.assertEqual(desc["tool"], "tools/upc_lookup.py")
        self.assertTrue(desc["sources"][0].startswith("https://api.openfoodfacts.org/"))
        self.assertIn("code", desc["params"][0])


if __name__ == "__main__":
    unittest.main()
