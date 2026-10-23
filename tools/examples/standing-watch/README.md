# Standing watch demo

A live demo of `tools/standing_watch.py` on a small public sample
list, run on 2026-10-23. The names are a public demonstration list,
not a client list. The product side is the same list as the hand built
sample baseline of the same date; the carrier side matches it entry
for entry, and the first snapshot below agrees with that sample's
figures (Old Dominion 10,313 power units, Schneider 9,866, XPO
20,208; recalls 21-128, 19-105, and 18-136 on record; the Instant Pot
Smart WiFi query empty).

Files:

* `watchlist.json` — the sample list in the documented format: three
  carriers by USDOT number, four products (three tracked by recall
  number, one of them also by product name, and one tracked by product
  name alone with no recall on record).
* `snapshot-run1-2026-10-23.json` — the first run's snapshot
  (run 2026-10-23T21:57:11Z): the fields that matter per entry, and
  for every response its query URL, UTC retrieval time, HTTP status,
  SHA-256, and the complete raw transcript.
* `report-run1-baseline-2026-10-23.md` — the baseline edition from
  run 1: one fields table and the full source evidence per entry.
* `snapshot-run2-2026-10-23.json` and
  `report-run2-no-change-2026-10-23.md` — a second run minutes later
  (2026-10-23T21:57:45Z) against the run 1 snapshot, showing the no
  change report shape: all seven entries unchanged, one line each
  with the run's source URLs, retrieval times, and response hashes.

Reproduce it (writes a fresh snapshot over the given path):

```sh
python3 tools/standing_watch.py \
    --watchlist tools/examples/standing-watch/watchlist.json \
    --snapshot /tmp/my-snapshot.json \
    --report /tmp/my-report.md
```

Run it twice against the same snapshot path: the first report is a
baseline edition, the second a change report against the first.
