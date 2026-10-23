# Acceptance fixtures: local quotes

SYNTHETIC inputs for `../acceptance.py` (issue #124). Both cases run
against the agent's committed synthetic provider store in
`../../tests/fixtures/` (seven invented providers on `.invalid` hosts; see
the store's `provenance.json`). Nothing here is a real request, business,
message or reply.

- `request-thin.json`: the posting's sample scenario "Rare service in a
  small town with few providers" (thin coverage). It is a service that
  few of the store's providers name. It carries a synthetic buyer contact,
  so that the run can show it never reaches a draft or the report.

In that case the script records one SYNTHETIC send through the agent's
own `record-sent` command: Riverside Rooter, web form,
2026-11-01T15:00:00Z. No reply is recorded, so the non responder path is
exercised. Nothing is sent to anyone.
