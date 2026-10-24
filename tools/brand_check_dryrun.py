#!/usr/bin/env python3
"""Offline end to end dry run of the Brand Name Checker (issue #137).

Runs every leg of tools/brand_name_checker.py against recorded responses
instead of the network, and compares each leg's verdict with the one
expected for it:

  domains     check_domain() on the RDAP route for each requested TLD
  handles     check_handle() for each requested platform
  app store   the iTunes Search route through itunes_matches(), exact
              name matches only
  trademark   uspto_trademarks.section() with no key, which must give the
              honest unconfirmed wording, word for word

It then renders the full report through brand_name_checker.report() with
the same recorded responses, so the whole pipeline runs end to end.

A domain route may instead record its answers attempt by attempt
("attempts", issue #220). Those routes run the checker's real get(), so the
single retry on no response added in issue #201 is exercised, not
re-implemented: urlopen is replaced, for that one call only, by a stub that
answers each attempt in turn (no response, or an HTTP error status) and
counts the requests. Such a domain gets two more checked rows: the number of
requests made, and whether its transcript carries the "retried once" line.

The cases and their recorded responses are in
tools/tests/fixtures/brandcheck-dryrun/cases.json. A route is a real
capture (a body the coordinator captured live on issue #51), a real status
record (the coordinator's status table on issue #51), or a SYNTHETIC
response labelled as such in its own file or note. Every body file's
SHA-256 is checked against its provenance before any case runs. A URL
with no recorded response stops the run: a dry run never goes to the
network.

    python3 tools/brand_check_dryrun.py            # verdict table, exit 0 when every verdict matches
    python3 tools/brand_check_dryrun.py --report   # also print each rendered report

Exit codes: 0 every verdict matched; 1 at least one verdict did not match;
2 the harness could not run (a fixture missing or altered, an unrecorded
URL). Standard library only.
"""

import argparse
import hashlib
import http.client
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import brand_name_checker as bnc  # noqa: E402
import uspto_trademarks  # noqa: E402

FIXTURES = HERE / "tests" / "fixtures"
CASES_FILE = FIXTURES / "brandcheck-dryrun" / "cases.json"
PROVENANCE_FILES = (FIXTURES / "brandcheck" / "provenance.json", FIXTURES / "brandcheck-dryrun" / "provenance.json")
STATUS_FILE = FIXTURES / "brandcheck" / "status-captures.json"
COUNTRIES = ["US"]

APP_MATCH = "exact name match"
APP_NONE = "no exact name match"
TRADEMARK_OK = "not covered (unconfirmed wording)"
TRADEMARK_BAD = "WORDING CHANGED"
REASONS = {"200": "OK", "404": "Not Found", "503": "Service Unavailable"}
RETRY_LINE = "[retried once: the first attempt got no response:"


class HarnessError(Exception):
    """The dry run could not run as recorded. No verdict is given."""


def recorded_hashes():
    hashes = {}
    for prov in PROVENANCE_FILES:
        for name, entry in json.loads(prov.read_text(encoding="utf-8")).items():
            if isinstance(entry, dict) and "sha256" in entry:
                hashes[(prov.parent / name).resolve()] = entry["sha256"]
    return hashes


def read_body(rel, hashes):
    path = (FIXTURES / rel).resolve()
    if path not in hashes:
        raise HarnessError("%s has no recorded hash in a provenance file" % rel)
    try:
        data = path.read_bytes()
    except OSError as err:
        raise HarnessError("cannot read %s: %s" % (rel, err))
    if hashlib.sha256(data).hexdigest() != hashes[path]:
        raise HarnessError("%s does not match its recorded SHA-256; it was altered" % rel)
    return data.decode("utf-8")


class Replay:
    """A fetch() for brand_name_checker that answers only from recorded routes."""

    def __init__(self, routes, hashes, status_records):
        self.routes = routes
        self.hashes = hashes
        self.status_records = status_records
        self.asked = []
        self.requests = {}  # url -> requests the checker made, for attempt routes

    def __call__(self, url, read_body_flag):
        self.asked.append(url)
        route = self.routes.get(url)
        if route is None:
            raise HarnessError("no recorded response for %s; a dry run never goes to the network" % url)
        if "attempts" in route:
            return self.replay_attempts(url, read_body_flag, route["attempts"])
        final = route.get("final_url", url)
        if "error" in route:
            return bnc.Result(url, final, "replayed", None, None, [], None, route["error"])
        if "status_record" in route:
            record = self.status_records.get(route["status_record"])
            if record is None:
                raise HarnessError("%s is not in the recorded status table" % route["status_record"])
            status, kind = record["status"], "real status recorded on issue #51"
        else:
            status = route["status"]
            kind = "real capture from issue #51" if "capture" in route else "SYNTHETIC"
        line = "HTTP %d %s (replayed, %s; the status line itself was not captured)" % (
            status, REASONS.get(str(status), ""), kind)
        body = None
        source = route.get("capture") or route.get("synthetic")
        if read_body_flag and status == 200 and source and source.endswith(".json"):
            body = read_body(source, self.hashes)
        return bnc.Result(url, final, "replayed", line, status, [], body, None)


    def replay_attempts(self, url, read_body_flag, attempts):
        """The checker's real get(), with urlopen answering the recorded attempts in turn."""
        queue = list(attempts)
        self.requests[url] = 0

        def stub(request, timeout=None):
            self.requests[url] += 1
            if not queue:
                raise HarnessError("%s: the checker made more requests than the %d recorded"
                                   % (url, len(attempts)))
            attempt = queue.pop(0)
            if "no_response" in attempt:
                raise http.client.RemoteDisconnected(attempt["no_response"])
            status = attempt.get("status")
            if isinstance(status, int) and status >= 400:
                raise urllib.error.HTTPError(url, status, REASONS.get(str(status), ""), {}, None)
            raise HarnessError("%s: an attempt is no_response or an HTTP error status, got %r" % (url, attempt))

        saved = urllib.request.urlopen
        urllib.request.urlopen = stub
        try:
            result = bnc.get(url, read_body_flag)
        finally:
            urllib.request.urlopen = saved
        return result._replace(checked="replayed")


def run_case(case, hashes, status_records):
    """[(leg, expected, actual)] and the rendered report for one case."""
    fetch = Replay(case["routes"], hashes, status_records)
    name, rows = case["name"], []
    for tld in case["tlds"]:
        result, verdict, _ = bnc.check_domain(name, tld, fetch)
        rows.append(("domain %s" % tld, verdict))
        if result.url in fetch.requests:  # an attempt route: the retry rows
            rows.append(("domain %s requests" % tld, str(fetch.requests[result.url])))
            rows.append(("domain %s retry note" % tld,
                         "present" if RETRY_LINE in bnc.transcript(result, "") else "absent"))
    for platform in case["platforms"]:
        _, verdict = bnc.check_handle(platform, name, fetch)
        rows.append((platform, verdict))
    res = fetch(bnc.itunes_url(name, case["app_limit"]), True)
    parsed = bnc.itunes_matches(res.body, name) if res.status == 200 and res.body is not None else None
    rows.append(("app store", bnc.UNCONFIRMED if parsed is None else (APP_MATCH if parsed[2] else APP_NONE)))
    section = uspto_trademarks.section(name, COUNTRIES, env={})
    rows.append(("trademark", TRADEMARK_OK if section == uspto_trademarks.unconfirmed_lines(COUNTRIES)
                 else TRADEMARK_BAD))
    report = bnc.report(name, case["tlds"], case["platforms"], case["app_limit"], 0, COUNTRIES,
                        Replay(case["routes"], hashes, status_records), env={})
    expect = case["expect"]
    if set(expect) != {leg for leg, _ in rows}:
        raise HarnessError("case %s: expected legs %s, ran %s" % (case["case"], sorted(expect),
                                                                  sorted(leg for leg, _ in rows)))
    return [(leg, expect[leg], actual) for leg, actual in rows], report


def load():
    try:
        cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))["cases"]
        status = {c["request"]: c for c in json.loads(STATUS_FILE.read_text(encoding="utf-8"))["captures"]}
        hashes = recorded_hashes()
    except (OSError, ValueError, KeyError) as err:
        raise HarnessError("cannot load the dry run fixtures: %s" % err)
    return cases, status, hashes


def run_all():
    cases, status, hashes = load()
    return [(case, *run_case(case, hashes, status)) for case in cases]


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Offline dry run of the Brand Name Checker against recorded responses.")
    p.add_argument("--report", action="store_true", help="also print each case's rendered report")
    args = p.parse_args(argv)
    try:
        results = run_all()
    except HarnessError as err:
        stderr.write("error: %s\n" % err)
        return 2
    mismatches = 0
    out = ["# Brand Name Checker dry run (offline, recorded responses)", ""]
    for case, rows, report in results:
        out += ["## Case %s: %s" % (case["case"], case["name"]), "", case["about"], "",
                "| Leg | Expected | Actual | Result |", "| --- | --- | --- | --- |"]
        for leg, expected, actual in rows:
            ok = expected == actual
            mismatches += 0 if ok else 1
            out.append("| %s | %s | %s | %s |" % (leg, expected, actual, "match" if ok else "MISMATCH"))
        out.append("")
        if args.report:
            out += ["### Rendered report", "", report]
    total = sum(len(rows) for _, rows, _ in results)
    out.append("Result: %d of %d verdicts matched%s." % (total - mismatches, total,
                                                         "" if not mismatches else "; %d MISMATCH" % mismatches))
    stdout.write("\n".join(out) + "\n")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
