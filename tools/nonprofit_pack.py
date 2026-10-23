#!/usr/bin/env python3
"""Nonprofit diligence pack runner: a batch over the ProPublica fetcher.

Given a list of nonprofit names or EINs, resolves each entry against the
ProPublica Nonprofit Explorer API v2 and assembles one combined Markdown
pack in the delivery format from AGENT-BRIEF.md:

* a summary table at the front: entity as listed, status, the count of
  filings with extracted figures, the tax period and total revenue of the
  filing the figures come from (where the source states them), and the
  number of the section that carries the evidence for the row;
* one section per entry, rendered by tools/propublica_nonprofits.py
  itself, so every claim keeps its source link with the raw excerpt
  printed directly beneath it, verbatim;
* a closing list of the entities that could not be found, each proven
  with the complete raw response printed in its section.

Resolution rules, the single fetcher's discipline carried into the batch:

* An EIN entry is fetched directly.
* A name entry is searched. The result is examined only when its name
  equals the entry exactly, ignoring case and spacing, the same rule as
  the single fetcher. No exact match, or more than one, leaves the entry
  not resolved: the search section is printed as fetched and the summary
  says so. The runner never picks a near match.
* An entity listed twice is examined once; the later row points at the
  first section.

The empty search, observed live on 2026-10-23: the search endpoint
answers a search with no results with HTTP 404 and the usual search
body carrying total_results 0 and an empty organizations array. The
single fetcher still fails closed on any non-200 and is unchanged;
this runner is the tool that reads that one observed shape as an empty
result, and only for a search URL whose body parses to total_results 0
with an empty organizations array. The complete raw response, the 404
status line included, is printed in the entry's section as the proof.
Every other non-200 answer, transport failure, or body that is not the
expected JSON fails the whole run closed: nothing on stdout, a
diagnostic on stderr, exit 2. An organization fetch that fails is
never read as "not found"; the empty shape was observed for search
only.

Key: none needed. Standard library only. The network calls are GETs to
projects.propublica.org made through this file's own fetch, which keeps
the real status line and headers of every answer, 404 answers included,
so transcripts are captures and not reconstructions.

Usage examples (the list is tools/examples/nonprofit-pack-list.txt,
the five well known nonprofits of the captured demo pack plus one name
that is not found):

    python3 tools/nonprofit_pack.py --list tools/examples/nonprofit-pack-list.txt
    python3 tools/nonprofit_pack.py --name 'Feeding America' --ein 53-0196605

List file format: one entry per line; a line that is a 9 digit EIN,
dash optional, is an EIN entry, anything else is a name entry; blank
lines and lines starting with # are skipped.
"""

import argparse
import base64
import http.client
import os
import sys
import urllib.parse
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import propublica_nonprofits as pp  # noqa: E402

TIMEOUT_SECONDS = 30

Entry = namedtuple("Entry", "text kind ein")
Outcome = namedtuple("Outcome", "entry status section filings tax_prd revenue")


# ----------------------------------------------------------------------
# Fetching: like the single fetcher's, but a transcript is kept for a
# 404 answer too, so the observed empty search shape can be proven with
# its full raw response instead of a snippet.
# ----------------------------------------------------------------------

def is_empty_search(capture):
    """True only for the observed empty shape: a search body that parses
    to total_results 0 with an empty organizations array."""
    try:
        data = pp.root(capture)
    except pp.FetchError:
        return False
    if not (data.has("total_results") and data.has("organizations")):
        return False
    try:
        return data.value("total_results") == 0 and data.value("organizations") == []
    except Exception:
        return False


def _open(parts, target):
    """An http.client connection to the URL's origin, plus the request
    target to send on it. When the environment configures a proxy
    (https_proxy and friends, no_proxy honored), the connection goes
    through it, with a CONNECT tunnel for https so the origin's own
    status line, headers, and body are what come back. Without this the
    fetch would bypass the proxy the rest of the toolbox relies on."""
    host = parts.hostname
    port = parts.port or (443 if parts.scheme == "https" else 80)
    bypass = {h.strip() for h in os.environ.get("no_proxy", "").split(",") if h.strip()}
    proxy = None
    if host not in bypass:
        var = "https_proxy" if parts.scheme == "https" else "http_proxy"
        raw = os.environ.get(var) or os.environ.get(var.upper())
        if raw:
            proxy = urllib.parse.urlsplit(raw)
    if parts.scheme == "https":
        if proxy is None:
            return http.client.HTTPSConnection(host, port, timeout=TIMEOUT_SECONDS), target
        conn = http.client.HTTPSConnection(proxy.hostname, proxy.port or 8080, timeout=TIMEOUT_SECONDS)
        headers = {}
        if proxy.username:
            cred = base64.b64encode(("%s:%s" % (urllib.parse.unquote(proxy.username),
                                                urllib.parse.unquote(proxy.password or ""))
                                     ).encode("utf-8")).decode("ascii")
            headers["Proxy-Authorization"] = "Basic " + cred
        conn.set_tunnel(host, port, headers)
        return conn, target
    if proxy is not None:
        conn = http.client.HTTPConnection(proxy.hostname, proxy.port or 8080, timeout=TIMEOUT_SECONDS)
        return conn, urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
    return http.client.HTTPConnection(host, port, timeout=TIMEOUT_SECONDS), target


def fetch(url):
    """GET the URL and return a pp.Capture. A 200 answer is returned, and
    so is a 404 answer to a search URL whose body is the observed empty
    search shape; anything else raises pp.FetchError, so a failure can
    never be printed as a result."""
    retrieved = pp.utc_now_iso()
    parts = urllib.parse.urlsplit(url)
    target = parts.path + ("?" + parts.query if parts.query else "")
    conn, target = _open(parts, target)
    try:
        conn.request("GET", target, headers={"Accept": "application/json",
                                             "User-Agent": "tiny-ledger-nonprofit-pack"})
        response = conn.getresponse()
        raw = response.read()
    except (OSError, http.client.HTTPException) as err:
        raise pp.FetchError("%s could not be fetched: %s" % (url, err))
    finally:
        conn.close()
    version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
    status_line = "%s %s %s" % (version, response.status, response.reason)
    headers = ["%s: %s" % (k, v) for k, v in response.getheaders()]
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError as err:
        raise pp.FetchError("%s body is not UTF-8: %s" % (url, err))
    capture = pp.Capture(url, retrieved, status_line, response.status, headers, body)
    if response.status == 200:
        return capture
    if response.status == 404 and parts.path.endswith("/search.json") and is_empty_search(capture):
        return capture
    raise pp.FetchError("%s answered HTTP %s %s: %s" % (url, response.status, response.reason, body[:300]))


# ----------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------

def parser():
    p = argparse.ArgumentParser(description="Nonprofit diligence pack runner (batch over the ProPublica fetcher).")
    p.add_argument("--list", dest="list_path", help="file with one entry per line, a name or a 9 digit EIN")
    p.add_argument("--name", action="append", default=[], help="organization name entry; repeatable")
    p.add_argument("--ein", action="append", default=[], help="EIN entry, 9 digits, dash optional; repeatable")
    p.add_argument("--subject", help="pack heading (default: a generated batch label)")
    return p


def parse_entry(text):
    text = text.strip()
    try:
        return Entry(text, "ein", pp.normalize_ein(text))
    except ValueError:
        return Entry(text, "name", None)


def read_list(path):
    entries = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.append(parse_entry(line))
    return entries


def collect_entries(args):
    entries = []
    if args.list_path:
        entries += read_list(args.list_path)
    for name in args.name:
        entries.append(parse_entry(name))
    for ein in args.ein:
        entries.append(Entry(ein.strip(), "ein", pp.normalize_ein(ein)))
    if not entries:
        raise ValueError("no entries: give --list, --name, or --ein")
    return entries


# ----------------------------------------------------------------------
# Summary figures, read from the same parsed body the section renders
# ----------------------------------------------------------------------

def filing_summary(capture):
    """(filings count, tax_prd literal, totrevenue literal) for the filing
    the rendered section takes its figures from, or (count, None, None)
    when no filing carries a readable tax_prd. Literals are the raw JSON
    text, exactly as the section prints them."""
    data = pp.root(capture)
    filings = data.children("filings_with_data")
    dated = [f for f in filings if pp.tax_prd_of(f) is not None]
    if not dated:
        return len(filings), None, None
    latest = max(dated, key=pp.tax_prd_of)
    revenue = latest.literal("totrevenue") if latest.has("totrevenue") else None
    return len(filings), latest.literal("tax_prd"), revenue


# ----------------------------------------------------------------------
# Assembly
# ----------------------------------------------------------------------

def assemble(entries, subject, fetcher=fetch):
    outcomes = []
    sections = []
    seen = {}
    for entry in entries:
        number = len(sections) + 1
        if entry.kind == "ein":
            if entry.ein in seen:
                outcomes.append(Outcome(entry, "Found (same organization as entry %d)" % seen[entry.ein][0],
                                        seen[entry.ein][1], None, None, None))
                continue
            cap = fetcher(pp.organization_url(entry.ein))
            section = pp.render_organization(cap, "Organization: EIN %s" % entry.ein)
            count, tax_prd, revenue = filing_summary(cap)
            seen[entry.ein] = (len(outcomes) + 1, number)
            outcomes.append(Outcome(entry, "Found", number, count, tax_prd, revenue))
            sections.append(["## Section %d: %s" % (number, entry.text), ""] + section)
            continue
        search = fetcher(pp.search_url(entry.text))
        data, orgs, found = pp.search_results(search, {})
        if not orgs:
            section = pp.render_search(search, entry.text, [], {})
            outcomes.append(Outcome(entry, "Not found", number, None, None, None))
            sections.append(["## Section %d: %s" % (number, entry.text), ""] + section)
            continue
        matches = pp.exact_name_matches(found, entry.text)
        if len(matches) != 1:
            if not matches:
                status = "Not resolved: no exact name match"
                note = ("No search result's name equals the entry exactly, so no organization record "
                        "was fetched. The results as returned are listed in the search section above; "
                        "rerun with the EIN of the intended result to examine it.")
            else:
                status = "Not resolved: %d exact name matches" % len(matches)
                note = ("%d search results carry this exact name, so the runner does not choose "
                        "between them. Rerun with the EIN of the intended result to examine it."
                        % len(matches))
            section = pp.render_search(search, entry.text, [], {})
            outcomes.append(Outcome(entry, status, number, None, None, None))
            sections.append(["## Section %d: %s" % (number, entry.text), "", note, ""] + section)
            continue
        ein = matches[0]
        search_section = pp.render_search(search, entry.text, [ein], {})
        if ein in seen:
            first_entry, first_section = seen[ein]
            outcomes.append(Outcome(entry, "Found (same organization as entry %d)" % first_entry,
                                    number, None, None, None))
            sections.append(["## Section %d: %s" % (number, entry.text), "",
                             "Resolved to EIN %s, examined in full at section %d." % (ein, first_section),
                             ""] + search_section)
            continue
        cap = fetcher(pp.organization_url(ein))
        section = search_section + pp.render_organization(cap, "Organization: EIN %s" % ein)
        count, tax_prd, revenue = filing_summary(cap)
        seen[ein] = (len(outcomes) + 1, number)
        outcomes.append(Outcome(entry, "Found", number, count, tax_prd, revenue))
        sections.append(["## Section %d: %s" % (number, entry.text), ""] + section)

    lines = ["# Nonprofit diligence pack: %s" % subject, "",
             "Scope: the ProPublica Nonprofit Explorer API v2 as returned at the stated times; figures are "
             "the API's extracted Form 990 values as shown, not an audit, and not a full reading of any filing. "
             "Each summary row is traceable to the section numbered in its last column; every figure in the "
             "table appears in that section with its source link and the raw excerpt beneath it.", ""]
    lines += ["## Summary", "",
              "| # | Entity (as listed) | Status | Filings with extracted figures | Filing tax period | "
              "Total revenue | Section |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for i, o in enumerate(outcomes, 1):
        cell = lambda v: pp.inline(v) if v is not None else "n/a"
        lines.append("| %d | %s | %s | %s | %s | %s | %d |" % (
            i, o.entry.text.replace("|", "\\|"), o.status,
            str(o.filings) if o.filings is not None else "n/a",
            cell(o.tax_prd), cell(o.revenue), o.section))
    lines.append("")
    for section in sections:
        lines += section
    lines += ["## Entities that could not be found", ""]
    missing = [(i, o) for i, o in enumerate(outcomes, 1) if o.status == "Not found"]
    if not missing:
        lines.append("None: no listed entity came back with an empty search.")
    for i, o in missing:
        lines.append("- Entry %d, \"%s\": the search returned no organizations. The complete raw response, "
                     "including the HTTP 404 status line the search endpoint answers an empty search with, "
                     "is printed in section %d." % (i, o.entry.text, o.section))
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        entries = collect_entries(args)
        subject = args.subject or "batch of %d entries" % len(entries)
        out = assemble(entries, subject)
    except (ValueError, OSError) as err:
        print("error: %s" % err, file=sys.stderr)
        return 2
    except pp.FetchError as err:
        print("fetch failed, no pack printed: %s" % err, file=sys.stderr)
        return 2
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
