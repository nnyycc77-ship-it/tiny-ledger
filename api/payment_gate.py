#!/usr/bin/env python3
"""x402 payment gate for the recall check API.

A standard library WSGI middleware in front of api/recall_api.py. Every
request passes through untouched except GET /recall, which is paid:
0.05 USDC per call under the x402 "exact" scheme on Base mainnet,
settled through a facilitator (PayAI by default). The flow follows the
x402 v1 resource server shape:

1. GET /recall with no X-PAYMENT header is answered 402 with the
   payment requirements (the "accepts" list) and a Bazaar discovery
   extension, so registries can index the endpoint from the 402 alone.
2. A call carrying X-PAYMENT (the base64 JSON payment payload) is
   verified with the facilitator (POST /verify). A payload the
   facilitator rejects is answered 402 with its reason; a facilitator
   that cannot be reached is answered 502 and no report is served.
3. A verified payment is settled (POST /settle) before the report is
   produced, and the settle receipt rides back in the
   X-PAYMENT-RESPONSE header, base64 JSON, per the x402 spec.

Configuration is environment only; nothing is read from files and no
key or secret exists here (the facilitator used needs none):

    PAYOUT_WALLET_ADDRESS   where the USDC lands. Required: the gate
                            refuses to wrap without it, because a paid
                            endpoint with nowhere to pay is pointless.
                            Validated by api.recall_api.payout_wallet.
    FACILITATOR_URL         default https://facilitator.payai.network
    X402_PRICE_ATOMIC       default "50000" (0.05 USDC, 6 decimals)
    X402_NETWORK            default "base"
    X402_ASSET              default USDC on Base,
                            0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

Run it (from the repository root):

    PAYOUT_WALLET_ADDRESS=0x... python3 server.py

or point any WSGI host at `api.payment_gate:app`.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import recall_api  # noqa: E402

FACILITATOR_ENV = "FACILITATOR_URL"
PRICE_ENV = "X402_PRICE_ATOMIC"
NETWORK_ENV = "X402_NETWORK"
ASSET_ENV = "X402_ASSET"

DEFAULT_FACILITATOR = "https://facilitator.payai.network"
DEFAULT_PRICE = "50000"
DEFAULT_NETWORK = "base"
DEFAULT_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DESCRIPTION = ("Sourced recall check from public United States recall "
               "records (CPSC products, NHTSA vehicles)")
MAX_TIMEOUT_SECONDS = 60
FACILITATOR_TIMEOUT = 30
APP_JSON = "application/json; charset=utf-8"
TEXT_PLAIN = "text/plain; charset=utf-8"


class FacilitatorError(RuntimeError):
    """The facilitator could not be reached or answered unusably."""


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

class GateConfig:
    """The gate's configuration, read from an environment mapping."""

    def __init__(self, env=None):
        env = os.environ if env is None else env
        wallet = recall_api.payout_wallet(env)
        if wallet is None:
            raise recall_api.ConfigError(
                "%s is not set; refusing to gate a paid endpoint with no "
                "payout address" % recall_api.PAYOUT_ENV
            )
        self.pay_to = wallet
        self.facilitator_url = (env.get(FACILITATOR_ENV, "")
                                or DEFAULT_FACILITATOR).rstrip("/")
        self.price = env.get(PRICE_ENV, "") or DEFAULT_PRICE
        if not self.price.isdigit():
            raise recall_api.ConfigError(
                "%s is set but is not an atomic amount (digits only): %r"
                % (PRICE_ENV, self.price)
            )
        self.network = env.get(NETWORK_ENV, "") or DEFAULT_NETWORK
        self.asset = env.get(ASSET_ENV, "") or DEFAULT_ASSET


# ----------------------------------------------------------------------
# The 402 document
# ----------------------------------------------------------------------

def request_url(environ):
    """The full URL of the current request, from the WSGI environ."""
    scheme = environ.get("wsgi.url_scheme", "http")
    host = environ.get("HTTP_HOST", "")
    if not host:
        host = environ.get("SERVER_NAME", "")
        port = environ.get("SERVER_PORT", "")
        if port and port != ("443" if scheme == "https" else "80"):
            host = "%s:%s" % (host, port)
    path = (environ.get("SCRIPT_NAME", "")
            + environ.get("PATH_INFO", "")
            or "/")
    url = "%s://%s%s" % (scheme, host, path)
    query = environ.get("QUERY_STRING", "")
    if query:
        url += "?" + query
    return url


def payment_requirements(config, resource):
    """One x402 v1 "exact" payment requirement for this resource."""
    return {
        "scheme": "exact",
        "network": config.network,
        "maxAmountRequired": config.price,
        "resource": resource,
        "description": DESCRIPTION,
        "mimeType": "text/markdown",
        "payTo": config.pay_to,
        "maxTimeoutSeconds": MAX_TIMEOUT_SECONDS,
        "asset": config.asset,
        "extra": {"name": "USD Coin", "version": "2"},
    }


def bazaar_extension():
    """Bazaar discovery metadata: how to call the endpoint, what returns."""
    text = {"type": "string"}
    return {
        "info": {
            "input": {
                "type": "http",
                "method": "GET",
                "queryParams": {
                    "product": "Instant Pot",
                    "make": "Hyundai",
                    "model": "Elantra",
                    "year": "2021",
                },
            },
            "output": {
                "type": "text/markdown",
                "example": "# Recall check: ...",
            },
        },
        "schema": {
            "type": "object",
            "properties": {
                "product": dict(
                    text,
                    description="Product name for a CPSC SaferProducts "
                                "check. Give this form, or make+model+year.",
                ),
                "exact_name": dict(
                    text,
                    description="Optional: exact product name near matches "
                                "are checked against; required with near.",
                ),
                "near": dict(
                    text,
                    description="Optional, repeatable: a near-match product "
                                "name to check and exclude with a reason; "
                                "needs exact_name.",
                ),
                "make": dict(text, description="Vehicle make (NHTSA form)."),
                "model": dict(text, description="Vehicle model (NHTSA form)."),
                "year": dict(text, description="Vehicle model year (NHTSA form)."),
                "exclude": dict(
                    text,
                    description="Optional, repeatable: CAMPAIGN=reason "
                                "exclusion for the vehicle form.",
                ),
            },
            "additionalProperties": False,
        },
    }


def payment_required_body(config, resource, error):
    """The x402 v1 402 document: error, accepts, discovery extension."""
    return {
        "x402Version": 1,
        "error": error,
        "accepts": [payment_requirements(config, resource)],
        "extensions": {"bazaar": bazaar_extension()},
    }


# ----------------------------------------------------------------------
# Facilitator
# ----------------------------------------------------------------------

def facilitator_post(url, payload):
    """POST JSON to a facilitator endpoint; return the parsed JSON object.

    A facilitator that answers with an HTTP error status but a JSON
    object body (the verify and settle verdicts are JSON objects) is
    read normally; anything else unusable raises FacilitatorError, so
    the caller refuses to serve rather than guess.
    """
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=FACILITATOR_TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as err:
        raw = err.read()
    except (urllib.error.URLError, OSError) as err:
        raise FacilitatorError("facilitator request to %s failed: %s" % (url, err))
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as err:
        raise FacilitatorError(
            "facilitator at %s answered unparsable JSON: %s" % (url, err))
    if not isinstance(parsed, dict):
        raise FacilitatorError(
            "facilitator at %s answered a non object JSON body" % url)
    return parsed


# ----------------------------------------------------------------------
# The gate
# ----------------------------------------------------------------------

class PaymentGate:
    """WSGI middleware: x402 exact payment in front of GET /recall."""

    def __init__(self, wrapped, config):
        self.wrapped = wrapped
        self.config = config

    def __call__(self, environ, start_response):
        if (environ.get("REQUEST_METHOD", "GET") != "GET"
                or environ.get("PATH_INFO", "") != "/recall"):
            return self.wrapped(environ, start_response)

        config = self.config
        resource = request_url(environ)
        header = environ.get("HTTP_X_PAYMENT", "")
        if not header:
            return self._payment_required(
                start_response, resource, "X-PAYMENT header is required")
        try:
            payload = json.loads(
                base64.b64decode(header, validate=True).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payment payload is not a JSON object")
        except ValueError:
            return self._payment_required(
                start_response, resource, "invalid payment payload")

        body = {
            "paymentPayload": payload,
            "paymentRequirements": payment_requirements(config, resource),
        }
        try:
            verdict = facilitator_post(config.facilitator_url + "/verify", body)
        except FacilitatorError as err:
            return self._bad_gateway(start_response, err)
        if not verdict.get("isValid"):
            return self._payment_required(
                start_response, resource,
                verdict.get("invalidReason") or "payment verification failed")
        try:
            settled = facilitator_post(config.facilitator_url + "/settle", body)
        except FacilitatorError as err:
            return self._bad_gateway(start_response, err)
        if not settled.get("success"):
            return self._payment_required(
                start_response, resource,
                settled.get("errorReason") or "payment settlement failed")

        receipt = base64.b64encode(
            json.dumps(settled).encode("utf-8")).decode("ascii")

        def gated_start_response(status, headers, exc_info=None):
            return start_response(
                status,
                list(headers) + [("X-PAYMENT-RESPONSE", receipt)],
                exc_info,
            )

        return self.wrapped(environ, gated_start_response)

    def _payment_required(self, start_response, resource, error):
        body = json.dumps(
            payment_required_body(self.config, resource, error),
            indent=2).encode("utf-8")
        start_response("402 Payment Required", [
            ("Content-Type", APP_JSON),
            ("Content-Length", str(len(body))),
        ])
        return [body]

    def _bad_gateway(self, start_response, err):
        body = ("Payment facilitator unavailable, no report served: %s\n"
                % err).encode("utf-8")
        start_response("502 Bad Gateway", [
            ("Content-Type", TEXT_PLAIN),
            ("Content-Length", str(len(body))),
        ])
        return [body]


def build_app(env=None):
    """The gated application: recall_api.app behind a PaymentGate.

    Raises recall_api.ConfigError when the payout wallet is unset or
    malformed, so a host that builds at startup refuses to start.
    """
    return PaymentGate(recall_api.app, GateConfig(env))


def app(environ, start_response):
    """WSGI entry point: `api.payment_gate:app` for any WSGI host.

    A missing or malformed payout wallet is answered 500, the same
    misconfigured shape api.recall_api.app uses, never a served report.
    """
    try:
        gate = build_app()
    except recall_api.ConfigError as err:
        body = ("Service misconfigured: %s\n" % err).encode("utf-8")
        start_response("500 Internal Server Error", [
            ("Content-Type", TEXT_PLAIN),
            ("Content-Length", str(len(body))),
        ])
        return [body]
    return gate(environ, start_response)
