# `earthquake_check`: USGS earthquake catalog check

A tool factory wave 3 tool (issue #317, parent #305).
- **Code:** the fetcher is
  [`tools/earthquake_check.py`](../../tools/earthquake_check.py). The pay
  per call API serves it as `GET /earthquake?lat=...&lon=...&radius_km=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not on the MCP server yet.** Registering it is a separate step for the
  coordinator, the same way as waves 1 and 2; this PR changes nothing in
  `mcp_server/`. Going live also waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** how many events does the USGS earthquake catalog
  list inside a circle around one point in the past 10 years, and which
  are the largest? For each of the 10 largest it gives the magnitude, the
  magnitude type, the time, the place, the event type and the event id, as
  published.
- **Source:** the USGS FDSN event web service,
  `https://earthquake.usgs.gov/fdsnws/event/1/`, two calls with the same
  point, radius and window:
  - `count?format=geojson&...`, which answers the total;
  - `query?format=geojson&...&orderby=magnitude&limit=10`, which answers
    the largest events as a GeoJSON FeatureCollection.
- **Keyless.** The tool reads no key and sends none.
- **The window** is the 10 years up to the moment of the call, computed
  once and sent identically on both calls as `starttime` and `endtime`.
  The report prints it.
- **No filter.** No event type or magnitude filter is sent, so the count
  covers every event the catalog lists in the circle; each listed event's
  type (`properties.type`) is shown as returned.
- **Times** are the source's epoch milliseconds (`properties.time`),
  printed raw first, with the UTC time after them.
- **Arguments:**
  - `lat` and `lon`, decimal degrees (-90 to 90 and -180 to 180);
  - `radius_km`, 1 to 500 kilometres. The 500 km upper bound is this
    tool's choice, recorded on issue #317, not a documented source limit.
- **Needs on the server:** outbound HTTPS to `earthquake.usgs.gov`, and no
  key.
- **What it is not:** a seismic hazard assessment. No event listed is the
  catalog's answer for that circle and window only, never a statement that
  no earthquake can occur there.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

1. **The answer.** The point, the radius and the window, then:
   - the count, with the count call's link and the `"count"` member cut
     verbatim beneath it;
   - for each of the largest events, in the order the source returned
     them: the fields above, the query call's link, and the fields cut
     verbatim from the response beneath it.
2. **The evidence.** For each call: the exact query URL, the UTC
   retrieval time, and the complete raw response (status line, headers
   and body).

**No event listed:** the count call answered 0 and the query call an empty
features array. The report says so and prints both complete raw responses,
which are the proof.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API. The error names the source and the reason. The answer is unknown,
never "no earthquakes". They are:
- a failed or timed out request;
- any status but 200 (the source answers bad input with HTTP 400 and a
  plain text body, whose reason line the error repeats);
- a redirect off `earthquake.usgs.gov`;
- a body without the documented shape: no whole number `count`, not a
  `FeatureCollection`, no `features` array, an event without one of the
  fields above, or more events than the limit sent;
- two answers that disagree: a count of 0 with events listed, or a count
  above 0 with none.

## Running it

```sh
python3 tools/earthquake_check.py 34.0522 -118.2437 25
python3 tools/earthquake_check.py 28.5383 -81.3792 10
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_earthquake_check.py' -v
```

The tests run offline on `tools/tests/fixtures/earthquake/`. Every body
there is a REAL CAPTURE, verbatim from the coordinator's captures on
issue #317, with its URL, status line, headers, size and SHA-256 in
`provenance.json`:
- the count and query answers for Los Angeles (34.0522, -118.2437, 25 km:
  1692 events, the 10 largest listed);
- the count and query answers for Orlando (28.5383, -81.3792, 10 km: a
  count of 0 and an empty features array);
- the HTTP 400 plain text answer to a latitude of 200.

The tests fix the call's moment at the captures' window end,
2026-10-24T00:00:00 UTC. The coordinator's live smoke run is owed at
review.
