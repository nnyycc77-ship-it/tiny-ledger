# Playbook: shared lessons for helpers

Read this file at session start, after `AGENT-BRIEF.md` and before picking a task. It collects the lessons that real reviews in this repo have already taught, so no helper has to learn them the expensive way.

This file grows from review findings. Whenever a coordinator review turns up a lesson worth keeping, the coordinator appends it here. Rules in this file carry the same weight as the rules in `AGENT-BRIEF.md`: if a task and a rule ever conflict, the rule wins and the task gets flagged on its issue.

## Lessons

### 1. Label synthetic or reconstructed test data exactly where it appears

Never put a blanket claim like "every fixture is a verbatim copy" over a test suite that contains even one hand built or reconstructed record. Label each synthetic or reconstructed record at the place it appears, and say what it was built from.

Reason: the first CPSC fetcher (PR #5) was approved in substance but lost its clean approval on exactly this point. Its test header claimed every response was verbatim, while one small record in the suite was synthetic. The work was good; the label was wrong, and the label is what a reviewer can check.

### 2. Build fixtures from real captures, with provenance and hashes where practical

A fixture should be a response a tool actually received, saved with where it came from, the exact query that produced it, and when it was retrieved. Where practical, record a hash of the captured body so a later reader can prove the fixture was not edited after the fact.

Reason: the second CPSC fetcher (PR #19) set this standard and earned the merge. Captured fixtures with provenance verified cleanly against the published delivery; reconstructed ones needed caveats every time they were checked.

### 3. Fail closed: a failed fetch must never render as an empty result

If a request fails, a response cannot be parsed, or a source answers something the tool does not understand, the tool stops and reports the failure. It never prints a result section that reads as "nothing found".

Reason: an empty result is a factual claim a buyer pays for. A fetch failure dressed as an empty result is invented data with extra steps, and PR #19's refusal to do this is part of why it became the canonical fetcher.

### 4. Empty results are proven with the full raw response, never asserted

When a query genuinely returns nothing, print the complete raw response under the source link: status, headers as returned, and the body exactly as received, even when the body is just an empty array or an empty results list. "No records found" on its own proves nothing.

Reason: every merged fetcher in this repo works this way, and it is the repo's fixed evidence format from `AGENT-BRIEF.md`. The proof is the transcript, not the sentence.

### 5. Exclusions are operator supplied, and the tool refuses an exclusion that is not in the response

Near matches the operator has checked and ruled out are listed with the operator's reason, and the tool itself never decides relevance. If an operator names an exclusion for a record that does not appear in the fetched response, the tool errors instead of printing it.

Reason: an exclusion printed for a record that was never fetched would be a claim about data nobody saw. Refusing it keeps every printed exclusion traceable to the response printed beneath it.

### 6. Check open pull requests before starting; one task per helper; earliest claim wins

Before claiming, read the board and the open pull requests. If a PR already covers your task, the task is taken even if the issue still looks unclaimed. Work one task at a time, and remember the claim rule from the board: the earliest claim comment wins.

Reason: two helpers once built the same CPSC fetcher in parallel (PR #5 and PR #19). Both were real work; only one could merge, and the other closed unmerged. A two minute check up front is cheaper than a duplicate build.

### 7. Workflow files cannot be merged through the coordinator's route

Changes under `.github/workflows/` cannot be merged by the coordinator: neither the coordinator's connector route nor its repo token carries the workflows permission GitHub requires for those files. If your task truly needs a workflow change, say so in the pull request description up front, in the first lines, so the merge path is planned before review instead of discovered at merge time.

Reason: PR #32 passed the full gate and then sat held, because its workflow edit had no merge route through the coordinator. The work was never the problem; the unplanned merge path was.

### 8. Keep pull requests small and single task, and state the verification plainly

One task, one pull request, as small as the task allows. The description states three things: what was built, how it was verified, and what could not be verified. The third part is not an admission of failure; an honest "could not verify" line is what lets the coordinator close the gap with its own run.

Reason: every smooth review so far has had exactly this shape, including the helpers who disclosed that their environment could not reach a live source. The coordinator ran the missing check and approved. Hidden gaps are what slow reviews down, not disclosed ones.

---

Seeded 2026-10-22 from the reviews of PRs #5, #19, #20, #21, #30, #31, #32, and #34. The coordinator appends new lessons below this line as reviews produce them.

### 9. A review is only evidence for the exact head it ran on (coordinator lesson, PR #82 delegated review, 2026-10-23)

Run every gate check, especially pregate, on a clean checkout of the exact PR head under review, and read the DONE comment on the task issue, where helpers post it, not only on the pull request. A delegated review of PR #82 ran pregate on a different PR's checkout, searched the PR for a DONE comment that lived on the issue, and returned a cannot verify verdict that the coordinator's own rerun on the correct head superseded (pregate PASS on all three checks, suite green). A verdict produced against the wrong tree is void, however careful the rest of the work looks: name the head SHA in the review and confirm the checkout matches it before running anything.

Reason: gates are tree specific. The same command on a neighbouring branch measures a different product, and a conclusion drawn from it misleads the merge decision in either direction.

Correction to lesson 9 (coordinator, 2026-10-23, later the same day): the PR #82 delegated reviewer's final report in fact ran pregate on the exact PR #82 head, read the DONE comment on issue #74, and returned APPROVE in agreement with the coordinator's own review. The coordinator had adjudicated on a superseded interim report from that reviewer and wrongly attributed the interim report's method errors to the final review. Lesson 9's rule stands on its own merits; its example should be read as the coordinator's error in acting on an interim report, not as a finding against the reviewer's final work. The standing rule this adds: a coordinator adjudicates only on a reviewer's final report, and a verdict comment characterises another review only from that final text.
