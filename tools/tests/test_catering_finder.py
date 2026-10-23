"""CI entry for the catering finder agent tests (agents/catering-finder, issue #75).

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to agents/catering-finder/tests, where the agent's own
suite lives, so it runs in CI without a workflow change. No test logic
lives here.

The nested discovery runs on a fresh TestLoader, not on the loader passed
in, for the reason recorded in test_near_agent.py: before Python 3.13 a
nested discover on the outer loader leaves its _top_level_dir pointing at
the nested folder and breaks every module loaded after it.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "agents" / "catering-finder" / "tests")
    nested = unittest.TestLoader()
    return nested.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
