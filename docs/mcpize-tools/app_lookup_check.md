# `app_lookup_check`: App Store lookup

A tool factory wave 1 tool (issue #167, parent #158). The fetcher is
[`tools/app_lookup_check.py`](../../tools/app_lookup_check.py), and it is served as
`GET /app` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** which App Store apps the public iTunes Search API
  returns for an app name. It shows `resultCount` as shown and the number
  of entries in the results array, and states any difference between the
  two without reconciling it. Then, per app and in response order, each
  as shown or "not shown":
  - `trackName`, `sellerName`, `averageUserRating`, `userRatingCount`
    and `trackViewUrl` (the store link);
  - whether `trackName` equals the searched name, ignoring case and
    spacing.

  The tool never decides which app the buyer means: the exact-name mark
  is a mechanical comparison only.
- **Source:** the iTunes Search API, `https://itunes.apple.com/search`,
  keyless.
- **Arguments:**
  - `name`, the app name to search for;
  - optional `country`, a two-letter store code (default `us`);
  - optional `limit`, 1 to 200 (default 10). The range is Apple's
    "Values: 1 to 200", as captured on #167.
- **Needs on the server:** outbound HTTPS to `itunes.apple.com`. No key,
  no environment value.
- **Nothing found is said in its own terms:** the search matches loosely.
  On #167 an invented name returned five unrelated apps, not an empty
  list. So "nothing found" is zero exact name matches, said in those
  terms with the complete raw response beneath it. It is never claimed
  as proof that no such app exists.
- **Fails closed:** a response that is not HTTP 200, a body that is not a
  JSON object with `resultCount` and a results array, or a transport
  failure prints nothing and exits 2 (502 on the API).
- **What it is not:** a review of any app. Ratings and listings change.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price
  set by the owner ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this docs page sets or changes a price; pricing stays in the
  owner redeploy step.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_app_lookup_check.py' -v
```

The tests run offline on the recorded responses in
[`tools/tests/fixtures/app-lookup/`](../../tools/tests/fixtures/app-lookup/),
with their provenance.
