# `github_repo_check`: GitHub repository check

A tool factory wave 1 tool (issue #166, parent #158).
- **Code:** the fetcher is
  [`tools/github_repo_check.py`](../../tools/github_repo_check.py). The pay
  per call API serves it as `GET /github?owner=...&repo=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Registered on the MCP server.** The server on main lists it
  (`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
  PR #208 (issue #204), the shared surface step the #158 ruling called for.
  Going live still waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** for one public repository, its stars, its license,
  its last push date, and whether it is archived. Each is shown exactly as
  GitHub's REST API returns it.
- **Source:** GitHub REST API, "Get a repository",
  `GET https://api.github.com/repos/{owner}/{repo}`.
  - **Keyless.** No Authorization header is ever sent, and no token is
    read from anywhere.
  - **The limit.** GitHub's rate limit page, as quoted on #166: "The
    primary rate limit for unauthenticated requests is 60 requests per
    hour."
- **Arguments:** `owner` and `repo`. Each may contain letters, digits,
  `.`, `_` and `-`.
- **Needs on the server:** outbound HTTPS to `api.github.com`, and no
  key.
  - **Shared limit.** The 60 per hour limit belongs to the server's IP
    address, so heavy use shares it.
  - **The keyless check.** Every report prints the `x-ratelimit-*`
    headers as returned. If the limit shown is not 60, the report says
    something on the way may have authenticated the request, so the
    result is not proven keyless. This is why the build environment,
    whose proxy adds credentials, never produced evidence for this tool.
- **What it is not:** an audit of the code, the license terms, or the
  maintainers. "Archived" and "license" mean what GitHub reports. A null
  license means GitHub detected none, not that the code is unlicensed.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The request.** The exact query, a note that it was sent keyless, the
  UTC retrieval time, and the rate limit headers.
- **The four claims.** Each is marked "as shown":
  - `stargazers_count`;
  - `license`, its name and `spdx_id`, or null;
  - `pushed_at`;
  - `archived`.
- **The evidence.** Those four fields cut verbatim from the response, and
  then the complete raw response under the source link.
- **Where the field names come from.** `stargazers_count`, `license` and
  `archived` are in the "Get a repository" example response quoted on
  #166. `pushed_at` is read from the captured keyless responses, which all
  carry it.

**404:** GitHub's 404 is reported as "no public repository at that name
visible without authentication", because it may not exist or may be
private. The raw response is the proof.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API:
- a rate limit answer (403 or 429);
- any other status;
- a redirect off `api.github.com`;
- a failed request;
- a body without the documented fields.

A rate limit is never shown as not found.

## Running it

```sh
python3 tools/github_repo_check.py psf requests
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_github_repo_check.py' -v
```

The tests run offline:
- **Fixtures:** the coordinator's four keyless captures from #166, verbatim
  in `tools/tests/fixtures/github-repo/` with their hashes: a licensed repo,
  an archived repo, a repo with no license, and a 404.
- **Coordinator live run:** the coordinator's keyless live smoke run is
  owed at review.
