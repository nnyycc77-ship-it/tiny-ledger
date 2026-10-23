#!/usr/bin/env python3
"""CPSC recall search -> Markdown. Python 3.10+ and curl; no API key needed.

curl captures response headers and body without reserializing either. Its default
config is disabled. Only the fixed public endpoint is queried, without accounts.

Three query shapes, one per run, all against the same endpoint:

    python3 tools/cpsc_recalls.py 'Instant Pot'             # ProductName search
    python3 tools/cpsc_recalls.py --recall-title Peloton     # RecallTitle search
    python3 tools/cpsc_recalls.py --recall-number 21-128     # RecallNumber detail query

Each returned record is rendered as a claim block (recall number, announcement
date, product, hazard, remedy, units, remedy options, CPSC page) with every
value as shown in the response, above the complete raw response capture.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from urllib.parse import parse_qs, urlencode, urlsplit


ENDPOINT = "https://www.saferproducts.gov/RestWebServices/Recall"

# The query fields this tool knows how to send. ProductName is the default
# and the only one the near-match searches use.
FIELDS = ("ProductName", "RecallTitle", "RecallNumber")
FIELD_HEADINGS = {
    "ProductName": "Product query",
    "RecallTitle": "Recall title query",
    "RecallNumber": "Recall number query",
}

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

NOT_PRESENT = "not present in the API record"


class FetchError(ValueError):
    """A failed or uninterpretable response must never become an empty result."""


@dataclass(frozen=True)
class Capture:
    url: str
    retrieved: str
    raw: str


def query_url(value, field="ProductName"):
    if field not in FIELDS:
        raise ValueError(f"Unsupported query field {field!r}; expected one of {', '.join(FIELDS)}")
    if not value.strip():
        raise ValueError("Query text must not be blank")
    return ENDPOINT + "?" + urlencode({"format": "json", field: value})


def query_field(url):
    """The supported field a capture URL queried, read from the URL itself."""
    params = parse_qs(urlsplit(url).query)
    present = [field for field in FIELDS if field in params]
    if len(present) != 1:
        raise FetchError("Capture URL does not name exactly one supported query field; "
                         "no recall conclusion")
    return present[0]


def fetch(value, field="ProductName"):
    url = query_url(value, field)
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


def dashed(number):
    """'15741' as shown -> '15-741', the form the CPSC pages and deliveries use.
    Anything that is not five digits is kept exactly as shown."""
    text = number.strip()
    return f"{text[:2]}-{text[2:]}" if len(text) == 5 and text.isdigit() else text


def long_date(value):
    """'2015-07-15T00:00:00' -> 'July 15, 2015', or None when the value does not
    parse; the caller then prints only the value as shown."""
    try:
        parsed = datetime.strptime(value[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    return f"{MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"


def _shown_strings(items, key):
    """Non-blank string values of `key` across a list of objects, in order.
    Anything else (missing key, blank, wrong type) is left out, never invented."""
    if not isinstance(items, list):
        return []
    return [item[key] for item in items
            if isinstance(item, dict) and isinstance(item.get(key), str) and item[key].strip()]


def _shown_lines(label, values):
    if not values:
        return [f"- {label}: {NOT_PRESENT}"]
    if len(values) == 1:
        return [f"- {label} as shown: {inline(values[0])}"]
    return [f"- {label} as shown ({i} of {len(values)}): {inline(v)}"
            for i, v in enumerate(values, 1)]


def render_record(row):
    """One claim block per recall, every value as shown in the response."""
    number = row["RecallNumber"]
    lines = [f"#### Recall {dashed(number)}", f"- Recall number as shown: {inline(number)}"]

    date = row.get("RecallDate")
    if isinstance(date, str) and date.strip():
        long = long_date(date)
        lines.append(f"- Announcement date as shown: {inline(date)}" + (f" ({long})" if long else ""))
    else:
        lines.append(f"- Announcement date: {NOT_PRESENT}")

    title = row.get("Title")
    lines.append(f"- Title as shown: {inline(title)}" if isinstance(title, str) and title.strip()
                 else f"- Title: {NOT_PRESENT}")

    hazards = _shown_strings(row.get("Hazards"), "Name")
    remedies = _shown_strings(row.get("Remedies"), "Name")
    lines.extend(_shown_lines("Product", _shown_strings(row.get("Products"), "Name")))
    lines.extend(_shown_lines("Hazard", hazards))
    lines.extend(_shown_lines("Remedy", remedies))
    lines.extend(_shown_lines("Units", _shown_strings(row.get("Products"), "NumberOfUnits")))

    options = _shown_strings(row.get("RemedyOptions"), "Option")
    lines.append(f"- Remedy options as shown: {'; '.join(inline(o) for o in options)}" if options
                 else f"- Remedy options: {NOT_PRESENT}")

    page = row.get("URL")
    lines.append(f"- CPSC recall page as shown: {inline(page)}" if isinstance(page, str) and page.strip()
                 else f"- CPSC recall page: {NOT_PRESENT}")

    if hazards and remedies and [normalized(h) for h in hazards] == [normalized(r) for r in remedies]:
        lines.append("- Note: the remedy text in this API record repeats the hazard text word for "
                     "word. Read the remedy from the CPSC recall page above and quote that page "
                     "as its own source.")
    return lines


def render_query(capture, exact_name=None, near=False):
    rows = records(capture)
    heading = "### Checked near-match query" if near else f"### {FIELD_HEADINGS[query_field(capture.url)]}"
    lines = [heading, "",
             f"Exact query: GET {capture.url}",
             f"Retrieved (UTC): {capture.retrieved}", "",
             f"CPSC returned {len(rows)} record(s) for this query."]
    if not rows:
        lines.append("No records returned for this query; this is not a product safety clearance.")
    else:
        lines.append("")
    labels = []
    for row in rows:
        names = [p["Name"] for p in row["Products"]]
        excluded = exact_name is not None and all(
            normalized(name) != normalized(exact_name) for name in names
        )
        label = "Checked and excluded" if excluded else "Returned candidate"
        labels.append(label)
        lines.append(f"- {label}: recall {inline(row['RecallNumber'])}; "
                     f"product name(s) as shown: {', '.join(inline(n) for n in names)}.")
        if excluded:
            lines.append(f"  Reason: none of the returned product names equals "
                         f"{inline(exact_name)} under the requested exact-name rule "
                         "(case and whitespace ignored). This excludes a name match only; "
                         "model applicability still requires review.")
    # One claim block per record, in response order, values as shown in the body below.
    for row, label in zip(rows, labels):
        lines.append("")
        lines.extend(render_record(row))
        lines.append(f"- Listed above as: {label}")
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
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("product", nargs="?", type=nonblank, help="CPSC ProductName search text")
    parser.add_argument("--recall-title", type=nonblank,
                        help="RecallTitle search text, instead of a product name")
    parser.add_argument("--recall-number", type=nonblank,
                        help="RecallNumber detail query, e.g. 21-128, instead of a product name")
    parser.add_argument("--exact-name", type=nonblank,
                        help="exclude records with no equal product name; not a model safety check")
    parser.add_argument("--near-product", action="append", default=[], type=nonblank,
                        help="additional ProductName search to check; requires --exact-name")
    args = parser.parse_args(argv)
    chosen = [(value, field) for value, field in
              ((args.product, "ProductName"), (args.recall_title, "RecallTitle"),
               (args.recall_number, "RecallNumber")) if value is not None]
    if len(chosen) != 1:
        parser.error("give exactly one of: a product name, --recall-title, or --recall-number")
    if args.near_product and args.exact_name is None:
        parser.error("--near-product requires --exact-name to state an exclusion rule")
    queries = chosen + [(product, "ProductName") for product in args.near_product]
    sections = []
    try:
        for index, (value, field) in enumerate(queries):
            sections.append(render_query(fetch(value, field), args.exact_name, near=index > 0))
    except FetchError as exc:
        print(f"CPSC fetch failed: {exc}. No report emitted.", file=sys.stderr)
        return 1
    output = "## CPSC recall search\n\n" + "\n".join(sections)
    # Binary output preserves the captured CRLFs on every supported platform.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
