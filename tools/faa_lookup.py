#!/usr/bin/env python3
"""FAA aircraft registry lookup by N number (issue #181, tool factory wave 2).

What aircraft is registered under this tail number, and whose name is on
the registration? Reads the FAA's releasable aircraft database, published
as one keyless ZIP download, and prints one Markdown report in the delivery
format from AGENT-BRIEF.md: the record's own make, model, year and
registrant name, then the matched rows printed whole beneath their source.

    python3 tools/faa_lookup.py N100ZT
    python3 tools/faa_lookup.py N100ZT --refresh

Source (coordinator captures on issue #181, retrieved 2026-10-24 about
06:51 UTC):

  https://registry.faa.gov/database/ReleasableAircraft.zip
      The download page says the archive is refreshed daily at 11:30 pm
      central time and holds comma delimited text files. Two are read:
      MASTER.txt (one row per registered aircraft) and ACFTREF.txt (one row
      per manufacturer, model and series code). Both open with a header row
      naming every column (after a byte order mark); the parser reads those
      header names. The layout document (ardata.pdf) gives what the columns
      mean: N-NUMBER is the number without its leading N, MFR MDL CODE links
      a MASTER row to its ACFTREF row (CODE), YEAR MFR is the year
      manufactured, NAME is the first registrant's name, and ACFTREF's MFR
      and MODEL are the manufacturer name and the model and series name.

Cache. The archive (about 73 MB) is downloaded at most once per UTC day
into a cache folder outside the repo: $TINY_LEDGER_CACHE/faa, or
~/.cache/tiny-ledger/faa. Beside it, a JSON record keeps the URL, the
retrieval time, the status line and headers, the byte count and the
SHA-256. A cached archive whose bytes no longer match that SHA-256 is
downloaded again. --refresh downloads regardless.

Release date. The archive carries no date file. The place the release is
stated is the download's Last-Modified header, so every report states that
value, labelled as the archive Last-Modified, with the retrieval time and
the archive SHA-256.

Matching. The query is upper cased, spaces are removed and one leading N is
dropped; a MASTER row matches when its N-NUMBER, with the file's space
padding trimmed, equals that. The answer names the four values with their
padding trimmed and their column named; the rows themselves are printed
exactly as the file has them.

No match is proven by the file as read: MASTER.txt's byte count, line count
and SHA-256 are printed, with the archive's, so the check can be repeated.

Fail closed. A failed download, a status other than 200 (the captures show
a 302 redirect for a wrong URL and a 403 refusal), an archive that is not a
ZIP, or one without MASTER.txt and ACFTREF.txt in the captured header
shape stops the run with exit 2 and no report. Redirects are never
followed. A failure is never shown as no match.

Standard library only.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_URL = "https://registry.faa.gov/database/ReleasableAircraft.zip"
# The User-Agent this tool sends. The captures on #181 show the host
# refusing a plain curl agent (403) and answering a browser agent; which
# agent to send is pending a coordinator ruling on #181.
USER_AGENT = "tiny-ledger-faa-lookup"
TIMEOUT_SECONDS = 300
CACHE_ENV = "TINY_LEDGER_CACHE"
MASTER, ACFTREF = "MASTER.txt", "ACFTREF.txt"
MASTER_COLUMNS = ("N-NUMBER", "MFR MDL CODE", "YEAR MFR", "NAME")
ACFTREF_COLUMNS = ("CODE", "MFR", "MODEL")
N_PATTERN = re.compile(r"^[0-9A-Z]{1,5}$")


class SourceFailed(Exception):
    """The archive could not be fetched or read. No report is produced."""


# ----------------------------------------------------------------------
# Query
# ----------------------------------------------------------------------

def check_n_number(raw):
    """'n100zt' or 'N 100ZT' -> ('N100ZT', '100ZT'). Raises ValueError."""
    text = "".join(str(raw or "").split()).upper()
    value = text[1:] if text.startswith("N") else text
    if not N_PATTERN.match(value):
        raise ValueError("an N number is up to five letters or digits after the N, e.g. N100ZT, got %r" % raw)
    return "N" + value, value


# ----------------------------------------------------------------------
# Download and cache
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # the redirect answer itself is returned, and fails the status check


def download(url, dest):
    """Stream the URL to dest without following redirects. Returns the
    record kept beside the archive. Raises SourceFailed on anything but a
    200, leaving nothing at dest."""
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    retrieved = utc_now_iso()
    try:
        response = opener.open(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError) as err:
        raise SourceFailed("%s: download failed: %s" % (url, err))
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        if response.status != 200:
            body = response.read(4096).decode("utf-8", "replace")
            raise SourceFailed("%s answered %s; headers: %s; body (first 4096 bytes): %s"
                               % (url, status, "; ".join(headers), body))
        digest, size = hashlib.sha256(), 0
        partial = dest.with_suffix(dest.suffix + ".part")
        partial.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(partial, "wb") as out:
                while True:
                    chunk = response.read(1 << 20)
                    if not chunk:
                        break
                    digest.update(chunk)
                    size += len(chunk)
                    out.write(chunk)
        except OSError as err:
            partial.unlink(missing_ok=True)
            raise SourceFailed("%s: download interrupted after %d bytes: %s" % (url, size, err))
    os.replace(partial, dest)
    return {"url": url, "retrieved_utc": retrieved, "status": status, "headers": headers,
            "last_modified": response.headers.get("Last-Modified"), "bytes": size,
            "sha256": digest.hexdigest()}


def cache_dir():
    base = os.environ.get(CACHE_ENV)
    return (Path(base) if base else Path.home() / ".cache" / "tiny-ledger") / "faa"


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_archive(folder=None, refresh=False, fetch=download, today=None):
    """The cached archive path and its record, downloading when the cache
    is missing, from an earlier UTC day, altered, or refresh is asked."""
    folder = Path(folder) if folder else cache_dir()
    archive, meta_path = folder / "ReleasableAircraft.zip", folder / "ReleasableAircraft.json"
    today = today or utc_now_iso()[:10]
    if not refresh and archive.is_file() and meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except ValueError:
            meta = None
        if meta and meta.get("retrieved_utc", "")[:10] == today and file_sha256(archive) == meta.get("sha256"):
            meta["from_cache"] = True
            return archive, meta
    meta = fetch(ARCHIVE_URL, archive)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    meta["from_cache"] = False
    return archive, meta


# ----------------------------------------------------------------------
# Reading the archive
# ----------------------------------------------------------------------

def _header(line, member, needed):
    names = [n.strip() for n in next(csv.reader([line.decode("utf-8-sig")]))]
    missing = [n for n in needed if n not in names]
    if missing:
        raise SourceFailed("%s in the archive has no column(s) %s in its header row" % (member, ", ".join(missing)))
    return names


def scan(zf, member, needed, key, wanted):
    """Stream one member. Returns (names, matching raw lines, bytes, lines, sha256)."""
    try:
        handle = zf.open(member)
    except KeyError:
        raise SourceFailed("the archive has no %s" % member)
    digest, size, count, names, hits = hashlib.sha256(), 0, 0, None, []
    with handle:
        for line in handle:
            digest.update(line)
            size += len(line)
            count += 1
            if names is None:
                names = _header(line, member, needed)
                index = names.index(key)
                continue
            first = next(csv.reader([line.decode("latin-1")]))
            if len(first) > index and first[index].strip() == wanted:
                hits.append(line)
    if names is None:
        raise SourceFailed("%s in the archive is empty" % member)
    return names, hits, size, count, digest.hexdigest()


def decode_row(raw):
    """A matched line as text, exactly as stored apart from its line end."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return text.rstrip("\r\n")


def lookup(archive, value):
    try:
        zf = zipfile.ZipFile(archive)
    except (zipfile.BadZipFile, OSError) as err:
        raise SourceFailed("the downloaded file is not a readable ZIP archive: %s" % err)
    with zf:
        mnames, mhits, mbytes, mlines, msha = scan(zf, MASTER, MASTER_COLUMNS, "N-NUMBER", value)
        refs = []
        codes = sorted({next(csv.reader([decode_row(h)]))[mnames.index("MFR MDL CODE")].strip() for h in mhits})
        for code in codes:
            anames, ahits, _, _, _ = scan(zf, ACFTREF, ACFTREF_COLUMNS, "CODE", code)
            refs.append((code, anames, ahits))
    return {"master": (mnames, mhits, mbytes, mlines, msha), "refs": refs}


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def _field(names, row, column):
    return row[names.index(column)].strip()


def render(display, value, meta, found):
    mnames, mhits, mbytes, mlines, msha = found["master"]
    lines = ["## Subject: %s" % display, "",
             "Database: FAA releasable aircraft database (Aircraft Registration Master file and Aircraft "
             "Reference file), one ZIP download.", "",
             "QUERY: N-NUMBER = %s (the file stores the number without its leading N). %d matching MASTER.txt "
             "row%s." % (value, len(mhits), "" if len(mhits) == 1 else "s"), "",
             "Archive: %s, archive Last-Modified %s, retrieved %s (UTC)%s, %d bytes, SHA-256 %s. MASTER.txt as "
             "read: %d bytes, %d lines including the header, SHA-256 %s." % (
                 meta["url"], meta.get("last_modified") or "(not stated)", meta["retrieved_utc"],
                 " from the cache" if meta.get("from_cache") else "", meta["bytes"], meta["sha256"],
                 mbytes, mlines, msha), ""]
    if not mhits:
        lines.append("REGISTRATION: no MASTER.txt row carries N-NUMBER %s. The proof is the file as read, "
                     "identified above by its byte count, line count and SHA-256." % value)
        return lines
    refs = {code: (anames, ahits) for code, anames, ahits in found["refs"]}
    for raw in mhits:
        row = next(csv.reader([decode_row(raw)]))
        code = _field(mnames, row, "MFR MDL CODE")
        anames, ahits = refs.get(code, (None, []))
        ref = next(csv.reader([decode_row(ahits[0])])) if ahits else None
        lines.append("REGISTRATION, as the record states it (space padding trimmed):")
        lines.append("- Make (ACFTREF MFR): %s" % (_field(anames, ref, "MFR") if ref else
                                                    "(no ACFTREF.txt row for code %s)" % code))
        lines.append("- Model (ACFTREF MODEL): %s" % (_field(anames, ref, "MODEL") if ref else
                                                      "(no ACFTREF.txt row for code %s)" % code))
        lines.append("- Year (MASTER YEAR MFR): %s" % _field(mnames, row, "YEAR MFR"))
        lines.append("- Registrant name (MASTER NAME): %s" % _field(mnames, row, "NAME"))
        if len(ahits) > 1:
            lines.append("- ACFTREF.txt has %d rows for code %s; the first is used above, all are printed below."
                         % (len(ahits), code))
        lines.append("")
        lines.append("### Source. %s (MASTER.txt row, N-NUMBER %s)" % (meta["url"], value))
        lines.append("Excerpt (the complete raw MASTER.txt row, exactly as the file has it):")
        lines += ["```", decode_row(raw), "```"]
        for ahit in ahits:
            lines.append("### Source. %s (ACFTREF.txt row, CODE %s)" % (meta["url"], code))
            lines.append("Excerpt (the complete raw ACFTREF.txt row, exactly as the file has it):")
            lines += ["```", decode_row(ahit), "```"]
        lines.append("")
    return lines[:-1]


def run(n_number, folder=None, refresh=False, fetch=download):
    display, value = check_n_number(n_number)
    archive, meta = ensure_archive(folder, refresh, fetch)
    return render(display, value, meta, lookup(archive, value))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Look up an N number in the FAA aircraft registry download.")
    parser.add_argument("n_number", help="the N number, e.g. N100ZT")
    parser.add_argument("--cache", help="cache folder (default $%s/faa or ~/.cache/tiny-ledger/faa)" % CACHE_ENV)
    parser.add_argument("--refresh", action="store_true", help="download the archive even if today's is cached")
    args = parser.parse_args(argv)
    try:
        check_n_number(args.n_number)
    except ValueError as err:
        parser.error(str(err))
    try:
        lines = run(args.n_number, args.cache, args.refresh)
    except SourceFailed as err:
        sys.stderr.write("source failure, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
