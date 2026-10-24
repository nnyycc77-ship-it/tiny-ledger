# `weather_alert_check`: US National Weather Service active alerts

A tool factory wave 3 tool (issue #318).

- **Code:** the fetcher is
  [`tools/weather_alert_check.py`](../../tools/weather_alert_check.py).
  The pay per call API serves it as `GET /weather?lat=...&lon=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not yet registered on the MCP server.** This PR adds the fetcher,
  the API dispatcher, this page, and the offline tests only. MCP
  surface registration is a separate later shared step, and going live
  waits on the owner redeploy after that.

## The tool at a glance

- **What it answers:** for one point (latitude and longitude), which
  weather alerts the US National Weather Service lists as active at
  that point right now: for each alert, the event name (`event`), the
  severity (`severity`), and the expiry (`expires`, as shown; when the
  service shows null there, the alert's `ends` is shown instead).
- **Observation only:** a report records what the service listed at
  the retrieval time. No active alerts at that time is not a statement
  that conditions are safe or that no alert will be issued. Every
  report says so.
- **Source, keyless:** the National Weather Service API's active
  alerts endpoint,
  `GET https://api.weather.gov/alerts/active?point={lat},{lon}`,
  which answers a GeoJSON FeatureCollection. No key exists for this
  API and none is sent; the tool sends an identifying User-Agent, as
  the API's guidance asks. Coverage is the United States and its
  territories: an out of coverage point is answered with an error
  status and a problem document (400 observed live on 2026-10-24 for
  a London point), which the tool reports as a failed fetch, never
  as no alerts.
- **Where the response shape comes from:** live captures made for
  this issue on 2026-10-24, committed under
  `tools/tests/fixtures/weather-alerts/` with their provenance: the
  collection carries `features`, `title` and `updated`; each feature
  carries a `properties` object with `event`, `severity`, `expires`
  and `ends`.
- **Arguments:** `lat` and `lon` in decimal degrees.
- **Needs on the server:** outbound HTTPS to `api.weather.gov`, and
  no key.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The answer first.** The point, the collection `title` and
  `updated` as shown, then one block per alert with its event name,
  severity, and expiry, each marked "as shown". When the service
  returns several alerts for a point, each is listed.
- **Then the evidence.** The exact query URL, the UTC retrieval time,
  the fields cut verbatim from the response, and the complete raw
  response (status line, headers, body). A `Set-Cookie` header, when
  one is returned, is counted in a note but not printed.

## How an empty or failed lookup is reported

- **Empty:** a 200 answer with an empty `features` array is a report
  of no active alerts at that point at the retrieval time, and the
  complete raw response printed in the evidence is the proof.
- **Failed:** a failed or timed out request, any status but 200 (an
  out of coverage error status included), a redirect off
  `api.weather.gov`, or
  a body without the documented shape stops the run with exit 2 and
  no report. A failed fetch is reported as unknown, never as a
  negative claim.
