#!/usr/bin/env python3
"""Mechanical pre gate for pull requests in this repo (REVIEW.md, "Every tier").

Runs three checks over the lines a change adds and prints one result line per
check, followed by one indented line per finding (file:line: reason). Exits 0
when every check passes, 1 when any check fails, and 2 when the gate itself
cannot run (bad input, git failure, unreadable AGENT-BRIEF.md). It fails
closed: an error never prints PASS.

  1. secrets     credential shaped strings in added lines
  2. honesty     track record wording, guarantee language, unlabelled example data
  3. provenance  every SHA-256 recorded in a fixture provenance file matches the
                 fixture bytes

Standard library only, fully offline. The diff comes from local git, from a
unified diff file (`--diff FILE`, `-` for stdin), or whole files are treated
as added (`--files PATH ...`).

  python3 tools/pregate.py                      # working tree vs origin/main
  python3 tools/pregate.py --base main
  python3 tools/pregate.py --committed          # the committed range only
  git diff main...HEAD | python3 tools/pregate.py --diff -
  python3 tools/pregate.py --files README.md docs/*.md

Which lines git mode gates, and where the honesty label window is read from:

* Default: the working tree against the merge base of `<base>` and HEAD, so
  an uncommitted edit is gated exactly as it will be committed. Staged and
  unstaged changes are included, and untracked files (not ignored) count as
  added whole. The label window is read from the working tree, the same
  source as the added lines.
* `--committed`: `git diff <base>...HEAD`, the committed range a reviewer or
  CI gates. The label window is read from HEAD, again the same source. When
  the working tree differs from HEAD the gate says so in a NOTE line, since
  the findings describe the commit and not the files on disk.
* `--diff` and `--files`: the label window is read from the working tree.

The first output line names the source that was gated. Before this split
the gate diffed the committed range but read the window from disk, so an
uncommitted edit produced findings at line numbers that matched neither.

This gate is the mechanical half of the review only. A PASS here does not
replace the reviewer reading every added line (REVIEW.md says a scan run by a
tool the reviewer did not inspect does not count on its own).

Context rules for the secrets scan
----------------------------------
Always fail, anywhere, fixtures included: PEM private key blocks, AWS access
key ids, GitHub tokens, Google API keys, Slack tokens, Stripe live keys,
OpenAI and Anthropic style keys, JSON web tokens, Authorization: Bearer values,
credentials embedded in a URL, and seed phrases (12 to 24 lowercase words as a
whole quoted value, or after a seed / mnemonic / recovery phrase label). These
shapes have no legitimate place in a public repo, including in a recorded
response, so no context excuses them.

A secret named assignment (a name containing key, secret, password, token,
private, seed, mnemonic, credential, ...) given a literal value of 8 or more
characters fails, unless the value is an obvious placeholder: `<...>`,
`${VAR}`, `$VAR`, all one repeated character, an environment variable name
(upper case letters, digits and underscores only, the way tools name the
variable they read a key from), or a value that says it is not real
(not-a-real..., fake, dummy, placeholder, example, redacted). A real key
carries none of those, and test stand ins in the merged tools use them.
One more exemption: a value that is exactly 0x followed by 40 hex digits is a
public EVM payment address, not key material, so it passes under a wallet or
other secret named key (issue #84: payout_wallet and payTo in the API's
descriptor and 402 captures). The match is exact; a private key is 64 hex
and is still caught by this rule's other cases and by the 64 hex rules below.

64 character hex strings (with or without 0x), the shape of a private key and
also of a SHA-256 digest or a transaction hash:

* Fixture content passes. Fixture content is a file under a `fixtures/`
  directory, or a provenance file (`provenance*.json`, `*.meta.json`). These
  are recorded API responses and the hashes recorded for them; the
  provenance check below verifies that what they record is real.
* Key context fails. A key context is a line where a secret word (the list
  above, plus pk, privkey, signer, wallet) appears before the hex string. It
  fails even when a hash word is also present, because a hex string next to
  a key word is classified up, the way REVIEW.md says to classify when in
  doubt.
* Hash context passes. A hash context is a line where a hash word (sha256,
  sha, hash, digest, checksum, keccak, topic, tx, txhash, transaction, block,
  commit, merkle, root) appears before the hex string, with no secret word.
* Any other assignment fails: `name = "<hex>"`, `"name": "<hex>"`,
  `name: <hex>`. A 64 hex value assigned to a name that says nothing about
  what it is cannot be told apart from a key, so it must be named.
* Otherwise a bare hex string in prose passes. A bare hex string is not
  enough to fail on its own.

The line is drawn there because a 64 hex value is only dangerous when it is a
key, and the only offline evidence of what it is is how it is labelled.
Fixture directories are exempt because their content is captured from a
source and hash checked, not written by hand.

Honesty lint rules
------------------
* Track record: an added line that makes a track record claim (paid jobs,
  jobs won, paid out, swept to, USDC in total, listed for hire, the true
  record, deployed on Arc, a count of jobs or clients, an earned amount) must
  carry that claim word for word from the AGENT-BRIEF.md track record
  paragraph: the sentence containing it, with whitespace and Markdown list or
  quote markers ignored, must be a contiguous substring of that paragraph.
  Quote the paragraph on its own lines; an added lead in on the same line
  fails. Changing the paragraph itself in AGENT-BRIEF.md fails too: the
  reviewer updates it, not a helper.
* Guarantee language fails: guarantee / guaranteed / guarantees (unless
  negated within four words before it: no, not, never, without, nothing,
  cannot, does not, ...), risk free, no risk, zero risk, 100% safe, can't
  lose, sure profit, assured returns, and promise of returns, profit,
  safety or outcomes.
* Example data must be labelled where it appears. Example shaped data is
  example.com/.org/.net addresses, John or Jane Doe, Acme, lorem ipsum,
  555-01xx phone numbers, 123 Main St. It passes when the
  same line or one of the five lines before it (read from the file, so an
  unchanged label counts) says example, e.g., for instance, fixture,
  synthetic, sample, placeholder, illustrative, hypothetical, demo, dummy,
  fake or mock, or when the file sits under examples/ or fixtures/. The
  example shapes themselves are removed before looking for a label, so
  example.com does not label itself. The file is read from the same source
  as the added lines (working tree by default, HEAD with --committed).
* tools/pregate.py, tools/pregate-README.md and tools/tests/test_pregate.py
  are exempt from the honesty lint: their text defines and tests its rules,
  so it necessarily contains the phrases the lint looks for. The secrets
  scan and the provenance check still apply to them in full.

Provenance rules
----------------
Every provenance file in the repo (`provenance*.json`, `*.meta.json`) is
checked, not only changed ones, so a tampered fixture fails whatever else
the change touches. Recorded hashes are read from: a top level object whose
keys are fixture file names relative to the provenance file, each holding a
"sha256"; an object holding "file", "path" or "fixture" plus "sha256"; or a
`<stem>.meta.json` with a top level "sha256", for the single sibling
`<stem>.*`. The SHA-256 of the fixture's raw bytes must equal the recorded
value exactly. A missing fixture, an ambiguous sibling, or a recorded value
that is not 64 hex characters fails. A provenance file with no hash passes
(there is nothing to verify; usaspending meta files are of this kind).
What this cannot catch: a fixture edited together with its recorded hash.
That is why the reviewer still reads provenance changes in the diff.

Accepted capture findings (issue #198)
--------------------------------------
A verbatim capture can contain words the lints look for: a third party's
"guarantee" in an app description, a consumer's "guaranteed" in a complaint,
or keys_url and license key field names in a GitHub response body. Before
this rule each such finding had to be accepted per PR by coordinator ruling
(PR #173, PR #185, and PR #174 under the #166 ruling). Now a secrets or
honesty finding is accepted when its file is a fixture listed in a
provenance file whose recorded SHA-256 matches the file's bytes in this
run. An accepted finding does not fail its check. It is printed, never
dropped, in an "ACCEPTED capture findings" section after the three result
lines, one "file:line: check: reason" line each, so the reviewer still
reads it.

Not accepted:
* the same line in any file that is not such a fixture;
* a fixture whose hash does not verify (the provenance check fails too), or
  a fixture no provenance file lists;
* the always fail credential shapes and seed phrases above, in any file:
  no context excuses them, a verified capture included.

The hashes are read from the working tree, as the provenance check always
has been. With --committed and a working tree that differs from HEAD, the
gate's NOTE line applies here too.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF_EXEMPT = {"tools/pregate.py", "tools/pregate-README.md", "tools/tests/test_pregate.py"}


class GateError(Exception):
    """The gate could not run. Never reported as a pass."""


# ---------------------------------------------------------------- input


def parse_diff(text):
    """Unified diff text -> {path: [(line_no, text), ...]} of added lines."""
    added, path, line_no = {}, None, 0
    for raw in text.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            if path is not None:
                added.setdefault(path, [])
            continue
        if raw.startswith("--- ") or raw.startswith("diff --git"):
            continue
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if m:
            line_no = int(m.group(1))
            continue
        if path is None:
            continue
        if raw.startswith("+"):
            added[path].append((line_no, raw[1:]))
            line_no += 1
        elif raw.startswith(" "):
            line_no += 1
    return added


DIFF_FLAGS = ("--no-color", "--no-renames", "--no-ext-diff", "--unified=0")


def git_run(root, *args):
    """Run one git command in root; stdout bytes, or GateError."""
    cmd = ["git", "-C", str(root)] + list(args)
    try:
        out = subprocess.run(cmd, capture_output=True, check=False)
    except OSError as exc:
        raise GateError("cannot run git: %s" % exc)
    if out.returncode != 0:
        raise GateError("git %s failed: %s" % (" ".join(args), out.stderr.decode("utf-8", "replace").strip()))
    return out.stdout


def git_diff(base, root, committed=False):
    """Unified diff text of the change plus the list of untracked files.

    Default: merge base of `base` and HEAD -> working tree, so uncommitted
    edits are gated as they will be committed; untracked (not ignored) files
    are returned separately to be treated as added whole.
    committed=True: `base...HEAD`, the committed range only; no untracked
    files."""
    if committed:
        return git_run(root, "diff", *DIFF_FLAGS, base + "...HEAD").decode("utf-8", "replace"), []
    merge_base = git_run(root, "merge-base", base, "HEAD").decode("utf-8", "replace").strip()
    text = git_run(root, "diff", *DIFF_FLAGS, merge_base).decode("utf-8", "replace")
    listing = git_run(root, "ls-files", "--others", "--exclude-standard", "-z").decode("utf-8", "replace")
    return text, [p for p in listing.split("\0") if p]


def git_short(root, rev):
    return git_run(root, "rev-parse", "--short", rev).decode("utf-8", "replace").strip()


def git_dirty_count(root):
    """Number of working tree paths that differ from HEAD, untracked included."""
    status = git_run(root, "status", "--porcelain", "--untracked-files=all").decode("utf-8", "replace")
    return len([l for l in status.splitlines() if l.strip()])


def untracked_as_added(paths, root):
    """Untracked files as whole added files. A file that is not UTF-8 text has
    no lines to gate, the way git diff reports a binary file without lines."""
    added = {}
    for p in paths:
        try:
            text = (root / p).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise GateError("cannot read %s: %s" % (p, exc))
        added[p] = list(enumerate(text.splitlines(), start=1))
    return added


def files_as_added(paths, root):
    added = {}
    for p in paths:
        full = (root / p) if not Path(p).is_absolute() else Path(p)
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise GateError("cannot read %s: %s" % (p, exc))
        rel = str(full.resolve().relative_to(root.resolve())) if full.resolve().is_relative_to(root.resolve()) else p
        added[rel] = list(enumerate(text.splitlines(), start=1))
    return added


def file_lines(root, path):
    """Lines of a file in the working tree, or None when it cannot be read."""
    try:
        return (root / path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None


def head_lines(root, path):
    """Lines of a file as committed in HEAD, or None when HEAD has no such file."""
    try:
        return git_run(root, "show", "HEAD:" + path).decode("utf-8").splitlines()
    except (GateError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------- secrets

SECRET_WORDS = {"key", "keys", "apikey", "secret", "secrets", "password", "passwd", "pwd",
                "passphrase", "token", "tokens", "private", "priv", "privkey", "pk",
                "seed", "mnemonic", "credential", "credentials", "signer", "wallet", "auth"}
HASH_WORDS = {"sha256", "sha", "sha3", "hash", "hashes", "digest", "checksum", "keccak",
              "topic", "topics", "tx", "txhash", "transaction", "block", "blockhash",
              "commit", "merkle", "root"}

ALWAYS = [
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("Stripe live key", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{16,}")),
    ("OpenAI or Anthropic style key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("bearer token", re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._~+/\-]{16,}")),
    ("credentials in URL", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s/:@]+:[^\s/@]{3,}@[^\s/]+")),
]
SEED_LABEL = re.compile(r"(?i)\b(?:seed|mnemonic|recovery|secret)[ _-]?(?:phrase|words?)?\b\s*[:=]\s*[\"']?((?:[a-z]{3,8}\s+){11,23}[a-z]{3,8})")
SEED_QUOTED = re.compile(r"[\"']((?:[a-z]{3,8} ){11,23}[a-z]{3,8})[\"']")
ASSIGN = re.compile(r"""(?P<name>[A-Za-z_][A-Za-z0-9_.\-]*)["']?\s*(?:=|:)\s*["'](?P<val>[^"'\s]{8,})["']""")
HEX64 = re.compile(r"(?<![0-9A-Za-z])(?:0x)?[0-9a-fA-F]{64}(?![0-9A-Za-z])")
HEX_ASSIGN = re.compile(r"""(?P<name>[A-Za-z_][A-Za-z0-9_.\-]*)["']?\s*(?:=|:)\s*["']?(?:0x)?[0-9a-fA-F]{64}(?![0-9A-Za-z])""")
ADDRESS40 = re.compile(r"^0x[0-9a-fA-F]{40}$")  # public EVM address, issue #84
PLACEHOLDER = re.compile(r"^(?:<[^>]*>|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|(.)\1+|\*+|[A-Z][A-Z0-9_]*)$"
                         r"|(?i:not[-_ ]?a[-_ ]?real|fake|dummy|placeholder|example|redacted)")


def words(text):
    """Identifier aware lower case words: api_key, apiKey, API-KEY -> api, key."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return [w.lower() for w in re.split(r"[^A-Za-z0-9]+", text) if w]


def is_fixture_path(path):
    parts = Path(path).parts
    name = Path(path).name
    return "fixtures" in parts or re.match(r"provenance.*\.json$", name) or name.endswith(".meta.json")


def scan_secrets(added):
    findings = []
    for path, lines in sorted(added.items()):
        fixture = bool(is_fixture_path(path))
        for no, line in lines:
            for label, rx in ALWAYS:
                if rx.search(line):
                    findings.append((path, no, label))
            if SEED_LABEL.search(line) or SEED_QUOTED.search(line):
                findings.append((path, no, "seed phrase shaped value"))
            for m in ASSIGN.finditer(line):
                name_words = set(words(m.group("name")))
                val = m.group("val")
                if name_words & SECRET_WORDS and not (name_words & HASH_WORDS) and not PLACEHOLDER.search(val) \
                        and not HEX64.fullmatch(val) and not ADDRESS40.match(val):
                    findings.append((path, no, "literal value assigned to secret named %r" % m.group("name")))
            if fixture:
                continue
            for m in HEX64.finditer(line):
                before = set(words(line[:m.start()]))
                if before & SECRET_WORDS:
                    findings.append((path, no, "64 hex string in a key context"))
                    continue
                if before & HASH_WORDS:
                    continue
                if any(a.end() == m.end() for a in HEX_ASSIGN.finditer(line)):
                    findings.append((path, no, "64 hex string assigned to an unlabelled name"))
    return findings


# ---------------------------------------------------------------- honesty

TRACK_TRIGGERS = re.compile(
    r"(?i)\bpaid jobs?\b|\bjobs? (?:won|delivered|completed|paid)\b|\bpaid out\b|\bswept to\b"
    r"|\bUSDC in total\b|\blisted for hire\b|\btrue record\b|\btrack record (?:is|was|shows|includes)\b"
    r"|\bdeployed on Arc\b|\bearned\s+(?:[$]?\d|over|more than|about)"
    r"|\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|dozens? of|hundreds? of)\s+(?:paid\s+)?"
    r"(?:jobs|clients|customers|buyers|engagements|orders)\b")
GUARANTEE = re.compile(
    r"(?i)\bguarantee[sd]?\b|\brisk[- ]free\b|\bno risk\b|\bzero risk\b|\b100\s?% (?:safe|secure|accurate)\b"
    r"|\bcan(?:'|no)?t lose\b|\bcannot lose\b|\bsure profit\b|\bassured (?:returns?|profits?|income)\b"
    r"|\bpromis(?:e|es|ed|ing) (?:of )?(?:returns?|profits?|income|earnings|safety|outcomes?|results)\b")
NEGATION = re.compile(r"(?i)\b(?:no|not|never|without|nothing|cannot|can't|doesn't|does not|isn't|won't|nor)\b")
EXAMPLE_SHAPES = re.compile(
    r"(?i)\bexample\.(?:com|org|net)\b|\b(?:john|jane) doe\b|\bacme\b|\blorem ipsum\b"
    r"|\b555[- .]01\d\d\b|\b123 main st")
EXAMPLE_LABEL = re.compile(
    r"(?i)\bexamples?\b|\be\.g\.|\bfor instance\b|\bfixtures?\b|\bsynthetic\b|\bsamples?\b|\bplaceholders?\b"
    r"|\billustrative\b|\bhypothetical\b|\bdemo\b|\bdummy\b|\bfake\b|\bmock(?:ed)?\b")
MD_PREFIX = re.compile(r"^\s*(?:(?:>|[*+\-]|\d+[.)])\s*)*")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def track_record_paragraph(root):
    brief = root / "AGENT-BRIEF.md"
    try:
        text = brief.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise GateError("cannot read AGENT-BRIEF.md: %s" % exc)
    m = re.search(r"As of\s+\d{4}-\d{2}-\d{2}\s+the true record is:.*?deadline\.", text, re.S)
    if not m:
        raise GateError("track record paragraph not found in AGENT-BRIEF.md")
    start = text[:m.start()].count("\n") + 1
    end = start + m.group(0).count("\n")
    return norm(m.group(0)), (start, end)


def claim_matches(sentence, canonical):
    s = norm(MD_PREFIX.sub("", sentence)).strip("\"'`*_ ")
    if not s:
        return True
    if s in canonical:
        return True
    return (s[0].swapcase() + s[1:]) in canonical


def lint_honesty(added, root, read_lines=None):
    """read_lines(path) -> the file's lines from the same source as `added`,
    for the example label window; default is the working tree."""
    if read_lines is None:
        read_lines = lambda path: file_lines(root, path)  # noqa: E731
    canonical, (b_start, b_end) = track_record_paragraph(root)
    findings = []
    for path, lines in sorted(added.items()):
        if path == "AGENT-BRIEF.md":
            for no, _ in lines:
                if b_start <= no <= b_end:
                    findings.append((path, no, "track record paragraph changed; only the reviewer updates it"))
            continue
        if path in SELF_EXEMPT:
            continue
        under_examples = bool({"examples", "fixtures"} & set(Path(path).parts))
        full = None
        for no, line in lines:
            for sentence in re.split(r"(?<=[.!?;])\s+", line):
                if TRACK_TRIGGERS.search(sentence) and not claim_matches(sentence, canonical):
                    findings.append((path, no, "track record claim not word for word from AGENT-BRIEF.md"))
                    break
            for m in GUARANTEE.finditer(line):
                lead = " ".join(line[:m.start()].split()[-4:])
                if not NEGATION.search(lead):
                    findings.append((path, no, "guarantee language: %r" % m.group(0)))
            if EXAMPLE_SHAPES.search(line) and not under_examples:
                if full is None:
                    full = read_lines(path) or []
                window = full[max(0, no - 6):no] if full else [line]
                if not any(EXAMPLE_LABEL.search(EXAMPLE_SHAPES.sub("", w)) for w in window + [line]):
                    findings.append((path, no, "example data not labelled as an example or fixture"))
    return findings


# ---------------------------------------------------------------- provenance


def provenance_files(root):
    found = set()
    for pattern in ("provenance*.json", "*.meta.json"):
        for p in root.rglob(pattern):
            if ".git" not in p.relative_to(root).parts:
                found.add(p)
    return sorted(found)


def recorded_hashes(prov):
    """(provenance path) -> [(fixture path, recorded sha256 or bad value)]."""
    try:
        data = json.loads(prov.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise GateError("cannot parse %s: %s" % (prov, exc))
    out = []
    if prov.name.endswith(".meta.json") and isinstance(data, dict) and "sha256" in data:
        stem = prov.name[:-len(".meta.json")]
        sibs = [p for p in prov.parent.iterdir()
                if p.is_file() and p != prov and not p.name.endswith(".meta.json") and p.name.split(".")[0] == stem]
        out.append((sibs[0] if len(sibs) == 1 else None, data["sha256"], stem))
        return out
    if not isinstance(data, dict):
        return out
    for key, val in data.items():
        if isinstance(val, dict) and "sha256" in val:
            name = val.get("file") or val.get("path") or val.get("fixture") or key
            out.append((prov.parent / name, val["sha256"], name))
    if "sha256" in data and any(k in data for k in ("file", "path", "fixture")):
        name = data.get("file") or data.get("path") or data.get("fixture")
        out.append((prov.parent / name, data["sha256"], name))
    return out


def verify_provenance(root, verified=None):
    """(findings, hashes checked). When `verified` is a set, the repo relative
    path of every fixture whose bytes match its recorded hash is added to it."""
    findings, checked = [], 0
    for prov in provenance_files(root):
        rel = str(prov.relative_to(root))
        for fixture, recorded, name in recorded_hashes(prov):
            checked += 1
            if not isinstance(recorded, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded.lower()):
                findings.append((rel, 0, "recorded sha256 for %s is not 64 hex characters" % name))
            elif fixture is None:
                findings.append((rel, 0, "no single fixture file matches %s" % name))
            elif not fixture.is_file():
                findings.append((rel, 0, "fixture %s is missing" % name))
            else:
                actual = hashlib.sha256(fixture.read_bytes()).hexdigest()
                if actual != recorded.lower():
                    findings.append((rel, 0, "sha256 mismatch for %s: recorded %s, actual %s" % (name, recorded, actual)))
                elif verified is not None:
                    verified.add(Path(os.path.relpath(fixture, root)).as_posix())
    return findings, checked


# ---------------------------------------------------------------- verbatim captures

NEVER_ACCEPTED = {label for label, _ in ALWAYS} | {"seed phrase shaped value"}


def split_accepted(findings, verified):
    """(failing, accepted). A finding is accepted when its file is a fixture
    whose provenance hash verified, unless it is one of the always fail
    credential shapes, which no context excuses."""
    failing, accepted = [], []
    for finding in findings:
        path, _, reason = finding
        if Path(os.path.normpath(path)).as_posix() in verified and reason not in NEVER_ACCEPTED:
            accepted.append(finding)
        else:
            failing.append(finding)
    return failing, accepted


# ---------------------------------------------------------------- report


def report(name, findings, ok_note):
    if not findings:
        print("PASS %s: %s" % (name, ok_note))
        return True
    first = findings[0]
    print("FAIL %s: %d finding(s), first at %s:%d" % (name, len(findings), first[0], first[1]))
    for path, no, reason in findings:
        print("  %s:%d: %s" % (path, no, reason))
    return False


def run(argv=None):
    ap = argparse.ArgumentParser(description="Offline pre gate: secrets, honesty, provenance.")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--base", default=None, help="git ref to diff against (default origin/main)")
    src.add_argument("--diff", help="unified diff file, or - for stdin")
    src.add_argument("--files", nargs="+", help="treat these whole files as added")
    ap.add_argument("--committed", action="store_true",
                    help="git mode: gate the committed range <base>...HEAD only, "
                         "instead of the working tree against the merge base")
    ap.add_argument("--root", default=str(ROOT), help="repository root (default: this repo)")
    args = ap.parse_args(argv)
    root = Path(args.root)
    read_lines = None
    notes = []
    try:
        if args.diff:
            text = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
            added = parse_diff(text)
            source = "unified diff %s; label window from the working tree" % ("on stdin" if args.diff == "-" else args.diff)
        elif args.files:
            added = files_as_added(args.files, root)
            source = "%d whole file(s) as added; label window from the working tree" % len(added)
        else:
            base = args.base or "origin/main"
            text, untracked = git_diff(base, root, committed=args.committed)
            added = parse_diff(text)
            if args.committed:
                read_lines = lambda path: head_lines(root, path)  # noqa: E731
                source = "committed range %s...HEAD (HEAD %s); label window from HEAD" % (base, git_short(root, "HEAD"))
                dirty = git_dirty_count(root)
                if dirty:
                    notes.append("NOTE %d path(s) in the working tree differ from HEAD; these findings describe "
                                 "the commit, not the files on disk. Run without --committed to gate the "
                                 "working tree." % dirty)
            else:
                extra = untracked_as_added(untracked, root)
                added.update(extra)
                source = ("working tree vs merge base %s of %s; %d untracked file(s) included; "
                          "label window from the working tree"
                          % (git_short(root, git_run(root, "merge-base", base, "HEAD").decode().strip()),
                             base, len(extra)))
        n_lines = sum(len(v) for v in added.values())
        verified = set()
        prov, checked = verify_provenance(root, verified)
        secrets, accepted_secrets = split_accepted(scan_secrets(added), verified)
        honesty, accepted_honesty = split_accepted(lint_honesty(added, root, read_lines), verified)
    except GateError as exc:
        print("ERROR pregate could not run: %s" % exc)
        return 2
    print("SOURCE %s" % source)
    for note in notes:
        print(note)
    scope = "%d added line(s) in %d file(s)" % (n_lines, len(added))
    ok = report("secrets", secrets, scope)
    ok = report("honesty", honesty, scope) and ok
    ok = report("provenance", prov, "%d recorded hash(es) verified" % checked) and ok
    accepted = [("secrets",) + f for f in accepted_secrets] + [("honesty",) + f for f in accepted_honesty]
    if accepted:
        print("ACCEPTED capture findings: %d, in fixture files whose provenance hash verified; listed for the "
              "reviewer, not failing the gate" % len(accepted))
        for check, path, no, reason in accepted:
            print("  %s:%d: %s: %s" % (path, no, check, reason))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
