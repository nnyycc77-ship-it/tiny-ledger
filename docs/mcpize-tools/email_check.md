# `email_check`: email check (MX, SPF, DMARC over DNS over HTTPS)

A tool factory wave 3 tool (issue #338, parent #305).
- **Code:** the fetcher is
  [`tools/email_check.py`](../../tools/email_check.py). The pay per call
  API serves it as `GET /email?address=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not registered on the MCP server.** Registration is the shared wave
  end surface step, and going live waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** for one email address, whether the address is
  well formed, whether its domain has MX records, and the domain's SPF
  and DMARC policies, each as the source returns it.
- **Source:** Cloudflare DNS over HTTPS,
  `GET https://cloudflare-dns.com/dns-query` with
  `Accept: application/dns-json`. Three queries: MX on the domain, TXT
  on the domain, and TXT on `_dmarc.{domain}`.
  - **Keyless.** No key or account is used. The wave 3 source check
    (issue #305 research) confirmed this source for exactly this use,
    repeating the wave 1 domain trust finding.
- **Arguments:** `address`, one email address.
- **Needs on the server:** outbound HTTPS to `cloudflare-dns.com`, and
  no key.
- **What it is not:** a delivery test or a mailbox check. Well formed is
  a statement about the address's shape only, and no mail server is ever
  contacted. "The domain has MX records" is not a promise that mail to
  it will be delivered or read.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## How the readings work

- **Well formed** is decided locally: exactly one @, a local part of 1
  to 64 allowed characters with no leading, trailing or doubled dot,
  and a domain of at least two valid DNS labels. A malformed address is
  refused before any query is sent.
- **NXDOMAIN is not NODATA.** DNS Status 3 means the name does not
  exist; Status 0 with no Answer section means the name exists and
  publishes no record of that type. The report keeps them apart.
- **A null MX is read as written.** A single MX answer of `0 .` is a
  null MX (RFC 7505): the domain formally declares it accepts no email
  at all. `example.com`, the reserved example domain, publishes exactly
  that, and the report says so
  rather than counting it as a mail server.
- **SPF and DMARC are selected by prefix.** Among the TXT records, the
  SPF record is the one beginning `v=spf1` and the DMARC record the one
  beginning `v=DMARC1`. A TXT record that arrives split into quoted
  chunks is joined with nothing between them before selection, as DNS
  joins it.

## What a report contains

- The observation line, the well formed verdict with what it does and
  does not claim, and the readings note.
- The MX reading (the records as shown, the null MX reading, NODATA, or
  NXDOMAIN), the SPF record as shown or its stated absence, and the
  DMARC record as shown or its stated absence.
- One source section per query: the exact query, the UTC retrieval
  time, the source link, and the complete raw response beneath it.

**Failures:** any query that fails, times out, answers a non 200
status, or answers a body that is not the documented DNS JSON shape
gives no report, with exit 2 on the CLI and 502 on the API. A timeout is
unknown, never a negative: the source check measured this endpoint
taking far longer than a short client timeout in this environment, so
the tool allows 60 seconds per query.

## Running it

```sh
python3 tools/email_check.py someone@gmail.com
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_email_check.py' -v
```

The tests run offline on three live capture sets (fixtures in
`tools/tests/fixtures/email-check/` with their hashes in
`provenance.json`): gmail.com with all records present, example.com
with its null MX, and a name under the reserved `.invalid` TLD answered
NXDOMAIN on all three queries. The live smoke run for this build is
recorded on the PR for issue #338.
