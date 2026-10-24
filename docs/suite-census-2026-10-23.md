# Offline suite census, 2026-10-24 (twelfth pass)

The census for issue
[#375](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/375). It
refreshes the censuses filed under issues
[#112](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/112),
[#200](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/200),
[#236](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/236),
[#247](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/247),
[#259](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/259),
[#269](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/269),
[#277](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/277),
[#286](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/286),
[#301](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/301),
[#344](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/344) and
[#350](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/350).
Every offline suite in the repo was run in one pass against merged
main.

The #350 census was pinned to 0a80737. Three PRs merged after it
(#367, the #350 census itself; #373, the api_smoke census pin test;
and #372, the Carrier Watch offer page and the OFAC and OIG standing
watch types). This census is pinned to 96ab9af, the combined main
the coordinator's start message on issue #375 names. This file
replaces the #350 census in place, as each census replaced the one
before. The numbers below are the counts the runs returned.

- **Main commit:** `96ab9af06813088a88a585948baec7ef604a6b3f`
  (96ab9af, "Merge pull request #372 from
  nnyycc77-ship-it/h5-carrier-watch-offer-sanctions-332").
- **Taken:** 2026-10-24, by H6, on a clean detached checkout of that
  commit. Runs started at 14:53:17 UTC; the last started at 14:55:15
  UTC.
- **Interpreters:** python3.12 (3.12.3) is the only Python installed
  in this environment, and `python3` here is python3.12.
  - Every Python suite ran under python3.12, the interpreter the
    `test` workflow pins, so the headline counts are the CI
    interpreter's counts. Suite 11's workflow pins python3.11; its
    count here is the python3.12 run.
  - The interpreter cross check the #350 census made (python3.11,
    python3.12 and python3.13, identical counts) could not be
    repeated in this environment, because python3.11 and python3.13
    are not installed in it.
  - Node here is v24.22.1; the `test` workflow pins Node major 22.
    The proof page tests pass on both, but the versions are not the
    same and this census does not claim they are.
- **Network:** none used. Every suite ran in its default offline mode.
  Live checks are opt in by environment variable, and none was set (see
  Skips).
- **How each suite was run:** from the repository root with the command
  shown. `__pycache__` folders were removed before the pass, and
  `PYTHONDONTWRITEBYTECODE=1` was set, so the tree stayed clean.
- **What wrote each log:** a small runner script, `run.sh`, kept
  outside the repo. It wrote the `$ command`, `# started <time> at
  <commit>` and `# exit <code>` lines around each command's own output.
  Those are the only lines in the logs that the suites did not print
  themselves.

## Result

**No failures anywhere in the repo.** Every suite that ran locally is
green. That includes the full tools suite and the api suite, which the
acceptance asks for. No failure was found, so no QUEUE issue was
filed.

| | Python and Node tests run | Passed | Failed | Skipped |
| --- | --- | --- | --- | --- |
| **Repo total, unique tests** | 1458 | 1451 | 0 | 7 |

The total counts each test once, on python3.12, the CI version.

| Suite (unique tests) | Tests |
| --- | --- |
| `tools/tests` (own tests) | 1072 |
| Seven agent suites | 228 |
| `near-agent/tests` | 49 |
| `api` | 100 |
| Node proof page tests | 9 |

1072 + 228 + 49 + 100 + 9 = 1458.

Not in the total:

- **The Foundry suite (26 tests)** cannot run in this environment (see
  below). CI ran it on the same commit, and the job passed.
- **Two checks that are not unit test suites** both passed: the
  `api_smoke` offline run and pregate.

## Per suite

Counts are from the python3.12 run. The commands are written with
`python3`, as the workflows write them.

| # | Suite | Command | Tests | Passed | Failed | Skipped | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Delivery tooling, as CI runs it | `python3 -m unittest discover -s tools/tests -v` | 1349 | 1342 | 0 | 7 | 0 |
| 2 | Recall API | `python3 -m unittest discover -s api -v` | 100 | 100 | 0 | 0 | 0 |
| 3 | NEAR worker | `python3 -m unittest discover -s near-agent/tests -v` | 49 | 49 | 0 | 0 | 0 |
| 4 | Agent: call-for-me | `python3 -m unittest discover -s agents/call-for-me/tests -t agents/call-for-me/tests -v` | 50 | 49 | 0 | 1 | 0 |
| 5 | Agent: catering-finder | `python3 -m unittest discover -s agents/catering-finder/tests -t agents/catering-finder/tests -v` | 29 | 29 | 0 | 0 | 0 |
| 6 | Agent: field-service-planner | `python3 -m unittest discover -s agents/field-service-planner/tests -t agents/field-service-planner/tests -v` | 38 | 38 | 0 | 0 | 0 |
| 7 | Agent: local-quotes | `python3 -m unittest discover -s agents/local-quotes/tests -t agents/local-quotes/tests -v` | 27 | 27 | 0 | 0 | 0 |
| 8 | Agent: media-generator | `python3 -m unittest discover -s agents/media-generator/tests -t agents/media-generator/tests -v` | 32 | 32 | 0 | 0 | 0 |
| 9 | Agent: video-clipping | `python3 -m unittest discover -s agents/video-clipping/tests -t agents/video-clipping/tests -v` | 28 | 28 | 0 | 0 | 0 |
| 10 | Agent: video-dubbing | `python3 -m unittest discover -s agents/video-dubbing/tests -t agents/video-dubbing/tests -v` | 24 | 24 | 0 | 0 | 0 |
| 11 | USAspending workflow subset | `python3 -m unittest discover -s tools/tests -p 'test_usaspending_awards.py' -v` | 18 | 17 | 0 | 1 | 0 |
| 12 | Proof page logic | `node --test app/proof-core.test.mjs` | 9 | 9 | 0 | 0 | 0 |
| 13 | AgentTab contract (Foundry) | `forge test -vvv` | 26 in CI | not run here | | | 127 |
| 14 | Recall API smoke, offline | `python3 tools/api_smoke.py` | see note | PASS | | | 0 |
| 15 | Pregate on the clean tree | `python3 tools/pregate.py` | 3 checks | 3 | 0 | | 0 |

For the unittest suites, Passed is Tests minus Skipped. Each run ended
with unittest's own summary line: `OK` or `OK (skipped=N)`, with no
failures and no errors. For suite 12, node printed `tests 9`, `pass 9`
and `fail 0`.

### Interpreter cross check

Not repeated in this environment: python3.11 and python3.13 are not
installed here, so suites ran under python3.12 only. The #350 census,
run where all three interpreters exist, found identical counts under
each; nothing in this pass either confirms or contradicts that, and
this census claims only the python3.12 counts it measured.

### How the suites overlap

- **Suite 1 is the CI suite.** Its 1349 tests are 1072 of its own, plus
  all 277 tests of suites 3 to 10. The `load_tests` shims in
  `tools/tests/test_<name>.py` pull those in: 50 + 29 + 38 + 27 + 32 +
  28 + 24 = 228 agent tests, plus 49 NEAR worker tests.
- **Splitting 1349 into 1072 and 277.** The test ids in each standalone
  log for suites 3 to 10 were matched against the suite 1 verbose log.
  Every standalone suite's full id set appears inside suite 1 with the
  same count, so suite 1 holds 277 shim tests and 1349 − 277 = 1072 of
  its own.
- **Result words.** 1308 of suite 1's 1349 test lines carry their
  result word on the same line: 1301 `ok` and 7 `skipped`. The other
  41 do not, and none of them failed, because the run ended
  `OK (skipped=7)`. They break down as follows:
  - **37 tests with a docstring.** unittest prints the docstring on
    the line after the name, and the result word follows it. These are
    the per route and per tool same-text tests in
    `test_wave1_integration` (10), `test_wave2_integration` (8),
    `test_wave1_mcp_integration` (10) and `test_mcp_wave2_integration`
    (9).
  - **4 tests that print output in the middle of their line:**
    `test_fmcsa_carrier.FetchTests.test_main_argument_rules`,
    `test_nonprofit_pack.Inputs.test_no_entries_is_refused`,
    `test_rdap_discriminate.RenderTests.test_bad_input_is_refused_before_any_request`
    and
    `test_standing_watch.SanctionsWatchTests.test_sanctions_fetch_failure_aborts`.
    They print argparse usage or an error message they expect, so the
    result word moves later in the line.
- **Suite 11** is the `usaspending-test.yml` workflow. Its 18 tests
  are part of suite 1's own 1072.
- **The unique repo total** is suite 1, plus suite 2, plus suite 12:
  1349 + 100 + 9 = 1458. The skips are suite 1's 7, which include the
  skips of suites 4 and 11. So 1458 − 7 = 1451 passed.

## Changes since the #350 census

- **Repo total:** 1443 → 1458 unique tests: 1451 passed, 0 failed, 7
  skipped. The whole increase is suite 1's own tests (+15); every
  other suite is unchanged.
- **Suite 1:** 1334 → 1349. The before counts are from a rerun of
  suite 1 at 0a80737 in this same pass (1334, `OK (skipped=7)`,
  matching the #350 census), and the module counts of both runs'
  verbose logs were compared across all 78 modules present in either
  log. Exactly two modules changed:

  | Module | Tests at 0a80737 | Tests at 96ab9af | Change |
  | --- | --- | --- | --- |
  | `test_api_smoke_census` (PR #373) | 0 | 9 | +9 |
  | `test_standing_watch` (PR #372) | 16 | 22 | +6 |

  9 + 6 = 15. `test_api_smoke_census` is the new offline test that
  pins the api_smoke census figures in `tools/README.md` (issue
  #368). The `test_standing_watch` growth is the OFAC and OIG watch
  types PR #372 added to `tools/standing_watch.py` (issue #332). No
  other suite 1 module changed its count. Own tests are 1072
  (1057 + 15). The shim count is unchanged at 277, and every shim
  suite's ids inside suite 1 match its standalone run.
- **Suite 2 (api):** unchanged at 100, with the same per module
  counts as the #350 census: `test_endpoints` 48, `test_recall_api`
  25, `test_payment_gate` 22 and `test_openapi_alignment` 5.
  48 + 25 + 22 + 5 = 100.
- **Suites 3 to 12:** unchanged counts.
- **Result words:** 41 suite 1 lines carry no result word on the same
  line, the same total as the #350 census, with a different
  composition:
  - The docstring group is the same 37.
  - The print group is again 4, but
    `test_standing_watch.SanctionsWatchTests.test_sanctions_fetch_failure_aborts`,
    new with PR #372, takes the place of
    `test_hosted_mcp_probe.ProbeCannotRunTests.test_main_returns_2_when_the_probe_cannot_run`,
    which in this run carried its `ok` on the same line. The #350
    census noted that which of these the log shows varies between
    runs; this run shows the other side of that variation for the
    probe test, plus one genuinely new print case.
  - Every one of these tests passed: the run ended `OK (skipped=7)`.
- **Interpreters:** the cross interpreter rerun the #344 census could
  not make and the #350 census made again could not be repeated in
  this environment (python3.11 and python3.13 absent); see the cross
  check note above.
- **Skips:** unchanged at 7, the same seven tests with the same
  reasons, verified from this run's suite 1 log.
- **Pregate:** reports 275 recorded provenance hashes on the clean
  tree, unchanged from the #350 census; none of the three merges
  since added a fixture.

## Skips

Every skip is a live check that runs only when an environment variable
is set. The skip reasons below are copied from the suite 1 verbose
log.

| Test | Suite | Skip reason as printed |
| --- | --- | --- |
| `test_call_flow.DocsAndSourcesTests.test_captures_verify` | 1, 4 | `set CALL_FOR_ME_CAPTURES to a folder of fetched captures` |
| `test_cpsc_recalls.LiveTests.test_cli_nonempty_and_empty_with_excluded_near_match` | 1 | `set CPSC_LIVE=1 for public API checks` |
| `test_cpsc_recalls.LiveTests.test_cli_title_and_number_query_shapes` | 1 | `set CPSC_LIVE=1 for public API checks` |
| `test_edgar_formd.LiveTests.test_cli_against_edgar` | 1 | `set EDGAR_LIVE=1 and EDGAR_CONTACT for a live EDGAR check` |
| `test_nonprofit_pack.Live.test_live_demo_list` | 1 | `set PROPUBLICA_LIVE=1 to query the live API` |
| `test_propublica_nonprofits.Live.test_live_organization_matches_capture_identity` | 1 | `set PROPUBLICA_LIVE=1 to query the live API` |
| `test_usaspending_awards.LiveTests.test_live_queries_return_valid_evidence` | 1, 11 | `opt-in live public API check` |

## CI on this commit

**The `test` workflow** ran on 96ab9af (run 40104323791, push). All
three of its jobs ended in success:

- `delivery-tool-tests` (job 120902745476);
- `forge-test` (job 120902745273);
- `proof-page-tests` (job 120902745320).

**The `USAspending fetcher tests` workflow** (run 40104323698, job
120902744996) ended in success as well.

**One limit, stated plainly:** this census read the runs' and jobs'
results only. No CI test or skip count is claimed. What the job
results show is that CI is green on this commit.

## What could not run here

**Suite 13, AgentTab contract (Foundry), did not run.** The `forge`
binary is not installed in this environment. The full log of the run:

```
$ forge test -vvv
# started 2026-10-24T14:55:05Z at 96ab9af06813088a88a585948baec7ef604a6b3f
/tmp/census375-logs/run.sh: line 7: forge: command not found
# exit 127
```

No install was attempted, because this is a docs only task. The CI
evidence stands in for the local run.

**CI result on the same commit.** The `forge-test` job ran the suite
on 96ab9af (job 120902745273 in run 40104323791) and completed with
success. `test/AgentTab.t.sol` declares 26 `function test` entries,
matching the suite size every earlier census recorded. This census
did not observe the job's log itself (see the limit under CI on this
commit), so suite 13 is not counted in the repo total.

## Notes on suites 14 and 15

**Suite 14, `tools/api_smoke.py`.** It ran with no arguments, its
default offline mode. In that mode it reads the captured transcripts
in `tools/tests/fixtures/api_smoke/` and makes no connection. Its
result line:

```
Result: PASS, every assertion held.
```

**Suite 15, pregate on the clean tree.** With no changes to gate, it
checks no added lines. It still verifies the 275 recorded provenance
hashes:

```
PASS secrets: 0 added line(s) in 0 file(s)
PASS honesty: 0 added line(s) in 0 file(s)
PASS provenance: 275 recorded hash(es) verified
```

## How to retake this census

1. Run each command in the per suite table from the repository root,
   on a clean checkout, once per interpreter available.
2. Compare the counts against this file. The repo total changes
   whenever a suite gains or loses tests.
3. Keep the overlap rule: count suite 1, suite 2 and suite 12, and
   leave out suites 3 to 11, which suite 1 already contains.
