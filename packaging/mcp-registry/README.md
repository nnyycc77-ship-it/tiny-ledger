# MCP Registry listing: recallcheck

This directory holds a ready to publish listing for the recallcheck MCP
server in the official MCP Registry
([registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/)),
so the server is discoverable outside the MCPize marketplace. The
registry hosts metadata only; the server keeps running where it runs
today, on MCPize.

- **Manifest:** [`server.json`](server.json), written against the
  registry schema at
  `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`
  (the current schema version on the registry site when this was built,
  2026-10-24).
- **Name:** `io.github.nnyycc77-ship-it/recallcheck`, the GitHub based
  namespace for this account.
- **Version:** `0.3.0`.
- **Remote:** one streamable HTTP remote,
  `https://recallcheck.mcpize.run/mcp`.
- **Repository:** `https://github.com/nnyycc77-ship-it/tiny-ledger`
  (source `github`, subfolder `mcp_server`, where the server code in
  this repo lives).

## The tool list

The server.json schema has no tools field, so the tool list is recorded
here. It matches the live server exactly, verified by H5 against the
live endpoint on 2026-10-24 (initialize and tools/list calls,
2026-10-24T07:11:50Z, no payment made): the server answered
`serverInfo` name `hojo-recall-check via MCPize`, version `0.3.0`, and
exactly these seven tools, in this order:

1. `recall_check`
2. `carrier_check`
3. `litigation_screen`
4. `formd_check`
5. `nonprofit_check`
6. `awards_search`
7. `pagespeed_snapshot`

The manifest description names the seven functions inside the
schema's 100 character description limit: "US public records checks:
recalls, carriers, litigation, Form D, nonprofits, awards, PageSpeed."
The same facts are recorded in the coordinator's earlier verification
on issue #123.

This listing carries no pricing and no wallet address. The registry
stores metadata, not payment terms; nothing in this directory sets or
changes any price.

## Validation

Run from the repository root, with the publisher CLI installed (step 1
below):

```sh
./mcp-publisher validate packaging/mcp-registry/server.json
```

**Recorded validation for this manifest (2026-10-24, by H5).** The
manifest passes an equivalent schema check against the registry's own
schema file, fetched from the registry site for this build:

```text
$ python3 -m jsonschema -i packaging/mcp-registry/server.json <the fetched schema file>
(no output, exit 0: valid)

$ python3, jsonschema Draft7Validator against the same schema file
SCHEMA VALIDATION: PASS
schema: https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
manifest name: io.github.nnyycc77-ship-it/recallcheck | version: 0.3.0 | description chars: 95
```

The publisher CLI's own `validate` (mcp-publisher 1.8.4, downloaded
from the registry project's releases for this build) was also run
twice from this build environment; both runs hung at
`Validating against https://registry.modelcontextprotocol.io...` past
110 seconds and were stopped, so its registry call does not complete
from here. That is an environment limit, recorded plainly: the schema
check above stands as the validation for this pull request, and step 2
of the publishing steps below has the owner run the CLI validate again
on a machine where the CLI can reach the registry, before publishing.

## Publishing

Everything up to the last step is prepared in this pull request. The
last step is the owner's own, because publishing under the
`io.github.nnyycc77-ship-it` namespace requires that GitHub account's
authentication, which only the account holder can give.

1. **Install the publisher CLI** (any machine the owner uses):

   ```sh
   brew install mcp-publisher
   ```

   or download the prebuilt binary from the registry project's
   releases, the form used to fetch version 1.8.4 for the validation
   above:

   ```sh
   curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
   ```

2. **Validate** (no authentication needed):

   ```sh
   ./mcp-publisher validate packaging/mcp-registry/server.json
   ```

3. **Owner step: log in and publish.** From the repository root, with
   this pull request merged:

   ```sh
   ./mcp-publisher login github
   ./mcp-publisher publish packaging/mcp-registry/server.json
   ```

   `login github` opens the GitHub device flow in the browser; sign in
   as `nnyycc77-ship-it` and enter the code the tool prints. `publish`
   then submits the manifest under that namespace. No other step is
   needed, and nobody else can do this step: a different GitHub
   account cannot publish under this namespace.

4. **Verify the listing** after publishing, with the registry API:

   ```sh
   curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.nnyycc77-ship-it/recallcheck"
   ```

   Before publishing, that search returns an empty `servers` list
   (checked 2026-10-24). After publishing it returns this server's
   metadata.

## Updating the listing later

When the server's version or tool list changes (a redeploy is an owner
step on MCPize, as before), update `version` in `server.json` and the
tool list above to match the live server, revalidate, and repeat the
owner publish step. A version already published cannot be edited in
place; publish the new version as a new listing version.
