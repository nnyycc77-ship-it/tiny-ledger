# Domain trust check

`tools/domain_trust_check.py`, issue
[#159](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/159) (tool
factory wave 1, parent #158).

## What it answers

Give it one domain. It answers five questions from what public sources
return at that moment, in the delivery format from `AGENT-BRIEF.md`:
every claim cites its source, and every response is printed in full
beneath its request URL.

1. What A records does the domain have?
2. What MX records (mail servers) does it have?
3. Is there an SPF record, and what is its ending policy? The ending
   policy is the qualifier on the final `all` mechanism: `-all`, `~all`,
   `?all`, `+all`, or a bare `all`. A record with no `all` but a
   `redirect=` modifier is reported as ending in that redirect. A record
   with neither is reported as such. If more than one record begins
   `v=spf1`, the tool reports that and picks none.
4. Is there a DMARC record at `_dmarc.<domain>`, and what is its `p=`
   policy as shown?
5. Does the site answer HTTPS at `https://<domain>/`, and where does it
   redirect? Redirects are not followed automatically. Each hop is
   requested in turn, up to 5, and each hop is its own source with its
   own transcript.

It is an observation of one moment. It is not a security audit or a
mail delivery assessment, and v1 does not check certificates.

## Sources

- **DNS: the Cloudflare DNS over HTTPS JSON API,** `https://cloudflare-dns.com/dns-query`.
  - The request is a GET with `name` and `type`, plus the header
    `accept: application/dns-json`. That is the form the API
    documentation gives; the coordinator captured the page on
    2026-10-24 ([#159 comment 6378417977](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/159#issuecomment-6378417977)).
  - That documentation says `Status` is the DNS response code, with the
    codes defined in the IANA DNS parameters registry, and that `Answer`
    holds `name`, `type`, `TTL` and `data`.
  - No key and no account are needed.
- **The site itself:** a GET of `https://<domain>/` with stdlib urllib,
  redirects not followed.

## Run it

```sh
python3 tools/domain_trust_check.py example.com   # the reserved example domain, as the example input
```

The same check is served by the API as `GET /domain?domain=<domain>`
(`api/endpoints.py`). Like every wave 1 tool, it will join the MCP server
in the one shared surface PR at the end of the wave, per the ruling on
#158.

## Price

On the MCP shelf it is priced at **0.25 USDC per call**, the shelf price
the owner set on issue #147
([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
That happens once the tool passes review and the owner's redeploy step
for the whole wave puts the shelf live. Nothing in this repo changes a
price.

## Empty results and failures

**Empty results are proven by the transcript, never asserted.**
- **A name that does not exist.** The answer's `Status` is shown, for
  example 3 for `does-not-exist.invalid`.
- **No record of the asked type.** The answer is `Status 0` with no
  record of that type, for example no DMARC record at
  `_dmarc.neverssl.com`.

Both are reported as empty results, with the full response printed
beneath.

**Fail closed.** The run stops, prints nothing on stdout and exits 2 for
any of these:
- a DNS answer that is not HTTP 200;
- a body that is not the API's JSON object (an integer `Status`, and an
  `Answer` array of records with `name`, `type` and `data`);
- a transport failure on the DNS leg.

On the site leg, a connection that fails is itself the observation. The
error text is reported for that hop, and no transcript is printed,
because no response exists.

## Example

This is the report for example.com, replayed from the coordinator's live
captures of 2026-10-24
([#159 comments 6378418247 and 6378418840](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/159#issuecomment-6378418247)).
The Sources section, with every transcript, is left out here. The
coordinator's live smoke run of the finished tool is owed at review.

The example domain, A records:
```text
### A records

QUERY: example.com A (retrieved 2026-10-24T01:51:42Z; source S1). HTTP status as returned: 200 OK. DNS Status as shown: 0.

- A record as shown: `104.20.23.154` (TTL 39).
- A record as shown: `172.66.147.243` (TTL 39).
```

The example domain, MX records:
```text
### MX records

QUERY: example.com MX (retrieved 2026-10-24T01:51:42Z; source S2). HTTP status as returned: 200 OK. DNS Status as shown: 0.

- MX record as shown: `0 .` (TTL 285).
```

The example domain, TXT records (SPF):
```text
### TXT records (SPF)

QUERY: example.com TXT (retrieved 2026-10-24T01:51:43Z; source S3). HTTP status as returned: 200 OK. DNS Status as shown: 0.

- TXT records in the answer: 2, of which 1 begin v=spf1.
- SPF record as shown (data `"v=spf1 -all"`): `v=spf1 -all`
- SPF ending policy: `-all`, the final all mechanism of the record (source S3).
```

The example domain, DMARC record:
```text
### DMARC record

QUERY: _dmarc.example.com TXT (retrieved 2026-10-24T01:51:44Z; source S4). HTTP status as returned: 200 OK. DNS Status as shown: 0.

- TXT records in the answer: 1, of which 1 begin v=DMARC1.
- DMARC record as shown (data `"v=DMARC1;p=reject;sp=reject;adkim=s;aspf=s"`): `v=DMARC1;p=reject;sp=reject;adkim=s;aspf=s`
- DMARC policy (p= tag as shown): `reject` (source S4).
```

The example domain, HTTPS:
```text
### HTTPS

- Hop 1: GET https://example.com/ answered 200 OK (retrieved 2026-10-24T01:51:49Z; source S5).
- HTTPS: the final hop answered 200 OK at https://example.com/.
```

## Tests

`tools/tests/test_domain_trust_check.py` (20 tests) runs on the 11 real
fixture captures in `tools/tests/fixtures/domain-trust/`, whose provenance is in
that folder's `provenance.json`. The tests cover:
- the example.com report end to end;
- the second domains: iana.org, whose SPF ends in `redirect=` with
  DMARC `p=none`, and wikipedia.org, whose SPF ends in `~all`;
- both empty results;
- the google.com redirect and the 5-hop limit;
- failing closed.

`api/test_endpoints.py` covers `GET /domain`.

Two capture bodies needed care, and the provenance file records both.
The posted text of the example domain's page (example.com) dropped its final newline, and the
posted text of google.com's 301 body dropped its CR bytes. In each case
the fixture holds the only byte arrangement that matches the
coordinator's recorded body SHA-256 and byte count.
