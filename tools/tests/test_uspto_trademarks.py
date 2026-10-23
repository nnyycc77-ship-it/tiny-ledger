"""Tests for tools/uspto_trademarks.py (issue #125). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_uspto_trademarks.py' -v

The key values below are placeholder strings, not credentials. The fake
fetch answers every request with a SYNTHETIC transport failure so the
whole report is deterministic; only the trademark section is under test.
"""

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import brand_name_checker as bnc  # noqa: E402
import uspto_trademarks as tm  # noqa: E402

PLACEHOLDER_KEY = "placeholder-not-a-real-uspto-key"

# Today's section, word for word as the checker printed it before issue #125.
TODAY = ("### Trademarks\n\nNot covered. No working trademark source has been captured for this tool, so no "
         "trademark search was run and no mark or status is stated. The database it would search: USPTO "
         "trademark search (United States). Countries requested: US, EU.\n\n")


def fetch(url, read_body):
    # SYNTHETIC: a fixed transport failure for every request.
    return bnc.Result(url, url, "2026-10-23T00:00:00Z", None, None, [], None, "SYNTHETIC failure")


def run(env):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = bnc.main(["Nike", "--trademark-countries", "US,EU"], fetch=fetch, env=env)
    return code, out.getvalue(), err.getvalue()


class KeyTests(unittest.TestCase):
    def test_key_comes_from_the_one_variable_only(self):
        self.assertIsNone(tm.read_key({}))
        self.assertIsNone(tm.read_key({tm.KEY_ENV: "   "}))
        self.assertIsNone(tm.read_key({"USPTO_KEY": PLACEHOLDER_KEY, "API_KEY": PLACEHOLDER_KEY}))
        self.assertEqual(tm.read_key({tm.KEY_ENV: " %s\n" % PLACEHOLDER_KEY}), PLACEHOLDER_KEY)


class UnconfirmedTests(unittest.TestCase):
    def test_no_key_keeps_todays_wording_word_for_word(self):
        code, out, err = run({})
        self.assertEqual((code, err), (0, ""))
        self.assertIn(TODAY, out)
        self.assertEqual("\n".join(tm.section("Nike", ["US", "EU"], {})) + "\n", TODAY)

    def test_a_key_alone_upgrades_nothing_and_is_never_printed(self):
        _, without, _ = run({})
        code, with_key, err = run({tm.KEY_ENV: PLACEHOLDER_KEY})
        self.assertEqual(code, 0)
        self.assertEqual(with_key, without)
        self.assertIn("USPTO_API_KEY is set, but the USPTO search request is not documented", err)
        self.assertNotIn(PLACEHOLDER_KEY, with_key + err)


if __name__ == "__main__":
    unittest.main()
