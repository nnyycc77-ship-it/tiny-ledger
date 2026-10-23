"""CI entry for the local services quote agent tests (agents/local-quotes, issue #76).

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to agents/local-quotes/tests, where the agent's own
suite lives, so it runs in CI without a workflow change. No test logic
lives here. The nested discovery uses a fresh TestLoader, for the reason
recorded in test_catering_finder.py.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "agents" / "local-quotes" / "tests")
    nested = unittest.TestLoader()
    return nested.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
