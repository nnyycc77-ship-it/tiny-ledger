#!/usr/bin/env python3
"""Validate the structured CPSC recalls dataset (issue #148).

    python3 tools/validate_cpsc_dataset.py datasets/cpsc-recalls/
    python3 tools/validate_cpsc_dataset.py datasets/cpsc-recalls/ --recheck 10   # live: needs the CPSC API

The offline checks, against the folder's own provenance.json and
schema.json, as `tools/build_cpsc_dataset.py` wrote them:
1. The dataset file exists and its sha256 is the one in provenance.json.
2. Every line parses as one JSON object.
3. The line count equals the provenance total and file_lines.
4. Each RecallID appears once.
5. Each record's RecallDate falls inside the provenance range.
6. No line carries a key path missing from schema.json, and schema.json
   lists no path that no line carries.
7. The month query counts, less the duplicates, add up to the total.

`--recheck N` is the live spot check. It picks N lines spread evenly across
the file and fetches each one again with the fetcher's RecallNumber query.
The live record with the same RecallID must equal the line exactly: the
same keys, the same values, nothing added or missing.

Exit status: 0 when every check passes, 1 when any fails, 2 on a usage
error.
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_cpsc_dataset as builder  # noqa: E402
import cpsc_recalls as cpsc  # noqa: E402


def validate(folder):
    """Return (problems, records) for the offline checks."""
    folder = Path(folder)
    problems = []
    try:
        prov = json.loads((folder / "provenance.json").read_text(encoding="utf-8"))
        schema = json.loads((folder / "schema.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return ["cannot read provenance.json or schema.json: %s" % exc], []
    path = folder / prov.get("file", "")
    if not path.is_file():
        return ["dataset file %s is missing" % path], []
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != prov.get("file_sha256"):
        problems.append("sha256 of %s does not match provenance.json" % path.name)
    records = []
    for n, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        try:
            rec = json.loads(line)
        except ValueError as exc:
            problems.append("line %d does not parse: %s" % (n, exc))
            continue
        if not isinstance(rec, dict):
            problems.append("line %d is not a JSON object" % n)
            continue
        records.append(rec)
    if not (len(records) == prov.get("total_records") == prov.get("file_lines")):
        problems.append("%d records in the file; provenance total %s, file_lines %s"
                        % (len(records), prov.get("total_records"), prov.get("file_lines")))
    ids = [r.get("RecallID") for r in records]
    if len(set(ids)) != len(ids):
        problems.append("RecallID repeated: %s" % sorted({i for i in ids if ids.count(i) > 1})[:5])
    lo, hi = date.fromisoformat(prov["range"]["start"]), date.fromisoformat(prov["range"]["end"])
    for r in records:
        try:
            day = builder.recall_day(r)
        except builder.BuildError as exc:
            problems.append(str(exc))
            continue
        if not lo <= day <= hi:
            problems.append("recall %s dated %s is outside %s to %s" % (r.get("RecallNumber"), day, lo, hi))
    allowed = {f["path"] for f in schema.get("fields", [])}
    seen = set()
    for r in records:
        keys = set(builder.key_paths(r, "", {}))
        seen |= keys
        extra = keys - allowed
        if extra:
            problems.append("recall %s carries field(s) not in schema.json: %s" % (r.get("RecallNumber"), sorted(extra)))
    unused = allowed - seen
    if unused:
        problems.append("schema.json lists field(s) no record carries: %s" % sorted(unused))
    returned = sum(q.get("records", 0) for q in prov.get("month_queries", []))
    if returned != prov.get("records_returned_by_month_queries") or \
            returned - prov.get("duplicates_dropped", 0) != len(records):
        problems.append("month query counts (%d returned, %s duplicates) do not add up to %d records"
                        % (returned, prov.get("duplicates_dropped"), len(records)))
    return problems, records


def recheck(records, n, fetch_url=cpsc.fetch_url):
    """Live spot check: N evenly spread lines against a fresh RecallNumber query each."""
    problems, done = [], []
    if not records:
        return ["no records to recheck"], done
    step = max(1, len(records) // n)
    for rec in records[::step][:n]:
        url = cpsc.query_url(str(rec["RecallNumber"]), "RecallNumber")
        try:
            live = [r for r in cpsc.records(fetch_url(url)) if r.get("RecallID") == rec["RecallID"]]
        except cpsc.FetchError as exc:
            problems.append("%s: %s" % (url, exc))
            continue
        if len(live) != 1:
            problems.append("%s: %d live records with RecallID %s" % (url, len(live), rec["RecallID"]))
        elif live[0] != rec:
            changed = sorted(k for k in set(live[0]) | set(rec) if live[0].get(k) != rec.get(k))
            problems.append("recall %s differs from the live record in: %s" % (rec["RecallNumber"], changed))
        else:
            done.append("recall %s (RecallID %s) equals the live record, %s" % (rec["RecallNumber"], rec["RecallID"], url))
    return problems, done


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--recheck", type=int, metavar="N", help="live: refetch N lines and compare exactly")
    args = parser.parse_args(argv)
    problems, records = validate(args.folder)
    for p in problems:
        sys.stdout.write("FAIL %s\n" % p)
    if not problems:
        sys.stdout.write("PASS offline checks: %d records, sha256, counts, unique RecallID, dates, schema fields\n"
                         % len(records))
    if args.recheck:
        live_problems, done = recheck(records, args.recheck)
        for d in done:
            sys.stdout.write("PASS %s\n" % d)
        for p in live_problems:
            sys.stdout.write("FAIL %s\n" % p)
        problems += live_problems
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
