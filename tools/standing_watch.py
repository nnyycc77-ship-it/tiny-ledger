#!/usr/bin/env python3
"""Standing watch: recheck a buyer list and report only what changed.

A buyer supplies a watchlist (JSON, format below). Each run pulls the
same public sources the delivery fetchers use, stores a dated snapshot
of the fields that matter, diffs the new snapshot against the previous
one, and emits a Markdown report: a baseline edition on the first run,
after that a change report (alerts for changed entries, one line for
each entry with no change).

Two watch types, both reusing the existing fetchers in this folder:

* Carriers, by USDOT number, through `fmcsa_carrier.py` (FMCSA Company
  Census File, SAFER Company Snapshot, Licensing and Insurance). The
  fields that matter are the ones the fetcher returns: the Census
  record fields as shown (status_code and docket1_status_code carry
  the authority state, safety_rating the rating), every labelled SAFER
  value (Operating Authority Status, USDOT Status, Rating, and the
  rest), and the Licensing and Insurance record lines found.
* Products, through `cpsc_recalls.py` (CPSC SaferProducts). Each entry
  carries one or more queries (ProductName, RecallTitle, or
  RecallNumber, the fields the CPSC fetcher supports). The field that
  matters is the set of recall numbers found across the entry's
  queries, plus each query's record count. A product is tracked under
  name variants and, once known, its recall number, because a
  ProductName search can miss a record that stands in the same
  database (see docs/standing-watch.md).

Nothing here invents or interprets: values are stored and reported
exactly as shown in the responses, and codes are reported as shown.

Watchlist format (JSON):

    {
      "version": 1,
      "carriers": [
        {"usdot": "90849", "label": "OLD DOMINION FREIGHT LINE INC"}
      ],
      "products": [
        {"label": "Peloton Tread+",
         "queries": [{"field": "RecallNumber", "value": "21-128"},
                     {"field": "ProductName", "value": "Tread+"}]}
      ]
    }

A carrier needs only its USDOT number; the label is optional. A
product needs a label and at least one query.

Snapshot storage follows the repo fixture habits: the snapshot JSON
keeps, for every response, the exact query URL, the UTC retrieval
time, the HTTP status line, the SHA-256 of the raw transcript, and the
complete raw transcript itself (the FMCSA fetcher's transcript for
carriers, the curl capture for products). A no change claim can
therefore be checked against the stored pull, hash first.

Fail closed, like the fetchers: a transport failure or an
uninterpretable response aborts the run, prints nothing to the report,
leaves the previous snapshot untouched, and exits 2. An HTTP error
status from FMCSA is data, not a failure: it is recorded in the
provenance and the entry's fields read as not determinable, the way
the carrier fetcher renders it.

Usage:

    python3 tools/standing_watch.py \
        --watchlist tools/examples/standing-watch/watchlist.json \
        --snapshot /path/to/snapshot.json \
        --report /path/to/report.md

--report may be omitted, in which case the report goes to stdout. The
snapshot file is read (when it exists) as the previous snapshot and
then overwritten with this run's snapshot. Standard library only; the
CPSC fetcher also needs the system curl, as its own header says.
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
from pathlib import Path

import cpsc_recalls as cpsc
import fmcsa_carrier as fc

SNAPSHOT_FORMAT = "standing-watch-snapshot"
CARRIER_SOURCES = ("census", "safer", "li")


class WatchError(ValueError):
    """A watchlist or snapshot problem. Never rendered as a result."""


# ----------------------------------------------------------------------
# Watchlist
# ----------------------------------------------------------------------

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "entry"


def entry_keys(watchlist):
    keys = []
    for entry in watchlist["carriers"]:
        keys.append("carrier:%s" % entry["usdot"])
    for entry in watchlist["products"]:
        keys.append("product:%s" % slug(entry["label"]))
    return keys


def validate_watchlist(data, origin):
    if not isinstance(data, dict):
        raise WatchError("%s: the watchlist must be a JSON object" % origin)
    if data.get("version") != 1:
        raise WatchError("%s: \"version\" must be 1" % origin)
    carriers = data.get("carriers", [])
    products = data.get("products", [])
    if not isinstance(carriers, list) or not isinstance(products, list):
        raise WatchError("%s: \"carriers\" and \"products\" must be arrays" % origin)
    out_carriers = []
    for i, entry in enumerate(carriers):
        if not isinstance(entry, dict) or "usdot" not in entry:
            raise WatchError("%s: carriers[%d] needs a \"usdot\" number" % (origin, i))
        try:
            usdot = fc.check_usdot(entry["usdot"])
        except ValueError as err:
            raise WatchError("%s: carriers[%d]: %s" % (origin, i, err))
        label = entry.get("label") or "USDOT %s" % usdot
        if not isinstance(label, str) or not label.strip():
            raise WatchError("%s: carriers[%d] label must be text" % (origin, i))
        out_carriers.append({"usdot": usdot, "label": label})
    out_products = []
    for i, entry in enumerate(products):
        if not isinstance(entry, dict) or not str(entry.get("label", "")).strip():
            raise WatchError("%s: products[%d] needs a \"label\"" % (origin, i))
        queries = entry.get("queries")
        if not isinstance(queries, list) or not queries:
            raise WatchError("%s: products[%d] needs at least one query" % (origin, i))
        out_queries = []
        for j, query in enumerate(queries):
            if not isinstance(query, dict):
                raise WatchError("%s: products[%d] queries[%d] must be an object" % (origin, i, j))
            field = query.get("field")
            value = query.get("value")
            if field not in cpsc.FIELDS:
                raise WatchError(
                    "%s: products[%d] queries[%d] field must be one of %s"
                    % (origin, i, j, ", ".join(cpsc.FIELDS)))
            if not isinstance(value, str) or not value.strip():
                raise WatchError("%s: products[%d] queries[%d] value must be text" % (origin, i, j))
            out_queries.append({"field": field, "value": value})
        out_products.append({"label": entry["label"], "queries": out_queries})
    watchlist = {"carriers": out_carriers, "products": out_products}
    keys = entry_keys(watchlist)
    if not keys:
        raise WatchError("%s: the watchlist has no entries" % origin)
    if len(set(keys)) != len(keys):
        raise WatchError("%s: two entries reduce to the same watch key (%s)"
                         % (origin, ", ".join(sorted({k for k in keys if keys.count(k) > 1}))))
    return watchlist


def load_watchlist(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as err:
        raise WatchError("cannot read the watchlist %s: %s" % (path, err))
    except ValueError as err:
        raise WatchError("the watchlist %s is not valid JSON: %s" % (path, err))
    return validate_watchlist(data, str(path))


# ----------------------------------------------------------------------
# Field extraction: only what the fetchers actually return
# ----------------------------------------------------------------------

def carrier_fields(usdot, captures):
    """captures: {"census": Capture, "safer": Capture, "li": Capture} for
    the carrier with this USDOT number. Returns the flat field map,
    values as shown, None where the source does not show a value."""
    fields = {}
    census = captures["census"]
    record = None
    count = None
    if census.status_ok:
        try:
            records = fc.parse_census(census.body)
        except ValueError:
            records = None
        if records is not None:
            count = len(records)
            for candidate in records:
                if str(candidate.get("dot_number", "")) == str(usdot):
                    record = candidate
                    break
            if record is None and len(records) == 1:
                record = records[0]
    fields["census.record_count"] = count
    for field in fc.CENSUS_FIELDS:
        value = record.get(field) if record else None
        fields["census.%s" % field] = (
            str(value) if value is not None and str(value) != "" else None)
    safer = captures["safer"]
    if safer.status_ok:
        found = fc.labelled_values(fc.text_lines(safer.body), fc.SAFER_LABELS,
                                   fc.SAFER_MULTILINE, fc.SAFER_STOP_PREFIXES)
        for label in fc.SAFER_LABELS:
            fields["safer.%s" % label] = fc.value_text(found[label])
    else:
        for label in fc.SAFER_LABELS:
            fields["safer.%s" % label] = None
    li = captures["li"]
    if li.status_ok:
        fields["li.record_lines"] = [
            line for line in fc.text_lines(li.body) if line.startswith(fc.LI_PREFIXES)]
    else:
        fields["li.record_lines"] = None
    return fields


def product_fields(queries, captures):
    """queries: the entry's query dicts; captures: the CPSC Capture for
    each query, in the same order. Returns the field map: the sorted
    set of recall numbers as shown across all queries, and each
    query's record count. Raises cpsc.FetchError when a response is
    not a readable recall result, so a bad response aborts the run
    instead of reading as empty."""
    numbers = set()
    fields = {"recall_numbers": []}
    for query, capture in zip(queries, captures):
        rows = cpsc.records(capture)
        fields["query.%s=%s.record_count" % (query["field"], query["value"])] = len(rows)
        for row in rows:
            numbers.add(row["RecallNumber"])
    fields["recall_numbers"] = sorted(numbers)
    return fields


# ----------------------------------------------------------------------
# Fetching one entry (live)
# ----------------------------------------------------------------------

def _response(source, capture, raw, extra=None):
    response = {
        "source": source,
        "url": capture.url,
        "retrieved_utc": capture.retrieved,
        "status": capture.status_line if hasattr(capture, "status_line")
                  else raw.split("\n", 1)[0].strip(),
        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "raw": raw,
    }
    if extra:
        response.update(extra)
    return response


def fetch_carrier_entry(entry):
    urls = {"census": fc.census_record_url, "safer": fc.safer_url, "li": fc.li_url}
    captures = {}
    for source in CARRIER_SOURCES:
        captures[source] = fc.fetch(urls[source](entry["usdot"]))
    return {
        "watch_id": "carrier:%s" % entry["usdot"],
        "type": "carrier",
        "label": entry["label"],
        "usdot": entry["usdot"],
        "fields": carrier_fields(entry["usdot"], captures),
        "responses": [_response(s, captures[s], captures[s].transcript) for s in CARRIER_SOURCES],
        "_captures": captures,
    }


def fetch_product_entry(entry):
    captures = [cpsc.fetch(q["value"], q["field"]) for q in entry["queries"]]
    fields = product_fields(entry["queries"], captures)
    responses = []
    for query, capture in zip(entry["queries"], captures):
        responses.append(_response("cpsc", capture, capture.raw,
                                   {"field": query["field"], "value": query["value"]}))
    return {
        "watch_id": "product:%s" % slug(entry["label"]),
        "type": "product",
        "label": entry["label"],
        "queries": entry["queries"],
        "fields": fields,
        "responses": responses,
        "_captures": captures,
    }


# ----------------------------------------------------------------------
# Snapshot
# ----------------------------------------------------------------------

def build_snapshot(watchlist_name, results, run_utc):
    entries = {}
    for result in results:
        entry = {"type": result["type"], "label": result["label"],
                 "fields": result["fields"], "responses": result["responses"]}
        if result["type"] == "carrier":
            entry["usdot"] = result["usdot"]
        else:
            entry["queries"] = result["queries"]
        entries[result["watch_id"]] = entry
    return {"format": SNAPSHOT_FORMAT, "version": 1,
            "watchlist_file": watchlist_name, "run_utc": run_utc, "entries": entries}


def load_snapshot(path):
    """The previous snapshot dict, or None when no snapshot exists yet.
    A snapshot that exists but does not parse is an error, never a
    silent baseline."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as err:
        raise WatchError("the snapshot %s is not valid JSON: %s" % (path, err))
    if not isinstance(data, dict) or data.get("format") != SNAPSHOT_FORMAT \
            or not isinstance(data.get("entries"), dict):
        raise WatchError("the snapshot %s is not a standing watch snapshot" % path)
    return data


# ----------------------------------------------------------------------
# Diff
# ----------------------------------------------------------------------

def diff_entries(prev_entry, cur_entry):
    """[(field, old, new)] in field order: current order first, then
    fields only the previous snapshot carried."""
    prev_fields = prev_entry["fields"] if prev_entry else {}
    cur_fields = cur_entry["fields"]
    changes = []
    for field, new in cur_fields.items():
        old = prev_fields.get(field)
        if field not in prev_fields or old != new:
            changes.append((field, old, new))
    for field, old in prev_fields.items():
        if field not in cur_fields:
            changes.append((field, old, None))
    return changes


def diff_snapshots(prev, cur):
    """{key: {"status": same|changed|new|removed, "changes": [...]}}."""
    out = {}
    prev_entries = prev["entries"] if prev else {}
    for key, entry in cur["entries"].items():
        if key not in prev_entries:
            out[key] = {"status": "new" if prev else "baseline", "changes": []}
        else:
            changes = diff_entries(prev_entries[key], entry)
            out[key] = {"status": "changed" if changes else "same", "changes": changes}
    for key in prev_entries:
        if key not in cur["entries"]:
            out[key] = {"status": "removed", "changes": []}
    return out


# ----------------------------------------------------------------------
# Report rendering
# ----------------------------------------------------------------------

def shown(value):
    if value is None:
        return "not present in the record"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "none"
    return str(value)


def fields_table(fields):
    lines = ["| Field | Value as shown |", "| --- | --- |"]
    for field, value in fields.items():
        lines.append("| %s | %s |" % (field, shown(value).replace("|", "\\|")))
    return lines


def evidence_lines(result):
    """The full source evidence for one entry, in the fixed delivery
    format, reusing the fetchers' own renderers."""
    lines = []
    if result["type"] == "carrier":
        captures = result["_captures"]
        sections = (fc.census_section(result["usdot"], captures["census"]),
                    fc.safer_section(result["usdot"], captures["safer"]),
                    fc.li_section(result["usdot"], captures["li"]))
        for section in sections:
            lines.extend(section)
            lines.append("")
    else:
        for capture in result["_captures"]:
            lines.extend(cpsc.render_query(capture).rstrip("\n").split("\n"))
            lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def provenance_lines(result):
    lines = []
    for response in result["responses"]:
        lines.append("  Source: %s, retrieved %s, response SHA-256 %s"
                     % (response["url"], response["retrieved_utc"], response["sha256"]))
    return lines


def describe(result):
    if result["type"] == "carrier":
        return "%s (carrier, USDOT %s)" % (result["label"], result["usdot"])
    return "%s (product)" % result["label"]


def render_report(watchlist_name, results, snapshot, prev, diff):
    run_utc = snapshot["run_utc"]
    lines = []
    if prev is None:
        lines += ["# Standing watch: baseline edition", "",
                  "Watchlist: %s" % watchlist_name,
                  "Run (UTC): %s" % run_utc, "",
                  "The first run on a list establishes the baseline: the state of "
                  "every entry as the public record shows it now. Later runs pull "
                  "the same sources again and report only what changed against "
                  "this baseline. Every value below is as shown in its source; "
                  "the complete raw response for each query is printed beneath "
                  "its source link, and the same pulls are stored in this run's "
                  "snapshot file with their SHA-256 hashes.", ""]
        for result in results:
            lines += ["## %s" % describe(result), "", "### Fields that matter", ""]
            lines += fields_table(result["fields"])
            lines += ["", "### Source evidence", ""]
            lines += evidence_lines(result)
            lines.append("")
        return "\n".join(lines).rstrip("\n") + "\n"
    changed = [r for r in results if diff[r["watch_id"]]["status"] == "changed"]
    new = [r for r in results if diff[r["watch_id"]]["status"] == "new"]
    same = [r for r in results if diff[r["watch_id"]]["status"] == "same"]
    removed = [k for k, d in diff.items() if d["status"] == "removed"]
    lines += ["# Standing watch: change report", "",
              "Watchlist: %s" % watchlist_name,
              "Previous snapshot (UTC): %s" % prev["run_utc"],
              "This run (UTC): %s" % run_utc, "",
              "Entries checked: %d. Changed: %d. New: %d. No change: %d. "
              "No longer on the watchlist: %d."
              % (len(results), len(changed), len(new), len(same), len(removed)), ""]
    if changed:
        lines += ["## Change alerts", ""]
        for result in changed:
            lines += ["### %s" % describe(result), ""]
            for field, old, new_value in diff[result["watch_id"]]["changes"]:
                lines.append("- %s: changed from %s to %s"
                             % (field, shown(old), shown(new_value)))
            lines += ["", "Source evidence for the new state:", ""]
            lines += evidence_lines(result)
            lines.append("")
    if new:
        lines += ["## New on the watchlist", ""]
        for result in new:
            lines += ["### %s" % describe(result), "", "### Fields that matter", ""]
            lines += fields_table(result["fields"])
            lines += ["", "### Source evidence", ""]
            lines += evidence_lines(result)
            lines.append("")
    if removed:
        lines += ["## No longer on the watchlist", ""]
        for key in removed:
            entry = prev["entries"][key]
            lines.append("- %s (%s) was on the previous snapshot and is not on "
                         "the current watchlist." % (entry["label"], key))
        lines.append("")
    if same:
        lines += ["## No change", ""]
        for result in same:
            lines.append("- %s: no change in the fields that matter."
                         % describe(result))
            lines += provenance_lines(result)
        lines.append("")
    if not changed and not new and not removed:
        lines += ["No entry changed in this run.", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


# ----------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------

def run_watch(watchlist, watchlist_name, prev, run_utc):
    results = []
    for entry in watchlist["carriers"]:
        results.append(fetch_carrier_entry(entry))
    for entry in watchlist["products"]:
        results.append(fetch_product_entry(entry))
    snapshot = build_snapshot(watchlist_name, results, run_utc)
    diff = diff_snapshots(prev, snapshot)
    report = render_report(watchlist_name, results, snapshot, prev, diff)
    return snapshot, report, diff


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Recheck a standing watch list and report what changed.")
    parser.add_argument("--watchlist", required=True, help="watchlist JSON file")
    parser.add_argument("--snapshot", required=True,
                        help="snapshot JSON file: read as the previous snapshot when "
                        "it exists, then overwritten with this run's snapshot")
    parser.add_argument("--report",
                        help="write the Markdown report here; default stdout")
    args = parser.parse_args(argv)
    try:
        watchlist = load_watchlist(args.watchlist)
        prev = load_snapshot(args.snapshot)
        snapshot, report, _diff = run_watch(
            watchlist, Path(args.watchlist).name, prev, fc.utc_now_iso())
    except WatchError as err:
        sys.stderr.write("standing watch: %s\n" % err)
        return 2
    except cpsc.FetchError as err:
        sys.stderr.write("standing watch: CPSC fetch failed: %s; no report, "
                         "snapshot untouched\n" % err)
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("standing watch: fetch failed: %s; no report, "
                         "snapshot untouched\n" % err)
        return 2
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    Path(args.snapshot).write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    changed = sum(1 for d in _diff.values() if d["status"] == "changed")
    sys.stderr.write("standing watch: %d entries checked, %d changed; snapshot "
                     "written to %s\n" % (len(snapshot["entries"]), changed, args.snapshot))
    return 0


if __name__ == "__main__":
    sys.exit(main())
