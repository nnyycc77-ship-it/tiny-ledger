# uspto_trademarks.py: the Brand Name Checker's trademark leg

Issue #125. `tools/brand_name_checker.py` takes its trademark section from
`tools/uspto_trademarks.py`.

**State today: the leg stays "Not covered".** With no key, and with a key,
the report's trademark section is the same wording the checker printed
before this issue, byte for byte. `tools/tests/test_uspto_trademarks.py`
compares the whole report against the one main printed at `d46c1c1`. The
reason is the coordinator's ruling on #125: the keyed USPTO route on record
is TSDR, which answers status by case number. **No documented name search
endpoint is on record.** So the request builder and the response reader are
marked NOT DOCUMENTED and refuse to run. The leg switches on only when a
documented name search endpoint and a live keyed run both exist. The code
existing does not switch it on.

```sh
python3 tools/brand_name_checker.py Nike                       # no key: unchanged report
USPTO_API_KEY=... python3 tools/brand_name_checker.py Nike     # key: same report, refusal note on stderr
python3 -m unittest discover -s tools/tests -p 'test_uspto_trademarks.py' -v
```

**Key:** the key is read from the environment variable `USPTO_API_KEY`
only. It is never printed, logged, or written to a file, and the refusal
note does not include it.

## Owner step sheet

1. **Where the key is requested.** USPTO registers API keys for its
   Trademark Status and Document Retrieval (TSDR) APIs against a
   USPTO.gov account, through the account route linked from the page below
   (account.uspto.gov). The key is tied to that account.

   Source: <https://www.uspto.gov/trademarks/apply/check-status-view-documents/trademark-bulk-data>,
   opened live by the coordinator on 2026-10-23 and quoted verbatim on
   <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/125#issuecomment-6372123640>
   (comment body sha256 `a9e32be266b145b165671338ab693d895d97ce8357b3b12c3f63a597ff7b67ae`):

   ```text
   "You need an application programing interface (API) key to download bulk data in the Trademark Status and Document Retrieval (TSDR) system. TSDR allows you to make programmatic requests for trademark case status, documents, and images through our web APIs. ... You must register for an API key in order to use the TSDR APIs. An API key is a string value that allows the USPTO to regulate TSDR usage based on the key tied to your USPTO.gov account. It serves as a unique identifier and a token for authentication. Find more information on our TSDR Data API webpage, including frequently asked questions on the TSDR APIs and detailed instructions and sample URL search queries in our user guide. If you have questions about the TSDR APIs, email APIhelp@uspto.gov."
   ```

2. **Cost.** No fee is stated on the USPTO page. This sheet does not claim
   more than that.

   Source: the same coordinator comment:

   ```text
   The page states no price for the key; the sheet says "no fee is stated on the USPTO page" rather than asserting more than that.
   ```

3. **How the key reaches the worker host.** It goes through the Secure Vault
   API access flow, into the host's environment as `USPTO_API_KEY`. It
   never goes in chat or in this repo.

   Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/125>
   (issue body sha256 `a8e87a11e5440758f1cb6c0dd62516fb54419bd16a5395107fd544b475ab4d40`):

   ```text
   a short owner step sheet in the module README: where the key is requested, that it is free, and that it is delivered through the Secure Vault API access flow, never in chat or in the repo.
   ```

   The issue asks the sheet to say the key is free. The USPTO page as
   captured states no price, so step 2 says only that.

4. **What a key does today: nothing visible in the report.** TSDR answers
   case status, documents and images for a known case number. It does not
   answer a candidate name. No official keyed endpoint that takes a name
   and returns exact and near matches is on record.

   Source: the same coordinator comment:

   ```text
   **Not grounded, and not supplied: an official keyed name search endpoint.** The coordinator could not verify any official USPTO developer API that takes a candidate name and returns exact and near matches under a key. TSDR as documented above is keyed on a case (serial) number.
   ```

## What switches the leg on

All three are needed:

1. A documented USPTO name search endpoint, captured with its request,
   authentication and response shapes.
2. `build_search_request` and `read_search_response` written from that
   documentation, rendering in the checker's claim, source and raw excerpt
   format, with an empty result proven by the full raw response.
3. A live keyed run.

Until then the 60 USDC bid's honest "could not confirm" wording on #51
stands unchanged.
