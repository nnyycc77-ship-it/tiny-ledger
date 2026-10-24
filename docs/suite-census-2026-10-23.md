# Offline suite census, 2026-10-24

The census for issue
[#200](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/200),
refreshing the census first filed under issue
[#112](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/112): every
offline suite in the repo, run in one pass against merged main, after
tool factory waves 1 and 2 landed. This file replaces the 2026-10-23
census in place; the numbers below are the settled counts now.

- **Main commit:** `eab32ca7aaa5fdb5dfe0acd81f05a331f597fd85` (eab32ca,
  "Merge pull request #199 from nnyycc77-ship-it/h3-pregate-capture-findings").
- **Taken:** 2026-10-24, runs started 07:57 UTC and finished by 08:02
  UTC, by H6, on a clean checkout of that commit.
- **Interpreters:** python3.12 for the Python suites and Node v24.22.1
  for the proof page tests. python3.11 and python3.13 are not installed
  in this environment, so the three interpreter cross check the first
  census ran could not be repeated; every count below is python3.12,
  the CI version.
- **Network:** none used. Every suite ran in its default offline mode.
  Live checks are opt in by environment variable, and none was set (see
  Skips).
- **How each suite was run:** from the repository root with the command
  shown. `__pycache__` folders were removed before the pass.
- **What wrote each log:** a small runner script, `run.sh`, kept outside
  the repo. It wrote the `$ command`, `# started <time> at <commit>` and
  `# exit <code>` lines around each command's own output. Those are the
  only lines in the logs that the suites did not print themselves.

## Result

**No failures anywhere in the repo.** Every suite that ran locally is
green, and the full tools suite and the api suite are both green, as
the issue's acceptance asks. The one failure the first census recorded,
`test_mcpize_listing.ListingTests.test_track_record_paragraph_is_quoted_verbatim`,
passes on this commit; its tracking issue
[#115](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/115) is
closed.

| | Python tests run | Passed | Failed | Skipped |
| --- | --- | --- | --- | --- |
| **Repo total, unique tests** | 1104 | 1097 | 0 | 7 |

The total counts each test once, on python3.12, the CI version.

| Python suite (unique tests) | Tests |
| --- | --- |
| `tools/tests` (own tests) | 730 |
| Seven agent suites | 228 |
| `near-agent/tests` | 49 |
| `api` | 88 |
| Node proof page tests | 9 |

Not in the total:

- **The Foundry suite (26 tests)** cannot run in this environment (see
  below). CI ran it on the same commit, and the job passed.
- **Two checks that are not unit test suites** both passed: the
  `api_smoke` offline run and pregate.

## Per suite

| # | Suite | Command | Tests | Passed | Failed | Skipped | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Delivery tooling, as CI runs it | `python3 -m unittest discover -s tools/tests -v` | 1007 | 1000 | 0 | 7 | 0 |
| 2 | Recall API | `python3 -m unittest discover -s api -v` | 88 | 88 | 0 | 0 | 0 |
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

### How the suites overlap

- **Suite 1 is the CI suite.** Its 1007 tests are 730 of its own, plus
  all 277 tests of suites 3 to 10. The `load_tests` shims in
  `tools/tests/test_<name>.py` pull those in: 50 + 29 + 38 + 27 + 32 +
  28 + 24 = 228 agent tests, plus 49 NEAR worker tests.
- **Splitting 1007 into 730 and 277:** each test line in the suite 1
  verbose log was grouped by its module name. The shim suites matched
  their standalone counts exactly, module for module. Two of suite 1's
  own test lines print argparse output in the middle of the verbose
  line (`test_fmcsa_carrier.FetchTests.test_main_argument_rules` and
  `test_nonprofit_pack.Inputs.test_no_entries_is_refused`), so they do
  not carry the result word on the same line; both are named here and
  counted in the 730 by subtraction: 1007 minus 277.
- **Suite 11** is the `usaspending-test.yml` workflow. Its 18 tests are
  part of suite 1's own 730.
- **The unique repo total** is suite 1, plus suite 2, plus suite 12.
  That is 1007 + 88 + 9 = 1104.

## Changes since the 2026-10-23 census

- Repo total grew from 622 to 1104 unique tests. Suite 1 grew from 547
  to 1007 (its own tests from 322 to 730, the wave 1 and 2 tool suites
  landing in `tools/tests`), suite 2 from 66 to 88 (the wave endpoint
  additions), suite 3 from 28 to 49, suite 4 from 36 to 50, suite 6
  from 35 to 38, and suite 9 from 14 to 28.
- The one failure is fixed, as recorded under Result.
- Skips went from 6 to 7: one new opt in live test,
  `test_nonprofit_pack.Live.test_live_demo_list`, joined the set.
- Pregate now reports 131 recorded provenance hashes on the clean tree,
  up from 39.

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

The `test` workflow ran on eab32ca (run 40075937698, push) and all
three of its jobs ended in success: `delivery-tool-tests` (job
120819164710), `forge-test` (job 120819164785) and `proof-page-tests`
(job 120819164556). The `USAspending fetcher tests` workflow (run
40075937853) ended in success as well.

One limit, stated plainly: the board connector this census was taken
through refuses the redirect that job log downloads use, so the CI
jobs' own log lines could not be read from here. The CI skip
comparison the first census made (CI skipping 24 media tests this
environment runs) therefore could not be repeated from evidence this
round, and no CI skip count is claimed. What is known from the job
results alone: CI is green on this commit, and the media fixture
suites (9 and 10) ran and passed here, where ffmpeg is installed.

## What could not run here

**Suite 13, AgentTab contract (Foundry), did not run.** The `forge`
binary is not installed in this environment. The full log of the run:

```
$ forge test -vvv
# started 2026-10-24T07:58:48Z at eab32ca7aaa5fdb5dfe0acd81f05a331f597fd85
/tmp/census2/run.sh: line 8: forge: command not found
# exit 127
```

No install was attempted; this is a docs only task and the CI evidence
below stands in for the local run.

**CI result on the same commit.** The `forge-test` job ran the suite
on eab32ca (job 120819164785 in run 40075937698) and completed with
success. `test/AgentTab.t.sol` declares 26 `function test` entries,
which matches the suite size the first census recorded. This census
did not observe the job's log itself (see the limit under CI on this
commit), so suite 13 is not counted in the repo total.

## Notes on suites 14 and 15

**Suite 14, `tools/api_smoke.py`.** It ran with no arguments, which is
its default offline mode. In that mode it reads the captured
transcripts in `tools/tests/fixtures/api_smoke/` and builds no
connection. Its output ends:

```
Result: PASS, every assertion held.
```

**Suite 15, pregate on the clean tree.** With no changes to gate, it
checks no added lines. It still verifies the 131 recorded provenance
hashes:

```
PASS secrets: 0 added line(s) in 0 file(s)
PASS honesty: 0 added line(s) in 0 file(s)
PASS provenance: 131 recorded hash(es) verified
```

## How to retake this census

Run each command in the per suite table from the repository root on a
clean checkout, once per interpreter available. Then compare against
this file. The repo total changes whenever a suite gains or loses
tests. The overlap rule stays the same: count suite 1, suite 2 and
suite 12, and leave out suites 3 to 11, which suite 1 already contains.
