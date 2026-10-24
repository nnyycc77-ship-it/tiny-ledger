# pregate.py

The mechanical half of the review gate in `REVIEW.md` ("Every tier, no
exceptions"), as one offline script. It runs the same way on a helper's
machine, inside the coordinator's review, and in CI. Standard library
Python 3 and local `git` only; no network, no keys, no dependencies.

```sh
python3 tools/pregate.py                     # working tree vs origin/main, as it will be committed
python3 tools/pregate.py --base main
python3 tools/pregate.py --committed         # the committed range origin/main...HEAD only
git diff main...HEAD | python3 tools/pregate.py --diff -
python3 tools/pregate.py --files README.md   # whole files treated as added
```

It prints one `SOURCE` line naming what was gated, one result line per
check, then one indented `file:line: reason` line per finding, and exits 0
when all three pass, 1 when any fails, and 2 when it cannot run (bad ref,
unreadable diff, AGENT-BRIEF.md missing or without its track record
paragraph). An error never prints PASS.

## Which lines git mode gates

| Mode | Added lines | Honesty label window |
| --- | --- | --- |
| default | the working tree against the merge base of `<base>` and HEAD: committed, staged and unstaged changes, plus untracked (not ignored) files as added whole | the working tree |
| `--committed` | `git diff <base>...HEAD`, the committed range a reviewer or CI gates | HEAD |
| `--diff`, `--files` | the given diff or files | the working tree |

Added lines and the label window always come from the same source, so a
finding's `file:line` matches the file it was read from. Run the default
mode before committing: it gates the change exactly as it will be
committed. `--committed` is for gating an exact head; when the working tree
differs from HEAD it prints a `NOTE` line saying the findings describe the
commit and not the files on disk. On a clean tree the two modes agree.

Before this split the gate diffed the committed range but read the label
window from disk, so running it on an uncommitted edit gave findings at
line numbers matching neither (issue #54, from the PR #49 fix round).

| Check | What fails |
| --- | --- |
| `secrets` | Credential shapes in added lines (private key blocks, AWS, GitHub, Google, Slack, Stripe, OpenAI/Anthropic style keys, JWTs, bearer values, credentials in URLs, seed phrases); a literal assigned to a secret named variable; a 64 hex string in a key context or assigned to an unlabelled name. |
| `honesty` | A track record claim that is not word for word from `AGENT-BRIEF.md`; any edit to that paragraph; guarantee language; example shaped data with no example or fixture label on its line or the five lines before it. |
| `provenance` | Any SHA-256 recorded in a `provenance*.json` or `*.meta.json` anywhere in the repo that does not match its fixture's bytes, a missing fixture, or a malformed recorded value. |

The context rules (what counts as fixture content, what counts as a key
context, and why the line is drawn there) are written out in full in the
docstring at the top of `pregate.py`, beside the code that applies them.
In short: files under `fixtures/` and provenance files are captured and
hash checked, so a 64 hex value there passes; a 64 hex value after a key,
secret, seed, signer or wallet word fails even next to a hash word; after a
hash word (sha256, digest, tx, topic, commit, ...) it passes; assigned to a
name that says neither, it fails; bare in prose, it passes.

**Accepted capture findings (issue #198).** A secrets or honesty finding
inside a fixture whose provenance hash verifies is a verbatim capture
finding: a third party's "guarantee" in an app description, a consumer's
"guaranteed" in a complaint, `keys_url` in a GitHub response body. It does
not fail its check. It is listed, file and line, in an `ACCEPTED capture
findings` section after the three result lines, never silently. Not
accepted:
- the same line in a non-fixture file;
- a fixture that no provenance file lists, or whose hash does not verify
  (the provenance check fails as well);
- the always-fail credential shapes and seed phrases, which fail in any
  file.

A PASS is not a review. `REVIEW.md` still requires the reviewer to read
every added line; this gate makes that read start from a list instead of
from nothing. Known limit: a fixture edited together with its recorded
hash passes the provenance check, so provenance changes are read in the
diff.

## Tests

```sh
python3 -m unittest discover -s tools/tests -p 'test_pregate.py' -v
```

The existing `test.yml` workflow already runs every suite under
`tools/tests`, so these tests run in CI with no workflow change.

## CI step (follow up, not in this change)

Running the gate itself on each pull request needs a workflow edit, which
the coordinator's route cannot merge (`PLAYBOOK.md` lesson 7). The step to
add to the `delivery-tool-tests` job in `.github/workflows/test.yml`, as a
separate owner side change:

```yaml
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Pre gate (secrets, honesty, provenance)
        if: github.event_name == 'pull_request'
        run: python3 tools/pregate.py --committed --base origin/${{ github.base_ref }}
```

`fetch-depth: 0` replaces the job's existing checkout so the base branch is
present for the three dot diff.
