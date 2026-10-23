#!/usr/bin/env python3
"""Pay per call recall check API.

One HTTP endpoint, GET /recall, that answers a product name (CPSC
SaferProducts) or a vehicle (NHTSA recalls, make + model + year) with a
sourced recall check in the delivery format from AGENT-BRIEF.md. The
check itself is produced by the fetchers in tools/, called as library
code, so the API prints exactly what those tools print: the claim
lines, the exact query, the UTC retrieval time, the source link, and
the complete raw response directly beneath the link. A failed fetch is
answered with an error status and no report, never with an empty
result.

Standard library only. The CPSC fetcher shells out to the system curl
executable (see tools/README.md), so the host needs curl on PATH.

Configuration: one optional environment value, PAYOUT_WALLET_ADDRESS,
the wallet that receives USDC for calls. When set it is echoed in the
X-Payout-Wallet response header and in the GET / descriptor. Nothing
else is read from the environment, and no key or secret exists in this
folder. Payment collection itself is the registry's job, not this
service's; this service only says where to pay.

Run locally:

    python3 api/recall_api.py                 # http://127.0.0.1:8000
    python3 api/recall_api.py --port 8080

Then:

    GET /                                      service descriptor (JSON)
    GET /recall?product=Instant+Pot            CPSC product check (Markdown)
    GET /recall?product=X&exact_name=X&near=Y  with a checked near match
    GET /recall?make=Hyundai&model=Elantra&year=2021   NHTSA vehicle check
    GET /recall?make=...&exclude=21V796000=reason      with an exclusion

`app` is a WSGI application for any WSGI host (gunicorn, Vercel's
Python runtime, and the like). `handle()` is the host-free core.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
from pathlib import Path
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import endpoints  # noqa: E402
from tools import cpsc_recalls, nhtsa_recalls  # noqa: E402

PAYOUT_ENV = "PAYOUT_WALLET_ADDRESS"
WALLET_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
SERVICE_NAME = "Hojo Research Agent recall check"
TEXT_MD = "text/markdown; charset=utf-8"
TEXT_PLAIN = "text/plain; charset=utf-8"
APP_JSON = "application/json; charset=utf-8"
OPENAPI_FILE = ROOT / "api" / "openapi.json"


class ConfigError(ValueError):
    """The one environment value is present but not a wallet address."""


class BadRequest(ValueError):
    """The query does not name a product or a complete vehicle."""


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def payout_wallet(env=None):
    """Return the payout wallet address from the environment, or None.

    A set but malformed value raises ConfigError rather than being
    passed through, so a typo never reaches a buyer as a payment
    destination. Only the shape (0x plus 40 hex digits) is checked.
    """
    env = os.environ if env is None else env
    value = env.get(PAYOUT_ENV, "").strip()
    if not value:
        return None
    if not WALLET_RE.match(value):
        raise ConfigError(
            "%s is set but is not an EVM address (0x followed by 40 hex digits); "
            "refusing to serve with a malformed payout address" % PAYOUT_ENV
        )
    return value


def descriptor(wallet):
    """The GET / document: what the endpoint takes and where to pay."""
    doc = {
        "service": SERVICE_NAME,
        "endpoint": "/recall",
        "method": "GET",
        "forms": {
            "product": {
                "params": ["product", "exact_name (optional)", "near (optional, repeatable; needs exact_name)"],
                "source": cpsc_recalls.ENDPOINT,
            },
            "vehicle": {
                "params": ["make", "model", "year", "exclude (optional, repeatable, CAMPAIGN=reason)"],
                "source": nhtsa_recalls.BASE_URL + nhtsa_recalls.DEFAULT_ENDPOINT,
            },
        },
        "response": "text/markdown in the delivery format: claims, exact query, UTC retrieval time, source link, raw response beneath the link",
        "payout_wallet": wallet,
        "payment": "USDC to payout_wallet; collected by the registry that lists this service, not by this endpoint",
    }
    # Every endpoint, including this module's own /recall, in one table
    # (issue #65). The keys above are unchanged for existing clients.
    doc["endpoints"] = dict(
        {"/recall": {"method": "GET", "tool": "tools/cpsc_recalls.py and tools/nhtsa_recalls.py",
                     "params": doc["forms"]["product"]["params"] + doc["forms"]["vehicle"]["params"],
                     "sources": [doc["forms"]["product"]["source"], doc["forms"]["vehicle"]["source"]]}},
        **endpoints.describe())
    return doc


# ----------------------------------------------------------------------
# The check
# ----------------------------------------------------------------------

def _single(query, key):
    values = query.get(key, [])
    values = [v for v in values if v.strip()]
    if len(values) > 1:
        raise BadRequest("give %s once" % key)
    return values[0].strip() if values else None


def _many(query, key):
    return [v for v in query.get(key, []) if v.strip()]


def product_check(product, exact_name=None, near=()):
    """CPSC check via tools/cpsc_recalls.py. Returns Markdown text."""
    if near and exact_name is None:
        raise BadRequest("near requires exact_name to state the exclusion rule")
    sections = []
    for index, name in enumerate([product, *near]):
        capture = cpsc_recalls.fetch(name)
        sections.append(cpsc_recalls.render_query(capture, exact_name, near=index > 0))
    head = [
        "# Recall check: %s" % cpsc_recalls.inline(product).strip('"'),
        "",
        "Observation only: this report records what the public CPSC recall "
        "database returned at the retrieval time stated below; no product was "
        "bought, sold, handled, or tested, and an empty result is not a safety "
        "clearance.",
        "",
        "Produced by the %s API from tools/cpsc_recalls.py. The query, the "
        "retrieval time, the source link, and the complete raw response are "
        "below." % SERVICE_NAME,
        "",
        "## CPSC recall search",
        "",
    ]
    return "\n".join(head) + "\n".join(sections)


def vehicle_check(make, model, year, exclude=()):
    """NHTSA check via tools/nhtsa_recalls.py. Returns Markdown text."""
    params = [("make", make), ("model", model), ("modelYear", year)]
    endpoint = nhtsa_recalls.DEFAULT_ENDPOINT
    exclusions = nhtsa_recalls.parse_exclusions(list(exclude))
    url = nhtsa_recalls.build_url(endpoint, params)
    retrieved, transcript, body = nhtsa_recalls.fetch(url)
    subject = "%s %s %s" % (year, make, model)
    lines = nhtsa_recalls.render_section(subject, endpoint, params, url, retrieved,
                                         transcript, body, exclusions, pretty=False)
    head = [
        "# Recall check: %s" % subject,
        "",
        "Observation only: this report records what the public NHTSA recall "
        "database returned at the retrieval time stated below; no vehicle was "
        "inspected, and an empty result is not a safety clearance.",
        "",
        "Produced by the %s API from tools/nhtsa_recalls.py. The query, the "
        "retrieval time, the source link, and the complete raw response are "
        "below." % SERVICE_NAME,
        "",
    ]
    return "\n".join(head + lines) + "\n"


def recall(query):
    """Dispatch a parsed query (dict of lists) to the right check.

    Returns Markdown text. Raises BadRequest for a bad query, and lets
    the fetchers' own errors through for the caller to map to 502.
    """
    product = _single(query, "product")
    make = _single(query, "make")
    model = _single(query, "model")
    year = _single(query, "year")
    if product and (make or model or year):
        raise BadRequest("give either product, or make+model+year, not both")
    if product:
        return product_check(product, _single(query, "exact_name"), _many(query, "near"))
    if make or model or year:
        missing = [k for k, v in (("make", make), ("model", model), ("year", year)) if not v]
        if missing:
            raise BadRequest("the vehicle form needs make, model and year; missing: %s" % ", ".join(missing))
        return vehicle_check(make, model, year, _many(query, "exclude"))
    raise BadRequest("give product=<name>, or make=<make>&model=<model>&year=<year>")


# ----------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------

def handle(method, path, query_string, wallet):
    """Host-free request handler. Returns (status, headers, body bytes)."""
    common = [("Cache-Control", "no-store")]
    if wallet:
        common.append(("X-Payout-Wallet", wallet))

    def reply(status, content_type, text):
        body = text.encode("utf-8")
        return status, [("Content-Type", content_type), ("Content-Length", str(len(body)))] + common, body

    if path == "/" or path == "":
        if method != "GET":
            return reply("405 Method Not Allowed", TEXT_PLAIN, "GET only.\n")
        return reply("200 OK", APP_JSON, json.dumps(descriptor(wallet), indent=2) + "\n")
    if path == "/openapi.json":
        # The shipped api/openapi.json, served byte for byte as it is on disk
        # (issue #85). A public descriptor like GET /: the payment gate only
        # intercepts /recall, so this route is never paid.
        if method != "GET":
            return reply("405 Method Not Allowed", TEXT_PLAIN, "GET only.\n")
        try:
            body = OPENAPI_FILE.read_bytes()
        except OSError as err:
            return reply("503 Service Unavailable", TEXT_PLAIN, "OpenAPI document unavailable: %s\n" % err)
        return "200 OK", [("Content-Type", APP_JSON), ("Content-Length", str(len(body)))] + common, body
    if path in endpoints.ROUTES:
        if method != "GET":
            return reply("405 Method Not Allowed", TEXT_PLAIN, "GET only.\n")
        query = urllib.parse.parse_qs(query_string or "", keep_blank_values=True)
        try:
            text = endpoints.call(path, query)
        except endpoints.BadRequest as err:
            return reply("400 Bad Request", TEXT_PLAIN, "Bad request: %s\n" % err)
        except endpoints.Unavailable as err:
            return reply("503 Service Unavailable", TEXT_PLAIN, "Endpoint unavailable, no report emitted: %s\n" % err)
        except endpoints.FetchFailed as err:
            return reply("502 Bad Gateway", TEXT_PLAIN, "%s\n" % err)
        except ValueError as err:
            # A fetcher's own validation of operator input against the response
            # (an exclusion naming a record the response does not hold).
            return reply("400 Bad Request", TEXT_PLAIN, "Bad request: %s\n" % err)
        except (urllib.error.URLError, OSError) as err:
            return reply("502 Bad Gateway", TEXT_PLAIN, "Fetch failed, no report emitted: %s\n" % err)
        return reply("200 OK", TEXT_MD, text)
    if path != "/recall":
        return reply("404 Not Found", TEXT_PLAIN, "Unknown path. GET / describes the service.\n")
    if method != "GET":
        return reply("405 Method Not Allowed", TEXT_PLAIN, "GET only.\n")

    query = urllib.parse.parse_qs(query_string or "", keep_blank_values=True)
    try:
        text = recall(query)
    except BadRequest as err:
        return reply("400 Bad Request", TEXT_PLAIN, "Bad request: %s\n" % err)
    except ValueError as err:
        # cpsc_recalls.FetchError is a ValueError; so are the NHTSA fetcher's
        # exclusion and parse errors. Neither becomes an empty result.
        if isinstance(err, cpsc_recalls.FetchError):
            return reply("502 Bad Gateway", TEXT_PLAIN,
                         "Fetch failed, no report emitted: %s\n" % err)
        return reply("400 Bad Request", TEXT_PLAIN, "Bad request: %s\n" % err)
    except (urllib.error.URLError, OSError) as err:
        return reply("502 Bad Gateway", TEXT_PLAIN,
                     "Fetch failed, no report emitted: %s\n" % err)
    return reply("200 OK", TEXT_MD, text)


def app(environ, start_response):
    """WSGI entry point."""
    try:
        wallet = payout_wallet()
    except ConfigError as err:
        body = ("Service misconfigured: %s\n" % err).encode("utf-8")
        start_response("500 Internal Server Error",
                       [("Content-Type", TEXT_PLAIN), ("Content-Length", str(len(body)))])
        return [body]
    status, headers, body = handle(
        environ.get("REQUEST_METHOD", "GET"),
        environ.get("PATH_INFO", "/"),
        environ.get("QUERY_STRING", ""),
        wallet,
    )
    start_response(status, headers)
    return [body]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the recall check API locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    try:
        wallet = payout_wallet()
    except ConfigError as err:
        sys.stderr.write("refusing to start: %s\n" % err)
        return 2
    sys.stderr.write("recall API on http://%s:%d/  payout wallet: %s\n"
                     % (args.host, args.port, wallet or "(not set)"))
    with make_server(args.host, args.port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
