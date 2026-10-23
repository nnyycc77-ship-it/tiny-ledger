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
