"""Offline tests for tools/npi_check.py (issue #326). No network.

Run from the repository root: python3 -m unittest discover -s tools/tests -v

The five captures are LIVE CAPTUREs made by H5 for this issue on
2026-10-24 with the tool's User-Agent, filed under fixtures/npi/ next to
a provenance.json that records each query URL, retrieval time and
SHA-256:

- npi-number-hit.http: number=1740584747 answers 1 result, an individual
  (NPI-1) with status A, credential D.O., three taxonomies (the third
  flagged primary) and LOCATION and MAILING addresses in MO.
- npi-name-individual-hit.http: first_name=Brian, last_name=Aalbers
  answers the same provider.
- npi-name-org-empty.http: organization_name=Brian Aalbers answers
  result_count 0 with an empty results array.
- npi-number-empty.http: number=9999999999 (well formed, unassigned)
  answers result_count 0 with an empty results array.
- npi-errors-bad-version.http: a query with version=9.9 answers an
  Errors document (Unsupported Version) at HTTP 200.

The paging cases build their pages in code from minimal result objects
and are labelled SYNTHETIC where they appear; no fixture file is mutated.
"""

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import npi_check as npi  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "npi"
RETRIEVED = "2026-10-24T12:35:00Z"


def load_cap(name, url):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    status_line, rest = text.split("\n", 1)
    head, _, body = rest.partition("\n\n")
    headers = [tuple(line.split(": ", 1)) for line in head.split("\n")]
    return npi.Capture(url, RETRIEVED, status_line, headers, body)


def stub(caps):
    def fetch(url):
        if url not in caps:
            raise AssertionError("unexpected URL fetched: %s" % url)
        return caps[url]
    return fetch


NUM_PARAMS = [("number", "1740584747")]
IND_PARAMS = [("first_name", "Brian"), ("last_name", "Aalbers")]
ORG_PARAMS = [("organization_name", "Brian Aalbers")]
EMPTY_NUM_PARAMS = [("number", "9999999999")]

NUMBER_HIT = load_cap("npi-number-hit.http", npi.page_url(NUM_PARAMS, 0))
IND_HIT = load_cap("npi-name-individual-hit.http", npi.page_url(IND_PARAMS, 0))
ORG_EMPTY = load_cap("npi-name-org-empty.http", npi.page_url(ORG_PARAMS, 0))
NUMBER_EMPTY = load_cap("npi-number-empty.http", npi.page_url(EMPTY_NUM_PARAMS, 0))
ERRORS = load_cap("npi-errors-bad-version.http", npi.page_url(NUM_PARAMS, 0))


def report_text(query, caps):
    return "\n".join(npi.report(query, fetcher=stub(caps)))


class QueryTests(unittest.TestCase):
    def test_check_query(self):
        self.assertEqual(npi.check_query(" 1740584747 "), ("npi", "1740584747"))
        self.assertEqual(npi.check_query("Brian   Aalbers"), ("name", "Brian Aalbers"))
        for bad in ["", "12345", "174058474700", "Brian123", "A", "Brian@Aalbers", None]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                npi.check_query(bad)

    def test_interpretations(self):
        self.assertEqual(npi.interpretations("npi", "1740584747"),
                         [("NPI number", [("number", "1740584747")])])
        labels = [label for label, _ in npi.interpretations("name", "Brian Aalbers")]
        self.assertEqual(len(labels), 2)
        params = dict(npi.interpretations("name", "Brian Aalbers"))
        self.assertEqual(params[labels[0]], [("first_name", "Brian"), ("last_name", "Aalbers")])
        self.assertEqual(params[labels[1]], [("organization_name", "Brian Aalbers")])
        single = dict(npi.interpretations("name", "Aalbers"))
        self.assertEqual(single[[k for k in single if k.startswith("Individual")][0]],
                         [("last_name", "Aalbers")])

    def test_page_url_shape(self):
        self.assertEqual(npi.page_url(NUM_PARAMS, 0),
                         "https://npiregistry.cms.hhs.gov/api/?version=2.1&number=1740584747&limit=200&skip=0")
        self.assertIn("organization_name=Brian%20Aalbers", npi.page_url(ORG_PARAMS, 200))


class NumberHitTests(unittest.TestCase):
    """The live number capture: one provider, all fields as shown."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text("1740584747", {NUMBER_HIT.url: NUMBER_HIT})

    def test_header_and_observation(self):
        self.assertIn("# NPI Registry check: 1740584747", self.text)
        self.assertIn("does not merge sources", self.text)

    def test_provider_fields(self):
        self.assertIn("The registry returned 1 record(s) for this interpretation across 1 page(s):", self.text)
        self.assertIn('- NPI number (number) as shown: "1740584747"', self.text)
        self.assertIn('- Enumeration type (enumeration_type) as shown: `"NPI-1"`', self.text)
        self.assertIn('- Name as shown: `"BRIAN"` `"MICHAEL"` `"AALBERS"`', self.text)
        self.assertIn('- Credential (credential) as shown: `"D.O."`', self.text)
        self.assertIn('- Status (status) as shown: `"A"`', self.text)

    def test_taxonomies_with_primary_flags_as_shown(self):
        self.assertIn('- Taxonomy as shown: `"Pediatrics, Neurodevelopmental Disabilities"`', self.text)
        self.assertEqual(self.text.count("primary: `false`"), 2)
        self.assertEqual(self.text.count("primary: `true`"), 1)
        self.assertNotIn("No taxonomy in this record is flagged primary.", self.text)

    def test_practice_state_is_the_location_state(self):
        self.assertIn('- Practice state: `"MO"` (state as shown, of the LOCATION address', self.text)

    def test_evidence_complete(self):
        self.assertIn("Exact query URL: <%s>" % NUMBER_HIT.url, self.text)
        self.assertIn("UTC retrieval time: %s" % RETRIEVED, self.text)
        self.assertIn('"number":"1740584747"', self.text)  # verbatim fields block and raw body
        self.assertIn(NUMBER_HIT.body, self.text)  # complete raw response


class NameModeTests(unittest.TestCase):
    """The live name captures: individual hits, organization is empty."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text("Brian Aalbers", {IND_HIT.url: IND_HIT, ORG_EMPTY.url: ORG_EMPTY})

    def test_both_interpretations_reported(self):
        self.assertIn("Interpretation: Individual name (first word as first_name, last word as last_name)",
                      self.text)
        self.assertIn("Interpretation: Organization name (the whole name as organization_name)", self.text)
        self.assertIn('- NPI number (number) as shown: "1740584747"', self.text)
        self.assertIn("No match under this interpretation.", self.text)
        self.assertNotIn("No matching provider under any interpretation.", self.text)
        self.assertIn(ORG_EMPTY.body, self.text)  # the empty organization proof


class NoMatchTests(unittest.TestCase):
    def test_number_empty_is_a_proven_no_match(self):
        text = report_text("9999999999", {NUMBER_EMPTY.url: NUMBER_EMPTY})
        self.assertIn("No matching provider under any interpretation.", text)
        self.assertIn("not a statement that the provider does not exist", text)
        self.assertIn('"result_count":0', text.replace(" ", ""))  # the empty shape, in the raw body
        self.assertIn(NUMBER_EMPTY.body, text)


class ErrorsDocumentTests(unittest.TestCase):
    """The live bad version capture: an Errors document at HTTP 200 is
    refused, never read as an empty result. The replay serves it for the
    tool's own URL."""

    def test_errors_document_fails_closed(self):
        with self.assertRaises(npi.FetchError) as ctx:
            report_text("1740584747", {ERRORS.url: ERRORS})
        self.assertIn("Errors document", str(ctx.exception))


class PagingTests(unittest.TestCase):
    """SYNTHETIC pages built in code: result_count is never a total, so a
    full page is followed with skip until a short page arrives, and the
    page cap is named when hit."""

    def synth_page(self, url, numbers):
        results = [{"number": n, "enumeration_type": "NPI-1",
                    "basic": {"first_name": "SYNTH", "last_name": "PAGE", "status": "A"},
                    "taxonomies": [], "addresses": []} for n in numbers]
        body = json.dumps({"result_count": len(results), "results": results})
        return npi.Capture(url, RETRIEVED, "HTTP/1.1 200 OK", [], body)

    def test_full_page_then_short_page(self):
        with mock.patch.object(npi, "PAGE_LIMIT", 2):
            p0 = self.synth_page(npi.page_url(NUM_PARAMS, 0), [1000000001, 1000000002])
            p1 = self.synth_page(npi.page_url(NUM_PARAMS, 2), [1000000003])
            results, captures, capped = npi.collect(NUM_PARAMS, stub({p0.url: p0, p1.url: p1}))
        self.assertEqual(len(results), 3)
        self.assertEqual(len(captures), 2)
        self.assertFalse(capped)

    def test_page_cap_is_named(self):
        with mock.patch.object(npi, "PAGE_LIMIT", 2), mock.patch.object(npi, "MAX_PAGES", 2):
            p0 = self.synth_page(npi.page_url(NUM_PARAMS, 0), [1000000001, 1000000002])
            p1 = self.synth_page(npi.page_url(NUM_PARAMS, 2), [1000000003, 1000000004])
            results, captures, capped = npi.collect(NUM_PARAMS, stub({p0.url: p0, p1.url: p1}))
            text = "\n".join(npi.report("1740584747", fetcher=stub({p0.url: p0, p1.url: p1})))
        self.assertEqual(len(results), 4)
        self.assertTrue(capped)
        self.assertIn("the page cap of 2 was reached with a full last page", text)
        self.assertIn("The registry returned 4 record(s) for this interpretation across 2 page(s)", text)


class ShapeFailureTests(unittest.TestCase):
    """SYNTHETIC reshaped bodies: never a report, never a negative claim."""

    def assert_no_report(self, body):
        cap = npi.Capture(NUMBER_HIT.url, RETRIEVED, "HTTP/1.1 200 OK", [], body)
        with self.assertRaises(npi.FetchError):
            npi.report("1740584747", fetcher=stub({cap.url: cap}))

    def test_result_count_mismatch(self):
        self.assert_no_report('{"result_count": 2, "results": []}')

    def test_result_missing_basic_name(self):
        self.assert_no_report('{"result_count": 1, "results": [{"number": 1, "enumeration_type": "NPI-1",'
                              ' "basic": {"status": "A"}, "taxonomies": [], "addresses": []}]}')

    def test_not_json(self):
        self.assert_no_report("<html>bad gateway</html>")


class TransportTests(unittest.TestCase):
    def test_url_error_fails_closed(self):
        with mock.patch.object(npi.urllib.request, "urlopen",
                               side_effect=urllib.error.URLError("down")):
            with self.assertRaises(npi.FetchError):
                npi.fetch(NUMBER_HIT.url)

    def test_http_error_fails_closed(self):
        err = urllib.error.HTTPError(NUMBER_HIT.url, 503, "Unavailable", {}, None)
        with mock.patch.object(npi.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(npi.FetchError) as ctx:
                npi.fetch(NUMBER_HIT.url)
        self.assertIn("HTTP 503", str(ctx.exception))


class MainTests(unittest.TestCase):
    def run_main(self, argv, caps=None):
        out, err = io.StringIO(), io.StringIO()
        code = npi.main(argv, fetcher=stub(caps or {}), stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_hit_exit_0(self):
        code, out, _ = self.run_main(["1740584747"], {NUMBER_HIT.url: NUMBER_HIT})
        self.assertEqual(code, 0)
        self.assertIn("1740584747", out)

    def test_bad_arguments_exit_2_without_a_report(self):
        for argv in (["12345"], ["Brian123"], [], ["A"]):
            code, out, err = self.run_main(argv)
            self.assertEqual(code, 2, argv)
            self.assertNotIn("# NPI Registry check", out)
            self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
