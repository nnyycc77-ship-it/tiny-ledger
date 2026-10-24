#!/usr/bin/env python3
"""The remaining fetchers as paid API endpoints (issue #65).

Nine GET endpoints beside GET /recall, each wrapping one merged fetcher in
tools/ as library code and returning that fetcher's own rendered Markdown
in the delivery format from AGENT-BRIEF.md: the claim lines, the exact
query, the UTC retrieval time, the source link, and the complete raw
response directly beneath the link. This module adds a title block and
nothing else to the fetchers' output.

    /carrier     tools/fmcsa_carrier.py        usdot | name
    /litigation  tools/courtlistener_recap.py  party (repeatable)
    /awards      tools/usaspending_awards.py   recipient | naics
    /nonprofit   tools/propublica_nonprofits.py  name | ein
    /formd       tools/edgar_formd.py          cik | issuer
    /pagespeed   tools/pagespeed_snapshot.py   url (repeatable, up to 5)
    /ofac        tools/ofac_sdn_check.py       name
    /domain      tools/domain_trust_check.py   domain
    /app         tools/app_lookup_check.py     name (country, limit optional)
    /vin         tools/vin_decode.py           vin

Each endpoint takes the fetcher's own command line inputs as query
parameters under the same names (hyphens become underscores), validates
them the way the fetcher's command line does, and maps outcomes the way
GET /recall does: a bad query is 400 with no report; a transport failure,
an HTTP error the fetcher treats as fatal, or a response the fetcher
cannot read is 502 with no report; an operator exclusion naming a record
the response does not contain is 400. A failed fetch is never an empty
result.

Server side values, read from the environment at call time and never
printed: COURTLISTENER_TOKEN (optional, lifts the anonymous rate limit),
PAGESPEED_API_KEY (optional; without it the API answers 429 with quota 0,
and that transcript is the report), EDGAR_CONTACT (required for /formd by
EDGAR fair access: the operator's "Name address" contact for the
User-Agent; when it is unset /formd answers 503 and fetches nothing).

`handle()` in api/recall_api.py routes these paths here and stays host
free; payment collection is outside this module, exactly as for /recall.
Standard library only.
"""

import os
import sys
import types
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import app_lookup_check as al  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import domain_trust_check as dt  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
from tools import ofac_sdn_check as ofac  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import usaspending_awards as ua  # noqa: E402
from tools import vin_decode as vd  # noqa: E402

SERVICE_NAME = "Hojo Research Agent"


class BadRequest(ValueError):
    """The query is not a valid call of this endpoint. No fetch was made."""


class FetchFailed(Exception):
    """The source could not be fetched or read. No report is produced."""


class Unavailable(Exception):
    """The endpoint lacks a server side value it needs. No fetch was made."""


# ----------------------------------------------------------------------
# Query helpers
# ----------------------------------------------------------------------

def _single(query, key, default=None):
    values = [v.strip() for v in query.get(key, []) if v.strip()]
    if len(values) > 1:
        raise BadRequest("give %s once" % key)
    return values[0] if values else default


def _many(query, key):
    return [v for v in query.get(key, []) if v.strip()]


def _int(query, key, default, minimum=None, maximum=None):
    raw = _single(query, key)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise BadRequest("%s must be an integer" % key)
    if minimum is not None and value < minimum:
        raise BadRequest("%s must be at least %d" % (key, minimum))
    if maximum is not None and value > maximum:
        raise BadRequest("%s must be at most %d" % (key, maximum))
    return value


def _flag(query, key):
    raw = _single(query, key)
    if raw is None:
        return False
    if raw.lower() in ("1", "true", "yes"):
        return True
    if raw.lower() in ("0", "false", "no"):
        return False
    raise BadRequest("%s must be 1 or 0" % key)


def _head(title, observation, tool):
    return [
        "# %s" % title,
        "",
        observation,
        "",
        "Produced by the %s API from %s. The query, the retrieval time, the "
        "source link, and the complete raw response are below." % (SERVICE_NAME, tool),
        "",
    ]


def _text(head, lines):
    return "\n".join(head + list(lines)) + "\n"


def _transport(err):
    return FetchFailed("fetch failed, no report emitted: %s" % err)


# ----------------------------------------------------------------------
# /carrier
# ----------------------------------------------------------------------

def carrier(query, env=None):
    """FMCSA carrier data via tools/fmcsa_carrier.py."""
    usdot = _single(query, "usdot")
    name = _single(query, "name")
    subject = _single(query, "subject")
    sources = _many(query, "source")
    exclude = _many(query, "exclude")
    limit = _int(query, "limit", 50, minimum=1)
    if bool(usdot) == bool(name):
        raise BadRequest("give exactly one of usdot or name")
    if exclude and not name:
        raise BadRequest("exclude applies to a name search")
    if sources and not usdot:
        raise BadRequest("source applies to a usdot run")
    try:
        exclusions = fc.parse_exclusions(exclude)
        if usdot:
            usdot = fc.check_usdot(usdot)
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    ordered = []
    for s in sources or fc.ALL_SOURCES:
        if s not in fc.ALL_SOURCES:
            raise BadRequest("source must be one of %s" % ", ".join(fc.ALL_SOURCES))
        if s not in ordered:
            ordered.append(s)
    try:
        if name:
            capture = fc.fetch(fc.census_name_url(name, limit))
            lines = ["## Carrier search: %s" % (subject or name), ""]
            lines.extend(fc.name_search_section(name, capture, exclusions))
            title = "Carrier vetting: %s" % (subject or name)
        else:
            urls = {"census": fc.census_record_url, "safer": fc.safer_url, "li": fc.li_url}
            captures = {}
            for s in ordered:
                captures[s] = fc.fetch(urls[s](usdot))
            lines = fc.render_carrier(subject or "USDOT %s" % usdot, usdot, captures, ordered)
            title = "Carrier vetting: %s" % (subject or "USDOT %s" % usdot)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head(title,
                 "Observation only: this report records what the public FMCSA sources "
                 "returned at the retrieval times stated below; nothing about the carrier "
                 "was inspected or verified beyond those records.",
                 "tools/fmcsa_carrier.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /litigation
# ----------------------------------------------------------------------

def litigation(query, env=None):
    """CourtListener RECAP docket search via tools/courtlistener_recap.py."""
    env = os.environ if env is None else env
    parties = _many(query, "party")
    if not parties:
        raise BadRequest("give at least one party=<name variant>; the first is the exact name whose results are listed")
    subject = _single(query, "subject")
    order_by = _single(query, "order_by", cl.DEFAULT_ORDER)
    list_count = _int(query, "list", 10, minimum=0)
    docket_details = _flag(query, "docket_details")
    try:
        exclusions = cl.parse_exclusions(_many(query, "exclude"))
        filed_after = _single(query, "filed_after")
        filed_after = cl.check_date(filed_after) if filed_after else cl.default_filed_after()
        variants = []
        for v in parties:
            cl.party_query(v)
            if v not in variants:
                variants.append(v)
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    token = env.get(cl.TOKEN_ENV) or None
    subject = subject or variants[0]
    try:
        searches = []
        for i, variant in enumerate(variants):
            label = cl.LABELS[i] if i < len(cl.LABELS) else "variant %d" % (i + 1)
            searches.append((variant, label, cl.fetch(cl.search_url(variant, filed_after, order_by), token)))
        docket_captures = None
        if docket_details:
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
                        docket_captures.append((str(docket_id), cl.fetch(cl.docket_url(docket_id), token)))
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    lines = cl.render_section(subject, variants, filed_after, order_by, searches,
                              list_count, exclusions, docket_captures)
    head = _head("Litigation screen: %s" % subject,
                 "Observation only: this report records what the public CourtListener RECAP "
                 "docket index returned at the retrieval times stated below; it is an index "
                 "level screen, not a legal opinion, and an empty result is not proof of no "
                 "litigation.",
                 "tools/courtlistener_recap.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /awards
# ----------------------------------------------------------------------

def awards(query, env=None):
    """USAspending prime contract awards via tools/usaspending_awards.py."""
    args = types.SimpleNamespace(
        recipient=_single(query, "recipient"),
        naics=_many(query, "naics"),
        start=_single(query, "start"),
        end=_single(query, "end"),
        page=_int(query, "page", 1),
        limit=_int(query, "limit", 10),
        exclude=_many(query, "exclude"),
    )
    try:
        request_body = ua.build_query(args)
        excluded = ua.exclusions(args.exclude)
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    try:
        capture = ua.fetch(request_body)
    except (ValueError, UnicodeError, urllib.error.URLError, TimeoutError, OSError) as err:
        # The fetcher raises ValueError for a non 200 status or a non JSON
        # content type; both are failed fetches, never empty results.
        raise _transport(err)
    try:
        report = ua.render(capture, excluded)
    except ValueError as err:
        if "exclude" in str(err):
            raise BadRequest(str(err).replace("--exclude", "exclude"))
        raise FetchFailed("source response not understood, no report emitted: %s" % err)
    subject = args.recipient or ("NAICS " + ", ".join(args.naics))
    head = _head("Contract awards: %s" % subject,
                 "Observation only: this report records one page of what the public "
                 "USAspending API returned at the retrieval time stated below; Award Amount "
                 "is the API field as returned, not a payment or revenue estimate.",
                 "tools/usaspending_awards.py")
    return "\n".join(head) + report


# ----------------------------------------------------------------------
# /nonprofit
# ----------------------------------------------------------------------

def nonprofit(query, env=None):
    """ProPublica Nonprofit Explorer via tools/propublica_nonprofits.py."""
    name = _single(query, "name")
    subject = _single(query, "subject")
    try:
        eins = []
        for e in _many(query, "ein"):
            n = pp.normalize_ein(e)
            if n not in eins:
                eins.append(n)
        excluded = pp.exclusions(_many(query, "exclude"))
        if excluded and not name:
            raise ValueError("exclude needs name: exclusions are search results")
        if set(excluded) & set(eins):
            raise ValueError("an EIN cannot be both examined and excluded")
        if not name and not eins:
            raise ValueError("give name=<organization>, ein=<EIN>, or both")
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    subject = subject or name or ", ".join(eins)
    try:
        report = pp.report(name, eins, excluded, subject, fetcher=pp.fetch)
    except pp.FetchError as err:
        raise _transport(err)
    head = _head("Nonprofit diligence: %s" % subject,
                 "Observation only: this report records what the public ProPublica Nonprofit "
                 "Explorer API returned at the retrieval times stated below; the figures are "
                 "the API's extracted Form 990 values as shown, not an audit.",
                 "tools/propublica_nonprofits.py")
    return "\n".join(head) + report


# ----------------------------------------------------------------------
# /formd
# ----------------------------------------------------------------------

def formd(query, env=None):
    """SEC EDGAR Form D filings via tools/edgar_formd.py."""
    env = os.environ if env is None else env
    try:
        contact = ef.contact_from(None, env)
    except ValueError:
        raise Unavailable(
            "%s is not set on the server; EDGAR fair access needs the operator's "
            "contact in the User-Agent, so this endpoint fetches nothing until it is set"
            % ef.CONTACT_ENV)
    cik = _single(query, "cik")
    issuer = _single(query, "issuer")
    max_filings = _int(query, "max_filings", 10, minimum=0)
    if (cik is None) == (issuer is None):
        raise BadRequest("give exactly one of cik or issuer")
    try:
        exclusions = ef.parse_exclusions(_many(query, "exclude"))
        if cik is not None:
            ef.cik10(cik)
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    try:
        lines = ef.run(contact, cik=cik, issuer=issuer, max_filings=max_filings, exclusions=exclusions)
    except ef.FetchError as err:
        raise _transport(err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    subject = ("CIK %s" % cik) if cik is not None else issuer
    head = _head("Form D filings: %s" % subject,
                 "Observation only: this report records what the public SEC EDGAR APIs "
                 "returned at the retrieval times stated below; it is a listing of filings "
                 "as indexed, not an analysis of any offering.",
                 "tools/edgar_formd.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /pagespeed
# ----------------------------------------------------------------------

def pagespeed(query, env=None):
    """PageSpeed Insights snapshot via tools/pagespeed_snapshot.py."""
    env = os.environ if env is None else env
    urls = _many(query, "url")
    if not urls:
        raise BadRequest("give at least one url=<page URL> (up to %d)" % ps.MAX_PAGES)
    strategy = _single(query, "strategy", "mobile")
    if strategy not in ps.STRATEGIES:
        raise BadRequest("strategy must be one of %s" % ", ".join(ps.STRATEGIES))
    try:
        pages = []
        for p in urls:
            p = ps.check_url(p)
            if p not in pages:
                pages.append(p)
        if len(pages) > ps.MAX_PAGES:
            raise ValueError("at most %d pages per call, got %d" % (ps.MAX_PAGES, len(pages)))
        exclusions = ps.parse_exclusions(_many(query, "exclude"), pages)
    except ValueError as err:
        raise BadRequest(str(err).replace("--", ""))
    key = env.get(ps.KEY_ENV) or None
    subject = _single(query, "subject") or urllib.parse.urlsplit(pages[0]).netloc
    try:
        captures = {}
        for p in pages:
            captures[p] = ps.fetch(ps.request_url(p, strategy, key), key, ps.recorded_url(p, strategy, bool(key)))
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    lines = ps.render_report(subject, pages, strategy, captures, exclusions)
    head = _head("PageSpeed snapshot: %s" % subject,
                 "Snapshot only: this report records what the public PageSpeed Insights API "
                 "returned for each page at the retrieval time stated below; it is a measurement "
                 "of that moment, not a permanent grade.",
                 "tools/pagespeed_snapshot.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /ofac
# ----------------------------------------------------------------------

def ofac_sdn(query, env=None):
    """OFAC SDN list name check (primary names and aliases) via tools/ofac_sdn_check.py."""
    name = _single(query, "name")
    if not name or ofac.significant(name) < ofac.MIN_QUERY_CHARS:
        raise BadRequest("name is required, with at least %d letters or digits" % ofac.MIN_QUERY_CHARS)
    try:
        sdn = ofac.fetch(ofac.SDN_URL)
        alt = ofac.fetch(ofac.ALT_URL)
        return ofac.render(name, sdn, alt) + "\n"
    except ofac.FetchError as err:
        raise FetchFailed(str(err))


# ----------------------------------------------------------------------
# /domain
# ----------------------------------------------------------------------

def domain(query, env=None):
    """DNS mail and web posture via tools/domain_trust_check.py."""
    name = _single(query, "domain")
    if name is None:
        raise BadRequest("give domain=<a bare domain>, for example domain=example.com")
    try:
        name = dt.check_domain(name)
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = dt.run(name)
    except dt.FetchError as err:
        raise _transport(err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head("Domain trust check: %s" % name,
                 "Observation only: this report records what the Cloudflare DNS over HTTPS API and "
                 "the site itself returned at the retrieval times stated below; it is not a security "
                 "audit or a mail delivery assessment.",
                 "tools/domain_trust_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /vin
# ----------------------------------------------------------------------

def vin(query, env=None):
    """NHTSA vPIC VIN decode via tools/vin_decode.py."""
    try:
        number = vd.check_vin(_single(query, "vin", ""))
        year = vd.check_year(_single(query, "model_year"))
    except ValueError as err:
        raise BadRequest(str(err))
    url = vd.build_url(number, year)
    try:
        retrieved, transcript, body = vd.fetch(url)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    lines = vd.render_section(number, year, url, retrieved, transcript, body)
    head = _head("VIN decode: %s" % number,
                 "Observation only: this report records what the public NHTSA vPIC API "
                 "returned for this VIN at the retrieval time stated below; the values and "
                 "the error codes are vPIC's as shown, not an inspection of the vehicle.",
                 "tools/vin_decode.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /app
# ----------------------------------------------------------------------

def app(query, env=None):
    """App Store apps matching a name via tools/app_lookup_check.py."""
    try:
        term, country, limit = al.check_inputs(_single(query, "name", ""), _single(query, "country", al.DEFAULT_COUNTRY),
                                                _int(query, "limit", al.DEFAULT_LIMIT))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = al.render(term, country, limit, al.fetch(al.search_url(term, country, limit)))
    except al.FetchError as err:
        raise _transport(err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head("App lookup: %s" % term,
                 "Observation only: this report records what the public iTunes Search API returned for "
                 "this search at the retrieval time stated below, in the order returned; it is not a "
                 "review of any app.",
                 "tools/app_lookup_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# Registry and descriptor
# ----------------------------------------------------------------------

ROUTES = {
    "/carrier": carrier,
    "/litigation": litigation,
    "/awards": awards,
    "/nonprofit": nonprofit,
    "/formd": formd,
    "/pagespeed": pagespeed,
    "/ofac": ofac_sdn,
    "/domain": domain,
    "/vin": vin,
    "/app": app,
}

DESCRIPTIONS = {
    "/ofac": {
        "tool": "tools/ofac_sdn_check.py",
        "params": ["name (person or company name; at least %d letters or digits)" % ofac.MIN_QUERY_CHARS],
        "sources": [ofac.SDN_URL, ofac.ALT_URL],
    },
    "/carrier": {
        "tool": "tools/fmcsa_carrier.py",
        "params": ["usdot (or name, not both)", "name (Census File name search)", "subject (optional heading)",
                   "source (optional, repeatable, with usdot: census, safer, li)", "limit (optional, with name, default 50)",
                   "exclude (optional, repeatable, with name, USDOT=reason)"],
        "sources": [fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL],
    },
    "/litigation": {
        "tool": "tools/courtlistener_recap.py",
        "params": ["party (repeatable; the first is the exact name whose results are listed)", "subject (optional heading)",
                   "filed_after (optional, YYYY-MM-DD; default five years before today)", "order_by (optional, default %s)" % cl.DEFAULT_ORDER,
                   "list (optional, default 10)", "docket_details (optional, 1 to fetch each listed docket record)",
                   "exclude (optional, repeatable, DOCKET_ID=reason)"],
        "sources": [cl.SEARCH_URL],
    },
    "/awards": {
        "tool": "tools/usaspending_awards.py",
        "params": ["recipient (or naics, or both)", "naics (repeatable, 2 to 6 digit prefix)", "start and end (optional, together, YYYY-MM-DD)",
                   "page (optional, default 1)", "limit (optional, default 10, maximum 100)",
                   "exclude (optional, repeatable, GENERATED_ID=reason)"],
        "sources": [ua.ENDPOINT],
    },
    "/nonprofit": {
        "tool": "tools/propublica_nonprofits.py",
        "params": ["name (or ein, or both)", "ein (repeatable)", "subject (optional heading)",
                   "exclude (optional, repeatable, with name, EIN=reason)"],
        "sources": [pp.API],
    },
    "/formd": {
        "tool": "tools/edgar_formd.py",
        "params": ["cik (or issuer, not both)", "issuer (EDGAR company search by name)", "max_filings (optional, default 10)",
                   "exclude (optional, repeatable, ACCESSION=reason)"],
        "sources": [ef.SUBMISSIONS_URL, ef.COMPANY_SEARCH_URL],
        "note": "Needs %s set on the server (EDGAR fair access); answers 503 without it." % ef.CONTACT_ENV,
    },
    "/pagespeed": {
        "tool": "tools/pagespeed_snapshot.py",
        "params": ["url (repeatable, up to %d)" % ps.MAX_PAGES, "subject (optional heading)",
                   "strategy (optional: mobile or desktop, default mobile)", "exclude (optional, repeatable, URL=reason)"],
        "sources": [ps.API_URL],
        "note": "Uses %s from the server environment when set; without it the API answers 429 with quota 0 and that transcript is the report." % ps.KEY_ENV,
    },
    "/domain": {
        "tool": "tools/domain_trust_check.py",
        "params": ["domain (a bare domain, e.g. example.com)"],
        "sources": [dt.DOH_URL, "https://<domain>/ (the site itself, redirects not followed, up to %d hops)" % dt.MAX_HOPS],
    },
    "/vin": {
        "tool": "tools/vin_decode.py",
        "params": ["vin (17 characters, or fewer with * for unknown ones)",
                   "model_year (optional, four digits; vPIC recommends sending it)"],
        "sources": [vd.BASE_URL],
    },
    "/app": {
        "tool": "tools/app_lookup_check.py",
        "params": ["name (the app name to search for)", "country (optional, two letter store code, default us)",
                   "limit (optional, 1 to %d, default %d)" % (al.MAX_LIMIT, al.DEFAULT_LIMIT)],
        "sources": [al.SEARCH_URL],
    },
}


def describe():
    """The endpoint table for the GET / descriptor: path, tool, params, sources."""
    out = {}
    for path in ROUTES:
        entry = dict(DESCRIPTIONS[path])
        entry["method"] = "GET"
        out[path] = entry
    return out


def call(path, query, env=None):
    """Run the endpoint for `path` on a parsed query. Raises BadRequest,
    FetchFailed, Unavailable, or a fetcher ValueError (an operator exclusion
    the response does not contain), for the HTTP layer to map."""
    return ROUTES[path](query, env)
