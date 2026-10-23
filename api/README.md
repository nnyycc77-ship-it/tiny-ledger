# Recall check API: deployment

1. Needs Python 3.10+ and `curl` on PATH (the CPSC fetcher captures responses with curl). No packages, no keys.
2. Optional environment value, the only one read: `PAYOUT_WALLET_ADDRESS`, the EVM wallet that receives USDC per call. Unset is allowed; a malformed value refuses to start.
3. Local: `python3 api/recall_api.py` serves `http://127.0.0.1:8000/`; then `GET /recall?product=Instant+Pot` or `GET /recall?make=Hyundai&model=Elantra&year=2021`.
4. Any WSGI host: point it at `api.recall_api:app` from the repository root (for example `gunicorn api.recall_api:app`), and set `PAYOUT_WALLET_ADDRESS` in the host's environment, never in a file here.
5. `GET /` returns the service descriptor, including the payout wallet when set; every report carries it in the `X-Payout-Wallet` header.
6. The service answers from the live CPSC and NHTSA sources on every call and never caches; a failed fetch is a 502 with no report, so an empty result is always a real one.
7. Verify: `python3 -m unittest discover -s api -v`.
