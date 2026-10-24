# OFAC SDN list name check

Issue #160 (tool factory wave 1, parent #158). The tool is
`tools/ofac_sdn_check.py`, and the API route is `GET /ofac?name=...`.

## What it answers

Is this person or company name on the US Treasury OFAC Specially
Designated Nationals (SDN) list, under a primary name or an alias? If so,
which entries match, and what do those entries say?

**Observation only.** A name match is not a determination that a party
is the listed person or entity. No match is not a sanctions clearance.

## Source

Both files are public, need no key, and are read live on every call:

| File | URL | What it holds |
| --- | --- | --- |
| `SDN.CSV` | <https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV> | primary names, one line per entry |
| `ALT.CSV` | <https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ALT.CSV> | aliases, linked to entries by ENT_NUM |

**How the sources were confirmed.** The URLs, the file shape and OFAC's
format tutorial were captured live by the coordinator on 2026-10-24,
under option B on issue #160 (comments 6378275074 and 6378275367). The
build environment cannot reach OFAC hosts.

**The redirect.** OFAC answers with a redirect to a signed storage URL
that carries a short-lived token. The report never prints that URL.

**Which columns are named.** OFAC's tutorial, "Tutorial on the Use of
List-related Legacy Flat Files", documents that the first column of
`SDN.CSV` is ENT_NUM, the primary key. It links to the ENT_NUM column of
`ALT.CSV`. From the captured lines' own shape:
- `SDN.CSV`: the second column carries the name, and the third the type
  where present ("individual", "vessel", or `-0-`).
- `ALT.CSV`: the fourth column carries the alias name.

OFAC's full column specification is a separate document that has not
been captured. So the report names no other column, and prints each
matching entry's lines whole instead.

## What a report contains

- **The matching rule.** Names are compared after folding case, removing
  accents where Unicode decomposition splits them off (é becomes e; a
  letter with no such decomposition is still replaced), and replacing
  every non-letter, non-digit character with a space. An exact
  match is the whole normalised name equal; a contains match is the name
  appearing as whole words. Primary names and aliases are both checked.
  No fuzzy or phonetic score is computed or claimed.
- **Word order.** Word order is kept as typed. The list writes individuals
  surname first ("ABBAS, Abu"), so search individuals that way, or by a
  single distinctive word.
- **Each file read.** The exact URL, the UTC retrieval time, the response
  headers listed in the tool, and the file's byte size, SHA-256, line
  count and entry count as read.
- **Each match.** The entry's ENT_NUM, name and type as shown; whether
  the match was exact or contains, and on the primary name or an alias;
  its SDN.CSV line verbatim with its line number; and every ALT.CSV line
  for that ENT_NUM, verbatim.
- **Long results.** Up to 50 entries are listed, in file order. Any more
  are counted, not listed.
- **No match.** The report states it under the rule, with both files'
  SHA-256 and their entry and alias counts, so the check can be repeated
  against the same files.
- **Fails closed.** A failed request, a non-200 answer, or a file not in
  the captured shape gives exit 2 (502 on the API) and no report. A
  failure is never shown as no match.

**Running it:**

```sh
python3 tools/ofac_sdn_check.py "Banco Nacional"
python3 tools/ofac_sdn_check.py "ABBAS, Abu"
```

The name needs at least 3 letters or digits.

## Price

**0.25 USDC per call** on the MCP shelf: x402, Base mainnet, USDC. This is
the owner's ruling on issue #147 (comment 6377953191), which sets every
shelf tool at 0.25 USDC.

**Registered on the MCP server, not live yet.** The server on main lists
it as `ofac_sanctions_check` (`tool_definitions()` in
`mcp_server/recall_mcp.py`). It was added by PR #208 (issue #204), the
shared surface step the #158 ruling called for. The tool goes live only
with the owner's redeploy step.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_ofac_sdn_check.py' -v
```

The tests run offline, with network access blocked.
- **Fixtures.** `tools/tests/fixtures/ofac/` holds verbatim excerpts of
  the real files: the first 30 SDN lines, an individual entry, a vessel
  entry, and their ALT lines. The complete files' size, line count and
  SHA-256 are in its `provenance.json`.
- **Coordinator live run.** The coordinator's live smoke run is owed at
  review.
