# `uk_sanctions_check`: UK consolidated sanctions list name check

A tool factory wave 3 tool (issue #342, parent #305). The fetcher is
[`tools/uk_sanctions_check.py`](../../tools/uk_sanctions_check.py), and
it is served as `GET /uksanctions` by the pay per call API
([`api/endpoints.py`](../../api/endpoints.py)). As the issue states,
this PR does not register it on the MCP server; that is the shared
registration step at wave end. Going live waits on the owner redeploy
step.

- **What it answers:** Whether a person or company name appears on the UK consolidated list of financial sanctions targets, as a primary name or an alias, when the list is read. Every matching list entry is printed with all of its CSV rows verbatim.
- **Source:** the UK consolidated list file `https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv`, linked from the GOV.UK page "Consolidated list of targets" (https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets/consolidated-list-of-targets). It is one public CSV file, keyless, read whole and matched locally, the same way as the OFAC tool reads its files.
- **Arguments:** `name`, a person or company name with at least 3 letters or digits.
- **Needs on the server:** Outbound HTTPS to `ofsistorage.blob.core.windows.net`. No key, no environment value.
- **Matching rule:** the OFAC tool's rule (issues #160 and #251).
  - Names are compared after folding case and accents, with every character that is not a letter or digit replaced by a space.
  - An exact match is the whole name; a contains match is the query as whole words.
  - A row's name is formed from `Name 1` to `Name 6` in two orders, both checked: the file's column order (`Name 6` first) and `Name 1` to `Name 5` followed by `Name 6`.
  - Rows are grouped into list entries by `Group ID`.
  - The `Name Non-Latin Script` column is printed but not matched.
  - No fuzzy or phonetic score is computed or claimed.
- **What it is not:** A determination that a party is the listed person or entity. A no match is not a sanctions clearance. The report states facts from the file as read and gives no assessment or advice.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price, and `mcpize.yaml` is untouched.

Every report states the file as read: the exact URL, the UTC retrieval time, the bytes, the SHA-256, the physical lines, the records, the list entries and the list date line. A no match is therefore proven against those exact bytes and can be repeated. The multi-megabyte file is not pasted.

**Fail closed.** These all stop with exit 2 and no report (502 on the API):
- a failed request;
- any status other than 200;
- a file not in the captured shape: the date line, then the 36 column header, then 36 field records.

The answer is then unknown, never a no match.

## The file, as captured

Captured by the coordinator under Option B on issue #342 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/342#issuecomment-6384612039)), retrieved 2026-10-24, about 13:07 UTC: HTTP 200, 16,641,139 bytes, SHA-256 `9585695391b51f72ca9eae1b6671e1f81fb1fa6e21a1661dad346636f2320c7f`, 19,763 physical lines, 19,761 records after the header. These are the coordinator's figures for the full file, which is not in this repo. Lines 1 and 2, verbatim:

```
Last Updated,03/06/2026
Name 6,Name 1,Name 2,Name 3,Name 4,Name 5,Title,Name Non-Latin Script,Non-Latin Script Type,Non-Latin Script Language,DOB,Town of Birth,Country of Birth,Nationality,Passport Number,Passport Details,National Identification Number,National Identification Details,Position,Address 1,Address 2,Address 3,Address 4,Address 5,Address 6,Post/Zip Code,Country,Other Information,Group Type,Alias Type,Alias Quality,Regime,Listed On,UK Sanctions List Date Designated,Last Updated,Group ID
```

## What a report shows, on a recorded row

The claims are the tool's own lines for the query `Gazprom Neft` against the test excerpt; the offline tests check these exact lines. The row beneath them is verbatim from the capture.

- `1 list entry matched Gazprom Neft: 1 with an exact match, 0 by contains match only.`
- `### Group ID 16736: Entity, regime Russia`
- `- exact match on GAZPROM NEFT (Alias Type as shown: Primary name)`

Source: https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv, the GAZPROM NEFT row, captured by the coordinator under Option B on issue #342 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/342#issuecomment-6384614890)), from the file above; kept in [`tools/tests/fixtures/uk-sanctions/conlist-excerpt.csv`](../../tools/tests/fixtures/uk-sanctions/conlist-excerpt.csv) with its provenance.
```
GAZPROM NEFT,,,,,,,ГАЗПРОМ НЕФТЬ,Cyrillic,Russian,,,,,,,,,,5 Let. A. Galernaya,,,,,Saint Petersburg,190000,Russia,"(UK Sanctions List Ref):RUS2383. Financial sanctions imposed in addition to an asset freeze: Trust services. Date trust services sanctions imposed: 10/01/2025. (UK Statement of Reasons):GAZPROM NEFT is an involved person under the Russia (Sanctions) (EU Exit) Regulations 2019 based on the following grounds: 1) GAZPROM NEFT is or has been involved in obtaining a benefit from or supporting the Government of Russia by carrying on business in a sector of strategic significance to the Government of Russia, namely the Russian energy sector; and 2) GAZPROM NEFT is or has been involved in obtaining a benefit from or supporting the Government of Russia by carrying on business of economic significance to the Government of Russia. (Business Reg No):Russia TIN: 5504036333",Entity,Primary name,,Russia,10/01/2025,10/01/2025,15/01/2025,16736
```

## Not verified here

This container cannot reach the list file or the GOV.UK page, because the proxy refuses the connection. No live run was made from it. The tool is tested offline on an excerpt assembled from four verbatim lines of the coordinator's capture: the date line, the header, one Individual row and one Entity row. The coordinator's live smoke run at review is the live check.

- **No headers on record.** No response headers were captured, so the header part of a live report is not on record here.
- **No alias row captured.** Alias grouping is tested on a labelled synthetic row.
- **Full-file shape not seen.** The full file was not seen here, so its shape beyond the four captured lines, for example rows with line breaks inside quoted fields, is checked only by the coordinator's live run.
