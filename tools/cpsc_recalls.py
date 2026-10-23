#!/usr/bin/env python3
"""CPSC recall search -> Markdown. Python 3.10+ and curl; no API key needed.

curl captures response headers and body without reserializing either. Its default
config is disabled. Only the fixed public endpoint is queried, without accounts.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from urllib.parse import urlencode


ENDPOINT = "https://www.saferproducts.gov/RestWebServices/Recall"


class FetchError(ValueError):
    """A failed or uninterpretable response must never become an empty result."""


@dataclass(frozen=True)
class Capture:
    url: str
    retrieved: str
    raw: str


def query_url(product):
    if not product.strip():
        raise ValueError("Product name must not be blank")
    return ENDPOINT + "?" + urlencode({"format": "json", "ProductName": product})


def fetch(product):
    url = query_url(product)
    try:
        result = subprocess.run(
            ["curl", "--disable", "--silent", "--show-error", "--http1.1",
             "--suppress-connect-headers", "--include", "--proto", "=https",
             "--connect-timeout", "10", "--max-time", "30",
             "--header", "Accept: application/json",
             "--header", "Accept-Encoding: identity", url],
            capture_output=True, timeout=35, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FetchError("curl unavailable or timed out; no recall conclusion") from exc
    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if result.returncode:
        raise FetchError(f"curl failed (exit {result.returncode}); no recall conclusion")
    try:
        return Capture(url, retrieved, result.stdout.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise FetchError("Response is not UTF-8; no recall conclusion") from exc


def records(capture):
    # Do not pretty print, strip, reorder, or reconstruct the evidence.
    headers, separator, body = capture.raw.partition("\r\n\r\n")
    if not separator or not re.match(r"HTTP/1\.[01] 200(?: |\r\n)", headers):
        raise FetchError("Expected HTTP 200; no recall conclusion")
    if not re.search(r"(?im)^content-type:\s*application/json(?:\s*;|\s*$)", headers):
        raise FetchError("Expected JSON content type; no recall conclusion")
    try:
        rows = json.loads(body)
    except (ValueError, RecursionError) as exc:
        raise FetchError("Invalid JSON; no recall conclusion") from exc
    if not isinstance(rows, list):
        raise FetchError("Expected a JSON array; no recall conclusion")
    for row in rows:
        if (not isinstance(row, dict)
                or not isinstance(row.get("RecallNumber"), str)
                or not row["RecallNumber"].strip()
                or not isinstance(row.get("Products"), list)
                or not row["Products"]
                or any(not isinstance(p, dict)
                       or not isinstance(p.get("Name"), str)
                       or not p["Name"].strip() for p in row["Products"])):
            raise FetchError("Unexpected recall record schema; no recall conclusion")
    return rows


def inline(value):
    # JSON quoting exposes newlines; escaping prevents source text becoming Markdown.
    text = json.dumps(value, ensure_ascii=False)
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", text)


def normalized(value):
    return " ".join(value.split()).casefold()


def render_query(capture, exact_name=None, near=False):
    rows = records(capture)
    lines = ["### Checked near-match query" if near else "### Product query", "",
             f"Exact query: GET {capture.url}",
             f"Retrieved (UTC): {capture.retrieved}", "",
             f"CPSC returned {len(rows)} record(s) for this query."]
    if not rows:
        lines.append("No records returned for this query; this is not a product safety clearance.")
    else:
        lines.append("")
    for row in rows:
        names = [p["Name"] for p in row["Products"]]
        excluded = exact_name is not None and all(
            normalized(name) != normalized(exact_name) for name in names
        )
        label = "Checked and excluded" if excluded else "Returned candidate"
        lines.append(f"- {label}: recall {inline(row['RecallNumber'])}; "
                     f"product name(s) as shown: {', '.join(inline(n) for n in names)}.")
        if excluded:
            lines.append(f"  Reason: none of the returned product names equals "
                         f"{inline(exact_name)} under the requested exact-name rule "
                         "(case and whitespace ignored). This excludes a name match only; "
                         "model applicability still requires review.")
    # A fence longer than any run in the evidence cannot be closed by source text.
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.raw)), default=0))
    lines.extend(["", f"Source: <{capture.url}>", fence])
    return "\n".join(lines) + "\n" + capture.raw + (
        "" if capture.raw.endswith("\n") else "\n"
    ) + fence + "\n"


def nonblank(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be blank")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product", type=nonblank, help="CPSC ProductName search text")
    parser.add_argument("--exact-name", type=nonblank,
                        help="exclude records with no equal product name; not a model safety check")
    parser.add_argument("--near-product", action="append", default=[], type=nonblank,
                        help="additional ProductName search to check; requires --exact-name")
    args = parser.parse_args(argv)
    if args.near_product and args.exact_name is None:
        parser.error("--near-product requires --exact-name to state an exclusion rule")
    sections = []
    try:
        for index, product in enumerate([args.product, *args.near_product]):
            sections.append(render_query(fetch(product), args.exact_name, near=index > 0))
    except FetchError as exc:
        print(f"CPSC fetch failed: {exc}. No report emitted.", file=sys.stderr)
        return 1
    output = "## CPSC recall search\n\n" + "\n".join(sections)
    # Binary output preserves the captured CRLFs on every supported platform.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
