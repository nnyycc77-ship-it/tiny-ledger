# `flood_check`: FEMA flood zone check

A tool factory wave 2 tool (issue #175).
- **Code:** the fetcher is
  [`tools/flood_check.py`](../../tools/flood_check.py). The pay per call
  API serves it as `GET /flood?lat=...&lon=...` or
  `GET /flood?address=...` ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not on the MCP server yet.** Under the wave registration ruling on
  #158, confirmed for wave 2 on #175, every wave tool that passes review is
  registered on the server in one shared surface PR at the end of the
  wave. Going live is one owner redeploy step after that.

## The tool at a glance

- **What it answers:** for one point, or one US street address, what the
  FEMA National Flood Hazard Layer (NFHL) shows there:
  - the flood zone (`FLD_ZONE`) and zone subtype (`ZONE_SUBTY`);
  - SFHA, true when `SFHA_TF` is `T` and false when it is `F`;
  - the static BFE (`STATIC_BFE`), shown as none when the service returns
    -9999;
  - the DFIRM ID;
  - the FIRM panel (`FIRM_PAN`), its type, and its effective date
    (`EFF_DATE`), the raw epoch milliseconds first and the UTC date after.
- **Screening only:** not a Standard Flood Hazard Determination and not
  insurance advice. Every report says so.
- **Sources, both keyless:**
  - FEMA NFHL MapServer point queries on layer 28 (Flood Hazard Zones)
    and layer 3 (FIRM Panels), at
    `https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/{layer}/query`.
  - For an address, the US Census Geocoder,
    `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress`
    with `benchmark=Public_AR_Current&format=json`, as documented at
    <https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html>.
- **Where the query shape and field names come from:**
  - the NFHL query URL and every field name are the ones recorded in the
    committed delivery
    `deliveries/flood-screen-d4f252e4-8a3b-40dd-981e-befb2de63da0.md`;
  - the `features` array of `attributes` objects is shown in
    `deliveries/site-diligence-12164581-c517-4e51-8d25-76b4f7f58ecd-rev1.md`
    (S6 to S11);
  - the geocoder's `addressMatches`, `matchedAddress` and `coordinates`
    (x is the longitude, y the latitude) are from the coordinator's
    captures on #175.
- **Arguments:** `lat` and `lon` in decimal degrees, or `address`. Not both.
- **Needs on the server:** outbound HTTPS to `hazards.fema.gov` and
  `geocoding.geo.census.gov`, and no key.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The answer first.** For an address, the matched address and
  coordinates as shown. Then, for each feature on each layer, the fields
  above, each marked "as shown". When a layer returns several features
  (a point on a panel boundary, for example), each is listed.
- **Then the evidence.** For each query: the exact query URL, the UTC
  retrieval time, the fields cut verbatim from the response, and the
  complete raw response (status line, headers, body). A `Set-Cookie`
  header is noted and not printed.

**Empty results are reports, with the raw body as the proof:**
- **No polygon:** a layer that returns an empty `features` array is
  reported as no polygon on that layer at that point. It is never shown as
  "not in a flood zone".
- **No address match:** an empty `addressMatches` array is reported as no
  match, and no flood query is run.
- **Several matches:** they are listed as shown, and no flood query is
  run. Give a more specific address.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API:
- a failed request or a closed connection;
- any status but 200;
- a redirect off the source host;
- a body without the documented shape, an ArcGIS error answer included.

A failure is never shown as an empty result.

## Running it

```sh
python3 tools/flood_check.py 27.9235 -82.4515
python3 tools/flood_check.py --address "1600 Pennsylvania Ave NW, Washington, DC"
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_flood_check.py' -v
```

The tests run offline, on the fixtures in `tools/tests/fixtures/flood/`
(provenance in `provenance.json`):
- **Census Geocoder:** the coordinator's two captures from #175, a match
  and a no match, verbatim with their posted hashes.
- **NFHL, interim:** bodies DERIVED from the Tampa delivery's excerpts
  (attribute lines verbatim, wrapper SYNTHETIC), and a SYNTHETIC empty
  answer. The coordinator's complete raw NFHL captures are owed on #175:
  `hazards.fema.gov` closed every connection from the coordinator's
  routes at 03:36 to 03:46 UTC on 2026-10-24.
- **Coordinator live run:** the coordinator's live smoke run is owed at
  review.
