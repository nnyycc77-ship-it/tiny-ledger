# `ofac_sanctions_check`: OFAC SDN list name check

A tool factory wave 1 tool (issue #160, parent #158). The MCP tool name is
`ofac_sanctions_check`; the fetcher it runs is
[`tools/ofac_sdn_check.py`](../../tools/ofac_sdn_check.py), served as
`GET /ofac` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

**The full page is [`docs/ofac-sdn-check.md`](../ofac-sdn-check.md),**
written before this folder existed and kept there. That page covers what
the tool answers, its sources, the matching rule, what a report contains,
and the verification steps. In short:

- **What it answers:** is this person or company name on the US Treasury
  OFAC Specially Designated Nationals (SDN) list, under a primary name or
  an alias? If so, which entries match, and what do those entries say?
- **Sources:** `SDN.CSV`
  (`https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV`)
  and `ALT.CSV`
  (`https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ALT.CSV`),
  both public and keyless, read live on every call.
- **Arguments:** `name`, a person or company name with at least 3 letters
  or digits.
- **Needs on the server:** outbound HTTPS to
  `sanctionslistservice.ofac.treas.gov`, and to the signed storage URL it
  redirects to. No key, no environment value.
- **What it is not:** a name match is not a determination that a party is
  the listed person or entity, and no match is not a sanctions clearance.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price
  set by the owner ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this docs page sets or changes a price; pricing stays in the
  owner redeploy step.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_ofac_sdn_check.py' -v
```
