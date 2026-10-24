"""Tests for tools/insider_check.py and its GET /insider route (issue #182). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_insider_check.py' -v

Fixtures:
- fixtures/insider/ (recorded in provenance.json): the coordinator's four
  EDGAR captures on issue #182, each body verbatim; every SHA-256 matches
  the one posted. Their response headers were not posted, so each is given
  its posted status line and its body only.
- fixtures/edgar/ (recorded in that folder's provenance.json): the
  submissions indexes already in the repo for tools/edgar_formd.py, Apple
  (CIK 320193) for the hit and 8VC DSS III (CIK 2156237), which lists no
  ownership filing, for the empty result.
Variants built here say DERIVED where they are built, and stand-ins say
SYNTHETIC. Every test runs with urlopen replaced by a function that fails
the test, except the fetch test, which replaces it with a recorder.
"""

import hashlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import edgar_formd as ef  # noqa: E402
import insider_check as ic  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "insider"
EDGAR = Path(__file__).parent / "fixtures" / "edgar"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
EDGAR_PROV = json.loads((EDGAR / "provenance.json").read_text(encoding="utf-8"))
CONTACT = "Test Operator operator@example.com"  # placeholder contact for the tests


def posted(name, module=ef):
    """A capture as posted: its status line and verbatim body (headers were not posted)."""
    body = (FIX / name).read_bytes().decode("utf-8")
    status = {"HTTP 200": "HTTP/1.1 200 OK", "HTTP 404": "HTTP/1.1 404 Not Found"}[PROV[name]["status"]]
    return module.Capture(PROV[name]["url"], "2026-10-24T07:07:00Z", status + "\n\n" + body, body)


def indexed(name, module=ef):
    transcript = (EDGAR / name).read_bytes().decode("utf-8")
    return module.Capture(EDGAR_PROV[name]["url"], EDGAR_PROV[name]["retrieved_utc"], transcript,
                          transcript.partition("\n\n")[2])


class Fake:
    """Serves recorded captures by URL; any other URL fails the test. Records the contact sent."""

    def __init__(self, module=ef, overrides=None):
        self.by_url = {EDGAR_PROV[n]["url"]: indexed(n, module) for n in ("submissions-320193.http",
                                                                        "submissions-2156237.http")}
        self.by_url.update({PROV[n]["url"]: posted(n, module) for n in ("form4-040540.xml", "form4-040127.xml")})
        self.by_url.update(overrides or {})
        self.calls = []

    def __call__(self, url, contact):
        self.calls.append((url, contact))
        if url not in self.by_url:
            raise AssertionError("unexpected url %s" % url)
        return self.by_url[url]


def no_network(*args, **kwargs):
    raise AssertionError("insider_check tried to reach the network")


def run(argv, fetcher=None, env=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = ic.main(argv, fetcher=fetcher or Fake(), stdout=out, stderr=err, env=env or {})
    return code, out.getvalue(), err.getvalue()


APPLE = ["--cik", "320193", "--max-filings", "2", "--contact", CONTACT]


class FixtureTests(unittest.TestCase):
    def test_hashes_match_the_posted_ones(self):
        # Body sha256 values exactly as the coordinator posted them on issue #182.
        posted_sha256 = {
            "index-040540 body sha256": "6a574b86fcd58f0840a7dd08ef29123d23e5afe6e70f0dbe9f01e9663b7d9264",
            "form4-040540 body sha256": "dc6c562d2414f8e5218fd73fb87ae1390f3037ecc45699ef44fe09ba3cc7c8fc",
            "form4-040127 body sha256": "63d65b6e17d6566bbdccfdb96db267169bc6984a0e552bb363c87739b9cc8dac",
            "missing-404 body sha256": "e7c8e0946214e047a0cdc9efdd82ac60edee9bacf0075efb9fee174aef508b6c",
        }
        for key, sha in posted_sha256.items():
            stem = key.replace(" body sha256", "")
            name = [n for n in PROV if n.startswith(stem)][0]
            self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), sha, name)
            self.assertEqual(PROV[name]["sha256"], sha)

    def test_the_raw_document_url_is_the_one_the_folder_index_lists(self):
        folder = json.loads((FIX / "index-040540.json").read_text(encoding="utf-8"))
        self.assertIn("form4.xml", [i["name"] for i in folder["directory"]["item"]])
        self.assertEqual(ef.primary_doc_url("320193", "0001140361-26-040540", "xslF345X06/form4.xml"),
                         PROV["form4-040540.xml"]["url"])


class HitTests(unittest.TestCase):
    def test_newest_ownership_filings_with_transactions_as_filed(self):
        fake = Fake()
        code, out, err = run(APPLE, fake)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([u for u, _ in fake.calls], [EDGAR_PROV["submissions-320193.http"]["url"],
                                                     PROV["form4-040540.xml"]["url"], PROV["form4-040127.xml"]["url"]])
        self.assertTrue(all(c == CONTACT for _, c in fake.calls))
        self.assertIn("EDGAR's submissions index lists 616 ownership filings (form 3, 3/A, 4, 4/A, 5 or 5/A) among the "
                      "1002 filings in its recent window; the newest 2, in index order, are read below.", out)
        self.assertLess(out.index("## Answer"), out.index("## Evidence: the submissions index"))
        self.assertIn("### Form 4, accession 0001140361-26-040540, filed 2026-10-22", out)
        self.assertIn('- Reporting owner as filed: "Newstead Jennifer" (rptOwnerCik "0001780525"); relationship flags '
                      'as filed: isOfficer true; officerTitle "SVP, GC and Government Affairs"', out)
        self.assertIn('- transactionCode as filed: "S"', out)
        self.assertIn('- Shares as filed: "2399"', out)
        self.assertIn('- Price per share as filed: "339.62"', out)
        first = out[out.index("accession 0001140361-26-040540"):out.index("accession 0001140361-26-040127")]
        self.assertNotIn("Conversion or exercise price", first)  # derivative rows only
        self.assertIn('- Acquired or disposed code as filed: "D"', out)
        self.assertIn('- Shares owned following the transaction as filed: "34795"', out)
        self.assertIn('footnote F1: "This transaction was made pursuant to a Rule 10b5-1 trading plan', out)
        self.assertIn("not explained here", out)
        self.assertIn("Response: HTTP/1.1 200 OK; body 3294 bytes, SHA-256 %s" % PROV["form4-040540.xml"]["sha256"], out)

    def test_derivative_rows_and_footnote_only_prices(self):
        _, out, _ = run(APPLE)
        section = out[out.index("accession 0001140361-26-040127"):]
        self.assertEqual(section.count("(non-derivative table)"), 7)
        # Counted in the captured document: 7 nonDerivativeTransaction and 4 derivativeTransaction elements.
        self.assertEqual(section.count("(derivative table)"), 4)
        self.assertIn('- Price per share as filed: no value given; footnote F1: "Each restricted stock unit', section)
        self.assertIn('- Price per share as filed: "344.18"; footnote F6: "This transaction was executed in multiple '
                      'trades', section)
        self.assertIn("- Conversion or exercise price as filed: no value given; footnote F1:", section)

    def test_raw_rows_are_printed_verbatim_beneath_the_link(self):
        _, out, _ = run(APPLE)
        doc = (FIX / "form4-040540.xml").read_text(encoding="utf-8")
        row = doc[doc.index("<nonDerivativeTransaction>"):doc.index("</nonDerivativeTransaction>") + 27]
        self.assertIn("Transaction 1, verbatim from the document:\n```\n%s\n```" % row, out)
        self.assertIn(doc[doc.index("<footnotes>"):doc.index("</footnotes>") + 12], out)
        self.assertIn("form 4, filingDate 2026-10-22, accessionNumber 0001140361-26-040540, primaryDocument "
                      "xslF345X06/form4.xml", out)


class EmptyTests(unittest.TestCase):
    def test_no_ownership_filing_is_proven_by_the_full_index_response(self):
        fake = Fake()
        code, out, _ = run(["--cik", "2156237", "--contact", CONTACT], fake)
        self.assertEqual(code, 0)
        self.assertEqual(len(fake.calls), 1)
        self.assertIn("EDGAR's submissions index lists no Form 3, 4 or 5 filing (form 3, 3/A, 4, 4/A, 5 or 5/A) among "
                      "the 1 filings in its recent window.", out)
        self.assertIn("This covers that window only.", out)
        self.assertIn(indexed("submissions-2156237.http").transcript, out)

    def test_older_index_pages_are_named_and_not_read(self):
        # DERIVED: the 8VC index with an older page named in filings.files.
        cap = indexed("submissions-2156237.http")
        body = cap.body.replace('"files":[]', '"files":[{"name":"CIK0002156237-submissions-001.json"}]')
        self.assertNotEqual(body, cap.body)
        derived = ef.Capture(cap.url, cap.retrieved, cap.transcript.replace(cap.body, body), body)
        _, out, _ = run(["--cik", "2156237", "--contact", CONTACT], Fake(overrides={cap.url: derived}))
        self.assertIn('The index also names older pages, not read: "CIK0002156237-submissions-001.json".', out)


class FailureTests(unittest.TestCase):
    def test_the_captured_archives_404_stops_the_run(self):
        url = PROV["form4-040540.xml"]["url"]
        missing = posted("missing-404.xml")
        code, out, err = run(APPLE, Fake(overrides={url: ef.Capture(url, missing.retrieved, missing.transcript,
                                                                   missing.body)}))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("EDGAR Archives ownership document answered 'HTTP/1.1 404 Not Found', not 200; no report "
                      "(query %s)" % url, err)

    def test_a_body_that_is_not_an_ownership_document_stops_the_run(self):
        url = PROV["form4-040540.xml"]["url"]
        for body in ((FIX / "index-040540.json").read_text(encoding="utf-8"),  # the folder index: JSON, not XML
                     "<?xml version=\"1.0\"?><edgarSubmission/>",  # SYNTHETIC: another root
                     (FIX / "form4-040540.xml").read_text(encoding="utf-8").replace("<reportingOwner>", "<x>")
                     .replace("</reportingOwner>", "</x>"),  # DERIVED: no reportingOwner
                     (FIX / "form4-040540.xml").read_text(encoding="utf-8").replace("ownershipDocument>",
                                                                                   "otherDocument>"),  # DERIVED
                     (FIX / "form4-040540.xml").read_text(encoding="utf-8").replace(
                         "<footnotes>", "<!-- <nonDerivativeTransaction>x</nonDerivativeTransaction> --><footnotes>")):
            # DERIVED, last: a comment holding a row tag, so the raw rows cannot be paired with the parsed ones.
            cap = ef.Capture(url, "T", "HTTP/1.1 200 OK\n\n" + body, body)
            code, out, err = run(APPLE, Fake(overrides={url: cap}))
            self.assertEqual((code, out), (2, ""))
            self.assertIn("no report", err)

    def test_a_failed_request_is_never_an_empty_result(self):
        def broken(url, contact):
            raise ef.FetchError("request failed: SYNTHETIC connection reset; no report")
        code, out, err = run(["--cik", "2156237", "--contact", CONTACT], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection reset", err)

    def test_no_contact_or_bad_inputs_are_refused_before_any_fetch(self):
        def must_not(url, contact):
            raise AssertionError("no fetch expected")
        for argv in (["--cik", "320193"], ["--cik", "320193", "--contact", "no address"],
                     ["--cik", "abc", "--contact", CONTACT], ["--cik", "320193", "--contact", CONTACT, "--max-filings", "0"],
                     ["--cik", "320193", "--contact", CONTACT, "--max-filings", "21"]):
            self.assertEqual(run(argv, must_not)[0], 2, argv)

    def test_the_user_agent_names_this_tool_and_the_contact(self):
        sent = []

        class Answer:  # SYNTHETIC response object
            status, reason, version, headers = 200, "OK", 11, {}

            def read(self):
                return b"{}"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake(request, timeout=None):
            sent.append(request.get_header("User-agent"))
            return Answer()
        with mock.patch("urllib.request.urlopen", fake), mock.patch.object(ef, "pace", lambda: None):
            ic.fetch(EDGAR_PROV["submissions-320193.http"]["url"], CONTACT)
        self.assertEqual(sent, ["tiny-ledger insider_check.py %s" % CONTACT])


class RouteTests(unittest.TestCase):
    def get(self, qs, env):
        with mock.patch.object(endpoints.ins, "fetch", Fake(module=endpoints.ef)), \
                mock.patch("urllib.request.urlopen", no_network), mock.patch.dict("os.environ", env, clear=True):
            return recall_api.handle("GET", "/insider", qs, None)

    def test_route(self):
        env = {"EDGAR_CONTACT": CONTACT}
        status, _, body = self.get("cik=320193&max_filings=2", env)
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("### Form 4, accession 0001140361-26-040540, filed 2026-10-22", text)
        self.assertEqual(self.get("cik=2156237", env)[0], "200 OK")
        for qs in ("", "cik=320193&issuer=Apple", "cik=abc", "cik=320193&max_filings=0", "cik=320193&max_filings=21"):
            self.assertEqual(self.get(qs, env)[0], "400 Bad Request", qs)
        self.assertEqual(self.get("cik=320193", {})[0], "503 Service Unavailable")
        self.assertIn(ef.SUBMISSIONS_URL, endpoints.describe()["/insider"]["sources"])

    def test_route_maps_a_failure_to_502(self):
        def broken(url, contact):
            raise endpoints.ins.FetchError("SYNTHETIC failure; no report")
        with mock.patch.object(endpoints.ins, "fetch", broken), \
                mock.patch.dict("os.environ", {"EDGAR_CONTACT": CONTACT}, clear=True):
            self.assertEqual(recall_api.handle("GET", "/insider", "cik=320193", None)[0], "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
