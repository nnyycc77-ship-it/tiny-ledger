"""Drift check for the MCP Registry listing (issue #246).

Offline only: no network. The MCP Registry listing added by issue #186
lives at packaging/mcp-registry/server.json (the merged PR #203 placed
it there, not at the repo root). Nothing else in the suite pinned it, so
this test parses server.json independently and compares the values it
carries against their sources in the repo, with every disagreement
naming the disagreeing sources.

Values carried by server.json that ARE pinned here:

- `version` against SERVER_VERSION in mcp_server/recall_mcp.py;
- `name`: its last segment (the server slug) against the slug in
  mcpize.yaml, and its owner segment against the owner named in the
  listing's own `repository.url`;
- `remotes[0].url` against the hosted endpoint the runbook names in
  docs/mcpize-redeploy-runbook.md ("**Endpoint:** ...");
- `websiteUrl` against the marketplace listing page URL the runbook
  names in the same section;
- `repository.subfolder` names a directory that exists in this repo
  and holds the server code (recall_mcp.py).

Values carried by server.json that are NOT pinned, because no source in
the repo states them in a comparable form: `$schema` (the registry's
own schema URL), `description` and `title` (listing copy with no
verbatim source in the repo), `remotes[0].type`, and the `repository`
block's `id`, `source`, and `url` beyond the owner segment used above.
Nothing is invented for them; they are listed here so the gap is
explicit, in the open, and reviewed.

The comparison lives in disagreements() so the mutation tests below can
feed it drifted inputs: every drift case is SYNTHETIC, built in this
file, and each asserts the returned message names the sources.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_server import recall_mcp  # noqa: E402

LISTING = ROOT / "packaging" / "mcp-registry" / "server.json"
RUNBOOK = ROOT / "docs" / "mcpize-redeploy-runbook.md"
MCPIZE_YAML = ROOT / "mcpize.yaml"


def load_listing():
    return json.loads(LISTING.read_text(encoding="utf-8"))


def yaml_slug():
    match = re.search(r'^slug:\s*"([^"]+)"', MCPIZE_YAML.read_text(encoding="utf-8"),
                      re.MULTILINE)
    return match.group(1) if match else None


def runbook_urls():
    text = RUNBOOK.read_text(encoding="utf-8")
    endpoint = re.search(r"\*\*Endpoint:\*\* `([^`]+)`", text)
    listing = re.search(r"`(https://mcpize\.com/mcp/[a-z0-9-]+)`, named in PR #45", text)
    return (endpoint.group(1) if endpoint else None,
            listing.group(1) if listing else None)


def disagreements(listing, server_version, slug, endpoint, listing_url):
    """One message per drift, each naming the disagreeing sources."""
    out = []
    if listing.get("version") != server_version:
        out.append("server.json vs mcp_server/recall_mcp.py: listing version "
                   "%r != SERVER_VERSION %r"
                   % (listing.get("version"), server_version))
    name = listing.get("name") or ""
    owner, _, last = name.partition("/")
    owner = owner.rsplit(".", 1)[-1] if "." in owner else owner
    repo_url = (listing.get("repository") or {}).get("url") or ""
    repo_owner = repo_url.rstrip("/").split("/")[-2] if "/" in repo_url else None
    if owner != repo_owner:
        out.append("server.json vs server.json repository.url: listing name "
                   "owner %r != repository owner %r" % (owner, repo_owner))
    if last != slug:
        out.append("server.json vs mcpize.yaml: listing name slug %r != "
                   "the slug %r" % (last, slug))
    remotes = listing.get("remotes") or []
    remote_url = remotes[0].get("url") if remotes else None
    if remote_url != endpoint:
        out.append("server.json vs docs/mcpize-redeploy-runbook.md: remote "
                   "url %r != the endpoint the runbook names %r"
                   % (remote_url, endpoint))
    if listing.get("websiteUrl") != listing_url:
        out.append("server.json vs docs/mcpize-redeploy-runbook.md: "
                   "websiteUrl %r != the listing page the runbook names %r"
                   % (listing.get("websiteUrl"), listing_url))
    return out


class RealSourcesAgreeTests(unittest.TestCase):
    def test_listing_agrees_with_its_sources(self):
        endpoint, listing_url = runbook_urls()
        found = disagreements(load_listing(), recall_mcp.SERVER_VERSION,
                              yaml_slug(), endpoint, listing_url)
        self.assertEqual(found, [],
                         "drift detected: " + "; ".join(found))

    def test_repository_subfolder_holds_the_server_code(self):
        listing = load_listing()
        subfolder = (listing.get("repository") or {}).get("subfolder")
        self.assertTrue(subfolder, "the listing carries no repository subfolder")
        self.assertTrue((ROOT / subfolder / "recall_mcp.py").is_file(),
                        "repository subfolder %r does not hold recall_mcp.py"
                        % subfolder)


class MutationTests(unittest.TestCase):
    """SYNTHETIC drift, fed to the same comparison the real test uses.
    Each case must be caught and must name the disagreeing sources."""

    def setUp(self):
        self.listing = load_listing()
        self.endpoint, self.listing_url = runbook_urls()

    def check(self, listing):
        return disagreements(listing, recall_mcp.SERVER_VERSION, yaml_slug(),
                             self.endpoint, self.listing_url)

    def test_drifted_version_names_the_server_source(self):
        drifted = dict(self.listing)
        drifted["version"] = "0.4.0"  # synthetic
        found = self.check(drifted)
        self.assertTrue(any(m.startswith("server.json vs mcp_server/recall_mcp.py")
                            for m in found), found)

    def test_drifted_name_names_mcpize_yaml(self):
        drifted = dict(self.listing)
        drifted["name"] = "io.github.nnyycc77-ship-it/othercheck"  # synthetic
        found = self.check(drifted)
        self.assertTrue(any(m.startswith("server.json vs mcpize.yaml")
                            for m in found), found)

    def test_drifted_remote_names_the_runbook(self):
        drifted = dict(self.listing)
        drifted["remotes"] = [{"type": "streamable-http",
                               "url": "https://synthetic.invalid/mcp"}]
        found = self.check(drifted)
        self.assertTrue(any(m.startswith("server.json vs docs/mcpize-redeploy-runbook.md")
                            for m in found), found)


if __name__ == "__main__":
    unittest.main()
