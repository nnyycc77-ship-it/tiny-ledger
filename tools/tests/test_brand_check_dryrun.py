"""Tests for tools/brand_check_dryrun.py (issue #137). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_brand_check_dryrun.py' -v

The harness replays the recorded responses in
fixtures/brandcheck-dryrun/cases.json: real captures and real status
records from issue #51, and SYNTHETIC bodies labelled inside their own
files. These tests also run it with urlopen replaced by a function that
fails the test, to prove no live call happens.
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import brand_check_dryrun as dry  # noqa: E402
import uspto_trademarks  # noqa: E402

CASES = json.loads(dry.CASES_FILE.read_text(encoding="utf-8"))["cases"]
UNCONFIRMED = uspto_trademarks.UNCONFIRMED % "US"


def no_network(*args, **kwargs):
    raise AssertionError("a dry run tried to reach the network: %r" % (args[:1],))


def run(argv=()):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = dry.main(list(argv), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class ProvenanceTests(unittest.TestCase):
    def test_every_route_names_its_kind_and_every_body_is_hashed(self):
        hashes = dry.recorded_hashes()
        for case in CASES:
            for url, route in case["routes"].items():
                kinds = [k for k in ("capture", "status_record", "synthetic") if k in route]
                self.assertEqual(len(kinds), 1, (case["case"], url))
                source = route.get("capture") or route.get("synthetic")
                if source and source.endswith(".json"):
                    self.assertIn((dry.FIXTURES / source).resolve(), hashes, source)
                    dry.read_body(source, hashes)  # raises when altered

    def test_synthetic_bodies_say_so_inside_the_file(self):
        for path in (dry.FIXTURES / "brandcheck-dryrun").glob("synthetic-*.json"):
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["_SYNTHETIC"].startswith("SYNTHETIC"),
                            path.name)
        for case in CASES:
            for route in case["routes"].values():
                if "synthetic" in route and not route["synthetic"].endswith(".json"):
                    self.assertTrue(route["synthetic"].startswith("SYNTHETIC"), route)

    def test_the_three_required_cases_exist(self):
        self.assertEqual([c["case"] for c in CASES], ["taken", "free", "mixed"])
        taken = next(c for c in CASES if c["case"] == "taken")
        self.assertTrue(all("synthetic" not in r for r in taken["routes"].values()))


class DryRunTests(unittest.TestCase):
    def test_every_verdict_matches_offline(self):
        code, out, err = run()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Result: 15 of 15 verdicts matched.", out)
        self.assertNotIn("MISMATCH", out)

    def test_no_key_trademark_leg_keeps_the_unconfirmed_wording(self):
        code, out, _ = run(["--report"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("| trademark | not covered (unconfirmed wording) | not covered (unconfirmed "
                                   "wording) | match |"), 3)
        self.assertEqual(out.count("### Trademarks\n\n" + UNCONFIRMED + "\n"), 3)

    def test_rendered_reports_carry_the_replayed_evidence(self):
        _, out, _ = run(["--report"])
        self.assertIn('"ldhName":"NIKE.COM"', out)
        self.assertIn("(replayed, real capture from issue #51;", out)
        self.assertIn("(replayed, real status recorded on issue #51;", out)
        self.assertIn("(replayed, SYNTHETIC;", out)
        mixed = out.split("## Case mixed")[1]
        self.assertNotIn("real capture from issue #51", mixed)
        self.assertIn("SYNTHETIC: connection reset", out)

    def test_a_changed_trademark_wording_is_caught(self):
        changed = lambda name, countries, env=None: ["### Trademarks", "", "Covered: no conflicting marks.", ""]
        with mock.patch.object(dry.uspto_trademarks, "section", changed):
            code, out, _ = run()
        self.assertEqual(code, 1)
        self.assertEqual(out.count("| trademark | not covered (unconfirmed wording) | WORDING CHANGED | MISMATCH |"), 3)

    def test_a_wrong_expectation_is_reported_as_a_mismatch(self):
        cases = json.loads(dry.CASES_FILE.read_text(encoding="utf-8"))
        cases["cases"][1]["expect"]["x"] = "taken (live account)"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            path.write_text(json.dumps(cases), encoding="utf-8")
            with mock.patch.object(dry, "CASES_FILE", path):
                code, out, _ = run()
        self.assertEqual(code, 1)
        self.assertIn("| x | taken (live account) | no account found | MISMATCH |", out)
        self.assertIn("14 of 15 verdicts matched; 1 MISMATCH", out)

    def test_an_altered_fixture_or_unrecorded_url_stops_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "fixtures"
            shutil.copytree(dry.FIXTURES / "brandcheck", fixtures / "brandcheck")
            shutil.copytree(dry.FIXTURES / "brandcheck-dryrun", fixtures / "brandcheck-dryrun")
            body = fixtures / "brandcheck-dryrun" / "synthetic-itunes-quillvexa.json"
            body.write_text(body.read_text(encoding="utf-8").replace("Seller One", "Seller 1"), encoding="utf-8")
            patches = dict(FIXTURES=fixtures, CASES_FILE=fixtures / "brandcheck-dryrun" / "cases.json",
                           STATUS_FILE=fixtures / "brandcheck" / "status-captures.json",
                           PROVENANCE_FILES=(fixtures / "brandcheck" / "provenance.json",
                                             fixtures / "brandcheck-dryrun" / "provenance.json"))
            with contextlib.ExitStack() as stack:
                for key, value in patches.items():
                    stack.enter_context(mock.patch.object(dry, key, value))
                code, out, err = run()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("does not match its recorded SHA-256", err)

        replay = dry.Replay({}, {}, {})
        with self.assertRaises(dry.HarnessError):
            replay("https://rdap.org/domain/unrecorded.com", True)


if __name__ == "__main__":
    unittest.main()
