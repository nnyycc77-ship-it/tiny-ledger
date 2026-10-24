"""Tests that pin the api_smoke coverage census in tools/README.md.

Run:  python3 -m unittest discover -s tools/tests -p 'test_api_smoke_census.py' -v

The census block in tools/README.md (Coverage census, issue #258) states
figures that were refreshed by hand nine times (issues #258, #270, #279,
#288, #295, #303, #310, #351, #354): the GET path denominator and its
list, the 200, 400, 502 and 503 captured and reasoned counts, the
fixture and provenance counts, and the offline run's section and PASS
line totals with their per shape arithmetic. This module recounts every
one of those figures and compares it with the figure the block states,
so a stale figure fails the suite instead of waiting for the next
manual refresh to catch it.

Current tree choice (issue #368 acceptance): the block names the pin
commit its figures were taken on. This test recounts on the tree it
runs in rather than checking out the pinned commit, for two reasons.
A test run cannot assume the pinned commit is retrievable from its
checkout: continuous integration checkouts may be shallow or single
branch, and the pinned commit is an ancestor that such a checkout is
not required to carry. And the census contract is that its figures
reproduce from the tree that carries the block: a refresh moves the
pin and the figures together, so on any tree whose block is current
the recount of that same tree must reproduce them. The pin itself is
still read here and asserted to be a full 40 character commit id.

How the recount works, figure by figure:

* The denominator and its list are compared with the paths in
  api/openapi.json, read from the tree.
* The captured and reasoned counts are compared with the tables in
  tools/api_smoke.py (ENDPOINT_FIXTURES, NO_ENDPOINT_CAPTURE,
  BAD_QUERY_FIXTURES, NO_400_CAPTURE, SOURCE_FAILURE_FIXTURES,
  NO_502_CAPTURE, UNAVAILABLE_FIXTURES) and, for the 503 shape, with
  the paths whose entries in api/openapi.json declare a 503, read
  through the tool's own repo_openapi_503_paths(). Where the block
  prints a list (the denominator, the 200 and 400 captured lists, the
  503 reasoned list) the list itself is compared, not only its length;
  where it names reasoned endpoints in prose, each name must appear.
* The fixture counts are compared with the transcripts in
  tools/tests/fixtures/api_smoke/ and the entries of its
  provenance.json; the two sets of names must be equal.
* The run totals and the per shape arithmetic are compared with a
  real offline run, in process through api_smoke.main([]), the same
  entry point the command line and the coordinator's recount use.
  Sections are counted by their own sequential numbering (a section
  header counts only when its number is the next one expected, so a
  lookalike line inside a printed transcript cannot inflate the
  count), and PASS lines are grouped by section kind from the
  section titles.

The block is parsed on whitespace normalized text, so rewrapping a
paragraph does not break the pin, but rewording a figure's sentence
fails the parse loudly rather than passing silently: a figure this
module cannot find is a failure, never a skip. Standard library
only, no network. This module adds no fixtures of its own.
"""

import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import api_smoke as smoke  # noqa: E402

README = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
FIX = Path(__file__).parent / "fixtures" / "api_smoke"


def census_block():
    start = README.index("Coverage census (issue #258")
    end = README.index("Output is one Markdown section", start)
    return re.sub(r"\s+", " ", README[start:end])


BLOCK = census_block()
OPENAPI_PATHS = sorted(json.loads((ROOT / "api" / "openapi.json").read_text(encoding="utf-8"))["paths"])


def stated(pattern, text=BLOCK):
    m = re.search(pattern, text)
    if m is None:
        raise AssertionError("census block figure not found: %s" % pattern)
    return m


def stated_int(pattern, text=BLOCK):
    return int(stated(pattern, text).group(1))


def stated_list(marker, text=BLOCK):
    """The backticked paths in the first parenthesised list after marker."""
    i = text.index(marker)
    j = text.index("(", i)
    depth, k = 0, j
    while True:
        if text[k] == "(":
            depth += 1
        elif text[k] == ")":
            depth -= 1
            if depth == 0:
                break
        k += 1
    return sorted(set(re.findall(r"`(/[a-z]*)`", text[j:k + 1])))


class CensusBlock(unittest.TestCase):
    def test_pin_is_a_full_commit_id(self):
        pin = stated(r"taken on main ([0-9a-f]{40})\b").group(1)
        self.assertEqual(len(pin), 40)

    def test_denominator_matches_openapi(self):
        self.assertEqual(stated_int(r"the GET denominator is the (\d+) paths"),
                         len(OPENAPI_PATHS))
        self.assertEqual(stated_list("the GET denominator is"), OPENAPI_PATHS)

    def test_200_shape_matches_the_tables(self):
        self.assertEqual(stated_int(r"- 200 reports: (\d+) captured"),
                         len(smoke.ENDPOINT_FIXTURES))
        self.assertEqual(stated_list("- 200 reports:"), sorted(smoke.ENDPOINT_FIXTURES))
        self.assertEqual(stated_int(r"(\d+) reasoned in the tool's"),
                         len(smoke.NO_ENDPOINT_CAPTURE))
        for path in smoke.NO_ENDPOINT_CAPTURE:
            self.assertIn("`%s`" % path, BLOCK)

    def test_400_shape_matches_the_tables(self):
        self.assertEqual(stated_int(r"- 400 bad query: (\d+) captured"),
                         len(smoke.BAD_QUERY_FIXTURES))
        self.assertEqual(stated_list("- 400 bad query:"), sorted(smoke.BAD_QUERY_FIXTURES))
        self.assertEqual(stated_int(r"- 400 bad query: \d+ captured \([^)]*\); (\d+) reasoned"),
                         len(smoke.NO_400_CAPTURE))
        for path in smoke.NO_400_CAPTURE:
            self.assertIn("`%s`" % path, BLOCK)

    def test_502_shape_matches_the_tables(self):
        m = stated(r"- 502 source failure: the same (\d+) captured; (\d+) reasoned")
        self.assertEqual(int(m.group(1)), len(smoke.SOURCE_FAILURE_FIXTURES))
        self.assertEqual(int(m.group(2)), len(smoke.NO_502_CAPTURE))

    def test_503_shape_matches_the_tables_and_the_document(self):
        declared = sorted(smoke.repo_openapi_503_paths())
        self.assertEqual(declared, sorted(smoke.UNAVAILABLE_FIXTURES))
        m = stated(r"- 503 unavailable: (\d+) captured \(`(/[a-z]*)` and `(/[a-z]*)`,")
        self.assertEqual(int(m.group(1)), len(smoke.UNAVAILABLE_FIXTURES))
        self.assertEqual(sorted([m.group(2), m.group(3)]), declared)
        self.assertEqual(stated_int(r"(\d+) reasoned, each because its entry declares no 503"),
                         len(OPENAPI_PATHS) - len(declared))
        seg = BLOCK[BLOCK.index("declares no 503 response:"):BLOCK.index("The fixture folder holds")]
        listed = sorted(set(re.findall(r"`(/[a-z]*)`", seg)))
        self.assertEqual(listed, [p for p in OPENAPI_PATHS if p not in declared])

    def test_fixture_counts_match_the_folder_and_provenance(self):
        files = sorted(p.name for p in FIX.glob("*.http"))
        provenance = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(set(files), set(provenance))
        m = stated(r"holds (\d+) transcripts with (\d+) provenance entries")
        self.assertEqual(int(m.group(1)), len(files))
        self.assertEqual(int(m.group(2)), len(provenance))
        b = stated(r"(\d+) endpoint 200 captures, (\d+) bad query captures, "
                   r"(\d+) source failure captures, and (\d+) unavailable captures")
        parts = [int(b.group(i)) for i in range(1, 5)]
        self.assertEqual(parts, [len(smoke.ENDPOINT_FIXTURES), len(smoke.BAD_QUERY_FIXTURES),
                                 len(smoke.SOURCE_FAILURE_FIXTURES), len(smoke.UNAVAILABLE_FIXTURES)])
        self.assertEqual(len(files), 3 + sum(parts))


class OfflineRun(unittest.TestCase):
    """One real offline run, shared by the run figure tests."""

    @classmethod
    def setUpClass(cls):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            cls.code = smoke.main([])
        cls.text = out.getvalue()
        cls.sections = []  # (number, title, pass lines)
        expected = 1
        current = None
        for line in cls.text.splitlines():
            m = re.match(r"^### (\d+)\. (.*)$", line)
            if m and int(m.group(1)) == expected:
                current = [int(m.group(1)), m.group(2).strip(), 0]
                cls.sections.append(current)
                expected += 1
            elif line.startswith("- PASS:") and current is not None:
                current[2] += 1
        cls.total_pass = cls.text.count("- PASS:")

    def kind_sums(self):
        kinds = {"originals": 0, "endpoint": 0, "bad query": 0, "400 accounting": 0,
                 "source failure": 0, "502 accounting": 0, "unavailable": 0,
                 "503 accounting": 0, "coverage": 0}
        for number, title, passes in self.sections:
            if number <= 3:
                kinds["originals"] += passes
            elif title == "Bad query (400) accounting":
                kinds["400 accounting"] += passes
            elif title == "Source failure (502) accounting":
                kinds["502 accounting"] += passes
            elif title == "Unavailable (503) accounting":
                kinds["503 accounting"] += passes
            elif title == "Endpoint coverage":
                kinds["coverage"] += passes
            elif re.match(r"^Endpoint GET \S+ bad query \(400\)$", title):
                kinds["bad query"] += passes
            elif re.match(r"^Endpoint GET \S+ source failure \(502\)$", title):
                kinds["source failure"] += passes
            elif re.match(r"^Endpoint GET \S+ unavailable \(503\)$", title):
                kinds["unavailable"] += passes
            elif re.match(r"^Endpoint GET \S+ \(tools/", title):
                kinds["endpoint"] += passes
            else:
                self.fail("unclassified smoke section: %s" % title)
        return kinds

    def test_run_totals_match_the_block(self):
        self.assertEqual(self.code, 0)
        self.assertIn("Result: PASS, every assertion held.", self.text)
        m = stated(r"prints (\d+) numbered sections and (\d+) PASS lines")
        self.assertEqual(int(m.group(1)), len(self.sections))
        self.assertEqual(int(m.group(2)), self.total_pass)
        self.assertEqual(sum(s[2] for s in self.sections), self.total_pass)

    def test_run_arithmetic_matches_the_block(self):
        kinds = self.kind_sums()
        m = stated(r"(\d+) in the three original sections, (\d+) across the (\d+) "
                   r"endpoint 200 sections \(5 each\), (\d+) across the (\d+) bad query "
                   r"sections \(4 each\), (\d+) in the 400 accounting, (\d+) across the "
                   r"(\d+) source failure sections \(4 each\), (\d+) in the 502 accounting, "
                   r"(\d+) across the (\d+) unavailable sections \(5 each\), (\d+) in the "
                   r"503 accounting, and (\d+) in the closing coverage section")
        g = [int(m.group(i)) for i in range(1, 14)]
        self.assertEqual(g[0], kinds["originals"])
        self.assertEqual(g[1], kinds["endpoint"])
        self.assertEqual(g[2], len(smoke.ENDPOINT_FIXTURES))
        self.assertEqual(g[3], kinds["bad query"])
        self.assertEqual(g[4], len(smoke.BAD_QUERY_FIXTURES))
        self.assertEqual(g[5], kinds["400 accounting"])
        self.assertEqual(g[6], kinds["source failure"])
        self.assertEqual(g[7], len(smoke.SOURCE_FAILURE_FIXTURES))
        self.assertEqual(g[8], kinds["502 accounting"])
        self.assertEqual(g[9], kinds["unavailable"])
        self.assertEqual(g[10], len(smoke.UNAVAILABLE_FIXTURES))
        self.assertEqual(g[11], kinds["503 accounting"])
        self.assertEqual(g[12], kinds["coverage"])
        self.assertEqual(sum(kinds.values()), self.total_pass)


if __name__ == "__main__":
    unittest.main()
