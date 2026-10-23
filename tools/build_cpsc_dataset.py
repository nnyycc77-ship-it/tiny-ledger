#!/usr/bin/env python3
"""Build the structured CPSC recalls dataset (issue #148). Python 3.10+ and curl.

    python3 tools/build_cpsc_dataset.py --start 2023-01-01 --end 2025-12-31 \\
        --out datasets/cpsc-recalls/

What it does:
- Queries the CPSC recall API (the endpoint and curl capture path of
  `tools/cpsc_recalls.py`) one calendar month at a time, with
  RecallDateStart and RecallDateEnd.
- Checks every response with the fetcher's own `records()` schema check.
- Checks that every record's RecallDate falls inside the month asked for.
  If one does not, the API did not filter by date, and the run stops.
- Cross-checks each year with one whole-year query. Its unique RecallIDs
  must equal the union of that year's months, or the run stops.

What it writes into --out:
- `recalls-<start year>-<end year>.jsonl`: one recall per line. Each line
  is the source record object as returned, re-serialized compactly with
  keys in source order, values unchanged and nothing added. A record that
  comes back twice with identical content is kept once, and the repeat is counted.
- `provenance.json` and `PROVENANCE.md`: for every query, the exact URL,
  the retrieval time, the record count and the sha256 of the raw response;
  then the totals, the cross-check and the dataset file's sha256.
- `schema.json` and `SCHEMA.md`: every key path the records hold, with
  the JSON types seen and how many records carry it. This is read from the
  data, not assumed.

It fails closed. A failed fetch, a non 200 response, an unexpected record
shape, a date outside the month asked for, a count that does not
reconcile, or a RecallID repeated with different content stops the run.
Nothing is written then, because the outputs go to a temporary folder
first.
"""

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from collections import OrderedDict
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpsc_recalls as cpsc  # noqa: E402


class BuildError(RuntimeError):
    """The dataset cannot be built cleanly from what the API returned."""


def months(start, end):
    """(first day, last day) per calendar month from start to end, inclusive."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        first = date(y, m, 1)
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        last = date.fromordinal(nxt.toordinal() - 1)
        yield max(first, start), min(last, end)
        y, m = nxt.year, nxt.month


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def recall_day(row):
    value = row.get("RecallDate")
    if not isinstance(value, str) or len(value) < 10:
        raise BuildError("record %s has no usable RecallDate (%r)" % (row.get("RecallNumber"), value))
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        raise BuildError("record %s RecallDate %r is not a date" % (row.get("RecallNumber"), value))


def query(fetch_url, lo, hi):
    url = cpsc.date_range_url(lo.isoformat(), hi.isoformat())
    try:
        capture = fetch_url(url)
        rows = cpsc.records(capture)
    except cpsc.FetchError as exc:
        raise BuildError("%s: %s" % (url, exc))
    for row in rows:
        day = recall_day(row)
        if not lo <= day <= hi:
            raise BuildError("%s returned recall %s dated %s, outside %s to %s; the API did not filter by date, "
                             "so this query cannot build the dataset" % (url, row["RecallNumber"], day, lo, hi))
    body = capture.raw.partition("\r\n\r\n")[2]
    return {"url": url, "retrieved": capture.retrieved, "records": len(rows),
            "raw_sha256": sha256(capture.raw), "body_sha256": sha256(body)}, rows


def key_paths(value, prefix, out):
    """Every key path in a record, with the JSON types seen at it."""
    kind = {dict: "object", list: "array", str: "string", bool: "boolean", type(None): "null"}.get(
        type(value), "number" if isinstance(value, (int, float)) else type(value).__name__)
    if prefix:
        out.setdefault(prefix, set()).add(kind)
    if isinstance(value, dict):
        for k, v in value.items():
            key_paths(v, prefix + "." + k if prefix else k, out)
    elif isinstance(value, list):
        for v in value:
            key_paths(v, prefix + "[]", out)
    return out


def build(start, end, out_dir, fetch_url=cpsc.fetch_url, now=None):
    if end < start:
        raise BuildError("--end is before --start")
    queries, by_id, duplicates = [], OrderedDict(), 0
    for lo, hi in months(start, end):
        meta, rows = query(fetch_url, lo, hi)
        queries.append(meta)
        for row in rows:
            rid = row.get("RecallID")
            if rid is None:
                raise BuildError("record %s has no RecallID" % row["RecallNumber"])
            if rid in by_id:
                if by_id[rid] != row:
                    raise BuildError("RecallID %s came back twice with different content" % rid)
                duplicates += 1
                continue
            by_id[rid] = row
    years = []
    for year in range(start.year, end.year + 1):
        lo, hi = max(date(year, 1, 1), start), min(date(year, 12, 31), end)
        meta, rows = query(fetch_url, lo, hi)
        ids = {r.get("RecallID") for r in rows}
        month_ids = {rid for rid, r in by_id.items() if lo <= recall_day(r) <= hi}
        if ids != month_ids:
            raise BuildError("%d: the whole-year query holds %d unique recalls, the months %d (only in the year: %s; "
                             "only in the months: %s)" % (year, len(ids), len(month_ids),
                                                          sorted(ids - month_ids)[:5], sorted(month_ids - ids)[:5]))
        meta["unique_recall_ids"] = len(ids)
        years.append(meta)
    rows = sorted(by_id.values(), key=lambda r: (r["RecallDate"], str(r["RecallNumber"]), r["RecallID"]))
    name = "recalls-%d-%d.jsonl" % (start.year, end.year)
    lines = [json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows]
    data = "\n".join(lines) + ("\n" if lines else "")
    paths, per_record = {}, []
    for r in rows:
        mine = key_paths(r, "", {})
        per_record.append(set(mine))
        for path, kinds in mine.items():
            paths.setdefault(path, set()).update(kinds)
    schema = {"record_count": len(rows), "fields": [
        {"path": p, "types": sorted(t), "records_with_field": sum(1 for keys in per_record if p in keys)}
        for p, t in sorted(paths.items())]}
    provenance = {
        "source": "CPSC recall API (SaferProducts.gov RestWebServices), %s" % cpsc.ENDPOINT,
        "tool": "tools/build_cpsc_dataset.py, capture path of tools/cpsc_recalls.py",
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "built_utc": now or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "month_queries": queries,
        "year_cross_checks": years,
        "records_returned_by_month_queries": sum(q["records"] for q in queries),
        "duplicates_dropped": duplicates,
        "total_records": len(rows),
        "file": name,
        "file_sha256": sha256(data),
        "file_lines": len(lines),
    }
    tmp = Path(tempfile.mkdtemp(prefix="cpsc-dataset-"))
    try:
        (tmp / name).write_text(data, encoding="utf-8")
        (tmp / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        (tmp / "schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        (tmp / "PROVENANCE.md").write_text(render_provenance(provenance), encoding="utf-8")
        (tmp / "SCHEMA.md").write_text(render_schema(schema, provenance), encoding="utf-8")
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in tmp.iterdir():
            shutil.copyfile(f, out_dir / f.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return provenance


def render_provenance(p):
    lines = ["# Provenance: CPSC recalls %s to %s" % (p["range"]["start"], p["range"]["end"]), "",
             "Written by `tools/build_cpsc_dataset.py` at %s (UTC). Source: %s." % (p["built_utc"], p["source"]), "",
             "## Totals", "",
             "- Records returned by the month queries: %d" % p["records_returned_by_month_queries"],
             "- Repeated records dropped (same RecallID and identical content, kept once): %d" % p["duplicates_dropped"],
             "- Records in the dataset: **%d**, one per line of `%s`" % (p["total_records"], p["file"]),
             "- `%s` sha256: `%s`" % (p["file"], p["file_sha256"]), "",
             "## How the count was verified", "",
             "1. Every month query returned HTTP 200 with a JSON array that passed the fetcher's record schema "
             "check, and every record's RecallDate falls inside the month asked for.",
             "2. Records are kept once per RecallID. A RecallID repeated with different content would have stopped the build.",
             "3. For each year, one whole-year query was run. Its set of unique RecallIDs equals the union of that "
             "year's month queries:", ""]
    lines += ["   - %s to %s: %d unique recalls, `%s`, retrieved %s" % (
        y["url"].split("RecallDateStart=")[1][:10], y["url"].split("RecallDateEnd=")[1][:10], y["unique_recall_ids"],
        y["url"], y["retrieved"]) for y in p["year_cross_checks"]]
    lines += ["", "## Month queries", "", "| Month query URL | Retrieved (UTC) | Records | Raw response sha256 |",
              "| --- | --- | --- | --- |"]
    lines += ["| %s | %s | %d | `%s` |" % (q["url"], q["retrieved"], q["records"], q["raw_sha256"]) for q in p["month_queries"]]
    return "\n".join(lines) + "\n"


def render_schema(s, p):
    lines = ["# Schema: CPSC recalls %s to %s" % (p["range"]["start"], p["range"]["end"]), "",
             "Every field in `%s`, read from the %d records themselves. Each field is a key of the CPSC recall API "
             "record, returned by %s. Nothing is added, renamed or derived. `[]` marks an array element, and a dot "
             "a nested key." % (p["file"], s["record_count"], p["source"].split(", ", 1)[-1]), "",
             "| Field (source key path) | JSON types seen | Records carrying it |", "| --- | --- | --- |"]
    lines += ["| `%s` | %s | %d of %d |" % (f["path"], ", ".join(f["types"]), f["records_with_field"], s["record_count"])
              for f in s["fields"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        p = build(args.start, args.end, args.out)
    except BuildError as exc:
        sys.stderr.write("error: %s; nothing written\n" % exc)
        return 2
    sys.stdout.write("wrote %d records to %s (%s)\n" % (p["total_records"], args.out / p["file"], p["file_sha256"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
