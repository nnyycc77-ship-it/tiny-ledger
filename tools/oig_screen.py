#!/usr/bin/env python3
"""HHS OIG exclusion screen (issue #180, tool factory wave 2).

Is this person or entity on the HHS OIG List of Excluded Individuals and
Entities (LEIE)? Downloads the complete current LEIE database, keyless,
screens every row for the name, and prints one Markdown report in the
delivery format from AGENT-BRIEF.md: the answer first, with each matched
row's exclusion type and exclusion date as published, then the evidence:
the exact query, the UTC retrieval time, the database date, the file's
size, SHA-256 and row count, and each matched raw row in full.

    python3 tools/oig_screen.py "Aaron Smith"
    python3 tools/oig_screen.py "1 Best Care"

Source, grounded in the coordinator's captures on issue #180 (comments
6380708777 to 6380713028):
- The file is https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv,
  linked as "Updated LEIE Database (CSV)" from the LEIE Database &
  Supplement Downloads page, which says it "contains the entire dataset of
  all exclusions in effect", is replaced every month, and that reinstated
  individuals and entities are removed from it.
- The header row is checked exactly as captured (18 columns, ending
  WAIVERDATE,WVRSTATE). OIG's Database Record Layout PDF gives only field
  names and lengths: it defines no exclusion type codes, so EXCLTYPE is
  shown as published and never explained. Dates are 8 characters, shown
  as published (the captured rows are YYYYMMDD); a 0 in REINDATE or
  WAIVERDATE is the file's own empty marker, shown as 0.
- The database date is the file's Last-Modified header as returned (the
  captures show it matching the page's "Last Update"). It is never the
  retrieval time: an answer without Last-Modified is refused.

Matching, the same rule as tools/ofac_sdn_check.py: case folded, every
character that is not a letter or digit a space; exact, or contains as
whole words. A row with a LASTNAME is compared in four forms (first last,
first middle last, last first, last first middle); a BUSNAME is compared
as written. The first 50 matches in file order are listed. No match is not
a clearance. There is no cache: every run reads the file as published.

Failures: a failed download, any status but 200, a redirect off
oig.hhs.gov, no Last-Modified header, or a file whose header row or row
widths are not the captured shape stops the run with exit 2 and no report,
naming the source and the reason. A failure is never "no match".

Standard library only.
"""

import argparse
import csv
import hashlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from ofac_sdn_check import fenced, match_kind, significant  # noqa: E402

LEIE_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
PAGE_URL = "https://oig.hhs.gov/exclusions/leie-database-supplement-downloads/"
LAYOUT_URL = "https://oig.hhs.gov/exclusions/files/leie_record_layout.pdf"
HOST = "oig.hhs.gov"
USER_AGENT = "tiny-ledger-oig-screen"
TIMEOUT_SECONDS = 120
MIN_QUERY_CHARS = 3
MAX_LISTED = 50
HEADER = ("LASTNAME", "FIRSTNAME", "MIDNAME", "BUSNAME", "GENERAL", "SPECIALTY", "UPIN", "NPI", "DOB", "ADDRESS",
          "CITY", "STATE", "ZIP", "EXCLTYPE", "EXCLDATE", "REINDATE", "WAIVERDATE", "WVRSTATE")
# Response headers printed as returned: the ones the coordinator's capture stated (issue #180, Capture B).
SHOWN_HEADERS = ("Content-Type", "Content-Length", "Content-Disposition", "Last-Modified", "ETag")
RULE = ("Names are compared after folding case and replacing every character that is not a letter or digit "
        "with a space. An exact match is the whole normalised query equal to a whole normalised name; a contains "
        "match is the normalised query appearing inside it as whole words. A row with a LASTNAME is compared as "
        "FIRSTNAME LASTNAME, FIRSTNAME MIDNAME LASTNAME, LASTNAME FIRSTNAME and LASTNAME FIRSTNAME MIDNAME; a "
        "BUSNAME is compared as written. No fuzzy or phonetic score is computed or claimed.")
OBSERVATION = ("Observation only: this report records what the HHS OIG LEIE database file contained when read at "
               "the time below. A name match is not a determination that a party is the excluded person or entity, "
               "and no match is not a clearance: the LEIE is matched by name only here, and OIG's own search and "
               "verification are not performed.")


class FetchError(ValueError):
    """A failed or unreadable database file. Never an empty result."""


class Download:
    """The file as read: the requested URL, retrieval time, headers shown, bytes."""

    def __init__(self, url, retrieved, headers, data):
        self.url = url
        self.retrieved = retrieved
        self.headers = headers  # [(name, value)] limited to SHOWN_HEADERS, as returned
        self.data = data

    def header(self, name):
        for k, v in self.headers:
            if k.lower() == name.lower():
                return v
        return None


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url=LEIE_URL):
    """GET the database file. Raises FetchError."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            headers = [(k, v) for k, v in response.headers.items()
                       if k.lower() in {h.lower() for h in SHOWN_HEADERS}]
            data = response.read()
            final_url = response.geturl() or url
    except urllib.error.HTTPError as err:
        err.close()
        raise FetchError("the LEIE database %s answered HTTP %s %s; no report" % (url, err.code, err.reason))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("the LEIE database download %s failed: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("the LEIE database %s answered HTTP %s; no report" % (url, status))
    if urllib.parse.urlsplit(final_url).netloc != HOST:
        raise FetchError("the LEIE database %s was redirected off %s; no report" % (url, HOST))
    return Download(url, retrieved, headers, data)


def decode(download):
    try:
        return download.data.decode("utf-8"), "UTF-8"
    except UnicodeDecodeError:
        return download.data.decode("latin-1"), "Latin-1 (the bytes are not valid UTF-8)"


def rows(download):
    """[(line number, raw line, {column: value})], the line count and the encoding.
    Raises FetchError unless the header row and every row's width are the captured shape."""
    text, encoding = decode(download)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    out, header_seen = [], False
    for number, line in enumerate(lines, 1):
        raw = line[:-1] if line.endswith("\r") else line
        if not raw.strip():
            continue
        fields = next(csv.reader([raw]))
        if not header_seen:
            if tuple(fields) != HEADER:
                raise FetchError("the LEIE database %s does not start with the captured header row (line %d reads "
                                 "%r); no report" % (download.url, number, raw[:200]))
            header_seen = True
            continue
        if len(fields) != len(HEADER):
            raise FetchError("the LEIE database %s line %d has %d fields, not the captured %d; no report"
                             % (download.url, number, len(fields), len(HEADER)))
        out.append((number, raw, dict(zip(HEADER, fields))))
    if not out:
        raise FetchError("the LEIE database %s has no data rows; no report" % download.url)
    return out, len(lines), encoding


def name_forms(row):
    """[(label, name as written)] compared for one row."""
    forms = []
    if row["LASTNAME"].strip():
        first, mid, last = row["FIRSTNAME"], row["MIDNAME"], row["LASTNAME"]
        for label, parts in (("first last", (first, last)), ("first middle last", (first, mid, last)),
                             ("last first", (last, first)), ("last first middle", (last, first, mid))):
            name = " ".join(p.strip() for p in parts if p.strip())
            if name not in [f[1] for f in forms]:
                forms.append((label, name))
    if row["BUSNAME"].strip():
        forms.append(("BUSNAME", row["BUSNAME"].strip()))
    return forms


def best_match(query, row):
    """(kind, form label, name) of the best match on the row, or None."""
    found = [(match_kind(query, name), label, name) for label, name in name_forms(row)]
    found = [f for f in found if f[0]]
    for kind in ("exact", "contains"):
        for f in found:
            if f[0] == kind:
                return f
    return None


def shown_name(row):
    if row["LASTNAME"].strip():
        name = "%s, %s" % (row["LASTNAME"].strip(), " ".join(p for p in (row["FIRSTNAME"].strip(),
                                                                         row["MIDNAME"].strip()) if p))
        return name.rstrip(", ")
    return row["BUSNAME"].strip()


def render(query, download):
    """The report lines for one query. Raises ValueError on a short query, FetchError on the file."""
    if significant(query) < MIN_QUERY_CHARS:
        raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
    db_date = download.header("Last-Modified")
    if not db_date:
        raise FetchError("the LEIE database %s answered with no Last-Modified header, so its database date cannot "
                         "be stated; no report" % download.url)
    data_rows, line_count, encoding = rows(download)
    sha = hashlib.sha256(download.data).hexdigest()
    matches = [(n, raw, row, m) for n, raw, row in data_rows for m in [best_match(query, row)] if m]
    screened = ("Screened: %d data rows of the LEIE database dated %s (the file's Last-Modified header as "
                "returned), file SHA-256 %s." % (len(data_rows), db_date, sha))
    lines = ["# OIG exclusion screen: %s" % query, "", OBSERVATION, "", "## Answer", ""]
    if not matches:
        lines += ["No row of the LEIE database matched %s under the matching rule below. %s No match is not a "
                  "clearance." % (query, screened), ""]
    else:
        exact = sum(1 for m in matches if m[3][0] == "exact")
        lines += ["%d LEIE row%s matched %s: %d with an exact match, %d by contains match only. %s"
                  % (len(matches), "" if len(matches) == 1 else "s", query, exact, len(matches) - exact, screened), ""]
        if len(matches) > MAX_LISTED:
            lines += ["The first %d, in file order, are listed; %d more matched and are not listed."
                      % (MAX_LISTED, len(matches) - MAX_LISTED), ""]
        lines += ["EXCLTYPE codes are shown as published: OIG's Database Record Layout (<%s>) gives field names "
                  "and lengths only and does not define the codes. A 0 in REINDATE or WAIVERDATE is the file's "
                  "own empty marker, as published." % LAYOUT_URL, ""]
        for number, raw, row, (kind, label, name) in matches[:MAX_LISTED]:
            lines += ["### Line %d: %s" % (number, shown_name(row)), "",
                      "- Exclusion type (EXCLTYPE) as published: %s" % row["EXCLTYPE"],
                      "- Exclusion date (EXCLDATE) as published: %s" % row["EXCLDATE"],
                      "- REINDATE as published: %s" % row["REINDATE"],
                      "- WAIVERDATE as published: %s; WVRSTATE as published: %s"
                      % (row["WAIVERDATE"], row["WVRSTATE"] or "(empty)"),
                      "- Row has a LASTNAME: %s" % ("yes" if row["LASTNAME"].strip() else "no (BUSNAME row)"),
                      "- Matched: %s match on %s (%s)" % (kind, name, label), "",
                      "Source: <%s>, line %d of the file as read" % (download.url, number), fenced(raw), ""]
    lines += ["## Matching rule", "", RULE, "",
              "## Database read", "",
              "Exact query: GET %s" % download.url,
              "Sent keyless.",
              "Retrieved (UTC): %s" % download.retrieved,
              "Database date: %s (the file's Last-Modified header as returned; OIG's downloads page, %s, states "
              "its own Last Update date)." % (db_date, PAGE_URL),
              "File as read: %d bytes, SHA-256 %s, %d lines, decoded as %s; %d data rows under the captured header "
              "row." % (len(download.data), sha, line_count, encoding, len(data_rows)), "",
              "Response headers as returned (the ones listed in the tool):",
              fenced("\n".join("%s: %s" % kv for kv in download.headers)), ""]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Screen a person or entity name against the HHS OIG LEIE database.")
    p.add_argument("name", help="a person name or an entity name")
    args = p.parse_args(argv)
    query = " ".join(args.name.split())
    try:
        if significant(query) < MIN_QUERY_CHARS:
            raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
        lines = render(query, (fetcher or fetch)(LEIE_URL))
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
