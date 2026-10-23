"""Tests for the delivery templates in templates/. Standard library only.

Run:  python3 -m unittest discover -s tools/tests -p 'test_templates.py' -v

The templates quote hard rules 2 and 3 of AGENT-BRIEF.md as Markdown block
quotes. These tests rebuild that quote from the live AGENT-BRIEF.md and
check each template carries it byte for byte, so a change to the brief that
is not carried into the templates fails here. They also check the skeleton
sections, the checklist, and that no template contains a bare year, score
or count where a placeholder belongs (templates hold no example data).
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
SERVICE_FILES = [
    "service-07-pagespeed-snapshot.md",
    "service-08-public-dataset-build.md",
    "service-09-bilingual-research-brief.md",
    "service-10-solidity-read-only-review.md",
]
SKELETON_HEADINGS = [
    "## Scope and inputs",
    "## Checked and excluded",
    "## Sources",
    "## Service checklist (before delivering)",
    "## Format rules that bind this delivery",
]


def brief_rule(number):
    brief = (ROOT / "AGENT-BRIEF.md").read_text(encoding="utf-8")
    start = brief.index("%d. **" % number)
    end = brief.index("%d. **" % (number + 1))
    return brief[start:end].rstrip("\n")


def quoted(text):
    return "\n".join("> " + l if l else ">" for l in text.split("\n"))


class TemplateFilesTests(unittest.TestCase):
    def test_all_four_templates_and_index_exist(self):
        for name in SERVICE_FILES + ["README.md"]:
            self.assertTrue((TEMPLATES / name).is_file(), name)

    def test_index_links_every_template(self):
        index = (TEMPLATES / "README.md").read_text(encoding="utf-8")
        for name in SERVICE_FILES:
            self.assertIn("(%s)" % name, index)

    def test_each_template_quotes_brief_rules_verbatim(self):
        rule2, rule3 = quoted(brief_rule(2)), quoted(brief_rule(3))
        self.assertIn("Never invent data", rule2)
        self.assertIn("The delivery format is fixed", rule3)
        for name in SERVICE_FILES:
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            self.assertIn(rule3, text, name)
            self.assertIn(rule2, text, name)
            self.assertIn("[AGENT-BRIEF.md, hard rule 3](../AGENT-BRIEF.md)", text, name)

    def test_each_template_has_skeleton_and_checklist(self):
        for name in SERVICE_FILES:
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            for heading in SKELETON_HEADINGS:
                self.assertIn(heading + "\n", text, "%s lacks %s" % (name, heading))
            self.assertIn("Report skeleton begins", text, name)
            self.assertIn("Report skeleton ends", text, name)
            self.assertLess(text.index("Report skeleton begins"), text.index("## Scope and inputs"), name)
            self.assertLess(text.index("## Checked and excluded"), text.index("## Sources"), name)
            self.assertGreaterEqual(text.count("- [ ] "), 6, name)
            self.assertIn("Retrieved: <YYYY-MM-DDTHH:MM:SSZ>", text, name)

    def test_templates_hold_no_example_data(self):
        # Outside the quoted brief (which carries dated track record text), a
        # template must not contain a four digit year, a decimal score, or a
        # currency amount: those belong in placeholders, filled from a source.
        for name in SERVICE_FILES:
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            body = "\n".join(l for l in text.split("\n") if not l.startswith(">"))
            body = body.replace("YYYY-MM-DDTHH:MM:SSZ", "").replace("YYYY-MM-DD", "").replace("DD/MM/YYYY", "")
            body = re.sub(r"https?://\S+", "", body)       # links to repo issues carry numbers
            body = re.sub(r"issue #\d+", "", body)
            body = re.sub(r"\b(19|20)\d\d\b", "YEAR", body)
            self.assertNotIn("YEAR", body, "%s has a bare year" % name)
            self.assertIsNone(re.search(r"\b\d+\.\d+\b", body), "%s has a decimal figure" % name)
            self.assertIsNone(re.search(r"[$€£]\s?\d", body), "%s has a currency amount" % name)
            self.assertIsNone(re.search(r"\b\d+\s+(USDC|USD)\b", body), "%s has a money figure" % name)

    def test_service_specific_points_present(self):
        s7 = (TEMPLATES / SERVICE_FILES[0]).read_text(encoding="utf-8")
        for needle in ["Largest Contentful Paint", "Cumulative Layout Shift", "Total Blocking Time",
                       "Page the API could not measure", "snapshot"]:
            self.assertIn(needle, s7)
        s8 = (TEMPLATES / SERVICE_FILES[1]).read_text(encoding="utf-8")
        for needle in ["`source_record_id`", "`source_query`", "## Collection method", "## Column dictionary"]:
            self.assertIn(needle, s8)
        s9 = (TEMPLATES / SERVICE_FILES[2]).read_text(encoding="utf-8")
        for needle in ["Translation (agent's, not source text):", "## Source list by language", "## What the sources do not say"]:
            self.assertIn(needle, s9)
        s10 = (TEMPLATES / SERVICE_FILES[3]).read_text(encoding="utf-8")
        for needle in ["not an\naudit, not a certification", "Severity (reviewer's opinion)", "## Not reviewed", "```solidity"]:
            self.assertIn(needle, s10)


if __name__ == "__main__":
    unittest.main()
