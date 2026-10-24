"""Tests for tools/github_repo_check.py and its GET /github route (issue #166). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_github_repo_check.py' -v

Fixtures (fixtures/github-repo/, recorded in provenance.json): the
coordinator's keyless captures on issue #166, each response as its header
block and its body, verbatim; every body's SHA-256 matches the one posted.
Variants built here from those responses say DERIVED where they are built.
Every test runs with urlopen replaced by a function that fails the test,
except the fetch tests, which replace it with a recorder.
"""

import hashlib
import io
import json
import re
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import github_repo_check as g  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "github-repo"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
CASES = {"psf/requests": "psf-requests", "atom/atom": "atom-atom",
         "octocat/Hello-World": "octocat-hello-world", "zqxflorp/no-such-repo-xyz123": "missing-404"}


def captured(name, module=g, change_headers=None):
    block = (FIX / ("%s.headers" % name)).read_text(encoding="utf-8").split("\n")
    status_line, headers = block[0], [tuple(line.split(": ", 1)) for line in block[1:] if line]
    if change_headers:
        headers = change_headers(headers)
    status = int(re.findall(r" (\d{3}) ", status_line + " ")[0])
    url = PROV["%s.body" % name]["url"]
    return module.Capture(url, url, "2026-10-24T02:36:00Z", status, status_line, headers,
                          (FIX / ("%s.body" % name)).read_text(encoding="utf-8"))


def replay(module=g, **kw):
    def fetcher(url):
        for full, name in CASES.items():
            if url == module.repo_url(*full.split("/")):
                return captured(name, module, **kw)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("github_repo_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = g.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_and_every_capture_is_keyless(self):
        # Body sha256 values exactly as the coordinator posted them on issue #166.
        posted_sha256 = {
            "psf-requests body sha256": "cc0f273af19d8c6315194540eb6af00bb8d92d678c9dbd4ed1ede725db85d44f",
            "atom-atom body sha256": "378b9ca730a125c94097eec8d9d32c2cc628ed198c348eade651fa1e0ef640b0",
            "octocat-hello-world body sha256": "8f1ef395bd00e759e37531c7f6a4d86683cb2c48d698f99a2fc780e86b86dba0",
            "missing-404 body sha256": "a298fd3d1a255b0eb21a952212460852e05ba9721d3445fb42d7ad054d88f94a",
        }
        for key, sha in posted_sha256.items():
            name = key.replace(" body sha256", "")
            for ext in ("headers", "body"):
                data = (FIX / ("%s.%s" % (name, ext))).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), PROV["%s.%s" % (name, ext)]["sha256"])
            self.assertEqual(PROV["%s.body" % name]["sha256"], sha)
            self.assertIn("X-RateLimit-Limit: 60", (FIX / ("%s.headers" % name)).read_text(encoding="utf-8"))


class ReportTests(unittest.TestCase):
    def test_licensed_archived_repo(self):
        code, out, err = run(["atom", "atom"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("- Stars as shown (stargazers_count): 60710", out)
        self.assertIn("- License as shown: MIT License (spdx_id MIT)", out)
        self.assertIn("- Last push as shown (pushed_at): 2023-01-03T10:49:48Z", out)
        self.assertIn("- Archived as shown: true", out)
        self.assertIn('"stargazers_count": 60710', out)
        self.assertIn('"archived": true', out)
        self.assertIn('"pushed_at": "2023-01-03T10:49:48Z"', out)
        self.assertIn((FIX / "atom-atom.body").read_text(encoding="utf-8"), out)
        self.assertIn("Sent with no Authorization header (keyless).", out)
        self.assertIn("X-RateLimit-Limit: 60\nX-RateLimit-Remaining: 47", out)
        self.assertNotIn("not proven keyless", out)

    def test_licensed_live_repo(self):
        _, out, _ = run(["psf", "requests"])
        self.assertIn("- Stars as shown (stargazers_count): 54635", out)
        self.assertIn("- License as shown: Apache License 2.0 (spdx_id Apache-2.0)", out)
        self.assertIn("- Last push as shown (pushed_at): 2026-09-28T16:55:48Z", out)
        self.assertIn("- Archived as shown: false", out)

    def test_no_license_and_not_archived(self):
        _, out, _ = run(["octocat", "Hello-World"])
        self.assertIn("- Archived as shown: false", out)
        self.assertIn("- License as shown: none: the response's license is null (GitHub detected no license)", out)
        self.assertIn('"license": null', out)

    def test_404_is_a_report_with_its_raw_response(self):
        code, out, _ = run(["zqxflorp", "no-such-repo-xyz123"])
        self.assertEqual(code, 0)
        self.assertIn("there is no public repository at zqxflorp/no-such-repo-xyz123 visible without authentication",
                      out)
        self.assertIn('"message": "Not Found"', out)
        self.assertNotIn("Stars as shown", out)

    def test_a_limit_other_than_60_is_flagged_as_not_proven_keyless(self):
        # DERIVED: the real atom/atom capture with only X-RateLimit-Limit changed.
        change = lambda hs: [(k, "15000" if k == "X-RateLimit-Limit" else v) for k, v in hs]
        _, out, _ = run(["atom", "atom"], replay(change_headers=change))
        self.assertIn("x-ratelimit-limit is 15000, not the unauthenticated 60", out)
        self.assertIn("is not proven keyless", out)

    def test_a_body_not_in_the_documented_shape_is_refused(self):
        def wrong(url):
            cap = captured("atom-atom")
            cap.body = cap.body.replace('"archived"', '"archived_x"')  # DERIVED
            return cap
        code, out, err = run(["atom", "atom"], wrong)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("not the documented repository shape", err)


class FetchTests(unittest.TestCase):
    class Answer:
        def __init__(self, status, body, url, headers=()):
            self.status, self.code, self.reason = status, status, {200: "OK", 404: "Not Found"}.get(status, "X")
            self._body, self._url, self.headers = body, url, dict(headers)
            self.version = 11

        def read(self):
            return self._body

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def test_no_authorization_header_is_ever_sent(self):
        sent = []

        def fake(request, timeout=None):
            sent.append(dict(request.header_items()))
            return self.Answer(200, (FIX / "atom-atom.body").read_bytes(), request.full_url,
                               {"X-RateLimit-Limit": "60"})
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "placeholder-not-a-token"}), \
                mock.patch("urllib.request.urlopen", fake):
            cap = g.fetch(g.repo_url("psf", "requests"))
        self.assertEqual(cap.status, 200)
        self.assertEqual(len(sent), 1)
        self.assertNotIn("Authorization", sent[0])
        self.assertNotIn("placeholder-not-a-token", json.dumps(sent))

    def test_rate_limit_and_other_statuses_fail_closed(self):
        for status in (403, 429, 500, 301):
            def fake(request, timeout=None, status=status):
                if status in (403, 429, 500):
                    raise urllib.error.HTTPError(request.full_url, status, "X", {"x-ratelimit-remaining": "0"},
                                                 io.BytesIO(b'{"message":"SYNTHETIC"}'))
                return self.Answer(status, b"{}", request.full_url)
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(g.FetchError, msg=status) as ctx:
                    g.fetch(g.repo_url("psf", "requests"))
            if status in (403, 429):
                self.assertIn("this is not a not found", str(ctx.exception))

    def test_a_redirect_off_the_api_host_is_refused(self):
        def fake(request, timeout=None):
            return self.Answer(200, b"{}", "https://example.invalid/elsewhere")
        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(g.FetchError):
                g.fetch(g.repo_url("psf", "requests"))

    def test_bad_names_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for owner, repo in (("psf/x", "requests"), ("", "requests"), ("psf", ".."), ("psf", "a b"), ("psf", "x?y")):
            self.assertEqual(run([owner, repo], must_not)[0], 2, (owner, repo))


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.github_repo_check, its own module object.
        with mock.patch.object(endpoints.gh, "fetch", replay(endpoints.gh)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/github", qs, None)

    def test_route(self):
        status, _, body = self.get("owner=atom&repo=atom")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("- Archived as shown: true", text)
        self.assertEqual(self.get("owner=zqxflorp&repo=no-such-repo-xyz123")[0], "200 OK")
        self.assertEqual(self.get("owner=psf")[0], "400 Bad Request")
        self.assertEqual(self.get("owner=psf/x&repo=y")[0], "400 Bad Request")
        self.assertEqual(endpoints.describe()["/github"]["sources"], [g.API_URL])

    def test_route_maps_a_refusal_to_502(self):
        def refused(url):
            raise endpoints.gh.FetchError("SYNTHETIC 403 rate limit; no report")
        with mock.patch.object(endpoints.gh, "fetch", refused):
            self.assertEqual(recall_api.handle("GET", "/github", "owner=psf&repo=requests", None)[0], "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
