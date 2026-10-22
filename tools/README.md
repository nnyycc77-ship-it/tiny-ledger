# tools

Command line fetchers, one per source, that query a live public source
and print one Markdown section in the delivery format from
`AGENT-BRIEF.md`: the claim lines, the source link, and the complete
raw response printed verbatim directly beneath the link. Each run
records the exact query URL and the retrieval time in UTC. Standard
library Python 3 only, no dependencies, no keys stored here. Where a
source needs a free public key, the fetcher reads it from the
environment and its header comment says so.

| Source | Fetcher | Key |
| --- | --- | --- |
| CPSC SaferProducts recall API | `cpsc_recalls.py` | none needed |

## cpsc_recalls.py

```
python3 tools/cpsc_recalls.py --subject "Vornado VH101 heater" --product-name VH101
python3 tools/cpsc_recalls.py --subject "Samsung top-load washer" \
  --product-name "Top-Load Washing Machines" --date-start 2018-01-01 --date-end 2023-12-31
python3 tools/cpsc_recalls.py --recall-number 18-136 --pretty
```

Query fields: `--product-name`, `--recall-title`, `--recall-number`,
`--date-start` and `--date-end` (YYYY-MM-DD), and `--param KEY=VALUE`
for any other field the API accepts. Spaces are encoded as `%20` in the
recorded query URL, as in the published deliveries.

An empty result is proven, not asserted: the section prints the
complete raw HTTP response transcript (status line, headers in order,
blank line, body) for the exact query, and the body is the empty array.
Every query prints that transcript, so the raw excerpt is always
directly beneath the source link.

Near matches the operator has checked and ruled out are listed with
`--exclude NN-NNN="reason"`, repeatable. The record is printed under
"Checked and excluded" with the reason, in the same block format as a
match. The tool refuses an exclusion for a recall number that is not in
the response, so an exclusion can never describe a record that was not
fetched. The tool never decides relevance itself.

When a record's remedy field repeats its hazard field word for word
(the API does this for some records, for example 21-128), the block
carries a note saying to read the remedy from the linked CPSC recall
page and quote that page as its own source.

`--pretty` adds one pretty printed JSON excerpt per record after the
transcript, values unchanged, the way `deliveries/` shows records.

## Tests

```
python3 -m unittest discover -s tools -v
```

The tests need no network. Their fixtures are verbatim copies of
responses recorded in `deliveries/`, and the fetch test runs against a
local server on 127.0.0.1.
