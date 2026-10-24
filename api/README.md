# Recall check API: deployment

1. Needs Python 3.10+ and `curl` on PATH (the CPSC fetcher captures responses with curl). No packages, no keys.
2. Optional environment value, the only one read: `PAYOUT_WALLET_ADDRESS`, the EVM wallet that receives USDC per call. Unset is allowed; a malformed value refuses to start.
3. Local: `python3 api/recall_api.py` serves `http://127.0.0.1:8000/`; then `GET /recall?product=Instant+Pot` or `GET /recall?make=Hyundai&model=Elantra&year=2021`.
4. Any WSGI host: point it at `api.recall_api:app` from the repository root (for example `gunicorn api.recall_api:app`), and set `PAYOUT_WALLET_ADDRESS` in the host's environment, never in a file here.
5. `GET /` returns the service descriptor, including the payout wallet when set; every report carries it in the `X-Payout-Wallet` header.
6. The service answers from the live CPSC and NHTSA sources on every call and never caches; a failed fetch is a 502 with no report, so an empty result is always a real one.
7. Verify: `python3 -m unittest discover -s api -v`.

## Endpoints beyond `/recall` (issue #65)

Every merged fetcher in `tools/` is an endpoint with the same contract as `GET /recall`: the fetcher's own inputs as query parameters, the fetcher's rendered Markdown in the delivery format as the response (claim lines, exact query, UTC retrieval time, source link, complete raw response beneath the link), a 400 with no report for a bad query, and a 502 with no report when the fetch fails. `GET /` lists every endpoint under `endpoints` with its params and sources; `openapi.json` describes each one. The routing lives in `api/endpoints.py`; `api/recall_api.py` keeps `/recall` byte compatible.

| Path | Fetcher | Inputs |
| --- | --- | --- |
| `GET /carrier` | `tools/fmcsa_carrier.py` | `usdot` or `name`; optional `subject`, `source` (repeatable, with usdot), `limit`, `exclude` (with name) |
| `GET /litigation` | `tools/courtlistener_recap.py` | `party` (repeatable); optional `subject`, `filed_after`, `order_by`, `list`, `docket_details=1`, `exclude` |
| `GET /awards` | `tools/usaspending_awards.py` | `recipient` or `naics` (repeatable); optional `start`+`end`, `page`, `limit`, `exclude` |
| `GET /nonprofit` | `tools/propublica_nonprofits.py` | `name` or `ein` (repeatable); optional `subject`, `exclude` (with name) |
| `GET /formd` | `tools/edgar_formd.py` | `cik` or `issuer`; optional `max_filings`, `exclude` |
| `GET /pagespeed` | `tools/pagespeed_snapshot.py` | `url` (repeatable, up to 5); optional `subject`, `strategy`, `exclude` |
| `GET /domain` | `tools/domain_trust_check.py` | `domain` (a bare domain) |
| `GET /vin` | `tools/vin_decode.py` | `vin`; optional `model_year` |

Server side values, read from the environment at call time and never printed or written: `COURTLISTENER_TOKEN` (optional, lifts the anonymous rate limit), `PAGESPEED_API_KEY` (optional; without it the API answers 429 with quota 0, and that transcript is the report), and `EDGAR_CONTACT` (required for `/formd` by EDGAR fair access: the operator's "Name address" contact for the User-Agent; `/formd` answers 503 and fetches nothing while it is unset). The x402 payment gate in `api/payment_gate.py` wraps `GET /recall` only as of this version; the other endpoints are served without payment until the gate is extended, which is a separate task.

Verify: `python3 -m unittest discover -s api -v` runs the recall, payment gate and endpoint suites.
