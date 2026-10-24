"""Tests for tools/broken_link_check.py (issue #164). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_broken_link_check.py' -v

Fixtures (fixtures/broken-links/, recorded in provenance.json): the link
target responses and the no links page are real captures made by H7 with the
tool's own fetch path; page-with-dead.http is SYNTHETIC, a page body written
for this test so the link set is small and stable (it says so in an HTML
comment at the top of its body and in provenance.json). Every test runs with
urlopen replaced by a function that fails the test, except the fetch tests,
which replace it with a recorder.
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
import broken_link_check as bl  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "broken-links"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
RETRIEVED = "2026-10-24T04:55:23Z"
PAGE_URL = PROV["page-with-dead.http"]["url"]
NO_LINKS_URL = PROV["page-no-links.http"]["url"]
TARGET_FILES = {
    "https://example.com/": "link-example-com.http",
    "https://www.iana.org/domains/example": "link-iana-example.http",
    "https://example.com/no-such-page-broken-link-check": "link-example-com-404.http",
}


def captured(name):
    text = (FIX / name).read_text(encoding="utf-8")
    head, _, body = text.partition("\n\n")
    lines = head.split("\n")
    status = int(re.findall(r" (\d{3}) ", lines[0] + " ")[0])
    headers = [tuple(line.split(": ", 1)) for line in lines[1:] if line]
    entry = PROV[name]
    return bl.Capture(entry["url"], entry.get("final_url", entry["url"]), RETRIEVED,
                      status, lines[0], headers, body)


def replay(fail_for=()):
    pages = {PAGE_URL: "page-with-dead.http", NO_LINKS_URL: "page-no-links.http"}

    def fetcher(url, want_body=True):
        if url in fail_for:
            raise bl.FetchError("request to %s failed: simulated outage; no answer" % url)
        if url in pages:
            return captured(pages[url])
        if url in TARGET_FILES:
            return captured(TARGET_FILES[url])
        raise AssertionError("unexpected url %s" % url)

    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("broken_link_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = bl.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_and_bytes_match_provenance(self):
        for name, entry in PROV.items():
            if name == "_about":
                continue
            data = (FIX / name).read_bytes()
            self.assertEqual(len(data), entry["bytes"], name)
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"], name)

    def test_synthetic_page_is_labelled_where_it_appears(self):
        self.assertIn("SYNTHETIC", PROV["_about"])
        body = (FIX / "page-with-dead.http").read_text(encoding="utf-8").partition("\n\n")[2]
        self.assertTrue(body.startswith("<!-- SYNTHETIC PAGE"), body[:60])


class ReportTests(unittest.TestCase):
    def test_hit_a_dead_link_is_listed_with_its_status(self):
        # The fixture page and its recorded example targets.
        code, out, err = run([PAGE_URL])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("LINKS: 7 link(s) on the page; 3 unique HTTP target(s) checked, 1 same page "
                      "anchor(s) not fetched, 1 non HTTP link(s) not fetched, 0 target(s) past the "
                      "cap of 100 not checked.", out)
        self.assertIn("Dead links (final status 400 or above): 1", out)
        # The one dead fixture link, with its status:
        self.assertIn("- https://example.com/no-such-page-broken-link-check -> HTTP/1.1 404 Not Found",
                      out)
        # The duplicate and the relative spelling of the dead link are checked once:
        # the fixture dead link is listed once as dead and once in the full results.
        self.assertEqual(out.count("- https://example.com/no-such-page-broken-link-check -> "
                                   "HTTP/1.1 404 Not Found\n"), 1)
        self.assertEqual(out.count("no-such-page-broken-link-check -> HTTP/1.1 404 Not Found [dead]"), 1)
        # Every checked fixture link is listed with its status; the redirect is named.
        self.assertIn("- https://example.com/ -> HTTP/1.1 200 OK", out)
        self.assertIn("- https://www.iana.org/domains/example -> HTTP/1.1 200 OK "
                      "(redirected to http://www.iana.org/help/example-domains)", out)
        self.assertIn("- https://example.com/no-such-page-broken-link-check -> HTTP/1.1 404 Not "
                      "Found [dead]", out)
        # The unfetched kinds are accounted for, not dropped.
        self.assertIn("Same page anchors, not fetched: '#top'", out)
        self.assertIn("Non HTTP links, not fetched: 'mailto:someone@example.com'", out)
        # The page transcript is the proof, verbatim beneath the source link.
        self.assertIn("Source: <%s>" % PAGE_URL, out)
        self.assertIn((FIX / "page-with-dead.http").read_text(encoding="utf-8"), out)

    def test_empty_a_page_with_no_links_proves_it_with_the_full_page(self):
        code, out, err = run([NO_LINKS_URL])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("LINKS: 0 link(s) on the page; 0 unique HTTP target(s) checked", out)
        self.assertIn("Dead links (final status 400 or above): 0", out)
        self.assertIn("- None were checked; the page holds no HTTP link target", out)
        self.assertIn((FIX / "page-no-links.http").read_text(encoding="utf-8"), out)

    def test_link_check_failure_is_listed_as_a_failure_never_as_dead(self):
        code, out, _ = run([PAGE_URL], fetcher=replay(fail_for={"https://www.iana.org/domains/example"}))
        self.assertEqual(code, 0)
        self.assertIn("Check failures (the request itself failed; not counted as dead): 1", out)
        self.assertIn("- https://www.iana.org/domains/example -> request to "
                      "https://www.iana.org/domains/example failed: simulated outage; no answer", out)
        self.assertIn("Dead links (final status 400 or above): 1", out)
        self.assertNotIn("iana.org/domains/example -> HTTP", out)


class FailureTests(unittest.TestCase):
    def test_page_transport_failure_is_exit_2_with_no_report(self):
        def fetcher(url, want_body=True):
            raise bl.FetchError("request to %s failed: simulated outage; no answer" % url)

        code, out, err = run([PAGE_URL], fetcher=fetcher)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("simulated outage", err)

    def test_page_that_does_not_answer_200_is_exit_2_with_no_report(self):
        # The recorded example 404 response, served as the page itself.
        def fetcher(url, want_body=True):
            return captured("link-example-com-404.http")

        code, out, err = run(["https://example.com/no-such-page-broken-link-check"], fetcher=fetcher)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("answered HTTP/1.1 404 Not Found", err)
        self.assertIn("not an empty result", err)

    def test_bad_page_urls_are_refused_before_any_fetch(self):
        # Bad inputs, among them example URLs that must never be fetched.
        for bad in ["", "notaurl", "ftp://example.com/", "https://", "//example.com/"]:
            code, out, err = run([bad])
            self.assertEqual(code, 2, bad)
            self.assertEqual(out, "", bad)
            self.assertIn("page URL must be an http or https URL", err, bad)


class FetchTests(unittest.TestCase):
    """The real fetch path, with urlopen replaced by a recorder."""

    def test_fetch_records_status_headers_and_body_for_any_status(self):
        class Resp:
            status, code, version, reason = 404, 404, 11, "Not Found"
            headers = {"Content-Type": "text/html"}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            # The recorder's final URL, an example target that is missing.
            def geturl(self):
                return "https://example.com/missing"

            def read(self, n=-1):
                return b"<html>gone</html>"

        # A recorded style response for an example target that is missing.
        with mock.patch("urllib.request.urlopen", return_value=Resp()) as opened:
            cap = bl.fetch("https://example.com/missing")
        self.assertEqual(cap.status, 404)
        self.assertEqual(cap.status_line, "HTTP/1.1 404 Not Found")
        self.assertEqual(cap.body, "<html>gone</html>")
        request = opened.call_args[0][0]
        self.assertEqual(request.headers.get("User-agent"), bl.USER_AGENT)

    def test_fetch_transport_failure_raises_fetch_error(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused (test)")):
            with self.assertRaises(bl.FetchError):
                bl.fetch("https://example.com/")


if __name__ == "__main__":
    unittest.main()
