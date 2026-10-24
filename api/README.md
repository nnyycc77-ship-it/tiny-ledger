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
| `GET /app` | `tools/app_lookup_check.py` | `name`; optional `country` (two letters, default `us`), `limit` (1 to 200, default 10) |
| `GET /vin` | `tools/vin_decode.py` | `vin`; optional `model_year` |
| `GET /fx` | `tools/exchange_rate_check.py` | `base`, `target`; optional `amount`, `date` |
| `GET /meta` | `tools/meta_tag_check.py` | `url` (a page URL, http or https) |
| `GET /flood` | `tools/flood_check.py` | `lat` and `lon`, or `address` (a US street address) |
| `GET /safety` | `tools/safety_file.py` | `make`, `model`, `year` |
| `GET /fda` | `tools/fda_recall_check.py` | `name`; optional `field` (product or firm), `category` (food, device or both), `limit` (1 to 100, default 10) |
| `GET /epa` | `tools/epa_screen.py` | `name`, `state`; optional `city`, `registry_id` |
| `GET /oig` | `tools/oig_screen.py` | `name` (a person or entity name) |
| `GET /trials` | `tools/clinical_trial_check.py` | `term`; optional `limit` (1 to 100, default 10) |
| `GET /links` | `tools/broken_link_check.py` | `url` (the page URL) |
| `GET /insider` | `tools/insider_check.py` | `cik` or `issuer`; optional `max_filings` (1 to 20, default 5); needs `EDGAR_CONTACT` |

Server side values, read from the environment at call time and never printed or written: `COURTLISTENER_TOKEN` (optional, lifts the anonymous rate limit), `PAGESPEED_API_KEY` (optional; without it the API answers 429 with quota 0, and that transcript is the report), and `EDGAR_CONTACT` (required for `/formd` and `/insider` by EDGAR fair access: the operator's "Name address" contact for the User-Agent; each answers 503 and fetches nothing while it is unset). The x402 payment gate in `api/payment_gate.py` wraps `GET /recall` only as of this version; the other endpoints are served without payment until the gate is extended, which is a separate task.

Verify: `python3 -m unittest discover -s api -v` runs the recall, payment gate and endpoint suites.
