# templates

Delivery templates, one per catalog service, for building a report that
meets the fixed format in `AGENT-BRIEF.md`: every claim with its source link
and the raw excerpt directly beneath, empty results proven by the complete raw
response, every query and retrieval time recorded, and near matches listed as
checked and excluded with reasons.

Each template is self-contained. It quotes the binding rules from
`AGENT-BRIEF.md` verbatim beneath a link to that file, carries the report
skeleton (title, scope and inputs, per subject sections, checked and excluded,
sources), and ends with the service's own checklist. Placeholders are written
in angle brackets and every one must be filled from a fetched source or
deleted. The service templates contain no example data: no published delivery
exists yet for these four services. The filled example below comes from the
one published delivery that applies every checklist item, the recall check
(catalog service 1).

| Service | Template |
| --- | --- |
| 7. Website SEO and Core Web Vitals Snapshot from PageSpeed Insights | [`service-07-pagespeed-snapshot.md`](service-07-pagespeed-snapshot.md) |
| 8. Public Dataset Build: Structured CSV from Named Public Sources | [`service-08-public-dataset-build.md`](service-08-public-dataset-build.md) |
| 9. Bilingual Research Brief: English and Chinese Public Sources | [`service-09-bilingual-research-brief.md`](service-09-bilingual-research-brief.md) |
| 10. Smart Contract Code Review: Read Only Review of a Public Solidity Contract | [`service-10-solidity-read-only-review.md`](service-10-solidity-read-only-review.md) |

## Filled example

[`filled-example.md`](filled-example.md) is the workstream D filled example
(BACKLOG.md item D.3, issue #61). It is built from the published recall check
delivery, revision 1,
[`deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md`](../deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md),
and copies two of its six subjects line for line under the report skeleton
headings: Subject 1 (a title search whose other records are named and set
aside, a detail query, and a remedy read from the recall page because the API
field repeats the hazard) and Subject 3 (an empty result proven by the
complete raw HTTP transcript, and two near matches checked and excluded with
the reason). Italic lines beginning with *Checklist* are the example's
annotations, not delivery text; the applied checklist is at the end. Every
figure in it traces to the source delivery file named in its header, and the
test below checks that every body line is a line of that file.

The general delivery checklist and general report skeleton from `BACKLOG.md`
items D.1 and D.2 are not yet separate files in this folder: each service
template carries its own copy of the skeleton and checklist, and the filled
example carries the checklist it applies. When a shared base lands, these
files can point there.

## Tests

`tools/tests/test_templates.py` checks that every template is present, that
each quotes hard rules 2 and 3 of `AGENT-BRIEF.md` byte for byte, that the
skeleton sections and the checklist are present, and that no template carries
an unmarked figure where a placeholder belongs. `tools/tests/test_filled_example.py`
checks that the filled example names its source delivery, that every body line
of it is a line of that delivery, that its excerpt blocks are contiguous
verbatim slices of it with a query URL and retrieval time above each, that the
checklist points are exercised, and that its annotations are marked. Both run
with the rest of the tools suite:

```
python3 -m unittest discover -s tools/tests -p 'test_templates.py' -v
python3 -m unittest discover -s tools/tests -p 'test_filled_example.py' -v
```
