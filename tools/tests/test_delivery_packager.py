"""Tests for tools/delivery_packager.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_delivery_packager.py' -v

The committed examples replay real captures committed in this repo (see
tools/delivery-packager/README.md). One input below is not a recording
and is labelled as such: the CourtListener response used by the
litigation adapter test is SYNTHETIC, so the adapter is exercised on a
second shape besides the committed capture.
"""

import contextlib
import difflib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import courtlistener_recap as cl  # noqa: E402
import delivery_packager as dp  # noqa: E402

PK = TOOLS / "delivery-packager"
EXAMPLES = PK / "examples"
REPLAYED = ("recall", "carrier", "litigation", "formd", "nonprofit", "awards")
TIMING_FIELDS = {"run_started_utc", "service", "subject", "mode", "job", "bundle", "package_dir", "requests",
                 "fetch_seconds", "assemble_seconds", "verify_seconds", "total_seconds", "total_minutes",
                 "deliverable_sha256", "verify"}


def read_raw(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write_raw(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args, **kwargs)


class CommittedExamples(unittest.TestCase):
    def test_every_replayed_example_verifies_with_its_hash_in_the_timing_log(self):
        for name in REPLAYED:
            with self.subTest(name=name):
                self.assertEqual(dp.verify(EXAMPLES / name, PK / "timing-log.jsonl"), [])

    def test_examples_rebuild_byte_for_byte_from_their_job_and_bundle(self):
        for name in REPLAYED:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                manifest = json.loads((EXAMPLES / name / "manifest.json").read_text(encoding="utf-8"))
                failures, entry = dp.package(PK / "jobs" / ("%s.json" % name), Path(tmp) / name,
                                             replay=PK / "bundles" / ("%s.json" % name),
                                             packaged_utc=manifest["packaged_utc"])
                self.assertEqual(failures, [])
                self.assertEqual((Path(tmp) / name / "report.md").read_bytes(),
                                 (EXAMPLES / name / "report.md").read_bytes())
                self.assertEqual(json.loads((Path(tmp) / name / "manifest.json").read_text(encoding="utf-8")), manifest)
                self.assertEqual(entry["mode"], "replay")

    def test_timing_log_has_one_passing_line_per_example(self):
        lines = [json.loads(line) for line in (PK / "timing-log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(sorted(e["service"] for e in lines), sorted(REPLAYED))
        for e in lines:
            manifest = json.loads((EXAMPLES / e["service"] / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(set(e), TIMING_FIELDS)
            self.assertEqual(e["verify"], "PASS")
            self.assertEqual(e["mode"], "replay")
            self.assertEqual(e["deliverable_sha256"], manifest["deliverable_sha256"])
            self.assertAlmostEqual(e["total_minutes"], e["total_seconds"] / 60.0, places=3)

    def test_every_summary_line_names_a_section(self):
        for name in REPLAYED:
            summary, sections, order = dp.split_report(read_raw(EXAMPLES / name / "report.md"))
            self.assertTrue(summary)
            for line in summary:
                m = dp.SUMMARY_LINE_RE.match(line)
                self.assertIsNotNone(m, line)
                self.assertIn(m.group(3), sections)

    def test_no_price_field_anywhere_in_the_log_or_manifests(self):
        def keys(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    yield k
                    yield from keys(v)
            elif isinstance(node, list):
                for v in node:
                    yield from keys(v)
        docs = [json.loads(line) for line in (PK / "timing-log.jsonl").read_text(encoding="utf-8").splitlines()]
        docs += [json.loads((EXAMPLES / n / "manifest.json").read_text(encoding="utf-8")) for n in REPLAYED]
        for doc in docs:
            for k in keys(doc):
                self.assertNotRegex(k.lower(), r"price|dollar|per_minute|^usd$|_usd$|^fee", k)


class UnsourcedExample(unittest.TestCase):
    DIR = EXAMPLES / "unsourced-SYNTHETIC"

    def test_fails_for_exactly_the_documented_reasons(self):
        failures = dp.verify(self.DIR)
        self.assertEqual(len(failures), 3, failures)
        self.assertTrue(failures[0].startswith("Section S2: the complete raw response for "
                                               "https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128 "
                                               "is not printed in the section"))
        self.assertEqual(failures[1], "Section S2: the count cpsc_records has no printed raw response to recount from")
        self.assertEqual(failures[2], "unsourced summary claim (names no section): - No other recall applies to this product.")

    def test_cli_exit_status_is_one(self):
        self.assertEqual(quiet(dp.main, ["verify", "--dir", str(self.DIR)]), 1)

    def test_differs_from_the_recall_example_only_as_its_readme_says(self):
        good = read_raw(EXAMPLES / "recall" / "report.md").split("\n")
        bad = read_raw(self.DIR / "report.md").split("\n")
        ops = [op for op in difflib.SequenceMatcher(None, good, bad, autojunk=False).get_opcodes() if op[0] != "equal"]
        self.assertEqual([op[0] for op in ops], ["insert", "insert", "delete"], ops)
        label = bad[ops[0][3]:ops[0][4]]
        self.assertEqual(len(label), 2)
        self.assertEqual(sorted(label)[0], "")  # the label line and its blank line, in either diff alignment
        self.assertTrue(sorted(label)[1].startswith("SYNTHETIC TEST INPUT, not a delivery: "))
        self.assertEqual(bad[ops[1][3]:ops[1][4]], ["- No other recall applies to this product."])
        removed = good[ops[2][1]:ops[2][2]]
        self.assertEqual(removed[0], "Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128>")
        self.assertTrue(dp.FENCE_RE.match(removed[1]) and removed[-1] == removed[1])
        self.assertGreater(ops[2][1], good.index([l for l in good if l.startswith("## Section S2:")][0]))
        manifest = json.loads((self.DIR / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["deliverable_sha256"], hashlib.sha256((self.DIR / "report.md").read_bytes()).hexdigest())


class Checks(unittest.TestCase):
    """Break one check at a time on a freshly packaged recall example."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dir = Path(self.tmp) / "pkg"
        self.log = Path(self.tmp) / "timing.jsonl"
        failures, _ = dp.package(PK / "jobs" / "recall.json", self.dir, replay=PK / "bundles" / "recall.json",
                                 timing_log=self.log)
        self.assertEqual(failures, [])
        self.report = read_raw(self.dir / "report.md")
        self.manifest = json.loads((self.dir / "manifest.json").read_text(encoding="utf-8"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rewrite(self, report=None, manifest=None, rehash=True):
        report = self.report if report is None else report
        manifest = dict(self.manifest if manifest is None else manifest)
        write_raw(self.dir / "report.md", report)
        if rehash:
            manifest["deliverable_sha256"] = hashlib.sha256(report.encode("utf-8")).hexdigest()
        (self.dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_fresh_package_passes_with_its_timing_line(self):
        self.assertEqual(dp.verify(self.dir, self.log), [])

    def test_stated_count_changed_in_the_section_fails(self):
        self.rewrite(self.report.replace("CPSC returned 1 record(s) for this query.",
                                         "CPSC returned 2 record(s) for this query.", 1))
        self.assertEqual(dp.verify(self.dir), ["Section S1: count mismatch for cpsc_records: section states 2, "
                                               "manifest records 1, raw response recounts to 1"])

    def test_count_changed_in_manifest_and_summary_still_fails_on_the_recount(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["sections"][0]["counts"][0]["value"] = "2"
        report = self.report.replace('"Tread+": 1. (Section S1)', '"Tread+": 2. (Section S1)')
        report = report.replace("CPSC returned 1 record(s) for this query.", "CPSC returned 2 record(s) for this query.", 1)
        self.rewrite(report, manifest)
        failures = dp.verify(self.dir)
        self.assertEqual(failures, ["Section S1: count mismatch for cpsc_records: section states 2, manifest records 2, "
                                    "raw response recounts to 1"])

    def test_missing_deliverable_hash_fails(self):
        manifest = dict(self.manifest)
        del manifest["deliverable_sha256"]
        self.rewrite(manifest=manifest, rehash=False)
        self.assertIn("deliverable hash not recorded in the manifest", dp.verify(self.dir))

    def test_report_edited_after_packaging_fails_the_hash(self):
        self.rewrite(self.report + "\nAn added line.\n", rehash=False)
        self.assertTrue(any(f.startswith("deliverable hash does not match the report") for f in dp.verify(self.dir)))

    def test_hash_absent_from_the_timing_log_fails(self):
        self.log.write_text("", encoding="utf-8")
        self.assertIn("deliverable hash not recorded in the timing log %s" % self.log, dp.verify(self.dir, self.log))

    def test_summary_line_without_a_section_fails(self):
        self.rewrite(self.report.replace("## Summary\n\n", "## Summary\n\n- The product is fine.\n", 1))
        self.assertEqual(dp.verify(self.dir), ["unsourced summary claim (names no section): - The product is fine."])

    def test_summary_line_naming_an_absent_section_fails(self):
        self.rewrite(self.report.replace("(Section S2)", "(Section S9)", 1))
        self.assertEqual(len(dp.verify(self.dir)), 1)
        self.assertIn("names Section S9, which is not in the package", dp.verify(self.dir)[0])

    def test_summary_value_not_recorded_fails(self):
        self.rewrite(self.report.replace('"21-128": 1. (Section S2)', '"21-128": 3. (Section S2)', 1))
        self.assertEqual(len(dp.verify(self.dir)), 1)
        self.assertIn("does not match a count recorded for Section S2", dp.verify(self.dir)[0])

    def test_section_with_no_recorded_capture_fails(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["sections"][1]["captures"] = []
        self.rewrite(manifest=manifest)
        failures = dp.verify(self.dir)
        self.assertIn("Section S2 carries claims without a source: no capture is recorded for it", failures)

    def test_retrieval_time_removed_from_the_section_fails(self):
        retrieved = self.manifest["sections"][0]["captures"][0]["retrieved_utc"]
        head, sep, tail = self.report.partition("## Section S2:")
        head = head.replace("Retrieved (UTC): %s" % retrieved, "Retrieved (UTC): (removed)")
        self.rewrite(head + sep + tail)
        self.assertTrue(any(f.startswith("Section S1: the retrieval time %s" % retrieved) for f in dp.verify(self.dir)))

    def test_report_file_outside_the_package_is_refused(self):
        manifest = dict(self.manifest)
        manifest["report_file"] = "../report.md"
        self.rewrite(manifest=manifest)
        self.assertEqual(len(dp.verify(self.dir)), 1)
        self.assertIn("must be a file name inside the package", dp.verify(self.dir)[0])

    def test_unknown_or_dropped_section_fails(self):
        self.rewrite(self.report.replace("## Section S2:", "## Section S3:", 1))
        self.assertTrue(any("do not match the manifest sections" in f for f in dp.verify(self.dir)))


class Replay(unittest.TestCase):
    def test_request_outside_the_bundle_stops_the_run_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = json.loads((PK / "jobs" / "recall.json").read_text(encoding="utf-8"))
            job["inputs"]["queries"].append({"field": "ProductName", "value": "Not in the bundle"})
            (Path(tmp) / "job.json").write_text(json.dumps(job), encoding="utf-8")
            with self.assertRaises(dp.PackageError) as ctx:
                dp.package(Path(tmp) / "job.json", Path(tmp) / "out", replay=PK / "bundles" / "recall.json")
            self.assertIn("not in the capture bundle", str(ctx.exception))
            self.assertFalse((Path(tmp) / "out").exists())
            self.assertEqual(quiet(dp.main, ["package", "--job", str(Path(tmp) / "job.json"), "--out",
                                            str(Path(tmp) / "out2"), "--replay", str(PK / "bundles" / "recall.json")]), 2)

    def test_bundle_entry_pointing_at_the_wrong_capture_is_refused(self):
        bundle = json.loads((PK / "bundles" / "recall.json").read_text(encoding="utf-8"))
        bundle["captures"][0]["origin"]["index"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
            with self.assertRaises(dp.PackageError) as ctx:
                dp.package(PK / "jobs" / "recall.json", Path(tmp) / "out", replay=Path(tmp) / "bundle.json")
            self.assertIn("is for", str(ctx.exception))

    def test_every_bundle_capture_loads_and_matches_its_record(self):
        for name in REPLAYED:
            bundle = json.loads((PK / "bundles" / ("%s.json" % name)).read_text(encoding="utf-8"))
            for entry in bundle["captures"]:
                url, retrieved, transcript, origin = dp.load_origin(entry)
                self.assertTrue(retrieved.startswith("2026-10-23T"), (name, retrieved))
                self.assertIn("replayed from", origin)

    def test_cli_package_exit_zero_and_bad_job_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(quiet(dp.main, ["package", "--job", str(PK / "jobs" / "awards.json"), "--out",
                                            str(Path(tmp) / "a"), "--replay", str(PK / "bundles" / "awards.json")]), 0)
            (Path(tmp) / "bad.json").write_text(json.dumps({"service": "astrology", "subject": "x",
                                                            "buyer_ask": "y", "inputs": {}}), encoding="utf-8")
            self.assertEqual(quiet(dp.main, ["package", "--job", str(Path(tmp) / "bad.json"), "--out",
                                            str(Path(tmp) / "b")]), 2)
            self.assertFalse((Path(tmp) / "b").exists())


class JobSpec(unittest.TestCase):
    def test_blank_buyer_ask_and_missing_inputs_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for job in ({"service": "recall", "subject": "x", "buyer_ask": " ", "inputs": {}},
                        {"service": "recall", "subject": "x", "buyer_ask": "y"}):
                (Path(tmp) / "j.json").write_text(json.dumps(job), encoding="utf-8")
                with self.assertRaises(dp.PackageError):
                    dp.load_job(Path(tmp) / "j.json")

    def test_near_query_without_exact_name_is_refused(self):
        with self.assertRaises(dp.PackageError):
            dp.adapt_recall({"queries": [{"field": "ProductName", "value": "x", "near": True}]}, dp.Source())


# SYNTHETIC: a hand written CourtListener search body in the field shape the
# fetcher reads (count, next, previous, results of docket objects). Every
# name, number and date in it is invented; it describes no real case.
SYNTHETIC_CL_BODY = json.dumps({
    "count": 2, "next": None, "previous": None,
    "results": [
        {"docket_id": 900001, "docketNumber": "1:26-cv-00001", "court": "SYNTHETIC District Court",
         "caseName": "Synthetic Example Corp. v. Placeholder Holdings", "dateFiled": "2026-01-02",
         "suitNature": "", "cause": "", "dateTerminated": None},
        {"docket_id": 900002, "docketNumber": "1:26-cv-00002", "court": "SYNTHETIC District Court",
         "caseName": "Placeholder Holdings v. Synthetic Example Corp.", "dateFiled": "2026-01-03",
         "suitNature": "", "cause": "", "dateTerminated": "2026-02-01"},
    ]})


class SyntheticCourtListenerSource(dp.Source):
    mode = "replay"

    def _obtain(self, kind, key):
        assert kind == "courtlistener"
        transcript = "HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + SYNTHETIC_CL_BODY
        status, headers, body = dp.split_transcript(transcript)
        return cl.Capture(key, "2026-10-23T23:00:00Z", status, headers, body), "SYNTHETIC test response, not a capture"


class Litigation(unittest.TestCase):
    JOB = {"service": "litigation", "subject": "Synthetic Example Corp. (SYNTHETIC)", "buyer_ask": "SYNTHETIC test ask",
           "inputs": {"parties": ["Synthetic Example Corp."], "filed_after": "2021-10-23", "list": 10}}

    def test_adapter_packages_and_verifies_on_a_synthetic_response(self):
        report, manifest = dp.build(self.JOB, SyntheticCourtListenerSource(), "2026-10-23T23:00:00Z")
        self.assertEqual(manifest["sections"][0]["counts"][0]["rule"], "cl_window_count")
        self.assertEqual(manifest["sections"][0]["counts"][0]["value"], "2")
        with tempfile.TemporaryDirectory() as tmp:
            write_raw(Path(tmp) / "report.md", report)
            (Path(tmp) / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(dp.verify(tmp), [])

    def test_litigation_example_labels_its_body_only_capture(self):
        report = read_raw(EXAMPLES / "litigation" / "report.md")
        self.assertIn("the status line above it is built from the capturer's stated HTTP 200, and no headers were captured",
                      report)
        prov = json.loads((PK / "captures" / "provenance.json").read_text(encoding="utf-8"))
        entry = prov["courtlistener-search-jabil-inc.json"]
        self.assertEqual(entry["posted_at"], "https://github.com/nnyycc77-ship-it/tiny-ledger/issues/154#issuecomment-6377076098")
        body = (PK / "captures" / "courtlistener-search-jabil-inc.json").read_bytes()
        self.assertEqual(len(body), 15532)
        self.assertEqual(hashlib.sha256(body).hexdigest(), entry["sha256"])
        self.assertIn(body.decode("utf-8"), report)
        manifest = json.loads((EXAMPLES / "litigation" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["sections"][0]["counts"][0]["value"], "15")

if __name__ == "__main__":
    unittest.main()
