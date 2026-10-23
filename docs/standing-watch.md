# Standing watch: carrier and recall change reports

The standing watch is the recurring form of two checks this repo
already sells one at a time: FMCSA carrier vetting and CPSC product
recall checks. Instead of a single report, the buyer hands over a list
once, and the watch rechecks that list on a cycle and reports only
what changed. A quiet cycle produces a short no change report. A real
change produces an alert naming the entry, the field, the old value,
and the new value, with the new state's source evidence printed in
the fixed delivery format.

The tool is `tools/standing_watch.py`. It reuses the existing
fetchers (`tools/fmcsa_carrier.py`, `tools/cpsc_recalls.py`) and adds
no new source and no new dependency.

## How a buyer list becomes a standing watch

1. The buyer sends the list: carrier legal names with USDOT numbers,
   and product names as sold. Names alone are a starting point, not
   an identity: a carrier name search can return more than one
   carrier, and a CPSC product name search can miss a record that
   stands in the same database.
2. At setup, each entry is pinned to the identifier the watch will
   recheck forever: the USDOT number for a carrier, and for a product
   its name variants plus, once a recall is known, the recall number.
   The pinned list is written as a watchlist file (format below) and
   the buyer confirms it.
3. The first run establishes the baseline and the buyer receives a
   baseline edition: one table of the fields that matter per entry,
   with the complete raw response for every query printed beneath its
   source link.
4. Each later run pulls the same sources again, stores a new dated
   snapshot, diffs it against the previous one, and delivers a change
   report: alerts for changed entries with the new evidence, one line
   for each entry that did not change.
5. The snapshots are kept. Any line in any report can be checked
   against the stored pull for that cycle, by SHA-256 hash first and
   by the full transcript after that.

## The watchlist file

JSON, one file per buyer list:

```json
{
  "version": 1,
  "carriers": [
    {"usdot": "90849", "label": "OLD DOMINION FREIGHT LINE INC"}
  ],
  "products": [
    {"label": "Peloton Tread+",
     "queries": [{"field": "RecallNumber", "value": "21-128"},
                 {"field": "ProductName", "value": "Tread+"}]}
  ]
}
```

A carrier needs only its USDOT number; the label is an optional
heading. A product needs a label and at least one query. Query fields
are the ones the CPSC fetcher supports: `ProductName`, `RecallTitle`,
`RecallNumber`. A worked example with its demo runs lives in
`tools/examples/standing-watch/`.

## What is watched

Only what the fetchers actually return; nothing is derived or
interpreted, and status and rating codes are reported as shown.

Carriers, per entry:

* From the FMCSA Company Census File record: every selected field as
  shown, including `status_code` and `docket1_status_code` (the
  authority state as the record shows it) and `safety_rating`, plus
  the record count for the USDOT query.
* From the SAFER Company Snapshot: every labelled value the fetcher
  reads, including Operating Authority Status, USDOT Status, and
  Rating where the page shows them.
* From FMCSA Licensing and Insurance: the record lines the fetcher
  finds in the response text. This source is the insurance view; it
  also presents a verification challenge to automated reads on some
  days, and on those days the snapshot records that no record fields
  were found in the response, with the full response stored, rather
  than claiming an insurance state.

Products, per entry: the set of recall numbers as shown across the
entry's queries, and each query's record count. An entry with no
recall today has the proven empty result as its baseline; the alert
fires the day a recall number appears.

## Snapshots and provenance

Each run writes one snapshot JSON: the watchlist name, the run time
in UTC, and per entry the field map plus, for every response, the
exact query URL, the UTC retrieval time, the HTTP status line, the
SHA-256 of the raw transcript, and the complete raw transcript. This
is the repo's fixture habit applied to a product: a claim in a report
is only ever as good as the stored pull under it.

## Report shapes

* Baseline edition (first run): the fields table and the full source
  evidence for every entry.
* Change report: a summary line; change alerts with the field, the
  old value, and the new value, and the changed entry's full source
  evidence for the new state; a section for entries new to the list;
  a section for entries removed from it; and a no change section with
  one line per quiet entry carrying that run's source URLs, retrieval
  times, and response hashes (the full pulls sit in the run's
  snapshot file).
* A run where nothing changed says so in one line after the no
  change list.

## Limits, stated plainly

* A failed fetch never reads as an empty result. A transport failure
  or an uninterpretable response aborts the run, leaves the previous
  snapshot untouched, and produces no report; the cycle is rerun, not
  papered over. An FMCSA HTTP error status is recorded as provenance
  and the entry's fields read as not determinable from that response.
* Product name searches can miss. Searching the CPSC ProductName
  field for "Peloton Tread" returned zero records on 2026-10-23 while
  recall 21-128 for the Tread+ stands in the same database. That is
  why entries are pinned to recall numbers once known and tracked
  under name variants, and why an empty result is always proven with
  the full raw response.
* The watch reports changes to the public record. It does not rate
  carriers, judge products, or recommend action; what a change means
  for the buyer is the buyer's call.
