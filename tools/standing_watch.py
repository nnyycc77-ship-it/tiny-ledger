#!/usr/bin/env python3
"""Standing watch: recheck a buyer list and report only what changed.

A buyer supplies a watchlist (JSON, format below). Each run pulls the
same public sources the delivery fetchers use, stores a dated snapshot
of the fields that matter, diffs the new snapshot against the previous
one, and emits a Markdown report: a baseline edition on the first run,
after that a change report (alerts for changed entries, one line for
each entry with no change).

Three watch types, all reusing the existing fetchers in this folder:

* Carriers, by USDOT number, through `fmcsa_carrier.py` (FMCSA Company
  Census File, SAFER Company Snapshot, Licensing and Insurance). The
  fields that matter are the ones the fetcher returns: the Census
  record fields as shown (status_code and docket1_status_code carry
  the authority state, safety_rating the rating), every labelled SAFER
  value (Operating Authority Status, USDOT Status, Rating, and the
  rest), and the Licensing and Insurance record lines found.
* Sanctions entries, through `ofac_sdn_check.py` (the OFAC SDN list,
  primary names and aliases) and `oig_screen.py` (the HHS OIG LEIE
  database). Each entry names one list and one subject name, taken the
  way the fetcher takes it. The fields that matter are only what the
  fetchers return: the match state and the matched record fields as
  shown. An empty result is proven by the full downloaded list file,
  stored in the snapshot like every other response.
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
      ],
      "sanctions": [
        {"list": "OFAC SDN", "subject": "BANCO NACIONAL DE CUBA"},
        {"list": "OIG LEIE", "subject": "1 BEST CARE, INC",
         "label": "Best Care (watch)"}
      ]
    }

A carrier needs only its USDOT number; the label is optional. A
product needs a label and at least one query. A sanctions entry needs
a list (OFAC SDN or OIG LEIE) and a subject name with at least as many
letters or digits as the fetchers require; the label is optional and
defaults to the subject.

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
import ofac_sdn_check as ofac
import oig_screen as oig

SNAPSHOT_FORMAT = "standing-watch-snapshot"
CARRIER_SOURCES = ("census", "safer", "li")
SANCTIONS_LISTS = ("OFAC SDN", "OIG LEIE")


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
    for entry in watchlist["sanctions"]:
        keys.append("sanctions:%s:%s" % (slug(entry["list"]), slug(entry["subject"])))
    return keys


def validate_watchlist(data, origin):
    if not isinstance(data, dict):
        raise WatchError("%s: the watchlist must be a JSON object" % origin)
    if data.get("version") != 1:
        raise WatchError("%s: \"version\" must be 1" % origin)
    carriers = data.get("carriers", [])
    products = data.get("products", [])
    sanctions = data.get("sanctions", [])
    if not isinstance(carriers, list) or not isinstance(products, list) \
            or not isinstance(sanctions, list):
        raise WatchError("%s: \"carriers\", \"products\" and \"sanctions\" must be arrays" % origin)
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
    out_sanctions = []
    for i, entry in enumerate(sanctions):
        if not isinstance(entry, dict) or entry.get("list") not in SANCTIONS_LISTS:
            raise WatchError("%s: sanctions[%d] list must be one of %s"
                             % (origin, i, ", ".join(SANCTIONS_LISTS)))
        subject = entry.get("subject")
        if not isinstance(subject, str) or not subject.strip():
            raise WatchError("%s: sanctions[%d] needs a \"subject\" name" % (origin, i))
        subject = " ".join(subject.split())
        if ofac.significant(subject) < ofac.MIN_QUERY_CHARS:
            raise WatchError("%s: sanctions[%d] subject must have at least %d letters or digits, "
                             "the minimum the fetchers accept" % (origin, i, ofac.MIN_QUERY_CHARS))
        label = entry.get("label") or subject
        if not isinstance(label, str) or not label.strip():
            raise WatchError("%s: sanctions[%d] label must be text" % (origin, i))
        out_sanctions.append({"list": entry["list"], "subject": subject, "label": label})
    watchlist = {"carriers": out_carriers, "products": out_products, "sanctions": out_sanctions}
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


def ofac_fields(subject, sdn, alt):
    """The fields that matter for one OFAC SDN entry, from the two
    downloads: the match state and one line per matched list entry,
    carrying the matched record fields the fetcher itself shows (the
    entry number, the name and type as shown, and how the subject
    matched). Raises ofac.FetchError when a file is not in the
    captured shape, so a bad file aborts the run."""
    sdn_rows, _o, _n, _e = ofac.rows(sdn, 1, "SDN.CSV")
    alt_rows, _o2, _n2, _e2 = ofac.rows(alt, 3, "ALT.CSV")
    by_ent = {}
    for _number, _raw, fields in alt_rows:
        by_ent.setdefault(fields[0].strip(), []).append(fields)
    matched = []
    for _number, _raw, fields in sdn_rows:
        ent = fields[0].strip()
        found = []
        kind = ofac.match_kind(subject, fields[1])
        if kind:
            found.append((kind, "primary name", fields[1]))
        for alt_fields in by_ent.get(ent, []):
            akind = ofac.match_kind(subject, alt_fields[3])
            if akind:
                found.append((akind, "alias", alt_fields[3]))
        if found:
            matched.append(
                "ENT_NUM %s: %s; type as shown: %s; matched: %s"
                % (ent, fields[1],
                   fields[2].strip() if len(fields) > 2 and fields[2].strip() else "not present",
                   "; ".join("%s match on the %s %s" % f for f in found)))
    return {"match_state": "match" if matched else "no match",
            "matched_entries": matched}


def oig_fields(subject, download):
    """The fields that matter for one OIG LEIE entry, from the
    download: the match state and one line per matched row, carrying
    the matched record fields the fetcher itself shows (the name as
    shown, the exclusion fields as published, and how the subject
    matched). Raises oig.FetchError when the file is not in the
    captured shape."""
    data_rows, _n, _e = oig.rows(download)
    matched = []
    for number, _raw, row in data_rows:
        found = oig.best_match(subject, row)
        if found:
            kind, form_label, name = found
            matched.append(
                "Line %d: %s; EXCLTYPE as published: %s; EXCLDATE as published: %s; "
                "REINDATE as published: %s; WAIVERDATE as published: %s; matched: %s match "
                "on %s (%s)"
                % (number, oig.shown_name(row), row["EXCLTYPE"], row["EXCLDATE"],
                   row["REINDATE"], row["WAIVERDATE"], kind, name, form_label))
    return {"match_state": "match" if matched else "no match",
            "matched_rows": matched}


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


def _download_response(source, download, decode):
    """The snapshot response record for one downloaded list file. The
    hash is over the file bytes themselves, the identity the fetchers
    print in their own file blocks; the raw text stored is the file
    decoded the way the owning fetcher decodes it, so the stored pull
    is the full response an empty result is proven against."""
    text, _encoding = decode(download)
    return {"source": source, "url": download.url,
            "retrieved_utc": download.retrieved,
            "status": "downloaded (the fetcher raises on any non 200 response)",
            "sha256": hashlib.sha256(download.data).hexdigest(),
            "raw": text}


def fetch_sanctions_entry(entry):
    if entry["list"] == "OFAC SDN":
        sdn = ofac.fetch(ofac.SDN_URL)
        alt = ofac.fetch(ofac.ALT_URL)
        fields = ofac_fields(entry["subject"], sdn, alt)
        downloads = {"sdn": sdn, "alt": alt}
        responses = [_download_response("ofac_sdn", sdn, ofac.decode),
                     _download_response("ofac_alt", alt, ofac.decode)]
    else:
        leie = oig.fetch(oig.LEIE_URL)
        fields = oig_fields(entry["subject"], leie)
        downloads = {"leie": leie}
        responses = [_download_response("oig_leie", leie, oig.decode)]
    return {
        "watch_id": "sanctions:%s:%s" % (slug(entry["list"]), slug(entry["subject"])),
        "type": "sanctions",
        "label": entry["label"],
        "list": entry["list"],
        "subject": entry["subject"],
        "fields": fields,
        "responses": responses,
        "_downloads": downloads,
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
        elif result["type"] == "sanctions":
            entry["list"] = result["list"]
            entry["subject"] = result["subject"]
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
    elif result["type"] == "sanctions":
        downloads = result["_downloads"]
        if result["list"] == "OFAC SDN":
            lines.extend(ofac.render(result["subject"], downloads["sdn"],
                                     downloads["alt"]).rstrip("\n").split("\n"))
        else:
            lines.extend(oig.render(result["subject"], downloads["leie"]))
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
    if result["type"] == "sanctions":
        return "%s (sanctions, %s)" % (result["label"], result["list"])
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
    for entry in watchlist["sanctions"]:
        results.append(fetch_sanctions_entry(entry))
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
    except (ofac.FetchError, oig.FetchError) as err:
        sys.stderr.write("standing watch: sanctions fetch failed: %s; "
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
