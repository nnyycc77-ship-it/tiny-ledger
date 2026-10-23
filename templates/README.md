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
deleted. The templates contain no example data; no published delivery exists
yet for these four services, so no filled example is included.

| Service | Template |
| --- | --- |
| 7. Website SEO and Core Web Vitals Snapshot from PageSpeed Insights | [`service-07-pagespeed-snapshot.md`](service-07-pagespeed-snapshot.md) |
| 8. Public Dataset Build: Structured CSV from Named Public Sources | [`service-08-public-dataset-build.md`](service-08-public-dataset-build.md) |
| 9. Bilingual Research Brief: English and Chinese Public Sources | [`service-09-bilingual-research-brief.md`](service-09-bilingual-research-brief.md) |
| 10. Smart Contract Code Review: Read Only Review of a Public Solidity Contract | [`service-10-solidity-read-only-review.md`](service-10-solidity-read-only-review.md) |

The workstream D base from `BACKLOG.md` (the general delivery checklist, the
general report skeleton, and a filled example built from a published
delivery; issue #4) is not in this folder yet. Until it lands, each template
here stands alone; when it lands, the shared rules can move into it and these
templates can point there.

## Tests

`tools/tests/test_templates.py` checks that every template is present, that
each quotes hard rules 2 and 3 of `AGENT-BRIEF.md` byte for byte, that the
skeleton sections and the checklist are present, and that no template carries
an unmarked figure where a placeholder belongs. It runs with the rest of the
tools suite:

```
python3 -m unittest discover -s tools/tests -p 'test_templates.py' -v
```
