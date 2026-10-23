# Nonprofit pack runner: design note and how the shape extends

`tools/nonprofit_pack.py` (issue #149) is the batch form of the
ProPublica nonprofit fetcher. Given a list of names or EINs it resolves
every entry against the ProPublica Nonprofit Explorer API v2 and
assembles one combined Markdown pack in the delivery format from
AGENT-BRIEF.md: a summary table up front whose every figure appears in
the numbered section the row points to, one evidence section per entry
rendered by `tools/propublica_nonprofits.py` itself, and a closing list
of the entities that could not be found, proven with the complete raw
response.

## The shape, and why it survives swapping entity types

The runner is three pieces with a thin assembly over them:

1. **Resolver** (in `assemble`): turns one list entry into zero or one
   examined entity record, under a stated resolution rule. For
   nonprofits the rule is the single fetcher's: an EIN is fetched
   directly; a name is examined only on an exact name match in the
   search results, ignoring case and spacing; no match or several
   matches leaves the entry not resolved, with the search section
   printed as fetched. Resolved entities are deduplicated by EIN.
2. **Per entity renderer**: the existing fetcher's `render_search` and
   `render_organization`, reused rather than reimplemented, so a pack
   section is byte for byte the delivery format a single fetch
   produces: source link, claim, verbatim excerpt.
3. **Summary extractor** (`filing_summary`): reads the summary figures
   (count of filings with extracted figures, and the latest filing's
   tax period and total revenue) out of the same parsed body the
   section renders, parsing the same capture the excerpts are cut
   from. That is what makes the acceptance bar, every summary figure
   traceable into its section, hold by construction rather than by
   checking afterwards.

Assembly owns only the batch concerns: the table, the section
numbering the table points at, dedupe, and the closing not found list.

One behavior is the runner's alone and is recorded in its module
docstring: the search endpoint answers an empty search with HTTP 404
and the usual search body carrying total_results 0 and an empty
organizations array (observed live on 2026-10-23 and proven by the
capture in `tools/tests/fixtures/propublica/search-empty-zxqv.json`).
The single fetcher fails closed on any non-200 and is unchanged; the
runner reads that one shape as an empty result, only for a search URL
whose body parses to exactly that shape, and prints the complete raw
response as the proof. Every other failure fails the whole run closed.

## Extending to company batches later

A company pack is the same assembly with the three pieces swapped,
nothing else changes:

* **Resolver**: the company fetcher's source of record does the
  resolution instead: for a carrier batch, FMCSA Licensing and
  Insurance or SAFER by USDOT number or exact legal name; for a public
  company batch, SEC EDGAR by CIK or exact registrant name. The
  discipline carries over unchanged: exact identity match or not
  resolved, never a near match; dedupe by the registry's key (USDOT
  number, CIK).
* **Per entity renderer**: the company fetcher's own delivery format
  renderer, built the way `carrier_fmcsa.py` and `sec_formd.py`
  already render single entities with excerpt proven claims.
* **Summary extractor**: the two or three registry native figures the
  buyer needs in the table (for carriers, say, operating status and
  power units; for Form D issuers, offering amount and amount sold),
  read from the same capture the section renders.

What does not exist yet, and a company pack issue would have to build
first: a company registry fetcher with the same capture and excerpt
machinery for whichever registry the batch runs against. The registry
fetchers in `tools/` today are single entity tools; the pack shape
above is designed so that adding one is a swap of the three pieces,
not a rewrite of the runner.
