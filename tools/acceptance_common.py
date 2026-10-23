"""Shared layer for the agent acceptance self tests (issue #124).

Each built NEAR agent has `agents/<agent>/acceptance/acceptance.py`. It
runs the agent the way a marketplace tester would, through its documented
entry point, on committed fixtures, and checks the outputs against every
acceptance criterion the job posting stated. This module holds what they
share:

- `no_network()`: every non loopback socket connect or name lookup is
  refused and recorded. Proxy variables are cleared for the run, so a
  proxy on loopback cannot carry a request out. An agent that reaches for
  the network fails its run instead of slipping through.
- `load()` and `run_main()`: import an agent module from its file, and
  call its `main(argv)` with output captured.
- `Criterion` and `Result`: one status per criterion, with the evidence
  lines behind it. A status is PASS, FAIL or UNTESTABLE. UNTESTABLE always
  carries the reason, for example a live service, a human judgement, or an
  ambiguous criterion. A criterion is never given an invented threshold.

Offline only. Nothing here contacts a marketplace, a provider or a person.
"""

import contextlib
import importlib.util
import io
import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"

PASS, FAIL, UNTESTABLE = "PASS", "FAIL", "UNTESTABLE"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}
PROXY_VARS = {"http_proxy", "https_proxy", "all_proxy", "ftp_proxy"}


class NetworkAttempt(RuntimeError):
    """An agent tried to reach a host other than loopback."""


@contextlib.contextmanager
def no_network(attempts=None):
    """Refuse non loopback network access; append each refused target to
    `attempts` when a list is given."""
    real_connect, real_connect_ex = socket.socket.connect, socket.socket.connect_ex
    real_getaddrinfo = socket.getaddrinfo

    def host_of(address):
        return address[0] if isinstance(address, tuple) and address else address

    def refuse(target):
        if attempts is not None:
            attempts.append(str(target))
        raise NetworkAttempt("network access attempted: %r" % (target,))

    def connect(sock, address):
        if host_of(address) not in LOOPBACK:
            refuse(address)
        return real_connect(sock, address)

    def connect_ex(sock, address):
        if host_of(address) not in LOOPBACK:
            refuse(address)
        return real_connect_ex(sock, address)

    def getaddrinfo(host, *args, **kwargs):
        if host not in LOOPBACK:
            refuse(host)
        return real_getaddrinfo(host, *args, **kwargs)

    saved_env = {k: os.environ.pop(k) for k in list(os.environ) if k.lower() in PROXY_VARS}
    socket.socket.connect, socket.socket.connect_ex = connect, connect_ex
    socket.getaddrinfo = getaddrinfo
    try:
        yield attempts
    finally:
        socket.socket.connect, socket.socket.connect_ex = real_connect, real_connect_ex
        socket.getaddrinfo = real_getaddrinfo
        os.environ.update(saved_env)


def load(name, path):
    """Import a module from a file path, with its folder on sys.path."""
    path = Path(path)
    if name in sys.modules:
        return sys.modules[name]
    folder = str(path.parent)
    if folder not in sys.path:
        sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_main(fn, argv, env=None, attempts=None):
    """Call an agent's main(argv) offline. Returns (exit code, stdout, stderr).
    `env` replaces os.environ for the call when given."""
    out, err = io.StringIO(), io.StringIO()
    saved = dict(os.environ)
    if env is not None:
        os.environ.clear()
        os.environ.update(env)
    try:
        with no_network(attempts), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = fn(argv)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
    finally:
        os.environ.clear()
        os.environ.update(saved)
    return (0 if code is None else code), out.getvalue(), err.getvalue()


class Criterion:
    """One acceptance criterion's outcome on one case."""

    def __init__(self, cid, text):
        self.cid, self.text = cid, text
        self.fails, self.untestable, self.passes = [], [], []

    def ok(self, evidence):
        self.passes.append(evidence)
        return self

    def fail(self, evidence):
        self.fails.append(evidence)
        return self

    def cannot(self, reason):
        self.untestable.append(reason)
        return self

    def check(self, condition, evidence_ok, evidence_fail):
        return self.ok(evidence_ok) if condition else self.fail(evidence_fail)

    @property
    def status(self):
        if self.fails:
            return FAIL
        if self.untestable:
            return UNTESTABLE
        return PASS if self.passes else UNTESTABLE

    def evidence(self):
        passes = [e for e in self.passes if e]
        if self.fails:
            return self.fails
        if self.untestable:
            return self.untestable + passes[:1]
        return passes[:2]


class Result:
    """All criteria for one case of one agent."""

    def __init__(self, agent, case, source):
        self.agent, self.case, self.source = agent, case, source
        self.criteria = []

    def criterion(self, cid, text):
        c = Criterion(cid, text)
        self.criteria.append(c)
        return c

    def counts(self):
        out = {PASS: 0, FAIL: 0, UNTESTABLE: 0}
        for c in self.criteria:
            out[c.status] += 1
        return out

    def render(self):
        lines = ["## %s: %s" % (self.agent, self.case), "", "Criteria source: %s" % self.source, ""]
        for c in self.criteria:
            lines.append("%-10s %s. %s" % (c.status, c.cid, c.text))
            for e in c.evidence():
                lines.append("           evidence: %s" % e)
        n = self.counts()
        lines += ["", "Summary: %d PASS, %d FAIL, %d UNTESTABLE" % (n[PASS], n[FAIL], n[UNTESTABLE]), ""]
        return "\n".join(lines)


def print_results(results, stream=None):
    stream = stream or sys.stdout
    total = {PASS: 0, FAIL: 0, UNTESTABLE: 0}
    for r in results:
        stream.write(r.render() + "\n")
        for k, v in r.counts().items():
            total[k] += v
    stream.write("Total: %d PASS, %d FAIL, %d UNTESTABLE\n" % (total[PASS], total[FAIL], total[UNTESTABLE]))
    return total


def hhmm(text):
    """'09:05' -> minutes after midnight."""
    h, m = text.strip().split(":")
    return int(h) * 60 + int(m)
