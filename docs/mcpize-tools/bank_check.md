# `bank_check`: FDIC BankFind bank check

A tool factory wave 3 tool (issue #320, parent #305).
- **Code:** the fetcher is
  [`tools/bank_check.py`](../../tools/bank_check.py). The pay per call API
  serves it as `GET /bank?name=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not registered on the MCP server.** This PR follows the wave 1 and 2
  shape: fetcher, API dispatcher and this page. Registration on the
  server is a separate shared surface step, and going live waits on the
  owner redeploy step.

## The tool at a glance

- **What it answers:** which FDIC insured institutions have a name
  beginning with the typed name, and for each of them the FDIC
  certificate number, the city and state, and the active status, each
  exactly as the FDIC BankFind Institutions API returns it. Or a proven
  no match, under the rule below.
- **Source:** FDIC BankFind API,
  `GET https://banks.data.fdic.gov/api/Institutions` (the API redirects
  the request to `api.fdic.gov/banks/...`; the report prints the final
  URL when that happens).
  - **Keyless.** No `api_key` parameter is ever sent. The wave 3 source
    check (issue #305 research) found the API answers full real data
    with no key at all, and refuses an invalid key outright, so a
    placeholder key would be worse than none.
  - **The snapshot.** Every report names the FDIC index snapshot the
    answer came from (`meta.index` name and its `createTimestamp`), as
    returned. The answer is the index as built at that time, not a live
    register.
- **Arguments:** `name`, the start of the bank's name as FDIC lists it,
  with at least 3 letters or digits; the first word needs at least 2 and
  no filter characters.
- **Needs on the server:** outbound HTTPS to `banks.data.fdic.gov` and
  `api.fdic.gov`, and no key.
- **What it is not:** a check that a bank is safe, solvent or open
  today. "Active" is FDIC's ACTIVE field as shown (1 active, 0 not
  active). Money fields are not requested and never printed: FDIC
  reports money in thousands of dollars, and this tool does not need
  them.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## How the match works

The API's `NAME` filter is a prefix match on the whole name field,
verified live on issue #320: `NAME:Chase*` returns only names beginning
with Chase, and the quoted phrase form `NAME:"JPMorgan Chase Bank"`
returns total 0 for a bank that plainly exists, so the phrase form is
never used. The tool sends the typed name's first word with a trailing
wildcard (`NAME:{first word}*`, page limit 5000), then keeps, locally,
the institutions whose name, after folding case and accents and
replacing every other non letter or digit character with a space,
begins with the whole typed name at a word boundary.

So the name must be typed as FDIC lists it, from its start:
"JPMorgan Chase Bank" finds JPMorgan Chase Bank, National Association
(and the Dearborn charter, whose name also begins that way), while
"Chase Bank" alone cannot find it. The report states this rule and the
page total, so the reader can see exactly what was searched.

## What a report contains

- **The request.** The exact query, a note that it was sent keyless, the
  UTC retrieval time, the final URL when the API redirected, and the
  index snapshot identity.
- **The rule and the counts.** The matching rule, the prefix page total,
  and how many institutions on the page matched.
- **Each match.** The institution name as its heading, then CERT, CITY,
  STNAME and ACTIVE as shown, with the active reading in words.
- **The evidence.** The complete raw response under the source link.

**No match:** reported only when the fetched page is the whole
candidate set (page total no larger than the rows returned) and no row
on it matches under the rule. The full raw response is the proof.

**Failures:** these give no report, with exit 2 on the CLI and 502 on
the API:

- any status other than 200 (a refusal is never a no match);
- a redirect to a host other than `banks.data.fdic.gov` or
  `api.fdic.gov`;
- a failed request;
- a body that is not the documented Institutions shape;
- a page total larger than the rows returned, because then a no match
  could not be proven.

## Running it

```sh
python3 tools/bank_check.py "JPMorgan Chase Bank"
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_bank_check.py' -v
```

The tests run offline on three live captures (fixtures in
`tools/tests/fixtures/bank-check/` with their hashes in
`provenance.json`): the JPMorgan page (3 institutions, 2 matches), the
Wells Fargo page (38 institutions, 29 matches), and a page whose total
is 0, plus derived variants for the unprovable page and the malformed
body, and the GET /bank route. The live smoke run for this build is
recorded on the PR for issue #320.
