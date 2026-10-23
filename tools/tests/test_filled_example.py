"""Tests for templates/filled-example.md (workstream D item 3, issue #61).

Run:  python3 -m unittest discover -s tools/tests -p 'test_filled_example.py' -v

The filled example is built from one real published delivery. These tests
hold it to the acceptance in BACKLOG.md: it names its source delivery file,
every body line of it is a line of that delivery (so every figure, date,
count, URL, retrieval time and excerpt matches the source figure for
figure), its excerpt blocks are contiguous verbatim slices of the source,
it carries the skeleton sections and the applied checklist, and its
annotations are marked so a reader can tell them from delivery text.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "templates" / "filled-example.md"
SOURCE_NAME = "recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md"
SOURCE = ROOT / "deliveries" / SOURCE_NAME
BEGIN, END = "<!-- example body begins -->", "<!-- example body ends -->"
SKELETON_ONLY = {"## Scope and inputs", "## Checked and excluded"}


def example():
    return EXAMPLE.read_text(encoding="utf-8")


def body():
    text = example()
    return text.split(BEGIN, 1)[1].split(END, 1)[0]


def is_annotation(line):
    return line.startswith("*Checklist") and line.endswith("*")


class FilledExampleTests(unittest.TestCase):
    def test_header_names_the_source_delivery_which_exists(self):
        text = example()
        self.assertTrue(SOURCE.is_file())
        self.assertIn("`deliveries/%s`" % SOURCE_NAME, text)
        self.assertIn("(../deliveries/%s)" % SOURCE_NAME, text)
        self.assertLess(text.index(SOURCE_NAME), text.index(BEGIN))

    def test_every_body_line_is_a_line_of_the_source_delivery(self):
        source_lines = set(SOURCE.read_text(encoding="utf-8").split("\n"))
        strays = []
        for line in body().split("\n"):
            if not line.strip() or is_annotation(line) or line in SKELETON_ONLY:
                continue
            if line not in source_lines:
                strays.append(line)
        self.assertEqual(strays, [], "body lines not found verbatim in the source delivery")

    def test_excerpt_blocks_are_contiguous_verbatim_slices(self):
        source = SOURCE.read_text(encoding="utf-8")
        text = body()
        blocks = re.findall(r"\n```\n(.*?)\n```\n", text, re.S)
        self.assertGreaterEqual(len(blocks), 15)
        for block in blocks:
            self.assertIn("\n" + block + "\n", source, block[:80])
        # Every excerpt sits directly beneath a source link: each S heading has a
        # Query URL and a Retrieved line before its first fence.
        headings = re.findall(r"^### (S\d+)\. .*$", text, re.M)
        self.assertEqual(headings, ["S1", "S2", "S3", "S10", "S11", "S12", "S13", "S14", "S15", "S16"])
        self.assertEqual(len(re.findall(r"^- Query URL: https?://", text, re.M)), len(headings))
        self.assertEqual(len(re.findall(r"^- Retrieved \(UTC\): 2026-10-22T\d\d:\d\d:\d\dZ$", text, re.M)), len(headings))

    def test_checklist_points_are_exercised(self):
        text = body()
        # Empty result proven by the complete raw transcript (S10).
        self.assertIn("returned 0 records", text)
        self.assertIn("Excerpt (Complete raw HTTP response transcript to the Instant Pot Smart WiFi query):", text)
        self.assertIn("HTTP/1.1 200 OK\nContent-Type: application/json; charset=utf-8", text)
        self.assertIn("Content-Length: 2\n\n[]\n```", text)
        # Near matches checked and excluded with the reason, under their own heading.
        self.assertIn("## Checked and excluded\n", text)
        start = text.index("## Checked and excluded")
        self.assertIn("checked and excluded because they name different models", text[start:])
        self.assertIn("#### Recall 15-741", text[start:])
        self.assertIn("#### Recall 18-110", text[start:])
        # Other records of a title search named rather than dropped (Subject 1).
        self.assertIn("the other 4 are records 21-129, 23-201, 26-067, and 21-702", text)
        # A field that repeats another is noted and read from the page instead.
        self.assertIn("the remedy text field repeats the hazard text word for word", text)
        # Skeleton order: scope, subjects, checked and excluded, summary, sources.
        order = [text.index(h) for h in ("## Scope and inputs", "## Subject 1:", "## Subject 3:",
                                          "## Checked and excluded", "## Summary table", "## Sources")]
        self.assertEqual(order, sorted(order))

    def test_annotations_are_marked_and_the_applied_checklist_follows_the_body(self):
        text = example()
        annotations = [l for l in body().split("\n") if l.startswith("*")]
        self.assertGreaterEqual(len(annotations), 5)
        for line in annotations:
            self.assertTrue(is_annotation(line), line)
        tail = text.split(END, 1)[1]
        self.assertIn("## Delivery checklist, as applied above", tail)
        self.assertGreaterEqual(tail.count("- [x] "), 8)
        self.assertNotIn("- [ ] ", tail)
        self.assertIn("tools/tests/test_filled_example.py", tail)

    def test_templates_index_links_the_example(self):
        index = (ROOT / "templates" / "README.md").read_text(encoding="utf-8")
        self.assertIn("(filled-example.md)", index)
        self.assertIn(SOURCE_NAME, index)


if __name__ == "__main__":
    unittest.main()
