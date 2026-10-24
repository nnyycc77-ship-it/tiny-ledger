# `address_geocode_check`: US address geocode check

A tool factory wave 3 tool (issue #319).
- **Code:** the fetcher is
  [`tools/address_geocode_check.py`](../../tools/address_geocode_check.py).
  The pay per call API serves it as `GET /geocode?address=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not yet registered on the MCP server.** This PR lands the fetcher,
  the API dispatcher, this page and the offline tests only, per the
  wave registration ruling on issue #158. Registration on the server
  and going live still wait on the separate surface and owner redeploy
  steps.

## The tool at a glance

- **What it answers:** for one US street address, what the US Census
  Bureau geocoder matches it to:
  - the matched address (`matchedAddress`), as shown;
  - the coordinates, `x` the longitude and `y` the latitude, as shown;
  - the county, the `Counties` geography's `NAME` and `GEOID`, as
    shown;
  - the census tract `GEOID`, when the `Census Tracts` geography is
    returned;
  - the address components (city, state, ZIP) as shown.
- **Coordinates are interpolated** along the matched address range by
  the geocoder; they are not a rooftop or parcel point. Every report
  says so.
- **Source, keyless:** the Census Geocoder,
  `https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress`
  with `benchmark=Public_AR_Current&vintage=Current_Current&format=json`,
  as documented at
  <https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html>.
  The benchmark and the vintage are pinned because an unpinned pair
  drifts silently as the Census Bureau republishes. The geographies
  endpoint is used rather than locations/onelineaddress because it
  returns the county and the census tract with the match.
- **Where the query shape and field names come from:** the live
  captures recorded in `tools/tests/fixtures/census-geocoder/`
  (provenance in `provenance.json`), taken with the tool's own fetch
  for this issue: a match (1600 Pennsylvania Ave NW, Washington, DC
  20500) and a no match.
- **Arguments:** `address`, a US street address of 1 to 200 characters.
- **Needs on the server:** outbound HTTPS to
  `geocoding.geo.census.gov`, and no key.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The answer first.** For each match: the matched address, the
  coordinates, the county, the census tract GEOID when returned, and
  the address components, each marked "as shown". When the geocoder
  returns several matches, each is listed and numbered.
- **Then the evidence.** The exact query URL, the UTC retrieval time,
  the fields cut verbatim from the response, and the complete raw
  response (status line, headers, body). A `Set-Cookie` header is noted
  and not printed.

**Empty results are reports, with the raw body as the proof:**
- **No match:** an empty `addressMatches` array is reported as no
  match for this input, with the complete raw response as the proof.
  It is never shown as a statement that no such address exists.

**Failures:** these give no report, with exit 2 on the CLI and 502 on
the API:
- a failed or timed out request;
- any status but 200;
- a redirect off the source host;
- a body without the documented shape (a match with no coordinates,
  no county, or coordinates out of range included).

A failure is unknown, never a no match.

## Running it

```sh
python3 tools/address_geocode_check.py 1600 Pennsylvania Ave NW, Washington, DC 20500
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_address_geocode_check.py' -v
```

The tests run offline, on the fixtures in
`tools/tests/fixtures/census-geocoder/` (provenance in
`provenance.json`): two REAL CAPTURES taken live for this issue, a
match and a no match, verbatim with their hashes. A live smoke run for
this issue covered both addresses end to end through the tool itself.
