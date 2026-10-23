# Acceptance fixtures: field service planner

SYNTHETIC fixtures for `../acceptance.py` (issue #124). Every name and
address is invented, in the made up town the planner's own test fixtures
use (Sampletown). No real customer, crew or business is represented.

- `jobs-unreachable.csv`: the job posting's sample scenario "A job with a
  time window no crew member can reach". Job U1's window, 06:00 to 06:30,
  closes before any crew shift starts (the earliest shift in
  `../../tests/fixtures/crew.csv` starts at 08:00). Jobs U2 to U4
  are ordinary. Places and drive times come from the planner's committed
  fixture `../../tests/fixtures/places.json`, which places every address
  used here.

The other cases reuse the planner's committed test fixtures in
`../../tests/fixtures/` unchanged (see their `provenance.json`).
