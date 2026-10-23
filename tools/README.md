# CPSC recall fetcher

Run from the repository root with Python and curl installed. No API key,
account, wallet, or Python package installation is needed. curl is used to
retain the received HTTP status line and header order alongside the complete
response body. Its default config is disabled; redirects are not followed.

```sh
python3 tools/cpsc_recalls.py 'Instant Pot'
python3 tools/cpsc_recalls.py 'Instant Pot Smart WiFi' \
  --exact-name 'Instant Pot Smart WiFi' --near-product 'Instant Pot'
```

These search terms come from the published recall delivery.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/5be7e2905c9b8253793ce45455f4b698f38919f4/deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md>
```text
## Subject 3: Instant Pot Smart WiFi 6 Qt
```

The broader search term is recorded in that delivery too.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/5be7e2905c9b8253793ce45455f4b698f38919f4/deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md>
```text
Other Instant Pot records in the same database, checked and excluded because they name different models: a ProductName = "Instant Pot" query returned 1 record (retrieved 2026-10-22T03:29:56Z), record 15-741 below, and a detail query for record 18-110 was run as well (retrieved 2026-10-22T03:29:25Z). Neither record names the Smart WiFi, and neither names a 6 Qt model.
```

The CLI emits a single Markdown section on stdout. Every query has its exact
GET URL, retrieval time in UTC, result claims, source link, and complete curl
response capture immediately beneath the link. The body is not pretty printed
or reordered, including for an empty array. HTTP headers and body retain their
original line endings; the Markdown closing fence adds a separator newline
when the captured body has none. curl removes transfer framing, such as chunk
sizes; this is an HTTP response capture, not a packet trace.

By default records are candidates, not verified model matches. `--exact-name`
keeps records where any product name equals the supplied name, ignoring case
and whitespace. Other records are listed as checked and excluded with the
source names and this narrow reason. `--near-product` adds another search and
requires `--exact-name`; it can be repeated. These are name comparisons only:
alternate names and actual model applicability require reviewer judgment.
An empty result is never described as proof that a product is safe. The tool
does not claim to search other databases or resolve hazard/remedy discrepancies.

Transport, HTTP, JSON, and required-field errors exit unsuccessfully, with a
diagnostic on stderr and no partial report on stdout. No failed query becomes
an empty-result claim. Review a generated report before using it in a delivery.

## Verification

```sh
python3 -m unittest discover -s tools/tests -v
CPSC_LIVE=1 python3 -m unittest discover -s tools/tests -v
```

Offline tests use the unmodified public HTTP captures in `tests/fixtures/`.
`provenance.json` records each source URL, actual UTC retrieval time, and SHA-256
digest. Malformed-response tests deliberately corrupt captures only to verify
error handling. The optional live test invokes the CLI against CPSC, checks an
empty query and a broader query with a checked/excluded name, and requires no
fixture or mocked transport. Live results can change; a failure requires review,
not replacement with invented data.
