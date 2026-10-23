"""Offline tests for the CPSC recalls dataset builder and validator (issue #148).

Run:  python3 -m unittest discover -s tools/tests -p 'test_cpsc_dataset.py' -v

Every record and response here is SYNTHETIC: invented recalls served by a
fake fetch_url that answers the builder's date range queries the way the
real endpoint is expected to. No network is used. The real pull is made
from a working environment and validated with the same validator.
"""

import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_cpsc_dataset as builder  # noqa: E402
import cpsc_recalls as cpsc  # noqa: E402
import validate_cpsc_dataset as validator  # noqa: E402


def synthetic_record(rid, number, day, name):
    """A SYNTHETIC recall in the CPSC record shape; not a real recall."""
    return {"RecallID": rid, "RecallNumber": number, "RecallDate": day + "T00:00:00",
            "Description": "SYNTHETIC test record %s" % number, "URL": "https://www.cpsc.gov/Recalls/test/%s" % number,
            "Title": "SYNTHETIC %s" % name, "LastPublishDate": day + "T00:00:00",
            "Products": [{"Name": name, "Description": "", "Model": "", "Type": "", "CategoryID": "",
                          "NumberOfUnits": "About 10"}],
            "Hazards": [{"Name": "SYNTHETIC hazard", "HazardType": "", "HazardTypeID": ""}]}


RECORDS = [synthetic_record(1, "23001", "2023-01-05", "Test kettle"),
           synthetic_record(2, "23002", "2023-01-30", "Test lamp"),
           synthetic_record(3, "23010", "2023-02-14", "Test stroller"),
           synthetic_record(4, "23020", "2023-03-31", "Test heater")]


class FakeAPI:
    """Answers RecallDateStart/End and RecallNumber queries from a record list."""

    def __init__(self, records, ignore_dates=False, extra_in_year=None):
        self.records, self.ignore_dates, self.extra_in_year = records, ignore_dates, extra_in_year
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        if "RecallNumber" in q:
            rows = [r for r in self.records if r["RecallNumber"] == q["RecallNumber"]]
        else:
            lo, hi = q["RecallDateStart"], q["RecallDateEnd"]
            rows = self.records if self.ignore_dates else [r for r in self.records if lo <= r["RecallDate"][:10] <= hi]
            if self.extra_in_year and lo.endswith("-01-01") and hi.endswith("-12-31"):
                rows = rows + [self.extra_in_year]
        body = json.dumps(rows)
        return cpsc.Capture(url, "2026-10-23T21:00:00Z",
                            "HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\n\r\n" + body)


class Build(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "out"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def build(self, api, start="2023-01-01", end="2023-12-31"):
        return builder.build(date.fromisoformat(start), date.fromisoformat(end), self.out, fetch_url=api,
                             now="2026-10-23T21:00:00Z")

    def test_lines_are_the_source_records_unchanged(self):
        p = self.build(FakeAPI(RECORDS))
        lines = (self.out / p["file"]).read_text(encoding="utf-8").splitlines()
        self.assertEqual([json.loads(l) for l in lines], RECORDS)
        self.assertEqual(p["total_records"], 4)
        self.assertEqual(len(p["month_queries"]), 12)
        self.assertEqual(p["year_cross_checks"][0]["unique_recall_ids"], 4)
        for name in ("provenance.json", "PROVENANCE.md", "schema.json", "SCHEMA.md", "recalls-2023-2023.jsonl"):
            self.assertTrue((self.out / name).is_file(), name)
        schema = json.loads((self.out / "schema.json").read_text(encoding="utf-8"))
        paths = {f["path"] for f in schema["fields"]}
        self.assertIn("Products[].Name", paths)
        self.assertIn("Hazards[].Name", paths)
        self.assertEqual(validator.validate(self.out)[0], [])

    def test_month_boundaries(self):
        got = list(builder.months(date(2023, 1, 15), date(2023, 3, 10)))
        self.assertEqual(got, [(date(2023, 1, 15), date(2023, 1, 31)), (date(2023, 2, 1), date(2023, 2, 28)),
                               (date(2023, 3, 1), date(2023, 3, 10))])

    def test_api_that_ignores_dates_stops_the_build(self):
        with self.assertRaisesRegex(builder.BuildError, "did not filter by date"):
            self.build(FakeAPI(RECORDS, ignore_dates=True))
        self.assertFalse(self.out.exists())

    def test_year_cross_check_mismatch_stops_the_build(self):
        stray = synthetic_record(9, "23099", "2023-06-01", "Test fan")
        with self.assertRaisesRegex(builder.BuildError, "whole-year query holds 5 unique recalls, the months 4"):
            self.build(FakeAPI(RECORDS, extra_in_year=stray))
        self.assertFalse(self.out.exists())

    def test_fetch_failure_stops_the_build(self):
        def broken(url):
            raise cpsc.FetchError("curl failed (exit 56); no recall conclusion")
        with self.assertRaisesRegex(builder.BuildError, "curl failed"):
            self.build(broken)
        self.assertFalse(self.out.exists())

    def with_change(self, change):
        api = FakeAPI(RECORDS)
        plain = api.__call__

        def changed(url):
            cap = plain(url)
            head, _, body = cap.raw.partition("\r\n\r\n")
            return cpsc.Capture(url, cap.retrieved, head + "\r\n\r\n" + json.dumps(change(url, json.loads(body))))
        return changed

    def test_record_outside_its_month_stops_the_build(self):
        api = self.with_change(lambda url, rows: rows + [RECORDS[0]] if "RecallDateStart=2023-02-01" in url else rows)
        with self.assertRaisesRegex(builder.BuildError, "dated 2023-01-05, outside 2023-02-01 to 2023-02-28"):
            self.build(api)
        self.assertFalse(self.out.exists())

    def test_identical_repeat_in_one_response_is_kept_once_and_counted(self):
        api = self.with_change(lambda url, rows: rows + [RECORDS[2]] if "RecallDateStart=2023-02-01&" in url else rows)
        p = self.build(api)
        self.assertEqual((p["records_returned_by_month_queries"], p["duplicates_dropped"], p["total_records"]),
                         (5, 1, 4))
        self.assertEqual(validator.validate(self.out)[0], [])

    def test_repeat_with_different_content_stops_the_build(self):
        other = dict(RECORDS[2], Title="SYNTHETIC different title")
        api = self.with_change(lambda url, rows: rows + [other] if "RecallDateStart=2023-02-01&" in url else rows)
        with self.assertRaisesRegex(builder.BuildError, "RecallID 3 came back twice with different content"):
            self.build(api)


class Validate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "out"
        self.prov = builder.build(date(2023, 1, 1), date(2023, 12, 31), self.out, fetch_url=FakeAPI(RECORDS),
                                  now="2026-10-23T21:00:00Z")
        self.file = self.out / self.prov["file"]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rewrite(self, change):
        lines = self.file.read_text(encoding="utf-8").splitlines()
        self.file.write_text("\n".join(change(lines)) + "\n", encoding="utf-8")

    def test_added_field_fails(self):
        def add(lines):
            rec = json.loads(lines[0])
            rec["Enriched"] = "not from CPSC"
            return [json.dumps(rec)] + lines[1:]
        self.rewrite(add)
        problems = " ".join(validator.validate(self.out)[0])
        self.assertIn("not in schema.json: ['Enriched']", problems)
        self.assertIn("sha256", problems)

    def test_dropped_line_fails_the_count(self):
        self.rewrite(lambda lines: lines[:-1])
        self.assertIn("3 records in the file", " ".join(validator.validate(self.out)[0]))

    def test_main_exit_codes(self):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(validator.main([str(self.out)]), 0)
            self.rewrite(lambda lines: lines + ["not json"])
            self.assertEqual(validator.main([str(self.out)]), 1)
        self.assertIn("FAIL line 5 does not parse", out.getvalue())

    def test_recheck_compares_live_records_exactly(self):
        _, records = validator.validate(self.out)
        problems, done = validator.recheck(records, 2, fetch_url=FakeAPI(RECORDS))
        self.assertEqual(problems, [])
        self.assertEqual(len(done), 2)
        changed = [dict(r) for r in RECORDS]
        changed[0]["Title"] = "SYNTHETIC changed upstream"
        problems, _ = validator.recheck(records, 4, fetch_url=FakeAPI(changed))
        self.assertTrue(any("differs from the live record in: ['Title']" in p for p in problems), problems)


DATASET = ROOT / "datasets" / "cpsc-recalls"


@unittest.skipUnless((DATASET / "provenance.json").is_file(), "the live dataset has not been pulled into datasets/")
class CommittedDataset(unittest.TestCase):
    """The committed dataset passes every offline check (the live recheck is run at review)."""

    def test_offline_checks_pass(self):
        problems, records = validator.validate(DATASET)
        self.assertEqual(problems, [])
        self.assertTrue(records)

if __name__ == "__main__":
    unittest.main()
