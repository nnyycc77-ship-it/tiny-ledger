"""Checks the public deliveries index (issue #143) traces to committed records.

Run:  python3 -m unittest discover -s tools/tests -p 'test_deliveries_index.py' -v

The checks:
- the track record paragraph on the page is AGENT-BRIEF.md's, word for word;
- every delivered file it links exists;
- every file under deliveries/ appears on the page, so no delivery is
  left out, the disputed one included;
- the NEAR submission's time and hash are the ones the runbook quotes;
- every commit the page cites exists, when the checkout has the history;
- the services catalog links the page.
"""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs" / "deliveries-index.md"
CATALOG = ROOT / "docs" / "services-catalog.md"
RUNBOOK = ROOT / "docs" / "near-delivery-runbook.md"


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


class DeliveriesIndex(unittest.TestCase):
    def setUp(self):
        self.text = PAGE.read_text(encoding="utf-8")

    def test_track_record_is_the_brief_word_for_word(self):
        brief = (ROOT / "AGENT-BRIEF.md").read_text(encoding="utf-8")
        want = re.search(r"As of\s+\d{4}-\d{2}-\d{2}\s+the\s+true\s+record\s+is:.*?deadline\.", brief, re.S).group(0)
        quote = "\n".join(l[2:] for l in self.text.split("## Track record", 1)[1].splitlines() if l.startswith("> "))
        self.assertEqual(norm(quote), norm(want))

    def test_every_linked_delivery_exists_and_every_delivery_is_listed(self):
        linked = set(re.findall(r"\]\(\.\./(deliveries/[^)]+\.md)\)", self.text))
        for rel in linked:
            self.assertTrue((ROOT / rel).is_file(), rel)
        present = {"deliveries/" + p.name for p in (ROOT / "deliveries").glob("*.md")}
        self.assertEqual(present - linked, set(), "delivered file(s) missing from the index")

    def test_near_entry_matches_the_runbook_quote(self):
        runbook = RUNBOOK.read_text(encoding="utf-8")
        row = re.search(r"^\| (87d3fce7-[0-9a-f-]+) \| .*? \| (\S+) \| `([0-9a-f]{64})` \|", self.text, re.M)
        self.assertIsNotNone(row)
        self.assertIn(row.group(1), runbook)
        self.assertIn("submittedAt %s" % row.group(2), runbook)
        self.assertIn("deliverableHash %s" % row.group(3), runbook)

    def test_landed_amounts_sum_to_the_track_record_total(self):
        from decimal import Decimal
        section = self.text.split("## Synmerco deliveries", 1)[1].split("## Disputed job", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| \d{3} \|", r)]
        self.assertEqual(len(rows), 7)
        landed = [Decimal(re.search(r"\| ([\d.]+) USDC \|", r).group(1)) for r in rows]
        brief = (ROOT / "AGENT-BRIEF.md").read_text(encoding="utf-8")
        total = Decimal(re.search(r"([\d.]+) USDC\s+in\s+total", brief).group(1))
        self.assertEqual(round(sum(landed), 2), total)
        self.assertIn("**%s USDC**" % sum(landed), section)

    def test_disputed_job_is_shown_as_disputed(self):
        section = self.text.split("## Disputed job", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| 853 |", section)
        self.assertIn("**Disputed, then refunded. Nothing landed.**", section)

    def test_cited_commits_exist(self):
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT,
                                 capture_output=True, text=True)
        if shallow.returncode != 0 or shallow.stdout.strip() != "false":
            self.skipTest("the checkout has no full history to look commits up in")
        for sha in sorted(set(re.findall(r"\(([0-9a-f]{7})(?:,|\))", self.text))):
            found = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=ROOT, capture_output=True)
            self.assertEqual(found.returncode, 0, sha)

    def test_catalog_links_the_page(self):
        self.assertIn("(deliveries-index.md)", CATALOG.read_text(encoding="utf-8"))
        self.assertIn("(services-catalog.md)", self.text)


if __name__ == "__main__":
    unittest.main()
