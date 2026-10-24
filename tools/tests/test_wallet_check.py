"""Offline tests for tools/wallet_check.py (issue #337). No network.

Run from the repository root: python3 -m unittest discover -s tools/tests -v

The three captures are LIVE CAPTUREs made by H5 for this issue on
2026-10-24 with the tool's User-Agent, filed under fixtures/wallet/ next
to a provenance.json that records each query URL, retrieval time and
SHA-256:

- wallet-genesis.http: the genesis block address
  1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa. chain_stats: tx_count 67114,
  funded_txo_count 81049, funded_txo_sum 5768738760, spent 0.
  mempool_stats: 1 unconfirmed transaction, funded_txo_sum 3672.
- wallet-unused-empty.http: a never used address constructed locally by
  H5 (base58check over a hash160 derived from a fixture seed string);
  every figure in both stats blocks is 0.
- wallet-invalid.http: the genesis address with its last character
  changed, answered HTTP 400 with the plain text body
  "Invalid Bitcoin address".

Reshaped bodies in the failure tests are SYNTHETIC, built in code and
labelled where they appear. No fixture file is mutated.
"""

import io
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import wallet_check as wc  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "wallet"
RETRIEVED = "2026-10-24T12:50:00Z"
GENESIS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
UNUSED = "1FFPELMBGpG36ANkH62XZxs4tKwEpc4jqu"


def load_cap(name, url):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    status_line, rest = text.split("\n", 1)
    head, _, body = rest.partition("\n\n")
    headers = [tuple(line.split(": ", 1)) for line in head.split("\n") if ": " in line]
    return wc.Capture(url, RETRIEVED, status_line, headers, body)


def stub(cap):
    def fetch(url):
        if url != cap.url:
            raise AssertionError("unexpected URL fetched: %s" % url)
        return cap
    return fetch


GENESIS_CAP = load_cap("wallet-genesis.http", wc.address_url(GENESIS))
UNUSED_CAP = load_cap("wallet-unused-empty.http", wc.address_url(UNUSED))
INVALID_TEXT = (FIXTURES / "wallet-invalid.http").read_text(encoding="utf-8")


def report_text(address, cap):
    return "\n".join(wc.report(address, fetcher=stub(cap)))


class AddressShapeTests(unittest.TestCase):
    def test_check_address(self):
        self.assertEqual(wc.check_address(" %s " % GENESIS), GENESIS)
        self.assertEqual(wc.check_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
                         "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        self.assertEqual(wc.check_address("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"),
                         "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy")
        for bad in ["", None, "notanaddress", "0OIl0000000000000000000000000",
                    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlb", "1A1z", GENESIS + "xx"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                wc.check_address(bad)

    def test_address_url(self):
        self.assertEqual(wc.address_url(GENESIS), "https://mempool.space/api/address/%s" % GENESIS)


class GenesisTests(unittest.TestCase):
    """The live genesis capture: confirmed and unconfirmed kept apart."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text(GENESIS, GENESIS_CAP)

    def test_header_and_facts_line(self):
        self.assertIn("# Bitcoin address check: %s" % GENESIS, self.text)
        self.assertIn("are never added together", self.text)
        self.assertIn('Address (address) as shown: `"%s"`' % GENESIS, self.text)

    def test_confirmed_figures(self):
        self.assertIn("Confirmed figures (chain_stats):", self.text)
        self.assertIn("- Transaction count (tx_count) as shown: 67114", self.text)
        self.assertIn("- Total received (funded_txo_sum) as shown: 5768738760 satoshis", self.text)
        self.assertIn("- Total sent (spent_txo_sum) as shown: 0 satoshis", self.text)
        self.assertIn("- Funded output count (funded_txo_count) as shown: 81049", self.text)
        self.assertIn("- Current balance (funded_txo_sum minus spent_txo_sum): 5768738760 satoshis", self.text)

    def test_unconfirmed_block_separate_and_never_merged(self):
        self.assertIn("Unconfirmed figures (mempool_stats):", self.text)
        self.assertIn("- Transaction count (tx_count) as shown: 1", self.text)
        self.assertIn("- Total received (funded_txo_sum) as shown: 3672 satoshis", self.text)
        self.assertIn("- Net unconfirmed (funded_txo_sum minus spent_txo_sum): 3672 satoshis", self.text)
        # The merged figure (confirmed + unconfirmed received) appears nowhere.
        self.assertNotIn("5768742432", self.text)

    def test_no_zero_line(self):
        self.assertNotIn("Every figure in both stats blocks is zero", self.text)

    def test_evidence_complete(self):
        self.assertIn("Exact query URL: <%s>" % GENESIS_CAP.url, self.text)
        self.assertIn("UTC retrieval time: %s" % RETRIEVED, self.text)
        self.assertIn('"funded_txo_sum":5768738760', self.text)
        self.assertIn(GENESIS_CAP.body, self.text)  # complete raw response


class UnusedEmptyTests(unittest.TestCase):
    """The live never used capture: the proven all zero document."""

    @classmethod
    def setUpClass(cls):
        cls.text = report_text(UNUSED, UNUSED_CAP)

    def test_all_zero_stated_and_proven(self):
        self.assertIn("Every figure in both stats blocks is zero, as shown.", self.text)
        self.assertIn("The complete raw response below is the proof.", self.text)
        self.assertIn("- Transaction count (tx_count) as shown: 0", self.text)
        self.assertIn("- Current balance (funded_txo_sum minus spent_txo_sum): 0 satoshis", self.text)
        self.assertIn(UNUSED_CAP.body, self.text)


class InvalidAddressTests(unittest.TestCase):
    """The live refusal capture: HTTP 400, plain text body."""

    def test_the_captured_refusal_body(self):
        status_line, _, body = INVALID_TEXT.partition("\n\n")
        self.assertTrue(status_line.startswith("HTTP/1.1 400"))
        self.assertEqual(body.strip(), "Invalid Bitcoin address")

    def test_a_400_refusal_fails_closed(self):
        err = urllib.error.HTTPError(GENESIS_CAP.url, 400, "Bad Request", {}, None)
        with mock.patch.object(wc.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(wc.FetchError) as ctx:
                wc.fetch(GENESIS_CAP.url)
        self.assertIn("HTTP 400", str(ctx.exception))


class ShapeFailureTests(unittest.TestCase):
    """SYNTHETIC reshaped bodies: never a report, never figures."""

    def assert_no_report(self, body):
        cap = wc.Capture(GENESIS_CAP.url, RETRIEVED, "HTTP/1.1 200 OK", [], body)
        with self.assertRaises(wc.FetchError):
            wc.report(GENESIS, fetcher=stub(cap))

    def test_missing_mempool_stats(self):
        self.assert_no_report('{"address": "%s", "chain_stats": {"funded_txo_count": 0, "funded_txo_sum": 0,'
                              ' "spent_txo_count": 0, "spent_txo_sum": 0, "tx_count": 0}}' % GENESIS)

    def test_figure_as_string(self):
        self.assert_no_report('{"address": "%s", "chain_stats": {"funded_txo_count": 0,'
                              ' "funded_txo_sum": "5768738760", "spent_txo_count": 0, "spent_txo_sum": 0,'
                              ' "tx_count": 0}, "mempool_stats": {"funded_txo_count": 0, "funded_txo_sum": 0,'
                              ' "spent_txo_count": 0, "spent_txo_sum": 0, "tx_count": 0}}' % GENESIS)

    def test_plain_text_body(self):
        self.assert_no_report("Invalid Bitcoin address")


class TransportTests(unittest.TestCase):
    def test_url_error_fails_closed(self):
        with mock.patch.object(wc.urllib.request, "urlopen",
                               side_effect=urllib.error.URLError("down")):
            with self.assertRaises(wc.FetchError):
                wc.fetch(GENESIS_CAP.url)


class MainTests(unittest.TestCase):
    def run_main(self, argv, cap=None):
        out, err = io.StringIO(), io.StringIO()
        code = wc.main(argv, fetcher=stub(cap) if cap else None, stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_hit_exit_0(self):
        code, out, _ = self.run_main([GENESIS], GENESIS_CAP)
        self.assertEqual(code, 0)
        self.assertIn("5768738760", out)

    def test_bad_arguments_exit_2_without_a_report(self):
        for argv in (["notanaddress"], [], ["bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlb"]):
            code, out, err = self.run_main(argv)
            self.assertEqual(code, 2, argv)
            self.assertNotIn("# Bitcoin address check", out)
            self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
