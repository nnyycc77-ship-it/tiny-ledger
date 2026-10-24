# `domain_trust_check`: domain trust check

A tool factory wave 1 tool (issue #159, parent #158). The fetcher is
[`tools/domain_trust_check.py`](../../tools/domain_trust_check.py), and it is served as
`GET /domain` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** The DNS mail and web posture of one domain, as the
  public sources show it:
  - its A and MX records;
  - its SPF record (the TXT record that begins `v=spf1`) and that
    record's ending policy;
  - its DMARC record (the TXT record at `_dmarc.<domain>` that begins
    `v=DMARC1`) and its `p=` tag;
  - the outcome of requesting the site over HTTPS, with redirects not
    followed, up to 5 hops, each hop its own source.

  Each is shown as the response gives it.
- **Sources:** DNS through the Cloudflare DNS over HTTPS JSON API,
  `https://cloudflare-dns.com/dns-query` (four keyless GETs with
  `accept: application/dns-json`), and the site itself,
  `https://<domain>/`.
- **Arguments:** `domain`, a bare domain. The tool's own usage example is
  the reserved example domain `example.com`.
- **Needs on the server:** outbound HTTPS to `cloudflare-dns.com` and to
  the domain checked. No key, no environment value.
- **Empty results are proven, never asserted:** a name that does not
  exist (the API's `Status` field as shown), or an answer with no record
  of the asked type, is printed with its complete raw response beneath
  it.
- **Fails closed:** a DNS answer that is not HTTP 200, a body that is not
  the API's JSON object, or a transport failure on the DNS leg prints
  nothing and exits 2 (502 on the API). A connection to the site that
  fails is reported with the error text it raised, since that failure is
  the observation.
- **What it is not:** a security audit or a mail delivery assessment. No
  certificate check is made. The SPF and DMARC readings are the records'
  own text as shown, not a deliverability verdict.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price
  set by the owner ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this docs page sets or changes a price; pricing stays in the
  owner redeploy step.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_domain_trust_check.py' -v
```

The tests run offline on the recorded responses in
[`tools/tests/fixtures/domain-trust/`](../../tools/tests/fixtures/domain-trust/),
with their provenance.
