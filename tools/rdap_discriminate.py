#!/usr/bin/env python3
"""RDAP discriminating check for the brand name checker (issue #201).

The deferred suggestion on issue #53: live runs of tools/brand_name_checker.py
reported "could not confirm" for an invented .com with the error "request
failed: Remote end closed connection without response" (no HTTP response at
all), where a coordinator capture of the same URL answered a clean 404. Two
causes fit and this check tells them apart, in one pass:

* request shape: the tool's request fails while a plain client's request to
  the same URL succeeds, every time;
* intermittent upstream: the same client sometimes gets a response and
  sometimes no response.

For each name and TLD it sends the same RDAP URL
(https://rdap.org/domain/<label>.<tld>, redirects followed) through each
client, --rounds times, interleaved round by round:

    tool         one attempt of brand_name_checker's request, exactly as sent
                 (User-Agent tiny-ledger-brand-name-checker, Accept */*), without
                 the single retry get() adds, so each row is one attempt
    urllib       a plain urllib GET with urllib's default headers
    curl         curl -sS -L with curl's default User-Agent (when curl exists)
    curl-tool-ua curl -sS -L -A tiny-ledger-brand-name-checker (when curl exists)

It prints every attempt (client, round, UTC start time, elapsed time, the
outcome: an HTTP status, or no response with the error text exactly as
raised) and a classification per URL. It only sends GET requests and never
reads a 404 body.

    python3 tools/rdap_discriminate.py zqxflorp nike --rounds 3

Standard library only; curl is optional and its absence is stated in the
output. Exit 0 when the pass completed (whatever the outcomes), 2 on bad
input.
"""

import argparse
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import brand_name_checker as bnc  # noqa: E402

Attempt = namedtuple("Attempt", "client round started elapsed_ms status error")
CLIENTS = ("tool", "urllib", "curl", "curl-tool-ua")
MAX_ROUNDS = 10


def tool_client(url):
    """(status or None, error or None): one attempt of the brand checker's own
    request, without the retry get() adds, so every row is a single attempt."""
    result, _ = bnc._attempt(url, True)
    return (None, result.error) if result.error else (result.status, None)


def urllib_client(url):
    request = urllib.request.Request(url)  # urllib's default headers only
    try:
        with urllib.request.urlopen(request, timeout=bnc.TIMEOUT_SECONDS) as response:
            return response.status, None
    except urllib.error.HTTPError as err:
        err.close()  # never read an error body
        return err.code, None
    except (urllib.error.URLError, OSError, ValueError) as err:
        return None, str(err)


def curl_client(user_agent=None):
    def client(url):
        cmd = ["curl", "-sS", "-L", "-o", "/dev/null", "-w", "%{http_code}", "--max-time",
               str(bnc.TIMEOUT_SECONDS)]
        if user_agent:
            cmd += ["-A", user_agent]
        try:
            done = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=bnc.TIMEOUT_SECONDS + 5)
        except (OSError, subprocess.TimeoutExpired) as err:
            return None, "curl could not run: %s" % err
        code = done.stdout.strip()
        if done.returncode != 0 or not code.isdigit() or code == "000":
            return None, "curl exit %d: %s" % (done.returncode, done.stderr.strip() or "no output")
        return int(code), None
    return client


def default_clients():
    clients = {"tool": tool_client, "urllib": urllib_client}
    if shutil.which("curl"):
        clients["curl"] = curl_client()
        clients["curl-tool-ua"] = curl_client(bnc.USER_AGENT)
    return clients


def run_pass(urls, clients, rounds, now=bnc.utc_now_iso, clock=time.monotonic):
    """{url: [Attempt]} with the clients interleaved round by round."""
    out = {url: [] for url in urls}
    for r in range(1, rounds + 1):
        for url in urls:
            for name, client in clients.items():
                started, t0 = now(), clock()
                status, error = client(url)
                out[url].append(Attempt(name, r, started, int(round((clock() - t0) * 1000)), status, error))
    return out


def outcome(a):
    return "HTTP %d" % a.status if a.error is None else "no response"


def classify(attempts):
    """One of: agree, request shape, intermittent, all fail, differ."""
    by_client = {}
    for a in attempts:
        by_client.setdefault(a.client, set()).add(outcome(a))
    if all(len(v) == 1 for v in by_client.values()):
        seen = set().union(*by_client.values())
        if len(seen) == 1:
            return "all fail" if seen == {"no response"} else "agree"
        tool = by_client.get("tool", set())
        others = [v for k, v in by_client.items() if k != "tool"]
        if tool == {"no response"} and any(v != {"no response"} for v in others):
            return "request shape"
        return "differ"
    return "intermittent"


MEANING = {
    "agree": "every attempt by every client got the same answer",
    "request shape": "the tool's request got no response every time while another client got an HTTP answer "
                     "every time: the cause is in the tool's request",
    "intermittent": "at least one client got an HTTP answer on some attempts and no response on others: the "
                    "cause is intermittent upstream, and a single retry on a transport failure is proportionate",
    "all fail": "no client got any HTTP answer: the endpoint was unreachable from this run",
    "differ": "the clients got different answers, each consistently; read the attempts",
}


def render(results, clients, rounds):
    lines = ["# RDAP discriminating check (issue #201)", "",
             "Clients: %s. Rounds: %d, interleaved." % (", ".join(clients), rounds)]
    missing = [c for c in CLIENTS if c not in clients]
    if missing:
        lines.append("Not run: %s (curl is not installed here)." % ", ".join(missing))
    lines.append("")
    for url, attempts in results.items():
        verdict = classify(attempts)
        lines += ["## %s" % url, "", "Classification: **%s**: %s." % (verdict, MEANING[verdict]), "",
                  "| Client | Round | Started (UTC) | Elapsed ms | Outcome |", "| --- | --- | --- | --- | --- |"]
        for a in attempts:
            shown = outcome(a) if a.error is None else "no response: %s" % a.error.replace("|", "\\|")
            lines.append("| %s | %d | %s | %d | %s |" % (a.client, a.round, a.started, a.elapsed_ms, shown))
        lines.append("")
    return lines


def main(argv=None, clients=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Tell request shape from intermittent upstream for RDAP failures.")
    p.add_argument("names", nargs="+", help="candidate names, as given to the brand checker")
    p.add_argument("--tlds", default="com", help="comma separated TLDs (default com)")
    p.add_argument("--rounds", type=int, default=3, help="attempts per client per URL, 1 to %d" % MAX_ROUNDS)
    args = p.parse_args(argv)
    tlds = [t.strip().lower() for t in args.tlds.split(",") if t.strip()]
    labels = [bnc.label(n) for n in args.names]
    if not 1 <= args.rounds <= MAX_ROUNDS or not tlds or not all(labels) \
            or not all(t.isalnum() for t in tlds):
        stderr.write("error: give names with letters or digits, TLDs such as com, and 1 to %d rounds\n"
                     % MAX_ROUNDS)
        return 2
    urls = [bnc.RDAP_BASE + "%s.%s" % (l, t) for l in labels for t in tlds]
    clients = clients if clients is not None else default_clients()
    stdout.write("\n".join(render(run_pass(urls, clients, args.rounds), list(clients), args.rounds)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
