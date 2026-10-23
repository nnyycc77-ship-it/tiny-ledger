"""Tests for tools/brand_name_checker.py. Standard library only, no network
beyond 127.0.0.1.

Run:  python3 -m unittest discover -s tools/tests -p 'test_brand_name_checker.py' -v

Fixtures (tools/tests/fixtures/brandcheck/), all captured live by the
coordinator on 2026-10-23 and posted on issue #51 (H3's environment could
not reach these hosts):

* REAL CAPTURE bodies, hash checked here against provenance.json:
  rdap-nike.com.json (RDAP 200 for nike.com), itunes-search-nike.json and
  itunes-search-zqxflorp.json (iTunes Search, limit 2).
* REAL STATUS RECORD: status-captures.json transcribes the coordinator's
  status table for the status-only legs (RDAP 404 for zqxflorp.com, X 200
  and 404, Instagram and TikTok 200 login walls). The local server below
  answers each route with the status recorded there.
* SYNTHETIC: every status-only response body the local server sends
  (the tool never reads them), the redirect hop, the hanging 404, and the
  error answers (503, transport failure). Their status lines and headers
  come from the local test server, not from the real hosts. Each is
  labelled where it is defined.
"""

import contextlib
import hashlib
import http.server
import io
import json
import re
import socketserver
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import brand_name_checker as bnc  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "brandcheck"
PROVENANCE = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
STATUS = {c["request"]: c for c in json.loads((FIX / "status-captures.json").read_text(encoding="utf-8"))["captures"]}
RDAP_NIKE = (FIX / "rdap-nike.com.json").read_text(encoding="utf-8")
ITUNES_NIKE = (FIX / "itunes-search-nike.json").read_text(encoding="utf-8")
ITUNES_ZQX = (FIX / "itunes-search-zqxflorp.json").read_text(encoding="utf-8")


def recorded(url):
    return STATUS[url]["status"]


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send(self, status, body=b"", ctype="text/plain", extra=()):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        for k, v in extra:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path
        # RDAP: redirect hop (SYNTHETIC, mirrors the recorded rdap.org -> verisign redirect).
        if p == "/rdap/domain/nike.com":
            return self.send(302, extra=[("Location", "/verisign/com/v1/domain/nike.com")])
        if p == "/verisign/com/v1/domain/nike.com":
            return self.send(recorded("https://rdap.org/domain/nike.com"), RDAP_NIKE.encode(), "application/rdap+json")
        if p in ("/rdap/domain/zqxflorp.com", "/rdap/domain/getzqxflorp.com", "/rdap/domain/zqxflorphq.com"):
            # Status from the recorded zqxflorp.com 404. SYNTHETIC hanging body: Content-Length promises
            # far more than is sent, so a reader that reads the 404 body would stall.
            self.send_response(recorded("https://rdap.org/domain/zqxflorp.com"))
            self.send_header("Content-Type", "application/rdap+json")
            self.send_header("Content-Length", "1000000")
            self.end_headers()
            self.wfile.write(b'{"errorCode":404')
            self.wfile.flush()
            time.sleep(3)
            return
        if p == "/rdap/domain/zqxflorpapp.com":
            return self.send(200, RDAP_NIKE.encode(), "application/rdap+json")  # SYNTHETIC reuse: a taken variation
        if p == "/rdap/domain/broken.com":
            return self.send(503, b"SYNTHETIC unavailable")
        if p == "/x/nike":
            return self.send(recorded("https://x.com/nike"), b"SYNTHETIC page", "text/html",
                             [("Set-Cookie", "guest_id=SYNTHETIC-cookie-value; Path=/")])
        if p in ("/x/zqxflorp", "/x/getzqxflorp", "/x/zqxflorphq", "/x/zqxflorpapp"):
            return self.send(recorded("https://x.com/zqxflorp"), b"SYNTHETIC page", "text/html")
        if p == "/ig/nike/":
            return self.send(recorded("https://www.instagram.com/nike/"), b"SYNTHETIC login wall", "text/html")
        if p == "/tt/@nike":
            return self.send(recorded("https://www.tiktok.com/@nike"), b"SYNTHETIC login wall", "text/html")
        if p == "/itunes/search?term=Nike&entity=software&limit=2":
            return self.send(200, ITUNES_NIKE.encode(), "text/javascript; charset=utf-8")
        if p == "/itunes/search?term=zqxflorp&entity=software&limit=2":
            return self.send(200, ITUNES_ZQX.encode(), "text/javascript; charset=utf-8")
        return self.send(404, b"SYNTHETIC unrouted")

    def log_message(self, *args):
        pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name, entry in PROVENANCE.items():
            if "sha256" not in entry:
                continue
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), entry["sha256"])

    def test_itunes_urls_reproduce_the_captured_requests(self):
        self.assertEqual(bnc.itunes_url("Nike", 2), PROVENANCE["itunes-search-nike.json"]["url"])
        self.assertEqual(bnc.itunes_url("zqxflorp", 2), PROVENANCE["itunes-search-zqxflorp.json"]["url"])


class Rules(unittest.TestCase):
    def r(self, status, error=None, body=None):
        return bnc.Result("u", "u", "t", None if status is None else "HTTP/1.1 %s X" % status, status, [], body, error)

    def test_domain_verdicts(self):
        self.assertEqual(bnc.domain_verdict(self.r(200, body="{}")), bnc.REGISTERED)
        self.assertEqual(bnc.domain_verdict(self.r(404)), bnc.NOT_REGISTERED)
        for s in (403, 429, 500, 503):
            self.assertEqual(bnc.domain_verdict(self.r(s)), bnc.UNCONFIRMED)
        self.assertEqual(bnc.domain_verdict(self.r(None, error="timed out")), bnc.UNCONFIRMED)

    def test_handle_verdicts_never_call_a_login_wall_available(self):
        self.assertEqual(bnc.handle_verdict("x", self.r(200)), bnc.LIVE)
        self.assertEqual(bnc.handle_verdict("x", self.r(404)), bnc.NO_ACCOUNT)
        for platform in ("instagram", "tiktok"):
            self.assertEqual(bnc.handle_verdict(platform, self.r(200)), bnc.UNCONFIRMED)
            self.assertEqual(bnc.handle_verdict(platform, self.r(404)), bnc.NO_ACCOUNT)
        for s in (None, 302, 429, 500):
            self.assertEqual(bnc.handle_verdict("x", self.r(s, error="x" if s is None else None)), bnc.UNCONFIRMED)

    def test_itunes_exact_match_on_real_captures(self):
        count, returned, exact = bnc.itunes_matches(ITUNES_NIKE, "Nike")
        self.assertEqual((count, returned), ("2", 2))
        self.assertEqual([e.value("trackName") for e in exact], ["Nike: Engineered for Athletes"])
        count, returned, exact = bnc.itunes_matches(ITUNES_ZQX, "zqxflorp")
        self.assertEqual((returned, exact), (2, []))  # loose matching: two unrelated apps, no exact match

    def test_title_part_cuts_at_the_first_subtitle_separator(self):
        self.assertEqual(bnc.title_part("Nike: Engineered for Athletes"), "Nike")
        self.assertEqual(bnc.title_part("Nike SNKRS: Sneakers & Apparel"), "Nike SNKRS")
        self.assertEqual(bnc.normalize("Nike SNKRS"), "nikesnkrs")


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % cls.server.server_port
        cls.saved = (bnc.RDAP_BASE, bnc.X_BASE, bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH)
        bnc.RDAP_BASE, bnc.X_BASE = base + "/rdap/domain/", base + "/x/"
        bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH = base + "/ig/", base + "/tt/@", base + "/itunes/search"

    @classmethod
    def tearDownClass(cls):
        bnc.RDAP_BASE, bnc.X_BASE, bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH = cls.saved
        cls.server.shutdown()
        cls.server.server_close()

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = bnc.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_taken_brand(self):
        code, out, err = self.run_main(["Nike", "--app-limit", "2"])
        self.assertEqual(code, 0, err)
        self.assertRegex(out, r"\| nike\.com \| registered \| HTTP/1\.\d 200 OK \| \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ \|")
        self.assertIn('"ldhName":"NIKE.COM"', out)
        self.assertIn('{"eventAction":"registration","eventDate":"1995-03-04T05:00:00Z"}', out)
        self.assertIn("(answered from http://127.0.0.1", out)
        self.assertRegex(out, r"\| x \| Nike \| taken \(live account\) \|")
        self.assertRegex(out, r"\| instagram \| Nike \| could not confirm \|")
        self.assertRegex(out, r"\| tiktok \| Nike \| could not confirm \|")
        self.assertIn("1 exact name match(es) among 2 result(s) returned", out)
        self.assertIn('"trackName":"Nike: Engineered for Athletes"', out)
        self.assertIn("Set-Cookie: [value not printed]", out)
        self.assertNotIn("SYNTHETIC-cookie-value", out)
        self.assertIn("Google Play: out of scope", out)
        self.assertIn("### Trademarks\n\nNot covered.", out)
        self.assertTrue(out.rstrip().endswith("Trademark results are a starting point, not legal advice.\n"
                                              "No searched name was registered or reserved by the agent."))

    def test_free_invented_name_and_404_body_never_read(self):
        start = time.monotonic()
        code, out, err = self.run_main(["zqxflorp", "--app-limit", "2", "--platforms", "x"])
        self.assertLess(time.monotonic() - start, 2.5, "a 404 body was read")
        self.assertEqual(code, 0, err)
        self.assertRegex(out, r"\| zqxflorp\.com \| no registration found \| HTTP 404 ")
        self.assertIn("[body not read: a 404 body is never read]", out)
        self.assertNotIn('{"errorCode":404', out)
        self.assertRegex(out, r"\| x \| zqxflorp \| no account found \| HTTP 404 ")
        self.assertIn("0 exact name match(es) among 2 result(s) returned", out)
        self.assertTrue(fences_end_with(out, ITUNES_ZQX), "empty app result not proven with the full raw response")

    def test_variations_listed_only_when_verified_free(self):
        code, out, err = self.run_main(["zqxflorp", "--app-limit", "2", "--platforms", "x", "--variations", "2"])
        self.assertEqual(code, 0, err)
        variations = out.split("### Variations", 1)[1]
        self.assertIn("- zqxflorphq: free on every checked domain (zqxflorphq.com) and on X.", variations)
        self.assertIn("- getzqxflorp: free on every checked domain", variations)
        self.assertNotIn("zqxflorpapp: free", variations)  # its domain answered 200

    def test_no_variations_unless_asked(self):
        code, out, _ = self.run_main(["zqxflorp", "--app-limit", "2", "--platforms", "x"])
        self.assertNotIn("### Variations", out)

    def test_failed_checks_are_could_not_confirm_never_available(self):
        code, out, err = self.run_main(["broken", "--app-limit", "2", "--platforms", "x"])
        self.assertEqual(code, 0, err)
        self.assertRegex(out, r"\| broken\.com \| could not confirm \| HTTP 503 ")
        saved = bnc.X_BASE
        bnc.X_BASE = "http://127.0.0.1:9/x/"
        try:
            code, out, err = self.run_main(["broken", "--app-limit", "2", "--platforms", "x"])
        finally:
            bnc.X_BASE = saved
        self.assertRegex(out, r"\| x \| broken \| could not confirm \| no response \(")
        self.assertNotIn("no account found", out)
        self.assertIn("App Store | could not confirm", out)

    def test_bad_inputs_exit_2_with_nothing_on_stdout(self):
        for argv in (["Nike", "--tlds", "c$m"], ["Nike", "--platforms", "myspace"], ["%%%"],
                     ["Nike", "--app-limit", "0"]):
            with self.subTest(argv=argv):
                code, out, _ = self.run_main(argv)
                self.assertEqual((code, out), (2, ""))


def fences_end_with(text, body):
    return any(b.endswith("\n\n" + body) for b in re.findall(r"^```+\n(.*?)\n```+$", text, re.S | re.M))


if __name__ == "__main__":
    unittest.main()
