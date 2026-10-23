"""Checks the research source maps (issue #111) keep the shape the issue asks for.

Run:  python3 -m unittest discover -s tools/tests -p 'test_research_source_maps.py' -v

Each map must have the five required sections, name its job ID and both
sha256 values from the coordinator supply on #111, and give every source in
its source map table one of the three statuses the folder README defines.
A source marked "in repo record" must name a file that exists, so the
status cannot point at nothing. The README index must list every map. No
network: the files are only read.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "docs" / "research-source-maps"
MAPS = sorted(p for p in FOLDER.glob("*.md") if p.name != "README.md")
SECTIONS = ("## 1. Questions", "## 2. Deliverable shape", "## 3. Source map", "## 4. Tables to build",
            "## 5. Risk note")
STATUSES = ("named in the posting", "in repo record", "to be confirmed at delivery time")
JOB_RE = re.compile(r"^\| Job ID \| ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}) \|$", re.M)
SHA_RE = re.compile(r"^\| (Description|Proposal) sha256 \| ([0-9a-f]{64}) \|$", re.M)
PATH_RE = re.compile(r"`((?:near-agent|docs|packaging|tools|agents|api)/[A-Za-z0-9_./-]+)`")


def source_rows(text):
    part = text.split("## 3. Source map", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in part.splitlines() if re.match(r"^\| \d+ \|", line)]
    return [[cell.strip() for cell in row.strip("|").split(" | ")] for row in rows]


class SourceMaps(unittest.TestCase):
    def test_seven_maps(self):
        self.assertEqual(len(MAPS), 7, [p.name for p in MAPS])

    def test_sections_in_order(self):
        for path in MAPS:
            text = path.read_text(encoding="utf-8")
            at = [text.find(s) for s in SECTIONS]
            self.assertNotIn(-1, at, path.name)
            self.assertEqual(at, sorted(at), path.name)

    def test_job_id_and_both_hashes(self):
        seen = set()
        for path in MAPS:
            text = path.read_text(encoding="utf-8")
            jobs = JOB_RE.findall(text)
            self.assertEqual(len(jobs), 1, path.name)
            self.assertNotIn(jobs[0], seen, path.name)
            seen.add(jobs[0])
            self.assertEqual(sorted(k for k, _ in SHA_RE.findall(text)), ["Description", "Proposal"], path.name)

    def test_every_source_has_a_status(self):
        for path in MAPS:
            rows = source_rows(path.read_text(encoding="utf-8"))
            self.assertGreater(len(rows), 0, path.name)
            for row in rows:
                self.assertEqual(len(row), 5, (path.name, row[0]))
                self.assertTrue(row[4].startswith(STATUSES), (path.name, row[0], row[4]))

    def test_repo_record_points_at_a_file(self):
        for path in MAPS:
            for row in source_rows(path.read_text(encoding="utf-8")):
                if row[4].startswith("in repo record"):
                    cited = PATH_RE.findall(" ".join(row))
                    self.assertTrue(cited, (path.name, row[0]))
                    for rel in cited:
                        self.assertTrue((ROOT / rel).exists(), (path.name, row[0], rel))

    def test_readme_lists_every_map(self):
        readme = (FOLDER / "README.md").read_text(encoding="utf-8")
        for path in MAPS:
            self.assertIn("(%s)" % path.name, readme, path.name)
            job = JOB_RE.findall(path.read_text(encoding="utf-8"))[0]
            self.assertIn(job, readme, path.name)


if __name__ == "__main__":
    unittest.main()
