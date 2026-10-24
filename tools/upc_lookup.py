"""Open Food Facts product lookup: python3 tools/upc_lookup.py <code>

Given one product barcode (a UPC or EAN, digits only, in one of the
standard lengths 8, 12, 13 or 14, with its check digit verified locally
before any fetch), fetch the product document from the Open Food Facts
API (api.openfoodfacts.org/api/v2/product/<code>.json, keyless, standard
library only, the fields parameter always sent so the answer stays the
small product summary instead of the full crowdsourced document) and
report the product name, brand and category exactly as listed in the
response, each claim tied to the complete raw response printed beneath
it, in the evidence format the board fixed for this series: the exact
query URL, the UTC retrieval time, and the complete raw response
transcript, verbatim. No assessment or advice wording appears anywhere
in the report; the facts are the database's, as listed.

Two properties of this API shape the reading, both pinned by live
captures (tools/tests/fixtures/openfoodfacts/provenance.json):

- The API normalizes barcodes: a 12 digit UPC is answered under its
  zero padded 13 digit form (a query for 036000291452 returns the code
  0036000291452), so the returned code is compared to the requested
  code with leading zeros ignored. An answer whose significant digits
  differ from the requested code is about a different product: the
  tool refuses it and emits no report, never presenting one product
  as another.
- A barcode the database does not hold is answered with the not found
  document {"code": ..., "status": 0, "status_verbose": "product not
  found"}, normally delivered with HTTP 404 (live captures, issue
  #343). That document, quoted in full, is the proof of the not found
  report. Any other non 200 status, a body that does not parse, an
  off shape document, a timed out or failed fetch, or a redirect off
  the API host yields NO report at all (exit code 2): the lookup is
  unknown, never a claim that the product is or is not listed.

A field the response leaves blank (brands and categories are
crowdsourced and often empty, live capture 2000000000008) is reported
as not listed, never filled in and never read as more than the gap it
is.
"""

import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from propublica_nonprofits import Node, skip_ws  # noqa: E402

API_URL = "https://api.openfoodfacts.org/api/v2/product/{code}.json"
FIELDS = "product_name,brands,categories"
API_HOST = urllib.parse.urlparse(API_URL).hostname
USER_AGENT = "tiny-ledger-upc-lookup"
FETCH_TIMEOUT = 30
_BARCODE_LENGTHS = (8, 12, 13, 14)
_REDIRECT_CODES = frozenset((301, 302, 303, 307, 308))


class FetchError(ValueError):
    """The source could not be read or did not answer in shape."""


class Capture:
    """One fetched response, kept whole for the transcript."""

    def __init__(self, url, retrieved_utc, status_line, headers, body):
        self.url = url
        self.retrieved_utc = retrieved_utc
        self.status_line = status_line
        self.headers = list(headers)
        self.body = body
        parts = status_line.split(" ", 2)
        self.status = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    def transcript(self):
        lines = [self.status_line]
        lines.extend("%s: %s" % (name, value) for name, value in self.headers)
        lines.append("")
        lines.append(self.body)
        return lines


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects off the API host, so a transcript always comes
    from the source the report names. Same host redirects fall through
    to the standard handler. HTTPError answers are data too: fetch()
    decides which of them are the documented not found shape."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in _REDIRECT_CODES:
            host = urllib.parse.urlparse(newurl).hostname
            if host != API_HOST:
                raise FetchError("unexpected redirect to another host: %s" % (newurl,))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def product_url(code):
    """The exact request URL for one barcode."""
    return "%s?fields=%s" % (API_URL.format(code=code), FIELDS)


def check_digit(data_digits):
    """The GTIN check digit for the data digits of a barcode."""
    total = 0
    for index, char in enumerate(reversed(data_digits)):
        total += int(char) * (3 if index % 2 == 0 else 1)
    return (10 - total % 10) % 10


def check_code(raw):
    """Validate one barcode locally, before any fetch."""
    if raw is None:
        raise ValueError("code is required")
    code = str(raw).strip()
    if not code or not code.isdigit():
        raise ValueError("code must be digits only (got %r)" % (code[:60],))
    if len(code) not in _BARCODE_LENGTHS:
        raise ValueError(
            "code must be 8, 12, 13 or 14 digits (got %d)" % len(code))
    expected = check_digit(code[:-1])
    if int(code[-1]) != expected:
        raise ValueError(
            "code %s has check digit %s, expected %d; not a valid UPC or EAN"
            % (code, code[-1], expected))
    return code


def _significant(code):
    return code.lstrip("0") or "0"


def fetch(url):
    """Fetch one URL and keep the whole response as a Capture.

    A 404 is captured like a 200, because on this API a 404 can carry
    the documented not found document; the reader decides. Any other
    non success status, or a transport failure, raises FetchError."""
    request = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    })
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        response = opener.open(request, timeout=FETCH_TIMEOUT)
    except urllib.error.HTTPError as err:
        if err.code != 404:
            raise FetchError("fetch failed: HTTP %s for %s" % (err.code, url))
        body = err.read().decode("utf-8", "replace")
        headers = list(err.headers.items()) if err.headers else []
        status_line = "HTTP/1.1 404 %s" % (err.msg or "Not Found")
        return Capture(url, _utcnow(), status_line, headers, body)
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        raise FetchError("fetch failed for %s: %s" % (url, err))
    with response:
        final_url = response.geturl() or url
        if urllib.parse.urlparse(final_url).hostname != API_HOST:
            raise FetchError("unexpected redirect to another host: %s" % (final_url,))
        body = response.read().decode("utf-8", "replace")
        version = getattr(response, "version", 11)
        status_line = "HTTP/%s %s %s" % (
            "1.1" if version == 11 else "1.0",
            response.status, response.reason)
        headers = list(response.headers.items())
    return Capture(url, _utcnow(), status_line, headers, body)


def _parse_root(body, capture):
    try:
        root = Node(body, skip_ws(body, 0))
    except (ValueError, IndexError) as err:
        raise FetchError("the API response was not a JSON object: %s" % (err,))
    if not root.has("status") or root.value("status") not in (0, 1):
        raise FetchError(
            "unexpected shape: the response carries no status of 0 or 1: %s"
            % (root.whole()[:400],))
    if not root.has("code") or not isinstance(root.value("code"), str):
        raise FetchError(
            "unexpected shape: the response carries no code: %s"
            % (root.whole()[:400],))
    if root.value("status") == 1 and capture.status != 200:
        raise FetchError(
            "unexpected shape: a found document arrived with HTTP %s"
            % (capture.status,))
    return root


def _listed(product, key):
    """One product field as listed, or None when the response leaves it
    absent or blank."""
    if not product.has(key):
        return None
    value = product.value(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def _format(code, capture):
    root = _parse_root(capture.body, capture)
    returned = root.value("code")
    status = root.value("status")
    lines = ["# UPC lookup: %s" % (code,), ""]
    lines.append(
        "Facts as listed by Open Food Facts, a crowdsourced database. A "
        "field the response leaves blank is shown as not listed. This "
        "report makes no assessment of the product.")
    lines.append("")
    if _significant(returned) != _significant(code):
        raise FetchError(
            "the API answered for code %s, not the requested code %s; no report"
            % (returned, code))
    if status == 0:
        lines.append(
            "Answer: Open Food Facts holds no product for barcode %s; the "
            "API answered its not found document (status 0, status_verbose "
            "\"product not found\"), quoted in full below. That covers this "
            "request only; it says nothing about the product itself." % (code,))
    else:
        if not root.has("product"):
            raise FetchError(
                "unexpected shape: a found document carries no product: %s"
                % (root.whole()[:400],))
        product = root.child("product")
        lines.append("Answer (every claim tied to the transcript below):")
        if returned != code:
            lines.append(
                "- The API returned the code zero padded as `%s`; its "
                "significant digits are the requested code %s, as shown."
                % (returned, code))
        lines.append("- Code as shown: `%s`" % (returned,))
        for label, key in (("Product name", "product_name"),
                           ("Brand", "brands"),
                           ("Category", "categories")):
            value = _listed(product, key)
            if value is None:
                lines.append("- %s (%s): not listed in the response" % (label, key))
            else:
                lines.append("- %s (%s) as listed: `%s`" % (label, key, value))
    lines.append("")
    lines.append("### Open Food Facts API, product lookup (api/v2)")
    lines.append("")
    lines.append("Query: %s" % (capture.url,))
    lines.append("Retrieved (UTC): %s" % (capture.retrieved_utc,))
    lines.append("")
    lines.append("Verbatim field excerpts from the raw response:")
    lines.append("")
    lines.append("```")
    for key in ("code", "status", "status_verbose"):
        if root.has(key):
            lines.append("- %s: %s" % (key, root.excerpt(key)))
    if status == 1:
        product = root.child("product")
        for key in ("product_name", "brands", "categories"):
            if product.has(key):
                lines.append("- product.%s: %s" % (key, product.excerpt(key)))
    lines.append("```")
    lines.append("")
    lines.append("Complete raw response:")
    lines.append("")
    lines.append("```")
    lines.extend(capture.transcript())
    lines.append("```")
    return lines


def report(code, fetcher=None):
    """The Markdown evidence report for one barcode."""
    checked = check_code(code)
    capture = (fetcher or fetch)(product_url(checked))
    return _format(checked, capture)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: python3 tools/upc_lookup.py <UPC or EAN barcode>",
              file=sys.stderr)
        return 2
    try:
        lines = report(argv[0])
    except ValueError as err:
        # FetchError subclasses ValueError and check_code raises it;
        # either way no report is emitted, so a failed lookup can never
        # be mistaken for a not found claim.
        print("upc_lookup: %s" % (err,), file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
