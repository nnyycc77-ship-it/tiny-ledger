"""Tests for tools/ofac_sdn_check.py and its GET /ofac route (issue #160). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_ofac_sdn_check.py' -v

Fixtures (fixtures/ofac/, recorded in provenance.json): EXCERPTS of the
real SDN.CSV and ALT.CSV files, every line verbatim from the coordinator
captures on issue #160 (comments 6378275074 and 6378275367); the complete
files' size, line count and SHA-256 are in the provenance. Variants built
here from those lines say DERIVED where they are built. Every test runs
with urlopen replaced by a function that fails the test.
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
import ofac_sdn_check as o  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "ofac"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
SDN = (FIX / "sdn-excerpt.csv").read_bytes()
ALT = (FIX / "alt-excerpt.csv").read_bytes()
# The headers the coordinator's capture showed on the final 200 answer (comment 6378275074).
CAPTURED_HEADERS = [("Content-Type", "text/csv"), ("Last-Modified", "Wed, 21 Oct 2026 16:35:23 GMT")]


def download(url, data, headers=(), redirected=True):
    return o.Download(url, "2026-10-24T01:36:00Z", list(headers), data, redirected)


def replay(sdn=SDN, alt=ALT, headers=()):
    def fetcher(url):
        return download(url, sdn if url == o.SDN_URL else alt, headers)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("ofac_sdn_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = o.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_excerpts_match_provenance_and_name_the_complete_files(self):
        for name, data in (("sdn-excerpt.csv", SDN), ("alt-excerpt.csv", ALT)):
            self.assertEqual(hashlib.sha256(data).hexdigest(), PROV[name]["sha256"])
            self.assertTrue(PROV[name]["contents"].startswith("EXCERPT"))
        self.assertEqual(PROV["sdn-excerpt.csv"]["complete_file_as_retrieved"]["sha256"],
                         "96dade5a1cde8c9746937b4859ad75d8f2a34eed1a4046cc1f2240a830f70bda")
        self.assertEqual(len(SDN.decode().splitlines()), 32)


class MatchingTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(o.match_kind("banco nacional de cuba", "BANCO NACIONAL DE CUBA"), "exact")
        self.assertEqual(o.match_kind("Banco Nacional", "BANCO NACIONAL DE CUBA"), "contains")
        self.assertIsNone(o.match_kind("Banco Nac", "BANCO NACIONAL DE CUBA"))  # whole words only
        self.assertEqual(o.match_kind("CIMEX S.A.", "CIMEX, S.A."), "exact")
        self.assertEqual(o.match_kind("abbas abu", "ABBAS, Abu"), "exact")
        self.assertIsNone(o.match_kind("Abu Abbas", "ABBAS, Abu"))  # word order is not rearranged
        self.assertIsNone(o.match_kind("", "ANY"))

    def test_accent_folding(self):
        # Issue #251: accents fold where Unicode decomposition splits them
        # off, in both directions, where the old normalise turned them
        # into spaces (normalise("José Müller") was "jos m ller").
        self.assertEqual(o.normalise("José Müller"), "jose muller")
        self.assertEqual(o.match_kind("Jose Muller", "JOSÉ MÜLLER"), "exact")  # unaccented query, accented list name
        self.assertEqual(o.match_kind("José Müller", "JOSE MULLER"), "exact")  # the reverse
        self.assertEqual(o.match_kind("Jose", "JOSÉ GARCÍA"), "contains")
        self.assertEqual(o.match_kind("García", "GARCIA"), "exact")
        self.assertIsNone(o.match_kind("Jose Mulle", "JOSÉ MÜLLER"))  # whole words still required
        # The stated limit: a letter with no decomposition (ł) is not
        # folded; it still acts as a separator.
        self.assertEqual(o.normalise("Łukasz"), "ukasz")


class ReportTests(unittest.TestCase):
    def test_alias_match_prints_both_lines_verbatim(self):
        code, out, err = run(["National Bank of Cuba"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("### ENT_NUM 306: BANCO NACIONAL DE CUBA", out)
        self.assertIn("- Matched: exact match on the alias NATIONAL BANK OF CUBA", out)
        self.assertIn('306,"BANCO NACIONAL DE CUBA",-0- ,"CUBA",-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,"a.k.a. \'BNC\'."', out)
        self.assertIn('306,220,"aka","NATIONAL BANK OF CUBA",-0- ', out)
        self.assertIn("line 3 of the file as read", out)

    def test_contains_and_primary_matches_are_told_apart(self):
        _, out, _ = run(["Cimex"])
        self.assertIn("5 list entries matched Cimex: 1 with an exact match, 4 by contains match only.", out)
        self.assertIn("- Matched: exact match on the primary name CIMEX\n", out)
        for ent in ("536", "537", "551", "576"):
            self.assertIn("### ENT_NUM %s:" % ent, out)
        self.assertNotIn("### ENT_NUM 591:", out)  # CUBAEXPORT: "cimex" is not a whole word in it

    def test_individual_and_vessel_types_as_shown(self):
        _, out, _ = run(["Abbas Abu"])
        self.assertIn("- Type as shown (third column): individual", out)
        self.assertIn("ALT.CSV lines for ENT_NUM 2674", out)
        _, out, _ = run(["Mar Azul"])
        self.assertIn("- Type as shown (third column): vessel", out)
        self.assertIn("ALT.CSV has no line for ENT_NUM 4238.", out)

    def test_no_match_is_proven_by_the_files_as_read(self):
        code, out, _ = run(["zqxflorp holdings"])
        self.assertEqual(code, 0)
        self.assertIn("No primary name or alias matched zqxflorp holdings under the rule above. Checked: 32 SDN.CSV "
                      "entries (SHA-256 %s) and 4 ALT.CSV alias lines (SHA-256 %s)"
                      % (hashlib.sha256(SDN).hexdigest(), hashlib.sha256(ALT).hexdigest()), out)
        self.assertIn("File as read: %d bytes, SHA-256 %s, 32 lines" % (len(SDN), hashlib.sha256(SDN).hexdigest()), out)
        self.assertIn(o.RULE, out)
        self.assertIn("no match is not a sanctions clearance", out)

    def test_redirect_target_is_never_printed_and_headers_are(self):
        _, out, _ = run(["Cimex"], replay(headers=CAPTURED_HEADERS))
        self.assertIn("Answered through a redirect to a signed storage URL, not printed", out)
        self.assertIn("Last-Modified: Wed, 21 Oct 2026 16:35:23 GMT", out)
        self.assertNotIn("amazonaws", out)

    def test_long_result_lists_are_capped_and_counted(self):
        # DERIVED: 60 copies of a captured line with new ENT_NUMs.
        line = SDN.decode().splitlines()[6].split(",", 1)[1]  # "CIMEX",...
        sdn = "\n".join("%d,%s" % (90000 + i, line) for i in range(60)).encode() + b"\n"
        _, out, _ = run(["Cimex"], replay(sdn=sdn))
        self.assertIn("60 list entries matched", out)
        self.assertIn("The first 50, in file order, are listed; 10 more matched and are not listed.", out)
        self.assertEqual(out.count("\n### ENT_NUM "), 50)


class FailClosedTests(unittest.TestCase):
    def test_a_file_not_in_the_captured_shape_is_refused(self):
        for bad in (b"<html>maintenance</html>\n", b"", b"a,b\nc,d\ne,f\ng,h\n" + SDN):
            code, out, err = run(["Cimex"], replay(sdn=bad))
            self.assertEqual((code, out), (2, ""), bad[:20])
            self.assertIn("not in the captured shape", err)

    def test_a_failed_fetch_is_never_no_match(self):
        def broken(url):
            raise o.FetchError("request to %s failed: SYNTHETIC connection reset; no report" % url)
        code, out, err = run(["Cimex"], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection reset", err)

    def test_fetch_maps_http_errors_and_non_200(self):
        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", http_error):
            with self.assertRaises(o.FetchError):
                o.fetch(o.SDN_URL)

    def test_a_2xx_answer_that_is_not_200_is_refused(self):
        class Partial:  # SYNTHETIC response object: a 206 partial body
            status = 206
            headers = {"Content-Type": "text/csv"}

            def read(self):
                return SDN[:100]

            def geturl(self):
                return o.SDN_URL

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        with mock.patch("urllib.request.urlopen", lambda request, timeout=None: Partial()):
            with self.assertRaises(o.FetchError):
                o.fetch(o.SDN_URL)

    def test_short_names_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for name in ("", "ab", "a.b"):
            self.assertEqual(run([name], must_not)[0], 2, name)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.ofac_sdn_check, its own module object.
        with mock.patch.object(endpoints.ofac, "fetch", replay()), mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/ofac", qs, None)

    def test_route_serves_the_report_and_refuses_bad_queries(self):
        status, _, body = self.get("name=National+Bank+of+Cuba")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("### ENT_NUM 306: BANCO NACIONAL DE CUBA", text)
        self.assertEqual(self.get("")[0], "400 Bad Request")
        self.assertEqual(self.get("name=ab")[0], "400 Bad Request")
        self.assertEqual(self.get("name=a.b")[0], "400 Bad Request")
        self.assertIn("/ofac", endpoints.describe())
        self.assertEqual(endpoints.describe()["/ofac"]["sources"], [o.SDN_URL, o.ALT_URL])

    def test_route_maps_a_failed_fetch_to_502(self):
        def broken(url):
            raise endpoints.ofac.FetchError("SYNTHETIC failure; no report")
        with mock.patch.object(endpoints.ofac, "fetch", broken):
            status, _, _ = recall_api.handle("GET", "/ofac", "name=Cimex", None)
        self.assertEqual(status, "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
