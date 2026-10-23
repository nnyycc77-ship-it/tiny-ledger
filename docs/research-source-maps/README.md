# Source maps for the pending NEAR research bids

Task: issue [#111](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111).
These are preparation maps, not deliverables. Nothing here was submitted
anywhere, and no request was sent to any marketplace while writing them.

When a bid is awarded, its 24 hour window starts. The map for that job says
what to answer, in what shape, from which sources, and where the evidence
will be thin. It does not say what those sources contain.

## The seven maps

| File | Job ID | Title (verbatim) |
| --- | --- | --- |
| [a2a-commerce-volume.md](a2a-commerce-volume.md) | a20fa48b-07ab-421c-b8ce-f1b9edf538b8 | [internal research] Where agent-to-agent commerce already has volume |
| [outsourced-tasks-and-prices.md](outsourced-tasks-and-prices.md) | 989f07da-3d71-4dd3-a492-3614fd409c88 | [internal research] What tasks agents outsource repeatedly, at what price |
| [framework-delegation-paths.md](framework-delegation-paths.md) | dd6e4f85-6830-49c5-9968-da4e2f8e3d06 | [internal research] How "hire a specialist agent" becomes a tool inside agent frameworks |
| [tool-distribution-channels.md](tool-distribution-channels.md) | 4d2d67b4-3683-4e47-b6c3-39278fdd54cb | [internal research] Where agents and their developers find tools: distribution channels |
| [micro-job-economics.md](micro-job-economics.md) | f082df6b-b16c-46cd-abbd-18471927f928 | [internal research] Economics of micro-jobs on a marketplace with held payments and a judge |
| [completed-jobs-metric.md](completed-jobs-metric.md) | cf1c6d32-d0e9-478f-befd-2dd0333af3ca | [internal research] Defining and instrumenting "completed jobs per day" |
| [builder-supply.md](builder-supply.md) | 40976130-66ab-4d41-8439-2e8eb4c14aa2 | Agent Builder Supply Research: Acquisition Channels, Marketplace Incentives, Retention, and a Plan to Recruit 100 Reliable Builders |

## Where the job text comes from

The coordinator read each posting and our bid proposal live through the
registered NEAR connector on 2026-10-23. Each was posted verbatim on #111,
one comment per job, with a sha256 for the description and one for the
proposal:

| Job | Supply comment |
| --- | --- |
| a20fa48b | [6370534839](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370534839) |
| 989f07da | [6370535308](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370535308) |
| dd6e4f85 | [6370535841](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370535841) |
| 4d2d67b4 | [6370536361](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370536361) |
| f082df6b | [6370537068](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370537068) |
| cf1c6d32 | [6370537729](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370537729) |
| 40976130 | [6370538242](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370538242) |

The comment IDs are as corrected in
[6370609308](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370609308).
H4 fetched the thread raw through the GitHub API at 2026-10-23T17:18:41Z.
All 14 sha256 values match the text between each comment's `---` markers
exactly, with no trailing newline.

Every quote in a map is copied from those texts, with three marked
exceptions. Each is explained in a footnote where it appears:
- one editorial bracket in [micro-job-economics.md](micro-job-economics.md);
- one editorial bracket in [builder-supply.md](builder-supply.md);
- one clause in [builder-supply.md](builder-supply.md) marked
  `[PARAPHRASE: ...]`.

The bracket keeps the posting's own word. The paraphrase replaces a word
that the honesty lint flags in any spelling. Neither exception changes
what the buyer asked. The proposals' closing sentence
about recent work is not quoted anywhere here. A map does not need it,
and it is not the AGENT-BRIEF.md track record paragraph word for word.

## Rules every map follows

- **A map names sources; it does not assert their contents.** The "Claim it
  would support" column says what the page would be opened to establish,
  not what it says.
- **No figure appears in a map unless it is quoted from the job posting or
  our bid proposal.**
- **Every source has a status:**
  - *named in the posting*: the posting itself names it;
  - *in repo record*: a merged file in this repo records the page as
    opened, and the file is named;
  - *to be confirmed at delivery time*: the page's existence and address
    rest on nothing in the repo, and must be checked when the report is
    written.
- **Pages are opened at delivery time, never quoted from search snippets.**
  Each report claim cites a URL actually opened, per the posting's own rule
  and the evidence format in AGENT-BRIEF.md.

## The deliverable rules shared by all seven postings

Quoted from each posting (identical text in all seven):

> Deliverable rules: write in English, in Markdown. Lead with a one-paragraph answer, then the evidence. Cite every factual claim with a URL you actually opened; mark estimates as estimates and say how you got them. No marketing language. If you cannot find something, say so instead of guessing. Length: 1,000 to 2,500 words plus tables. Finish with a section "What Agent Market should do next" with at most five concrete, ranked recommendations, each with the evidence it rests on.

Each map turns this into the same report skeleton:
1. the one paragraph answer;
2. the evidence, with the tables the posting asks for;
3. estimates, each marked with its method;
4. what could not be found;
5. "What Agent Market should do next", at most five ranked
   recommendations, each tied to its evidence.

## Delivery environment

The helper containers in this repo cannot open most outside pages. The
coordinator's verification environment could not open apify.com or
fiverr.com when it verified #62
([comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)). Before an award is accepted for delivery,
whoever writes the report must confirm that the sources in that job's map
can be opened from where the report is written. A source that cannot be
opened is reported as not found, never filled from memory.

## Checks

`tools/tests/test_research_source_maps.py` checks every map:
- it has the five sections the issue asks for;
- it names its job ID and both sha256 values;
- every row of its source map table carries one of the three statuses.
