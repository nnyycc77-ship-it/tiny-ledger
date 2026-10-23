# Review checklist: tiers, delegation, and verdicts

This file is the canonical review checklist for work in this repo. The coordinator follows it on every review, and any delegated reviewer follows it exactly the same way. Read it beside `AGENT-BRIEF.md` and `PLAYBOOK.md`. Where this file and `AGENT-BRIEF.md` disagree, `AGENT-BRIEF.md` wins.

Every pull request that arrives through the task board gets one tier, one review, and one verdict. The tier decides how deep the review goes and who may run it.

## The three tiers

Classify the pull request by what it touches, not by its size. A pull request that touches more than one tier takes the highest of them. **When in doubt, classify up.**

### Tier 1, low

Docs and words only, no code. Membership: documentation, delivery templates, README changes, `PLAYBOOK.md` changes, comments, and any change whose full effect is text a reader sees. If a change alters what a program does, it is not tier 1.

### Tier 2, standard

Code that moves no money. Membership: new tools and fetchers that follow an already merged pattern, tests, fixes and refactors of non money code, and supporting scripts. Most board work lands here.

### Tier 3, high

Anything that touches money or the promises around it. Membership: payments, wallets, contracts, escrow, signing, delivery to a paying platform, pricing or payout logic, and any code whose failure could move funds, lose funds, or misstate what was paid. A change to the evidence format that paying deliveries rely on is tier 3 as well.

## Checklists

### Every tier, no exceptions

- **Secrets scan of every added line.** Read each added line in the diff for API keys, tokens, passwords, private keys, seed phrases, and credential shaped strings. A scan that was only run by a tool the reviewer did not inspect does not count on its own; the reviewer states what was scanned and what was found.
- **Honesty check against `AGENT-BRIEF.md`.** No invented data anywhere in code, fixtures, examples, or prose. Track record claims match `AGENT-BRIEF.md` word for word. Empty results are proven by the full raw response, never asserted. Exclusions stay operator supplied.
- **CI green on the head.** Verify the workflow runs for the exact head commit through the Actions API and read the conclusions. Green on an older head is not green. (The board token cannot call the Checks API; the Actions API is the route.)

### Tier 2 adds

- **Full diff read.** Every file, every hunk, read by the reviewer, not skimmed from the summary.
- **Tests rerun locally by the reviewer**, with the counts recorded in the verdict comment (suites run, tests passed, skipped, failed). The helper's own reported counts are a claim to verify, not evidence.
- **One spot live run** wherever the tool has a live source: the reviewer runs the tool once against the real source and compares the output to the recorded fixtures or the delivery it claims to reproduce. Where the helper disclosed it could not run live, that run is owed here.
- **Fixture provenance check.** Fixtures that claim to be captures name their source, query, and retrieval time; labelled synthetic or reconstructed data is marked exactly where it appears.

### Tier 3 adds

- **Every live run the helper could not do**, completed by the reviewer before any verdict.
- **Line by line reading of the money touching logic**: every path that can move, hold, release, or account for funds, read in full, with the failure modes named.
- **Tier 3 is never delegated.** The coordinator reviews tier 3 personally, always. A delegated reviewer who classifies a pull request as tier 3 stops and hands it back.

## Delegation

- **One pull request per reviewer.** A reviewer never holds two reviews at once.
- The reviewer reports back in the fixed short format below. The **coordinator adjudicates** every delegated report and posts the verdict; a delegated verdict is a recommendation until the coordinator posts it.
- **Roughly one in three delegated reviews is re audited** by the coordinator, who re runs the checklist on the same head. The audit is recorded on the verdict comment.
- **A confirmed miss becomes a `PLAYBOOK.md` lesson** in the same cycle it is found, written as a rule with its reason, so the next reviewer inherits it.

### Reviewer report format

```
REVIEW: PR #<number> | Tier: <1|2|3> | Delegated: <yes/no> | Audited: <yes/no>
Verdict: <APPROVE | APPROVE WITH FIXES | CHANGES REQUIRED>
Items: <numbered list of exactly what must change, or "none">
Tests: <command run by the reviewer, with counts>
Live runs: <what was run live and the result, or "none applicable">
Secrets scan: <added lines scanned, result>
CI: <workflow run for the head sha, conclusion>
```

## Delta reviews

When a pull request gets a new head after fixes, the re review covers **the delta since the last reviewed head plus the requested fixes only**. The reviewer confirms each listed fix landed, reads the delta in full, and reruns the tests the delta touches. The verdict comment names the previous head and the new head so the delta is auditable later.

## Verdicts

Exactly three verdicts exist. Use no others.

- **APPROVE** — the gate passed. Merges under the standing merge authority once CI is green on the head.
- **APPROVE WITH FIXES** — the approach is right and the listed items are the whole gap. Every item is listed exactly; nothing off list blocks the merge once the items land and the new head passes a delta review.
- **CHANGES REQUIRED** — the approach, the evidence, or the honesty of the change fails the gate. The items list says what a passing version would need.

Every verdict comment names the **tier** and whether the review was **delegated** and whether it was **audited**, and carries the evidence in the reviewer report format: tests with counts, live run results, and the scan result. A verdict without its evidence is not a verdict.

One merge limit sits above all tiers: a pull request that changes files under `.github/workflows/` cannot be merged through the coordinator's connector route, because the board token holds no Workflows permission. Such a pull request flags that in its description, and its merge path is planned with the coordinator before the review starts.

## Metrics

For every review, the coordinator records one line in `board-state.md` (in the program's hidden work files):

```
PR #<number> | tier <1|2|3> | DONE <time> | verdict <time> | <verdict> | <first pass | fix round N> | <delegated | own> | <audited | not audited>
```

These lines feed the daily summary: tasks merged per day, first pass approval rate, and review latency from DONE comment to verdict. When latency climbs past two coordinator cycles with work waiting, the coordinator delegates more reviews in parallel rather than letting the queue sit.
