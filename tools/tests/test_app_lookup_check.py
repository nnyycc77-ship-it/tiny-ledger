"""Tests for tools/app_lookup_check.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_app_lookup_check.py' -v

The fixtures in fixtures/app-lookup/ are real captures: the coordinator
retrieved both responses live on 2026-10-24 and posted them verbatim on
issue #167 (Option B); URLs, hashes and the stated retrieval time are in
fixtures/app-lookup/provenance.json. The #51 captures in
fixtures/brandcheck/ are reused for the parser's leading newline case.
Three inputs below are not recordings and are labelled where they
appear: a response with an empty results array (no capture holds one;
the search matches loosely), a response whose counts disagree, and two
malformed responses built to prove the tool fails closed.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app_lookup_check as al  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "app-lookup"
PROVENANCE = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
NIKE = "search-Nike-us-5.http"
ZQX = "search-zqxflorp-us-5.http"


def captured(name):
    meta = PROVENANCE[name]
    with open(FIX / name, encoding="utf-8", newline="") as fh:
        transcript = fh.read()
    head, _, body = transcript.partition("\n\n")
    lines = head.split("\n")
    return al.Capture(meta["url"], meta["retrieved_utc"], lines[0], lines[1:], body)


def serve(name):
    cap = captured(name)

    def fetch(url):
        if url != cap.url:
            raise AssertionError("no recorded capture for %s" % url)
        return cap
    return fetch


def report(name, term):
    return al.run(term, "us", 5, serve(name))


class Captures(unittest.TestCase):
    def test_fixtures_match_their_recorded_hashes_and_body_sizes(self):
        for name in (NIKE, ZQX):
            meta = PROVENANCE[name]
            raw = (FIX / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"], name)
            body = raw.decode("utf-8").partition("\n\n")[2].encode("utf-8")
            self.assertEqual(hashlib.sha256(body).hexdigest(), meta["body_sha256_as_posted"], name)
            self.assertEqual(len(body), meta["body_bytes"], name)

    def test_request_urls_reproduce_the_captured_requests(self):
        self.assertEqual(al.search_url("Nike", "us", 5), PROVENANCE[NIKE]["url"])
        self.assertEqual(al.search_url("zqxflorp", "us", 5), PROVENANCE[ZQX]["url"])

    def test_status_code_is_read_from_the_status_line_as_posted(self):
        cap = captured(NIKE)
        self.assertEqual(cap.status_line, "HTTP/1.1 HTTP/1.1 200 OK")
        self.assertEqual((cap.status, cap.status_text), (200, "200 OK"))


class NikeSearch(unittest.TestCase):
    def setUp(self):
        self.lines = report(NIKE, "Nike")
        self.body = captured(NIKE).body

    def test_counts_and_first_app_as_shown(self):
        self.assertIn("resultCount as shown: 5. Entries in the results array: 5.", self.lines)
        i = self.lines.index("### App 1 of 5")
        self.assertEqual(self.lines[i + 2:i + 8], [
            "- App name (trackName) as shown: `Nike: Engineered for Athletes`",
            "- Seller (sellerName) as shown: `Nike, Inc`",
            "- Average user rating (averageUserRating) as shown: `4.881750000000000255795384873636066913604736328125`",
            "- User rating count (userRatingCount) as shown: `1698620`",
            "- Store link (trackViewUrl) as shown: `https://apps.apple.com/us/app/nike-engineered-for-athletes/id1095459556?uo=4`",
            "- trackName equals the searched name, ignoring case and spacing: no.",
        ])

    def test_every_printed_value_is_a_literal_of_the_body(self):
        for line in self.lines[:self.lines.index("## Sources")]:
            if " as shown: `" in line:
                value = line.split(" as shown: `", 1)[1][:-1]
                self.assertTrue(json.dumps(value)[1:-1] in self.body or value in self.body, value)

    def test_exact_name_mark_is_mechanical(self):
        self.assertIn("Exact name matches among the returned apps: 0 of 5 (source S1).", self.lines)

    def test_complete_transcript_under_the_request_url(self):
        cap = captured(NIKE)
        start = self.lines.index("- Request URL: %s" % cap.url)
        fence = self.lines[start + 3]
        end = self.lines.index(fence, start + 4)
        self.assertEqual("\n".join(self.lines[start + 4:end]), cap.transcript)


class LooseMatch(unittest.TestCase):
    def test_invented_name_is_zero_exact_matches_not_an_empty_store(self):
        lines = report(ZQX, "zqxflorp")
        self.assertIn("resultCount as shown: 5. Entries in the results array: 5.", lines)
        self.assertIn("Exact name matches among the returned apps: 0 of 5 (source S1).", lines)
        self.assertIn("No returned app is named `zqxflorp`, ignoring case and spacing. The search matches "
                      "loosely: it returned 5 apps, and none of them carries the searched name (source S1). "
                      "This is a search observation, not proof that no such app exists.", lines)
        self.assertFalse(any("returned no apps" in line for line in lines))

    def test_issue_51_body_with_leading_newlines_parses(self):
        body = (Path(__file__).parent / "fixtures" / "brandcheck" / "itunes-search-zqxflorp.json").read_text(encoding="utf-8")
        self.assertTrue(body.startswith("\n\n\n"))
        # The #51 capture is body only; the status line and header here are test harness, not recorded.
        cap = al.Capture("https://itunes.apple.com/search?term=zqxflorp&entity=software&limit=2", "2026-10-23",
                         "HTTP/1.1 200 OK", ["Content-Type: text/javascript; charset=utf-8"], body)
        count, results = al.parse(cap)
        self.assertEqual((count, len(results)), (2, 2))


class BuiltInputs(unittest.TestCase):
    def built(self, body, status="HTTP/1.1 200 OK"):
        # Built inputs, not recordings; the URL is the captured Nike request.
        return al.Capture(PROVENANCE[NIKE]["url"], "2026-10-24T00:00:00Z", status, [], body)

    def test_empty_results_array_is_proven_by_the_transcript(self):
        # SYNTHETIC: no capture returns zero results for software searches.
        lines = al.render("Nike", "us", 5, self.built('{"resultCount":0,"results":[]}'))
        self.assertIn("The search returned no apps. The complete raw response is in source S1; this is a search "
                      "observation, not proof that no such app exists.", lines)
        self.assertIn('{"resultCount":0,"results":[]}', lines)

    def test_disagreeing_counts_are_stated(self):
        # SYNTHETIC: resultCount differs from the array length.
        lines = al.render("Nike", "us", 5, self.built('{"resultCount":3,"results":[]}'))
        self.assertIn("resultCount as shown: 3. Entries in the results array: 0. The two differ; both are shown as "
                      "returned.", lines)

    def test_non_200_and_malformed_bodies_fail_closed(self):
        for cap in (self.built(captured(NIKE).body, "HTTP/1.1 503 Service Unavailable"),
                    self.built("<html>not json</html>"), self.built('{"results": {}}')):
            with self.assertRaises(al.FetchError):
                al.parse(cap)
            out, err = io.StringIO(), io.StringIO()
            original = al.fetch
            al.fetch = lambda url, cap=cap: cap
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = al.main(["Nike"])
            finally:
                al.fetch = original
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("fetch failed, nothing printed", err.getvalue())


class Inputs(unittest.TestCase):
    def test_input_rules(self):
        self.assertEqual(al.check_inputs("  Nike  Run ", "US", 200), ("Nike Run", "us", 200))
        for args in (("",), ("Nike", "usa"), ("Nike", "us", 0), ("Nike", "us", 201)):
            with self.assertRaises(ValueError, msg=args):
                al.check_inputs(*args)

    def test_cli_prints_the_report(self):
        out = io.StringIO()
        original = al.fetch
        al.fetch = serve(NIKE)
        try:
            with contextlib.redirect_stdout(out):
                code = al.main(["Nike", "--limit", "5"])
        finally:
            al.fetch = original
        self.assertEqual(code, 0)
        self.assertTrue(out.getvalue().startswith("## App search: Nike\n"))


if __name__ == "__main__":
    unittest.main()
