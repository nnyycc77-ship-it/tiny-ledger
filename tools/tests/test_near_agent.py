"""CI entry for the near-agent worker tests.

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to near-agent/tests, where the worker's own suite lives
(issue #48 asks for the folder to carry its own tests), so the suite runs
in CI without a workflow change. No test logic lives here.

The nested discovery runs on a fresh TestLoader, not on the loader passed
in. Before Python 3.13, TestLoader.discover() does not restore its
_top_level_dir when it returns, so a nested discover on the outer loader
left it pointing at near-agent/tests and every tools/tests module loaded
after this one failed with "Path must be within the project" (reproduced
on Python 3.11.17 and 3.12.3; the coordinator saw the same on PR #52).
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "near-agent" / "tests")
    nested = unittest.TestLoader()
    return nested.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
