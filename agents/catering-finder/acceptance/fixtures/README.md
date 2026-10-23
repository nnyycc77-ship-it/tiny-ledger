# Acceptance fixtures: catering finder

SYNTHETIC inputs for `../acceptance.py` (issue #124). Every case runs
against the catering finder's committed synthetic vendor store in
`../../tests/fixtures/` (six invented vendors on `.invalid` hosts; see the
store's `provenance.json`). Nothing here is a real event, business,
message or reply.

- `brief-150.json`: the posting's sample scenario "Dinner for 150 guests"
  (thin coverage, large headcount), with a collection window end. It also
  carries a synthetic buyer contact, so that the run can show it never
  reaches a draft or the report.
- `replies-150.json`: the operator's send and reply records for that
  case. They are invented, and entered through the agent's own
  `record-sent` and `record-reply` commands into a temporary log.
- `brief-budget.json`: the posting's sample "set budget per person",
  with the budget per head set below some vendors' stated prices, so that
  over budget marking can be checked. It also carries the synthetic buyer
  contact.
