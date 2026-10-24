# `npi_check`: CMS NPI Registry lookup

A tool factory wave 3 tool (issue #326).

- **Code:** the fetcher is
  [`tools/npi_check.py`](../../tools/npi_check.py). The pay per call
  API serves it as `GET /npi?query=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not yet registered on the MCP server.** This PR adds the fetcher,
  the API dispatcher, this page, and the offline tests only. MCP
  surface registration is a separate later shared step, and going
  live waits on the owner redeploy after that.

## The tool at a glance

- **What it answers:** for one US healthcare provider name, or one
  10 digit NPI number, what the CMS NPI Registry (NPPES) holds: for
  each matching provider, the NPI number (`number`), the enumeration
  type, the name and credential as shown, the status, every taxonomy
  (`desc` and `code`, with its `primary` flag as shown), and the
  practice state.
- **Practice state rule, stated rather than assumed:** the state of
  the first address tagged `address_purpose` LOCATION; when a record
  shows no LOCATION address, the state of the first MAILING address,
  labelled as mailing either way in the line itself.
- **Observation only:** the registry is maintained on its own clock.
  Another source naming the same provider can differ (the wave 3
  source check found the same NPI in the wave 2 exclusion file with a
  different credential and state); the tool reports the registry as
  itself and never merges sources.
- **Source, keyless:** the NPPES NPI Registry API at
  `https://npiregistry.cms.hhs.gov/api/` with `version=2.1`, which is
  required. No key exists for this API and none is sent.
- **Where the response shape and traps come from:** the wave 3
  source check (issue #305 research) plus live captures made for
  this issue on 2026-10-24, committed under
  `tools/tests/fixtures/npi/` with their provenance:
  - a normal answer is an object with `result_count` and `results`;
  - an `Errors` document can arrive at HTTP 200 (an unsupported
    version is one case) and is refused, never read as empty;
  - `result_count` is capped by the page `limit`, so it is never a
    total: name searches page with `skip` until a short page, up to
    5 pages per interpretation, and the report counts the records
    actually returned, naming the cap when it is hit;
  - a record can list several taxonomies with none flagged primary,
    so every taxonomy is listed with its flag as shown.
- **Arguments:** one `query`: an NPI number (exactly 10 digits) or a
  provider name. A name is read two ways and both are reported: as an
  individual (first word as `first_name`, last word as `last_name`;
  a single word as `last_name`) and as an organization (the whole
  name as `organization_name`).
- **Needs on the server:** outbound HTTPS to
  `npiregistry.cms.hhs.gov`, and no key.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The answer first.** One section per interpretation, counting the
  records actually returned across its pages, then one block per
  provider with the fields above, each marked "as shown".
- **Then the evidence.** For every query page: the exact query URL,
  the UTC retrieval time, the fields cut verbatim from the response,
  and the complete raw response (status line, headers, body). A
  `Set-Cookie` header, when one is returned, is counted in a note but
  not printed.

## How an empty or failed lookup is reported

- **No match:** every interpretation ends with `result_count` 0 and
  an empty `results` array; the report says no matching provider
  under any interpretation, and the complete raw responses printed in
  the evidence are the proof. It is the registry's answer at the
  retrieval time only, never a statement that the provider does not
  exist.
- **Failed:** a failed or timed out request, any status but 200, a
  redirect off `npiregistry.cms.hhs.gov`, an `Errors` document, or a
  body without the documented shape stops the run with exit 2 and no
  report. A failed fetch is reported as unknown, never as a negative
  claim.
