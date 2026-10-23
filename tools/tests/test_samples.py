"""Checks the public sample pages (issue #136) are the delivered reports, unchanged.

Run:  python3 -m unittest discover -s tools/tests -p 'test_samples.py' -v

Each page in docs/samples/ has a short header, then a line holding only
"---", then the delivered report. The test checks that:
- the text after the header equals the delivered file under deliveries/
  byte for byte;
- the sha256 the header prints is that file's;
- the header links back to the services catalog;
- the catalog links the page.

No figure on a sample page can drift from what was delivered.
"""

import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "docs" / "samples"
CATALOG = ROOT / "docs" / "services-catalog.md"
SEPARATOR = "\n---\n"


class SamplePages(unittest.TestCase):
    def pages(self):
        pages = sorted(SAMPLES.glob("*.md"))
        self.assertEqual([p.name for p in pages], ["cook-county-tax-comps.md", "tampa-flood-screen.md"])
        return pages

    def test_body_is_the_delivered_file_byte_for_byte(self):
        for page in self.pages():
            text = page.read_text(encoding="utf-8")
            head, body = text.split(SEPARATOR, 1)
            src = re.search(r"\| Delivered file \| \[`(deliveries/[^`]+\.md)`\]\(\.\./\.\./\1\), sha256 `([0-9a-f]{64})` \|", head)
            self.assertIsNotNone(src, page.name)
            delivered = (ROOT / src.group(1)).read_bytes()
            self.assertEqual(body.encode("utf-8"), delivered, page.name)
            self.assertEqual(hashlib.sha256(delivered).hexdigest(), src.group(2), page.name)

    def test_header_heads_it_as_a_sample_and_links_the_catalog(self):
        for page in self.pages():
            head = page.read_text(encoding="utf-8").split(SEPARATOR, 1)[0]
            self.assertTrue(head.startswith("# Sample of delivered work: "), page.name)
            self.assertIn("| Job type | ", head)
            self.assertRegex(head, r"\| Delivery date \| \d{4}-\d\d-\d\d ")
            self.assertIn("(../services-catalog.md)", head)

    def test_catalog_links_every_sample(self):
        catalog = CATALOG.read_text(encoding="utf-8")
        for page in self.pages():
            self.assertIn("(samples/%s)" % page.name, catalog)


if __name__ == "__main__":
    unittest.main()
