# Offline suite census, 2026-10-24 (fifth pass)

The census for issue
[#259](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/259). It
refreshes the censuses filed under issues
[#112](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/112),
[#200](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/200),
[#236](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/236) and
[#247](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/247). Every
offline suite in the repo was run in one pass against merged main.

The #247 census was pinned to 80e6464. Six PRs merged after it: the four
the issue names (#254, #256, #249, #255), then #262 and #253, which landed
while this census was being taken. The census is pinned to the newest of
those merges, so it measures main as it stands. This file replaces the #247
census in place, as each census replaced the one before. The numbers below
are the settled counts now.

- **Main commit:** `af30eb423ef090bfd2adaff7db44ae4bfb4d50e5` (af30eb4,
  "Merge pull request #253 from nnyycc77-ship-it/h3-openapi-seven-routes").
- **Taken:** 2026-10-24, by H4, on a clean checkout of that commit. Runs
  started at 10:26 UTC and finished by 10:31 UTC.
- **Interpreters:** each suite ran first on the interpreter its workflow
  pins:
  - python3.12 for the `test` workflow's two suites;
  - python3.11 for the `USAspending fetcher tests` workflow (suite 11);
  - Node v22.22.0 for the proof page tests, the major version the `test`
    workflow pins.

  Every Python suite was also run under the other two of python3.11,
  python3.12 and python3.13 (`python3` here is python3.13.16), and the
  counts were identical (see the cross check below). The headline counts
  are the python3.12 run.
- **Network:** none used. Every suite ran in its default offline mode.
  Live checks are opt in by environment variable, and none was set (see
  Skips).
- **How each suite was run:** from the repository root with the command
  shown. `__pycache__` folders were removed before the pass, and
  `PYTHONDONTWRITEBYTECODE=1` was set, so the tree stayed clean.
- **What wrote each log:** a small runner script, `run.sh`, kept outside
  the repo. It wrote the `$ command`, `# started <time> at <commit>` and
  `# exit <code>` lines around each command's own output. Those are the
  only lines in the logs that the suites did not print themselves.

## Result

**No failures anywhere in the repo.** Every suite that ran locally is
green, on all three interpreters. That includes the full tools suite and
the api suite, which the acceptance asks for. No failure was found, so no
QUEUE issue was filed.

| | Python and Node tests run | Passed | Failed | Skipped |
| --- | --- | --- | --- | --- |
| **Repo total, unique tests** | 1262 | 1255 | 0 | 7 |

The total counts each test once, on python3.12, the CI version.

| Suite (unique tests) | Tests |
| --- | --- |
| `tools/tests` (own tests) | 887 |
| Seven agent suites | 228 |
| `near-agent/tests` | 49 |
| `api` | 89 |
| Node proof page tests | 9 |

887 + 228 + 49 + 89 + 9 = 1262.

Not in the total:

- **The Foundry suite (26 tests)** cannot run in this environment (see
  below). CI ran it on the same commit, and the job passed.
- **Two checks that are not unit test suites** both passed: the
  `api_smoke` offline run and pregate.

## Per suite

Counts are from the python3.12 run. Suite 11 has the same counts on
python3.11, its workflow's interpreter. The commands are written with
`python3`, as the workflows write them; each was run as `python3.11 ...`,
`python3.12 ...` and `python3.13 ...`.

| # | Suite | Command | Tests | Passed | Failed | Skipped | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Delivery tooling, as CI runs it | `python3 -m unittest discover -s tools/tests -v` | 1164 | 1157 | 0 | 7 | 0 |
| 2 | Recall API | `python3 -m unittest discover -s api -v` | 89 | 89 | 0 | 0 | 0 |
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
failures and no errors. For suite 12, node printed `# tests 9`, `# pass 9`
and `# fail 0`.

### Interpreter cross check

Suites 1 to 11 and suite 14 were each run under python3.11, python3.12
and python3.13. Every pair of logs agreed on the tests run, the skips and
the exit code:

| # | python3.11 | python3.12 | python3.13 |
| --- | --- | --- | --- |
| 1 | 1164, OK (skipped=7) | 1164, OK (skipped=7) | 1164, OK (skipped=7) |
| 2 | 89, OK | 89, OK | 89, OK |
| 3 | 49, OK | 49, OK | 49, OK |
| 4 | 50, OK (skipped=1) | 50, OK (skipped=1) | 50, OK (skipped=1) |
| 5 | 29, OK | 29, OK | 29, OK |
| 6 | 38, OK | 38, OK | 38, OK |
| 7 | 27, OK | 27, OK | 27, OK |
| 8 | 32, OK | 32, OK | 32, OK |
| 9 | 28, OK | 28, OK | 28, OK |
| 10 | 24, OK | 24, OK | 24, OK |
| 11 | 18, OK (skipped=1) | 18, OK (skipped=1) | 18, OK (skipped=1) |
| 14 | PASS, exit 0 | PASS, exit 0 | PASS, exit 0 |

### How the suites overlap

- **Suite 1 is the CI suite.** Its 1164 tests are 887 of its own, plus
  all 277 tests of suites 3 to 10. The `load_tests` shims in
  `tools/tests/test_<name>.py` pull those in: 50 + 29 + 38 + 27 + 32 +
  28 + 24 = 228 agent tests, plus 49 NEAR worker tests.
- **Splitting 1164 into 887 and 277.** Each test line in the suite 1
  verbose log was grouped by its module name. For every shim suite, the
  per module counts inside suite 1 matched its standalone run exactly, so
  suite 1 holds 277 shim tests and 1164 − 277 = 887 of its own.
- **Result words.** 1123 of suite 1's 1164 test lines carry their result
  word on the same line: 1116 `ok` and 7 `skipped`. The other 41 do not,
  and none of them failed, because the run ended `OK (skipped=7)`. They
  break down as follows:
  - **37 tests with a docstring.** unittest prints the docstring on the
    line after the name, and the result word follows it. These are the
    per route and per tool same-text tests in `test_wave1_integration`
    (10), `test_wave2_integration` (8), `test_wave1_mcp_integration` (10)
    and `test_mcp_wave2_integration` (9).
  - **4 tests that print output in the middle of their line:**
    `test_fmcsa_carrier.FetchTests.test_main_argument_rules`,
    `test_hosted_mcp_probe.ProbeCannotRunTests.test_main_returns_2_when_the_probe_cannot_run`,
    `test_nonprofit_pack.Inputs.test_no_entries_is_refused` and
    `test_rdap_discriminate.RenderTests.test_bad_input_is_refused_before_any_request`.
    They print argparse usage or an error message they expect, so the
    result word moves later in the line.
- **Suite 11** is the `usaspending-test.yml` workflow. Its 18 tests are
  part of suite 1's own 887.
- **The unique repo total** is suite 1, plus suite 2, plus suite 12:
  1164 + 89 + 9 = 1262. The skips are suite 1's 7, which include the
  skips of suites 4 and 11. So 1262 − 7 = 1255 passed.

## Changes since the #247 census

- **Repo total:** grew from 1253 to 1262 unique tests (+9).
- **Suite 1:** grew from 1155 to 1164 (+9). Its own tests grew from 878
  to 887; the shim suites stayed at 277. All 9 come from the two test
  modules the six merges touched, counted from the suite 1 logs of both
  censuses, grouped by module:

  | Module | Tests at 80e6464 | Tests at af30eb4 | Change |
  | --- | --- | --- | --- |
  | `test_api_smoke` | 27 | 33 | +6 |
  | `test_ofac_sdn_check` | 15 | 18 | +3 |

  6 + 3 = 9. Between the two commits no other test module under
  `tools/tests` changed. Under `api`, `near-agent`, `agents`, `app` and
  `test`, the only file changed is `api/openapi.json`, which holds no
  tests; the api suite stays at 89.
- **Suites 2 to 12:** unchanged.
- **Result words:** the 41 lines without a result word on the same line
  are the same 41 tests as before.
- **Skips:** unchanged at 7, the same seven tests with the same reasons.
- **Pregate:** reports 206 recorded provenance hashes on the clean tree,
  up from 190.

## Skips

Every skip is a live check that runs only when an environment variable
is set. The skip reasons below are copied from the suite 1 verbose log.

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

**The `test` workflow** ran on af30eb4 (run 40085666837, push). All three
of its jobs ended in success:
- `delivery-tool-tests` (job 120847963270);
- `forge-test` (job 120847963230);
- `proof-page-tests` (job 120847963090).

**The `USAspending fetcher tests` workflow** (run 40085666882, job
120847963427) ended in success as well.

**One limit, stated plainly:** the job log download redirects to a
storage host that this environment's proxy refuses (`CONNECT tunnel
failed, response 403`). The CI jobs' own log lines could not be read from
here. No CI test or skip count is claimed. What the job results show is
that CI is green on this commit.

## What could not run here

**Suite 13, AgentTab contract (Foundry), did not run.** The `forge`
binary is not installed in this environment. The full log of the run:

```
$ forge test -vvv
# started 2026-10-24T10:30:24Z at af30eb423ef090bfd2adaff7db44ae4bfb4d50e5
/tmp/claude-0/-home-user-tiny-ledger/f93df76c-ca5d-58a0-b5ec-8e06d29d5672/scratchpad/census6/run.sh: line 4: forge: command not found
# exit 127
```

No install was attempted, because this is a docs only task. The CI
evidence stands in for the local run.

**CI result on the same commit.** The `forge-test` job ran the suite on
af30eb4 (job 120847963230 in run 40085666837) and completed with
success. `test/AgentTab.t.sol` declares 26 `function test` entries,
matching the suite size every earlier census recorded. This census did
not observe the job's log itself (see the limit under CI on this commit),
so suite 13 is not counted in the repo total.

## Notes on suites 14 and 15

**Suite 14, `tools/api_smoke.py`.** It ran with no arguments, its default
offline mode. In that mode it reads the captured transcripts in
`tools/tests/fixtures/api_smoke/` and makes no connection. Its result
line, under each of the three interpreters:

```
Result: PASS, every assertion held.
```

**Suite 15, pregate on the clean tree.** With no changes to gate, it
checks no added lines. It still verifies the 206 recorded provenance
hashes:

```
PASS secrets: 0 added line(s) in 0 file(s)
PASS honesty: 0 added line(s) in 0 file(s)
PASS provenance: 206 recorded hash(es) verified
```

## How to retake this census

1. Run each command in the per suite table from the repository root, on
   a clean checkout, once per interpreter available.
2. Compare the counts against this file. The repo total changes whenever
   a suite gains or loses tests.
3. Keep the overlap rule: count suite 1, suite 2 and suite 12, and leave
   out suites 3 to 11, which suite 1 already contains.
