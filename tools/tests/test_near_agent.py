"""CI entry for the near-agent worker tests.

The delivery-tool-tests job discovers tools/tests only. This module hands
that discovery on to near-agent/tests, where the worker's own suite lives
(issue #48 asks for the folder to carry its own tests), so the suite runs
in CI without a workflow change. No test logic lives here.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    start = str(ROOT / "near-agent" / "tests")
    return loader.discover(start_dir=start, pattern="test_*.py", top_level_dir=start)
