#!/usr/bin/env python3
"""Exchange rate check (issue #168, tool factory wave 1).

Looks up one currency pair with the public Frankfurter API
(api.frankfurter.dev, v1) live and prints one Markdown section in the
delivery format from AGENT-BRIEF.md: the claim lines, the source link,
and the complete raw HTTP response transcript printed verbatim directly
beneath the link.

No key is needed for this source and none is read. The only network
call is the one GET to api.frankfurter.dev, made with the capture path
of tools/nhtsa_recalls.py. Standard library only.

Usage examples:

    python3 tools/exchange_rate_check.py USD EUR
    python3 tools/exchange_rate_check.py USD EUR --amount 100
    python3 tools/exchange_rate_check.py USD EUR --date 2024-01-06

The URL is built as the v1 documentation (https://frankfurter.dev/v1/)
shows it: `latest` or a date, then base and symbols. When an amount is
given it is sent as `amount`, the form the recorded response for #168
capture B was fetched with:

    https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR[&amount=100]
    https://api.frankfurter.dev/v1/2024-01-06?base=USD&symbols=EUR

The v1 documentation says v1 "is deprecated in favor of v2, but will
continue to work"; this tool uses v1, the version whose responses are
recorded in tools/tests/fixtures/frankfurter/ with their provenance.

What the output contains, in order:

1. A subject heading and the database named.
2. QUERY: the pair, the amount and date asked, the HTTP status, and the
   retrieval time in UTC.
3. RATE: the response's own amount, base, date and rate for the target
   currency, each as shown in the body. With an amount, the converted
   figure is the API's own; this tool does no arithmetic. When the
   rate's own date differs from the date asked, both are stated.
   A response with no rate for the target says so, quoting the body's
   message as shown.
4. The source link (the exact query URL) and the retrieval time.
5. Directly beneath the link, the complete raw HTTP response
   transcript: status line, headers in the order returned, a blank
   line, then the body exactly as returned. A missing rate is proven by
   that transcript, never asserted.

Numbers are printed exactly as the body writes them (parsed as text,
never as floats), so 89.34 stays 89.34 and 100.0 stays 100.0.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import nhtsa_recalls as nr  # noqa: E402

BASE_URL = "https://api.frankfurter.dev/v1/"
SOURCE_HEADING = "Frankfurter API v1 (api.frankfurter.dev)"
CODE_PATTERN = re.compile(r"^[A-Z]{3}$")
AMOUNT_PATTERN = re.compile(r"^\d+(\.\d+)?$")


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_code(raw, label):
    """A three letter currency code, upper cased. Whether the API knows
    it is the API's answer."""
    code = str(raw or "").strip().upper()
    if not CODE_PATTERN.match(code):
        raise ValueError("%s is a three letter currency code such as USD, got %r" % (label, raw))
    return code


def check_amount(raw):
    if raw is None or str(raw).strip() == "":
        return None
    amount = str(raw).strip()
    if not AMOUNT_PATTERN.match(amount) or float(amount) <= 0:
        raise ValueError("amount is a positive number such as 100 or 12.5, got %r" % raw)
    return amount


def check_date(raw):
    if raw is None or str(raw).strip() == "":
        return None
    text = str(raw).strip()
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValueError("date is YYYY-MM-DD, got %r" % raw)
    if len(text) != 10:
        raise ValueError("date is YYYY-MM-DD, got %r" % raw)
    return text


def build_url(base, target, amount=None, on=None):
    """The query URL, in the parameter order of the v1 documentation."""
    params = [("base", base), ("symbols", target)]
    if amount:
        params.append(("amount", amount))
    return BASE_URL + (on or "latest") + "?" + urllib.parse.urlencode(params)


def describe_query(base, target, amount=None, on=None):
    text = "base = %s, symbols = %s" % (base, target)
    if amount:
        text += ", amount = %s" % amount
    text += ", date = %s" % (on or "latest")
    return text


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def fetch(url):
    """GET the URL; (retrieved_utc, transcript, body_text), as nhtsa_recalls.fetch."""
    return nr.fetch(url)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def status_of(transcript):
    return transcript.split("\n", 1)[0]


def parse_response(body):
    """The body as a JSON object with every number kept as its source text."""
    data = json.loads(body, parse_float=str, parse_int=str)
    if not isinstance(data, dict):
        raise ValueError("response body is not a JSON object")
    return data


def render_rate(data, base, target, amount, on):
    """The RATE lines for a parsed body."""
    rates = data.get("rates")
    if not isinstance(rates, dict) or target not in rates:
        message = data.get("message")
        line = "RATE: none returned for %s to %s." % (base, target)
        if message is not None:
            line += " The body's message as shown: %s." % json.dumps(message, ensure_ascii=False)
        return [line + " The complete raw HTTP response transcript is shown verbatim beneath the "
                "source link below."]
    shown = {k: data.get(k) for k in ("amount", "base", "date")}
    lines = ["RATE: %s %s = %s %s, rate date %s (each as shown in the response)." % (
        shown["amount"], shown["base"], rates[target], target, shown["date"])]
    lines.append("- amount as shown: %s" % shown["amount"])
    lines.append("- base as shown: %s" % shown["base"])
    lines.append("- date as shown: %s" % shown["date"])
    lines.append("- rates.%s as shown: %s" % (target, rates[target]))
    if amount:
        lines.append("- The figure for %s is the API's own conversion of the amount sent; this "
                     "tool does no arithmetic." % target)
    if on and shown["date"] != on:
        lines.append("- The date asked was %s; the response's own date is %s, so the rate is for "
                     "%s." % (on, shown["date"], shown["date"]))
    if shown["base"] != base:
        lines.append("- The base asked was %s; the response shows base %s." % (base, shown["base"]))
    others = sorted(k for k in rates if k != target)
    if others:
        lines.append("- The response also holds rates for: %s" % ", ".join(others))
    return lines


def render_section(base, target, amount, on, url, retrieved, transcript, body):
    """Build the whole Markdown section as a list of lines."""
    query_text = describe_query(base, target, amount, on)
    lines = ["## Subject: %s to %s" % (base, target), "",
             "Database: Frankfurter API v1 (api.frankfurter.dev), %s rates, queried by base and "
             "target currency%s." % ("historical" if on else "latest",
                                     " with an amount" if amount else ""), ""]
    lines.append("QUERY: %s answered %s (retrieved %s)." % (query_text, status_of(transcript), retrieved))
    lines.append("")
    try:
        data = parse_response(body)
    except ValueError as err:
        lines.append("RATE: not determinable from this response; %s. The complete raw HTTP "
                     "response transcript is shown verbatim beneath the source link below." % err)
    else:
        lines.extend(render_rate(data, base, target, amount, on))
    lines.append("")
    lines.append("### Source. %s" % SOURCE_HEADING)
    lines.append("- Query URL: %s" % url)
    lines.append("- Retrieved (UTC): %s" % retrieved)
    lines.append("Excerpt (complete raw HTTP response transcript for the query above: status "
                 "line, headers in the order returned, a blank line, then the complete body "
                 "exactly as returned):")
    lines.append("```")
    lines.extend(transcript.split("\n"))
    lines.append("```")
    return lines


def check_query(base, target, amount=None, on=None):
    """Validated (base, target, amount, date). Raises ValueError."""
    base, target = check_code(base, "base"), check_code(target, "target")
    if base == target:
        raise ValueError("base and target are the same currency (%s)" % base)
    return base, target, check_amount(amount), check_date(on)


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Look up an exchange rate with the Frankfurter API and print one Markdown "
        "section in the delivery format.")
    parser.add_argument("base", help="the currency to convert from, e.g. USD")
    parser.add_argument("target", help="the currency to convert to, e.g. EUR")
    parser.add_argument("--amount", help="an amount of the base currency; the API converts it")
    parser.add_argument("--date", help="YYYY-MM-DD for a historical rate; default latest")
    args = parser.parse_args(argv)
    try:
        base, target, amount, on = check_query(args.base, args.target, args.amount, args.date)
    except ValueError as err:
        parser.error(str(err))
    url = build_url(base, target, amount, on)
    try:
        retrieved, transcript, body = fetch(url)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\nquery URL: %s\n" % (err, url))
        return 2
    lines = render_section(base, target, amount, on, url, retrieved, transcript, body)
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
