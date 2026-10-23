"""Tests for tools/weekly_brief.py (issue #146). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_weekly_brief.py' -v

Which data is which:

* REAL CAPTURE: the EDGAR responses are the complete raw transcripts in
  fixtures/edgar/, captured by edgar_formd.fetch() on 2026-10-23 and hashed
  in fixtures/edgar/provenance.json. Two watchlist issuers (CIK 2156237 and
  1801756) each have a Form D filed on 2026-10-22.
* SYNTHETIC: the USAspending bodies in fixtures/weekly-brief/ are labelled
  SYNTHETIC inside each file and hashed in that folder's provenance.json.
* Every test runs with urlopen replaced by a function that fails the test.
"""

import hashlib
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edgar_formd as ef  # noqa: E402
import usaspending_awards as ua  # noqa: E402
import weekly_brief as wb  # noqa: E402

EDGAR = Path(__file__).parent / "fixtures" / "edgar"
OWN = Path(__file__).parent / "fixtures" / "weekly-brief"
EDGAR_PROV = json.loads((EDGAR / "provenance.json").read_text(encoding="utf-8"))
OWN_PROV = json.loads((OWN / "provenance.json").read_text(encoding="utf-8"))
SAMPLE_CONFIG = Path(__file__).resolve().parents[1] / "weekly-brief" / "sample-config.json"
CONTACT = "Test Operator you@example.com"
NOW = datetime(2026, 10, 23, 22, 0, tzinfo=timezone.utc)


def edgar_fetch(skip=("undeclared-403.http",), override=None):
    by_url = {m["url"]: n for n, m in EDGAR_PROV.items() if isinstance(m, dict) and "url" in m and n not in skip}
    if override:
        by_url.update(override)

    def fetch(url, contact):
        name = by_url[url]
        transcript = (EDGAR / name).read_bytes().decode("utf-8")
        return ef.Capture(url, EDGAR_PROV[name]["retrieved_utc"], transcript, transcript.partition("\n\n")[2])
    return fetch


def usa_fetch(name, sent=None):
    def fetch(query):
        if sent is not None:
            sent.append(query)
        return ua.Capture(query, "SYNTHETIC (fixture)", (OWN / name).read_text(encoding="utf-8"))
    return fetch


def no_network(*args, **kwargs):
    raise AssertionError("weekly_brief tried to reach the network")


def config(**edgar):
    base = {"title": "Test brief", "edgar": dict({"ciks": ["2156237", "1801756"], "sectors": [], "keywords": []}, **edgar),
            "usaspending": {"naics": ["5415"], "limit": 10}}
    return base


def build(cfg, week="2026-10-23", usa="synthetic-usaspending-two.json", sent=None, efetch=None):
    with mock.patch("urllib.request.urlopen", no_network):
        return wb.build(cfg, week, CONTACT, efetch or edgar_fetch(), usa_fetch(usa, sent), now=NOW)


class FixtureTests(unittest.TestCase):
    def test_hashes_and_synthetic_labels(self):
        for name in ("synthetic-usaspending-two.json", "synthetic-usaspending-empty.json"):
            data = (OWN / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), OWN_PROV[name]["sha256"])
            self.assertTrue(json.loads(data)["_SYNTHETIC"].startswith("SYNTHETIC"))
        for name in ("submissions-2156237.http", "submissions-1801756.http", "formd-0002156237-26-000001.http",
                     "formd-0000929638-26-003990.http"):
            self.assertEqual(hashlib.sha256((EDGAR / name).read_bytes()).hexdigest(), EDGAR_PROV[name]["sha256"])


class EdgarLegTests(unittest.TestCase):
    def test_sector_filter_lists_both_real_filings_with_their_figures(self):
        brief = build(config(sectors=["pooled investment fund"]))
        self.assertIn("### 8VC DSS III, L.P., D 0002156237-26-000001", brief)
        self.assertIn("### Argentem Opportunities Fund LP, D/A 0000929638-26-003990", brief)
        self.assertIn("- Total offering amount as shown: 400000000", brief)
        self.assertIn("- Total amount sold as shown: 243290624", brief)
        self.assertIn("- Total offering amount as shown: Indefinite", brief)
        self.assertIn('filings.recent.filingDate[0]: "2026-10-22"', brief)
        self.assertIn("<totalOfferingAmount>400000000</totalOfferingAmount>", brief)
        self.assertIn("In this brief: 2 Form D filing(s), 2 award(s).", brief)

    def test_keyword_filter_lists_one_and_names_the_one_it_checked(self):
        brief = build(config(keywords=["8vc"]))
        self.assertIn("### 8VC DSS III, L.P.", brief)
        self.assertNotIn("### Argentem", brief)
        self.assertIn("- Argentem Opportunities Fund LP (CIK 0001801756), D/A 0000929638-26-003990 filed 2026-10-22: "
                      "checked, not listed", brief)

    def test_only_filings_inside_the_window_are_read(self):
        asked, inner = [], edgar_fetch()

        def recording(url, contact):
            asked.append(url)
            return inner(url, contact)
        brief = build(config(), week="2026-10-21", efetch=recording)
        self.assertIn("No Form D filing in the window matched the filters.", brief)
        self.assertEqual(asked, [ef.submissions_url("2156237"), ef.submissions_url("1801756")])
        asked.clear()
        build(config(), week="2026-10-28", efetch=recording)
        self.assertEqual(sum(u.endswith("primary_doc.xml") for u in asked), 2)

    def test_empty_result_is_shown_empty_with_every_raw_response(self):
        brief = build(config(sectors=["Biotechnology"]))
        edgar = brief.split("## USAspending")[0]
        self.assertIn("No Form D filing in the window matched the filters. Every raw response read for this leg "
                      "follows, in full.", edgar)
        for name in ("submissions-2156237.http", "submissions-1801756.http", "formd-0002156237-26-000001.http",
                     "formd-0000929638-26-003990.http"):
            self.assertIn((EDGAR / name).read_bytes().decode("utf-8"), edgar, name)
        self.assertIn("In this brief: 0 Form D filing(s)", brief)

    def test_a_refused_request_stops_the_brief(self):
        url = ef.submissions_url("2156237")
        with self.assertRaises(ef.FetchError):
            build(config(), efetch=edgar_fetch(skip=(), override={url: "undeclared-403.http"}))


    def test_a_non_200_form_d_document_stops_the_brief_even_when_its_body_parses(self):
        # DERIVED: the real Form D transcript with only its status line changed to 404.
        inner = edgar_fetch()

        def derived(url, contact):
            cap = inner(url, contact)
            if url.endswith("primary_doc.xml"):
                return ef.Capture(url, cap.retrieved, cap.transcript.replace("HTTP/1.1 200 OK", "HTTP/1.1 404 Not Found", 1),
                                  cap.body)
            return cap
        with self.assertRaises(ef.FetchError):
            build(config(), efetch=derived)


class UsaspendingLegTests(unittest.TestCase):
    def test_query_is_the_fetchers_own_with_the_window(self):
        sent = []
        build(config(), sent=sent)
        expected = ua.build_query(wb.Namespace(recipient=None, naics=["5415"], start="2026-10-17",
                                               end="2026-10-23", page=1, limit=10))
        self.assertEqual(sent, [expected])
        self.assertEqual(json.loads(sent[0])["filters"]["time_period"],
                         [{"start_date": "2026-10-17", "end_date": "2026-10-23"}])

    def test_awards_carry_recipient_amount_date_link_and_raw_record(self):
        brief = build(config())
        self.assertIn("- Recipient as shown: SYNTHETIC ANALYTICS LLC", brief)
        self.assertIn("- Award Amount as shown: 1250000.5", brief)
        self.assertIn("- Award Amount as shown: not stated by the source", brief)
        self.assertIn("- Award page: <https://www.usaspending.gov/award/CONT_AWD_SYN0001_9700_-NONE-_-NONE->", brief)
        self.assertIn('{"internal_id":1,"Award ID":"SYN-0001"', brief)
        self.assertIn("The API reports more pages; this brief lists the first page only.", brief)

    def test_empty_awards_shown_empty_with_the_full_raw_response(self):
        brief = build(config(), usa="synthetic-usaspending-empty.json")
        self.assertIn("No award matched the filters for this window. The complete raw response follows.", brief)
        self.assertIn((OWN / "synthetic-usaspending-empty.json").read_text(encoding="utf-8"), brief)
        self.assertIn("0 award(s)", brief)


class FiguresTests(unittest.TestCase):
    def test_every_figure_is_in_its_excerpts(self):
        for brief in (build(config(sectors=["Pooled Investment Fund"])), build(config(keywords=["argentem"]))):
            self.assertEqual(wb.unsupported_figures(brief), [])

    def test_a_figure_missing_from_its_excerpt_is_caught(self):
        brief = build(config(sectors=["Pooled Investment Fund"]))
        for old, new in (("Total amount sold as shown: 0", "Total amount sold as shown: 5"),
                         ("Award Amount as shown: 1250000.5", "Award Amount as shown: 1250000"),
                         ("Start Date as shown: 2026-10-20", "Start Date as shown: 2026-10-2")):
            self.assertEqual(len(wb.unsupported_figures(brief.replace(old, new))), 1, new)


class CliTests(unittest.TestCase):
    def run_main(self, argv, env=None, usa="synthetic-usaspending-two.json"):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("urllib.request.urlopen", no_network):
            code = wb.main(argv, edgar_fetch=edgar_fetch(), usa_fetch=usa_fetch(usa), env=env or {},
                           stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_sample_config_runs_and_checks_clean(self):
        code, out, err = self.run_main(["--config", str(SAMPLE_CONFIG), "--week-ending", "2026-10-23",
                                        "--contact", CONTACT])
        self.assertEqual((code, err), (0, ""))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(out, encoding="utf-8")
            code, report, _ = self.run_main(["--check", str(path)])
            self.assertEqual(code, 0, report)
            path.write_text(out.replace("as shown: 243290624", "as shown: 243290625"), encoding="utf-8")
            code, report, _ = self.run_main(["--check", str(path)])
            self.assertEqual(code, 1)
            self.assertIn("NOT IN EXCERPT", report)

    def test_failures_exit_2_with_nothing_printed(self):
        code, out, err = self.run_main(["--config", str(SAMPLE_CONFIG), "--week-ending", "2026-10-23"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("contact", err)
        with tempfile.TemporaryDirectory() as tmp:
            for body in ('{"edgar": {"ciks": []}}', '{"usaspending": {"naics": []}}', '{"extra": 1}', "not json",
                         '{"edgar": {"ciks": ["abc"]}}'):
                path = Path(tmp) / "c.json"
                path.write_text(body, encoding="utf-8")
                code, out, _ = self.run_main(["--config", str(path), "--contact", CONTACT])
                self.assertEqual((code, out), (2, ""), body)
        code, out, _ = self.run_main(["--config", str(SAMPLE_CONFIG), "--week-ending", "23/10/2026",
                                      "--contact", CONTACT])
        self.assertEqual((code, out), (2, ""))

    def test_a_transport_failure_is_not_an_empty_result(self):
        def broken(query):
            raise urllib.error.URLError("SYNTHETIC: connection refused")
        out, err = io.StringIO(), io.StringIO()
        code = wb.main(["--config", str(SAMPLE_CONFIG), "--contact", CONTACT], edgar_fetch=edgar_fetch(),
                       usa_fetch=broken, env={}, stdout=out, stderr=err)
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("connection refused", err.getvalue())


if __name__ == "__main__":
    unittest.main()
