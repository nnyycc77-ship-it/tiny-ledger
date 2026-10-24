"""Tests for tools/epa_screen.py (issue #178). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_epa_screen.py' -v

Fixtures: fixtures/epa-echo/*.http are real, keyless responses from the live
EPA ECHO facility search web service, captured by the coordinator under
Option B on issue #178 (this container cannot reach echodata.epa.gov) and
posted byte for byte. Each file is curl output as saved: the proxy's
CONNECT reply line, then the response status line and headers with CRLF
line ends, a blank line, then the body. Each one's URL, comment, body size
and SHA-256, and the whole file's SHA-256, are in fixtures/epa-echo/
provenance.json; both hashes are checked here. The files are read as bytes,
so the CRLF line ends stay as recorded.

A fake fetch serves each fixture for the exact URL it was captured from and
fails the test on any other URL.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import epa_screen as ep  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "epa-echo"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RETRIEVED = "2026-10-24T05:10:25Z"  # test value; the captures' own times are in provenance.json

SEARCH_HIT = "search-baytown-olefins.http"
ROWS_HIT = "qid-baytown-olefins.http"
SEARCH_CLEAN = "search-bissonnet-exxon.http"
ROWS_CLEAN = "qid-bissonnet.http"
SEARCH_EMPTY = "search-empty.http"
SEARCH_BAD_STATE = "facilities-bad-state.http"
DFR_500 = "dfr-baytown.http"
BY_ID_ERROR = "facilities-by-id.http"


def raw(name):
    return (FIXTURES / name).read_bytes().decode("utf-8")


def body_of(text):
    """The body: everything after the response's own header block."""
    return text.split("\r\n\r\n", 2)[2]


def capture(name):
    text = raw(name)
    return RETRIEVED, text, body_of(text)


def served(*names, as_url=None):
    """A fetch serving each fixture for its captured URL (or for as_url)."""
    mapping = {(as_url or PROVENANCE[n]["url"]): n for n in names}

    def fetch(url):
        if url not in mapping:
            raise AssertionError("unexpected fetch: %s" % url)
        return capture(mapping[url])
    return fetch


def report(name, state, city=None, registry_id=None, fetch=None):
    with patch.object(ep, "fetch", fetch):
        return "\n".join(ep.run(name, state, city, registry_id))


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.glob("*.http")))
        for name, entry in PROVENANCE.items():
            data = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"], name)
            body = body_of(data.decode("utf-8")).encode("utf-8")
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry["body_sha256"], name)
            self.assertEqual(len(body), entry["body_bytes"], name)

    def test_the_tool_builds_each_captured_search_url(self):
        self.assertEqual(ep.search_url("BAYTOWN OLEFINS", "TX", "BAYTOWN"), PROVENANCE[SEARCH_HIT]["url"])
        self.assertEqual(ep.search_url("BISSONNET EXXON", "TX", "HOUSTON"), PROVENANCE[SEARCH_CLEAN]["url"])
        self.assertEqual(ep.search_url("ZQXFLORP INDUSTRIES", "TX"), PROVENANCE[SEARCH_EMPTY]["url"])
        self.assertEqual(ep.rows_url("126"), PROVENANCE[ROWS_HIT]["url"])
        self.assertEqual(ep.rows_url("158"), PROVENANCE[ROWS_CLEAN]["url"])

    def test_each_summary_names_the_query_id_its_rows_were_fetched_with(self):
        for search, rows in ((SEARCH_HIT, ROWS_HIT), (SEARCH_CLEAN, ROWS_CLEAN)):
            qid = json.loads(capture(search)[2])["Results"]["QueryID"]
            self.assertEqual(ep.rows_url(qid), PROVENANCE[rows]["url"])

    def test_status_line_skips_the_proxy_reply(self):
        self.assertEqual(ep.status_line(raw(SEARCH_HIT)), "HTTP/1.1 200 200")
        self.assertEqual(ep.status_line(raw(DFR_500)), "HTTP/1.1 500 Internal Server Error")
        self.assertEqual(ep.status_line("HTTP/1.1 200 OK\nContent-Type: x\n\n{}"), "HTTP/1.1 200 OK")


class Query(unittest.TestCase):
    def test_inputs(self):
        self.assertEqual(ep.check_query("  BAYTOWN   OLEFINS ", "tx", " baytown ", None),
                         ("BAYTOWN OLEFINS", "TX", "baytown", None))
        for bad in (("", "TX"), ("X", "Texas"), ("X", ""), ("X", "TX", None, "11000x")):
            with self.assertRaises(ValueError, msg=bad):
                ep.check_query(*bad)


class Hit(unittest.TestCase):
    def setUp(self):
        self.text = report("BAYTOWN OLEFINS", "TX", "BAYTOWN", fetch=served(SEARCH_HIT, ROWS_HIT))

    def test_answer_quotes_the_three_fields_of_every_row(self):
        rows = json.loads(capture(ROWS_HIT)[2])["Results"]["Facilities"]
        self.assertIn('QUERY: p_fn = BAYTOWN OLEFINS, p_cty = BAYTOWN, p_st = TX. The search answered QueryRows "4"',
                      self.text)
        self.assertIn("- BAYTOWN OLEFINS PLANT (RegistryID 110000463178, BAYTOWN, TX): FacComplianceStatus "
                      '"Significant Violation"; FacSNCFlg "Y"; FacQtrsWithNC "12"', self.text)
        self.assertIn("- EXXON - OLEFINS PLANT BAYTOWN (RegistryID 110052964315, TX): FacComplianceStatus "
                      '"Inactive"; FacSNCFlg "N"; FacQtrsWithNC "0"', self.text)
        self.assertEqual(self.text.count("): FacComplianceStatus "), len(rows))
        self.assertIn("These are 4 different facility records", self.text)

    def test_both_transcripts_sit_beneath_their_source_links(self):
        for name in (SEARCH_HIT, ROWS_HIT):
            self.assertIn("- Query URL: %s\n- Retrieved (UTC): %s\nExcerpt (complete raw HTTP response transcript"
                          % (PROVENANCE[name]["url"], RETRIEVED), self.text)
            self.assertIn("```\n%s\n```" % raw(name), self.text)


class RegistryFilter(unittest.TestCase):
    def test_selects_one_row(self):
        text = report("BAYTOWN OLEFINS", "TX", "BAYTOWN", "110000463178", fetch=served(SEARCH_HIT, ROWS_HIT))
        self.assertIn("rows filtered to RegistryID 110000463178", text)
        self.assertEqual(text.count("): FacComplianceStatus "), 1)
        self.assertIn('"Significant Violation"', text)
        self.assertNotIn("different facility records", text)

    def test_an_id_not_returned_is_said_so(self):
        text = report("BAYTOWN OLEFINS", "TX", "BAYTOWN", "999", fetch=served(SEARCH_HIT, ROWS_HIT))
        self.assertIn("ANSWER: RegistryID 999 is not among the 4 rows the search returned", text)


class NoViolation(unittest.TestCase):
    def test_row_states_no_violation_identified(self):
        text = report("BISSONNET EXXON", "TX", "HOUSTON", fetch=served(SEARCH_CLEAN, ROWS_CLEAN))
        self.assertIn('BISSONNET EXXON 62017 (RegistryID ', text)
        self.assertIn('FacComplianceStatus "No Violation Identified"; FacSNCFlg "N"', text)


class Empty(unittest.TestCase):
    def test_zero_rows_is_proven_and_never_called_clean(self):
        text = report("ZQXFLORP INDUSTRIES", "TX", fetch=served(SEARCH_EMPTY))
        self.assertIn("ANSWER: the service answered zero rows for these parameters", text)
        self.assertIn("it is not a finding that any facility is free of violations", text)
        self.assertIn("```\n%s\n```" % raw(SEARCH_EMPTY), text)
        self.assertNotIn("get_qid", text)

    def test_bad_state_answers_the_same_empty_shape(self):
        # The recorded p_st=ZZ search. check_query accepts any two letters, so
        # this reaches the service, and its zero rows stay an empty result.
        text = report("EXXON", "ZZ", fetch=served(SEARCH_BAD_STATE))
        self.assertIn('The search answered QueryRows "0"', text)
        self.assertIn("an unrecognised parameter can answer the same way", text)


class SourceFailure(unittest.TestCase):
    def test_http_500_is_a_failure(self):
        # Test arrangement: the recorded get_dfr 500 answer served as the
        # search response, to exercise the status check.
        url = ep.search_url("BAYTOWN OLEFINS", "TX")
        with self.assertRaises(ep.SourceFailed) as ctx:
            report("BAYTOWN OLEFINS", "TX", fetch=served(DFR_500, as_url=url))
        self.assertEqual(ctx.exception.status, "HTTP/1.1 500 Internal Server Error")
        self.assertIn("We could not process your query.", str(ctx.exception))

    def test_200_with_an_error_body_is_a_failure(self):
        # Test arrangement: the recorded HTTP 200 Error answer (get_facilities
        # with p_id) served as the search response.
        url = ep.search_url("BAYTOWN OLEFINS", "TX")
        with self.assertRaises(ep.SourceFailed) as ctx:
            report("BAYTOWN OLEFINS", "TX", fetch=served(BY_ID_ERROR, as_url=url))
        self.assertEqual(ctx.exception.status, "HTTP/1.1 200 200 (Results carries an Error)")
        self.assertIn("Queryset Limit would be exceeded", str(ctx.exception))


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "epa_screen.md"

    def test_page_quotes_the_tool_and_the_recorded_responses(self):
        page = self.PAGE.read_text(encoding="utf-8")
        text = report("BAYTOWN OLEFINS", "TX", "BAYTOWN", "110000463178", fetch=served(SEARCH_HIT, ROWS_HIT))
        claims = page.split("## What a report shows", 1)[1].split("Source: ", 1)[0]
        quoted = [q for line in claims.splitlines() if line.startswith("- `") for q in line[2:].split("`")[1::2]]
        self.assertGreaterEqual(len(quoted), 2)
        for q in quoted:
            self.assertIn(q, text)
        self.assertIn("Source: %s," % PROVENANCE[ROWS_HIT]["url"], page)
        self.assertIn("sha256 `%s`" % PROVENANCE[ROWS_HIT]["sha256"], page)

    def test_page_states_the_price(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)


class CommandLine(unittest.TestCase):
    def run_main(self, argv, fetch):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(ep, "fetch", fetch), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = ep.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_hit(self):
        code, out, _ = self.run_main(["--name", "BAYTOWN OLEFINS", "--city", "BAYTOWN", "--state", "TX"],
                                     served(SEARCH_HIT, ROWS_HIT))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("## Subject: BAYTOWN OLEFINS, BAYTOWN, TX\n"))

    def test_source_failure_prints_no_report(self):
        url = ep.search_url("BAYTOWN OLEFINS", "TX")
        code, out, err = self.run_main(["--name", "BAYTOWN OLEFINS", "--state", "TX"],
                                       served(DFR_500, as_url=url))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("source failure, nothing printed", err)

    def test_bad_input_fetches_nothing(self):
        def never(url):
            raise AssertionError("no fetch expected")
        code, out, _ = self.run_main(["--name", "X", "--state", "Texas"], never)
        self.assertEqual((code, out), (2, ""))

    def test_transport_failure_prints_no_report(self):
        def broken(url):
            raise urllib.error.URLError("connection refused (test)")
        code, out, err = self.run_main(["--name", "X", "--state", "TX"], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("fetch failed, nothing printed", err)


if __name__ == "__main__":
    unittest.main()
