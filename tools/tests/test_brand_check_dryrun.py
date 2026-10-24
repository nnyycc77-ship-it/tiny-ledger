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
import brand_name_checker as bnc  # noqa: E402
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

    def test_the_required_cases_exist(self):
        # taken, free and mixed from issue #137; retry from issue #220.
        self.assertEqual([c["case"] for c in CASES], ["taken", "free", "mixed", "retry"])
        taken = next(c for c in CASES if c["case"] == "taken")
        self.assertTrue(all("synthetic" not in r for r in taken["routes"].values()))


class DryRunTests(unittest.TestCase):
    def test_every_verdict_matches_offline(self):
        code, out, err = run()
        self.assertEqual((code, err), (0, ""))
        # 15 verdicts from issue #137, plus 12 for the retry case (issue #220).
        self.assertIn("Result: 27 of 27 verdicts matched.", out)
        self.assertNotIn("MISMATCH", out)

    def test_no_key_trademark_leg_keeps_the_unconfirmed_wording(self):
        code, out, _ = run(["--report"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("| trademark | not covered (unconfirmed wording) | not covered (unconfirmed "
                                   "wording) | match |"), 4)
        self.assertEqual(out.count("### Trademarks\n\n" + UNCONFIRMED + "\n"), 4)

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
        self.assertEqual(out.count("| trademark | not covered (unconfirmed wording) | WORDING CHANGED | MISMATCH |"), 4)

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
        self.assertIn("26 of 27 verdicts matched; 1 MISMATCH", out)

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


class RetryCaseTests(unittest.TestCase):
    """Issue #220: the single retry on no response (issue #201), through the checker's real get()."""

    def retry_section(self, argv=()):
        code, out, err = run(argv)
        self.assertEqual((code, err), (0, ""))
        return out.split("## Case retry")[1]

    def test_no_response_then_404_is_retried_once(self):
        section = self.retry_section()
        self.assertIn("| domain com | no registration found | no registration found | match |", section)
        self.assertIn("| domain com requests | 2 | 2 | match |", section)
        self.assertIn("| domain com retry note | present | present | match |", section)

    def test_no_response_twice_is_could_not_confirm_never_free(self):
        section = self.retry_section()
        self.assertIn("| domain io | could not confirm | could not confirm | match |", section)
        self.assertIn("| domain io requests | 2 | 2 | match |", section)

    def test_an_http_status_is_answered_once_with_no_retry(self):
        section = self.retry_section()
        self.assertIn("| domain net | could not confirm | could not confirm | match |", section)
        self.assertIn("| domain net requests | 1 | 1 | match |", section)
        self.assertIn("| domain net retry note | absent | absent | match |", section)

    def test_the_rendered_report_carries_the_retried_once_line(self):
        section = self.retry_section(["--report"])
        self.assertIn("| retryvexa.com | no registration found | HTTP 404 Not Found | replayed |", section)
        self.assertIn("request failed: SYNTHETIC: Remote end closed connection without response\n"
                      "[retried once: the first attempt got no response: SYNTHETIC: Remote end closed", section)
        self.assertEqual(section.count("[retried once:"), 2)  # com and io; net was not retried

    def test_a_checker_without_the_retry_would_be_caught(self):
        single = lambda url, read_body: bnc._attempt(url, read_body)[0]  # get() as it was before #201
        with mock.patch.object(bnc, "get", single):
            code, out, _ = run()
        self.assertEqual(code, 1)
        self.assertIn("| domain com | no registration found | could not confirm | MISMATCH |", out)
        self.assertIn("| domain com requests | 2 | 1 | MISMATCH |", out)

    def test_more_requests_than_recorded_stop_the_run(self):
        replay = dry.Replay({"https://rdap.org/domain/once.com": {
            "synthetic": "SYNTHETIC", "attempts": [{"no_response": "SYNTHETIC: closed"}]}}, {}, {})
        with mock.patch("urllib.request.urlopen", no_network), self.assertRaises(dry.HarnessError):
            replay("https://rdap.org/domain/once.com", True)

    def test_an_attempt_that_is_not_no_response_or_an_error_status_is_refused(self):
        for attempt in ({"status": 200}, {"status": "404"}, {}):  # SYNTHETIC malformed recordings
            replay = dry.Replay({"https://rdap.org/domain/bad.com": {"synthetic": "SYNTHETIC", "attempts": [
                attempt]}}, {}, {})
            with mock.patch("urllib.request.urlopen", no_network), self.assertRaises(dry.HarnessError):
                replay("https://rdap.org/domain/bad.com", True)

    def test_the_stub_is_removed_after_each_call(self):
        replay = dry.Replay({"https://rdap.org/domain/x.com": {"synthetic": "SYNTHETIC", "attempts": [
            {"status": 503}]}}, {}, {})
        with mock.patch("urllib.request.urlopen", no_network):
            replay("https://rdap.org/domain/x.com", True)
            import urllib.request
            self.assertIs(urllib.request.urlopen, no_network)


if __name__ == "__main__":
    unittest.main()
