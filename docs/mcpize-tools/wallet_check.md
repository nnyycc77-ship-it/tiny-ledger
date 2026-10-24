# `wallet_check`: Bitcoin address facts

A tool factory wave 3 tool (issue #337).

- **Code:** the fetcher is
  [`tools/wallet_check.py`](../../tools/wallet_check.py). The pay per
  call API serves it as `GET /wallet?address=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not yet registered on the MCP server.** This PR adds the fetcher,
  the API dispatcher, this page, and the offline tests only. MCP
  surface registration is a separate later shared step, and going
  live waits on the owner redeploy after that.

## The tool at a glance

- **What it answers:** for one Bitcoin address, the public facts the
  mempool.space explorer API holds for it: the transaction count,
  the total received and the total sent in satoshis, and the current
  balance in satoshis. Facts only: the report contains no assessment
  and no advice.
- **Source, keyless:** the mempool.space public API,
  `GET https://mempool.space/api/address/{address}`. It is a third
  party open source explorer API (not a protocol service), so the
  figures are that explorer's view of the chain and the mempool. No
  key exists for this API and none is sent.
- **How the figures are read, stated rather than assumed:**
  - the answer's figures come from `chain_stats` (confirmed): total
    received is `funded_txo_sum`, total sent is `spent_txo_sum`, and
    the current balance is `funded_txo_sum` minus `spent_txo_sum`,
    computed from those two shown figures (the API returns no
    balance field);
  - `mempool_stats` (unconfirmed) is printed as its own block, as
    shown. Confirmed and unconfirmed figures are never added
    together.
- **Where the response shape comes from:** the wave 3 source check
  (issue #305 research) plus live captures made for this issue on
  2026-10-24, committed under `tools/tests/fixtures/wallet/` with
  their provenance: an address document with `chain_stats` and
  `mempool_stats`, each block carrying `funded_txo_count`,
  `funded_txo_sum`, `spent_txo_count`, `spent_txo_sum` and
  `tx_count`, all amounts in satoshis.
- **Arguments:** one `address`: a legacy base58 address starting 1
  or 3, or a bech32 address starting bc1. The local check is a shape
  check only; the source stays the authority on validity and refuses
  a bad checksum.
- **Needs on the server:** outbound HTTPS to `mempool.space`, and no
  key.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The answer first.** The address as shown, then the confirmed
  block (transaction count, total received, total sent, funded and
  spent output counts, current balance), then the unconfirmed block
  in the same shape with its net labelled as unconfirmed.
- **Then the evidence.** The exact query URL, the UTC retrieval
  time, the fields cut verbatim from the response, and the complete
  raw response (status line, headers, body). A `Set-Cookie` header,
  when one is returned, is counted in a note but not printed.

## How an empty or failed lookup is reported

- **Empty:** an address with no activity answers a document whose
  figures are all zero. The report states that every figure in both
  stats blocks is zero, as shown, and the complete raw response
  printed in the evidence is the proof.
- **Failed:** a failed or timed out request, any status but 200
  (the source's HTTP 400 refusal of an address it judges invalid
  included; its body is the plain text "Invalid Bitcoin address"),
  a redirect off `mempool.space`, or a body without the documented
  shape stops the run with exit 2 and no report. A failed fetch is
  reported as unknown, never as figures.
