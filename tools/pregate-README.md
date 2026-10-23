# pregate.py

The mechanical half of the review gate in `REVIEW.md` ("Every tier, no
exceptions"), as one offline script. It runs the same way on a helper's
machine, inside the coordinator's review, and in CI. Standard library
Python 3 and local `git` only; no network, no keys, no dependencies.

```sh
python3 tools/pregate.py                     # added lines in origin/main...HEAD
python3 tools/pregate.py --base main
git diff main...HEAD | python3 tools/pregate.py --diff -
python3 tools/pregate.py --files README.md   # whole files treated as added
```

It prints one result line per check, then one indented `file:line: reason`
line per finding, and exits 0 when all three pass, 1 when any fails, and 2
when it cannot run (bad ref, unreadable diff, AGENT-BRIEF.md missing or
without its track record paragraph). An error never prints PASS.

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
        run: python3 tools/pregate.py --base origin/${{ github.base_ref }}
```

`fetch-depth: 0` replaces the job's existing checkout so the base branch is
present for the three dot diff.
