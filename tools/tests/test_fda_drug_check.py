"""Tests for tools/fda_drug_check.py (issue #163). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_fda_drug_check.py' -v

Fixtures: fixtures/openfda/*.http are two real, keyless responses from the
live openFDA drug label endpoint, captured by H6 in this environment on
issue #163 with the capture path of tools/nhtsa_recalls.py (this
environment can reach api.fda.gov): a hit (Tylenol, limit 1) and the
no match answer (HTTP 404, error code NOT_FOUND). Each one's URL,
retrieval time, body size and body SHA-256, and the whole file's SHA-256,
are in fixtures/openfda/provenance.json; both hashes are checked here.

The dosage form shapes are tested on small test bodies built in this
file, not recordings, and labelled as such where they appear: the
recorded Tylenol record carries neither a dosage_form field nor a
dosage_forms_and_strengths section, so no recorded body in this repo
shows those lines. The source failure shapes are tested the same way:
a mocked fetch raising URLError (transport failure) and a test body
that cannot be read as a label response. No source figure is invented:
the synthetic bodies below carry only the fields their tests name.
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
import fda_drug_check as fd  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "openfda"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RETRIEVED = "2026-10-24T05:00:08Z"  # test value; the captures' own times are in provenance.json

HIT = "tylenol-hit.http"
EMPTY = "no-match-404.http"

QUERIES = {  # fixture -> the name the capture was made with
    HIT: "Tylenol",
    EMPTY: "Zqxwvnotadrug",
}


def capture(name):
    """(retrieved, transcript, body) for a fixture, as fetch() returns them."""
    transcript = (FIXTURES / name).read_text(encoding="utf-8")
    return RETRIEVED, transcript, transcript.partition("\n\n")[2]


def section(name):
    drug = QUERIES[name]
    return "\n".join(fd.render_section(drug, fd.build_url(drug), *capture(name)))


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.glob("*.http")))
        for name, entry in PROVENANCE.items():
            raw = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], name)
            body = raw.split(b"\n\n", 1)[1]
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry["body_sha256"], name)
            self.assertEqual(len(body), entry["body_bytes"], name)

    def test_the_tool_builds_each_captured_url(self):
        for name, drug in QUERIES.items():
            self.assertEqual(fd.build_url(drug), PROVENANCE[name]["url"], name)


class Query(unittest.TestCase):
    def test_name_is_trimmed(self):
        self.assertEqual(fd.check_name("  Lipitor "), "Lipitor")
        self.assertEqual(fd.check_name("vitamin d3"), "vitamin d3")

    def test_bad_names_are_refused(self):
        for bad in ("", "   ", 'say "cheese"', "back\\slash", "line\nbreak", "x" * 101):
            with self.assertRaises(ValueError, msg=repr(bad)):
                fd.check_name(bad)

    def test_url_quotes_the_name(self):
        self.assertEqual(
            fd.build_url("vitamin d3"),
            "https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22vitamin%20d3%22"
            "+OR+openfda.generic_name:%22vitamin%20d3%22&limit=1")


class Render(unittest.TestCase):
    def test_hit_label_facts_as_shown(self):
        text = section(HIT)
        self.assertIn('QUERY: search = openfda.brand_name:"Tylenol" OR '
                      'openfda.generic_name:"Tylenol", limit = 1 answered HTTP/1.1 200 OK '
                      '(retrieved %s).' % RETRIEVED, text)
        self.assertIn("LABEL: first returned record of 109 matching label record(s) "
                      "(total as shown in the response).", text)
        self.assertIn("- brand_name as shown: TYLENOL Extra Strength", text)
        self.assertIn("- generic_name as shown: ACETAMINOPHEN", text)
        self.assertIn("- maker (openfda.manufacturer_name) as shown: Kenvue Brands LLC", text)
        self.assertIn("- product_type as shown: HUMAN OTC DRUG", text)
        self.assertIn("- route as shown: ORAL", text)
        self.assertIn("- warnings present: the record carries warnings.", text)
        self.assertIn("- effective_time as shown: 20241107", text)

    def test_hit_states_the_missing_dosage_form_plainly(self):
        # The recorded Tylenol record carries neither a dosage_form field
        # nor a dosage_forms_and_strengths section; the report says so
        # instead of filling the gap.
        text = section(HIT)
        self.assertIn("- dosage form: (not present in the API record: the record carries "
                      "neither a dosage_form field nor a dosage_forms_and_strengths section)", text)

    def test_no_match_is_proven_by_the_transcript(self):
        text = section(EMPTY)
        self.assertIn("answered HTTP/1.1 404 Not Found", text)
        self.assertIn('LABEL: no drug label record matched "Zqxwvnotadrug". The body\'s error '
                      'as shown: code "NOT_FOUND", message "No matches found!".', text)
        self.assertIn("```\n%s\n```" % capture(EMPTY)[1], text)

    def test_source_block_sits_directly_above_the_transcript(self):
        text = section(HIT)
        self.assertIn("### Source. openFDA drug label API (api.fda.gov/drug/label.json)\n"
                      "- Query URL: %s\n"
                      "- Retrieved (UTC): %s\nExcerpt (complete raw HTTP response transcript"
                      % (PROVENANCE[HIT]["url"], RETRIEVED), text)
        self.assertTrue(text.endswith("```\n%s\n```" % capture(HIT)[1]))

    def test_dosage_form_field_is_printed_as_shown(self):
        # A test body, not a recording: it carries only the fields named here.
        body = json.dumps({
            "meta": {"results": {"skip": 0, "limit": 1, "total": 1}},
            "results": [{"openfda": {"brand_name": ["TESTBRAND"],
                                     "manufacturer_name": ["Test Maker LLC"]},
                         "dosage_form": ["TABLET", "CAPSULE"],
                         "warnings": ["Keep out of reach of children."]}],
        })
        text = "\n".join(fd.render_section("Testbrand", fd.build_url("Testbrand"), RETRIEVED,
                                           "HTTP/1.1 200 OK\n\n" + body, body))
        self.assertIn("- dosage form as shown: TABLET, CAPSULE", text)
        self.assertIn("- warnings present: the record carries warnings.", text)

    def test_dosage_forms_and_strengths_section_is_quoted(self):
        # A test body, not a recording: it carries only the fields named here.
        body = json.dumps({
            "meta": {"results": {"skip": 0, "limit": 1, "total": 1}},
            "results": [{"openfda": {"brand_name": ["TESTBRAND"]},
                         "boxed_warning": ["A boxed warning."],
                         "dosage_forms_and_strengths": ["3 DOSAGE FORMS AND STRENGTHS Tablets: 10 mg."]}],
        })
        text = "\n".join(fd.render_section("Testbrand", fd.build_url("Testbrand"), RETRIEVED,
                                           "HTTP/1.1 200 OK\n\n" + body, body))
        self.assertIn("- dosage form: the record carries no dosage_form field; its "
                      "dosage_forms_and_strengths section as shown: "
                      "3 DOSAGE FORMS AND STRENGTHS Tablets: 10 mg.", text)
        self.assertIn("- warnings present: the record carries boxed_warning.", text)

    def test_no_warning_sections_is_stated(self):
        # A test body, not a recording: a record with no warning sections.
        body = json.dumps({
            "meta": {"results": {"skip": 0, "limit": 1, "total": 1}},
            "results": [{"openfda": {"brand_name": ["TESTBRAND"]}}],
        })
        text = "\n".join(fd.render_section("Testbrand", fd.build_url("Testbrand"), RETRIEVED,
                                           "HTTP/1.1 200 OK\n\n" + body, body))
        self.assertIn("- warnings present: none of the warning sections this tool checks "
                      "(boxed_warning, warnings, warnings_and_cautions) is present in the record.", text)
        self.assertIn("- maker (openfda.manufacturer_name) as shown: (not present in the API record)", text)

    def test_unreadable_body_keeps_the_transcript(self):
        body = "<html>error</html>"  # test body, not a recording
        transcript = "HTTP/1.1 502 Bad Gateway\n\n" + body
        text = "\n".join(fd.render_section("Lipitor", fd.build_url("Lipitor"),
                                           RETRIEVED, transcript, body))
        self.assertIn("LABEL: not determinable from this response", text)
        self.assertIn(body, text)


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "fda_drug_check.md"

    def test_page_quotes_the_tool_and_the_recorded_response(self):
        page = self.PAGE.read_text(encoding="utf-8")
        text = section(HIT)
        claims = page.split("## What a report shows", 1)[1].split("Source: ", 1)[0]
        quoted = [q for line in claims.splitlines() if line.startswith("- `") for q in line[2:].split("`")[1::2]]
        self.assertGreaterEqual(len(quoted), 3)
        for q in quoted:
            self.assertIn(q, text)
        entry = PROVENANCE[HIT]
        self.assertIn("Source: %s," % entry["url"], page)
        self.assertIn("```text\n%s\n```" % capture(HIT)[1], page)

    def test_page_states_the_shelf_price(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)


class CommandLine(unittest.TestCase):
    def run_main(self, argv, fetch):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(fd, "fetch", fetch), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = fd.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_one_fetch_of_the_exact_url(self):
        urls = []

        def fake(url):
            urls.append(url)
            return capture(HIT)
        code, out, _ = self.run_main(["Tylenol"], fake)
        self.assertEqual(code, 0)
        self.assertEqual(urls, [PROVENANCE[HIT]["url"]])
        self.assertTrue(out.startswith("## Subject: Tylenol\n"))

    def test_bad_input_fetches_nothing(self):
        def never(url):
            raise AssertionError("no fetch expected")
        for argv in ([], ['say "cheese"'], ["x" * 101]):
            code, out, _ = self.run_main(argv, never)
            self.assertEqual(code, 2, argv)
            self.assertEqual(out, "")

    def test_failed_fetch_prints_no_report(self):
        def broken(url):
            raise urllib.error.URLError("connection refused (test)")
        code, out, err = self.run_main(["Lipitor"], broken)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)


if __name__ == "__main__":
    unittest.main()
