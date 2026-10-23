"""CI entry for the media generator agent tests (issue #78).

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to agents/media-generator/tests, where the agent's own
suite lives, so it runs in CI without a workflow change. No test logic
lives here. A fresh TestLoader is used for the nested discovery for the
same reason as tools/tests/test_near_agent.py.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "agents" / "media-generator" / "tests")
    nested = unittest.TestLoader()
    return nested.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
