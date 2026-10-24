"""Tests for tools/meta_tag_check.py and its GET /meta route (issue #165). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_meta_tag_check.py' -v

Fixtures (fixtures/meta-tags/, recorded in provenance.json): three live
captures taken with this tool's own fetch path and User-Agent on
2026-10-24: ogp.me (title, description and Open Graph tags present),
example.com (title only; description and every Open Graph tag missing),
and httpbin.org/html (an HTML page whose head is empty, so every checked
tag is missing). Each fixture is the response's header block and its
body, verbatim, and the hashes in provenance.json are checked here.
Failure shapes are built in place from those captures or from a mocked
urlopen and say SYNTHETIC or DERIVED where they are built. Every test
runs with urlopen replaced by a function that fails the test, except the
fetch tests, which replace it with a recorder.
"""

import hashlib
import io
import json
import re
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import meta_tag_check as m  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "meta-tags"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
CASES = {"https://ogp.me/": "ogp-hit", "https://example.com/": "example-partial",
         "https://httpbin.org/html": "httpbin-empty"}


def captured(name, module=m):
    block = (FIX / ("%s.headers" % name)).read_text(encoding="utf-8").split("\n")
    status_line, headers = block[0], [tuple(line.split(": ", 1)) for line in block[1:] if line]
    status = int(re.findall(r" (\d{3}) ", status_line + " ")[0])
    url = PROV["%s.body" % name]["url"]
    return module.Capture(url, PROV["%s.body" % name]["final_url"], PROV["%s.body" % name]["retrieved_utc"],
                          status, status_line, headers,
                          (FIX / ("%s.body" % name)).read_text(encoding="utf-8"))


def replay(module=m):
    def fetcher(url):
        if url in CASES:
            return captured(CASES[url], module)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("meta_tag_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = m.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_and_bytes_match_provenance(self):
        for key, entry in PROV.items():
            data = (FIX / key).read_bytes()
            self.assertEqual(len(data), entry["bytes"], key)
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"], key)


class ReportTests(unittest.TestCase):
    def test_hit_page_all_checked_tags_present(self):
        code, out, err = run(["https://ogp.me/"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("- Title: present, as shown: The Open Graph protocol", out)
        self.assertIn('Description (meta name="description"): present, as shown: '
                      "The Open Graph protocol enables any web page to become a rich object "
                      "in a social graph.", out)
        self.assertIn("  - og:title: present, as shown: Open Graph protocol", out)
        self.assertIn("  - og:type: present, as shown: website", out)
        self.assertIn("  - og:url: present, as shown: https://ogp.me/", out)
        self.assertIn("  - og:image: present, as shown: https://ogp.me/logo.png", out)
        self.assertIn("  - og:description: present, as shown: The Open Graph protocol enables", out)
        self.assertIn("  - og:image:width: 300", out)  # a further og tag, listed as also present
        self.assertIn('<meta property="og:title" content="Open Graph protocol">', out)
        self.assertIn((FIX / "ogp-hit.body").read_text(encoding="utf-8"), out)
        self.assertIn("Retrieved (UTC): %s" % PROV["ogp-hit.body"]["retrieved_utc"], out)

    def test_partial_page_title_only(self):
        # Fixture case: the example.com capture in fixtures/meta-tags/ (title only).
        code, out, _ = run(["https://example.com/"])
        self.assertEqual(code, 0)
        self.assertIn("- Title: present, as shown: Example Domain", out)
        self.assertIn('Description (meta name="description"): missing', out)
        for key in m.CHECKED_OG:
            self.assertIn("  - %s: missing" % key, out)
        self.assertIn("- Further Open Graph tags: none present", out)
        self.assertNotIn("None of the checked tags are present", out)

    def test_empty_page_every_checked_tag_missing_is_a_report(self):
        code, out, err = run(["https://httpbin.org/html"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("- Title: missing", out)
        self.assertIn('Description (meta name="description"): missing', out)
        for key in m.CHECKED_OG:
            self.assertIn("  - %s: missing" % key, out)
        self.assertIn("None of the checked tags are present on this page.", out)
        self.assertIn((FIX / "httpbin-empty.body").read_text(encoding="utf-8"), out)

    def test_a_non_html_answer_is_refused_not_reported_as_empty(self):
        # DERIVED: the hit capture with only its Content-Type changed.
        cap = captured("ogp-hit")
        cap.headers = [(k, "text/plain" if k.lower() == "content-type" else v) for k, v in cap.headers]
        code, out, err = run(["https://ogp.me/"], lambda url: cap)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("not an HTML page; no report", err)

    def test_bad_urls_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        # Example inputs, all refused before any fetch; the example.com strings are synthetic.
        for bad in ("", "notaurl", "ftp://example.com/", "https://", "https://exa mple.com/", "example.com"):
            self.assertEqual(run([bad], must_not)[0], 2, bad)


class FetchTests(unittest.TestCase):
    class Answer:
        def __init__(self, status, body, url, headers=()):
            self.status, self.code = status, status
            self.reason = {200: "OK", 301: "Moved Permanently"}.get(status, "X")
            self._body, self._url, self.headers = body, url, dict(headers)
            self.version = 11

        def read(self, n=-1):
            return self._body if n is None or n < 0 else self._body[:n]

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def test_fetch_decodes_the_declared_charset(self):
        body = "<html><head><title>café</title></head></html>".encode("iso-8859-1")
        def fake(request, timeout=None):
            return self.Answer(200, body, request.full_url,
                               {"Content-Type": "text/html; charset=iso-8859-1"})
        with mock.patch("urllib.request.urlopen", fake):
            cap = m.fetch("https://example.com/")
        self.assertIn("café", cap.body)
        self.assertEqual(cap.status, 200)

    def test_source_failures_fail_closed(self):
        # SYNTHETIC answers: an HTTP error, a transport failure, and a non 200 status.
        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 500, "Server Error", {}, io.BytesIO(b"{}"))
        def transport(request, timeout=None):
            raise urllib.error.URLError("SYNTHETIC no route")
        def moved(request, timeout=None):
            return self.Answer(301, b"", request.full_url)
        for fake in (http_error, transport, moved):
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(m.FetchError):
                    m.fetch("https://example.com/")

    def test_main_maps_a_source_failure_to_exit_2_with_no_report(self):
        def refused(url):
            raise m.FetchError("SYNTHETIC 500; no report")
        code, out, err = run(["https://example.com/"], refused)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC 500; no report", err)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.meta_tag_check, its own module object.
        with mock.patch.object(endpoints.mt, "fetch", replay(endpoints.mt)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/meta", qs, None)

    def test_route(self):
        status, _, body = self.get("url=https%3A%2F%2Fogp.me%2F")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("- Title: present, as shown: The Open Graph protocol", text)
        self.assertEqual(self.get("url=https%3A%2F%2Fhttpbin.org%2Fhtml")[0], "200 OK")
        self.assertEqual(self.get("")[0], "400 Bad Request")
        self.assertEqual(self.get("url=notaurl")[0], "400 Bad Request")
        self.assertEqual(self.get("url=https%3A%2F%2Fa.example%2F&url=https%3A%2F%2Fb.example%2F")[0],
                         "400 Bad Request")
        self.assertEqual(endpoints.describe()["/meta"]["tool"], "tools/meta_tag_check.py")

    def test_route_maps_a_source_failure_to_502(self):
        def refused(url):
            raise endpoints.mt.FetchError("SYNTHETIC 500; no report")
        with mock.patch.object(endpoints.mt, "fetch", refused):
            self.assertEqual(recall_api.handle("GET", "/meta", "url=https%3A%2F%2Fexample.com%2F", None)[0],
                             "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
