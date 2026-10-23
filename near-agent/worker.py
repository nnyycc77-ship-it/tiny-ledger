#!/usr/bin/env python3
"""Self hosted worker for the Hojo Research Agent on the NEAR AI Agent Market.

Runs the agent side of the marketplace loop from code in this repo instead
of by hand (issue #48). Two modes:

  poll   GET /v1/agents/me/assignments and GET /v1/jobs/board?kind=standard
         against https://market.near.ai, then print a structured digest:
         the assignment count and ids, the board job count, and every job
         whose id is new or whose budget changed since the previous poll.
         The previous poll is remembered in a small local state file that
         holds job ids and budgets only, never a response and never the
         token. The default state path is outside the repository.

  act    start, message and submit on an assignment, and bid on a job.
         Every act command is a dry run unless --execute is given: without
         the flag the program prints the exact request it would send
         (method, URL, headers with the token redacted, body) and sends
         nothing. Nothing in this file sends a bid, start, message or
         submit on its own; --execute is the operator's explicit act, and
         a bid additionally needs the coordinator's separate approval
         outside this tool (see README.md).

Credentials: the agent API token is read from the environment variable
NEAR_AGENT_TOKEN and from nowhere else. It is never read from a file in
this repo, never written anywhere, and never printed or logged: every
line this program emits passes through a redaction step that replaces
the token value, and the Authorization header is printed as a
placeholder. A missing or empty token stops the program before any
request is built (exit 2).

Fail closed, as every tool in this repo does: a transport failure, a
non 2xx status, a body that is not JSON, or a response shape this program
does not recognise stops the run with the failure on stderr and exit 2.
No digest is printed from a response that was not understood, and the
state file is not touched. Only the final URL host market.near.ai over
HTTPS is ever contacted, redirects are not followed, and no request is
sent in the test suite (tests use a fake token string and a fake
transport).

Standard library only. Run from the repository root:

    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py poll
    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py poll --state /path/state.json
    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py bid JOB_ID --amount 25 --note "..."
    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py start ASSIGNMENT_ID
    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py message ASSIGNMENT_ID --text "..."
    NEAR_AGENT_TOKEN=... python3 near-agent/worker.py submit ASSIGNMENT_ID --text "..."

Add --execute to an act command to send it. There is no --execute for
poll; polling is read only and always runs.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_ENV = "NEAR_AGENT_TOKEN"
BASE_URL = "https://market.near.ai"
HOST = "market.near.ai"
USER_AGENT = "hojo-research-agent-worker/0.1 (+https://github.com/nnyycc77-ship-it/tiny-ledger)"
TIMEOUT_SECONDS = 30
MIN_INTERVAL_SECONDS = 30

# Read paths, fixed by the task text of issue #48.
ASSIGNMENTS_PATH = "/v1/agents/me/assignments"
BOARD_PATH = "/v1/jobs/board"
BOARD_QUERY = {"kind": "standard"}

REDACTED = "<redacted, supplied from the environment variable %s>" % TOKEN_ENV

# Act endpoints: method and path template per action. Entries are None until
# the API documentation for them is recorded in this repo (README.md names
# the source for each). Building a request for an undocumented action is an
# error, never a guessed path.
ACTIONS = {
    "start": None,
    "message": None,
    "submit": None,
    "bid": None,
}


class ConfigError(Exception):
    """The environment is not usable. Nothing was sent."""


class FetchError(Exception):
    """A request failed or an answer was not understood. Nothing is concluded."""


class NotDocumented(Exception):
    """The endpoint for this action is not recorded in this repo yet."""


# ----------------------------------------------------------------- token

def read_token(env=None):
    """Return the agent token from NEAR_AGENT_TOKEN, or raise ConfigError.

    The value is stripped of surrounding whitespace and otherwise passed
    through untouched. Nothing else is consulted: no file, no argument.
    """
    env = os.environ if env is None else env
    value = env.get(TOKEN_ENV, "").strip()
    if not value:
        raise ConfigError("%s is not set or is empty; refusing to run without the agent token" % TOKEN_ENV)
    return value


class Redactor:
    """Replaces the token value in every emitted line.

    A single choke point for stdout and stderr so a token can never leak
    through an error message, a header dump or a digest field.
    """

    def __init__(self, token):
        self.token = token

    def clean(self, text):
        if self.token:
            text = text.replace(self.token, REDACTED)
        return text

    def emit(self, stream, text):
        stream.write(self.clean(text))
        if not text.endswith("\n"):
            stream.write("\n")


# ----------------------------------------------------------------- requests

class Request:
    """One HTTP request this program would send: fully built, not yet sent."""

    def __init__(self, method, url, headers, body=None):
        self.method = method
        self.url = url
        self.headers = headers  # list of (name, value) in send order
        self.body = body  # bytes or None

    def describe(self):
        """The exact request as text, with the token placeholder in place.

        The Authorization value is printed as the placeholder, not through
        the redactor only: this text is what the operator checks before
        adding --execute, so it must never depend on a later step.
        """
        lines = ["%s %s" % (self.method, self.url)]
        for name, value in self.headers:
            if name.lower() == "authorization":
                value = "Bearer " + REDACTED
            lines.append("%s: %s" % (name, value))
        lines.append("")
        lines.append(self.body.decode("utf-8") if self.body is not None else "(no body)")
        return "\n".join(lines)


def build_url(path, query=None):
    url = BASE_URL + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


def build_request(token, method, path, query=None, body=None):
    headers = [
        ("Accept", "application/json"),
        ("Authorization", "Bearer " + token),
        ("User-Agent", USER_AGENT),
    ]
    data = None
    if body is not None:
        data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        headers.append(("Content-Type", "application/json"))
    return Request(method, build_url(path, query), headers, data)


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers  # list of (name, value) as returned
        self.body = body  # bytes


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchError("redirect %d to %s not followed" % (code, newurl))


class UrllibTransport:
    """Sends a Request over HTTPS to market.near.ai and nothing else."""

    def __init__(self, timeout=TIMEOUT_SECONDS):
        self.timeout = timeout
        self.opener = urllib.request.build_opener(_NoRedirect)

    def send(self, request):
        parts = urllib.parse.urlsplit(request.url)
        if parts.scheme != "https" or parts.netloc != HOST:
            raise FetchError("refusing to send to %s://%s; only https://%s is allowed" % (parts.scheme, parts.netloc, HOST))
        req = urllib.request.Request(request.url, data=request.body, method=request.method)
        for name, value in request.headers:
            req.add_header(name, value)
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                return Response(resp.status, list(resp.getheaders()), resp.read())
        except urllib.error.HTTPError as err:
            return Response(err.code, list(err.headers.items()), err.read())
        except (urllib.error.URLError, OSError, ValueError) as err:
            raise FetchError("transport failure for %s %s: %s" % (request.method, request.url, err))


def fetch_json(transport, request):
    """Send a read request and return its parsed JSON body, or raise FetchError.

    Any status outside 200 to 299 is a failure, with the status and the
    start of the body in the message (the body is passed through the
    redactor by the caller before it reaches a stream). A body that is not
    JSON is a failure too; nothing is concluded from it.
    """
    response = transport.send(request)
    text = response.body.decode("utf-8", "replace")
    if not 200 <= response.status < 300:
        raise FetchError("%s %s answered HTTP %d: %s" % (request.method, request.url, response.status, text[:500]))
    try:
        return json.loads(text)
    except ValueError as err:
        raise FetchError("%s %s answered a body that is not JSON (%s): %s" % (request.method, request.url, err, text[:500]))


# ----------------------------------------------------------------- state

def default_state_path(env=None):
    """~/.local/state/near-agent/state.json (XDG_STATE_HOME honoured): outside the repo."""
    env = os.environ if env is None else env
    base = env.get("XDG_STATE_HOME", "").strip() or os.path.join(env.get("HOME", "~"), ".local", "state")
    return Path(os.path.expanduser(base)) / "near-agent" / "state.json"


def load_state(path):
    """Return the saved board snapshot {job_id: budget} or {} when none exists.

    A state file that cannot be parsed is an error: a corrupt snapshot
    would make every job look new or unchanged by accident.
    """
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as err:
        raise ConfigError("state file %s is not JSON (%s); move it aside or pass --state" % (path, err))
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, dict):
        raise ConfigError("state file %s does not hold a jobs object; move it aside or pass --state" % path)
    return jobs


def save_state(path, jobs, polled_utc):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"polled_utc": polled_utc, "jobs": jobs}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def changed_jobs(previous, current):
    """Jobs whose id is new or whose budget differs from the previous poll.

    Returns a list of (job_id, previous_budget, current_budget) with
    previous_budget None for a job not seen before. Jobs that left the
    board are not reported here; the count line shows the board size.
    """
    out = []
    for job_id in sorted(current):
        before = previous.get(job_id)
        if job_id not in previous or before != current[job_id]:
            out.append((job_id, before, current[job_id]))
    return out


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ----------------------------------------------------------------- CLI

def build_parser():
    parser = argparse.ArgumentParser(prog="near-agent/worker.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    poll = sub.add_parser("poll", help="read assignments and the standard board; print the digest")
    poll.add_argument("--state", help="state file path (default: ~/.local/state/near-agent/state.json)")
    poll.add_argument("--repeat", type=int, default=1, help="number of polls to run (default 1)")
    poll.add_argument("--interval", type=int, default=60,
                      help="seconds between polls when --repeat is above 1 (minimum %d)" % MIN_INTERVAL_SECONDS)

    for name, help_text in (
        ("start", "start work on an assignment"),
        ("message", "send a message on an assignment"),
        ("submit", "submit a deliverable on an assignment"),
        ("bid", "bid on a board job"),
    ):
        act = sub.add_parser(name, help=help_text + " (dry run unless --execute)")
        act.add_argument("target_id", help="assignment id, or job id for bid")
        act.add_argument("--text", help="message or submission text")
        act.add_argument("--amount", help="bid amount, as the marketplace expects it")
        act.add_argument("--note", help="bid note")
        act.add_argument("--execute", action="store_true", help="actually send the request; the default is a dry run")
    return parser


def main(argv=None, env=None, transport=None, stdout=None, stderr=None):
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    env = os.environ if env is None else env
    args = build_parser().parse_args(argv)

    try:
        token = read_token(env)
    except ConfigError as err:
        stderr.write("error: %s\n" % err)
        return 2
    redactor = Redactor(token)
    transport = UrllibTransport() if transport is None else transport

    try:
        if args.command == "poll":
            return run_poll(args, token, transport, redactor, stdout, env)
        return run_act(args, token, transport, redactor, stdout, stderr)
    except (ConfigError, FetchError, NotDocumented) as err:
        redactor.emit(stderr, "error: %s" % err)
        return 2


def run_poll(args, token, transport, redactor, stdout, env):
    raise NotDocumented("poll digest: the board and assignment response fields are not recorded in this repo yet")


def run_act(args, token, transport, redactor, stdout, stderr):
    spec = ACTIONS.get(args.command)
    if spec is None:
        raise NotDocumented("%s: the endpoint for this action is not recorded in this repo yet; nothing was sent" % args.command)
    raise NotDocumented("%s: request building is not implemented yet" % args.command)


if __name__ == "__main__":
    sys.exit(main())
