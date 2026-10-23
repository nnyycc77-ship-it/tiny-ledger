#!/usr/bin/env python3
"""Delivery packager: one checked report package per job, timed.

Task: issue #154. For the six report services built on the fetchers in
this folder (recall, carrier, litigation, Form D, nonprofit, awards),
this tool takes a job spec, runs the service's existing fetcher render
functions unchanged, and writes a package directory:

* report.md, the deliverable: a title, the scope and inputs (the buyer
  ask quoted as given), a summary whose every line names the section
  that carries its evidence, one section per source query rendered by
  the fetcher itself (query URL, retrieval time, claims, and the
  complete raw response beneath its source link), and a closing list
  of every source with its retrieval time and where the capture came
  from;
* manifest.json, the record the verification pass checks against: per
  section, every capture's URL, retrieval time, and the SHA-256 of the
  raw response as printed in the section, and every count the section
  states, with the rule that recounts it from that raw response; plus
  the SHA-256 of report.md itself.

Verification (`verify`, and run automatically after `package`) fails
the package when:

* a section carries claims without a source: no capture recorded for
  it, or a capture whose URL, retrieval time, or complete raw response
  is missing from the section;
* a summary line names no section, names a section that does not exist,
  or states a value the named section does not record;
* a count the section states differs from the count recorded in the
  manifest, or from the fetcher parser's own recount of the raw
  response printed in the section;
* the deliverable hash is missing from the manifest or does not match
  report.md, or (with --timing-log) is not recorded in the timing log.

Timing: every `package` run appends one JSON line to the timing log,
with the seconds spent fetching (live) or loading recorded captures
(replay), assembling, and verifying, the total in minutes, the mode,
the deliverable hash, and the verification result. The log records
time only; it has no price field.

Two modes:

* live (the default): the fetchers' own fetch functions make the
  requests. Form D needs EDGAR_CONTACT (the fair access contact) and
  litigation reads COURTLISTENER_TOKEN if set, both from the
  environment only, as the fetchers already do.
* replay (--replay BUNDLE): every request is answered from a capture
  bundle that points at captures already committed in this repo (a
  fixture file, a live snapshot, or a published transcript), each
  checked against its recorded SHA-256 or rebuilt byte for byte before
  use. A request the bundle does not hold fails the run; nothing is
  ever fetched in replay mode.

Usage:

    python3 tools/delivery_packager.py package \\
        --job tools/delivery-packager/jobs/recall.json \\
        --replay tools/delivery-packager/bundles/recall.json \\
        --out /tmp/recall-package --timing-log /tmp/timing.jsonl
    python3 tools/delivery_packager.py verify --dir /tmp/recall-package

Standard library only. Exit codes: 0 package written and verified,
1 package written but verification failed, 2 nothing written (bad job,
fetch failure, or a request outside the replay bundle).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import courtlistener_recap as cl  # noqa: E402
import cpsc_recalls as cpsc  # noqa: E402
import edgar_formd as ef  # noqa: E402
import fmcsa_carrier as fc  # noqa: E402
import propublica_nonprofits as pp  # noqa: E402
import usaspending_awards as ua  # noqa: E402

TOOL = "tools/delivery_packager.py"
FORMAT = "tiny-ledger delivery package"

SERVICES = {
    "recall": "Product recall check (CPSC Recalls API)",
    "carrier": "Carrier vetting (FMCSA Company Census File, SAFER, Licensing and Insurance)",
    "litigation": "Federal litigation screen (CourtListener RECAP docket search)",
    "formd": "Form D private offering check (SEC EDGAR)",
    "nonprofit": "Nonprofit check (ProPublica Nonprofit Explorer API v2)",
    "awards": "Federal awards check (USAspending prime contract awards)",
}

SECTION_RE = re.compile(r"^## Section (S\d+): (.+)$")
EXCLUDED_HEADING = "## Package checked and excluded"
END_HEADING = "## Package sources"
SUMMARY_HEADING = "## Summary"
SUMMARY_LINE_RE = re.compile(r"^- (.+): (.+?)\. \(Section (S\d+)\)$")
FENCE_RE = re.compile(r"^`{3,}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class PackageError(Exception):
    """A job that cannot be packaged. Nothing is written."""


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


# ----------------------------------------------------------------------
# Transcripts
# ----------------------------------------------------------------------

def split_transcript(transcript):
    """(status line, header lines, body) of a transcript joined with "\\n"
    (status line, headers, a blank line, the body). Refuses a transcript
    that does not rebuild byte for byte from its parts."""
    lines = transcript.split("\n")
    try:
        blank = lines.index("")
    except ValueError:
        raise PackageError("transcript has no blank line after its headers")
    status_line, headers, body = lines[0], lines[1:blank], "\n".join(lines[blank + 1:])
    if "\n".join([status_line] + headers + ["", body]) != transcript:
        raise PackageError("transcript does not rebuild from its parts")
    return status_line, headers, body


def fence_blocks(lines):
    """Inner text of every fenced block in a list of lines. A block opens
    on a line of three or more backticks and closes on the same line."""
    blocks, i = [], 0
    while i < len(lines):
        if FENCE_RE.match(lines[i]):
            fence, inner, j = lines[i], [], i + 1
            while j < len(lines) and lines[j] != fence:
                inner.append(lines[j])
                j += 1
            if j < len(lines):
                blocks.append("\n".join(inner))
            i = j + 1
        else:
            i += 1
    return blocks


def outside_fences(lines):
    """The lines that are not inside a fenced block."""
    out, fence = [], None
    for line in lines:
        if fence is None and FENCE_RE.match(line):
            fence = line
        elif fence is not None and line == fence:
            fence = None
        elif fence is None:
            out.append(line)
    return out


def evidence_in(blocks, evidence):
    """The printed block holding this evidence, or None. The fetchers
    print the evidence with one newline before the closing fence, so a
    trailing newline of the evidence is not a separate line."""
    for block in blocks:
        if block == evidence or block + "\n" == evidence:
            return block
    return None


# ----------------------------------------------------------------------
# Sources: live fetch or replay of committed captures
# ----------------------------------------------------------------------

def _evidence(kind, cap):
    """The text a fetcher prints beneath the source link for a capture."""
    if kind in ("cpsc",):
        return cap.raw
    if kind == "usaspending":
        return cap.raw
    if kind == "propublica":
        return pp.transcript(cap)
    return cap.transcript


def _capture_from_transcript(kind, url, retrieved, transcript, request=None):
    if kind == "cpsc":
        return cpsc.Capture(url, retrieved, transcript)
    if kind == "usaspending":
        return ua.Capture(request, retrieved, transcript)
    if kind == "edgar":
        return ef.Capture(url, retrieved, transcript, transcript.partition("\n\n")[2])
    status_line, headers, body = split_transcript(transcript)
    if kind == "fmcsa":
        return fc.Capture(url, retrieved, status_line, headers, body, "utf-8")
    if kind == "courtlistener":
        return cl.Capture(url, retrieved, status_line, headers, body)
    if kind == "propublica":
        return pp.Capture(url, retrieved, status_line, int(status_line.split(" ", 2)[1]), headers, body)
    raise PackageError("unknown capture kind %r" % kind)


class Source(object):
    """Serves captures to the adapters and keeps the served list, in
    order, with the time spent obtaining them."""

    mode = None

    def __init__(self):
        self.served = []
        self.seconds = 0.0

    def get(self, kind, key):
        start = time.monotonic()
        try:
            got = self._obtain(kind, key)
        finally:
            self.seconds += time.monotonic() - start
        cap, origin, note = got if len(got) == 3 else (got[0], got[1], None)
        url = ua.ENDPOINT if kind == "usaspending" else cap.url
        self.served.append({"kind": kind, "url": url, "request": key if kind == "usaspending" else None,
                            "retrieved_utc": cap.retrieved, "origin": origin, "note": note,
                            "evidence": _evidence(kind, cap)})
        return cap

    def mark(self):
        return len(self.served)


class LiveSource(Source):
    mode = "live"

    def __init__(self, env=None):
        Source.__init__(self)
        self.env = os.environ if env is None else env

    def _obtain(self, kind, key):
        origin = "live request made by this run"
        if kind == "cpsc":
            return cpsc.fetch_url(key), origin
        if kind == "fmcsa":
            return fc.fetch(key), origin
        if kind == "courtlistener":
            return cl.fetch(key, self.env.get(cl.TOKEN_ENV) or None), origin
        if kind == "edgar":
            return ef.fetch(key, ef.contact_from(None, self.env)), origin
        if kind == "propublica":
            return pp.fetch(key), origin
        if kind == "usaspending":
            return ua.fetch(key), origin
        raise PackageError("unknown capture kind %r" % kind)


class ReplaySource(Source):
    """Answers requests from a capture bundle. Each bundle entry names a
    capture committed in this repo; the loader checks it against its
    recorded SHA-256, or rebuilds it byte for byte, before serving it."""

    mode = "replay"

    def __init__(self, bundle_path):
        Source.__init__(self)
        self.bundle_path = Path(bundle_path)
        try:
            bundle = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            raise PackageError("cannot read the capture bundle %s: %s" % (bundle_path, err))
        self.entries = {}
        for entry in bundle.get("captures", []):
            key = (entry["kind"], entry.get("request") if entry["kind"] == "usaspending" else entry["url"])
            if key in self.entries:
                raise PackageError("capture bundle lists %r twice" % (key,))
            self.entries[key] = entry

    def _obtain(self, kind, key):
        entry = self.entries.get((kind, key))
        if entry is None:
            raise PackageError("replay: the request %s is not in the capture bundle %s; nothing is fetched "
                               "in replay mode" % (key, rel(self.bundle_path)))
        url, retrieved, transcript, origin = load_origin(entry)
        note = None
        if entry["origin"]["type"] == "body_only_fixture":
            note = ("the response body below is the capture, byte for byte; the status line above it is built "
                    "from the capturer's stated HTTP 200, and no headers were captured")
        return _capture_from_transcript(kind, url, retrieved, transcript, entry.get("request")), origin, note


def _repo_path(path):
    p = (ROOT / path).resolve()
    if ROOT not in p.parents:
        raise PackageError("capture origin %s is outside the repository" % path)
    return p


def load_origin(entry):
    """(url, retrieved, transcript, origin text) for one bundle entry."""
    o = entry["origin"]
    kind = o["type"]
    if kind == "standing_watch_snapshot":
        snap = json.loads(_repo_path(o["file"]).read_text(encoding="utf-8"))
        r = snap["entries"][o["entry"]]["responses"][o["index"]]
        if r["url"] != entry["url"]:
            raise PackageError("snapshot response %s[%d] is for %s, not %s" % (o["entry"], o["index"], r["url"], entry["url"]))
        if sha256_text(r["raw"]) != r["sha256"]:
            raise PackageError("snapshot response %s[%d] does not match its recorded SHA-256" % (o["entry"], o["index"]))
        return r["url"], r["retrieved_utc"], r["raw"], "replayed from %s, entry %s, response %d (live run %s; SHA-256 %s as recorded)" % (
            o["file"], o["entry"], o["index"], snap["run_utc"], r["sha256"])
    if kind == "http_fixture":
        path = _repo_path(o["file"])
        prov = json.loads((path.parent / "provenance.json").read_text(encoding="utf-8"))[path.name]
        if prov["url"] != entry["url"]:
            raise PackageError("%s is recorded for %s, not %s" % (o["file"], prov["url"], entry["url"]))
        if sha256_file(path) != prov["sha256"]:
            raise PackageError("%s does not match the SHA-256 in its provenance.json" % o["file"])
        return prov["url"], prov["retrieved_utc"], path.read_bytes().decode("utf-8"), \
            "replayed from %s (SHA-256 %s, as recorded in its provenance.json)" % (o["file"], prov["sha256"])
    if kind == "usaspending_fixture":
        body_path, meta_path = _repo_path(o["body"]), _repo_path(o["meta"])
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta["request_body"] != entry["request"]:
            raise PackageError("%s records a different request body" % o["meta"])
        raw = body_path.read_bytes().decode("utf-8")
        return ua.ENDPOINT, meta["retrieved_utc"], raw, \
            "replayed from %s with the request and retrieval time in %s (SHA-256 %s)" % (o["body"], o["meta"], sha256_text(raw))
    if kind == "body_only_fixture":
        path = _repo_path(o["file"])
        prov = json.loads((path.parent / "provenance.json").read_text(encoding="utf-8"))[path.name]
        if prov["url"] != entry["url"]:
            raise PackageError("%s is recorded for %s, not %s" % (o["file"], prov["url"], entry["url"]))
        if sha256_file(path) != prov["sha256"]:
            raise PackageError("%s does not match the SHA-256 in its provenance.json" % o["file"])
        body = path.read_bytes().decode("utf-8")
        return prov["url"], prov["retrieved_utc"], prov["status_line_for_replay"] + "\n\n" + body, \
            ("replayed from %s, response body only (SHA-256 %s, as recorded in its provenance.json; captured by "
             "%s, posted at %s); the status line is built from the stated HTTP %s and no headers were captured"
             % (o["file"], prov["sha256"], prov["captured_by"].split(";")[0], prov["posted_at"], prov["http_status"]))
    if kind == "published_transcript":
        return _published_transcript(entry["url"], o["file"])
    raise PackageError("unknown capture origin type %r" % kind)


def _published_transcript(url, path):
    """A complete transcript printed by a fetcher in a committed report:
    the QUERY line with this URL, its Retrieved line, then the source
    link and the fenced transcript. The transcript is rebuilt from the
    fence exactly as printed."""
    lines = _repo_path(path).read_text(encoding="utf-8").split("\n")
    query = "QUERY: GET %s" % url
    starts = [i for i, line in enumerate(lines) if line == query]
    if len(starts) != 1:
        raise PackageError("%s holds %d QUERY lines for %s, not exactly one" % (path, len(starts), url))
    i = starts[0]
    m = re.match(r"^Retrieved \(UTC\): (\S+)$", lines[i + 1]) if i + 1 < len(lines) else None
    if not m:
        raise PackageError("%s: no Retrieved line under the QUERY line for %s" % (path, url))
    retrieved = m.group(1)
    try:
        j = lines.index("Source: <%s>" % url, i)
    except ValueError:
        raise PackageError("%s: no source link for %s" % (path, url))
    if j + 1 >= len(lines) or not FENCE_RE.match(lines[j + 1]):
        raise PackageError("%s: no fenced transcript under the source link for %s" % (path, url))
    fence = lines[j + 1]
    try:
        k = lines.index(fence, j + 2)
    except ValueError:
        raise PackageError("%s: the transcript fence for %s is not closed" % (path, url))
    transcript = "\n".join(lines[j + 2:k])
    return url, retrieved, transcript, "replayed from the transcript printed in %s (lines %d to %d; SHA-256 %s)" % (
        path, j + 3, k, sha256_text(transcript))


# ----------------------------------------------------------------------
# Count rules: what a section states, recounted from its raw response
# ----------------------------------------------------------------------

def _body(evidence):
    return split_transcript(evidence)[2]


def _recount_cpsc(url, evidence):
    return str(len(cpsc.records(cpsc.Capture(url, "", evidence))))


def _recount_census(url, evidence):
    return str(len(fc.parse_census(_body(evidence))))


def _recount_safer(url, evidence):
    found = fc.labelled_values(fc.text_lines(_body(evidence)), fc.SAFER_LABELS,
                               fc.SAFER_MULTILINE, fc.SAFER_STOP_PREFIXES)
    return str(sum(1 for v in found.values() if v is not None))


def _recount_li(url, evidence):
    return str(len([line for line in fc.text_lines(_body(evidence)) if line.startswith(fc.LI_PREFIXES)]))


def _recount_cl_count(url, evidence):
    return json.dumps(cl.parse_search(_body(evidence))["count"])


def _recount_edgar(url, evidence):
    return str(len(ef.form_d_filings(ef.parse_submissions(evidence.partition("\n\n")[2])[2])))


def _pp_capture(url, evidence):
    status_line, headers, body = split_transcript(evidence)
    return pp.Capture(url, "", status_line, 200, headers, body)


def _recount_pp_orgs(url, evidence):
    return str(len(pp.search_results(_pp_capture(url, evidence), {})[1]))


def _recount_pp_filings(url, evidence):
    return str(len(pp.root(_pp_capture(url, evidence)).children("filings_with_data")))


def _recount_usa(url, evidence):
    return str(len(json.loads(evidence)["results"]))


RULES = {
    "cpsc_records": (re.compile(r"^CPSC returned (\d+) record\(s\) for this query\.$"), _recount_cpsc),
    "census_records": (re.compile(r"^QUERY: dot_number = \d+ returned (\d+) records? \(retrieved "), _recount_census),
    "safer_fields": (re.compile(r"\)\. (\d+) of \d+ labelled fields were found in the page text\."), _recount_safer),
    "li_lines": (re.compile(r"\)\. (\d+) record text lines? found\.$"), _recount_li),
    "cl_window_count": (re.compile(r"^- Total count found in the window \(first variant's party search, "
                                   r"as returned by the API\): (.+)\.$"), _recount_cl_count),
    "edgar_formd": (re.compile(r"^EDGAR lists (\d+) Form D filings \(form D or D/A\) among the "), _recount_edgar),
    "pp_orgs": (re.compile(r"\. Organizations on this page: (\d+)\. "), _recount_pp_orgs),
    "pp_filings": (re.compile(r"^Figures, from the filings_with_data entry with the highest tax_prd "
                              r"\(\d+ of (\d+) entries\)\."), _recount_pp_filings),
    "usa_records": (re.compile(r"^USAspending returned (\d+) record\(s\) on requested page \d+\.$"), _recount_usa),
}


def stated(rule, lines):
    pattern = RULES[rule][0]
    found = [m.group(1) for m in (pattern.search(line) for line in lines) if m]
    return found


# ----------------------------------------------------------------------
# Service adapters: the fetchers' own renderers, one section per query
# ----------------------------------------------------------------------

class Section(object):
    def __init__(self, title, lines, captures, counts):
        self.title = title
        self.lines = lines
        self.captures = captures
        self.counts = counts  # [(rule, capture url, label)]


def _need(inputs, key, kind=str):
    value = inputs.get(key)
    if not isinstance(value, kind) or (kind is str and not value.strip()):
        raise PackageError("job inputs need %r (%s)" % (key, kind.__name__))
    return value


def _section(src, mark, title, lines, counts):
    # Some renderers return list items that hold several lines; flatten so
    # every item is one line of the report. A capture whose transcript is
    # not wholly a recording carries a note, printed first.
    served = src.served[mark:]
    notes = ["Note on the raw response for %s: %s." % (c["url"], c["note"]) for c in served if c.get("note")]
    head = notes + [""] if notes else []
    return Section(title, head + "\n".join(lines).split("\n"), served, counts)


def adapt_recall(inputs, src):
    queries = _need(inputs, "queries", list)
    exact = inputs.get("exact_name")
    sections = []
    for q in queries:
        field, value, near = q.get("field", "ProductName"), q.get("value"), bool(q.get("near"))
        if field not in cpsc.FIELD_HEADINGS or not isinstance(value, str) or not value.strip():
            raise PackageError("recall: each query needs a field in %s and a value" % sorted(cpsc.FIELD_HEADINGS))
        if near and not exact:
            raise PackageError("recall: a near-match query needs exact_name to state the exclusion rule")
        mark = src.mark()
        cap = src.get("cpsc", cpsc.query_url(value, field))
        text = cpsc.render_query(cap, exact, near=near)
        sections.append(_section(src, mark, 'CPSC %s query "%s"' % (field, value), text.rstrip("\n").split("\n"),
                                 [("cpsc_records", cap.url, 'CPSC records returned for the %s query "%s"' % (field, value))]))
    return sections


def adapt_carrier(inputs, src):
    usdot = fc.check_usdot(_need(inputs, "usdot"))
    sources = inputs.get("sources") or list(fc.ALL_SOURCES)
    if any(s not in fc.ALL_SOURCES for s in sources):
        raise PackageError("carrier: sources must be among %s" % (fc.ALL_SOURCES,))
    plan = {
        "census": (fc.census_record_url, fc.census_section, "FMCSA Company Census File record, USDOT %s",
                   "census_records", "FMCSA Census File records returned for USDOT %s"),
        "safer": (fc.safer_url, fc.safer_section, "FMCSA SAFER Company Snapshot, USDOT %s",
                  "safer_fields", "SAFER labelled fields found in the page text for USDOT %s"),
        "li": (fc.li_url, fc.li_section, "FMCSA Licensing and Insurance, USDOT %s",
               "li_lines", "Licensing and Insurance record text lines found for USDOT %s"),
    }
    sections = []
    for s in sources:
        url_of, render, title, rule, label = plan[s]
        mark = src.mark()
        cap = src.get("fmcsa", url_of(usdot))
        lines = render(usdot, cap)
        counts = [(rule, cap.url, label % usdot)] if stated(rule, lines) else []
        sections.append(_section(src, mark, title % usdot, lines, counts))
    return sections


def adapt_litigation(inputs, src):
    parties = _need(inputs, "parties", list)
    variants = []
    for v in parties:
        cl.party_query(v)
        if v not in variants:
            variants.append(v)
    filed_after = cl.check_date(_need(inputs, "filed_after"))
    order_by = inputs.get("order_by", cl.DEFAULT_ORDER)
    list_count = inputs.get("list", 10)
    exclusions = dict(inputs.get("exclusions") or {})
    subject = inputs.get("subject_name") or variants[0]
    mark = src.mark()
    searches = []
    for i, variant in enumerate(variants):
        label = cl.LABELS[i] if i < len(cl.LABELS) else "variant %d" % (i + 1)
        searches.append((variant, label, src.get("courtlistener", cl.search_url(variant, filed_after, order_by))))
    docket_captures = None
    if inputs.get("docket_details"):
        docket_captures = []
        first = searches[0][2]
        if first.status_ok:
            try:
                results = cl.parse_search(first.body)["results"][:list_count]
            except ValueError:
                results = []
            for record in results:
                docket_id = record.get("docket_id")
                if docket_id is not None and str(docket_id).isdigit():
                    docket_captures.append((str(docket_id), src.get("courtlistener", cl.docket_url(docket_id))))
    lines = cl.render_section(subject, variants, filed_after, order_by, searches, list_count, exclusions, docket_captures)
    counts = []
    if stated("cl_window_count", lines):
        counts.append(("cl_window_count", searches[0][2].url,
                       'CourtListener result count in the window for party "%s"' % variants[0]))
    return [_section(src, mark, 'CourtListener RECAP docket search, party "%s"' % variants[0], lines, counts)]


def adapt_formd(inputs, src):
    cik, issuer = inputs.get("cik"), inputs.get("issuer")
    if bool(cik) == bool(issuer):
        raise PackageError("formd: give exactly one of cik or issuer")
    if cik:
        cik = str(cik)
        ef.cik10(cik)
    mark = src.mark()
    lines = ef.run(None, cik=cik, issuer=issuer, max_filings=inputs.get("max_filings", 10),
                   exclusions=inputs.get("exclusions"), fetcher=lambda url, contact: src.get("edgar", url))
    served = src.served[mark:]
    subs = [c["url"] for c in served if "/submissions/CIK" in c["url"]]
    counts = [("edgar_formd", subs[0], "Form D filings (D or D/A) listed in the EDGAR submissions index's recent window")] \
        if subs and stated("edgar_formd", lines) else []
    return [_section(src, mark, "SEC EDGAR Form D filings, %s" % (issuer or "CIK %s" % cik), lines, counts)]


def adapt_nonprofit(inputs, src):
    name = inputs.get("name")
    eins = []
    for e in inputs.get("eins") or []:
        n = pp.normalize_ein(e)
        if n not in eins:
            eins.append(n)
    excluded = pp.exclusions(["%s=%s" % (k, v) for k, v in (inputs.get("exclusions") or {}).items()])
    if not name and not eins:
        raise PackageError("nonprofit: give name, eins, or both")
    sections, examined = [], list(eins)
    if name:
        mark = src.mark()
        search = src.get("propublica", pp.search_url(name))
        found = pp.search_results(search, excluded)[2]
        for ein in pp.exact_name_matches(found, name):
            if ein not in examined and ein not in excluded:
                examined.append(ein)
        lines = pp.render_search(search, name, examined, excluded)
        if not examined:
            lines += ["No search result's name equals the search text exactly and no EIN was given, so no "
                      "organization record was fetched.", ""]
        sections.append(_section(src, mark, 'ProPublica Nonprofit Explorer search "%s"' % name, lines,
                                 [("pp_orgs", search.url, 'Organizations on the search page for "%s"' % name)]))
    for ein in examined:
        mark = src.mark()
        cap = src.get("propublica", pp.organization_url(ein))
        lines = pp.render_organization(cap, "Organization: EIN %s" % ein)
        counts = [("pp_filings", cap.url, "filings_with_data entries for EIN %s" % ein)] \
            if stated("pp_filings", lines) else []
        sections.append(_section(src, mark, "ProPublica Nonprofit Explorer organization, EIN %s" % ein, lines, counts))
    return sections


def adapt_awards(inputs, src):
    args = SimpleNamespace(recipient=inputs.get("recipient"), naics=inputs.get("naics") or [],
                           start=inputs.get("start"), end=inputs.get("end"),
                           page=inputs.get("page", 1), limit=inputs.get("limit", 10))
    query = ua.build_query(args)
    excluded = dict(inputs.get("exclusions") or {})
    mark = src.mark()
    cap = src.get("usaspending", query)
    text = ua.render(cap, excluded)
    return [_section(src, mark, "USAspending prime contract awards, %s" % (args.recipient or ", ".join(args.naics)),
                     text.rstrip("\n").split("\n"),
                     [("usa_records", ua.ENDPOINT, "USAspending awards returned on requested page %d" % args.page)])]


ADAPTERS = {
    "recall": adapt_recall,
    "carrier": adapt_carrier,
    "litigation": adapt_litigation,
    "formd": adapt_formd,
    "nonprofit": adapt_nonprofit,
    "awards": adapt_awards,
}


# ----------------------------------------------------------------------
# Packaging
# ----------------------------------------------------------------------

def load_job(path):
    try:
        job = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise PackageError("cannot read the job spec %s: %s" % (path, err))
    if not isinstance(job, dict):
        raise PackageError("the job spec must be a JSON object")
    if job.get("service") not in SERVICES:
        raise PackageError("service must be one of %s" % ", ".join(SERVICES))
    for key in ("subject", "buyer_ask"):
        if not isinstance(job.get(key), str) or not job[key].strip():
            raise PackageError("the job spec needs a non-blank %r" % key)
    if not isinstance(job.get("inputs"), dict):
        raise PackageError("the job spec needs an inputs object")
    return job


def _value_for(rule, capture_url, section):
    """The count a section states for a rule, checked against the
    fetcher parser's recount of the printed raw response."""
    found = stated(rule, section.lines)
    if len(found) != 1:
        raise PackageError("section %r states %d values for rule %s, not exactly one" % (section.title, len(found), rule))
    cap = [c for c in section.captures if c["url"] == capture_url]
    recount = RULES[rule][1](capture_url, cap[0]["evidence"])
    if recount != found[0]:
        raise PackageError("section %r states %s for rule %s but the raw response recounts to %s"
                           % (section.title, found[0], rule, recount))
    return found[0]


def build(job, src, packaged_utc):
    """(report text, manifest dict) for a job. Raises PackageError or the
    fetcher's own errors; nothing is written by this function."""
    sections = ADAPTERS[job["service"]](job["inputs"], src)
    if not sections:
        raise PackageError("the job produced no sections")
    ids = ["S%d" % (i + 1) for i in range(len(sections))]
    summary, msections = [], []
    for sid, sec in zip(ids, sections):
        blocks = fence_blocks(sec.lines)
        caps = []
        for c in sec.captures:
            if evidence_in(blocks, c["evidence"]) is None:
                raise PackageError("section %r does not print the complete raw response for %s" % (sec.title, c["url"]))
            caps.append({"url": c["url"], "request": c["request"], "retrieved_utc": c["retrieved_utc"],
                         "evidence_sha256": sha256_text(evidence_in(blocks, c["evidence"])),
                         "origin": c["origin"]})
        counts = []
        for rule, url, label in sec.counts:
            value = _value_for(rule, url, sec)
            counts.append({"rule": rule, "capture_url": url, "label": label, "value": value})
            summary.append("- %s: %s. (Section %s)" % (label, value, sid))
        msections.append({"id": sid, "title": sec.title, "captures": caps, "counts": counts})

    inputs_json = json.dumps(job["inputs"], ensure_ascii=False, sort_keys=True)
    mode_line = ("replay of captures already committed in this repository; no request was made for this package"
                 if src.mode == "replay" else "live requests made by this run")
    out = ["# %s: %s" % (SERVICES[job["service"]], job["subject"]), "",
           "Produced by `%s`. Every claim below sits under its source link with the complete raw "
           "response printed beneath it, and every summary line names the section that carries its "
           "evidence. Values are as the sources returned them at the stated retrieval times." % TOOL, "",
           "## Scope and inputs", "",
           "- Service: %s" % SERVICES[job["service"]],
           "- Subject: %s" % job["subject"],
           "- Buyer ask, as given: %s" % job["buyer_ask"],
           "- Inputs: `%s`" % inputs_json,
           "- Sources: %s" % mode_line,
           "- Packaged (UTC): %s" % packaged_utc,
           "- Scope: only the queries listed in the sections below, as each source answered them. A "
           "section that finds nothing is a search observation, not a clearance.", "",
           SUMMARY_HEADING, ""]
    out += summary if summary else ["- No count is stated by any section; read the sections below."]
    out.append("")
    for sid, sec in zip(ids, sections):
        out += ["## Section %s: %s" % (sid, sec.title), ""] + sec.lines + [""]
    out += [EXCLUDED_HEADING, ""]
    excluded = ["- Section %s: %s" % (sid, line.lstrip("-# ").strip())
                for sid, sec in zip(ids, sections) for line in outside_fences(sec.lines)
                if re.search(r"(?i)checked and excluded", line)]
    out += excluded or ["- None: no result in any section was set aside as a near match for this job."]
    out += ["", END_HEADING, ""]
    for m in msections:
        for c in m["captures"]:
            out.append("- %s: %s, retrieved %s; %s." % (m["id"], c["url"], c["retrieved_utc"], c["origin"]))
    report = "\n".join(out).rstrip("\n") + "\n"
    manifest = {"format": FORMAT, "version": 1, "tool": TOOL, "service": job["service"],
                "subject": job["subject"], "buyer_ask": job["buyer_ask"], "inputs": job["inputs"],
                "mode": src.mode, "packaged_utc": packaged_utc, "report_file": "report.md",
                "deliverable_sha256": sha256_text(report), "sections": msections}
    return report, manifest


# ----------------------------------------------------------------------
# Verification
# ----------------------------------------------------------------------

def split_report(text):
    """(summary lines, {section id: (title, lines)}, section order)."""
    lines = text.split("\n")
    summary, sections, order = [], {}, []
    current, in_summary = None, False
    for line in lines:
        m = SECTION_RE.match(line)
        if line == SUMMARY_HEADING:
            in_summary, current = True, None
            continue
        if m:
            in_summary = False
            current = m.group(1)
            if current in sections:
                sections[current] = (sections[current][0], sections[current][1] + ["(duplicate heading)"])
            else:
                sections[current] = (m.group(2), [])
                order.append(current)
            continue
        if line in (EXCLUDED_HEADING, END_HEADING):
            in_summary, current = False, None
            continue
        if in_summary:
            if line.startswith("## "):
                in_summary = False
            elif line.strip():
                summary.append(line)
        elif current:
            sections[current][1].append(line)
    return summary, sections, order


def verify(package_dir, timing_log=None):
    """Failures of a written package, as strings; an empty list is PASS."""
    package_dir = Path(package_dir)
    failures = []
    try:
        manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        return ["manifest.json cannot be read: %s" % err]
    report_file = manifest.get("report_file", "report.md")
    if not isinstance(report_file, str) or Path(report_file).name != report_file:
        return ["manifest report_file must be a file name inside the package, got %r" % (report_file,)]
    report_path = package_dir / report_file
    try:
        report_bytes = report_path.read_bytes()
        text = report_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as err:
        return ["the report cannot be read: %s" % err]

    recorded = manifest.get("deliverable_sha256")
    if not isinstance(recorded, str) or not HEX64.match(recorded):
        failures.append("deliverable hash not recorded in the manifest")
    elif hashlib.sha256(report_bytes).hexdigest() != recorded:
        failures.append("deliverable hash does not match the report: manifest %s, report %s"
                        % (recorded, hashlib.sha256(report_bytes).hexdigest()))
    if timing_log is not None and isinstance(recorded, str):
        try:
            logged = [json.loads(line) for line in Path(timing_log).read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, ValueError) as err:
            logged = []
            failures.append("timing log cannot be read: %s" % err)
        if not any(entry.get("deliverable_sha256") == recorded for entry in logged):
            failures.append("deliverable hash not recorded in the timing log %s" % timing_log)

    summary, sections, order = split_report(text)
    msections = manifest.get("sections") or []
    mids = [s.get("id") for s in msections]
    if order != mids:
        failures.append("report sections %s do not match the manifest sections %s" % (order, mids))
    counted = 0
    by_id = {}
    for ms in msections:
        sid = ms.get("id")
        if sid not in sections:
            continue
        title, lines = sections[sid]
        by_id[sid] = ms
        body = "\n".join(lines)
        blocks = fence_blocks(lines)
        hashes = {sha256_text(b): b for b in blocks}
        caps = ms.get("captures") or []
        if not caps:
            failures.append("Section %s carries claims without a source: no capture is recorded for it" % sid)
        for c in caps:
            if not c.get("url") or c["url"] not in body:
                failures.append("Section %s: the source URL %s is not shown in the section" % (sid, c.get("url")))
            if not c.get("retrieved_utc") or c["retrieved_utc"] not in body:
                failures.append("Section %s: the retrieval time %s for %s is not shown in the section"
                                % (sid, c.get("retrieved_utc"), c.get("url")))
            if c.get("evidence_sha256") not in hashes:
                failures.append("Section %s: the complete raw response for %s is not printed in the section "
                                "(no block with SHA-256 %s)" % (sid, c.get("url"), c.get("evidence_sha256")))
        for k in ms.get("counts") or []:
            rule = k.get("rule")
            if rule not in RULES:
                failures.append("Section %s: unknown count rule %r" % (sid, rule))
                continue
            counted += 1
            found = stated(rule, lines)
            if len(found) != 1:
                failures.append("Section %s: %d stated values for %s, not exactly one" % (sid, len(found), rule))
                continue
            cap = [c for c in caps if c.get("url") == k.get("capture_url") and c.get("evidence_sha256") in hashes]
            if not cap:
                failures.append("Section %s: the count %s has no printed raw response to recount from" % (sid, rule))
                continue
            try:
                recount = RULES[rule][1](k["capture_url"], hashes[cap[0]["evidence_sha256"]])
            except Exception as err:  # a raw response the parser refuses cannot support a count
                failures.append("Section %s: the raw response for %s cannot be recounted (%s)" % (sid, rule, err))
                continue
            if not (found[0] == str(k.get("value")) == recount):
                failures.append("Section %s: count mismatch for %s: section states %s, manifest records %s, "
                                "raw response recounts to %s" % (sid, rule, found[0], k.get("value"), recount))
    if counted == 0:
        failures.append("no count in the package can be checked against its raw response")

    for line in summary:
        m = SUMMARY_LINE_RE.match(line)
        if not m:
            if line.startswith("- No count is stated"):
                continue
            failures.append("unsourced summary claim (names no section): %s" % line)
            continue
        label, value, sid = m.groups()
        ms = by_id.get(sid)
        if ms is None:
            failures.append("summary claim names Section %s, which is not in the package: %s" % (sid, line))
        elif not any(k.get("label") == label and str(k.get("value")) == value for k in ms.get("counts") or []):
            failures.append("summary claim does not match a count recorded for Section %s: %s" % (sid, line))
    return failures


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def package(job_path, out_dir, replay=None, timing_log=None, packaged_utc=None, env=None):
    """Build, write, verify, and log one package. Returns (failures, log entry)."""
    started = utc_now_iso()
    t0 = time.monotonic()
    job = load_job(job_path)
    src = ReplaySource(replay) if replay else LiveSource(env)
    packaged_utc = packaged_utc or started
    report, manifest = build(job, src, packaged_utc)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_bytes(report.encode("utf-8"))
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    t1 = time.monotonic()
    failures = verify(out)
    t2 = time.monotonic()
    fetch_s = src.seconds
    entry = {
        "run_started_utc": started, "service": job["service"], "subject": job["subject"],
        "mode": src.mode, "job": rel(job_path), "bundle": rel(replay) if replay else None,
        "package_dir": rel(out), "requests": len(src.served),
        "fetch_seconds": round(fetch_s, 3), "assemble_seconds": round(t1 - t0 - fetch_s, 3),
        "verify_seconds": round(t2 - t1, 3), "total_seconds": round(t2 - t0, 3),
        "total_minutes": round((t2 - t0) / 60.0, 4),
        "deliverable_sha256": manifest["deliverable_sha256"],
        "verify": "PASS" if not failures else "FAIL",
    }
    if timing_log:
        with open(timing_log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return failures, entry


def main(argv=None):
    ap = argparse.ArgumentParser(description="Package and verify one report delivery.")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("package", help="build, write, verify, and time one package")
    p.add_argument("--job", required=True, help="job spec JSON")
    p.add_argument("--out", required=True, help="package directory to write")
    p.add_argument("--replay", help="capture bundle JSON; answer every request from it, fetch nothing")
    p.add_argument("--timing-log", help="JSONL file to append this run's timing line to")
    p.add_argument("--packaged-at", help="UTC time to print as Packaged (default: now)")
    v = sub.add_parser("verify", help="verify a written package")
    v.add_argument("--dir", required=True, help="package directory")
    v.add_argument("--timing-log", help="also require the deliverable hash in this timing log")
    args = ap.parse_args(argv)

    if args.command == "verify":
        failures = verify(args.dir, args.timing_log)
        for f in failures:
            print("FAIL %s" % f)
        print("verify: %s (%s)" % ("PASS" if not failures else "FAIL", args.dir))
        return 0 if not failures else 1
    try:
        failures, entry = package(args.job, args.out, args.replay, args.timing_log, args.packaged_at)
    except (PackageError, ValueError, KeyError, cpsc.FetchError, ef.FetchError, pp.FetchError, OSError) as err:
        sys.stderr.write("delivery packager: %s\nnothing written\n" % err)
        return 2
    for f in failures:
        print("FAIL %s" % f)
    print("package: %s, verify %s, %.3f s total (%.4f min): fetch %.3f s, assemble %.3f s, verify %.3f s"
          % (entry["package_dir"], entry["verify"], entry["total_seconds"], entry["total_minutes"],
             entry["fetch_seconds"], entry["assemble_seconds"], entry["verify_seconds"]))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
