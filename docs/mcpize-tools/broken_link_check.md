# `broken_link_check`: broken link check

A tool factory wave 1 tool (issue #164, parent #158). The fetcher is
[`tools/broken_link_check.py`](../../tools/broken_link_check.py), and it is served as
`GET /links` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is not on the MCP server yet. Every wave 1 tool that passes review is
registered on the server in one shared surface PR at the end of the wave
(coordinator ruling on issue #158), and going live is one owner redeploy
step after that.

- **What it answers:** Which links on one page are dead. The page is fetched once, every link on it is checked once, and the dead ones are listed with their status codes, beside every checked link with the status line it answered.
- **Source:** The page itself, and then each link target on it. There is no API behind this tool. Links are the href targets of `<a>`, `<area>` and `<link>` elements, resolved against the page's final URL with fragments removed; duplicates are checked once and counted. A page `<base>` element is not applied. Outbound HTTPS (or HTTP, when the page or a target uses it) to the page's host and to each target's host. Keyless.
- **Arguments:** `url` (the page URL, http or https).
- **Needs on the server:** Outbound HTTP and HTTPS. No key, no environment value.
- **What counts as dead:** A final status of 400 or above, after redirects; the status line printed is the final answer's, with the final URL named when a redirect moved it. A link whose request itself fails is listed as a check failure with the error, never as dead. Same page anchors, non HTTP links (mailto:, tel:, and the like), and unique targets past the cap of 100 checked per page are listed as not fetched or not checked, so every link on the page is accounted for.
- **What it is not:** A crawl. Only the one page named is read; links are checked, never followed into a second page of links. A status is the server's answer at the retrieval moment; a target that answers later may answer differently.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. The claim lines sit
with the source link, the complete raw response of the page is printed
verbatim directly beneath it, and the exact query and retrieval time are
recorded. Each checked link's evidence is the status line it answered,
printed beside its URL. A page with no links is proven by its complete
raw response, never asserted. A page that fails to fetch, or answers
other than 200, is an error (exit 2, and 502 on the API route) with no
report: a failed fetch is never an empty result.

## What a report shows, on recorded responses

All recorded responses are in
[`tools/tests/fixtures/broken-links/`](../../tools/tests/fixtures/broken-links/),
with their provenance. The link target responses are real captures; the
page that carries them is synthetic, a small page body written for the
tests so the link set is stable, and it is labelled synthetic in its own
body and in the provenance file. The tool's lines for that page:

- `LINKS: 7 link(s) on the page; 3 unique HTTP target(s) checked, 1 same page anchor(s) not fetched, 1 non HTTP link(s) not fetched, 0 target(s) past the cap of 100 not checked.`
- `Dead links (final status 400 or above): 1`
- `- https://example.com/no-such-page-broken-link-check -> HTTP/1.1 404 Not Found`

The other outcomes, on the same recorded responses:

- **A page with no links** (a real capture, the robots.txt at iana.org): `LINKS: 0 link(s) on the page`, a dead count of 0, and the complete raw page response beneath the source link as the proof.
- **A link whose request fails:** listed under check failures with the error, and the dead count does not move.
- **A page that answers 404, or does not answer at all:** no report; the run stops with the status or the error on stderr.

## Live smoke run

One live run from the build environment, retrieved 2026-10-24 about
04:56 UTC: `python3 tools/broken_link_check.py https://www.iana.org/domains/example`
answered from `http://www.iana.org/help/example-domains` after a
redirect, with `LINKS: 33 link(s) on the page; 28 unique HTTP target(s)
checked` and `Dead links (final status 400 or above): 0`. The full
output of this run is quoted in the pull request for issue #164.
