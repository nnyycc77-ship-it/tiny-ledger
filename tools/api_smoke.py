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
4. Every other GET endpoint in the OpenAPI document answers 200 with
   its fetcher's Markdown report: a text/markdown body whose first line
   is the report title, carrying a retrieved UTC timestamp from the
   evidence format and the fenced raw response transcript (issue #205).
   The timestamp's label varies by fetcher (most print a Retrieved
   (UTC) line; /faa states the archive's retrieved time inline), so the
   assertion matches the timestamp itself, not one label. A final
   coverage section then counts every GET endpoint in the document
   exactly once: checked, or listed in NO_ENDPOINT_CAPTURE with the
   reason it has no captured 200 yet (issue #243). An endpoint in both
   or neither fails the run and is named.
5. The bad query (400) shape of every wrapped endpoint (issue #225):
   a request naming no valid input (the bare path, no query string)
   is answered 400 before any source fetch, with a plain text body
   naming the problem and no report served. Endpoints whose 400
   cannot be captured in this pattern are listed in NO_400_CAPTURE
   with the reason, and a closing accounting section counts every
   GET endpoint exactly once: captured, or reasoned. An endpoint in
   neither table fails the run and is named.
6. The source failure (502) shape of every wrapped endpoint (issue
   #235): a valid query whose source fetch fails is answered 502,
   with a plain text body naming the failure and no report served.
   The captures are replays: the local server was run with its
   proxy settings pointed at a closed local port, so every source
   fetch failed at transport and the server's own 502 answer was
   captured verbatim; each provenance entry records that config.
   Endpoints with no 502 shape are listed in NO_502_CAPTURE with
   the reason, under the same exactly once accounting.
7. The unavailable (503) shape (issue #245): api/openapi.json
   declares a 503 for GET /formd and GET /insider (issue #243),
   answered when the server carries no EDGAR_CONTACT, before any
   query validation and before any fetch. Each capture is a replay
   from the local server run without the contact. The accounting is driven by the document
   itself: an endpoint is capturable exactly when its entry in
   api/openapi.json declares a 503 response, and every other
   endpoint is reasoned as declaring no 503.

Read only. The tool sends GET requests and never an X-PAYMENT header, so
it can never pay for a call; the 402 check depends on that.

Offline mode (the default) reads the transcripts captured from the local
gated server in tools/tests/fixtures/api_smoke/ and checks their SHA-256
against provenance.json before asserting anything; a changed fixture is
an error, not a result, and so is a missing fixture or provenance entry,
named by its endpoint. The coverage denominator is the repo's own
api/openapi.json, read by the tool itself, so a stale capture cannot
undercount the surface. Live mode keeps the original three registry
checks only; the endpoint coverage is an offline fixture discipline.

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
RETRIEVED_UTC = re.compile(r"(?i)retrieved[^.\n]{0,30}\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
MAX_DESCRIPTION = 500

Capture = namedtuple("Capture", "url retrieved status_line status headers body")
FIXTURE_NAMES = {"descriptor": "descriptor.http", "payment": "recall-402.http", "openapi": "openapi.http"}

# Offline endpoint coverage (issue #205): one captured fixture per GET
# endpoint in api/openapi.json that is not already covered above (/ is
# the descriptor check, /recall is the payment check). Each entry is the
# endpoint path, its fixture file, and the tool file its report names.
# A path added to the OpenAPI document without an entry here fails the
# coverage section of the offline run and the api_smoke suite.
ENDPOINT_FIXTURES = {
    "/app": ("app.http", "app_lookup_check.py"),
    "/awards": ("awards.http", "usaspending_awards.py"),
    "/bank": ("bank.http", "bank_check.py"),
    "/carrier": ("carrier.http", "fmcsa_carrier.py"),
    "/csl": ("csl.http", "csl_screen.py"),
    "/drug": ("drug.http", "fda_drug_check.py"),
    "/epa": ("epa.http", "epa_screen.py"),
    "/faa": ("faa.http", "faa_lookup.py"),
    "/formd": ("formd.http", "edgar_formd.py"),
    "/fx": ("fx.http", "exchange_rate_check.py"),
    "/geocode": ("geocode.http", "address_geocode_check.py"),
    "/upc": ("upc.http", "upc_lookup.py"),
    "/links": ("links.http", "broken_link_check.py"),
    "/litigation": ("litigation.http", "courtlistener_recap.py"),
    "/meta": ("meta.http", "meta_tag_check.py"),
    "/nonprofit": ("nonprofit.http", "propublica_nonprofits.py"),
    "/pagespeed": ("pagespeed.http", "pagespeed_snapshot.py"),
    "/safety": ("safety.http", "safety_file.py"),
    "/trials": ("trials.http", "clinical_trial_check.py"),
    "/vin": ("vin.http", "vin_decode.py"),
}

# GET endpoints with no captured 200 report yet, and why (issue #243).
# Counted in the coverage section, never asserted from a capture that
# does not exist: each needs a 200 transcript captured from an
# environment that reaches its source, added to ENDPOINT_FIXTURES, and
# then removed here. Their 400 and 502 shapes are captured below.
_REFUSED = ("the capture for issue #243 ran in a container whose network policy refuses %s, so no "
            "200 report could be captured; a 200 transcript is owed from an environment that reaches it")
NO_ENDPOINT_CAPTURE = {
    "/disaster": ("the endpoint was added by issue #312 in a container whose network policy refuses "
                  "www.fema.gov, so no 200 report could be captured; a 200 transcript is owed from an "
                  "environment that reaches it"),
    "/domain": _REFUSED % "cloudflare-dns.com",
    "/earthquake": ("the capture for issue #317 ran in a container whose network policy refuses "
                    "earthquake.usgs.gov, so no 200 report could be captured; a 200 transcript is owed "
                    "from an environment that reaches it"),
    "/fda": _REFUSED % "api.fda.gov",
    "/flood": _REFUSED % "hazards.fema.gov",
    "/github": ("the capture container's only route to api.github.com adds credentials, so a 200 "
                "captured there would not show the keyless answer the endpoint promises; a keyless "
                "200 transcript is owed"),
    "/insider": ("the capture container holds no declared EDGAR fair access contact for live EDGAR "
                 "requests, so no 200 report could be captured; a 200 transcript is owed from a run "
                 "with a declared contact"),
    "/ofac": _REFUSED % "sanctionslistservice.ofac.treas.gov",
    "/oig": _REFUSED % "oig.hhs.gov",
}

# Offline 400 coverage (issue #225): one captured 400 transcript per
# wrapped endpoint above, taken from the bare path with no query string,
# which every wrapped endpoint answers 400 before any source fetch (the
# api endpoint suite proves the same cases with its fetch functions
# patched to raise). /formd is in this table because the capture server
# carries the operator contact it checks first; without that contact the
# endpoint answers 503 before any 400, which its provenance entry notes.
BAD_QUERY_FIXTURES = {
    "/app": "app-400.http",
    "/awards": "awards-400.http",
    "/bank": "bank-400.http",
    "/carrier": "carrier-400.http",
    "/csl": "csl-400.http",
    "/disaster": "disaster-400.http",
    "/domain": "domain-400.http",
    "/drug": "drug-400.http",
    "/earthquake": "earthquake-400.http",
    "/epa": "epa-400.http",
    "/faa": "faa-400.http",
    "/fda": "fda-400.http",
    "/flood": "flood-400.http",
    "/formd": "formd-400.http",
    "/fx": "fx-400.http",
    "/geocode": "geocode-400.http",
    "/upc": "upc-400.http",
    "/github": "github-400.http",
    "/insider": "insider-400.http",
    "/links": "links-400.http",
    "/litigation": "litigation-400.http",
    "/meta": "meta-400.http",
    "/nonprofit": "nonprofit-400.http",
    "/ofac": "ofac-400.http",
    "/oig": "oig-400.http",
    "/pagespeed": "pagespeed-400.http",
    "/safety": "safety-400.http",
    "/trials": "trials-400.http",
    "/vin": "vin-400.http",
}

# GET endpoints with no capturable offline 400, and why. Counted in the
# accounting section, never asserted from a capture that does not exist.
NO_400_CAPTURE = {
    "/": "the descriptor takes no query input, so it has no 400 shape",
    "/recall": ("the payment gate answers 402 to this tool's unpaid requests before any "
                "query validation, and the smoke never pays, so its 400 shape cannot be "
                "captured in this pattern"),
}

# Offline 502 coverage (issue #235): one replayed 502 transcript per
# wrapped endpoint above. The capture server ran with its proxy
# settings pointed at a closed local port, so the valid sample query's
# source fetch failed at transport and the endpoint answered its own
# 502; each provenance entry records that config. /faa's capture also
# pointed the tool cache at an empty folder, so it attempted its
# archive download instead of answering from its home folder cache.
SOURCE_FAILURE_FIXTURES = {
    "/app": "app-502.http",
    "/awards": "awards-502.http",
    "/bank": "bank-502.http",
    "/carrier": "carrier-502.http",
    "/csl": "csl-502.http",
    "/disaster": "disaster-502.http",
    "/domain": "domain-502.http",
    "/drug": "drug-502.http",
    "/earthquake": "earthquake-502.http",
    "/epa": "epa-502.http",
    "/faa": "faa-502.http",
    "/fda": "fda-502.http",
    "/flood": "flood-502.http",
    "/formd": "formd-502.http",
    "/fx": "fx-502.http",
    "/geocode": "geocode-502.http",
    "/upc": "upc-502.http",
    "/github": "github-502.http",
    "/insider": "insider-502.http",
    "/links": "links-502.http",
    "/litigation": "litigation-502.http",
    "/meta": "meta-502.http",
    "/nonprofit": "nonprofit-502.http",
    "/ofac": "ofac-502.http",
    "/oig": "oig-502.http",
    "/pagespeed": "pagespeed-502.http",
    "/safety": "safety-502.http",
    "/trials": "trials-502.http",
    "/vin": "vin-502.http",
}

# GET endpoints with no 502 shape to capture, and why. Counted in the
# accounting section, never asserted from a capture that does not exist.
NO_502_CAPTURE = {
    "/": "the descriptor answers from local state and fetches no source, so it has no 502 shape",
    "/recall": ("the payment gate answers 402 to this tool's unpaid requests before any "
                "source fetch, and the smoke never pays, so its 502 shape cannot be "
                "captured in this pattern"),
}

# Offline 503 coverage (issue #245): one replayed 503 transcript per
# endpoint whose entry in api/openapi.json declares a 503 response.
# Today that is /formd alone: the capture server ran without
# EDGAR_CONTACT, so the endpoint answered 503 before any fetch; its
# provenance entry records the missing contact as the capture config.
UNAVAILABLE_FIXTURES = {
    "/formd": "formd-503.http",
    "/insider": "insider-503.http",
}

# The reason every other GET endpoint is not captured for the 503
# shape: only an endpoint whose OpenAPI entry declares a 503 can be.
NO_503_REASON = "its entry in api/openapi.json declares no 503 response"


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
    named = [(key, name, None) for key, name in FIXTURE_NAMES.items()]
    named += [(path, name, path) for path, (name, _tool) in ENDPOINT_FIXTURES.items()]
    endpoints = {}
    for key, name, path in named:
        where = "fixture %s" % name if path is None else "fixture %s (endpoint %s)" % (name, path)
        entry = provenance.get(name)
        if not entry:
            raise SmokeError("no provenance for %s" % where)
        try:
            data = (fixtures / name).read_bytes()
        except OSError as err:
            raise SmokeError("cannot read %s: %s" % (where, err))
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise SmokeError("%s does not match its recorded sha256" % where)
        capture = parse_transcript(data.decode("utf-8"), entry["url"], entry["retrieved_utc"])
        if path is None:
            out[key] = capture
        else:
            endpoints[path] = capture
    out["endpoints"] = endpoints
    bad_queries = {}
    for path, name in BAD_QUERY_FIXTURES.items():
        where = "fixture %s (endpoint %s bad query)" % (name, path)
        entry = provenance.get(name)
        if not entry:
            raise SmokeError("no provenance for %s" % where)
        try:
            data = (fixtures / name).read_bytes()
        except OSError as err:
            raise SmokeError("cannot read %s: %s" % (where, err))
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise SmokeError("%s does not match its recorded sha256" % where)
        bad_queries[path] = parse_transcript(data.decode("utf-8"), entry["url"], entry["retrieved_utc"])
    out["bad_queries"] = bad_queries
    source_failures = {}
    for path, name in SOURCE_FAILURE_FIXTURES.items():
        where = "fixture %s (endpoint %s source failure)" % (name, path)
        entry = provenance.get(name)
        if not entry:
            raise SmokeError("no provenance for %s" % where)
        try:
            data = (fixtures / name).read_bytes()
        except OSError as err:
            raise SmokeError("cannot read %s: %s" % (where, err))
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise SmokeError("%s does not match its recorded sha256" % where)
        source_failures[path] = parse_transcript(data.decode("utf-8"), entry["url"], entry["retrieved_utc"])
    out["source_failures"] = source_failures
    unavailable = {}
    for path, name in UNAVAILABLE_FIXTURES.items():
        where = "fixture %s (endpoint %s unavailable)" % (name, path)
        entry = provenance.get(name)
        if not entry:
            raise SmokeError("no provenance for %s" % where)
        try:
            data = (fixtures / name).read_bytes()
        except OSError as err:
            raise SmokeError("cannot read %s: %s" % (where, err))
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise SmokeError("%s does not match its recorded sha256" % where)
        unavailable[path] = parse_transcript(data.decode("utf-8"), entry["url"], entry["retrieved_utc"])
    out["unavailable"] = unavailable
    out["declared_503_paths"] = repo_openapi_503_paths()
    out["coverage_paths"] = repo_openapi_get_paths()
    return out


def repo_openapi_get_paths():
    """The GET paths of the repo's own api/openapi.json, in document
    order: the coverage denominator. Read from the file beside the repo
    root (this tool lives in tools/), never from a capture, because a
    stale capture would undercount the surface. Unreadable is an error,
    not an empty list."""
    doc_file = Path(__file__).resolve().parent.parent / "api" / "openapi.json"
    try:
        doc = json.loads(doc_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise SmokeError("cannot read %s for the coverage count: %s" % (doc_file, err))
    paths = doc.get("paths") if isinstance(doc, dict) else None
    if not isinstance(paths, dict):
        raise SmokeError("%s has no paths object for the coverage count" % doc_file)
    return [path for path, ops in paths.items() if isinstance(ops, dict) and "get" in ops]


def repo_openapi_503_paths():
    """The GET paths whose entry in the repo's own api/openapi.json
    declares a 503 response: the 503 accounting's capturable set, read
    from the same file as the coverage denominator for the same
    reason. Unreadable is an error, not an empty list."""
    doc_file = Path(__file__).resolve().parent.parent / "api" / "openapi.json"
    try:
        doc = json.loads(doc_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise SmokeError("cannot read %s for the 503 count: %s" % (doc_file, err))
    paths = doc.get("paths") if isinstance(doc, dict) else None
    if not isinstance(paths, dict):
        raise SmokeError("%s has no paths object for the 503 count" % doc_file)
    out = []
    for path, ops in paths.items():
        if not (isinstance(ops, dict) and isinstance(ops.get("get"), dict)):
            continue
        responses = ops["get"].get("responses")
        if isinstance(responses, dict) and "503" in responses:
            out.append(path)
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


def check_endpoint_report(capture, path, tool):
    """The shape every wrapped fetcher endpoint answers with: its own
    rendered Markdown report in the delivery evidence format. `tool` is
    the fetcher the endpoint wraps (named in the section title); not
    every fetcher's report names it in the body, so it is not asserted."""
    content_type = next((h for h in capture.headers if h.lower().startswith("content-type:")), "")
    return [
        ("GET %s answers 200" % path, capture.status == 200),
        ("Content-Type is text/markdown", "text/markdown" in content_type),
        ("body is the endpoint report (Markdown title first)", capture.body.startswith("# ")),
        ("report carries a retrieved UTC timestamp",
         bool(RETRIEVED_UTC.search(capture.body))),
        ("report embeds the raw response transcript (fenced block)", "```" in capture.body),
    ]


def check_bad_query(capture, path):
    """The 400 shape: a plain text body naming the problem, no report."""
    content_type = next((h for h in capture.headers if h.lower().startswith("content-type:")), "")
    return [
        ("GET %s with no valid input answers 400" % path, capture.status == 400),
        ("Content-Type is text/plain", "text/plain" in content_type),
        ("body names the problem (starts with 'Bad request: ')",
         capture.body.startswith("Bad request: ") and len(capture.body.strip()) > len("Bad request:")),
        ("no report served (body is not a Markdown report)", not capture.body.startswith("# ")),
    ]


def check_bad_query_accounting(captures):
    """One line per GET endpoint in the repo's api/openapi.json: its 400
    shape is either captured in BAD_QUERY_FIXTURES or listed in
    NO_400_CAPTURE with the reason. An endpoint in both or neither
    fails here and is named."""
    lines = []
    for path in captures.get("coverage_paths", []):
        captured = path in captures.get("bad_queries", {})
        reasoned = path in NO_400_CAPTURE
        if captured and not reasoned:
            lines.append(("GET %s 400 shape captured in %s" % (path, BAD_QUERY_FIXTURES[path]), True))
        elif reasoned and not captured:
            lines.append(("GET %s 400 shape not capturable offline: %s" % (path, NO_400_CAPTURE[path]), True))
        else:
            lines.append(("GET %s 400 shape is not accounted for exactly once" % path, False))
    return lines


def check_source_failure(capture, path):
    """The 502 shape: a plain text body naming the failed source
    request, no report. Fetchers phrase the failure in their own
    words (fetch failed, request to ... failed, source failure), so
    the body assertion matches the word they all share."""
    content_type = next((h for h in capture.headers if h.lower().startswith("content-type:")), "")
    return [
        ("GET %s with its source failing answers 502" % path, capture.status == 502),
        ("Content-Type is text/plain", "text/plain" in content_type),
        ("body names the failure (mentions the failed fetch)",
         "fail" in capture.body.lower()),
        ("no report served (body is not a Markdown report)", not capture.body.startswith("# ")),
    ]


def check_source_failure_accounting(captures):
    """One line per GET endpoint in the repo's api/openapi.json: its 502
    shape is either captured in SOURCE_FAILURE_FIXTURES or listed in
    NO_502_CAPTURE with the reason. An endpoint in both or neither
    fails here and is named."""
    lines = []
    for path in captures.get("coverage_paths", []):
        captured = path in captures.get("source_failures", {})
        reasoned = path in NO_502_CAPTURE
        if captured and not reasoned:
            lines.append(("GET %s 502 shape captured in %s" % (path, SOURCE_FAILURE_FIXTURES[path]), True))
        elif reasoned and not captured:
            lines.append(("GET %s 502 shape not capturable offline: %s" % (path, NO_502_CAPTURE[path]), True))
        else:
            lines.append(("GET %s 502 shape is not accounted for exactly once" % path, False))
    return lines


def check_unavailable(capture, path):
    """The 503 shape: the endpoint is not configured on this server,
    so it answers before any fetch, in plain text naming the missing
    configuration (EDGAR_CONTACT for /formd) and stating that it
    fetches nothing; no report is served."""
    content_type = next((h for h in capture.headers if h.lower().startswith("content-type:")), "")
    return [
        ("GET %s unconfigured on the server answers 503" % path, capture.status == 503),
        ("Content-Type is text/plain", "text/plain" in content_type),
        ("body names the missing configuration (EDGAR_CONTACT)", "EDGAR_CONTACT" in capture.body),
        ("body states nothing was fetched", "fetches nothing" in capture.body),
        ("no report served (body is not a Markdown report)", not capture.body.startswith("# ")),
    ]


def check_unavailable_accounting(captures):
    """One line per GET endpoint in the repo's api/openapi.json: its
    503 shape is captured exactly when its entry in that document
    declares a 503 response, and reasoned with NO_503_REASON when it
    declares none. A declared endpoint with no capture, or a capture
    for an endpoint that declares no 503, fails here and is named."""
    lines = []
    declared = set(captures.get("declared_503_paths", []))
    for path in captures.get("coverage_paths", []):
        captured = path in captures.get("unavailable", {})
        if captured and path in declared:
            lines.append(("GET %s 503 shape captured in %s" % (path, UNAVAILABLE_FIXTURES[path]), True))
        elif not captured and path not in declared:
            lines.append(("GET %s 503 shape not capturable offline: %s" % (path, NO_503_REASON), True))
        else:
            lines.append(("GET %s 503 shape is not accounted for exactly once" % path, False))
    return lines


def check_coverage(captures):
    """One line per GET endpoint in the repo's api/openapi.json: covered
    when the run checked it (descriptor, payment, or an endpoint
    fixture), or listed in NO_ENDPOINT_CAPTURE with the reason it has no
    captured 200 yet. An endpoint in both or neither fails here and is
    named. The paths come from offline_captures, which read the repo
    file itself; a hand built captures dict without them covers only
    what it carries, so an unchecked endpoint still fails by name."""
    covered = {"/", "/recall"} | set(captures.get("endpoints", {}))
    lines = []
    for path in captures.get("coverage_paths", []):
        checked, reasoned = path in covered, path in NO_ENDPOINT_CAPTURE
        if checked and not reasoned:
            lines.append(("GET %s has an offline check" % path, True))
        elif reasoned and not checked:
            lines.append(("GET %s has no captured 200 yet: %s" % (path, NO_ENDPOINT_CAPTURE[path]), True))
        else:
            lines.append(("GET %s coverage is not accounted for exactly once" % path, False))
    return lines


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
    if "endpoints" in captures:
        number = 4
        for path, (_name, tool) in ENDPOINT_FIXTURES.items():
            capture = captures["endpoints"].get(path)
            if capture is None:
                continue
            parts.append(("%d. Endpoint GET %s (tools/%s)" % (number, path, tool), capture,
                          check_endpoint_report(capture, path, tool)))
            number += 1
        for path in BAD_QUERY_FIXTURES:
            capture = captures.get("bad_queries", {}).get(path)
            if capture is None:
                continue
            parts.append(("%d. Endpoint GET %s bad query (400)" % (number, path), capture,
                          check_bad_query(capture, path)))
            number += 1
        parts.append(("%d. Bad query (400) accounting" % number, captures["openapi"],
                      check_bad_query_accounting(captures)))
        number += 1
        for path in SOURCE_FAILURE_FIXTURES:
            capture = captures.get("source_failures", {}).get(path)
            if capture is None:
                continue
            parts.append(("%d. Endpoint GET %s source failure (502)" % (number, path), capture,
                          check_source_failure(capture, path)))
            number += 1
        parts.append(("%d. Source failure (502) accounting" % number, captures["openapi"],
                      check_source_failure_accounting(captures)))
        number += 1
        for path in UNAVAILABLE_FIXTURES:
            capture = captures.get("unavailable", {}).get(path)
            if capture is None:
                continue
            parts.append(("%d. Endpoint GET %s unavailable (503)" % (number, path), capture,
                          check_unavailable(capture, path)))
            number += 1
        parts.append(("%d. Unavailable (503) accounting" % number, captures["openapi"],
                      check_unavailable_accounting(captures)))
        number += 1
        parts.append(("%d. Endpoint coverage" % number, captures["openapi"],
                      check_coverage(captures)))
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
