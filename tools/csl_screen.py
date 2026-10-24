#!/usr/bin/env python3
"""US Consolidated Screening List screen (issue #179, tool factory wave 2).

Given a person or company name, screens it against the Consolidated
Screening List (CSL) published by the International Trade Administration
on trade.gov, and prints one Markdown report in the delivery format from
AGENT-BRIEF.md: the matching rule, the file read (exact URL, UTC
retrieval time, the list publication date as published, response
headers, bytes, SHA-256, rows screened), and every matching entry with
its list name, its program, and its matched raw row printed in full
beneath the source link.

    python3 tools/csl_screen.py "Huawei Technologies"

The CSL is the United States government's consolidated download of the
lists named in the question this tool answers: the Entity List, the
Denied Persons List, the Unverified List and the Military End User List
(Bureau of Industry and Security), the ITAR Debarred list (State
Department), and the Treasury lists the file carries, among them the
Specially Designated Nationals (SDN) list. The rows screened are the
rows of the file exactly as read; the source column of each row names
its list, and the report prints that name as shown.

Source (linked as the downloadable CSV from the Consolidated Screening
List page, https://www.trade.gov/consolidated-screening-list, read
2026-10-24):

  consolidated.csv  https://data.trade.gov/downloadable_consolidated_screening_list/v1/consolidated.csv
                    one CSV whose header, as captured, is: _id, source,
                    entity_number, type, programs, name, title,
                    addresses, federal_register_notice, start_date,
                    end_date, standard_order, license_requirement,
                    license_policy, call_sign, vessel_type,
                    gross_tonnage, gross_registered_tonnage, vessel_flag,
                    vessel_owner, remarks, source_list_url, alt_names,
                    citizenships, dates_of_birth, nationalities,
                    places_of_birth, source_information_url, ids.
                    The name printed for screening is the name column;
                    the aliases screened are the entries of the alt_names
                    column, separated by "; " in the file as captured.
                    The list publication date this tool reports is the
                    file's Last-Modified response header, the date the
                    source itself publishes for the file.

Pattern: the file is downloaded once and cached locally (under
tools/.csl_cache/, never committed); a run whose cache is younger than
24 hours matches against the cache and says so, with the original
retrieval time, and --refresh downloads again. A cached copy is the
file exactly as downloaded: its bytes and SHA-256 are printed either
way, so the screen can be repeated against the same file.

Matching rule (the rule of the OFAC SDN check already on the shelf,
issue #160), stated in every report: names are compared after folding
case and replacing every character that is not a letter or digit with a
space. An exact match is the whole normalised query equal to the whole
normalised name; a contains match is the normalised query appearing
inside the normalised name as whole words. The name column and every
alt_names entry are both checked. No fuzzy or phonetic score is
computed or claimed.

No match is proven by the file itself as read: the list publication
date, the number of rows screened, the byte size and the SHA-256 are
printed with the rule, so the screen can be repeated against the same
file. The multi-megabyte file is not pasted.

Fail closed: a failed request, a non 200 answer, a header that is not
the published header, or a row that is not the published width stops
the run with exit 2 and no report; a failed fetch is never shown as no
match. Observation only: a name match is not a determination that a
party is the listed person or entity, and no match is not a screening
clearance.

Standard library only.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CSL_URL = "https://data.trade.gov/downloadable_consolidated_screening_list/v1/consolidated.csv"
USER_AGENT = "tiny-ledger-csl-screen"
TIMEOUT_SECONDS = 120
MIN_QUERY_CHARS = 3
MAX_LISTED = 50
CACHE_TTL_SECONDS = 24 * 60 * 60
CACHE_DIR = Path(__file__).resolve().parent / ".csl_cache"
HEADER = ["_id", "source", "entity_number", "type", "programs", "name", "title", "addresses",
          "federal_register_notice", "start_date", "end_date", "standard_order", "license_requirement",
          "license_policy", "call_sign", "vessel_type", "gross_tonnage", "gross_registered_tonnage",
          "vessel_flag", "vessel_owner", "remarks", "source_list_url", "alt_names", "citizenships",
          "dates_of_birth", "nationalities", "places_of_birth", "source_information_url", "ids"]
COL = {name: i for i, name in enumerate(HEADER)}
SHOWN_HEADERS = ("Content-Type", "Content-Length", "Last-Modified", "ETag", "Date")
RULE = ("Names are compared after folding case and replacing every character that is not a letter or "
        "digit with a space. An exact match is the whole normalised query equal to the whole normalised "
        "name; a contains match is the normalised query appearing inside the normalised name as whole "
        "words. The name column and every alt_names entry are both checked. No fuzzy or phonetic score "
        "is computed or claimed.")
OBSERVATION = ("Observation only: this report records what the Consolidated Screening List file "
               "contained when read at the time below. A name match is not a determination that a "
               "party is the listed person or entity, and no match is not a screening clearance.")


class FetchError(ValueError):
    """A failed or unreadable source file. Never an empty result."""


class Download:
    """The list file as read: requested URL, retrieval time, headers shown, bytes.

    from_cache is None for a fresh download, or the cache directory the
    copy was read from; the retrieval time is always the time the file
    was downloaded, never the time it was read back from the cache."""

    def __init__(self, url, retrieved, headers, data, from_cache=None):
        self.url = url
        self.retrieved = retrieved
        self.headers = headers  # [(name, value)] limited to SHOWN_HEADERS, as returned
        self.data = data
        self.from_cache = from_cache

    def header(self, name):
        for k, v in self.headers:
            if k.lower() == name.lower():
                return v
        return None


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET the list file. Raises FetchError."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            headers = [(k, v) for k, v in response.headers.items()
                       if k.lower() in {h.lower() for h in SHOWN_HEADERS}]
            data = response.read()
    except urllib.error.HTTPError as err:
        err.close()
        raise FetchError("%s answered HTTP %s %s; no report" % (url, err.code, err.reason))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("%s answered HTTP %s; no report" % (url, status))
    return Download(url, retrieved, headers, data)


def cache_dir():
    override = os.environ.get("CSL_CACHE_DIR")
    return Path(override) if override else CACHE_DIR


def load(fetcher=None, refresh=False, directory=None):
    """The Download to screen: a fresh cache copy when one is in date, else a download.

    A cache copy is used only when its sidecar names this URL, its bytes
    still hash to the sidecar SHA-256, and it is younger than the TTL; a
    copy that fails any of those checks is downloaded again. A failed
    download never falls back to a stale or unreadable cache: it is a
    source failure, reported as one.
    """
    fetcher = fetcher or fetch
    directory = Path(directory) if directory is not None else cache_dir()
    body_path = directory / "consolidated.csv"
    side_path = directory / "consolidated.json"
    if not refresh and body_path.exists() and side_path.exists():
        try:
            side = json.loads(side_path.read_text(encoding="utf-8"))
            data = body_path.read_bytes()
            fresh = time.time() - float(side["stored_epoch"]) < CACHE_TTL_SECONDS
            if (side["url"] == CSL_URL and fresh
                    and hashlib.sha256(data).hexdigest() == side["sha256"]):
                return Download(CSL_URL, side["retrieved"], [tuple(h) for h in side["headers"]],
                                data, from_cache=directory)
        except (ValueError, KeyError, OSError):
            pass  # an unreadable cache is no cache; download below
    download = fetcher(CSL_URL)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(download.data)
        side_path.write_text(json.dumps({
            "url": CSL_URL, "retrieved": download.retrieved, "stored_epoch": time.time(),
            "sha256": hashlib.sha256(download.data).hexdigest(),
            "headers": [list(h) for h in download.headers]}, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass  # the cache is an optimisation; a screen that cannot cache still reports
    return download


def normalise(text):
    """Case folded, every non letter or digit a single space, trimmed."""
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text.casefold()).split())


def significant(text):
    """How many letters and digits the name has once normalised."""
    return len(normalise(text).replace(" ", ""))


def match_kind(query, name):
    """'exact', 'contains' (whole words) or None."""
    q, n = normalise(query), normalise(name)
    if not q:
        return None
    if q == n:
        return "exact"
    if (" %s " % q) in (" %s " % n):
        return "contains"
    return None


def decode(download):
    try:
        return download.data.decode("utf-8"), "UTF-8"
    except UnicodeDecodeError:
        return download.data.decode("latin-1"), "Latin-1 (the bytes are not valid UTF-8)"


def parse(download):
    """(rows, line_count, encoding): each data row as (file line number, raw line, fields).

    The header must be the published header exactly, and every data row
    must carry every published column; anything else is not the file
    this tool screens and is refused.
    """
    text, encoding = decode(download)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        raise FetchError("%s answered an empty body; no report" % CSL_URL)
    reader = csv.reader(io.StringIO(text))
    records = list(reader)
    if not records or records[0] != HEADER:
        raise FetchError("%s is not in the published shape (its header is not the published CSL header); "
                         "no report" % CSL_URL)
    rows = []
    for number, fields in enumerate(records[1:], 2):
        if len(fields) != len(HEADER):
            raise FetchError("%s is not in the published shape (line %d has %d fields, the header has "
                             "%d); no report" % (CSL_URL, number, len(fields), len(HEADER)))
        raw = lines[number - 1] if number - 1 < len(lines) else ""
        rows.append((number, raw[:-1] if raw.endswith("\r") else raw, fields))
    return rows, len(lines), encoding


def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def aliases(fields):
    """The alt_names entries, in the order the file prints them."""
    return [a.strip() for a in fields[COL["alt_names"]].split(";") if a.strip()]


def render(query, download):
    """The report for one query from one Download. Raises FetchError."""
    if significant(query) < MIN_QUERY_CHARS:
        raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
    rows, line_count, encoding = parse(download)
    matches = []
    for number, raw, fields in rows:
        found = []
        kind = match_kind(query, fields[COL["name"]])
        if kind:
            found.append((kind, "name", fields[COL["name"]]))
        for alias in aliases(fields):
            akind = match_kind(query, alias)
            if akind:
                found.append((akind, "alias", alias))
        if found:
            matches.append((number, raw, fields, found))
    list_date = download.header("Last-Modified") or "not returned by the source"
    lines = ["# Consolidated Screening List screen: %s" % query, "", OBSERVATION, "",
             "## Matching rule", "", RULE, "", "## File read", "",
             "Exact query: GET %s" % download.url,
             "Retrieved (UTC): %s" % download.retrieved]
    if download.from_cache is not None:
        lines.append("Read from the local cache at %s: the file exactly as downloaded at the "
                     "retrieval time above." % download.from_cache)
    lines += ["List publication date as published (the file's Last-Modified header): %s" % list_date,
              "File as read: %d bytes, SHA-256 %s, %d lines, decoded as %s; %d rows screened."
              % (len(download.data), hashlib.sha256(download.data).hexdigest(), line_count,
                 encoding, len(rows)), ""]
    if download.headers:
        lines += ["Response headers as returned (the ones listed in the tool):", "```",
                  "\n".join("%s: %s" % kv for kv in download.headers), "```", ""]
    lines += ["## Result", ""]
    if not matches:
        lines += ["No name or alias matched %s under the rule above. Screened: %d rows of the "
                  "Consolidated Screening List as published on %s (file SHA-256 %s), the file exactly "
                  "as read above." % (query, len(rows), list_date,
                                      hashlib.sha256(download.data).hexdigest()), ""]
        return "\n".join(lines)
    exact = sum(1 for m in matches if any(f[0] == "exact" for f in m[3]))
    lines += ["%d list entr%s matched %s: %d with an exact match, %d by contains match only."
              % (len(matches), "y" if len(matches) == 1 else "ies", query, exact,
                 len(matches) - exact), ""]
    if len(matches) > MAX_LISTED:
        lines += ["The first %d, in file order, are listed; %d more matched and are not listed."
                  % (MAX_LISTED, len(matches) - MAX_LISTED), ""]
    for number, raw, fields, found in matches[:MAX_LISTED]:
        lines += ["### %s" % fields[COL["name"]], "",
                  "- List as shown (source): %s" % fields[COL["source"]],
                  "- Program as shown: %s" % (fields[COL["programs"]] or "not shown"),
                  "- Type as shown: %s" % (fields[COL["type"]] or "not shown")]
        lines += ["- Matched: %s match on the %s %s" % (kind, where, name) for kind, where, name in found]
        lines += ["", "Source: <%s>, line %d of the file as read" % (CSL_URL, number), fenced(raw), ""]
    return "\n".join(lines)


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Screen a name against the US Consolidated Screening List.")
    p.add_argument("name", help="person or company name")
    p.add_argument("--refresh", action="store_true",
                   help="download the list again instead of using a cache copy in date")
    args = p.parse_args(argv)
    try:
        if significant(args.name) < MIN_QUERY_CHARS:
            raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
        report = render(args.name, load(fetcher=fetcher, refresh=args.refresh))
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
