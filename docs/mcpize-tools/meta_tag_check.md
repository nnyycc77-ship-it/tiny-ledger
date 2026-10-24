# `meta_tag_check`: meta tag check

A tool factory wave 1 tool (issue #165, parent #158).
- **Code:** the fetcher is
  [`tools/meta_tag_check.py`](../../tools/meta_tag_check.py). The pay per
  call API serves it as `GET /meta?url=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Registered on the MCP server.** The server on main lists it
  (`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
  PR #208 (issue #204), the shared surface step the #158 ruling called for.
  Going live still waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** for one web page, whether its title, its meta
  description and its checked Open Graph tags are present or missing,
  with the values exactly as the page prints them. Built for publisher
  audits: a page that shares badly usually has a missing tag, and this
  tool shows which one.
- **Source:** the page itself, at the exact URL given.
  - **Keyless.** There is no API and no key. The page is fetched once,
    with the standard library only, and no credentials of any kind are
    sent.
  - **Redirects** are followed the way a browser follows them, and the
    URL that finally answered is printed in the report.
- **Arguments:** `url`, one http or https page URL.
- **Needs on the server:** outbound HTTP or HTTPS to the page the caller
  names, and no key.
- **The checked tags:**
  - the `<title>` element;
  - the meta description, `<meta name="description">`;
  - the Open Graph tags `og:title`, `og:type`, `og:url`, `og:image` and
    `og:description`, the basic set named by the Open Graph protocol
    (https://ogp.me/). Any further `og:*` tags the page carries are
    listed as also present, in the order printed.
- **What it is not:** a judgement of the page, its wording, or its
  images. It reports what the page's own HTML carries, nothing more. A
  tag can be present and still wrong for the page; that call is the
  reader's.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The request.** The exact query and the UTC retrieval time, and the
  URL that finally answered when the request was redirected.
- **The claims.** Each checked tag marked present, with its value as
  shown, or missing. A `<title>` element with no text counts as missing,
  and so does a first tag of a kind when the page prints it twice: the
  first one printed is the one reported.
- **The evidence.** The head of the page cut verbatim, and then the
  complete raw response (status line, headers as returned, and the body
  exactly as received) under the source link.

**Empty result:** a page where every checked tag is missing is a
report, not an error. The missing lines are the claim, the report says
plainly that none of the checked tags are present, and the complete raw
response beneath the source link is the proof.

**Failures:** these give no report, with exit 2 on the CLI and 502 on
the API:
- a failed request;
- a status other than 200;
- an answer whose Content-Type is not HTML;
- a body that cannot be decoded with the charset the answer declared;
- a body over the 5,000,000 byte cap.

A source failure is never shown as a page with no tags.

## Running it

```sh
python3 tools/meta_tag_check.py https://ogp.me/
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_meta_tag_check.py' -v
```

The tests run offline:
- **Fixtures:** three live captures taken with this tool's own fetch
  path on 2026-10-24, verbatim in `tools/tests/fixtures/meta-tags/` with
  their hashes in `provenance.json`: ogp.me (title, description and Open
  Graph tags present), example.com (title only), and httpbin.org/html
  (every checked tag missing, proven by its full raw response).
- **Failure shapes** are covered offline: a non HTML answer is refused
  rather than reported as an empty page, and mocked HTTP error,
  transport failure and non 200 answers all fail closed.
- **Live smoke run:** one live run is recorded in the PR description,
  with its retrieval time.
