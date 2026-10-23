"""Tests for tools/uspto_trademarks.py (issue #125). No network, no key.

Run:  python3 -m unittest discover -s tools/tests -p 'test_uspto_trademarks.py' -v

Fixtures (tools/tests/fixtures/uspto/, recorded in provenance.json): neither
is a USPTO response. no-key-report.md is the whole report main printed at
d46c1c1, before this issue, for the run below; refusal-stderr.txt is this
branch's stderr for the same run with a placeholder key set. The fake fetch
answers every request with a SYNTHETIC transport failure, so the report is
deterministic. The key values here are placeholder strings, not
credentials.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import brand_name_checker as bnc  # noqa: E402
import uspto_trademarks as tm  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "uspto"
PROVENANCE = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
MAIN_REPORT = (FIX / "no-key-report.md").read_text(encoding="utf-8")
REFUSAL = (FIX / "refusal-stderr.txt").read_text(encoding="utf-8")
ARGV = ["Nike", "zqxflorp", "--trademark-countries", "US,EU", "--variations", "2"]
PLACEHOLDER_KEY = "placeholder-not-a-real-uspto-key"

# Today's section, word for word as the checker printed it before issue #125.
TODAY = ("### Trademarks\n\nNot covered. No working trademark source has been captured for this tool, so no "
         "trademark search was run and no mark or status is stated. The database it would search: USPTO "
         "trademark search (United States). Countries requested: US, EU.\n\n")


def fetch(url, read_body):
    # SYNTHETIC: a fixed transport failure for every request, as in the fixtures.
    return bnc.Result(url, url, "2026-10-23T00:00:00Z", None, None, [], None, "SYNTHETIC failure")


def run(env):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = bnc.main(ARGV, fetch=fetch, env=env)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name in ("no-key-report.md", "refusal-stderr.txt"):
            self.assertEqual(hashlib.sha256((FIX / name).read_bytes()).hexdigest(), PROVENANCE[name]["sha256"])
        self.assertIn("SYNTHETIC", PROVENANCE["_about"])

    def test_main_report_carries_todays_section_once_per_name(self):
        self.assertEqual(MAIN_REPORT.count(TODAY), 2)


class KeyTests(unittest.TestCase):
    def test_key_comes_from_the_one_variable_only(self):
        self.assertIsNone(tm.read_key({}))
        self.assertIsNone(tm.read_key({tm.KEY_ENV: "   "}))
        self.assertIsNone(tm.read_key({"USPTO_KEY": PLACEHOLDER_KEY, "API_KEY": PLACEHOLDER_KEY}))
        self.assertEqual(tm.read_key({tm.KEY_ENV: " %s\n" % PLACEHOLDER_KEY}), PLACEHOLDER_KEY)
        self.assertEqual(tm.KEY_ENV, "USPTO_API_KEY")


class FailClosedTests(unittest.TestCase):
    def test_no_key_report_equals_mains_report_byte_for_byte(self):
        code, out, err = run({})
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, MAIN_REPORT)

    def test_a_key_alone_upgrades_nothing_and_is_never_printed(self):
        code, out, err = run({tm.KEY_ENV: PLACEHOLDER_KEY})
        self.assertEqual(code, 0)
        self.assertEqual(out, MAIN_REPORT)
        self.assertEqual(err, REFUSAL)
        self.assertNotIn(PLACEHOLDER_KEY, out + err)

    def test_request_builder_and_response_reader_refuse_to_run(self):
        with self.assertRaises(tm.NotDocumented):
            tm.build_search_request("Nike", PLACEHOLDER_KEY)
        with self.assertRaises(tm.NotDocumented):
            tm.read_search_response('{"SYNTHETIC": "any body at all"}')

    def test_section_alone(self):
        self.assertEqual("\n".join(tm.section("Nike", ["US", "EU"], {})) + "\n", TODAY)
        err = io.StringIO()
        lines = tm.section("Nike", ["US", "EU"], {tm.KEY_ENV: PLACEHOLDER_KEY}, stderr=err)
        self.assertEqual("\n".join(lines) + "\n", TODAY)
        self.assertIn("NOT", tm.build_search_request.__doc__)
        self.assertIn("did not run", err.getvalue())


if __name__ == "__main__":
    unittest.main()
