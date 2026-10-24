# App lookup check

`tools/app_lookup_check.py`, issue
[#167](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/167) (tool
factory wave 1, parent #158).

## What it answers

Give it an app name. It answers which App Store apps the store returns
for that name, in the delivery format from `AGENT-BRIEF.md`: every claim
cites its source, and the response is printed in full beneath its
request URL.

For each app, in the order the store returns them, it shows:
- the app name (`trackName`);
- the seller (`sellerName`);
- the average user rating (`averageUserRating`) and the rating count
  (`userRatingCount`);
- the store link (`trackViewUrl`);
- whether the app name equals the searched name, ignoring case and
  spacing.

Each value is shown as the response gives it. A number keeps its literal
text from the body, so a rating prints as
`4.881750000000000255795384873636066913604736328125`, never rounded.

The report also gives `resultCount` as shown beside the number of
entries in the `results` array, and says so if the two differ. The
exact-name mark is a mechanical comparison: the tool never decides which
app the buyer means. The report is an observation of one moment, not a
review of any app.

## When no app has the name

The search matches loosely. On #167 the coordinator searched an
invented name (`zqxflorp`) and got five unrelated apps back, not an
empty list. Two further invented terms gave the same result. So this
tool's "nothing found" case is **zero exact name matches**. The report
says that in those terms, with the complete response beneath, and never
says the store returned nothing. A response whose `results` array is
truly empty is reported the same way. Neither is presented as proof that
no such app exists.

## Source

The source is the Apple iTunes Search API,
`https://itunes.apple.com/search`. It needs no key and no account. The
tool sends `term`, `country` (default `us`), `entity=software` and
`limit` (default 10).

Apple's documentation, the "Searching" page captured by the coordinator
on #167
([comment 6378882083](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/167#issuecomment-6378882083)),
documents these parameters. For `limit` it says "The default is 50.
Values: 1 to 200.", so the tool accepts 1 to 200.

That page does not list the result fields. The field names used here are
the ones the captured responses carry.

## Run it

```sh
python3 tools/app_lookup_check.py "Nike"                       # example app name
python3 tools/app_lookup_check.py "Nike" --country us --limit 5
```

The API serves the same check as
`GET /app?name=<name>[&country=<cc>][&limit=<n>]` (`api/endpoints.py`).
Like every wave 1 tool, it joins the MCP server in the one shared surface
PR at the end of the wave, per the ruling on #158.

## Price

On the MCP shelf the tool will cost **0.25 USDC per call**, the price
the owner set on issue #147
([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
That price applies once the tool passes review and the owner's redeploy
step for the whole wave puts the shelf live. Nothing in this repo changes
a price.

## Failures

The tool fails closed, printing nothing on stdout and exiting 2, when:
- the response is not HTTP 200;
- the body is not a JSON object holding `resultCount` and a `results`
  array of objects;
- the request fails in transport.

A body may begin with newlines and arrive as `text/javascript`, as the
captures do. The parser allows both.

## Example

This is the report for the example name `Nike`, replayed from the
coordinator's live capture of 2026-10-24, taken at about 02:36 UTC; the
response `Date` header reads 02:36:12 GMT
([#167 comment 6378882369](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/167#issuecomment-6378882369)).
Apps 3 to 5 and the Sources section, with the complete transcript, are
left out here. The coordinator's live smoke run of the finished tool is
owed at review.

```text
QUERY: iTunes Search API, term = `Nike`, country = us, entity = software, limit = 5 (retrieved 2026-10-24 about 02:36 UTC, as stated by the coordinator; source S1). HTTP status as returned: 200 OK.
resultCount as shown: 5. Entries in the results array: 5.

### App 1 of 5

- App name (trackName) as shown: `Nike: Engineered for Athletes`
- Seller (sellerName) as shown: `Nike, Inc`
- Average user rating (averageUserRating) as shown: `4.881750000000000255795384873636066913604736328125`
- User rating count (userRatingCount) as shown: `1698620`
- Store link (trackViewUrl) as shown: `https://apps.apple.com/us/app/nike-engineered-for-athletes/id1095459556?uo=4`
- trackName equals the searched name, ignoring case and spacing: no.

### App 2 of 5

- App name (trackName) as shown: `Nike SNKRS: Sneakers & Apparel`
- Seller (sellerName) as shown: `Nike, Inc`
- Average user rating (averageUserRating) as shown: `4.857549999999999812416717759333550930023193359375`
- User rating count (userRatingCount) as shown: `1413379`
- Store link (trackViewUrl) as shown: `https://apps.apple.com/us/app/nike-snkrs-sneakers-apparel/id911130812?uo=4`
- trackName equals the searched name, ignoring case and spacing: no.

...

Exact name matches among the returned apps: 0 of 5 (source S1).

No returned app is named `Nike`, ignoring case and spacing. The search matches loosely: it returned 5 apps, and none of them carries the searched name (source S1). This is a search observation, not proof that no such app exists.
```

No app in this response is named exactly "Nike". That is the mechanical
mark at work: the store's own name for its app is "Nike: Engineered for
Athletes".

## Tests

`tools/tests/test_app_lookup_check.py` has 14 tests. They run on the two
real captures in `tools/tests/fixtures/app-lookup/`, whose provenance is
in that folder's `provenance.json`, and on the #51 capture in
`tools/tests/fixtures/brandcheck/`, which checks that a body starting
with newlines parses. Built inputs, labelled where they appear, cover:
- a truly empty `results` array;
- counts that disagree;
- failing closed.

`api/test_endpoints.py` covers `GET /app`.

As posted, both captures have the status line `HTTP/1.1 HTTP/1.1 200 OK`.
The fixtures keep it verbatim, and the tool reads the status code as the
first three-digit field of the line.
