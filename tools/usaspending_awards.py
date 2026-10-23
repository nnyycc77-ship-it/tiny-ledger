#!/usr/bin/env python3
"""Fetch one page of public USAspending prime contract awards as Markdown.

No API key, environment configuration, account, or third-party package needed.
API contract: https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award.md
"""

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENDPOINT = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
FIELDS = [
    "Award ID", "Recipient Name", "Award Amount", "Awarding Agency",
    "Description", "Start Date", "End Date", "NAICS", "generated_internal_id",
]


@dataclass(frozen=True)
class Capture:
    query: str
    retrieved: str
    raw: str


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--recipient", help="Public recipient name, UEI, or DUNS search text")
    result.add_argument("--naics", action="append", default=[], help="NAICS prefix (repeatable)")
    result.add_argument("--start", help="Start date, YYYY-MM-DD (requires --end)")
    result.add_argument("--end", help="End date, YYYY-MM-DD (requires --start)")
    result.add_argument("--page", type=int, default=1, help="One page to fetch; default: 1")
    result.add_argument("--limit", type=int, default=10, help="Records per page; default: 10, maximum: 100")
    result.add_argument(
        "--exclude", action="append", default=[], metavar="GENERATED_ID=REASON",
        help="List a fetched near match as checked and excluded, with your reason",
    )
    return result


def build_query(args):
    recipient = args.recipient.strip() if args.recipient else ""
    if not recipient and not args.naics:
        raise ValueError("provide --recipient or --naics")
    if args.page < 1 or not 1 <= args.limit <= 100:
        raise ValueError("--page must be positive and --limit must be between 1 and 100")
    if any(not re.fullmatch(r"[0-9]{2,6}", code) for code in args.naics):
        raise ValueError("each --naics must be a numeric prefix of 2 to 6 digits")
    filters = {"award_type_codes": ["A", "B", "C", "D"]}
    if recipient:
        filters["recipient_search_text"] = [recipient]
    if args.naics:
        filters["naics_codes"] = {"require": args.naics}
    if bool(args.start) != bool(args.end):
        raise ValueError("--start and --end must be supplied together")
    if args.start:
        if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in (args.start, args.end)):
            raise ValueError("dates must use YYYY-MM-DD")
        if date.fromisoformat(args.start) > date.fromisoformat(args.end):
            raise ValueError("--start must not be after --end")
        filters["time_period"] = [{"start_date": args.start, "end_date": args.end}]
    return json.dumps({
        "filters": filters, "fields": FIELDS, "page": args.page,
        "limit": args.limit, "sort": "Award Amount", "order": "desc",
        "subawards": False,
    }, ensure_ascii=False, separators=(",", ":"))


def exclusions(values):
    result = {}
    for value in values:
        identifier, separator, reason = value.partition("=")
        if not separator or not identifier.strip() or not reason.strip():
            raise ValueError("each --exclude requires GENERATED_ID=REASON")
        if identifier in result:
            raise ValueError("duplicate --exclude identifier")
        result[identifier] = reason.strip()
    return result


def fetch(query):
    request = Request(ENDPOINT, data=query.encode("utf-8"), headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "tiny-ledger-usaspending-fetcher",
    }, method="POST")
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"unexpected HTTP status {response.status}")
        if response.headers.get_content_type() != "application/json":
            raise ValueError("source did not return application/json")
        # Keep the entire UTF-8 API response body, without JSON reserialization.
        # Do not capture HTTP headers: public responses can contain session cookies.
        raw = response.read().decode("utf-8")
    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return Capture(query, retrieved, raw)


def fenced(raw):
    fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", raw)), default=0))
    return fence + "\n" + raw + ("" if raw.endswith("\n") else "\n") + fence


def display(value):
    if value is None:
        return "not supplied by source"
    if isinstance(value, Decimal):
        text = str(value)
    elif isinstance(value, str):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    # Escape Markdown in summary values only. Evidence is never escaped or reformatted.
    return re.sub(r"([\\`*_{}\[\]()#+.!|<>~-])", r"\\\1", text)


def render(capture, excluded):
    data = json.loads(capture.raw, parse_float=Decimal)
    query = json.loads(capture.query)
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError("source response has no results array")
    records = data["results"]
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("source results contain a non-object record")
    metadata = data.get("page_metadata")
    if (not isinstance(metadata, dict) or type(metadata.get("hasNext")) is not bool
            or type(metadata.get("page")) is not int or metadata["page"] != query["page"]):
        raise ValueError("missing or inconsistent pagination metadata")
    identifiers = [record.get("generated_internal_id") for record in records]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise ValueError("a source record has no generated_internal_id")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("source returned duplicate generated_internal_id values")
    if set(excluded) - set(identifiers):
        raise ValueError("an --exclude identifier was not returned on this page")
    lines = [
        "## USAspending prime contract awards", "",
        "Scope: one requested page; no assertion of an exhaustive recipient or award search.",
        "Award Amount is the API field as returned, not a payment or revenue estimate.", "",
        f"Exact query: POST {ENDPOINT}",
        "Content-Type: application/json", "Exact request body:", fenced(capture.query),
        f"Retrieved (UTC): {capture.retrieved}", "",
        f"USAspending returned {len(records)} record(s) on requested page {metadata['page']}.",
        f"API page_metadata.hasNext: {str(metadata['hasNext']).lower()}.",
    ]
    if metadata["hasNext"]:
        lines.append("More pages are reported by the API; this section does not include them.")
    if not records:
        lines.append("No records on this page; this does not establish that the recipient has no awards.")
    for record in records:
        identifier = record["generated_internal_id"]
        lines.extend(["", "### " + ("Checked and excluded near match" if identifier in excluded else "Returned award"), ""])
        for field in FIELDS:
            lines.append(f"- {field} as shown: {display(record.get(field))}")
        if identifier in excluded:
            lines.append(f"- Reviewer-supplied exclusion reason: {display(excluded[identifier])}")
    if data.get("messages"):
        lines.extend(["", "API messages as returned: " + display(data["messages"])])
    lines.extend(["", f"Source: <{ENDPOINT}>", fenced(capture.raw)])
    return "\n".join(lines) + "\n"


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        query = build_query(args)
        excluded = exclusions(args.exclude)
        report = render(fetch(query), excluded)
    except (ValueError, UnicodeError, URLError, TimeoutError, OSError) as error:
        # A failed fetch or validation is never presented as an empty search.
        detail = f"HTTP {error.code}" if isinstance(error, HTTPError) else str(error)
        print(f"USAspending fetch failed; no report emitted: {detail}", file=sys.stderr)
        return 2
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
