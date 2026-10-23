"""CI entry for the field service planner tests (issue #73).

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to agents/field-service-planner/tests, where the agent's
own suite lives, so it runs in CI without a workflow change. No test logic
lives here. The nested discovery runs on a fresh TestLoader for the reason
recorded in test_near_agent.py (TestLoader.discover() before Python 3.13
does not restore its top level directory).
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "agents" / "field-service-planner" / "tests")
    nested = unittest.TestLoader()
    return nested.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
