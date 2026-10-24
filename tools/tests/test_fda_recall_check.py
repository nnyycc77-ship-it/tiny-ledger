"""Tests for tools/fda_recall_check.py and its GET /fda route (issue #177). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_fda_recall_check.py' -v

Fixtures (fixtures/fda-recall/, recorded in provenance.json): the
coordinator's four keyless openFDA captures on issue #177, each the
complete raw response (status line, CRLF headers, body), verbatim; every
SHA-256 matches the one posted. Variants built here from those responses
say DERIVED where they are built, and stand-ins say SYNTHETIC. Every test
runs with urlopen replaced by a function that fails the test, except the
fetch tests, which replace it with a fake.
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
import fda_recall_check as f  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "fda-recall"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
CASES = {("food", "peanut butter"): "food-hit.http", ("device", "catheter"): "device-hit.http",
         ("food", "zqxflorp"): "food-empty-404.http"}


def captured(name, module=f, url=None, body=None):
    head, _, raw_body = (FIX / name).read_bytes().decode("utf-8").partition("\r\n\r\n")
    lines = head.split("\r\n")
    headers = [tuple(line.split(": ", 1)) for line in lines[1:]]
    return module.Capture(url or PROV[name]["url"], "2026-10-24T04:40:00Z", int(lines[0].split(" ")[1]), lines[0],
                          headers, raw_body if body is None else body)


def replay(module=f, limit=3, bodies=None):
    """Answers the captured searches (and any URL in bodies, as DERIVED text over a capture)."""
    bodies = bodies or {}

    def fetcher(url):
        if url in bodies:
            name, body = bodies[url]
            return captured(name, module, url, body)
        for (category, term), name in CASES.items():
            if url == module.search_url(category, "product_description", term, limit):
                return captured(name, module)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("fda_recall_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = f.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_the_posted_ones(self):
        # Complete-response sha256 values exactly as the coordinator posted them on issue #177.
        posted_sha256 = {
            "food-hit response sha256": "95f8a7a8632c71587a2dc9137799ee59e7edddf19d01b175683fb2c402ae93b7",
            "device-hit response sha256": "a8a52b1c2d09ca2facf36b04e39f2c8cb0df6315dad46c7fa83642e6a429cb58",
            "food-empty-404 response sha256": "9973a48c66dd48a40b6ca2543812f4b2b8046ec4b6eb81c051ac53fefaf7934b",
            "food-error-500 response sha256": "7078bd94f756cdce96bd1a6852e46d7e8ef7d78d97f6f10e943d1a6dee4c94a8",
        }
        for key, sha in posted_sha256.items():
            name = key.replace(" response sha256", ".http")
            data = (FIX / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha, name)
            self.assertEqual(PROV[name]["sha256"], sha)
            self.assertEqual(hashlib.sha256(data.partition(b"\r\n\r\n")[2]).hexdigest(), PROV[name]["body_sha256"])

    def test_urls_are_the_captured_ones_byte_for_byte(self):
        for (category, term), name in CASES.items():
            self.assertEqual(f.search_url(category, "product_description", term, 3), PROV[name]["url"])


class HitTests(unittest.TestCase):
    def test_food_hit_lists_records_verbatim(self):
        code, out, err = run(["peanut butter", "--category", "food", "--limit", "3"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("openFDA reports 606 matching food enforcement records (meta.results.total as shown); "
                      "the first 3 are listed below", out)
        self.assertIn("#### 1. F-2473-2016, Class I", out)
        self.assertIn('- product_description: `"1.5 oz PEANUT BUTTER COOKIES, 80/case"`', out)
        self.assertIn('- recalling_firm: `"Savory Foods, Inc."`', out)
        self.assertIn('- status: `"Terminated"`', out)
        self.assertIn('- recall_initiation_date: `"20160211"`', out)
        self.assertIn('- report_date: `"20161012"`', out)
        self.assertIn('- termination_date: `"20161028"`', out)
        self.assertIn("#### 3. F-0426-2013, Class I", out)
        self.assertIn("Exact query: GET %s" % PROV["food-hit.http"]["url"], out)
        self.assertIn("Sent keyless (no api_key).", out)
        self.assertIn(captured("food-hit.http").transcript(), out)
        self.assertIn("Matched records, raw from the response:\n```\n{\n      \"status\": \"Terminated\"", out)
        self.assertEqual(out.count('"recall_number": "F-0718-2019"'), 2)  # the matched raw row, and the transcript

    def test_device_hit_shows_an_ongoing_recall_without_termination_date(self):
        _, out, _ = run(["catheter", "--category", "device", "--limit", "3"])
        self.assertIn("openFDA reports 2634 matching device enforcement records", out)
        self.assertIn("#### 1. Z-2372-2023, Class I", out)
        self.assertIn('- status: `"Ongoing"`', out)
        first = out[out.index("#### 1."):out.index("#### 2.")]
        self.assertIn("- termination_date: not in the record", first)
        self.assertIn("#### 2. Z-0272-2021, Class II", out)

    def test_both_categories_by_default(self):
        # DERIVED: the captured food empty answer stands in for the device search's answer.
        _, out, _ = run(["zqxflorp", "--limit", "3"], replay(bodies={
            f.search_url("device", "product_description", "zqxflorp", 3): ("food-empty-404.http", None)}))
        self.assertIn("## Food enforcement:", out)
        self.assertIn("## Device enforcement:", out)

    def test_all_listed_when_the_total_fits(self):
        # DERIVED: the food capture with meta.results.total changed to 3.
        url = f.search_url("food", "product_description", "peanut butter", 3)
        body = captured("food-hit.http").body.replace('"total": 606', '"total": 3')
        _, out, _ = run(["peanut butter", "--category", "food", "--limit", "3"],
                        replay(bodies={url: ("food-hit.http", body)}))
        self.assertIn("3 matching food enforcement records (meta.results.total as shown); all are listed", out)


class EmptyTests(unittest.TestCase):
    def test_404_not_found_is_the_proven_empty_result_never_a_clearance(self):
        code, out, err = run(["zqxflorp", "--category", "food", "--limit", "3"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("No food enforcement record matched. openFDA answered HTTP/1.1 404 Not Found with error code "
                      "NOT_FOUND", out)
        self.assertIn("not a clearance", out)
        self.assertIn('"message": "No matches found!"', out)
        self.assertIn(captured("food-empty-404.http").transcript(), out)
        self.assertNotIn("####", out)

    def test_a_404_without_not_found_is_a_failure(self):
        # DERIVED: the empty capture with its error code changed.
        url = f.search_url("food", "product_description", "zqxflorp", 3)
        body = captured("food-empty-404.http").body.replace("NOT_FOUND", "SOMETHING_ELSE")
        code, out, err = run(["zqxflorp", "--category", "food", "--limit", "3"],
                             replay(bodies={url: ("food-empty-404.http", body)}))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("without the NOT_FOUND error code", err)


class FailureTests(unittest.TestCase):
    class Answer:  # SYNTHETIC response object around captured bytes
        def __init__(self, status, data, url, headers=(), reason="OK"):
            self.status, self.code, self.reason, self.version = status, status, reason, 11
            self._data, self._url, self.headers = data, url, dict(headers)

        def read(self):
            return self._data

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def test_the_captured_500_names_source_query_and_reason(self):
        cap = captured("food-error-500.http")

        def fake(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 500, "Internal Server Error", dict(cap.headers),
                                         io.BytesIO(cap.body.encode()))
        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(f.FetchError) as ctx:
                f.fetch(PROV["food-error-500.http"]["url"])
        msg = str(ctx.exception)
        self.assertIn("openFDA request %s answered HTTP/1.1 500 Internal Server Error" % PROV["food-error-500.http"]["url"],
                      msg)
        self.assertIn("SERVER_ERROR; Check your request and try again; [parse_exception]", msg)

    def test_the_captured_404_and_200_are_captures(self):
        for name in ("food-empty-404.http", "food-hit.http"):
            cap = captured(name)

            def fake(request, timeout=None, cap=cap):
                if cap.status == 404:
                    raise urllib.error.HTTPError(request.full_url, 404, "Not Found", dict(cap.headers),
                                                 io.BytesIO(cap.body.encode()))
                return self.Answer(200, cap.body.encode(), request.full_url, cap.headers)
            with mock.patch("urllib.request.urlopen", fake):
                got = f.fetch(cap.url)
            self.assertEqual((got.status, got.body), (cap.status, cap.body), name)

    def test_transport_failures_and_redirects_fail_closed(self):
        url = PROV["food-hit.http"]["url"]

        def reset(request, timeout=None):
            raise urllib.error.URLError("SYNTHETIC connection reset")
        for fake in (reset, lambda request, timeout=None: self.Answer(200, b"{}", "https://example.invalid/x"),
                     lambda request, timeout=None: self.Answer(206, b"{}", url)):
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(f.FetchError):
                    f.fetch(url)

    def test_a_failed_fetch_exits_2_and_is_never_empty(self):
        def broken(url):
            raise f.FetchError("openFDA request %s failed: SYNTHETIC connection reset; no report" % url)
        code, out, err = run(["peanut butter"], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection reset", err)

    def test_bodies_not_in_the_captured_shape_exit_2(self):
        url = f.search_url("food", "product_description", "peanut butter", 3)
        body = captured("food-hit.http").body
        for bad in (body.replace('"recall_number"', '"recall_number_x"'), body.replace('"total": 606', '"total": 1'),
                    body.replace('"meta"', '"meta_x"'), "<html>SYNTHETIC</html>"):  # DERIVED, then SYNTHETIC
            code, out, err = run(["peanut butter", "--category", "food", "--limit", "3"],
                                 replay(bodies={url: ("food-hit.http", bad)}))
            self.assertEqual((code, out), (2, ""))
            self.assertIn("no report", err)

    def test_bad_inputs_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for argv in (["a"], ["x" * 101], ['say "hi"'], ["a\\b"], ["ok", "--field", "brand"],
                     ["ok", "--category", "drug"], ["ok", "--limit", "0"], ["ok", "--limit", "101"]):
            self.assertEqual(run(argv, must_not)[0], 2, argv)

    def test_firm_search_uses_recalling_firm(self):
        self.assertEqual(f.search_url("device", "recalling_firm", "Covidien LP", 10),
                         "https://api.fda.gov/device/enforcement.json?search=recalling_firm:%22Covidien+LP%22&limit=10")


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.fda_recall_check, its own module object.
        with mock.patch.object(endpoints.fda, "fetch", replay(endpoints.fda)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/fda", qs, None)

    def test_route(self):
        status, _, text = self.get("name=peanut+butter&category=food&limit=3")
        self.assertEqual(status, "200 OK")
        text = text.decode() if isinstance(text, bytes) else text
        self.assertIn("#### 1. F-2473-2016, Class I", text)
        self.assertEqual(self.get("name=zqxflorp&category=food&limit=3")[0], "200 OK")
        for qs in ("", "name=a", "name=ok&category=drug", "name=ok&field=brand", "name=ok&limit=0", "name=ok&limit=x"):
            self.assertEqual(self.get(qs)[0], "400 Bad Request", qs)
        self.assertEqual(endpoints.describe()["/fda"]["sources"],
                         [f.API_URL.format(category=c) for c in f.CATEGORIES])

    def test_route_maps_a_failure_to_502(self):
        def refused(url):
            raise endpoints.fda.FetchError("SYNTHETIC 500; no report")
        with mock.patch.object(endpoints.fda, "fetch", refused):
            self.assertEqual(recall_api.handle("GET", "/fda", "name=peanut+butter", None)[0], "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
