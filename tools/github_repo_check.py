#!/usr/bin/env python3
"""GitHub repository check (issue #166, tool factory wave 1).

Given an owner and a repository name, reads GitHub's public REST API once,
keyless, and prints one Markdown report in the delivery format from
AGENT-BRIEF.md: the stars, the license, the last push date and whether the
repository is archived, each as shown, with those fields cut verbatim from
the response beneath the claims and the complete raw response beneath the
source link.

    python3 tools/github_repo_check.py psf requests

Source: GET https://api.github.com/repos/{owner}/{repo}, the "Get a
repository" endpoint of GitHub's REST API. No Authorization header is ever
sent and no token is read from anywhere. GitHub's rate limit page, quoted
on issue #166: "You can make unauthenticated requests if you are only
fetching public data. ... The primary rate limit for unauthenticated
requests is 60 requests per hour." The x-ratelimit-* response headers are
printed as returned, so the limit the call ran under is visible. If the
answer carries a limit other than 60, the report says the request may have
been authenticated on the way (an intermediary can add credentials), so the
result is not proven keyless.

Fields printed: stargazers_count, license (with its name and spdx_id) and
archived are documented in the "Get a repository" example response quoted
on issue #166; pushed_at is not in that excerpt and is read from the
captured responses, which all carry it (the coordinator's keyless
captures, issue #166). Each is printed as shown; nothing is computed.

Outcomes: 200 is a report. 404 is a report too, of no public repository at
that name visible without authentication (it may not exist, or may be
private), with the raw response as the proof. A rate limit answer (403 or
429), any other status, a failed request, or a body that is not the
documented shape stops the run with exit 2 and no report: a rate limit is
never shown as not found.

Standard library only.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import Node, fenced, skip_ws  # noqa: E402

API_URL = "https://api.github.com/repos/{owner}/{repo}"
HOST = "api.github.com"
USER_AGENT = "tiny-ledger-github-repo-check"
TIMEOUT_SECONDS = 30
UNAUTHENTICATED_LIMIT = "60"
NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
FIELDS = ("stargazers_count", "license", "pushed_at", "archived")
RATE_HEADERS = ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-used", "x-ratelimit-reset",
                "x-ratelimit-resource")
OBSERVATION = ("Observation only: this report records what GitHub's public REST API returned for this "
               "repository at the retrieval time stated below, without authentication.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, final_url, retrieved, status, status_line, headers, body):
        self.url = url
        self.final_url = final_url
        self.retrieved = retrieved
        self.status = status
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def header(self, name):
        for k, v in self.headers:
            if k.lower() == name.lower():
                return v
        return None

    def transcript(self):
        return "\n".join([self.status_line] + ["%s: %s" % kv for kv in self.headers] + ["", self.body])


def check_name(value, what):
    text = (value or "").strip()
    if not NAME_RE.match(text) or text in (".", ".."):
        raise ValueError("%s must be letters, digits, '.', '_' or '-' (got %r)" % (what, value))
    return text


def repo_url(owner, repo):
    return API_URL.format(owner=urllib.parse.quote(owner, safe=""), repo=urllib.parse.quote(repo, safe=""))


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200 and 404; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    if request.has_header("Authorization"):  # never: this tool sends no credentials
        raise FetchError("refusing to send an Authorization header")
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if urllib.parse.urlsplit(final_url).netloc != HOST:
        raise FetchError("%s was redirected off %s; no report" % (url, HOST))
    capture = Capture(url, final_url, retrieved, status, status_line, headers, body)
    if status in (403, 429):
        raise FetchError("%s answered %s, a refusal or rate limit (x-ratelimit-remaining %s); no report, "
                         "and this is not a not found" % (url, status_line, capture.header("x-ratelimit-remaining")))
    if status not in (200, 404):
        raise FetchError("%s answered %s; no report" % (url, status_line))
    return capture


def rate_lines(capture):
    shown = [(k, v) for k, v in capture.headers if k.lower() in RATE_HEADERS]
    lines = ["Rate limit headers as returned (x-ratelimit-reset is UTC epoch seconds, per GitHub's docs):",
             fenced("\n".join("%s: %s" % kv for kv in shown) if shown else "(none returned)")]
    limit = capture.header("x-ratelimit-limit")
    if limit != UNAUTHENTICATED_LIMIT:
        lines += ["", "Note: this answer's x-ratelimit-limit is %s, not the unauthenticated %s. The tool sent no "
                  "credentials, but something on the way may have authenticated the request, so this result "
                  "is not proven keyless." % (limit or "absent", UNAUTHENTICATED_LIMIT)]
    return lines


def render(owner, repo, capture):
    """The report lines. Raises FetchError when a 200 body is not the documented shape."""
    full = "%s/%s" % (owner, repo)
    lines = ["# GitHub repository check: %s" % full, "", OBSERVATION, "",
             "Exact query: GET %s" % capture.url,
             "Sent with no Authorization header (keyless).",
             "Retrieved (UTC): %s" % capture.retrieved]
    if capture.final_url != capture.url:
        lines.append("Answered from: %s (GitHub redirected the request)" % capture.final_url)
    lines += [""] + rate_lines(capture) + [""]
    if capture.status == 404:
        lines += ["GitHub answered %s: there is no public repository at %s visible without authentication. "
                  "It may not exist, or it may be private; the response below is the proof."
                  % (capture.status_line, full), "",
                  "Source: <%s>" % capture.url, fenced(capture.transcript())]
        return lines
    try:
        node = Node(capture.body, skip_ws(capture.body, 0))
        missing = [f for f in FIELDS if not node.has(f)]
        if missing:
            raise ValueError("missing %s" % ", ".join(missing))
        stars, archived, pushed = node.value("stargazers_count"), node.value("archived"), node.value("pushed_at")
        lic = node.value("license")
        shown_name = node.value("full_name") if node.has("full_name") else full
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented repository shape (%s); no report"
                         % (capture.url, err))
    if lic is None:
        license_line = "none: the response's license is null (GitHub detected no license)"
    elif isinstance(lic, dict):
        license_line = "%s (spdx_id %s)" % (lic.get("name"), lic.get("spdx_id"))
    else:
        raise FetchError("%s answered a license that is neither an object nor null; no report" % capture.url)
    lines += ["Repository as shown (full_name): %s" % shown_name, "",
              "- Stars as shown (stargazers_count): %s" % json.dumps(stars),
              "- License as shown: %s" % license_line,
              "- Last push as shown (pushed_at): %s" % (pushed if pushed is not None else "null"),
              "- Archived as shown: %s" % json.dumps(archived), "",
              "Those fields, verbatim from the response:",
              fenced("\n".join(node.excerpt(f) for f in FIELDS)), "",
              "Source: <%s>" % capture.url, fenced(capture.transcript())]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Keyless GitHub repository check: stars, license, last push, archived.")
    p.add_argument("owner")
    p.add_argument("repo")
    args = p.parse_args(argv)
    try:
        owner, repo = check_name(args.owner, "owner"), check_name(args.repo, "repo")
        capture = (fetcher or fetch)(repo_url(owner, repo))
        lines = render(owner, repo, capture)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
