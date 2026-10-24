# Offline suite census, 2026-10-24 (tenth pass)

The census for issue
[#344](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/344). It
refreshes the censuses filed under issues
[#112](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/112),
[#200](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/200),
[#236](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/236),
[#247](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/247),
[#259](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/259),
[#269](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/269),
[#277](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/277),
[#286](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/286) and
[#301](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/301).
Every offline suite in the repo was run in one pass against merged
main.

The #301 census was pinned to 65dde36. Thirteen PRs merged after it
(#306, #307, #308, #313, #314, #315, #316, #325, #328, #333, #335, #336
and #340). This census is pinned to aa39a75, the commit issue #344
names, which was also merged main when the run was taken. This file
replaces the #301 census in place, as each census replaced the one
before. The numbers below are the counts the runs returned.

- **Main commit:** `aa39a753359d5db05deb417956ccb9b586584c6d`
  (aa39a75, "Merge pull request #340 from
  nnyycc77-ship-it/h5-wallet-check").
- **Taken:** 2026-10-24, by H5, on a clean detached checkout of that
  commit. Runs started at 13:25:54 UTC; the last started at 13:31:05
  UTC.
- **Interpreters:** python3.12 (3.12.3) is the only Python installed in
  this environment, and it is the interpreter the `test` workflow pins,
  so every Python count below is the python3.12 run. Two limits follow,
  stated plainly: python3.11 and python3.13 are not installed here, so
  the cross interpreter rerun the earlier censuses did could not be
  repeated, and suite 11, whose workflow pins python3.11, is counted
  from the python3.12 run. Node here is v24.22.1, while the `test`
  workflow pins Node major version 22; the proof page tests ran on the
  installed v24.
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
| **Repo total, unique tests** | 1369 | 1362 | 0 | 7 |

The total counts each test once, on python3.12, the CI version.

| Suite (unique tests) | Tests |
| --- | --- |
| `tools/tests` (own tests) | 986 |
| Seven agent suites | 228 |
| `near-agent/tests` | 49 |
| `api` | 97 |
| Node proof page tests | 9 |

986 + 228 + 49 + 97 + 9 = 1369.

Not in the total:

- **The Foundry suite (26 tests)** cannot run in this environment (see
  below). CI ran it on the same commit, and the job passed.
- **Two checks that are not unit test suites** both passed: the
  `api_smoke` offline run and pregate.

## Per suite

Counts are from the python3.12 run. The commands are written with
`python3`, as the workflows write them; each was run as
`python3.12 ...`.

| # | Suite | Command | Tests | Passed | Failed | Skipped | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Delivery tooling, as CI runs it | `python3 -m unittest discover -s tools/tests -v` | 1263 | 1256 | 0 | 7 | 0 |
| 2 | Recall API | `python3 -m unittest discover -s api -v` | 97 | 97 | 0 | 0 | 0 |
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

### Interpreter note

Earlier censuses ran suites 1 to 11 and suite 14 under python3.11,
python3.12 and python3.13 and found identical counts on all three.
This pass could not repeat that check: only python3.12 is installed in
this environment, and no other interpreter was installed for a docs
only task. Every count in this file is therefore the python3.12 run,
and suite 11's count is the python3.12 run of a suite whose workflow
pins python3.11. The proof page tests ran on Node v24.22.1; the
workflow pins Node major version 22.

### How the suites overlap

- **Suite 1 is the CI suite.** Its 1263 tests are 986 of its own, plus
  all 277 tests of suites 3 to 10. The `load_tests` shims in
  `tools/tests/test_<name>.py` pull those in: 50 + 29 + 38 + 27 + 32 +
  28 + 24 = 228 agent tests, plus 49 NEAR worker tests.
- **Splitting 1263 into 986 and 277.** The test ids in each standalone
  log for suites 3 to 10 were matched against the suite 1 verbose log.
  Every standalone suite's full id set appears inside suite 1 with the
  same count, so suite 1 holds 277 shim tests and 1263 − 277 = 986 of
  its own.
- **Result words.** 1223 of suite 1's 1263 test lines carry their
  result word on the same line: 1216 `ok` and 7 `skipped`. The other
  40 do not, and none of them failed, because the run ended
  `OK (skipped=7)`. They break down as follows:
  - **37 tests with a docstring.** unittest prints the docstring on
    the line after the name, and the result word follows it. These are
    the per route and per tool same-text tests in
    `test_wave1_integration` (10), `test_wave2_integration` (8),
    `test_wave1_mcp_integration` (10) and `test_mcp_wave2_integration`
    (9).
  - **3 tests that print output in the middle of their line:**
    `test_fmcsa_carrier.FetchTests.test_main_argument_rules`,
    `test_nonprofit_pack.Inputs.test_no_entries_is_refused` and
    `test_rdap_discriminate.RenderTests.test_bad_input_is_refused_before_any_request`.
    They print argparse usage or an error message they expect, so the
    result word moves later in the line.
- **Suite 11** is the `usaspending-test.yml` workflow. Its 18 tests
  are part of suite 1's own 986.
- **The unique repo total** is suite 1, plus suite 2, plus suite 12:
  1263 + 97 + 9 = 1369. The skips are suite 1's 7, which include the
  skips of suites 4 and 11. So 1369 − 7 = 1362 passed.

## Changes since the #301 census

- **Repo total:** 1268 → 1369 unique tests: 1362 passed, 0 failed, 7
  skipped. The whole increase is suite 1 (+98) and suite 2 (+3).
- **Suite 1:** 1165 → 1263. The +98 is exactly the six wave 3 tool
  suites that merged after 65dde36, counted from this run's log:
  `test_weather_alert_check` 19 (PR #325), `test_npi_check` 20
  (PR #335), `test_bank_check` 11 (PR #328),
  `test_disaster_history_check` 20 (PR #333),
  `test_address_geocode_check` 12 (PR #336) and `test_wallet_check` 16
  (PR #340). 19 + 20 + 11 + 20 + 12 + 16 = 98. Own tests are 986
  (888 + 98); the shim count is unchanged at 277, and every shim
  suite's ids inside suite 1 match its standalone run.
- **Suite 2 (api):** 94 → 97, all of it in `test_endpoints` (42 → 45),
  from the suite 2 log; `test_recall_api` 25, `test_payment_gate` 22
  and `test_openapi_alignment` 5 are unchanged. 45 + 25 + 22 + 5 = 97.
- **Suites 3 to 12:** unchanged counts. Nothing changed under
  `near-agent`, `agents`, `app` or `test` between the two pins.
- **Result words:** 1216 `ok` and 7 `skipped` on the same line; the
  suite 1 lines without a result word on the same line fell from 41
  to 40. The docstring group is the same 37. The print group lost one:
  `test_hosted_mcp_probe.ProbeCannotRunTests.test_main_returns_2_when_the_probe_cannot_run`
  carried its `ok` on the same line in this run, leaving 3.
- **Skips:** unchanged at 7, the same seven tests with the same
  reasons.
- **Pregate:** reports 237 recorded provenance hashes on the clean
  tree, up from 206, as the wave 3 fixture sets landed.

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

**The `test` workflow** ran on aa39a75 (run 40097857437, push). All
three of its jobs ended in success:

- `delivery-tool-tests` (job 120883768515);
- `forge-test` (job 120883768540);
- `proof-page-tests` (job 120883768337).

**The `USAspending fetcher tests` workflow** (run 40097857453, job
120883768306) ended in success as well.

**One limit, stated plainly:** this census read the runs' and jobs'
results only. No CI test or skip count is claimed. What the job
results show is that CI is green on this commit.

## What could not run here

**Suite 13, AgentTab contract (Foundry), did not run.** The `forge`
binary is not installed in this environment. The full log of the run:

```
$ forge test -vvv
# started 2026-10-24T13:31:05Z at aa39a753359d5db05deb417956ccb9b586584c6d
/home/hatch/workspace/agents/h5/census344-logs/run.sh: line 10: forge: command not found
# exit 127
```

No install was attempted, because this is a docs only task. The CI
evidence stands in for the local run.

**CI result on the same commit.** The `forge-test` job ran the suite
on aa39a75 (job 120883768540 in run 40097857437) and completed with
success. `test/AgentTab.t.sol` declares 26 `function test` entries,
matching the suite size every earlier census recorded. This census
did not observe the job's log itself (see the limit under CI on this
commit), so suite 13 is not counted in the repo total.

**The cross interpreter rerun did not run either.** python3.11 and
python3.13 are not installed in this environment, so the three
interpreter comparison the earlier censuses published could not be
repeated. See the interpreter note above.

## Notes on suites 14 and 15

**Suite 14, `tools/api_smoke.py`.** It ran with no arguments, its
default offline mode. In that mode it reads the captured transcripts
in `tools/tests/fixtures/api_smoke/` and makes no connection. Its
result line:

```
Result: PASS, every assertion held.
```

**Suite 15, pregate on the clean tree.** With no changes to gate, it
checks no added lines. It still verifies the 237 recorded provenance
hashes:

```
PASS secrets: 0 added line(s) in 0 file(s)
PASS honesty: 0 added line(s) in 0 file(s)
PASS provenance: 237 recorded hash(es) verified
```

## How to retake this census

1. Run each command in the per suite table from the repository root,
   on a clean checkout, once per interpreter available.
2. Compare the counts against this file. The repo total changes
   whenever a suite gains or loses tests.
3. Keep the overlap rule: count suite 1, suite 2 and suite 12, and
   leave out suites 3 to 11, which suite 1 already contains.
