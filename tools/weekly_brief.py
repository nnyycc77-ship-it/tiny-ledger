#!/usr/bin/env python3
"""Filings and awards weekly brief (issue #146).

Builds one dated Markdown brief for a seven day window ending on
--week-ending, from the two existing fetchers:

  SEC EDGAR Form D (tools/edgar_formd.py)
      For each CIK on the config's watchlist: the submissions index, then
      the primary XML of every Form D or D/A filed inside the window. A
      filing is listed when its industry group equals one of the config's
      sectors, or its issuer name or industry group contains one of the
      keywords (both case insensitive; with neither list given, every
      filing in the window is listed). The scope is the watchlist, not all
      of EDGAR: the fetcher reads one issuer at a time.

  USAspending prime contract awards (tools/usaspending_awards.py)
      One spending_by_award query: contract award types A to D, the
      config's NAICS prefixes as the category filter, and the window as
      time_period, exactly as that fetcher builds it. Every award on the
      returned page is listed.

Every entry carries the filer or recipient, the amount only where the
source states it ("not stated by the source" otherwise), the date, and the
source link with the raw excerpt it came from printed beneath it. A leg
with no matching entry says so and prints every raw response it read, in
full; it is never padded. Any failed or unexpected response stops the run
with exit 2 and no brief: a failed fetch is never shown as an empty
result.

Config (JSON):

    {"title": "Weekly filings and awards brief",
     "edgar": {"ciks": ["2156237"], "sectors": ["Pooled Investment Fund"], "keywords": []},
     "usaspending": {"naics": ["5415"], "limit": 25}}

Run (EDGAR needs an operator contact, as edgar_formd.py documents; the
contact below is a placeholder, use your own name and address):

    EDGAR_CONTACT="Your Name you@example.com" python3 tools/weekly_brief.py \\
        --config tools/weekly-brief/sample-config.json --week-ending 2026-10-23

Standard library only.
"""

import argparse
import json
import re
import sys
from argparse import Namespace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import edgar_formd as ef  # noqa: E402
import usaspending_awards as ua  # noqa: E402
from propublica_nonprofits import Node, elements, fenced, skip_ws  # noqa: E402

NOT_STATED = "not stated by the source"
AWARD_PAGE = "https://www.usaspending.gov/award/%s"
FORM_D_ELEMENTS = ("entityName", "industryGroupType", "totalOfferingAmount", "totalAmountSold")
CONFIG_KEYS = {"title", "edgar", "usaspending"}


class BriefError(ValueError):
    """The brief cannot be produced as configured. Nothing is printed."""


# ----------------------------------------------------------------- config

def load_config(path):
    try:
        config = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise BriefError("cannot read config %s: %s" % (path, err))
    if not isinstance(config, dict) or set(config) - CONFIG_KEYS:
        raise BriefError("config keys allowed: %s" % ", ".join(sorted(CONFIG_KEYS)))
    edgar, usa = config.get("edgar"), config.get("usaspending")
    if edgar is None and usa is None:
        raise BriefError("config needs an edgar section, a usaspending section, or both")
    if edgar is not None:
        if not isinstance(edgar, dict) or set(edgar) - {"ciks", "sectors", "keywords"}:
            raise BriefError("edgar takes ciks, sectors and keywords only")
        ciks = edgar.get("ciks")
        if not isinstance(ciks, list) or not ciks:
            raise BriefError("edgar.ciks must list at least one CIK")
        for cik in ciks:
            ef.cik10(cik)  # ValueError on a bad CIK
        for key in ("sectors", "keywords"):
            values = edgar.get(key, [])
            if not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
                raise BriefError("edgar.%s must be a list of non empty strings" % key)
    if usa is not None:
        if not isinstance(usa, dict) or set(usa) - {"naics", "limit"}:
            raise BriefError("usaspending takes naics and limit only")
        naics = usa.get("naics")
        if not isinstance(naics, list) or not naics:
            raise BriefError("usaspending.naics must list at least one NAICS prefix")
    return config


def window(week_ending):
    try:
        end = date.fromisoformat(week_ending)
    except ValueError:
        raise BriefError("--week-ending must be YYYY-MM-DD")
    return end - timedelta(days=6), end


# ----------------------------------------------------------------- EDGAR

def matches(parsed, sectors, keywords):
    """(True, why) when a parsed Form D passes the filters, else (False, why)."""
    if not sectors and not keywords:
        return True, "no sector or keyword filter set"
    groups = [g.casefold() for g in parsed["industryGroup"]]
    for sector in sectors:
        if sector.strip().casefold() in groups:
            return True, "industry group equals sector %s" % json.dumps(sector)
    haystack = " ".join(parsed["issuerName"] + parsed["industryGroup"]).casefold()
    for keyword in keywords:
        if keyword.strip().casefold() in haystack:
            return True, "issuer name or industry group contains keyword %s" % json.dumps(keyword)
    return False, "industry group %s matches no filter" % json.dumps(parsed["industryGroup"])


def xml_excerpt(body):
    """The Form D XML elements the entry quotes, cut verbatim from the body."""
    lines = []
    for tag in FORM_D_ELEMENTS:
        lines += [m.group(0) for m in re.finditer(r"<%s>[^<]*</%s>" % (tag, tag), body)]
    return "\n".join(lines)


def index_excerpt(body, position):
    """The filing's own entries in the submissions index, cut verbatim.

    The index is columnar (filings.recent.<field> arrays), so the excerpt
    is the raw text of element `position` in each array the entry quotes.
    """
    recent = Node(body, skip_ws(body, 0)).child("filings").child("recent")
    lines = []
    for field in ("form", "accessionNumber", "filingDate"):
        _, vs, _ = recent.spans[field]
        start, stop = elements(body, vs)[position]
        lines.append("filings.recent.%s[%d]: %s" % (field, position, body[start:stop]))
    return "\n".join(lines)


def shown(values):
    return "; ".join(values) if values else NOT_STATED


def edgar_leg(cfg, start, end, contact, fetcher):
    sectors, keywords = cfg.get("sectors", []), cfg.get("keywords", [])
    entries, checked, raws = [], [], []
    for cik in cfg["ciks"]:
        sub = fetcher(ef.submissions_url(cik), contact)
        ef.require_200(sub, "EDGAR submissions index")
        raws.append(sub)
        name, cik_shown, filings, _ = ef.parse_submissions(sub.body)
        for position, filing in enumerate(filings):
            if filing["form"] not in ef.FORM_D_TYPES:
                continue
            if not start.isoformat() <= filing["filingDate"] <= end.isoformat():
                continue
            url = ef.primary_doc_url(cik, filing["accessionNumber"], filing["primaryDocument"])
            if url is None or not url.endswith(".xml"):
                checked.append("%s %s: primary document is not XML; not read" % (cik, filing["accessionNumber"]))
                continue
            doc = fetcher(url, contact)
            ef.require_200(doc, "EDGAR Form D primary document")
            raws.append(doc)
            parsed = ef.parse_form_d(doc.body)
            ok, why = matches(parsed, sectors, keywords)
            if not ok:
                checked.append("%s (CIK %s), %s %s filed %s: checked, not listed: %s"
                               % (shown(parsed["issuerName"]), cik_shown, filing["form"],
                                  filing["accessionNumber"], filing["filingDate"], why))
                continue
            entries.append({"filing": filing, "parsed": parsed, "doc": doc, "cik": cik, "why": why,
                            "sub": sub, "position": position})
    lines = ["## SEC EDGAR Form D filings", "",
             "Scope: the %d issuer(s) on the watchlist (CIK %s), Form D and D/A filed %s to %s. "
             "Sectors: %s. Keywords: %s." % (len(cfg["ciks"]), ", ".join(str(c) for c in cfg["ciks"]),
                                              start, end, json.dumps(sectors), json.dumps(keywords)), ""]
    for e in entries:
        p, f = e["parsed"], e["filing"]
        lines += ["### %s, %s %s" % (shown(p["issuerName"]), f["form"], f["accessionNumber"]), "",
                  "- Filer as shown: %s" % shown(p["issuerName"]),
                  "- Date filed as shown (submissions index): %s" % f["filingDate"],
                  "- Total offering amount as shown: %s" % shown(p["totalOfferingAmount"]),
                  "- Total amount sold as shown: %s" % shown(p["totalAmountSold"]),
                  "- Industry group as shown: %s" % shown(p["industryGroup"]),
                  "- Listed because: %s" % e["why"],
                  "- Filing index: <%s>" % ef.filing_index_url(e["cik"], f["accessionNumber"]),
                  "", "Source: <%s>" % e["sub"].url, "Retrieved (UTC): %s" % e["sub"].retrieved,
                  fenced(index_excerpt(e["sub"].body, e["position"])),
                  "", "Source: <%s>" % e["doc"].url, "Retrieved (UTC): %s" % e["doc"].retrieved,
                  fenced(xml_excerpt(e["doc"].body)), ""]
    if checked:
        lines += ["Checked in the window and not listed:", ""] + ["- %s" % c for c in checked] + [""]
    if not entries:
        lines += ["No Form D filing in the window matched the filters. Every raw response read for this "
                  "leg follows, in full.", ""]
        for cap in raws:
            lines += ["Source: <%s>" % cap.url, "Retrieved (UTC): %s" % cap.retrieved,
                      fenced(cap.transcript), ""]
    return lines, len(entries)


# ----------------------------------------------------------------- USAspending

def usaspending_query(cfg, start, end):
    args = Namespace(recipient=None, naics=list(cfg["naics"]), start=start.isoformat(), end=end.isoformat(),
                     page=1, limit=int(cfg.get("limit", 25)))
    return ua.build_query(args)


def usaspending_leg(cfg, start, end, fetcher):
    query = usaspending_query(cfg, start, end)
    capture = fetcher(query)
    try:
        root = Node(capture.raw, skip_ws(capture.raw, 0))
        records = root.children("results")
        data = json.loads(capture.raw, parse_float=Decimal)
        has_next = data["page_metadata"]["hasNext"]
    except (ValueError, KeyError, TypeError, IndexError) as err:
        raise BriefError("USAspending response is not the documented shape: %s" % err)
    lines = ["## USAspending prime contract awards", "",
             "Scope: contract award types A to D, NAICS prefixes %s, time period %s to %s, one page of up to "
             "%s, sorted by Award Amount (the fetcher's query). Award Amount is the API field as returned."
             % (json.dumps(cfg["naics"]), start, end, json.loads(query)["limit"]), "",
             "Exact query: POST %s" % ua.ENDPOINT, "Exact request body:", fenced(query),
             "Retrieved (UTC): %s" % capture.retrieved, ""]
    for rec in records:
        name = rec.value("Recipient Name") if rec.has("Recipient Name") else None
        amount = rec.literal("Award Amount") if rec.has("Award Amount") and rec.value("Award Amount") is not None else None
        when = rec.value("Start Date") if rec.has("Start Date") else None
        gid = rec.value("generated_internal_id") if rec.has("generated_internal_id") else None
        if not isinstance(gid, str) or not gid:
            raise BriefError("a USAspending record has no generated_internal_id")
        lines += ["### %s, award %s" % (name or NOT_STATED, rec.value("Award ID") if rec.has("Award ID") else gid), "",
                  "- Recipient as shown: %s" % (name or NOT_STATED),
                  "- Award Amount as shown: %s" % (amount or NOT_STATED),
                  "- Start Date as shown: %s" % (when or NOT_STATED),
                  "- Award page: <%s>" % (AWARD_PAGE % gid),
                  "", "Source: <%s> (record from the response to the request above)" % ua.ENDPOINT,
                  fenced(rec.whole()), ""]
    if has_next:
        lines += ["The API reports more pages; this brief lists the first page only.", ""]
    if not records:
        lines += ["No award matched the filters for this window. The complete raw response follows.", "",
                  "Source: <%s>" % ua.ENDPOINT, fenced(capture.raw), ""]
    return lines, len(records)


# ----------------------------------------------------------------- brief

def build(config, week_ending, contact=None, edgar_fetch=None, usa_fetch=None, now=None):
    start, end = window(week_ending)
    made = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["# %s: week of %s to %s" % (config.get("title", "Filings and awards brief"), start, end), "",
             "Generated (UTC): %s, from the source reads named in each section. Every figure below is quoted "
             "from a raw excerpt beneath it; nothing is estimated." % made, ""]
    counts = []
    if config.get("edgar") is not None:
        section, n = edgar_leg(config["edgar"], start, end, contact, edgar_fetch or ef.fetch)
        lines += section
        counts.append("%d Form D filing(s)" % n)
    if config.get("usaspending") is not None:
        section, n = usaspending_leg(config["usaspending"], start, end, usa_fetch or ua.fetch)
        lines += section
        counts.append("%d award(s)" % n)
    lines.insert(4, "In this brief: %s." % ", ".join(counts))
    lines.insert(5, "")
    return "\n".join(lines).rstrip("\n") + "\n"


def unsupported_figures(brief):
    """Every 'as shown' value in an entry that is not a whole field inside
    one of that entry's quoted excerpts, as (entry heading, value). A value
    counts only as a complete XML element text (>value<) or JSON value
    ("value" or :value followed by , or }), never as a substring of
    another figure. Empty means every figure the brief states is in the
    excerpt beneath it."""
    problems = []
    for section in re.split(r"\n(?=### )", brief)[1:]:
        heading = section.split("\n", 1)[0]
        excerpts = "\n".join(m[1] for m in re.findall(r"^(`{3,})\n(.*?)\n\1$", section, re.S | re.M))
        for value in re.findall(r"^- [^:\n]* as shown(?: \([^)]*\))?: (.+)$", section, re.M):
            for part in value.split("; "):
                if part == NOT_STATED:
                    continue
                v = re.escape(part)
                if not re.search(r">%s<|\"%s\"|:\s*%s\s*[,}]" % (v, v, v), excerpts):
                    problems.append((heading, part))
    return problems


def main(argv=None, edgar_fetch=None, usa_fetch=None, env=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Filings and awards weekly brief.")
    p.add_argument("--config", help="brief config JSON (required unless --check)")
    p.add_argument("--check", metavar="BRIEF", help="verify an existing brief: every figure inside its excerpts")
    p.add_argument("--week-ending", default=datetime.now(timezone.utc).date().isoformat(),
                   help="last day of the seven day window, YYYY-MM-DD (default: today UTC)")
    p.add_argument("--contact", help="EDGAR operator contact (or EDGAR_CONTACT)")
    args = p.parse_args(argv)
    if args.check:
        try:
            problems = unsupported_figures(Path(args.check).read_text(encoding="utf-8"))
        except OSError as err:
            stderr.write("error: %s\n" % err)
            return 2
        for heading, value in problems:
            stdout.write("NOT IN EXCERPT: %s: %s\n" % (heading, value))
        stdout.write("%s: %s\n" % (args.check, "every figure is in its excerpts" if not problems
                                    else "%d figure(s) not in their excerpts" % len(problems)))
        return 1 if problems else 0
    if not args.config:
        p.error("--config is required")
    try:
        config = load_config(args.config)
        contact = ef.contact_from(args.contact, env) if config.get("edgar") is not None else None
        brief = build(config, args.week_ending, contact, edgar_fetch, usa_fetch)
    except (BriefError, ValueError, OSError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write(brief)
    return 0


if __name__ == "__main__":
    sys.exit(main())
