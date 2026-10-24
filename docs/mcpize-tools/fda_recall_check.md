# `fda_recall_check`: FDA enforcement recall check

A tool factory wave 2 tool (issue #177).
- **Code:** the fetcher is
  [`tools/fda_recall_check.py`](../../tools/fda_recall_check.py). The pay
  per call API serves it as `GET /fda?name=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not on the MCP server yet.** Under the wave registration ruling on
  #158, confirmed for this tool on #177, every wave tool that passes review
  is registered on the server in one shared surface PR at the end of the
  wave. Going live is one owner redeploy step after that.

## The tool at a glance

- **What it answers:** has this food product, medical device or firm drawn
  FDA enforcement recalls in openFDA's enforcement reports, and what do the
  records say? Each matching record is listed with these fields, exactly as
  returned:
  - `recall_number`, `classification` and `status`;
  - `product_description` and `recalling_firm`;
  - `reason_for_recall`;
  - `recall_initiation_date`, `report_date`, `center_classification_date`
    and `termination_date`.

  Dates are the source's own `YYYYMMDD` strings. An ongoing recall with no
  `termination_date` shows it as not in the record.
- **Source:** openFDA, `GET https://api.fda.gov/food/enforcement.json` and
  `GET https://api.fda.gov/device/enforcement.json`, with
  `search=<field>:"<name>"` sent as one quoted phrase, plus `limit`.
- **Arguments:**
  - `name`: 2 to 100 characters, with no double quote or backslash;
  - `field`: `product` (searches `product_description`, the default) or
    `firm` (searches `recalling_firm`);
  - `category`: `food`, `device` or `both` (the default);
  - `limit`: 1 to 100 records per category (default 10). openFDA allows up
    to 1000; the cap keeps reports readable.
- **Keyless.** openFDA's authentication page, as quoted on #177, says "An
  API key is required to make calls to the openFDA API." It also states
  the limits: "With no API key: 240 requests per minute, per IP address.
  1,000 requests per day, per IP address." All four coordinator captures on
  #177 were made with no key and answered, so keyless calls work inside
  those limits.
  - **This tool never sends a key.** The response's `Link` header echoes
    the query string, so a key sent as `api_key` could be printed back into
    a report.
- **Needs on the server:** outbound HTTPS to `api.fda.gov`, and no key.
- **What it is not:** a clearance. A search that matches nothing covers
  that exact phrase in that field only. Other spellings, the other field,
  and recalls outside openFDA's enforcement reports are not covered.
  openFDA's own disclaimer is in every raw response.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

For each category searched:
- **The answer.** openFDA's `meta.results.total` as shown, and each listed
  record's fields as above.
- **The evidence.** The exact query, a note that it was sent keyless, the
  UTC retrieval time, each matched record as raw JSON, and the complete
  raw response (status line, headers and body) under the source link.

**Empty result:** the captures on #177 prove that openFDA answers a search
with no match with HTTP 404, whose body's error code is `NOT_FOUND`
("No matches found!"). That answer is reported as no match, with its
complete raw response as the proof. It is never a clearance.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API. The error names the source, the query and the reason (openFDA's error
code, message and details when it gives them). They are:
- any other status, such as the captured 500 `SERVER_ERROR` answer to a
  malformed search;
- a 404 without `NOT_FOUND`;
- a failed request;
- a redirect off `api.fda.gov`;
- a body not in the captured shape.

A failure is never shown as an empty result.

## Running it

```sh
python3 tools/fda_recall_check.py "peanut butter"
python3 tools/fda_recall_check.py "Covidien" --field firm --category device
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_fda_recall_check.py' -v
```

The tests run offline on the coordinator's four keyless captures from #177,
verbatim in `tools/tests/fixtures/fda-recall/` with their hashes:
- a food hit (`peanut butter`, total 606);
- a device hit (`catheter`, total 2634);
- the empty result (404 `NOT_FOUND`);
- the malformed search error (500 `SERVER_ERROR`).

The coordinator's live smoke run is owed at review.
