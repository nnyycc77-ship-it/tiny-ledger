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
poll; polling is read only and always runs. `poll --replay-assignments
FILE --replay-board FILE` reads two saved response bodies instead of the
network and sends nothing; the test fixtures are such files.

Where the endpoint paths and field names come from: the two read paths
and the environment variable name are fixed by issue #48; the four act
endpoints and their body fields, and the assignment schema, are quoted
from the marketplace's OpenAPI document (https://market.near.ai/openapi.json)
on issue #48; the board job fields are read from a captured real board
response, excerpted in tests/fixtures with its provenance. README.md
carries the hashes.
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

# Act endpoints, from the marketplace's own OpenAPI document (see README.md,
# Sources: https://market.near.ai/openapi.json, read by the coordinator on
# 2026-10-23 and quoted on issue #48). Each entry: HTTP method, path template
# with {id}, the required body fields, the optional body fields. A body field
# the spec does not name is never sent. "start" has no request body.
ACTIONS = {
    "start": ("POST", "/v1/assignments/{id}/start", (), ()),
    "message": ("POST", "/v1/assignments/{id}/messages", ("body",), ("attachmentIds", "clientRequestId")),
    "submit": ("POST", "/v1/assignments/{id}/submit", ("deliverableMarkdown",), ("files",)),
    "bid": ("POST", "/v1/jobs/{id}/bids", ("amount", "proposal"), ("slaSeconds",)),
}

# Response fields the digest reads, from the same two sources (the captured
# board response and the OpenAPI JobAssignment / MyAssignmentItem schemas).
JOB_LIST_FIELD = "jobs"
JOB_ID_FIELD = "jobId"
JOB_BUDGET_FIELDS = ("budgetAmount", "budgetToken")
JOB_STATUS_FIELD = "status"
ASSIGNMENT_LIST_FIELD = "assignments"
ASSIGNMENT_ROW_FIELD = "assignment"
ASSIGNMENT_ID_FIELD = "assignmentId"
ASSIGNMENT_STATUS_FIELD = "status"


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
    poll.add_argument("--replay-assignments", metavar="FILE",
                      help="read the assignments response from this saved JSON body instead of the network")
    poll.add_argument("--replay-board", metavar="FILE",
                      help="read the board response from this saved JSON body instead of the network")

    for name, help_text in (
        ("start", "start work on an assignment"),
        ("message", "send a message on an assignment"),
        ("submit", "submit a deliverable on an assignment"),
        ("bid", "bid on a board job"),
    ):
        act = sub.add_parser(name, help=help_text + " (dry run unless --execute)")
        act.add_argument("target_id", help="assignment id, or job id for bid")
        act.add_argument("--text", help="message: the body field; submit: the deliverableMarkdown field")
        act.add_argument("--amount", help="bid: the amount field, a string such as 25.00")
        act.add_argument("--note", help="bid: the proposal field")
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


# ----------------------------------------------------------------- digest

def _require(mapping, key, where):
    if not isinstance(mapping, dict) or key not in mapping:
        raise FetchError("%s: expected an object with %r; the response shape is not the documented one" % (where, key))
    return mapping[key]


def board_jobs(payload):
    """{jobId: "budgetAmount budgetToken"} from a board response, or FetchError.

    Every job must carry jobId, budgetAmount and budgetToken as strings;
    anything else is an unrecognised shape and nothing is concluded.
    """
    jobs = _require(payload, JOB_LIST_FIELD, "board response")
    if not isinstance(jobs, list):
        raise FetchError("board response: %r is not a list" % JOB_LIST_FIELD)
    out = {}
    for index, job in enumerate(jobs):
        where = "board job %d" % index
        job_id = _require(job, JOB_ID_FIELD, where)
        amount = _require(job, JOB_BUDGET_FIELDS[0], where)
        token = _require(job, JOB_BUDGET_FIELDS[1], where)
        if not all(isinstance(v, str) and v for v in (job_id, amount, token)):
            raise FetchError("%s: %s, %s and %s must be non empty strings" % ((where,) + (JOB_ID_FIELD,) + JOB_BUDGET_FIELDS))
        if job_id in out:
            raise FetchError("%s: duplicate %s %s" % (where, JOB_ID_FIELD, job_id))
        out[job_id] = "%s %s" % (amount, token)
    return out


def job_titles(payload):
    """{jobId: title} for the digest lines; a missing title prints as such."""
    titles = {}
    for job in payload.get(JOB_LIST_FIELD, []):
        title = job.get("title")
        titles[job[JOB_ID_FIELD]] = title if isinstance(title, str) else "(no title field)"
    return titles


def assignment_rows(payload):
    """[(assignmentId, status)] from an assignments response, or FetchError.

    The documented wrapper is MyAssignmentItem {assignment, job,
    latestMessage, autoAcceptAt}; the id and status sit on the inner
    JobAssignment. The captured real response is {"assignments": []}.
    """
    items = _require(payload, ASSIGNMENT_LIST_FIELD, "assignments response")
    if not isinstance(items, list):
        raise FetchError("assignments response: %r is not a list" % ASSIGNMENT_LIST_FIELD)
    rows = []
    for index, item in enumerate(items):
        where = "assignment item %d" % index
        inner = _require(item, ASSIGNMENT_ROW_FIELD, where)
        assignment_id = _require(inner, ASSIGNMENT_ID_FIELD, where)
        status = inner.get(ASSIGNMENT_STATUS_FIELD)
        if not isinstance(assignment_id, str) or not assignment_id:
            raise FetchError("%s: %s must be a non empty string" % (where, ASSIGNMENT_ID_FIELD))
        rows.append((assignment_id, status if isinstance(status, str) else "(no status field)"))
    return rows


def render_digest(polled_utc, assignments, jobs, titles, changes, sources, state_path):
    lines = ["# NEAR AI Agent Market poll, %s" % polled_utc, ""]
    lines.append("Sources read (GET, Bearer token from %s):" % TOKEN_ENV)
    for label, url in sources:
        lines.append("- %s: %s" % (label, url))
    lines.append("")
    lines.append("Assignments: %d" % len(assignments))
    for assignment_id, status in assignments:
        lines.append("- %s (status %s)" % (assignment_id, status))
    lines.append("")
    lines.append("Board jobs (kind=standard): %d" % len(jobs))
    lines.append("")
    if changes:
        lines.append("Changed since the previous poll: %d" % len(changes))
        for job_id, before, after in changes:
            kind = "new" if before is None else "budget %s -> %s" % (before, after)
            lines.append("- %s: %s; budget %s; %s" % (job_id, kind, after, titles.get(job_id, "")))
    else:
        lines.append("Changed since the previous poll: 0")
    lines.append("")
    lines.append("State: %s" % state_path)
    return "\n".join(lines) + "\n"


def poll_once(token, transport, state_path, replay=None):
    """One poll. Returns the digest text; writes the state only after both reads parsed."""
    polled_utc = utc_now()
    assignments_req = build_request(token, "GET", ASSIGNMENTS_PATH)
    board_req = build_request(token, "GET", BOARD_PATH, BOARD_QUERY)
    if replay is None:
        assignments_payload = fetch_json(transport, assignments_req)
        board_payload = fetch_json(transport, board_req)
    else:
        assignments_payload, board_payload = replay
    assignments = assignment_rows(assignments_payload)
    jobs = board_jobs(board_payload)
    titles = job_titles(board_payload)
    previous = load_state(state_path)
    changes = changed_jobs(previous, jobs)
    sources = [("assignments", assignments_req.url), ("board", board_req.url)]
    if replay is not None:
        sources = [(label + " (replayed from a file, nothing sent)", url) for label, url in sources]
    digest = render_digest(polled_utc, assignments, jobs, titles, changes, sources, state_path)
    save_state(state_path, jobs, polled_utc)
    return digest


def read_replay(assignments_file, board_file):
    """Parse two saved response bodies for a poll that sends nothing."""
    try:
        return (json.loads(Path(assignments_file).read_text(encoding="utf-8")),
                json.loads(Path(board_file).read_text(encoding="utf-8")))
    except (OSError, ValueError) as err:
        raise ConfigError("replay files could not be read as JSON: %s" % err)


def run_poll(args, token, transport, redactor, stdout, env):
    state_path = Path(args.state) if args.state else default_state_path(env)
    replay = None
    if args.replay_board or args.replay_assignments:
        if not (args.replay_board and args.replay_assignments):
            raise ConfigError("--replay-board and --replay-assignments go together")
        replay = read_replay(args.replay_assignments, args.replay_board)
    if args.repeat < 1:
        raise ConfigError("--repeat must be at least 1")
    if args.repeat > 1 and args.interval < MIN_INTERVAL_SECONDS:
        raise ConfigError("--interval must be at least %d seconds" % MIN_INTERVAL_SECONDS)
    for index in range(args.repeat):
        if index:
            time.sleep(args.interval)
        redactor.emit(stdout, poll_once(token, transport, state_path, replay))
    return 0


# ----------------------------------------------------------------- act

def act_request(token, action, target_id, fields):
    """Build the request for one act command from the documented endpoint.

    `fields` maps spec body field names to values. Every required field
    must be present and non empty; a field the spec does not name is
    refused. Nothing is sent here.
    """
    spec = ACTIONS.get(action)
    if spec is None:
        raise NotDocumented("%s: the endpoint for this action is not recorded in this repo; nothing was sent" % action)
    method, template, required, optional = spec
    if not target_id or not isinstance(target_id, str):
        raise ConfigError("%s: an id is required" % action)
    unknown = sorted(set(fields) - set(required) - set(optional))
    if unknown:
        raise ConfigError("%s: field(s) %s are not in the documented request body" % (action, ", ".join(unknown)))
    missing = [name for name in required if fields.get(name) in (None, "")]
    if missing:
        raise ConfigError("%s: required field(s) %s missing" % (action, ", ".join(missing)))
    body = {name: value for name, value in fields.items() if value is not None} or None
    if not required and not optional:
        body = None
    path = template.replace("{id}", urllib.parse.quote(target_id, safe=""))
    return build_request(token, method, path, body=body)


def act_fields(args):
    """Map CLI options onto the documented body fields of each action."""
    if args.command == "start":
        return {}
    if args.command == "message":
        return {"body": args.text}
    if args.command == "submit":
        return {"deliverableMarkdown": args.text}
    if args.command == "bid":
        return {"amount": args.amount, "proposal": args.note}
    raise ConfigError("unknown command %s" % args.command)


def run_act(args, token, transport, redactor, stdout, stderr):
    request = act_request(token, args.command, args.target_id, act_fields(args))
    if not args.execute:
        redactor.emit(stdout, "DRY RUN: nothing sent. The request that --execute would send:\n\n" + request.describe())
        return 0
    response = transport.send(request)
    text = response.body.decode("utf-8", "replace")
    redactor.emit(stdout, "SENT %s %s\nHTTP %d\n%s" % (request.method, request.url, response.status, text))
    if not 200 <= response.status < 300:
        raise FetchError("%s answered HTTP %d" % (args.command, response.status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
