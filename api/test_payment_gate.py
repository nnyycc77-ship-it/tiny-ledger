"""Tests for api/payment_gate.py. No network.

Run from the repository root: python3 -m unittest discover -s api -v

The facilitator is a recording fake patched over the module's HTTP
poster, and the wrapped application is a stub, so no test reaches the
real facilitator or the real CPSC/NHTSA sources. The one pass through
test that uses the real recall app patches the fetchers the same way
api/test_recall_api.py does. No payment payload here is a real signed
payment; the signatures are filler bytes, because verify and settle
are the facilitator's job and the facilitator is faked.
"""

import base64
import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import payment_gate, recall_api  # noqa: E402
from tools import cpsc_recalls  # noqa: E402

WALLET = "0x" + "cd" * 20
PAYER = "0x" + "ef" * 20
FACILITATOR = "https://facilitator.example.test"
REPORT = "# Recall check: stub report\n"
QUERY = "product=Vornado+VH101"
RESOURCE = "http://api.example.test/recall?" + QUERY
DESCRIPTION = ("Sourced recall check from public United States recall "
               "records (CPSC products, NHTSA vehicles)")

PAYLOAD = {
    "x402Version": 1,
    "scheme": "exact",
    "network": "base",
    "payload": {
        "signature": "0xfiller",
        "authorization": {
            "from": PAYER,
            "to": WALLET,
            "value": "50000",
            "validAfter": "0",
            "validBefore": "9999999999",
            "nonce": "0x00",
        },
    },
}
SETTLE_OK = {
    "success": True,
    "transaction": "0xsettled",
    "network": "base",
    "payer": PAYER,
    "errorReason": None,
}


def encode(payload):
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")


def stub_app(environ, start_response):
    body = REPORT.encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "text/markdown; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ])
    return [body]


class RecordingApp:
    """The wrapped app, noting whether it was ever called."""

    def __init__(self):
        self.calls = []

    def __call__(self, environ, start_response):
        self.calls.append(environ.get("PATH_INFO", ""))
        return stub_app(environ, start_response)


def environ_for(path="/recall", query=QUERY, method="GET", headers=None):
    env = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "SCRIPT_NAME": "",
        "wsgi.url_scheme": "http",
        "HTTP_HOST": "api.example.test",
        "SERVER_NAME": "api.example.test",
        "SERVER_PORT": "80",
    }
    for name, value in (headers or {}).items():
        env["HTTP_" + name.upper().replace("-", "_")] = value
    return env


def call(app, environ):
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(app(environ, start_response))
    return captured["status"], captured["headers"], body


def make_gate(wrapped=None, **env):
    env.setdefault(recall_api.PAYOUT_ENV, WALLET)
    env.setdefault(payment_gate.FACILITATOR_ENV, FACILITATOR)
    return payment_gate.PaymentGate(
        wrapped if wrapped is not None else stub_app,
        payment_gate.GateConfig(env),
    )


class ConfigTests(unittest.TestCase):
    def test_unset_wallet_is_refused(self):
        with self.assertRaises(recall_api.ConfigError):
            payment_gate.GateConfig({})

    def test_malformed_wallet_is_refused(self):
        with self.assertRaises(recall_api.ConfigError):
            payment_gate.GateConfig({recall_api.PAYOUT_ENV: "0xnotawallet"})

    def test_defaults(self):
        config = payment_gate.GateConfig({recall_api.PAYOUT_ENV: WALLET})
        self.assertEqual(config.pay_to, WALLET)
        self.assertEqual(config.facilitator_url,
                         payment_gate.DEFAULT_FACILITATOR)
        self.assertEqual(config.price, "50000")
        self.assertEqual(config.network, "base")
        self.assertEqual(config.asset, payment_gate.DEFAULT_ASSET)

    def test_overrides_and_trailing_slash(self):
        config = payment_gate.GateConfig({
            recall_api.PAYOUT_ENV: WALLET,
            payment_gate.FACILITATOR_ENV: FACILITATOR + "/",
            payment_gate.PRICE_ENV: "10000",
            payment_gate.NETWORK_ENV: "base-sepolia",
            payment_gate.ASSET_ENV: "0x" + "12" * 20,
        })
        self.assertEqual(config.facilitator_url, FACILITATOR)
        self.assertEqual(config.price, "10000")
        self.assertEqual(config.network, "base-sepolia")
        self.assertEqual(config.asset, "0x" + "12" * 20)

    def test_non_digit_price_is_refused(self):
        with self.assertRaises(recall_api.ConfigError):
            payment_gate.GateConfig({
                recall_api.PAYOUT_ENV: WALLET,
                payment_gate.PRICE_ENV: "0.05",
            })


class UnpaidTests(unittest.TestCase):
    def test_402_shape_and_required_fields(self):
        status, headers, body = call(make_gate(), environ_for())
        self.assertEqual(status, "402 Payment Required")
        self.assertEqual(headers["Content-Type"], payment_gate.APP_JSON)
        doc = json.loads(body)
        self.assertEqual(doc["x402Version"], 1)
        self.assertEqual(doc["error"], "X-PAYMENT header is required")
        self.assertEqual(len(doc["accepts"]), 1)
        req = doc["accepts"][0]
        self.assertEqual(req["scheme"], "exact")
        self.assertEqual(req["network"], "base")
        self.assertEqual(req["maxAmountRequired"], "50000")
        self.assertEqual(req["resource"], RESOURCE)
        self.assertEqual(req["description"], DESCRIPTION)
        self.assertEqual(len(req["description"]), 93)
        self.assertLessEqual(len(req["description"]), 500)
        self.assertEqual(req["mimeType"], "text/markdown")
        self.assertEqual(req["payTo"], WALLET)
        self.assertEqual(req["maxTimeoutSeconds"], 60)
        self.assertEqual(req["asset"], payment_gate.DEFAULT_ASSET)
        self.assertEqual(req["extra"], {"name": "USD Coin", "version": "2"})
        bazaar = doc["extensions"]["bazaar"]
        self.assertEqual(bazaar["info"]["input"]["type"], "http")
        self.assertEqual(bazaar["info"]["input"]["method"], "GET")
        self.assertEqual(
            bazaar["info"]["input"]["queryParams"],
            {"product": "Instant Pot", "make": "Hyundai",
             "model": "Elantra", "year": "2021"},
        )
        self.assertEqual(bazaar["info"]["output"]["type"], "text/markdown")
        properties = bazaar["schema"]["properties"]
        for name in ["product", "exact_name", "near",
                     "make", "model", "year", "exclude"]:
            self.assertEqual(properties[name]["type"], "string")

    def test_resource_url_carries_the_query_string(self):
        env = environ_for(query="make=Hyundai&model=Elantra&year=2021")
        _, _, body = call(make_gate(), env)
        req = json.loads(body)["accepts"][0]
        self.assertEqual(
            req["resource"],
            "http://api.example.test/recall?make=Hyundai&model=Elantra&year=2021")

    def test_root_descriptor_passes_through_unpaid(self):
        gate = make_gate(wrapped=recall_api.app)
        with patch.dict(os.environ, {recall_api.PAYOUT_ENV: WALLET}):
            status, headers, body = call(gate, environ_for(path="/", query=""))
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(body)["payout_wallet"], WALLET)
        self.assertEqual(headers["X-Payout-Wallet"], WALLET)

    def test_non_get_and_other_paths_pass_through(self):
        wrapped = RecordingApp()
        gate = make_gate(wrapped=wrapped)
        status, _, body = call(gate, environ_for(method="POST"))
        self.assertEqual(status, "200 OK")
        self.assertEqual(body.decode(), REPORT)
        status, _, _ = call(gate, environ_for(path="/nope", query=""))
        self.assertEqual(status, "200 OK")
        self.assertEqual(wrapped.calls, ["/recall", "/nope"])


class PaymentHeaderTests(unittest.TestCase):
    def assert_invalid_payload(self, header):
        wrapped = RecordingApp()
        gate = make_gate(wrapped=wrapped)
        status, headers, body = call(
            gate, environ_for(headers={"X-PAYMENT": header}))
        self.assertEqual(status, "402 Payment Required")
        self.assertEqual(headers["Content-Type"], payment_gate.APP_JSON)
        doc = json.loads(body)
        self.assertEqual(doc["error"], "invalid payment payload")
        self.assertEqual(doc["accepts"][0]["payTo"], WALLET)
        self.assertEqual(wrapped.calls, [])

    def test_garbage_header(self):
        self.assert_invalid_payload("garbage!!!")

    def test_base64_of_non_json(self):
        self.assert_invalid_payload(
            base64.b64encode(b"hello").decode("ascii"))

    def test_base64_of_a_json_list(self):
        self.assert_invalid_payload(encode([1, 2, 3]))


class FacilitatorFlowTests(unittest.TestCase):
    def setUp(self):
        self.wrapped = RecordingApp()
        self.gate = make_gate(wrapped=self.wrapped)
        self.env = environ_for(headers={"X-PAYMENT": encode(PAYLOAD)})

    def poster_returning(self, verify, settle=None):
        calls = []

        def fake(url, payload):
            calls.append((url, payload))
            if url.endswith("/verify"):
                return verify
            if url.endswith("/settle"):
                return settle
            raise AssertionError("unexpected facilitator URL %s" % url)

        fake.calls = calls
        return fake

    def test_rejected_payment_is_402_with_the_facilitator_reason(self):
        fake = self.poster_returning(
            {"isValid": False, "invalidReason": "insufficient_funds",
             "payer": PAYER})
        with patch.object(payment_gate, "facilitator_post", side_effect=fake):
            status, _, body = call(self.gate, self.env)
        self.assertEqual(status, "402 Payment Required")
        doc = json.loads(body)
        self.assertEqual(doc["error"], "insufficient_funds")
        self.assertEqual(doc["accepts"][0]["resource"], RESOURCE)
        self.assertEqual(len(fake.calls), 1)
        url, payload = fake.calls[0]
        self.assertEqual(url, FACILITATOR + "/verify")
        self.assertEqual(payload["paymentPayload"], PAYLOAD)
        self.assertEqual(
            payload["paymentRequirements"]["payTo"], WALLET)
        self.assertEqual(self.wrapped.calls, [])

    def test_settle_failure_is_402_with_the_facilitator_reason(self):
        fake = self.poster_returning(
            {"isValid": True, "invalidReason": None, "payer": PAYER},
            {"success": False, "transaction": "", "network": "base",
             "payer": PAYER, "errorReason": "settlement_reverted"})
        with patch.object(payment_gate, "facilitator_post", side_effect=fake):
            status, _, body = call(self.gate, self.env)
        self.assertEqual(status, "402 Payment Required")
        self.assertEqual(json.loads(body)["error"], "settlement_reverted")
        self.assertEqual([url for url, _ in fake.calls],
                         [FACILITATOR + "/verify", FACILITATOR + "/settle"])
        self.assertEqual(self.wrapped.calls, [])

    def test_valid_payment_settles_then_serves_with_the_receipt(self):
        fake = self.poster_returning(
            {"isValid": True, "invalidReason": None, "payer": PAYER},
            SETTLE_OK)
        with patch.object(payment_gate, "facilitator_post", side_effect=fake):
            status, headers, body = call(self.gate, self.env)
        self.assertEqual(status, "200 OK")
        self.assertEqual(body.decode(), REPORT)
        self.assertEqual(self.wrapped.calls, ["/recall"])
        receipt = json.loads(
            base64.b64decode(headers["X-PAYMENT-RESPONSE"]).decode("utf-8"))
        self.assertEqual(receipt, SETTLE_OK)
        self.assertEqual([url for url, _ in fake.calls],
                         [FACILITATOR + "/verify", FACILITATOR + "/settle"])
        # The settle call carries the same body as the verify call.
        self.assertEqual(fake.calls[0][1], fake.calls[1][1])

    def test_facilitator_down_at_verify_is_502_with_no_report(self):
        def down(url, payload):
            raise payment_gate.FacilitatorError("connection refused")

        with patch.object(payment_gate, "facilitator_post", side_effect=down):
            status, _, body = call(self.gate, self.env)
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("no report served", body.decode())
        self.assertNotIn("Recall check", body.decode())
        self.assertEqual(self.wrapped.calls, [])

    def test_facilitator_down_at_settle_is_502_with_no_report(self):
        calls = []

        def flaky(url, payload):
            calls.append(url)
            if url.endswith("/verify"):
                return {"isValid": True, "invalidReason": None, "payer": PAYER}
            raise payment_gate.FacilitatorError("connection reset")

        with patch.object(payment_gate, "facilitator_post", side_effect=flaky):
            status, _, body = call(self.gate, self.env)
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("Recall check", body.decode())
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.wrapped.calls, [])


class FacilitatorPostTests(unittest.TestCase):
    def test_round_trip(self):
        seen = {}

        class Reply:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return b'{"isValid": true, "invalidReason": null}'

        def fake_urlopen(request, timeout=None):
            seen["url"] = request.full_url
            seen["data"] = json.loads(request.data.decode("utf-8"))
            seen["timeout"] = timeout
            return Reply()

        with patch.object(payment_gate.urllib.request, "urlopen", fake_urlopen):
            result = payment_gate.facilitator_post(
                FACILITATOR + "/verify", {"paymentPayload": PAYLOAD})
        self.assertEqual(result, {"isValid": True, "invalidReason": None})
        self.assertEqual(seen["url"], FACILITATOR + "/verify")
        self.assertEqual(seen["data"], {"paymentPayload": PAYLOAD})
        self.assertEqual(seen["timeout"], payment_gate.FACILITATOR_TIMEOUT)

    def test_http_error_with_a_json_verdict_is_read(self):
        body = b'{"isValid": false, "invalidReason": "bad_signature"}'
        error = urllib.error.HTTPError(
            FACILITATOR + "/verify", 400, "Bad Request", {}, io.BytesIO(body))
        with patch.object(payment_gate.urllib.request, "urlopen",
                          side_effect=error):
            result = payment_gate.facilitator_post(
                FACILITATOR + "/verify", {"paymentPayload": PAYLOAD})
        self.assertEqual(result["invalidReason"], "bad_signature")

    def test_unreachable_and_unparsable_raise_facilitator_error(self):
        with patch.object(payment_gate.urllib.request, "urlopen",
                          side_effect=urllib.error.URLError("refused")):
            with self.assertRaises(payment_gate.FacilitatorError):
                payment_gate.facilitator_post(
                    FACILITATOR + "/verify", {"paymentPayload": PAYLOAD})

        class Garbage:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return b"not json"

        with patch.object(payment_gate.urllib.request, "urlopen",
                          return_value=Garbage()):
            with self.assertRaises(payment_gate.FacilitatorError):
                payment_gate.facilitator_post(
                    FACILITATOR + "/verify", {"paymentPayload": PAYLOAD})


class WrappedServiceTests(unittest.TestCase):
    def test_module_app_without_a_wallet_is_a_500_not_a_report(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(recall_api.PAYOUT_ENV, None)
            status, _, body = call(payment_gate.app, environ_for())
        self.assertEqual(status, "500 Internal Server Error")
        self.assertIn("misconfigured", body.decode())
        self.assertNotIn("Recall check", body.decode())

    def test_gated_real_app_serves_the_report_after_settlement(self):
        verify = {"isValid": True, "invalidReason": None, "payer": PAYER}

        def fake(url, payload):
            return verify if url.endswith("/verify") else SETTLE_OK

        def fake_cpsc_fetch(product):
            raise cpsc_recalls.FetchError("no recorded capture in gate tests")

        gate = make_gate(wrapped=recall_api.app)
        env = environ_for(headers={"X-PAYMENT": encode(PAYLOAD)})
        with patch.object(payment_gate, "facilitator_post", side_effect=fake), \
             patch.object(cpsc_recalls, "fetch", side_effect=fake_cpsc_fetch), \
             patch.dict(os.environ, {recall_api.PAYOUT_ENV: WALLET}):
            status, headers, body = call(gate, env)
        # The gate settled and passed through; the report itself failed
        # at the (faked) source fetch, which the API answers 502. The
        # receipt header rides on whatever the service answers.
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("X-PAYMENT-RESPONSE", headers)
        self.assertIn("no report emitted", body.decode())


if __name__ == "__main__":
    unittest.main()
