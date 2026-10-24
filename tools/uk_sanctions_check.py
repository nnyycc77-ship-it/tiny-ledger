#!/usr/bin/env python3
"""UK consolidated sanctions list name check (issue #342, tool factory wave 3, tool 9).

Given a person or company name, reads the UK consolidated list of
financial sanctions targets live, as one keyless CSV file, matches it
locally, and prints one Markdown report in the delivery format from
AGENT-BRIEF.md: the matching rule, the file as read (exact URL, UTC
retrieval time, headers, bytes, SHA-256, records, list date), and every
matching list entry with its own CSV rows printed verbatim beneath it.

    python3 tools/uk_sanctions_check.py "Gazprom Neft"

Source, as ruled and captured by the coordinator on issue #342 (comments
6384611755 and 6384612039, retrieved 2026-10-24 about 13:07 UTC): the GOV.UK
page "Consolidated list of targets"
(https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets/consolidated-list-of-targets)
links the file

    https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv

Its first line is the list date ("Last Updated,<date>", printed as read)
and its second the header row of 36 named columns, as captured. Each
record is one name of one listed group: rows of the same group share the
"Group ID" column, and "Alias Type" says what the row's name is (for
example "Primary name" or "Primary name variation", as captured). The
tool groups rows by Group ID and names no other column's meaning.

Matching rule, the OFAC tool's (tools/ofac_sdn_check.py, issues #160 and
#251), applied to each row's name: names are compared after folding case,
removing accents where Unicode decomposition splits them off, and
replacing every character that is not a letter or digit with a space;
an exact match is the whole normalised query equal to the whole
normalised name, a contains match is the normalised query appearing in
it as whole words. A row's name is formed from the columns Name 1 to
Name 6 in two orders, both checked: the file's own column order (Name 6,
then Name 1 to Name 5) and Name 1 to Name 5 followed by Name 6. The
"Name Non-Latin Script" column is printed with the row but not matched:
under the rule its letters are not a to z and fold to separators.

No match is proven by the file itself as read: its byte size, SHA-256,
physical line count, record count, entry count and list date line are
printed with the rule, so the check can be repeated against the same
bytes. The multi-megabyte file is not pasted.

Fail closed: a failed request, a status other than 200, or a file not in
the captured shape (date line, then the 36 column header, then 36 field
records) stops with exit 2 and no report. A failed fetch is never shown
as no match. Observation only: a name match is not a determination that
a party is the listed person or entity, and no match is not a sanctions
clearance.

Standard library only.
"""

import argparse
import csv
import hashlib
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ofac_sdn_check as ofac  # noqa: E402  (the shared matching rule)

LIST_URL = "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv"
PAGE_URL = ("https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets/"
            "consolidated-list-of-targets")
USER_AGENT = "tiny-ledger-uk-sanctions-check"
TIMEOUT_SECONDS = 120
MIN_QUERY_CHARS = ofac.MIN_QUERY_CHARS
MAX_LISTED = 50
SHOWN_HEADERS = ("Content-Type", "Content-Length", "Last-Modified", "ETag")

# The header row as captured on issue #342 (comment 6384612039), verbatim.
HEADER = ("Name 6", "Name 1", "Name 2", "Name 3", "Name 4", "Name 5", "Title", "Name Non-Latin Script",
          "Non-Latin Script Type", "Non-Latin Script Language", "DOB", "Town of Birth", "Country of Birth",
          "Nationality", "Passport Number", "Passport Details", "National Identification Number",
          "National Identification Details", "Position", "Address 1", "Address 2", "Address 3", "Address 4",
          "Address 5", "Address 6", "Post/Zip Code", "Country", "Other Information", "Group Type",
          "Alias Type", "Alias Quality", "Regime", "Listed On", "UK Sanctions List Date Designated",
          "Last Updated", "Group ID")
COL = {name: i for i, name in enumerate(HEADER)}
NAME_ORDERS = (("Name 6", "Name 1", "Name 2", "Name 3", "Name 4", "Name 5"),
               ("Name 1", "Name 2", "Name 3", "Name 4", "Name 5", "Name 6"))

RULE = ("Names are compared after folding case, removing accents where Unicode decomposition splits them "
        "off, and replacing every character that is not a letter or digit with a space (the OFAC tool's "
        "rule). An exact match is the whole normalised query equal to the whole normalised name; a contains "
        "match is the normalised query appearing inside the normalised name as whole words. Each row's name "
        "is formed from Name 1 to Name 6 in two orders, both checked: the file's column order (Name 6, then "
        "Name 1 to Name 5) and Name 1 to Name 5 followed by Name 6. Primary name and alias rows are both "
        "checked, and rows are grouped into list entries by Group ID. The Name Non-Latin Script column is "
        "not matched. No fuzzy or phonetic score is computed or claimed.")
OBSERVATION = ("Observation only: this report records what the UK consolidated list of financial sanctions "
               "targets contained when read at the time below. A name match is not a determination that a "
               "party is the listed person or entity, and no match is not a sanctions clearance.")


class FetchError(ValueError):
    """A failed or unreadable list file. Never an empty result."""


class Download:
    """The file as read: the requested URL, retrieval time, headers shown, bytes."""

    def __init__(self, url, retrieved, headers, data, redirected):
        self.url = url
        self.retrieved = retrieved
        self.headers = headers
        self.data = data
        self.redirected = redirected


def fetch(url=LIST_URL):
    """GET the list file. Raises FetchError on anything but a 200."""
    retrieved = ofac.utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            wanted = {h.lower() for h in SHOWN_HEADERS}
            headers = [(k, v) for k, v in response.headers.items() if k.lower() in wanted]
            data = response.read()
            redirected = response.geturl() != url
    except urllib.error.HTTPError as err:
        err.close()
        raise FetchError("%s answered HTTP %s %s; no report" % (url, err.code, err.reason))
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed: %s; no report" % (url, err))
    if status != 200:
        raise FetchError("%s answered HTTP %s; no report" % (url, status))
    return Download(url, retrieved, headers, data, redirected)


# ----------------------------------------------------------------------
# Reading the file
# ----------------------------------------------------------------------

class ListFile:
    """The parsed file: list date line, records as (raw text, fields), counts."""

    def __init__(self, date_line, records, physical_lines, encoding):
        self.date_line = date_line
        self.records = records
        self.physical_lines = physical_lines
        self.encoding = encoding


def decode(data):
    try:
        return data.decode("utf-8-sig"), "UTF-8"
    except UnicodeDecodeError:
        return data.decode("latin-1"), "Latin-1 (the bytes are not valid UTF-8)"


def _records(text):
    """Yield (raw text, fields) per CSV record, the raw text exactly as in the file."""
    lines = text.splitlines(keepends=True)
    taken = []

    def feed():
        for line in lines:
            taken.append(line)
            yield line
    for fields in csv.reader(feed()):
        raw = "".join(taken)
        taken.clear()
        yield raw.rstrip("\r\n"), fields


def read_list(download):
    """The parsed list, or FetchError when the file is not in the captured shape."""
    text, encoding = decode(download.data)
    records = list(_records(text))
    if len(records) < 3:
        raise FetchError("%s is not in the captured shape (%d records); no report" % (download.url, len(records)))
    (date_raw, date_fields), (_, header) = records[0], records[1]
    if len(date_fields) != 2 or date_fields[0].strip() != "Last Updated":
        raise FetchError('%s does not open with the "Last Updated" date line; no report' % download.url)
    if tuple(h.strip() for h in header) != HEADER:
        raise FetchError("%s does not carry the captured 36 column header; no report" % download.url)
    data = [(raw, fields) for raw, fields in records[2:] if any(f.strip() for f in fields)]
    bad = [i for i, (_, fields) in enumerate(data) if len(fields) != len(HEADER)]
    if not data or bad:
        raise FetchError("%s is not in the captured shape (%d records, %d without %d fields); no report"
                         % (download.url, len(data), len(bad), len(HEADER)))
    return ListFile(date_raw, data, len(text.splitlines()), encoding)


def row_names(fields):
    """The row's name in each checked order, joined with single spaces (duplicates dropped)."""
    out = []
    for order in NAME_ORDERS:
        name = " ".join(fields[COL[c]].strip() for c in order if fields[COL[c]].strip())
        if name and name not in out:
            out.append(name)
    return out


def match_row(query, fields):
    """(kind, name) for the best form of the row's name that matches, or None."""
    found = [(kind, name) for name in row_names(fields) for kind in [ofac.match_kind(query, name)] if kind]
    if not found:
        return None
    return sorted(found, key=lambda kn: kn[0] != "exact")[0]


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def render(query, download):
    """The report for one query from one download. Raises ValueError on a
    short query and FetchError when the file is not in the captured shape."""
    if ofac.significant(query) < MIN_QUERY_CHARS:
        raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
    listed = read_list(download)
    groups, order = {}, []
    for raw, fields in listed.records:
        gid = fields[COL["Group ID"]].strip()
        if gid not in groups:
            groups[gid] = []
            order.append(gid)
        groups[gid].append((raw, fields))
    types = Counter(fields[COL["Group Type"]].strip() for _, fields in listed.records)
    sha = hashlib.sha256(download.data).hexdigest()
    matches = []
    for gid in order:
        hits = [(raw, fields, m) for raw, fields in groups[gid] for m in [match_row(query, fields)] if m]
        if hits:
            matches.append((gid, hits))

    lines = ["# UK consolidated sanctions list check: %s" % query, "", OBSERVATION, "",
             "## Matching rule", "", RULE, "", "## File read", "",
             "Exact query: GET %s" % download.url]
    if download.redirected:
        lines.append("Answered through a redirect; the final URL is not printed.")
    lines += ["Retrieved (UTC): %s" % download.retrieved,
              "Linked from: %s" % PAGE_URL,
              "List date line, as read (line 1): %s" % listed.date_line,
              "File as read: %d bytes, SHA-256 %s, %d physical lines, decoded as %s; %d records after the "
              "header, in %d list entries (distinct Group ID values)." % (
                  len(download.data), sha, listed.physical_lines, listed.encoding, len(listed.records),
                  len(groups)),
              "Records by Group Type, as read: %s." % ", ".join(
                  "%s %d" % (t or "(empty)", n) for t, n in sorted(types.items())), ""]
    if download.headers:
        lines += ["Response headers as returned (the ones listed in the tool):", "```",
                  "\n".join("%s: %s" % kv for kv in download.headers), "```", ""]
    lines += ["## Result", ""]
    if not matches:
        lines += ["No name matched %s under the rule above. Checked: %d records in %d list entries of the file "
                  "exactly as read above (%d bytes, SHA-256 %s, list date line %s)." % (
                      query, len(listed.records), len(groups), len(download.data), sha, listed.date_line), ""]
        return "\n".join(lines)
    exact = sum(1 for _, hits in matches if any(m[0] == "exact" for _, _, m in hits))
    lines += ["%d list entr%s matched %s: %d with an exact match, %d by contains match only." % (
        len(matches), "y" if len(matches) == 1 else "ies", query, exact, len(matches) - exact), ""]
    if len(matches) > MAX_LISTED:
        lines += ["The first %d, in file order, are listed; %d more matched and are not listed." % (
            MAX_LISTED, len(matches) - MAX_LISTED), ""]
    for gid, hits in matches[:MAX_LISTED]:
        first = groups[gid][0][1]
        lines += ["### Group ID %s: %s, regime %s" % (gid, first[COL["Group Type"]].strip() or "(empty)",
                                                     first[COL["Regime"]].strip() or "(empty)"), ""]
        for raw, fields, (kind, name) in hits:
            lines.append("- %s match on %s (Alias Type as shown: %s)" % (
                kind, name, fields[COL["Alias Type"]].strip() or "(empty)"))
        lines += ["", "All %d record%s of this entry in the file, verbatim:" % (
            len(groups[gid]), "" if len(groups[gid]) == 1 else "s"),
            ofac.fenced("\n".join(raw for raw, _ in groups[gid])), ""]
    return "\n".join(lines)


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = argparse.ArgumentParser(description="Check a name against the UK consolidated list of financial "
                                                 "sanctions targets.")
    parser.add_argument("name", help="person or company name")
    args = parser.parse_args(argv)
    try:
        if ofac.significant(args.name) < MIN_QUERY_CHARS:
            raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
        report = render(args.name, (fetcher or fetch)(LIST_URL))
    except FetchError as err:
        stderr.write("source failure, nothing printed: %s\n" % err)
        return 2
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
