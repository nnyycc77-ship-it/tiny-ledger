# Listing kit: the pay per call recall API

Ready to paste listing material for `GET /recall`, one section per registry
surface. This file is material only. It creates no account, submits no
form, and contacts no one. Each listing is filed by the owner, after the
API is publicly hosted.

**Sources.** Every fact here comes from one of these:

- the repo: `api/README.md`, `api/recall_api.py`, `api/payment_gate.py`,
  `api/openapi.json`, `mcpize.yaml`, `AGENT-BRIEF.md`;
- the coordinator's verified lead records on issue
  [#14](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/14) (Circle
  Agent Marketplace) and issue
  [#15](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/15) (CDP x402
  Bazaar).

Each section names its sources. Anything those sources do not record is
marked **to confirm at submission**. No registry was fetched live for this
file.

## Facts shared by every listing

Source: `api/payment_gate.py` (module docstring and `payment_requirements`),
`api/openapi.json` (`info`, `/recall`, `PaymentRequirements`),
`api/README.md`.

| Fact | Value | Source |
| --- | --- | --- |
| Paid endpoint | `GET /recall`. Only this endpoint is behind the payment gate; the six other endpoints are served without payment until the gate is extended. | `api/README.md`, `api/openapi.json` `info.description` |
| Query forms | a product (`product`, optional `exact_name` and repeatable `near`), or a vehicle (`make` + `model` + `year`, optional repeatable `exclude`) | `api/openapi.json` `/recall` parameters |
| Response | `text/markdown`: the report in the delivery format | `payment_gate.py` `mimeType`; `api/openapi.json` `/recall` 200 |
| Unpaid call | HTTP 402 with the x402 v1 body: `x402Version` 1, `error`, `accepts`, and `extensions.bazaar` | `payment_gate.py` `payment_required_body` |
| Scheme | `exact` | `payment_gate.py` |
| Network | `base` (Base mainnet) | `payment_gate.py` `DEFAULT_NETWORK` |
| Asset | USDC on Base, `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `payment_gate.py` `DEFAULT_ASSET` |
| Price per call | 0.05 USDC (`maxAmountRequired` `50000`, 6 decimals) | `payment_gate.py` `DEFAULT_PRICE`; `api/openapi.json` |
| payTo | the value of `PAYOUT_WALLET_ADDRESS` on the host. The gate refuses to run without it. | `payment_gate.py`; `api/recall_api.py` `payout_wallet` |
| Payout wallet value | **to confirm at submission.** The repo records no value for the API host; it is set in the host's environment, never in a file. The one payout address recorded in the repo is the MCPize recipient, at `pricing.recipient` in `mcpize.yaml`. Whether the API host uses the same address is not recorded. | `api/README.md` step 4; `mcpize.yaml` `pricing.recipient` |
| Facilitator | PayAI by default (`https://facilitator.payai.network`), changeable with `FACILITATOR_URL` | `payment_gate.py` `DEFAULT_FACILITATOR` |
| Settle receipt | returned in the `X-PAYMENT-RESPONSE` header, base64 JSON | `payment_gate.py`; `api/openapi.json` |
| Failed source fetch | HTTP 502 with no report, never an empty result | `api/README.md` step 6; `api/openapi.json` `/recall` 502 |
| Public host URL | **to confirm at submission.** No public deployment address is recorded in the repo. `api/openapi.json` declares `servers` as `[{"url": "/"}]`. | `api/openapi.json` `servers` |

## 1. CDP x402 Bazaar

Source: issue #15 (coordinator verification), `api/payment_gate.py`.

**How the listing happens** (from #15): there is no form. The Bazaar indexes
an endpoint after the CDP facilitator settles a payment for an endpoint that
advertises Bazaar metadata. Requirements recorded on #15:

- a CDP account and API key (an owner step);
- Bazaar discovery metadata declared on the endpoint, with a description of
  500 characters or fewer;
- a public HTTPS host;
- one settled call through the CDP facilitator.

Per #15, a resource with no settlement for 30 days is removed from the
catalog. `agentic.market` is the storefront for the same index.

**Facilitator mismatch, to resolve before listing.** The gate settles through
PayAI by default. #15 records that the Bazaar indexes on settlement through
the CDP facilitator. So `FACILITATOR_URL` on the host must point at the CDP
facilitator for this listing. The CDP facilitator URL is not recorded in the
repo or on #15: **to confirm at submission.** #15 also records the CDP fee
terms: the first 1,000 facilitator transactions each month are free, then
0.001 dollars each, with no listing fee.

### Listing description

The Bazaar reads the description from the endpoint's own payment
requirements, so the text that will show is the gate's `DESCRIPTION`. Paste
or confirm exactly this:

```
Sourced recall check from public United States recall records (CPSC products, NHTSA vehicles)
```

Length: 93 characters, within the 500 character limit.

**Optional fuller draft.** This is ready to paste, but it shows only after a
separate code change that sets `DESCRIPTION` in `api/payment_gate.py` to this
text. That change is not part of this docs task.

```
Sourced US recall check from public records: CPSC SaferProducts for consumer products, NHTSA for vehicles (make, model, year). Each call fetches the live source and returns Markdown with the exact query, the UTC retrieval time, the source link, and the complete raw response beneath it. An empty result is shown by the full raw response; a failed fetch returns 502 and no report. Near matches can be checked and excluded with a reason. 0.05 USDC per call on Base.
```

Length: 463 characters, within the 500 character limit.

### Endpoint facts the listing shows

These are the values the 402 `accepts` entry carries (`payment_requirements`
in `api/payment_gate.py`):

| Field | Value |
| --- | --- |
| `resource` | the full request URL, query string included: `https://<public host>/recall?product=...` or `https://<public host>/recall?make=...&model=...&year=...` (the host is to confirm at submission) |
| `scheme` | `exact` |
| `network` | `base` |
| `asset` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (USDC on Base) |
| `maxAmountRequired` | `50000` (0.05 USDC) |
| `payTo` | the host's `PAYOUT_WALLET_ADDRESS` (value to confirm at submission) |
| `mimeType` | `text/markdown` |
| `maxTimeoutSeconds` | `60` |
| Bazaar `extensions.bazaar.info.input` | `GET`, example query params `product=Instant Pot`, `make=Hyundai`, `model=Elantra`, `year=2021` |

## 2. Circle Agent Marketplace intake

Source: issue #14 (coordinator verification), `api/openapi.json`,
`api/payment_gate.py`, `api/README.md`.

**What the intake needs** (from #14):

- a service that answers 402 Payment Required when unpaid and serves the
  resource when paid. The gate does this for `GET /recall`.
- a published OpenAPI spec;
- a confirmed payout wallet address, which is sanctions screened during
  review.

#14 also records that listings are reviewed and approved manually, that
payment goes straight to the seller wallet in USDC, and that no listing fee
is stated.

### Service summary

Paste as the summary paragraph:

> Sourced recall check from public United States recall records. GET /recall
> takes a product name, checked against the CPSC SaferProducts recall
> database, or a vehicle make, model and year, checked against NHTSA
> recalls. It fetches the live source on every call and returns the report
> as Markdown: the claim lines, the exact query, the UTC retrieval time, the
> source link, and the complete raw source response directly beneath the
> link. A failed source fetch is a 502 with no report, never an empty result.
> Paid per call in USDC on Base under the x402 exact scheme.

### Intake fields

| Field | Value |
| --- | --- |
| Public sources | CPSC SaferProducts (products) and NHTSA recalls (vehicles) |
| Price | 0.05 USDC per call (`maxAmountRequired` `50000`), x402 `exact` scheme, Base mainnet |
| Payout wallet | the host's `PAYOUT_WALLET_ADDRESS`. **To confirm at submission**; see "Payout wallet value" above. |
| OpenAPI spec | [`api/openapi.json`](../api/openapi.json): OpenAPI 3.0.3, title "Hojo Research Agent recall check", version 1.1.0. Its public URL on the host is to confirm at submission. |
| Service URL | `https://<public host>/recall` (the host is to confirm at submission) |

## 3. agent402.tools

Source: the task text of issue #69. The repo and issues #14 and #15 record
nothing about agent402.tools, so every detail below beyond that task text is
marked to confirm.

**Origin registration facts:**

- What gets registered: the API's public origin, `https://<public host>`.
  The host is to confirm at submission.
- What the probe checks (as the issue states it): that the origin answers a
  402 with a valid `accepts` entry. The gate's unpaid `GET /recall` answer
  is that 402 (see "Endpoint facts the listing shows" above). Whether the
  probe calls `/recall` or another path is to confirm at submission. The
  probe gets a 402 only on `/recall`: `GET /` and the six other endpoints
  answer without payment.
- How registration is made: **to confirm at submission.**

**Note for the listing:** the index caps unproven sellers until they build
settlement history. A new listing of this endpoint starts in that state. The
cap figure itself is **to confirm at submission**.
