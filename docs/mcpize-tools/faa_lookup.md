# `faa_lookup`: FAA aircraft registration lookup

A tool factory wave 2 tool (issue #181). The fetcher is
[`tools/faa_lookup.py`](../../tools/faa_lookup.py), and it is served as
`GET /faa` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #213 (issue #210), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** What aircraft is registered under this N number, and whose name is on the registration? It gives make and model (the Aircraft Reference file's `MFR` and `MODEL`), year (`YEAR MFR`) and registrant name (`NAME`), exactly as the record states them with only the file's space padding trimmed, followed by the matched rows in full.
- **Source:** the FAA releasable aircraft database, one keyless ZIP download: `https://registry.faa.gov/database/ReleasableAircraft.zip`. The FAA download page says "The data in the download is refreshed daily at 11:30 pm central time. The download is delivered in a Comma-Delimited text file (.txt extension) format." The columns are read from each file's own header row. Their meanings come from the FAA layout document `ardata.pdf`: for example, N-Number is the "Identification number assigned to aircraft", and Registrant's Name is "The first registrant's name which appears on the Application for Registration". Both are quoted by the coordinator on #181.
- **Arguments:** `n_number`, for example `N100ZT`. The leading N is optional; the file stores the number without it.
- **Release date:** the archive carries no date file, so every reply states the archive's `Last-Modified` header, labelled as such, with the retrieval time and the archive's SHA-256.
- **Cache:** the archive is about 73 MB. It is downloaded at most once per UTC day into a cache folder outside the repo (`$TINY_LEDGER_CACHE/faa`, or `~/.cache/tiny-ledger/faa`), with its URL, retrieval time, headers, size and SHA-256 recorded beside it. A cached archive whose bytes no longer match is downloaded again.
- **Needs on the server:** outbound HTTPS to `registry.faa.gov`, and disk room for the archive. No key, no environment value.
- **What it is not:** a title search or an ownership finding. Registration data is a public record, and the report shows only what the record itself shows.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

## No match and failures

- **No match** is proven by the file as read. MASTER.txt's byte count, line count and SHA-256 are printed, with the archive's, so anyone can repeat the check against the same file. In the coordinator's capture (issue #181), the archive was 73,006,950 bytes with SHA-256 `40b3a90b708906d52a629ec7d0b7b323390a0e6af839fc30ebc1f22d5aefcb9d`. Its MASTER.txt was 195,251,786 bytes and 318,000 lines (1 header and 317,999 data rows), with SHA-256 `75f530621374af0b635b7e7ccd06190a9d9b06f750c66ebf6db1ab4748126c6c`, and no row carried N-NUMBER `00000`.
- **Failures fail closed.** A failed download, any status other than 200, an archive that is not a ZIP, or one whose MASTER.txt or ACFTREF.txt lacks the columns read stops the run. The CLI exits 2, the API answers 502, and no report is printed. Redirects are never followed: the captures show a wrong URL answering 302 to an unrelated page. The host also refused a plain curl user agent with a 403 in the coordinator's probe; the agent this tool sends is pending a coordinator ruling on #181. A failure is never shown as no match.

## What a report shows, on a recorded row

For the coordinator's capture of N100ZT, the report names make `TEXTRON AVIATION INC`, model `525C`, year `2022` and registrant name `BANK OF UTAH TRUSTEE`. The row is registered to a corporation: `TYPE REGISTRANT` is 3, which the layout document lists as "3 Corporation". Beneath that, the report prints the two raw rows exactly as the files have them.

Source: `https://registry.faa.gov/database/ReleasableAircraft.zip`, MASTER.txt row, captured by the coordinator under Option B on issue #181 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/181#issuecomment-6381130638)), archive Last-Modified Sat, 24 Oct 2026 04:58:32 GMT; saved as [`tools/tests/fixtures/faa-registry/master-row-100ZT.csv`](../../tools/tests/fixtures/faa-registry/master-row-100ZT.csv)
```text
100ZT,525C0392                      ,2076628,66011,2022,3,BANK OF UTAH TRUSTEE                              ,50 S 200 E STE 110               ,                                 ,SALT LAKE CITY    ,UT,841111617 ,S,035,US,20230909,20221004,1C        ,5,5 ,V ,50003405, ,20220926,                                                  ,                                                  ,                                                  ,                                                  ,                                                  ,20291031,01371937,                              ,                    ,A00705    ,
```
Source: the same archive, ACFTREF.txt row for code 2076628; saved as [`tools/tests/fixtures/faa-registry/acftref-row-2076628.csv`](../../tools/tests/fixtures/faa-registry/acftref-row-2076628.csv)
```text
2076628,TEXTRON AVIATION INC          ,525C                ,5,5 ,1,0,02,011,CLASS 3,0000,               ,                                                  ,
```

## Not verified here

This container cannot reach `registry.faa.gov` (the proxy refuses the
connection), so no download was made from it. The 73 MB archive is not
stored in the repo. The offline tests assemble a small archive from the
verbatim header lines and rows above, and the downloader is tested against
a local server. The coordinator's live smoke run at review is the live
check.
