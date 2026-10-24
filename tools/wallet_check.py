#!/usr/bin/env python3
"""Bitcoin address facts check (issue #337, tool factory wave 3).

Given a Bitcoin address, reads the public facts the mempool.space
explorer API holds for it and prints one Markdown report in the
delivery format from AGENT-BRIEF.md: the answer first (transaction
count, total received, total sent, and current balance, in satoshis),
then the evidence: the query's exact URL, UTC retrieval time, the
fields cut verbatim from the response, and the complete raw response.

    python3 tools/wallet_check.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

Source, keyless: the mempool.space public API,
GET https://mempool.space/api/address/{address}, a third party open
source explorer API. Its figures are that explorer's view of the chain
and the mempool. The response shape used here is from the live
captures made for this issue on 2026-10-24 (committed under
tools/tests/fixtures/wallet/ with their provenance): an object with
"address", "chain_stats" and "mempool_stats"; each stats block carries
"funded_txo_count", "funded_txo_sum", "spent_txo_count",
"spent_txo_sum" and "tx_count", all amounts in satoshis.

How the figures are read, stated rather than assumed:

- The answer's figures come from chain_stats only (confirmed). Total
  received is funded_txo_sum; total sent is spent_txo_sum; the current
  balance is funded_txo_sum minus spent_txo_sum, computed here from
  those two shown figures (the API returns no balance field).
- mempool_stats (unconfirmed) is printed as its own block, as shown.
  Confirmed and unconfirmed figures are never added together.

Facts only: the report states the figures and where they came from.
It contains no assessment and no advice.

Outcomes: an address document is a report; for an address with no
activity the document's figures are all zero, and the complete raw
response in the evidence is the proof of that empty result. The
source refuses an address it judges invalid at HTTP 400 with a plain
text body; that, any other non 200 status, a failed or timed out
request, a redirect off the source host, or a body without the
documented shape stops the run with exit 2 and no report: a failed
fetch is reported as unknown, never as figures.

Standard library only.
"""

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from propublica_nonprofits import Node, fenced, inline, skip_ws  # noqa: E402

API_URL = "https://mempool.space/api/address/"
USER_AGENT = "tiny-ledger-wallet-check"
TIMEOUT_SECONDS = 30
HIDDEN_HEADERS = ("set-cookie",)
BASE58 = frozenset("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
BECH32 = frozenset("qpzry9x8gf2tvdw0s3jn54khce6mua7l")
STAT_FIELDS = ("funded_txo_count", "funded_txo_sum", "spent_txo_count", "spent_txo_sum", "tx_count")

FACTS = ("This report records what the mempool.space API returned for this address at the retrieval time "
         "below. Amounts are in satoshis. Confirmed figures (chain_stats) and unconfirmed figures "
         "(mempool_stats) are reported in separate blocks and are never added together.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, retrieved, status_line, headers, body):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        shown = [kv for kv in self.headers if kv[0].lower() not in HIDDEN_HEADERS]
        lines = [self.status_line] + ["%s: %s" % kv for kv in shown]
        if len(shown) != len(self.headers):
            lines.append("(a Set-Cookie header was returned and is not printed)")
        return "\n".join(lines + ["", self.body])


# ----------------------------------------------------------------------
# Inputs and URLs
# ----------------------------------------------------------------------

def check_address(address):
    """The address text, or ValueError. A shape check only: legacy
    base58 (starts 1 or 3), or SegWit/Taproot bech32 (starts bc1). The
    source stays the authority on validity and refuses bad checksums."""
    text = (address or "").strip()
    if text.startswith("bc1"):
        rest = text[3:]
        if 11 <= len(rest) <= 59 and all(ch in BECH32 for ch in rest):
            return text
        raise ValueError("a bc1 address is bc1 followed by 11 to 59 bech32 characters (got %r)" % text)
    if text[:1] in ("1", "3") and 26 <= len(text) <= 35 and all(ch in BASE58 for ch in text):
        return text
    raise ValueError("give a Bitcoin address: legacy base58 starting 1 or 3 (26 to 35 characters) "
                     "or bech32 starting bc1 (got %r)" % text)


def address_url(address):
    return API_URL + urllib.parse.quote(address, safe="")


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        raise FetchError("%s answered HTTP %s; no report" % (url, err.code))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    with response:
        status = response.status
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, getattr(response, "reason", ""))
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("%s answered %s; no report" % (url, status_line))
    if urllib.parse.urlsplit(final_url).netloc != urllib.parse.urlsplit(url).netloc:
        raise FetchError("%s was redirected off its host; no report" % url)
    return Capture(url, retrieved, status_line, headers, body)


def root(capture):
    try:
        return Node(capture.body, skip_ws(capture.body, 0))
    except (ValueError, IndexError) as err:
        raise FetchError("%s answered a body that is not a JSON object (%s); no report" % (capture.url, err))


# ----------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------

def stats_block(node, field, capture):
    """One stats block Node, with every documented figure an integer."""
    try:
        block = node.child(field)
        for f in STAT_FIELDS:
            value = block.value(f)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError("%s.%s is not an integer" % (field, f))
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented address shape (%s); no report"
                         % (capture.url, err))
    return block


def document(capture):
    """(address Node, chain_stats Node, mempool_stats Node)."""
    node = root(capture)
    try:
        if not node.has("address"):
            raise ValueError("no address field (members: %s)" % (", ".join(sorted(node.spans)) or "none"))
    except (ValueError, IndexError, KeyError) as err:
        raise FetchError("%s answered a body that is not the documented address shape (%s); no report"
                         % (capture.url, err))
    return node, stats_block(node, "chain_stats", capture), stats_block(node, "mempool_stats", capture)


def stats_lines(block, heading, derived_label):
    funded = block.value("funded_txo_sum")
    spent = block.value("spent_txo_sum")
    return ["%s:" % heading,
            "- Transaction count (tx_count) as shown: %s" % block.literal("tx_count"),
            "- Total received (funded_txo_sum) as shown: %s satoshis" % block.literal("funded_txo_sum"),
            "- Total sent (spent_txo_sum) as shown: %s satoshis" % block.literal("spent_txo_sum"),
            "- Funded output count (funded_txo_count) as shown: %s" % block.literal("funded_txo_count"),
            "- Spent output count (spent_txo_count) as shown: %s" % block.literal("spent_txo_count"),
            "- %s (funded_txo_sum minus spent_txo_sum): %d satoshis" % (derived_label, funded - spent)]


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def report(address, fetcher=None):
    """The report lines. Raises FetchError on any failed or unreadable answer."""
    fetcher = fetcher or fetch
    capture = fetcher(address_url(address))
    node, chain, mempool = document(capture)
    lines = ["# Bitcoin address check: %s" % address, "", FACTS, "",
             "## Answer", "",
             "Address (address) as shown: %s" % inline(node.literal("address")), ""]
    lines += stats_lines(chain, "Confirmed figures (chain_stats)", "Current balance") + [""]
    lines += stats_lines(mempool, "Unconfirmed figures (mempool_stats)", "Net unconfirmed") + [""]
    if all(chain.value(f) == 0 for f in STAT_FIELDS) and all(mempool.value(f) == 0 for f in STAT_FIELDS):
        lines += ["Every figure in both stats blocks is zero, as shown. The complete raw response below "
                  "is the proof.", ""]
    excerpts = [node.excerpt("address")]
    for block in (chain, mempool):
        excerpts += [block.excerpt(f) for f in STAT_FIELDS]
    lines += ["## Evidence", "",
              "### mempool.space, address document", "",
              "Exact query URL: <%s>" % capture.url, "",
              "UTC retrieval time: %s" % capture.retrieved, "",
              "Fields, verbatim from the response:", fenced("\n".join(excerpts)), "",
              "Complete raw response:", fenced(capture.transcript()), ""]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Bitcoin address facts from the mempool.space API.")
    p.add_argument("address", nargs="?", help="a Bitcoin address")
    args = p.parse_args(argv)
    try:
        if args.address is None:
            raise ValueError("give a Bitcoin address")
        lines = report(check_address(args.address), fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
