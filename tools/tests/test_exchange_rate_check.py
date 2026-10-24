"""Tests for tools/exchange_rate_check.py (issue #168). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_exchange_rate_check.py' -v

Fixtures: fixtures/frankfurter/*.http are five real, keyless responses from
the live Frankfurter API v1, captured by the coordinator under Option B on
issue #168 (this container cannot reach api.frankfurter.dev) and saved as
posted: status line, headers in the order returned, a blank line, then the
body. Each one's URL, comment, body size and body SHA-256 (as the
coordinator posted it) and the whole file's SHA-256 are in
fixtures/frankfurter/provenance.json; both hashes are checked here.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import exchange_rate_check as fx  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "frankfurter"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RETRIEVED = "2026-10-24T03:06:02Z"  # test value; the captures' own times are in provenance.json

LATEST = "latest-USD-EUR.http"
AMOUNT = "latest-USD-EUR-amount-100.http"
WEEKEND = "date-2024-01-06-USD-EUR.http"
UNKNOWN = "latest-USD-XYZ-404.http"
CURRENCIES = "currencies.http"

QUERIES = {  # fixture -> (base, target, amount, date) the capture was made with
    LATEST: ("USD", "EUR", None, None),
    AMOUNT: ("USD", "EUR", "100", None),
    WEEKEND: ("USD", "EUR", None, "2024-01-06"),
    UNKNOWN: ("USD", "XYZ", None, None),
}


def capture(name):
    """(retrieved, transcript, body) for a fixture, as fetch() returns them."""
    transcript = (FIXTURES / name).read_text(encoding="utf-8")
    return RETRIEVED, transcript, transcript.partition("\n\n")[2]


def section(name):
    query = QUERIES[name]
    return "\n".join(fx.render_section(*query, fx.build_url(*query), *capture(name)))


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.glob("*.http")))
        for name, entry in PROVENANCE.items():
            raw = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], name)
            body = raw.split(b"\n\n", 1)[1]
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry["body_sha256"], name)
            self.assertEqual(len(body), entry["body_bytes"], name)

    def test_the_tool_builds_each_captured_url(self):
        for name, query in QUERIES.items():
            self.assertEqual(fx.build_url(*query), PROVENANCE[name]["url"], name)


class Query(unittest.TestCase):
    def test_codes(self):
        self.assertEqual(fx.check_code(" usd ", "base"), "USD")
        for bad in ("", "US", "USDX", "U$D", "12A"):
            with self.assertRaises(ValueError, msg=bad):
                fx.check_code(bad, "base")
        with self.assertRaisesRegex(ValueError, "same currency"):
            fx.check_query("USD", "usd")

    def test_amount_and_date(self):
        self.assertIsNone(fx.check_amount(None))
        self.assertEqual(fx.check_amount("100"), "100")
        self.assertEqual(fx.check_amount("12.5"), "12.5")
        for bad in ("0", "-5", "1e3", "abc", "1,000"):
            with self.assertRaises(ValueError, msg=bad):
                fx.check_amount(bad)
        self.assertEqual(fx.check_date("2024-01-06"), "2024-01-06")
        for bad in ("2024-1-6", "06/01/2024", "2024-02-30", "latest"):
            with self.assertRaises(ValueError, msg=bad):
                fx.check_date(bad)


class Render(unittest.TestCase):
    def test_latest_rate_as_shown(self):
        text = section(LATEST)
        self.assertIn("QUERY: base = USD, symbols = EUR, date = latest answered HTTP/1.1 200 OK (retrieved %s)."
                      % RETRIEVED, text)
        self.assertIn("RATE: 1.0 USD = 0.89342 EUR, rate date 2026-10-23 (each as shown in the response).", text)
        self.assertIn("- rates.EUR as shown: 0.89342", text)
        self.assertNotIn("no arithmetic", text)

    def test_amount_is_the_apis_own_figure(self):
        text = section(AMOUNT)
        self.assertIn("RATE: 100.0 USD = 89.34 EUR, rate date 2026-10-23", text)
        self.assertIn("- The figure for EUR is the API's own conversion of the amount sent; this tool does "
                      "no arithmetic.", text)

    def test_numbers_keep_their_source_text(self):
        # A test body, not a recording: 1.10 and 0.900 would print as 1.1
        # and 0.9 if parsed as floats.
        body = '{"amount":1.10,"base":"USD","date":"2026-10-23","rates":{"EUR":0.900}}'
        text = "\n".join(fx.render_section("USD", "EUR", None, None, fx.build_url("USD", "EUR"),
                                           RETRIEVED, "HTTP/1.1 200 OK\n\n" + body, body))
        self.assertIn("RATE: 1.10 USD = 0.900 EUR", text)

    def test_weekend_date_is_stated_as_the_responses_own(self):
        text = section(WEEKEND)
        self.assertIn("RATE: 1.0 USD = 0.91567 EUR, rate date 2024-01-05", text)
        self.assertIn("- The date asked was 2024-01-06; the response's own date is 2024-01-05, so the rate is "
                      "for 2024-01-05.", text)

    def test_unknown_currency_is_proven_by_the_transcript(self):
        text = section(UNKNOWN)
        self.assertIn("answered HTTP/1.1 404 Not Found", text)
        self.assertIn('RATE: none returned for USD to XYZ. The body\'s message as shown: "not found".', text)
        self.assertNotIn("as shown in the response).", text)
        self.assertIn("```\n%s\n```" % capture(UNKNOWN)[1], text)

    def test_source_block_sits_directly_above_the_transcript(self):
        text = section(LATEST)
        self.assertIn("### Source. Frankfurter API v1 (api.frankfurter.dev)\n"
                      "- Query URL: https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR\n"
                      "- Retrieved (UTC): %s\nExcerpt (complete raw HTTP response transcript" % RETRIEVED, text)
        self.assertTrue(text.endswith("```\n%s\n```" % capture(LATEST)[1]))

    def test_unreadable_body_keeps_the_transcript(self):
        body = "<html>error</html>"  # test body, not a recording
        transcript = "HTTP/1.1 502 Bad Gateway\n\n" + body
        text = "\n".join(fx.render_section("USD", "EUR", None, None, fx.build_url("USD", "EUR"),
                                           RETRIEVED, transcript, body))
        self.assertIn("RATE: not determinable from this response", text)
        self.assertIn(body, text)

    def test_currencies_capture_lists_both_test_codes(self):
        # The currencies list is not fetched by the tool (one GET per call;
        # the API's own answer decides), but it shows EUR and USD exist and
        # XYZ does not, matching the 200 and 404 captures.
        codes = json.loads(capture(CURRENCIES)[2])
        self.assertIn("EUR", codes)
        self.assertIn("USD", codes)
        self.assertNotIn("XYZ", codes)


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "exchange_rate_check.md"

    def test_page_quotes_the_tool_and_the_recorded_response(self):
        page = self.PAGE.read_text(encoding="utf-8")
        text = section(AMOUNT)
        claims = page.split("## What a report shows", 1)[1].split("Source: ", 1)[0]
        quoted = [q for line in claims.splitlines() if line.startswith("- `") for q in line[2:].split("`")[1::2]]
        self.assertGreaterEqual(len(quoted), 3)
        for q in quoted:
            self.assertIn(q, text)
        entry = PROVENANCE[AMOUNT]
        self.assertIn("Source: %s," % entry["url"], page)
        self.assertIn("```text\n%s\n```" % capture(AMOUNT)[1], page)

    def test_page_states_the_shelf_price_and_the_deprecation(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)
        self.assertIn('"The v1 API is deprecated in favor of v2, but will continue to work."', page)


class CommandLine(unittest.TestCase):
    def run_main(self, argv, fetch):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(fx, "fetch", fetch), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = fx.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_one_fetch_of_the_exact_url(self):
        urls = []

        def fake(url):
            urls.append(url)
            return capture(WEEKEND)
        code, out, _ = self.run_main(["usd", "eur", "--date", "2024-01-06"], fake)
        self.assertEqual(code, 0)
        self.assertEqual(urls, [PROVENANCE[WEEKEND]["url"]])
        self.assertTrue(out.startswith("## Subject: USD to EUR\n"))

    def test_bad_input_fetches_nothing(self):
        def never(url):
            raise AssertionError("no fetch expected")
        for argv in (["US", "EUR"], ["USD", "USD"], ["USD", "EUR", "--amount", "-1"], ["USD", "EUR", "--date", "x"]):
            code, out, _ = self.run_main(argv, never)
            self.assertEqual(code, 2, argv)
            self.assertEqual(out, "")

    def test_failed_fetch_prints_no_report(self):
        def broken(url):
            raise urllib.error.URLError("connection refused (test)")
        code, out, err = self.run_main(["USD", "EUR"], broken)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)


if __name__ == "__main__":
    unittest.main()
