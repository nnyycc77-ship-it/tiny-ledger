#!/usr/bin/env python3
"""Smoke checks for the public recall API (issue #68).

Asserts the response shapes a registry or buyer relies on, and prints
one Markdown section in the delivery format from AGENT-BRIEF.md: per
check, a claim line per assertion (PASS or FAIL, naming the assertion),
the source link (the exact request URL), the retrieval time in UTC, and
the complete raw response transcript (status line, headers in the order
returned, a blank line, the body exactly as returned) directly beneath.

    python3 tools/api_smoke.py                      # offline, fixtures
    python3 tools/api_smoke.py --live http://127.0.0.1:8000
    python3 tools/api_smoke.py --live https://<deployed host> --product 'Instant Pot'

Shapes asserted:

1. GET / is 200 JSON naming the service ("service"), the /recall
   endpoint ("endpoint" is "/recall"), and a "payout_wallet" with the
   EVM address shape (0x plus 40 hex digits).
2. GET /recall?product=<name> with no payment header is 402 JSON with
   x402Version 1 and an "accepts" entry carrying scheme "exact", network
   "base", a numeric maxAmountRequired, an asset address, a payTo address
   equal to the descriptor's payout_wallet, a resource, and a description
   of at most 500 characters.
3. GET /openapi.json is 200, parses as OpenAPI (an "openapi" field and a
   "paths" object), and names /recall in its paths.

Read only. The tool sends GET requests and never an X-PAYMENT header, so
it can never pay for a call; the 402 check depends on that.

Offline mode (the default) reads the transcripts captured from the local
gated server in tools/tests/fixtures/api_smoke/ and checks their SHA-256
against provenance.json before asserting anything; a changed fixture is
an error, not a result.

Exit 0 when every assertion passes, 1 when any fails, 2 when the checks
cannot run (a transport failure, an unreadable or altered fixture, bad
input). A failed fetch is never reported as a pass or a fail of a shape.
Standard library only.
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "tests" / "fixtures" / "api_smoke"
DEFAULT_PRODUCT = "Instant Pot"
TIMEOUT_SECONDS = 30
EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
MAX_DESCRIPTION = 500

Capture = namedtuple("Capture", "url retrieved status_line status headers body")
FIXTURE_NAMES = {"descriptor": "descriptor.http", "payment": "recall-402.http", "openapi": "openapi.http"}


class SmokeError(Exception):
    """The checks could not run. Never reported as a pass or a fail."""


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET url with no payment header. HTTP error statuses are captured,
    because a 402 or 404 is the evidence; transport failures raise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"Accept": "*/*", "User-Agent": "tiny-ledger-api-smoke"})
    assert request.get_header("X-payment") is None
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError) as err:
        raise SmokeError("%s could not be fetched: %s" % (url, err))
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise SmokeError("%s body could not be read: %s" % (url, err))
    return Capture(url, retrieved, status_line, response.status, headers, body)


def transcript(capture):
    return "\n".join([capture.status_line] + capture.headers + ["", capture.body])


def parse_transcript(text, url, retrieved):
    """A saved transcript back into a Capture."""
    head, sep, body = text.partition("\n\n")
    if not sep:
        raise SmokeError("fixture for %s is not a transcript (no blank line after headers)" % url)
    lines = head.split("\n")
    m = re.match(r"HTTP/\d\.\d (\d{3}) ", lines[0] + " ")
    if not m:
        raise SmokeError("fixture for %s has no status line" % url)
    return Capture(url, retrieved, lines[0], int(m.group(1)), lines[1:], body)


def offline_captures(fixtures=FIXTURES):
    try:
        provenance = json.loads((fixtures / "provenance.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise SmokeError("cannot read fixture provenance: %s" % err)
    out = {}
    for key, name in FIXTURE_NAMES.items():
        entry = provenance.get(name)
        if not entry:
            raise SmokeError("no provenance for fixture %s" % name)
        try:
            data = (fixtures / name).read_bytes()
        except OSError as err:
            raise SmokeError("cannot read fixture %s: %s" % (name, err))
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise SmokeError("fixture %s does not match its recorded sha256" % name)
        out[key] = parse_transcript(data.decode("utf-8"), entry["url"], entry["retrieved_utc"])
    return out


def live_captures(base, product):
    base = base.rstrip("/")
    return {
        "descriptor": fetch(base + "/"),
        "payment": fetch(base + "/recall?" + urllib.parse.urlencode({"product": product})),
        "openapi": fetch(base + "/openapi.json"),
    }


# ----------------------------------------------------------------------
# Assertions: each returns [(assertion text, passed)]
# ----------------------------------------------------------------------

def json_body(capture):
    try:
        return json.loads(capture.body)
    except ValueError:
        return None


def check_descriptor(capture):
    doc = json_body(capture)
    obj = doc if isinstance(doc, dict) else {}
    wallet = obj.get("payout_wallet")
    return [
        ("GET / answers 200", capture.status == 200),
        ("GET / body is a JSON object", isinstance(doc, dict)),
        ('"service" names the service', isinstance(obj.get("service"), str) and bool(obj.get("service"))),
        ('"endpoint" is "/recall"', obj.get("endpoint") == "/recall"),
        ('"payout_wallet" has the EVM address shape', isinstance(wallet, str) and bool(EVM_ADDRESS.match(wallet))),
    ]


def check_payment(capture, descriptor_wallet):
    doc = json_body(capture)
    obj = doc if isinstance(doc, dict) else {}
    accepts = obj.get("accepts")
    entry = accepts[0] if isinstance(accepts, list) and accepts and isinstance(accepts[0], dict) else {}
    amount = entry.get("maxAmountRequired")
    description = entry.get("description")
    return [
        ("GET /recall without payment answers 402", capture.status == 402),
        ("402 body is a JSON object", isinstance(doc, dict)),
        ('"x402Version" is 1', obj.get("x402Version") == 1),
        ('"accepts" holds an entry', bool(entry)),
        ('accepts[0].scheme is "exact"', entry.get("scheme") == "exact"),
        ('accepts[0].network is "base"', entry.get("network") == "base"),
        ("accepts[0].maxAmountRequired is numeric",
         isinstance(amount, int) or (isinstance(amount, str) and amount.isdigit())),
        ("accepts[0].asset has the EVM address shape",
         isinstance(entry.get("asset"), str) and bool(EVM_ADDRESS.match(entry["asset"]))),
        ("accepts[0].payTo has the EVM address shape",
         isinstance(entry.get("payTo"), str) and bool(EVM_ADDRESS.match(entry["payTo"]))),
        ("accepts[0].payTo equals the descriptor payout_wallet",
         isinstance(descriptor_wallet, str) and entry.get("payTo") == descriptor_wallet),
        ("accepts[0].resource is present", isinstance(entry.get("resource"), str) and bool(entry.get("resource"))),
        ("accepts[0].description is present and at most %d characters" % MAX_DESCRIPTION,
         isinstance(description, str) and 0 < len(description) <= MAX_DESCRIPTION),
    ]


def check_openapi(capture):
    doc = json_body(capture)
    obj = doc if isinstance(doc, dict) else {}
    paths = obj.get("paths")
    return [
        ("GET /openapi.json answers 200", capture.status == 200),
        ("body parses as OpenAPI (openapi field and paths object)",
         isinstance(obj.get("openapi"), str) and isinstance(paths, dict)),
        ("paths names /recall", isinstance(paths, dict) and "/recall" in paths),
    ]


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def section(title, capture, results):
    lines = ["### %s" % title, "", "QUERY: GET %s" % capture.url, "Retrieved (UTC): %s" % capture.retrieved,
             "HTTP status: %s" % capture.status_line, ""]
    for text, passed in results:
        lines.append("- %s: %s" % ("PASS" if passed else "FAIL", text))
    lines += ["", "Source: <%s>" % capture.url, fenced(transcript(capture)), ""]
    return lines


def run_checks(captures, mode):
    descriptor = json_body(captures["descriptor"])
    wallet = descriptor.get("payout_wallet") if isinstance(descriptor, dict) else None
    parts = [
        ("1. Service descriptor", captures["descriptor"], check_descriptor(captures["descriptor"])),
        ("2. Payment required (no payment header sent)", captures["payment"],
         check_payment(captures["payment"], wallet)),
        ("3. OpenAPI document", captures["openapi"], check_openapi(captures["openapi"])),
    ]
    failed = [(title, text) for title, _, results in parts for text, ok in results if not ok]
    lines = ["## Recall API smoke checks (%s)" % mode, "",
             "Read only: GET requests with no X-PAYMENT header; nothing is paid.", ""]
    if failed:
        lines.append("Result: FAIL, %d assertion(s) failed:" % len(failed))
        lines += ["- %s: %s" % (title, text) for title, text in failed]
    else:
        lines.append("Result: PASS, every assertion held.")
    lines.append("")
    for title, capture, results in parts:
        lines += section(title, capture, results)
    return "\n".join(lines), not failed


def main(argv=None):
    p = argparse.ArgumentParser(description="Read only smoke checks for the recall API.")
    p.add_argument("--live", metavar="BASE_URL", help="check a running deployment instead of the fixtures")
    p.add_argument("--product", default=DEFAULT_PRODUCT, help="product name for the 402 check (live mode)")
    args = p.parse_args(argv)
    try:
        if args.live:
            if not re.match(r"^https?://", args.live):
                raise SmokeError("--live needs an http(s) base URL")
            captures, mode = live_captures(args.live, args.product), "live: %s" % args.live
        else:
            captures, mode = offline_captures(), "offline: captured fixtures"
    except SmokeError as err:
        print("error: smoke checks could not run, no result: %s" % err, file=sys.stderr)
        return 2
    report, ok = run_checks(captures, mode)
    sys.stdout.write(report.rstrip("\n") + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
