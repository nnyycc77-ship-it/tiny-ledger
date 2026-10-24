#!/usr/bin/env python3
"""OFAC sanctions list name check (issue #160, tool factory wave 1).

Given a person or company name, reads the US Treasury OFAC Specially
Designated Nationals (SDN) list files live and prints one Markdown report
in the delivery format from AGENT-BRIEF.md: the matching rule, each file
read (exact URL, UTC retrieval time, response headers, bytes, SHA-256,
lines), and every matching list entry with its own lines from the files
printed verbatim beneath it.

    python3 tools/ofac_sdn_check.py "Banco Nacional"

Sources (coordinator captures on issue #160, comments 6378275074 and
6378275367, retrieved 2026-10-24 about 01:36 UTC):

  SDN.CSV  https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV
           primary names; answered with a redirect to a signed storage URL
           that carries a short-lived token, so the redirect target is
           never printed.
  ALT.CSV  https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ALT.CSV
           aliases, a separate file.

What the files' columns are, as far as this repo can ground them: OFAC's
tutorial ("Tutorial on the Use of List-related Legacy Flat Files", quoted
on issue #160) documents that the first column of SDN.CSV is ENT_NUM, the
primary key, and that it links to the ENT_NUM column of ALT.CSV. The
second SDN.CSV column carries the name and the third the type where
present, as every captured line shows. In ALT.CSV the first column is the
linking ENT_NUM and the fourth carries the alias name, as every captured
ALT line shows. The full column specification is a separate OFAC document
not captured here, so no other column is named: each matching entry's
lines are printed whole instead.

Matching rule (approved on issue #160, accent folding added on issue
#251), stated in every report: names are compared after folding case,
removing accents where Unicode decomposition splits them off (é becomes
e; a letter with no such decomposition is still replaced), and replacing
every character that is not a letter or digit with a space. An exact
match is the whole normalised query
equal to the whole normalised name; a contains match is the normalised
query appearing inside the normalised name as whole words. Primary names
and aliases are both checked. No fuzzy or phonetic score is computed or
claimed.

No match is proven by the files themselves as read: each file's byte size,
SHA-256 and line count are printed with the rule, so the check can be
repeated against the same files. The multi-megabyte files are not pasted.

Fail closed: a failed request, a non 200 answer, or a file that is not in
the captured shape stops the run with exit 2 and no report; a failed fetch
is never shown as no match. Observation only: a name match is not a
determination that a party is the listed person or entity, and no match
is not a sanctions clearance.

Standard library only.
"""

import argparse
import csv
import hashlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone

SDN_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
ALT_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ALT.CSV"
USER_AGENT = "tiny-ledger-ofac-sdn-check"
TIMEOUT_SECONDS = 120
MIN_QUERY_CHARS = 3
MAX_LISTED = 50
MAX_OTHER_LINES = 3
# Response headers printed as returned: the ones the coordinator's capture
# showed on the final 200 answer (issue #160, comment 6378275074).
SHOWN_HEADERS = ("Content-Type", "Content-Length", "Content-Disposition", "Last-Modified", "ETag",
                 "x-amz-meta-preview-description", "x-amz-meta-preview-date")
RULE = ("Names are compared after folding case, removing accents where Unicode decomposition splits "
        "them off (é becomes e; a letter with no such decomposition is still replaced), and replacing "
        "every character that is not a letter or digit with a space. An exact match is the whole "
        "normalised query equal to the whole normalised "
        "name; a contains match is the normalised query appearing inside the normalised name as whole "
        "words. Primary names (SDN.CSV) and aliases (ALT.CSV) are both checked. No fuzzy or phonetic score "
        "is computed or claimed.")
OBSERVATION = ("Observation only: this report records what OFAC's published SDN list files contained when "
               "read at the times below. A name match is not a determination that a party is the listed "
               "person or entity, and no match is not a sanctions clearance.")


class FetchError(ValueError):
    """A failed or unreadable source file. Never an empty result."""


class Download:
    """One file as read: the requested URL, retrieval time, headers shown, bytes."""

    def __init__(self, url, retrieved, headers, data, redirected):
        self.url = url
        self.retrieved = retrieved
        self.headers = headers  # [(name, value)] limited to SHOWN_HEADERS, as returned
        self.data = data
        self.redirected = redirected


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """GET a list file, following OFAC's redirect. Raises FetchError."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            headers = [(k, v) for k, v in response.headers.items()
                       if k.lower() in {h.lower() for h in SHOWN_HEADERS}]
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


def fold_accents(text):
    """Accents removed where Unicode decomposition splits them off: the
    decomposed form with its combining marks dropped, so é becomes e and
    ü becomes u. A letter with no such decomposition (for example ł) is
    left as it is, and so still acts as a separator in normalise."""
    return "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c))


def normalise(text):
    """Case and accents folded, every non letter or digit a single space, trimmed."""
    return " ".join(re.sub(r"[^0-9a-z]+", " ", fold_accents(text.casefold())).split())


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


def rows(download, name_column, what):
    """Each entry line as (line number, raw line, fields), plus the other lines.

    An entry line is one whose first field, ENT_NUM, is a whole number and
    that has the name column. A file with more than MAX_OTHER_LINES other
    non blank lines is not the captured shape and is refused.
    """
    text, encoding = decode(download)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    entries, other = [], []
    for number, line in enumerate(lines, 1):
        raw = line[:-1] if line.endswith("\r") else line
        if not raw.strip():
            continue
        fields = next(csv.reader([raw]))
        if fields and fields[0].strip().isdigit() and len(fields) > name_column:
            entries.append((number, raw, fields))
        else:
            other.append((number, raw))
    if not entries or len(other) > MAX_OTHER_LINES:
        raise FetchError("%s is not in the captured shape (%d entry lines, %d other lines); no report"
                         % (what, len(entries), len(other)))
    return entries, other, len(lines), encoding


def file_block(title, download, entries, other, line_count, encoding, unit):
    lines = ["### %s" % title, "",
             "Exact query: GET %s" % download.url]
    if download.redirected:
        lines.append("Answered through a redirect to a signed storage URL, not printed: it carries a "
                     "short-lived token.")
    lines += ["Retrieved (UTC): %s" % download.retrieved,
              "File as read: %d bytes, SHA-256 %s, %d lines, decoded as %s; %d %s (lines whose first field, "
              "ENT_NUM, is a number)." % (len(download.data), hashlib.sha256(download.data).hexdigest(),
                                         line_count, encoding, len(entries), unit), ""]
    if download.headers:
        lines += ["Response headers as returned (the ones listed in the tool):", "```",
                  "\n".join("%s: %s" % kv for kv in download.headers), "```", ""]
    if other:
        lines += ["Other lines in the file, verbatim:", "```",
                  "\n".join("line %d: %s" % o for o in other), "```", ""]
    return lines


def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def render(query, sdn, alt):
    """The report for one query from the two downloads. Raises FetchError."""
    if significant(query) < MIN_QUERY_CHARS:
        raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
    sdn_rows, sdn_other, sdn_lines, sdn_enc = rows(sdn, 1, "SDN.CSV")
    alt_rows, alt_other, alt_lines, alt_enc = rows(alt, 3, "ALT.CSV")
    by_ent = {}
    for number, raw, fields in alt_rows:
        by_ent.setdefault(fields[0].strip(), []).append((number, raw, fields))
    matches = []
    for number, raw, fields in sdn_rows:
        ent = fields[0].strip()
        found = []
        kind = match_kind(query, fields[1])
        if kind:
            found.append((kind, "primary name", fields[1]))
        for _, _, alt_fields in by_ent.get(ent, []):
            akind = match_kind(query, alt_fields[3])
            if akind:
                found.append((akind, "alias", alt_fields[3]))
        if found:
            matches.append((number, raw, fields, found))
    exact = sum(1 for m in matches if any(f[0] == "exact" for f in m[3]))
    lines = ["# OFAC SDN list check: %s" % query, "", OBSERVATION, "",
             "## Matching rule", "", RULE, "", "## Files read", ""]
    lines += file_block("SDN.CSV (primary names)", sdn, sdn_rows, sdn_other, sdn_lines, sdn_enc, "entries")
    lines += file_block("ALT.CSV (aliases)", alt, alt_rows, alt_other, alt_lines, alt_enc, "alias lines")
    lines += ["## Result", ""]
    if not matches:
        lines += ["No primary name or alias matched %s under the rule above. Checked: %d SDN.CSV entries "
                  "(SHA-256 %s) and %d ALT.CSV alias lines (SHA-256 %s), the files exactly as read above."
                  % (query, len(sdn_rows), hashlib.sha256(sdn.data).hexdigest(), len(alt_rows),
                     hashlib.sha256(alt.data).hexdigest()), ""]
        return "\n".join(lines)
    lines += ["%d list entr%s matched %s: %d with an exact match, %d by contains match only."
              % (len(matches), "y" if len(matches) == 1 else "ies", query, exact, len(matches) - exact), ""]
    if len(matches) > MAX_LISTED:
        lines += ["The first %d, in file order, are listed; %d more matched and are not listed."
                  % (MAX_LISTED, len(matches) - MAX_LISTED), ""]
    for number, raw, fields, found in matches[:MAX_LISTED]:
        ent = fields[0].strip()
        lines += ["### ENT_NUM %s: %s" % (ent, fields[1]), "",
                  "- ENT_NUM as shown: %s" % ent,
                  "- Name as shown: %s" % fields[1],
                  "- Type as shown (third column): %s" % (fields[2].strip() if len(fields) > 2 else "not present")]
        lines += ["- Matched: %s match on the %s %s" % (kind, where, name) for kind, where, name in found]
        lines += ["", "Source: <%s>, line %d of the file as read" % (SDN_URL, number), fenced(raw), ""]
        alts = by_ent.get(ent, [])
        if alts:
            lines += ["Source: <%s>, the ALT.CSV lines for ENT_NUM %s" % (ALT_URL, ent),
                      fenced("\n".join(a[1] for a in alts)), ""]
        else:
            lines += ["ALT.CSV has no line for ENT_NUM %s." % ent, ""]
    return "\n".join(lines)


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Check a name against the OFAC SDN list (primary names and aliases).")
    p.add_argument("name", help="person or company name")
    args = p.parse_args(argv)
    fetcher = fetcher or fetch
    try:
        if significant(args.name) < MIN_QUERY_CHARS:
            raise ValueError("the name must have at least %d letters or digits" % MIN_QUERY_CHARS)
        report = render(args.name, fetcher(SDN_URL), fetcher(ALT_URL))
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
