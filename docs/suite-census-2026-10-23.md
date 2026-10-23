# Offline suite census, 2026-10-23

The census for issue
[#112](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/112): every
offline suite in the repo, run in one pass against merged main.

- **Main commit:** `b31892bf9b2b9650db650d71d8cc8b1f4a20c319` (b31892b,
  "AGENT-BRIEF: track record updated to six paid Synmerco jobs (58.10
  USDC)").
- **Taken:** 2026-10-23T16:47:29Z, by H2, on a clean checkout of that
  commit.
- **Interpreters:** python3.11, python3.12 and python3.13 for the Python
  suites, and Node v22.22.0 for the proof page tests.
- **Network:** none used. Every suite ran in its default offline mode.
  Live checks are opt in by environment variable, and none was set (see
  Skips).
- **How each suite was run:** from the repository root with the command
  shown. `__pycache__` folders were removed between runs.
- **What wrote each log:** a small runner script, `run.sh`, kept outside
  the repo. It wrote the `$ command`, `# started <time> at <commit>` and
  `# exit <code>` lines around each command's own output. Those are the
  only lines in the logs that the suites did not print themselves.

## Result

**One failure in the whole repo**, the same on all three Pythons:
`test_mcpize_listing.ListingTests.test_track_record_paragraph_is_quoted_verbatim`.
It is tracked by the new QUEUE issue
[#115](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/115).

The three pregate failures this issue expected under #105 are gone. PR #106
fixed them, and `test_pregate` passes on this commit. The one failure is
the same LISTING.md test #105 also fixed. It came back with b31892b,
because the brief changed again and the listing quote did not.

| | Python tests run | Passed | Failed | Skipped |
| --- | --- | --- | --- | --- |
| **Repo total, unique tests** | 622 | 615 | 1 | 6 |

The total counts each test once, on python3.12, the CI version. The
python3.11 and python3.13 totals are identical.

| Python suite (unique tests) | Tests |
| --- | --- |
| `tools/tests` (own tests) | 322 |
| Seven agent suites | 197 |
| `near-agent/tests` | 28 |
| `api` | 66 |
| Node proof page tests | 9 |

Not in the total:

- **The Foundry suite (26 tests)** cannot run in this environment (see
  below). CI ran it on the same commit, and all 26 passed.
- **Two checks that are not unit test suites** both passed: the
  `api_smoke` offline run and pregate.

## Per suite

The counts are the same on python3.11, 3.12 and 3.13 unless a row says
otherwise.

| # | Suite | Command | Tests | Passed | Failed | Skipped | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Delivery tooling, as CI runs it | `python3 -m unittest discover -s tools/tests -v` | 547 | 540 | 1 | 6 | 1 |
| 2 | Recall API | `python3 -m unittest discover -s api -v` | 66 | 66 | 0 | 0 | 0 |
| 3 | NEAR worker | `python3 -m unittest discover -s near-agent/tests -v` | 28 | 28 | 0 | 0 | 0 |
| 4 | Agent: call-for-me | `python3 -m unittest discover -s agents/call-for-me/tests -t agents/call-for-me/tests -v` | 36 | 35 | 0 | 1 | 0 |
| 5 | Agent: catering-finder | `python3 -m unittest discover -s agents/catering-finder/tests -t agents/catering-finder/tests -v` | 29 | 29 | 0 | 0 | 0 |
| 6 | Agent: field-service-planner | `python3 -m unittest discover -s agents/field-service-planner/tests -t agents/field-service-planner/tests -v` | 35 | 35 | 0 | 0 | 0 |
| 7 | Agent: local-quotes | `python3 -m unittest discover -s agents/local-quotes/tests -t agents/local-quotes/tests -v` | 27 | 27 | 0 | 0 | 0 |
| 8 | Agent: media-generator | `python3 -m unittest discover -s agents/media-generator/tests -t agents/media-generator/tests -v` | 32 | 32 | 0 | 0 | 0 |
| 9 | Agent: video-clipping | `python3 -m unittest discover -s agents/video-clipping/tests -t agents/video-clipping/tests -v` | 14 | 14 | 0 | 0 | 0 |
| 10 | Agent: video-dubbing | `python3 -m unittest discover -s agents/video-dubbing/tests -t agents/video-dubbing/tests -v` | 24 | 24 | 0 | 0 | 0 |
| 11 | USAspending workflow subset | `python3 -m unittest discover -s tools/tests -p 'test_usaspending_awards.py' -v` | 18 | 17 | 0 | 1 | 0 |
| 12 | Proof page logic | `node --test app/proof-core.test.mjs` | 9 | 9 | 0 | 0 | 0 |
| 13 | AgentTab contract (Foundry) | `forge test -vvv` | 26 in CI | not run here | | | 127 |
| 14 | Recall API smoke, offline | `python3 tools/api_smoke.py` | see note | PASS | | | 0 |
| 15 | Pregate on the clean tree | `python3 tools/pregate.py` | 3 checks | 3 | 0 | | 0 |

### How the suites overlap

- **Suite 1 is the CI suite.** Its 547 tests are 322 of its own, plus all
  225 tests of suites 3 to 10. The `load_tests` shims in
  `tools/tests/test_<name>.py` pull those in: 36 + 29 + 35 + 27 + 32 + 14
  + 24 = 197 agent tests, plus 28 NEAR worker tests.
- **Splitting 547 into 322 and 225:** each test line in the suite 1
  verbose log was grouped by its module name. The 225 match the standalone
  counts of suites 3 to 10 exactly.
- **Suite 11** is the `usaspending-test.yml` workflow. Its 18 tests are
  part of suite 1's own 322.
- **The unique repo total** is suite 1, plus suite 2, plus suite 12. That
  is 547 + 66 + 9 = 622.

## The one failure

- **Suite:** 1, on python3.11, 3.12 and 3.13.
- **Command:** `python3 -m unittest discover -s tools/tests -v`
- **Test:** `test_track_record_paragraph_is_quoted_verbatim (test_mcpize_listing.ListingTests.test_track_record_paragraph_is_quoted_verbatim)`
- **Tracked by:** QUEUE issue
  [#115](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/115),
  filed from this census. #105, which fixed the same test before, is
  closed. #115 carries the evidence and points to the tested patch on
  [#105](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/105#issuecomment-6369914686).
- **CI:** `delivery-tool-tests` failed on this commit (job 120528811112).

First lines of the failure output (python3.12):

```
FAIL: test_track_record_paragraph_is_quoted_verbatim (test_mcpize_listing.ListingTests.test_track_record_paragraph_is_quoted_verbatim)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/tiny-ledger/tools/tests/test_mcpize_listing.py", line 83, in test_track_record_paragraph_is_quoted_verbatim
    self.assertIn(quoted, LISTING)
```

The assertion that follows says that the six-job paragraph from
`AGENT-BRIEF.md` is not found in `packaging/mcpize/LISTING.md`, which still
quotes the five-job paragraph. The full message is in #115.

## Skips

Every skip is a live check that runs only when an environment variable
is set. The skip reasons below are copied from the suite 1 verbose log.

| Test | Suite | Skip reason as printed |
| --- | --- | --- |
| `test_cpsc_recalls.LiveTests.test_cli_nonempty_and_empty_with_excluded_near_match` | 1 | `set CPSC_LIVE=1 for public API checks` |
| `test_cpsc_recalls.LiveTests.test_cli_title_and_number_query_shapes` | 1 | `set CPSC_LIVE=1 for public API checks` |
| `test_edgar_formd.LiveTests.test_cli_against_edgar` | 1 | `set EDGAR_LIVE=1 and EDGAR_CONTACT for a live EDGAR check` |
| `test_propublica_nonprofits.Live.test_live_organization_matches_capture_identity` | 1 | `set PROPUBLICA_LIVE=1 to query the live API` |
| `test_usaspending_awards.LiveTests.test_live_queries_return_valid_evidence` | 1, 11 | `opt-in live public API check` |
| `test_call_flow.DocsAndSourcesTests.test_captures_verify` | 1, 4 | `set CALL_FOR_ME_CAPTURES to a folder of fetched captures` |

## What could not run here

**Suite 13, AgentTab contract (Foundry), did not run.** The `forge`
binary is not installed in this environment. The full log of
the run:

```
$ forge test -vvv
# started 2026-10-23T16:47:29Z at b31892bf9b2b9650db650d71d8cc8b1f4a20c319
/tmp/claude-0/-home-user-tiny-ledger/ebdc6009-69ea-5cde-983b-13a255e93c3b/scratchpad/census/run.sh: line 11: forge: command not found
# exit 127
```

Installing it was not possible either. Both install hosts are refused by
this environment's egress proxy:

- `https://foundry.paradigm.xyz` answered HTTP code `000`;
- `https://github.com/foundry-rs/foundry/releases` answered `403`.

**CI result on the same commit.** The `forge-test` job ran the suite on
b31892b (job 120528811313, completed 2026-10-23T16:28:32Z). Its log ends:

```
Suite result: ok. 26 passed; 0 failed; 0 skipped; finished in 2.21ms (6.22ms CPU time)

Ran 1 test suite in 5.76ms (2.21ms CPU time): 26 tests passed, 0 failed, 0 skipped (26 total tests)
```

`test/AgentTab.t.sol` declares 26 `function test` entries, which matches.
This census did not observe that run itself, so suite 13 is not counted
in the repo total.

## Notes on suites 14 and 15

**Suite 14, `tools/api_smoke.py`.** It ran with no arguments, which is its
default offline mode. In that mode it reads the captured transcripts in
`tools/tests/fixtures/api_smoke/` and builds no connection. Its output
says:

```
## Recall API smoke checks (offline: captured fixtures)

Read only: GET requests with no X-PAYMENT header; nothing is paid.

Result: PASS, every assertion held.
```

**Suite 15, pregate on the clean tree.** With no changes to gate, it
checks no added lines. It still verifies the 39 recorded provenance
hashes:

```
PASS secrets: 0 added line(s) in 0 file(s)
PASS honesty: 0 added line(s) in 0 file(s)
PASS provenance: 39 recorded hash(es) verified
```

## How to retake this census

Run each command in the per suite table from the repository root on a
clean checkout, once per interpreter. Then compare against this file.
The repo total changes whenever a suite gains or loses tests. The overlap
rule stays the same: count suite 1, suite 2 and suite 12, and leave out
suites 3 to 11, which suite 1 already contains.
