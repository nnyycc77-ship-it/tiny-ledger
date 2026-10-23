"""Tests for tools/pregate.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_pregate.py' -v

Which data is which:

* SYNTHETIC: every diff, credential, hex string, claim sentence and example
  line below is built by these tests and labelled SYNTHETIC where it is
  built. None of it was captured from anywhere and none of it is a real
  key. Credential shapes are assembled at run time from pieces, so no
  credential shaped literal exists in this file (the gate scans this file
  too, see test_gate_passes_its_own_files).
* REAL CAPTURE: the provenance tests copy tools/tests/fixtures/instant-pot.http
  and tools/tests/fixtures/provenance.json, the CPSC capture merged with
  PR #19, unmodified, into a temporary directory, and then corrupt the copy
  only. The real fixture is never written.
* REAL TEXT: the track record tests read the live AGENT-BRIEF.md and copy it
  into a temporary repository root, so a verbatim claim is taken from the
  brief itself and a reworded one is the brief with one word changed.
"""

import re
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pregate  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def make_diff(path, lines, start=1):
    """SYNTHETIC unified diff adding `lines` to `path` from line `start`."""
    body = ["diff --git a/%s b/%s" % (path, path), "--- a/%s" % path, "+++ b/%s" % path,
            "@@ -0,0 +%d,%d @@" % (start, len(lines))]
    return "\n".join(body + ["+" + l for l in lines]) + "\n"


def hex64(ch="a"):
    """SYNTHETIC 64 character hex string, built at run time."""
    return (ch + "1") * 32


class GateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copy(REPO / "AGENT-BRIEF.md", self.root / "AGENT-BRIEF.md")  # REAL TEXT

    def tearDown(self):
        self.tmp.cleanup()

    def gate(self, *args, diff=None):
        out = io.StringIO()
        argv = ["--root", str(self.root)] + list(args)
        if diff is not None:
            p = self.root / "change.diff"
            p.write_text(diff, encoding="utf-8")
            argv += ["--diff", str(p)]
        with contextlib.redirect_stdout(out):
            code = pregate.run(argv)
        return code, out.getvalue()

    def result(self, out, check):
        return [l for l in out.splitlines() if l.split(" ")[1:2] == [check + ":"]][0]


class CleanChange(GateCase):
    def test_clean_change_passes(self):
        # SYNTHETIC doc lines with nothing for any check to find.
        code, out = self.gate(diff=make_diff("docs/notes.md", [
            "# Notes", "", "The fetcher prints the raw response beneath the source link."]))
        self.assertEqual(code, 0, out)
        for check in ("secrets", "honesty", "provenance"):
            self.assertTrue(self.result(out, check).startswith("PASS"), out)

    def test_removed_lines_are_not_scanned(self):
        # SYNTHETIC: a removed line carrying a planted key is not an added line.
        planted = "AKIA" + "Q" * 16
        diff = ("--- a/x.md\n+++ b/x.md\n@@ -1,1 +1,1 @@\n-old " + planted + "\n+new line\n")
        code, out = self.gate(diff=diff)
        self.assertEqual(code, 0, out)


class Secrets(GateCase):
    def assertSecretFails(self, line, path="tools/x.py"):
        code, out = self.gate(diff=make_diff(path, ["ok = 1", line], start=10))
        self.assertEqual(code, 1, out)
        self.assertTrue(self.result(out, "secrets").startswith("FAIL"), out)
        self.assertIn("%s:11:" % path, out)
        return out

    def test_planted_credentials_fail(self):
        # SYNTHETIC credential shapes, assembled from pieces at run time.
        planted = [
            'aws = "' + "AKIA" + "Z7" * 8 + '"',
            'gh = "' + "gh" + "p_" + "aB3" * 12 + '"',
            "-----BEGIN " + "OPENSSH PRIVATE KEY" + "-----",
            'k = "' + "AI" + "za" + "Sy" + "x" * 33 + '"',
            "curl -H 'Authorization: " + "Bearer " + "Zx9" * 8 + "'",
            "url = 'https://" + "deploy:" + "hunter2pass" + "@db.internal/x'",
            'client_secret = "' + "q8Wm" * 4 + '"',
        ]
        for line in planted:
            with self.subTest(line=line[:12]):
                self.assertSecretFails(line)

    def test_seed_phrase_fails(self):
        # SYNTHETIC 12 word phrase, ordinary words, not a real wallet phrase.
        phrase = " ".join(["river", "candle", "orbit", "maple", "stone", "violet",
                           "harbor", "tiger", "pencil", "cloud", "ember", "lunar"])
        self.assertSecretFails('words = "%s"' % phrase)
        self.assertSecretFails("mnemonic: %s" % phrase, path="notes.md")

    def test_env_names_and_stated_fakes_pass(self):
        # SYNTHETIC lines in the shape the merged tools use for key handling.
        code, out = self.gate(diff=make_diff("tools/y.py", [
            'KEY_ENV = "PAGESPEED_API_KEY"',
            'cap = fetch(url, token="not-a-real-token-value")',
            'api_key = os.environ.get(KEY_ENV, "")',
        ]))
        self.assertEqual(code, 0, out)

    def test_hex_in_labelled_fixture_passes_and_in_key_context_fails(self):
        # SYNTHETIC hex, the same 64 character shape in both places.
        h = hex64()
        code, out = self.gate(diff=make_diff("tools/tests/fixtures/capture.json",
                                             ['{"id": "%s"}' % h]))
        self.assertEqual(code, 0, out)
        code, out = self.gate(diff=make_diff("tools/tests/fixtures/provenance.json",
                                             ['    "sha256": "%s"' % h]))
        self.assertEqual(code, 0, out)
        out = self.assertSecretFails('private_key = "0x%s"' % h)
        self.assertIn("key context", out)
        self.assertSecretFails('signer pk 0x%s' % h, path="docs/deploy.md")

    def test_public_address_under_wallet_key_passes(self):
        # SYNTHETIC 0x plus 40 hex address, built at run time, in the shape of
        # the PR #81 descriptor capture line and a 402 payTo line (issue #84).
        addr = "0x" + "1" * 40
        mixed = "0x" + "aB3c" * 10
        for path in ("tools/tests/fixtures/api_smoke/descriptor.http", "api/notes.md"):
            with self.subTest(path=path):
                code, out = self.gate(diff=make_diff(path, [
                    '  "payout_wallet": "%s",' % addr,
                    '    "payTo": "%s",' % mixed,
                    'PAYOUT_WALLET_ADDRESS = "%s"' % mixed,
                ]))
                self.assertEqual(code, 0, out)

    def test_hex64_under_wallet_key_still_fails(self):
        # SYNTHETIC 64 hex value under the same wallet named key: key material.
        out = self.assertSecretFails('  "payout_wallet": "0x%s",' % hex64("d"))
        self.assertIn("key context", out)

    def test_non_address_under_wallet_key_follows_existing_rule(self):
        # SYNTHETIC near misses: none is exactly 0x plus 40 hex, so the
        # existing secret named assignment rule still applies to each.
        near = ["0x" + "1a" * 19 + "1",      # 39 hex digits
                "0x" + "1a" * 20 + "b",      # 41 hex digits
                "1a" * 20,                   # 40 hex, no 0x
                "0X" + "1a" * 20,            # upper case X
                "0x" + "1a" * 19 + "zz",     # not hex
                "q8Wmq8Wmq8Wm"]              # ordinary literal
        for val in near:
            with self.subTest(val=val):
                out = self.assertSecretFails('payout_wallet = "%s"' % val)
                self.assertIn("secret named 'payout_wallet'", out)

    def test_hex_hash_context_passes_and_unnamed_assignment_fails(self):
        # SYNTHETIC hex outside any fixture directory.
        h = hex64("c")
        code, out = self.gate(diff=make_diff("PROOF.md", [
            "Deploy tx hash: 0x%s" % h, "Body SHA-256 %s." % h, "A bare value %s in prose." % h]))
        self.assertEqual(code, 0, out)
        out = self.assertSecretFails('VALUE = "%s"' % h)
        self.assertIn("unlabelled name", out)


class Honesty(GateCase):
    def brief_lines(self):
        text = (self.root / "AGENT-BRIEF.md").read_text(encoding="utf-8")
        start = text.index("As of")
        end = text.index("deadline.", start) + len("deadline.")
        return text[start:end].split("\n")

    def test_verbatim_track_record_passes(self):
        # REAL TEXT: the paragraph copied from AGENT-BRIEF.md as a quote,
        # wrapped the way the brief wraps it.
        quoted = ["> " + l.strip() for l in self.brief_lines()]
        code, out = self.gate(diff=make_diff("docs/record.md", quoted))
        self.assertEqual(code, 0, out)

    def test_reworded_track_record_fails(self):
        # SYNTHETIC rewording of the REAL TEXT: one word changed per case.
        # The job count and the USDC total are read from the current
        # paragraph, so this test keeps working when the reviewer updates
        # the record, rather than naming the figures of one date.
        sentence = " ".join(l.strip() for l in self.brief_lines())
        count = re.search(r"\b([a-z]+) paid jobs\b", sentence)
        total = re.search(r"\b(\d+\.\d{2}) USDC\b", sentence)
        self.assertIsNotNone(count, "no '<count> paid jobs' phrase in the brief paragraph")
        self.assertIsNotNone(total, "no '<amount> USDC' figure in the brief paragraph")
        other_count = "twelve" if count.group(1) != "twelve" else "thirteen"
        other_total = "%.2f" % (float(total.group(1)) + 10)
        for old, new in [(count.group(0), other_count + " paid jobs"),
                         (total.group(0), other_total + " USDC"),
                         ("won and delivered", "won, delivered and praised")]:
            with self.subTest(new=new):
                code, out = self.gate(diff=make_diff("README.md", [sentence.replace(old, new)]))
                self.assertEqual(code, 1, out)
                self.assertIn("README.md:1: track record claim not word for word", out)

    def test_stronger_claims_fail(self):
        # SYNTHETIC claims, none of which is true or in the brief.
        for line in ["We have completed 40 paid jobs for repeat buyers.",
                     "The agent has earned over 500 USDC so far.",
                     "Dozens of clients rely on the recall check."]:
            with self.subTest(line=line):
                code, out = self.gate(diff=make_diff("README.md", [line]))
                self.assertEqual(code, 1, out)
                self.assertIn("track record claim", out)

    def test_editing_the_brief_paragraph_fails(self):
        text = (self.root / "AGENT-BRIEF.md").read_text(encoding="utf-8")
        no = text[:text.index("As of")].count("\n") + 1
        code, out = self.gate(diff=make_diff("AGENT-BRIEF.md", ["   As of the new date"], start=no))
        self.assertEqual(code, 1, out)
        self.assertIn("only the reviewer updates it", out)

    def test_guarantee_language_fails_and_negation_passes(self):
        # SYNTHETIC sentences.
        for line in ["Results are guaranteed within the hour.",
                     "A risk-free way to earn USDC.", "You can't lose with this tab."]:
            with self.subTest(line=line):
                code, out = self.gate(diff=make_diff("docs/pitch.md", [line]))
                self.assertEqual(code, 1, out)
                self.assertIn("guarantee language", out)
        code, out = self.gate(diff=make_diff("docs/pitch.md", [
            "An empty result is not a guarantee that a product is safe."]))
        self.assertEqual(code, 0, out)

    def test_example_data_must_be_labelled(self):
        # SYNTHETIC example lines; the file is written so the label window
        # is read from the file as the gate would read it in a real change.
        doc = self.root / "docs" / "usage.md"
        doc.parent.mkdir()
        doc.write_text("Contact jane doe at ops@example.com.\n", encoding="utf-8")
        code, out = self.gate(diff=make_diff("docs/usage.md", ["Contact jane doe at ops@example.com."]))
        self.assertEqual(code, 1, out)
        self.assertIn("example data not labelled", out)
        doc.write_text("Example input, not a real contact:\n\nContact jane doe at ops@example.com.\n",
                       encoding="utf-8")
        code, out = self.gate(diff=make_diff("docs/usage.md", ["Contact jane doe at ops@example.com."], start=3))
        self.assertEqual(code, 0, out)


class Provenance(GateCase):
    def copy_real_capture(self):
        # REAL CAPTURE, copied unmodified; only the copy is ever corrupted.
        dest = self.root / "tools" / "tests" / "fixtures"
        dest.mkdir(parents=True)
        shutil.copy(FIXTURES / "instant-pot.http", dest / "instant-pot.http")
        prov = __import__("json").loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
        (dest / "provenance.json").write_text(__import__("json").dumps(
            {"instant-pot.http": prov["instant-pot.http"]}), encoding="utf-8")
        return dest

    def test_untouched_capture_verifies(self):
        self.copy_real_capture()
        code, out = self.gate(diff=make_diff("docs/a.md", ["plain line"]))
        self.assertEqual(code, 0, out)
        self.assertIn("PASS provenance: 1 recorded hash(es) verified", out)

    def test_one_tampered_byte_fails(self):
        dest = self.copy_real_capture()
        data = bytearray((dest / "instant-pot.http").read_bytes())
        data[len(data) // 2] ^= 0x01
        (dest / "instant-pot.http").write_bytes(bytes(data))
        code, out = self.gate(diff=make_diff("docs/a.md", ["plain line"]))
        self.assertEqual(code, 1, out)
        self.assertIn("sha256 mismatch for instant-pot.http", out)

    def test_missing_fixture_fails(self):
        dest = self.copy_real_capture()
        (dest / "instant-pot.http").unlink()
        code, out = self.gate(diff=make_diff("docs/a.md", ["plain line"]))
        self.assertEqual(code, 1, out)
        self.assertIn("fixture instant-pot.http is missing", out)

    def test_meta_file_without_hash_passes(self):
        # SYNTHETIC meta file in the shape of fixtures/usaspending/*.meta.json.
        d = self.root / "fixtures"
        d.mkdir()
        (d / "q.meta.json").write_text('{"source": "https://api.usaspending.gov/"}', encoding="utf-8")
        code, out = self.gate(diff=make_diff("docs/a.md", ["plain line"]))
        self.assertEqual(code, 0, out)

    def test_repo_provenance_verifies(self):
        # REAL CAPTURES: every recorded hash in this repository.
        findings, checked = pregate.verify_provenance(REPO)
        self.assertEqual(findings, [])
        self.assertGreaterEqual(checked, 3)


class FailClosed(GateCase):
    def test_missing_brief_is_an_error_not_a_pass(self):
        (self.root / "AGENT-BRIEF.md").unlink()
        code, out = self.gate(diff=make_diff("docs/a.md", ["plain line"]))
        self.assertEqual(code, 2, out)
        self.assertNotIn("PASS", out)

    def test_bad_git_ref_is_an_error(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        code, out = self.gate("--base", "no-such-ref-here")
        self.assertEqual(code, 2, out)
        self.assertNotIn("PASS", out)

    def test_git_mode_reads_the_branch_diff(self):
        # SYNTHETIC repository: a base commit, then a branch adding one line.
        g = ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t.invalid"]
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)], check=True)
        subprocess.run(g + ["add", "AGENT-BRIEF.md"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "base"], check=True)
        subprocess.run(g + ["checkout", "-q", "-b", "work"], check=True)
        (self.root / "n.md").write_text("Results are guaranteed.\n", encoding="utf-8")
        subprocess.run(g + ["add", "n.md"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "work"], check=True)
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("n.md:1: guarantee language", out)


class GitModes(GateCase):
    """Git mode gates the working tree by default and the committed range
    with --committed, reading the honesty label window from the same source
    in each case. SYNTHETIC repositories throughout; AGENT-BRIEF.md is the
    REAL TEXT copy from GateCase."""

    def setUp(self):
        super().setUp()
        self.g = ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t.invalid"]
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)], check=True)
        self.git("add", "AGENT-BRIEF.md")
        self.git("commit", "-q", "-m", "base")
        self.git("checkout", "-q", "-b", "work")

    def git(self, *args):
        subprocess.run(self.g + list(args), check=True)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def commit(self, rel, text, msg="work"):
        self.write(rel, text)
        self.git("add", rel)
        self.git("commit", "-q", "-m", msg)

    def test_pr49_shape_uncommitted_label_is_gated_as_it_will_be_committed(self):
        # SYNTHETIC replay of the PR #49 fix round: a committed line carries
        # unlabelled example data, then the fix inserts a label line above it
        # in the working tree without committing, which shifts the line.
        self.commit("docs/usage.md", "# Usage\n\nContact ops@example.com for access.\n")
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("docs/usage.md:3: example data not labelled", out)

        self.write("docs/usage.md",
                   "# Usage\n\nThe contact below is a placeholder.\nContact ops@example.com for access.\n")
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 0, out)
        self.assertIn("SOURCE working tree vs merge base", out)
        self.assertIn("label window from the working tree", out)

        # The committed range is unchanged: the finding stays at the commit's
        # line 3, with the window read from HEAD (where no label exists), and
        # the gate says the tree differs from the commit it describes.
        code, out = self.gate("--base", "main", "--committed")
        self.assertEqual(code, 1, out)
        self.assertIn("docs/usage.md:3: example data not labelled", out)
        self.assertIn("SOURCE committed range main...HEAD", out)
        self.assertIn("label window from HEAD", out)
        self.assertIn("NOTE 1 path(s) in the working tree differ from HEAD", out)

    def test_untracked_and_staged_files_are_gated_by_default_only(self):
        # SYNTHETIC: a new file with guarantee language, first untracked,
        # then staged; neither is in the committed range.
        self.write("n.md", "Results are guaranteed.\n")
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("n.md:1: guarantee language", out)
        self.assertIn("1 untracked file(s) included", out)
        code, out = self.gate("--base", "main", "--committed")
        self.assertEqual(code, 0, out)
        self.assertIn("0 added line(s) in 0 file(s)", out)
        self.assertIn("NOTE 1 path(s) in the working tree differ from HEAD", out)

        self.git("add", "n.md")
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("n.md:1: guarantee language", out)
        self.assertIn("0 untracked file(s) included", out)

    def test_clean_tree_gives_the_same_result_in_both_modes(self):
        self.commit("n.md", "Results are guaranteed.\n")
        default_code, default_out = self.gate("--base", "main")
        committed_code, committed_out = self.gate("--base", "main", "--committed")
        self.assertEqual((default_code, committed_code), (1, 1), default_out + committed_out)
        self.assertIn("n.md:1: guarantee language", default_out)
        self.assertIn("n.md:1: guarantee language", committed_out)
        self.assertNotIn("NOTE", committed_out)
        self.assertEqual(default_out.splitlines()[1:], committed_out.splitlines()[1:])

    def test_untracked_binary_file_has_no_lines_to_gate(self):
        # SYNTHETIC bytes that are not UTF-8 text.
        (self.root / "blob.bin").write_bytes(bytes([0xFF, 0xFE, 0x00, 0x80]) * 8)
        code, out = self.gate("--base", "main")
        self.assertEqual(code, 0, out)
        self.assertIn("0 added line(s) in 0 file(s)", out)


class SelfCheck(unittest.TestCase):
    def test_gate_passes_its_own_files(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pregate.run(["--files", "tools/pregate.py", "tools/tests/test_pregate.py",
                                "tools/pregate-README.md"])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
