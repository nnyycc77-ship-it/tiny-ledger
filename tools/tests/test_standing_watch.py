"""Tests for tools/standing_watch.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_standing_watch.py' -v

Fixtures are real captures and recorded text, never invented data:

* The CPSC captures are the committed fixtures in tools/tests/fixtures/
  (instant-pot.http, one record; smart-wifi.http, an empty result),
  read with their provenance from fixtures/provenance.json, the same
  files test_cpsc_recalls.py uses.
* The FMCSA texts are copied verbatim from the published carrier
  vetting delivery deliveries/carrier-vetting-3b4e7143-c7e2-4fda-92f4-
  c19a99bbd98f.md, the same recordings test_fmcsa_carrier.py uses:
  the Census excerpt (delivery lines 447 to 467, with the object
  braces the delivery omitted restored around it so it parses, values
  unchanged), SAFER sources S2, S3, and S8 (delivery lines 475 to 499,
  507 to 526, 639 to 651), and the Licensing and Insurance source S9
  (delivery lines 659 to 672). No HTML of the SAFER or LI pages was
  recorded, only their text, so the HTML parser is exercised on a
  harness that wraps each recorded text line in a table row, exactly
  as in test_fmcsa_carrier.py; the harness is labelled a harness there
  and here.

Two things in these tests are synthetic and labelled where they
appear: (1) mutated copies of the recorded field maps, used only to
exercise the diff; (2) the fixed run timestamps, which are test
inputs, not retrieval times.
"""

import hashlib
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import cpsc_recalls as cpsc  # noqa: E402
import fmcsa_carrier as fc  # noqa: E402
import standing_watch as sw  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text())
RETRIEVED = "2026-10-22T21:34:25Z"  # SAFER retrieval time recorded for USDOT 2046

# Delivery source S1, FMCSA Company Census File record, USDOT 2046,
# delivery lines 447 to 467 verbatim (braces restored, values unchanged).
CENSUS_BODY_2046 = """[{
  "dot_number": "2046",
  "legal_name": "GARDA CL CENTRAL INC",
  "phy_city": "BOCA RATON",
  "phy_state": "FL",
  "power_units": "137",
  "total_drivers": "84",
  "docket1prefix": "MC",
  "docket1": "65419",
  "docket1_status_code": "A",
  "safety_rating": "S",
  "safety_rating_date": "20220817",
  "mcs150_mileage": "1420000",
  "mcs150_mileage_year": "2026",
  "mcs150_date": "20260601",
  "business_org_desc": "CORPORATION",
  "carship": "C",
  "carrier_operation": "A",
  "status_code": "A",
  "classdef": "AUTHORIZED FOR HIRE"
}]"""

# Delivery sources S2, S3, S8, SAFER Company Snapshot text, USDOT 2046.
SAFER_TEXT_2046 = """USDOT INFORMATION
Entity Type:
CARRIER
New Entrant Status:
(Active)
-->
USDOT Status:
ACTIVE
Out of Service Date:
None
USDOT Number:
2046
State Carrier ID Number:
MCS-150 Form Date:
06/01/2026
MCS-150 Mileage (Year):
1,420,000 (2026)
OPERATING AUTHORITY INFORMATION
Operating Authority Status:
AUTHORIZED FOR:
Motor Carrier of Property (Except Household Goods)
For Licensing and Insurance details
click here.
MC/MX/FF Number(s):
MC-65419
COMPANY INFORMATION
Legal Name:
GARDA CL CENTRAL INC
DBA Name:
Physical Address:
2000 NW CORPORATE BLVD
BOCA RATON, FL   33431-7304
Phone:
(561) 939-7000
Mailing Address:
2000 NW CORPORATE BLVD
BOCA RATON, FL   33431-7304
DUNS Number:
45-734-852
Power Units:
68
Non-CMV Units:
69
Drivers:
84
Carrier Safety Rating:
The rating below is current as of:
10/20/2026
Review Information:
Review Information
Rating Date:
08/17/2022
Review Date:
08/10/2022
Rating:
Satisfactory
Type:
Compliance Review"""

# Delivery source S9, Licensing and Insurance record text, USDOT 2046.
LI_TEXT_2046 = """US DOT: 2046
Docket Number: MC00065419
Legal Name: GARDA CL CENTRAL, INC
Authority Type | Authority Status | Application Pending
Common | ACTIVE | NO"""


def harness_html(text):
    """Test harness only: each recorded text line becomes one table row.
    Not a recording of any FMCSA page's HTML."""
    rows = "".join("<tr><td>%s</td></tr>" % line for line in text.split("\n"))
    return ("<html><head><title>t</title><script>var x = 'skip me';</script></head>"
            "<body><table>%s</table></body></html>" % rows)


def fc_capture(url, body, status_line="HTTP/1.1 200 OK"):
    return fc.Capture(url, RETRIEVED, status_line,
                      ["Content-Type: text/plain"], body, "utf-8")


def cpsc_capture(name):
    metadata = PROVENANCE[name]
    return cpsc.Capture(metadata["url"], metadata["retrieved_utc"],
                        (FIXTURES / name).read_bytes().decode("utf-8"))


def carrier_captures():
    return {
        "census": fc_capture(fc.census_record_url("2046"), CENSUS_BODY_2046),
        "safer": fc_capture(fc.safer_url("2046"), harness_html(SAFER_TEXT_2046)),
        "li": fc_capture(fc.li_url("2046"), harness_html(LI_TEXT_2046)),
    }


def sample_watchlist():
    return sw.validate_watchlist({
        "version": 1,
        "carriers": [{"usdot": "2046", "label": "GARDA CL CENTRAL INC"}],
        "products": [
            {"label": "Instant Pot",
             "queries": [{"field": "ProductName", "value": "Instant Pot"}]},
            {"label": "Instant Pot Smart WiFi 6 Qt",
             "queries": [{"field": "ProductName", "value": "Instant Pot Smart WiFi"}]},
        ],
    }, "test")


class FakeFetch:
    """Stands in for the fetchers' live fetches with recorded captures."""

    def __init__(self):
        self.carrier = carrier_captures()
        self.products = {
            "Instant Pot": cpsc_capture("instant-pot.http"),
            "Instant Pot Smart WiFi": cpsc_capture("smart-wifi.http"),
        }

    def fc_fetch(self, url):
        if url == fc.census_record_url("2046"):
            return self.carrier["census"]
        if url == fc.safer_url("2046"):
            return self.carrier["safer"]
        if url == fc.li_url("2046"):
            return self.carrier["li"]
        raise AssertionError("unexpected FMCSA URL %s" % url)

    def cpsc_fetch(self, value, field="ProductName"):
        return self.products[value]


class WatchlistTests(unittest.TestCase):
    def test_valid_watchlist_loads_and_keys(self):
        watchlist = sample_watchlist()
        self.assertEqual(sw.entry_keys(watchlist),
                         ["carrier:2046", "product:instant-pot",
                          "product:instant-pot-smart-wifi-6-qt"])

    def test_carrier_label_defaults_to_usdot(self):
        watchlist = sw.validate_watchlist(
            {"version": 1, "carriers": [{"usdot": "2046"}]}, "test")
        self.assertEqual(watchlist["carriers"][0]["label"], "USDOT 2046")

    def test_bad_watchlists_are_refused(self):
        bad = [
            {"version": 2, "carriers": [{"usdot": "2046"}]},
            {"version": 1, "carriers": [{"usdot": "20A6"}]},
            {"version": 1, "carriers": []},
            {"version": 1, "products": [{"label": "X", "queries": []}]},
            {"version": 1, "products": [
                {"label": "X", "queries": [{"field": "Bogus", "value": "Y"}]}]},
            {"version": 1, "products": [
                {"label": "Same Name", "queries": [{"field": "ProductName", "value": "A"}]},
                {"label": "Same Name", "queries": [{"field": "ProductName", "value": "B"}]}]},
        ]
        for data in bad:
            with self.subTest(data=data):
                with self.assertRaises(sw.WatchError):
                    sw.validate_watchlist(data, "test")


class FieldTests(unittest.TestCase):
    def test_carrier_fields_are_the_recorded_values(self):
        fields = sw.carrier_fields("2046", carrier_captures())
        self.assertEqual(fields["census.record_count"], 1)
        self.assertEqual(fields["census.dot_number"], "2046")
        self.assertEqual(fields["census.legal_name"], "GARDA CL CENTRAL INC")
        self.assertEqual(fields["census.status_code"], "A")
        self.assertEqual(fields["census.docket1_status_code"], "A")
        self.assertEqual(fields["census.safety_rating"], "S")
        self.assertEqual(fields["census.dba_name"], None)
        self.assertEqual(fields["safer.USDOT Status:"], "ACTIVE")
        self.assertEqual(fields["safer.Rating:"], "Satisfactory")
        self.assertEqual(fields["li.record_lines"],
                         ["US DOT: 2046", "Docket Number: MC00065419",
                          "Legal Name: GARDA CL CENTRAL, INC"])

    def test_carrier_fields_fail_closed_on_http_error(self):
        captures = carrier_captures()
        captures["census"] = fc_capture(fc.census_record_url("2046"),
                                         "not json", "HTTP/1.1 500 Server Error")
        fields = sw.carrier_fields("2046", captures)
        self.assertIsNone(fields["census.record_count"])
        self.assertIsNone(fields["census.status_code"])

    def test_product_fields_from_real_captures(self):
        instant = cpsc_capture("instant-pot.http")
        rows = cpsc.records(instant)
        fields = sw.product_fields(
            [{"field": "ProductName", "value": "Instant Pot"}], [instant])
        self.assertEqual(fields["recall_numbers"],
                         sorted({row["RecallNumber"] for row in rows}))
        self.assertEqual(fields["query.ProductName=Instant Pot.record_count"], len(rows))
        self.assertGreater(len(rows), 0)

    def test_product_fields_empty_result(self):
        smart = cpsc_capture("smart-wifi.http")
        fields = sw.product_fields(
            [{"field": "ProductName", "value": "Instant Pot Smart WiFi"}], [smart])
        self.assertEqual(fields["recall_numbers"], [])
        self.assertEqual(
            fields["query.ProductName=Instant Pot Smart WiFi.record_count"], 0)

    def test_product_fields_bad_response_aborts(self):
        bad = cpsc.Capture("https://www.saferproducts.gov/RestWebServices/Recall"
                           "?format=json&ProductName=X",
                           RETRIEVED, "HTTP/1.1 500 Server Error\r\n\r\n[]")
        with self.assertRaises(cpsc.FetchError):
            sw.product_fields([{"field": "ProductName", "value": "X"}], [bad])


class SnapshotDiffTests(unittest.TestCase):
    def run_fake(self, run_utc, prev=None):
        fake = FakeFetch()
        with mock.patch.object(fc, "fetch", fake.fc_fetch), \
                mock.patch.object(cpsc, "fetch", fake.cpsc_fetch):
            return sw.run_watch(sample_watchlist(), "watchlist.json", prev, run_utc)

    def test_snapshot_provenance_and_hashes(self):
        snapshot, _report, _diff = self.run_fake("2026-10-23T00:00:00Z")
        carrier = snapshot["entries"]["carrier:2046"]
        self.assertEqual([r["source"] for r in carrier["responses"]],
                         ["census", "safer", "li"])
        for response in carrier["responses"]:
            self.assertEqual(
                response["sha256"],
                hashlib.sha256(response["raw"].encode("utf-8")).hexdigest())
            self.assertTrue(response["url"].startswith("https://"))
        # JSON round trip keeps the snapshot readable and identical.
        again = json.loads(json.dumps(snapshot))
        self.assertEqual(again["entries"]["carrier:2046"]["fields"]["census.status_code"], "A")

    def test_identical_runs_have_no_changes(self):
        first, _r1, diff1 = self.run_fake("2026-10-23T00:00:00Z")
        self.assertTrue(all(d["status"] == "baseline" for d in diff1.values()))
        _second, report2, diff2 = self.run_fake("2026-10-24T00:00:00Z", prev=first)
        self.assertTrue(all(d["status"] == "same" for d in diff2.values()))
        self.assertIn("No entry changed in this run.", report2)

    def test_diff_names_old_and_new_values(self):
        # Synthetic mutation of the recorded field map, used only here to
        # exercise the diff: the rating and the recall set are altered
        # copies, not source data.
        first, _r, _d = self.run_fake("2026-10-23T00:00:00Z")
        mutated = json.loads(json.dumps(first))
        mutated["entries"]["carrier:2046"]["fields"]["census.safety_rating"] = "C"
        mutated["entries"]["product:instant-pot"]["fields"]["recall_numbers"] = []
        diff = sw.diff_snapshots(first, mutated)
        self.assertEqual(diff["carrier:2046"]["changes"],
                         [("census.safety_rating", "S", "C")])
        self.assertEqual(diff["product:instant-pot"]["status"], "changed")
        field, old, new = diff["product:instant-pot"]["changes"][0]
        self.assertEqual(field, "recall_numbers")
        self.assertEqual(new, [])
        self.assertTrue(old)

    def test_removed_and_new_entries(self):
        first, _r, _d = self.run_fake("2026-10-23T00:00:00Z")
        smaller = json.loads(json.dumps(first))
        del smaller["entries"]["product:instant-pot-smart-wifi-6-qt"]
        diff = sw.diff_snapshots(first, smaller)
        self.assertEqual(diff["product:instant-pot-smart-wifi-6-qt"]["status"], "removed")
        diff_back = sw.diff_snapshots(smaller, first)
        self.assertEqual(diff_back["product:instant-pot-smart-wifi-6-qt"]["status"], "new")


class ReportTests(unittest.TestCase):
    def run_fake(self, run_utc, prev=None):
        fake = FakeFetch()
        with mock.patch.object(fc, "fetch", fake.fc_fetch), \
                mock.patch.object(cpsc, "fetch", fake.cpsc_fetch):
            return sw.run_watch(sample_watchlist(), "watchlist.json", prev, run_utc)

    def test_baseline_report_carries_fields_and_full_raw(self):
        _snapshot, report, _diff = self.run_fake("2026-10-23T00:00:00Z")
        self.assertIn("# Standing watch: baseline edition", report)
        self.assertIn("| census.status_code | A |", report)
        self.assertIn("| census.safety_rating | S |", report)
        self.assertIn(fc.census_record_url("2046"), report)
        # The empty product result is proven with its full raw response.
        smart_raw = cpsc_capture("smart-wifi.http").raw
        self.assertIn(smart_raw.strip(), report)
        rows = cpsc.records(cpsc_capture("instant-pot.http"))
        self.assertIn(rows[0]["RecallNumber"], report)

    def test_change_report_alerts_and_quiet_lines(self):
        first, _r1, _d1 = self.run_fake("2026-10-23T00:00:00Z")
        # Synthetic mutation again, only to produce a changed carrier:
        # the second run is the recorded run except the rating field in
        # the previous snapshot is altered, so the diff must alert.
        prev = json.loads(json.dumps(first))
        prev["entries"]["carrier:2046"]["fields"]["census.safety_rating"] = "C"
        _snapshot, report, diff = self.run_fake("2026-10-24T00:00:00Z", prev=prev)
        self.assertEqual(diff["carrier:2046"]["status"], "changed")
        self.assertIn("## Change alerts", report)
        self.assertIn("- census.safety_rating: changed from C to S", report)
        self.assertIn("## No change", report)
        self.assertIn("Instant Pot Smart WiFi 6 Qt (product): no change in the "
                      "fields that matter.", report)
        # The unchanged product's full raw is not dumped in a change report;
        # it lives in the snapshot, named by its hash in the report.
        smart_raw = cpsc_capture("smart-wifi.http").raw
        self.assertNotIn(smart_raw.strip(), report)
        self.assertIn(hashlib.sha256(smart_raw.encode("utf-8")).hexdigest(), report)

    def test_transport_failure_aborts_the_run(self):
        def boom(url):
            raise urllib.error.URLError("no route")
        with mock.patch.object(fc, "fetch", boom):
            with self.assertRaises(urllib.error.URLError):
                sw.run_watch(sample_watchlist(), "watchlist.json", None,
                             "2026-10-23T00:00:00Z")


class SnapshotFileTests(unittest.TestCase):
    def test_missing_snapshot_is_none_and_garbage_is_an_error(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / "nope.json"
            self.assertIsNone(sw.load_snapshot(missing))
            bad = Path(folder) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            with self.assertRaises(sw.WatchError):
                sw.load_snapshot(bad)


if __name__ == "__main__":
    unittest.main()
