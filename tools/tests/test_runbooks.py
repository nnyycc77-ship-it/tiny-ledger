"""Checks the award readiness runbooks (issue #98) against the code they cite.

Run:  python3 -m unittest discover -s tools/tests -p 'test_runbooks.py' -v

Each runbook must keep its required sections; every `near-agent/worker.py`
command line in it must parse with the worker's own argument parser (so a
runbook cannot name a subcommand or option the worker does not have); every
repository path it cites must exist; every test directory it tells the
operator to run must exist; an agent runbook's job id must match the job id
in that agent's README; each coordinator answer it relies on (issue #98) must
carry its source link and raw excerpt; and the open questions must all be
there, so a step that is not grounded is never silently turned into an
instruction. No
network, no token: the worker parser is only asked to parse.
"""

import re
import shlex
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "near-agent"))
import worker  # noqa: E402

RUNBOOKS = sorted(ROOT.glob("agents/*/RUNBOOK.md")) + [ROOT / "tools" / "brand_name_checker-RUNBOOK.md"]
SECTIONS = ("## The award at a glance", "## 1. What the award brings and where it appears",
            "## 2. Owner steps (checklist)", "## 3. Agent side steps, in order", "## Live dependencies",
            "## Failure table", "## Grounded answers", "## Open questions", "## Sources")
FAILURES = ("Token refused", "Listing rejected", "Test failure inside the window")
OPEN_QUESTIONS = ("Submission path", "Self hire dry run", "Per hire price and window")
ANSWER_URL = "https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577"
ANSWERS = ("A. Agent shell", "B. Token", "C. Listing, price and delivery window", "D. Submission path",
           "E. Self hire dry run", "F. Award notice")
PATH_RE = re.compile(r"`((?:agents|tools|near-agent|api)/[A-Za-z0-9_./-]+)`")
JOB_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")


class Runbooks(unittest.TestCase):
    def test_every_agent_folder_has_a_runbook(self):
        folders = sorted(p for p in (ROOT / "agents").iterdir() if p.is_dir())
        self.assertTrue(folders)
        for folder in folders:
            with self.subTest(folder=folder.name):
                self.assertTrue((folder / "RUNBOOK.md").is_file())
        self.assertTrue((ROOT / "tools" / "brand_name_checker-RUNBOOK.md").is_file())

    def test_required_sections_failures_and_open_questions(self):
        for path in RUNBOOKS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(runbook=str(path.relative_to(ROOT))):
                for heading in SECTIONS:
                    self.assertIn(heading, text)
                for failure in FAILURES:
                    self.assertIn("| %s" % failure, text)
                block = text.split("## Open questions", 1)[1].split("\n## ", 1)[0]
                for n, title in enumerate(OPEN_QUESTIONS, start=1):
                    self.assertIn("%d. **%s:**" % (n, title), block)
                self.assertNotIn("%d. **" % (len(OPEN_QUESTIONS) + 1), block)
                self.assertIn("never guessed", text)

    def test_grounded_answers_carry_source_and_raw_excerpt(self):
        for path in RUNBOOKS:
            text = path.read_text(encoding="utf-8")
            block = text.split("## Grounded answers", 1)[1].split("\n## ", 1)[0]
            with self.subTest(runbook=str(path.relative_to(ROOT))):
                for label in ANSWERS:
                    entry = block.split("**%s.**" % label, 1)[1].split("\n**", 1)[0]
                    self.assertIn("Source: <%s>" % ANSWER_URL, entry)
                    self.assertRegex(entry, r"\n```text\n.+\n```")
                # an open question number cited in the steps must exist
                for n in re.findall(r"open questions? (\d+)", text, re.I):
                    self.assertLessEqual(int(n), len(OPEN_QUESTIONS))

    def test_worker_command_lines_parse_with_the_worker(self):
        parser = worker.build_parser()
        seen = 0
        for path in RUNBOOKS:
            for line in path.read_text(encoding="utf-8").splitlines():
                if "near-agent/worker.py" not in line:
                    continue
                cmd = line.split("near-agent/worker.py", 1)[1].strip()
                if not cmd or cmd.startswith(("(", "`")) or not re.match(r"[a-z]", cmd):
                    continue
                argv = shlex.split(cmd.rstrip("`"))
                with self.subTest(runbook=path.name, line=cmd):
                    parser.parse_args(argv)  # SystemExit fails the test
                    seen += 1
        self.assertGreaterEqual(seen, 3 * len(RUNBOOKS))

    def test_cited_paths_and_test_dirs_exist(self):
        for path in RUNBOOKS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(runbook=str(path.relative_to(ROOT))):
                for cited in PATH_RE.findall(text):
                    if "<" in cited:
                        continue
                    self.assertTrue((ROOT / cited.rstrip("/.")).exists(), cited)
                for d in re.findall(r"unittest discover -s (\S+)", text):
                    self.assertTrue((ROOT / d).is_dir(), d)

    def test_job_id_matches_the_agent_readme(self):
        for path in RUNBOOKS:
            if path.parent.parent.name != "agents":
                continue
            with self.subTest(agent=path.parent.name):
                runbook_ids = set(JOB_RE.findall(path.read_text(encoding="utf-8")))
                readme_ids = set(JOB_RE.findall((path.parent / "README.md").read_text(encoding="utf-8")))
                self.assertEqual(len(runbook_ids), 1, runbook_ids)
                self.assertTrue(runbook_ids <= readme_ids, (runbook_ids, readme_ids))


if __name__ == "__main__":
    unittest.main()
