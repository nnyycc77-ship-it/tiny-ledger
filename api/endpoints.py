#!/usr/bin/env python3
"""The remaining fetchers as paid API endpoints (issue #65).

Thirty-three GET endpoints beside GET /recall, each wrapping one merged fetcher in
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
    /github      tools/github_repo_check.py    owner, repo
    /bank        tools/bank_check.py           name
    /geocode     tools/address_geocode_check.py address
    /meta        tools/meta_tag_check.py       url
    /csl         tools/csl_screen.py           name
    /upc         tools/upc_lookup.py           code
    /vin         tools/vin_decode.py           vin
    /fx          tools/exchange_rate_check.py  base, target (amount, date optional)
    /flood       tools/flood_check.py          lat, lon | address
    /safety      tools/safety_file.py          make, model, year
    /fda         tools/fda_recall_check.py     name (field, category, limit optional)
    /epa         tools/epa_screen.py           name, state (city, registry_id optional)
    /oig         tools/oig_screen.py           name
    /trials      tools/clinical_trial_check.py term (limit optional)
    /links       tools/broken_link_check.py    url
    /insider     tools/insider_check.py        cik | issuer (max_filings optional)
    /drug        tools/fda_drug_check.py       name
    /faa         tools/faa_lookup.py           n_number
    /weather     tools/weather_alert_check.py  lat, lon
    /email       tools/email_check.py          address
    /npi         tools/npi_check.py            query (NPI number or provider name)
    /disaster    tools/disaster_history_check.py  state (county, limit optional)
    /wallet      tools/wallet_check.py         address
    /earthquake  tools/earthquake_check.py     lat, lon, radius_km
    /uksanctions tools/uk_sanctions_check.py   name

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

from tools import address_geocode_check as ag  # noqa: E402
from tools import app_lookup_check as al  # noqa: E402
from tools import bank_check as bk  # noqa: E402
from tools import broken_link_check as bl  # noqa: E402
from tools import clinical_trial_check as ct  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import domain_trust_check as dt  # noqa: E402
from tools import earthquake_check as eq  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import epa_screen as epa  # noqa: E402
from tools import exchange_rate_check as fx  # noqa: E402
from tools import fda_drug_check as fd  # noqa: E402
from tools import fda_recall_check as fda  # noqa: E402
from tools import flood_check as fl  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
from tools import insider_check as ins  # noqa: E402
from tools import github_repo_check as gh  # noqa: E402
from tools import csl_screen as cs  # noqa: E402
from tools import disaster_history_check as dh  # noqa: E402
from tools import faa_lookup as faa  # noqa: E402
from tools import meta_tag_check as mt  # noqa: E402
from tools import oig_screen as oig  # noqa: E402
from tools import ofac_sdn_check as ofac  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import safety_file as sf  # noqa: E402
from tools import usaspending_awards as ua  # noqa: E402
from tools import vin_decode as vd  # noqa: E402
from tools import weather_alert_check as wa  # noqa: E402
from tools import wallet_check as wc  # noqa: E402
from tools import email_check as ec  # noqa: E402
from tools import npi_check as npi  # noqa: E402
from tools import upc_lookup as ul  # noqa: E402
from tools import uk_sanctions_check as uks  # noqa: E402

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


def _fetcher_text(lines):
    """The body for a fetcher whose command line strips trailing blank
    lines before printing: flood, FDA recall and OIG each end their line
    list with an empty string and their main writes the join rstripped
    plus one newline. The endpoint serves the fetcher's own Markdown
    byte for byte, so the trailing empty lines are dropped here the
    same way (issue #215)."""
    lines = list(lines)
    while lines and lines[-1] == "":
        lines.pop()
    return _text([], lines)


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
# /github
# ----------------------------------------------------------------------

def github_repo(query, env=None):
    """Keyless GitHub repository check via tools/github_repo_check.py."""
    try:
        owner = gh.check_name(_single(query, "owner", ""), "owner")
        repo = gh.check_name(_single(query, "repo", ""), "repo")
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        capture = gh.fetch(gh.repo_url(owner, repo))
        lines = gh.render(owner, repo, capture)
    except gh.FetchError as err:
        raise FetchFailed(str(err))
    return _text([], lines)


# ----------------------------------------------------------------------
# /bank

def bank(query, env=None):
    """Keyless FDIC BankFind check via tools/bank_check.py."""
    try:
        name = bk.check_name(_single(query, "name", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        capture = bk.fetch(bk.search_url(name))
        lines = bk.render(name, capture)
    except bk.FetchError as err:
        raise FetchFailed(str(err))
    return _text([], lines)


# ----------------------------------------------------------------------
# /meta
# ----------------------------------------------------------------------

def meta_tags(query, env=None):
    """Meta tag check via tools/meta_tag_check.py: the page itself is the source."""
    try:
        url = mt.check_url(_single(query, "url", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = mt.render(url, mt.fetch(url))
    except mt.FetchError as err:
        raise FetchFailed(str(err))
    return _text([], lines)


# ----------------------------------------------------------------------
# /csl
# ----------------------------------------------------------------------

def csl(query, env=None):
    """US Consolidated Screening List screen via tools/csl_screen.py."""
    name = _single(query, "name")
    if not name or cs.significant(name) < cs.MIN_QUERY_CHARS:
        raise BadRequest("name is required, with at least %d letters or digits" % cs.MIN_QUERY_CHARS)
    try:
        return cs.render(name, cs.load()) + "\n"
    except cs.FetchError as err:
        raise FetchFailed(str(err))


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
# /trials
# ----------------------------------------------------------------------

def clinical_trials(query, env=None):
    """Clinical trials matching a term via tools/clinical_trial_check.py."""
    try:
        term, limit = ct.check_inputs(_single(query, "term", ""), _int(query, "limit", ct.DEFAULT_LIMIT))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = ct.render(term, limit, ct.fetch(ct.search_url(term, limit)))
    except ct.FetchError as err:
        raise _transport(err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head("Clinical trial search: %s" % term,
                 "Observation only: this report records what the public ClinicalTrials.gov API v2 returned "
                 "for this search at the retrieval time stated below, in the order returned; trial statuses "
                 "and listings change, and it is not a review of any trial, drug, or sponsor.",
                 "tools/clinical_trial_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /fx
# ----------------------------------------------------------------------

def exchange_rate(query, env=None):
    """Frankfurter exchange rate via tools/exchange_rate_check.py."""
    try:
        base, target, amount, on = fx.check_query(_single(query, "base", ""), _single(query, "target", ""),
                                                  _single(query, "amount"), _single(query, "date"))
    except ValueError as err:
        raise BadRequest(str(err))
    url = fx.build_url(base, target, amount, on)
    try:
        retrieved, transcript, body = fx.fetch(url)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    lines = fx.render_section(base, target, amount, on, url, retrieved, transcript, body)
    head = _head("Exchange rate: %s to %s" % (base, target),
                 "Observation only: this report records what the public Frankfurter API returned at "
                 "the retrieval time stated below; the rate, its date and any converted amount are "
                 "the API's own figures as shown, not a quote to trade at.",
                 "tools/exchange_rate_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /flood
# ----------------------------------------------------------------------

def flood(query, env=None):
    """FEMA NFHL flood zone check for a point or an address via tools/flood_check.py."""
    lat, lon, address = _single(query, "lat"), _single(query, "lon"), _single(query, "address")
    try:
        if address is not None:
            if lat is not None or lon is not None:
                raise ValueError("give lat and lon, or address, not both")
            args = {"address": fl.check_address(address)}
        else:
            if lat is None or lon is None:
                raise ValueError("give lat and lon, or address")
            la, lo = fl.check_point(lat, lon)
            args = {"lat": la, "lon": lo}
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = fl.report(fetcher=fl.fetch, **args)
    except fl.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /email

def email(query, env=None):
    """Keyless email check via tools/email_check.py."""
    try:
        _local, domain = ec.check_address(_single(query, "address", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        captures = [ec.fetch(ec.doh_url(name, rr)) for _label, name, rr in ec.queries(domain)]
        lines = ec.render(_single(query, "address", "").strip(), domain, captures)
    except ec.FetchError as err:
        raise FetchFailed(str(err))
    return _text([], lines)


# ----------------------------------------------------------------------
# /weather
# ----------------------------------------------------------------------

def weather(query, env=None):
    """US National Weather Service active alerts for a point via tools/weather_alert_check.py."""
    lat, lon = _single(query, "lat"), _single(query, "lon")
    try:
        if lat is None or lon is None:
            raise ValueError("give lat and lon")
        la, lo = wa.check_point(lat, lon)
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = wa.report(la, lo, fetcher=wa.fetch)
    except wa.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /npi
# ----------------------------------------------------------------------

def npi_lookup(query, env=None):
    """CMS NPI Registry check for an NPI number or a provider name via tools/npi_check.py."""
    raw = _single(query, "query")
    try:
        if raw is None:
            raise ValueError("give an NPI number (10 digits) or a provider name")
        npi.check_query(raw)
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = npi.report(raw, fetcher=npi.fetch)
    except npi.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /wallet
# ----------------------------------------------------------------------

def wallet(query, env=None):
    """Bitcoin address facts via tools/wallet_check.py."""
    raw = _single(query, "address")
    try:
        if raw is None:
            raise ValueError("give a Bitcoin address")
        address = wc.check_address(raw)
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = wc.report(address, fetcher=wc.fetch)
    except wc.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /earthquake
# ----------------------------------------------------------------------

def earthquake(query, env=None):
    """USGS earthquake catalog check for a circle around a point via tools/earthquake_check.py."""
    lat, lon, radius = _single(query, "lat"), _single(query, "lon"), _single(query, "radius_km")
    try:
        if lat is None or lon is None or radius is None:
            raise ValueError("give lat, lon and radius_km")
        lat, lon = eq.check_point(lat, lon)
        radius = eq.check_radius(radius)
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = eq.report(lat, lon, radius, fetcher=eq.fetch)
    except eq.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /safety
# ----------------------------------------------------------------------

def safety(query, env=None):
    """NHTSA safety file (ratings, recalls, complaints) via tools/safety_file.py."""
    try:
        make, model, year = sf.check_query(_single(query, "make", ""), _single(query, "model", ""),
                                           _single(query, "year", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = sf.render(make, model, year, sf.gather(make, model, year))
    except sf.SourceFailed as err:
        raise FetchFailed("source failure, no report emitted: %s" % err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head("Safety file: %s %s %s" % (year, make, model),
                 "Observation only: this report records what the public NHTSA APIs returned for this "
                 "model year at the retrieval times stated below; ratings, recalls and complaints are "
                 "NHTSA's records as shown, not an inspection or a judgement of any vehicle.",
                 "tools/safety_file.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /fda
# ----------------------------------------------------------------------

def fda_recall(query, env=None):
    """Keyless openFDA food and device enforcement search via tools/fda_recall_check.py."""
    try:
        args = fda.check_inputs(_single(query, "name", ""), _single(query, "field", "product"),
                                _single(query, "category", "both"), _int(query, "limit", fda.DEFAULT_LIMIT))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = fda.report(*args, fetcher=fda.fetch)
    except fda.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /epa
# ----------------------------------------------------------------------

def epa_screen(query, env=None):
    """EPA ECHO facility compliance screen via tools/epa_screen.py."""
    try:
        name, state, city, registry_id = epa.check_query(_single(query, "name", ""), _single(query, "state", ""),
                                                         _single(query, "city"), _single(query, "registry_id"))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = epa.render(name, state, city, registry_id, epa.gather(name, state, city))
    except epa.SourceFailed as err:
        raise FetchFailed("source failure, no report emitted: %s" % err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    head = _head("EPA compliance screen: %s, %s" % (name, state),
                 "Observation only: this report records what the public EPA ECHO facility search returned "
                 "at the retrieval times stated below; the status fields are ECHO's as shown, not a "
                 "compliance finding of this service.",
                 "tools/epa_screen.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /drug
# ----------------------------------------------------------------------

def drug(query, env=None):
    """openFDA drug label check via tools/fda_drug_check.py."""
    try:
        name = fd.check_name(_single(query, "name", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    url = fd.build_url(name)
    try:
        retrieved, transcript, body = fd.fetch(url)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    lines = fd.render_section(name, url, retrieved, transcript, body)
    head = _head("FDA drug label: %s" % name,
                 "Observation only: this report records what the public openFDA drug label "
                 "API returned for this name at the retrieval time stated below; the facts are "
                 "the first returned label record's as shown, and the report is not medical advice.",
                 "tools/fda_drug_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /oig
# ----------------------------------------------------------------------

def oig_exclusions(query, env=None):
    """HHS OIG LEIE exclusion screen via tools/oig_screen.py."""
    name = " ".join(_single(query, "name", "").split())
    if oig.significant(name) < oig.MIN_QUERY_CHARS:
        raise BadRequest("name must have at least %d letters or digits" % oig.MIN_QUERY_CHARS)
    try:
        lines = oig.render(name, oig.fetch(oig.LEIE_URL))
    except oig.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


# ----------------------------------------------------------------------
# /insider
# ----------------------------------------------------------------------

def insider(query, env=None):
    """SEC EDGAR insider activity (Forms 3, 4 and 5) via tools/insider_check.py."""
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
    max_filings = _int(query, "max_filings", ins.DEFAULT_MAX_FILINGS, minimum=1, maximum=ins.MAX_FILINGS)
    if (cik is None) == (issuer is None):
        raise BadRequest("give exactly one of cik or issuer")
    try:
        if cik is not None:
            ef.cik10(cik)
        elif not issuer.strip():
            raise ValueError("issuer name must not be blank")
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = ins.run(contact, cik=cik, issuer=issuer, max_filings=max_filings)
    except ins.FetchError as err:
        raise _transport(err)
    except (urllib.error.URLError, OSError) as err:
        raise _transport(err)
    return _text([], lines)


# ----------------------------------------------------------------------
# /faa
# ----------------------------------------------------------------------

def faa_lookup(query, env=None):
    """FAA aircraft registry lookup by N number via tools/faa_lookup.py."""
    try:
        display, _ = faa.check_n_number(_single(query, "n_number", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = faa.run(display)
    except faa.SourceFailed as err:
        raise FetchFailed("source failure, no report emitted: %s" % err)
    head = _head("Aircraft registration: %s" % display,
                 "Observation only: this report records what the FAA releasable aircraft database download, "
                 "as retrieved at the time stated below, holds for this N number; the registration is a public "
                 "record shown as the record states it.",
                 "tools/faa_lookup.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /disaster
# ----------------------------------------------------------------------

def disaster_history(query, env=None):
    """FEMA disaster declarations for a state or designated area via tools/disaster_history_check.py."""
    try:
        state = dh.check_state(_single(query, "state", ""))
        area = dh.check_area(_single(query, "county"))
        limit = dh.check_limit(_single(query, "limit"))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = dh.run(state, area, limit)
    except dh.SourceFailed as err:
        raise FetchFailed("source failure, no report emitted: %s" % err)
    place = "%s, %s" % (area, state) if area else state
    head = _head("Disaster declarations: %s" % place,
                 "Observation only: this report records what the public OpenFEMA disaster declarations API "
                 "returned at the retrieval time stated below; the declarations are FEMA's records as shown, "
                 "not an assessment of any place.",
                 "tools/disaster_history_check.py")
    return _text(head, lines)


# ----------------------------------------------------------------------
# /uksanctions
# ----------------------------------------------------------------------

def uk_sanctions(query, env=None):
    """UK consolidated sanctions list name check via tools/uk_sanctions_check.py."""
    name = _single(query, "name")
    if not name or uks.ofac.significant(name) < uks.MIN_QUERY_CHARS:
        raise BadRequest("name is required, with at least %d letters or digits" % uks.MIN_QUERY_CHARS)
    try:
        return uks.render(name, uks.fetch(uks.LIST_URL)) + "\n"
    except uks.FetchError as err:
        raise FetchFailed(str(err))


# ----------------------------------------------------------------------
# Registry and descriptor
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# /links
# ----------------------------------------------------------------------

def links(query, env=None):
    """Broken link check for one page via tools/broken_link_check.py."""
    try:
        lines = bl.report_lines(_single(query, "url", ""))
    except bl.FetchError as err:
        raise FetchFailed(str(err))
    except ValueError as err:
        raise BadRequest(str(err))
    return _text([], lines)


# ----------------------------------------------------------------------
# /geocode
# ----------------------------------------------------------------------

def geocode(query, env=None):
    """US address geocode check via tools/address_geocode_check.py."""
    try:
        address = ag.check_address(_single(query, "address", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = ag.report(address, fetcher=ag.fetch)
    except ag.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


def upc_lookup(query, env=None):
    """Open Food Facts product lookup via tools/upc_lookup.py."""
    try:
        code = ul.check_code(_single(query, "code", ""))
    except ValueError as err:
        raise BadRequest(str(err))
    try:
        lines = ul.report(code, fetcher=ul.fetch)
    except ul.FetchError as err:
        raise FetchFailed(str(err))
    return _fetcher_text(lines)


ROUTES = {
    "/carrier": carrier,
    "/litigation": litigation,
    "/awards": awards,
    "/nonprofit": nonprofit,
    "/formd": formd,
    "/pagespeed": pagespeed,
    "/ofac": ofac_sdn,
    "/domain": domain,
    "/upc": upc_lookup,
    "/vin": vin,
    "/github": github_repo,
    "/bank": bank,
    "/geocode": geocode,
    "/meta": meta_tags,
    "/csl": csl,
    "/app": app,
    "/trials": clinical_trials,
    "/fx": exchange_rate,
    "/flood": flood,
    "/safety": safety,
    "/fda": fda_recall,
    "/epa": epa_screen,
    "/oig": oig_exclusions,
    "/links": links,
    "/insider": insider,
    "/drug": drug,
    "/faa": faa_lookup,
    "/weather": weather,
    "/email": email,
    "/npi": npi_lookup,
    "/disaster": disaster_history,
    "/wallet": wallet,
    "/earthquake": earthquake,
    "/uksanctions": uk_sanctions,
}

DESCRIPTIONS = {
    "/insider": {
        "tool": "tools/insider_check.py",
        "params": ["cik (or issuer, not both)", "issuer (EDGAR company search by name)",
                   "max_filings (optional, 1 to %d, default %d)" % (ins.MAX_FILINGS, ins.DEFAULT_MAX_FILINGS)],
        "sources": [ef.SUBMISSIONS_URL, ef.ARCHIVE_URL, ef.COMPANY_SEARCH_URL],
        "note": "Needs %s set on the server (EDGAR fair access); answers 503 without it." % ef.CONTACT_ENV,
    },
    "/oig": {
        "tool": "tools/oig_screen.py",
        "params": ["name (person or entity name; at least %d letters or digits)" % oig.MIN_QUERY_CHARS],
        "sources": [oig.LEIE_URL],
        "note": "Keyless. Reads the complete current LEIE database file on every call; no match is not a clearance.",
    },
    "/fda": {
        "tool": "tools/fda_recall_check.py",
        "params": ["name (product, device or firm name, %d to %d characters)" % (fda.MIN_TERM_CHARS, fda.MAX_TERM_CHARS),
                   "field (optional: product or firm, default product)",
                   "category (optional: food, device or both, default both)",
                   "limit (optional, 1 to %d, default %d)" % (fda.MAX_LIMIT, fda.DEFAULT_LIMIT)],
        "sources": [fda.API_URL.format(category=c) for c in fda.CATEGORIES],
        "note": "Keyless: no api_key is sent. An empty result is openFDA's 404 NOT_FOUND, shown in full; never a clearance.",
    },
    "/earthquake": {
        "tool": "tools/earthquake_check.py",
        "params": ["lat and lon (decimal degrees)",
                   "radius_km (%d to %d kilometres)" % (eq.MIN_RADIUS_KM, eq.MAX_RADIUS_KM)],
        "sources": [eq.COUNT_URL, eq.QUERY_URL],
        "note": "Keyless. Events in the past %d years inside the circle: the count, and the %d largest by "
                "magnitude. No event listed is the catalog's answer, never a hazard clearance." % (eq.YEARS, eq.LARGEST),
    },
    "/flood": {
        "tool": "tools/flood_check.py",
        "params": ["lat and lon (decimal degrees), or address (a US street address)"],
        "sources": [fl.NFHL_URL.format(layer=fl.ZONES["layer"]), fl.NFHL_URL.format(layer=fl.PANELS["layer"]),
                    fl.GEOCODER_URL],
        "note": "Screening only: not a Standard Flood Hazard Determination. Keyless.",
    },
    "/weather": {
        "tool": "tools/weather_alert_check.py",
        "params": ["lat and lon (decimal degrees)"],
        "sources": [wa.ALERTS_URL],
        "note": "Keyless. US and territories coverage; an empty features array proves no active alerts at the retrieval time, never that conditions are safe.",
    },
    "/npi": {
        "tool": "tools/npi_check.py",
        "params": ["query (an NPI number, 10 digits, or a provider name)"],
        "sources": [npi.API_URL],
        "note": "Keyless. A name is read as an individual and as an organization; result_count is paged, never read as a total.",
    },
    "/wallet": {
        "tool": "tools/wallet_check.py",
        "params": ["address (a Bitcoin address)"],
        "sources": [wc.API_URL],
        "note": "Keyless. Public address facts in satoshis; confirmed and unconfirmed figures are reported separately and never added together.",
    },
    "/github": {
        "tool": "tools/github_repo_check.py",
        "params": ["owner (GitHub user or organization)", "repo (repository name)"],
        "sources": [gh.API_URL],
        "note": "Keyless: no Authorization header is sent; GitHub's unauthenticated limit is 60 requests per hour.",
    },
    "/email": {
        "tool": "tools/email_check.py",
        "params": ["address (an email address; the domain part is checked over DNS)"],
        "sources": [ec.DOH_URL],
        "note": "Keyless. Address shape is checked locally; MX, SPF and DMARC are read over DNS over HTTPS.",
    },
    "/bank": {
        "tool": "tools/bank_check.py",
        "params": ["name (the start of the bank's name as FDIC lists it; at least 3 letters or digits)"],
        "sources": [bk.API_URL],
        "note": "Keyless: no api_key parameter is sent. The NAME filter is a prefix match; matches are kept locally under the stated prefix rule.",
    },
    "/geocode": {
        "tool": "tools/address_geocode_check.py",
        "params": ["address (a US street address, 1 to %d characters)" % ag.MAX_ADDRESS_CHARS],
        "sources": [ag.API_URL],
        "note": "Keyless. Benchmark and vintage are pinned; coordinates are interpolated along the "
                "matched address range, not rooftop grade.",
    },
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
    "/meta": {
        "tool": "tools/meta_tag_check.py",
        "params": ["url (the page URL, http or https)"],
        "sources": ["https://<page>/ (the page itself, at the exact URL given by the caller)"],
        "note": "Keyless: the source is the page itself, fetched once. A source failure is 502, never a page with no tags.",
    },
    "/csl": {
        "tool": "tools/csl_screen.py",
        "params": ["name (person or company name; at least %d letters or digits)" % cs.MIN_QUERY_CHARS],
        "sources": [cs.CSL_URL],
        "note": "Keyless: the published list file is downloaded and cached locally for a day; every report states the list publication date and the rows screened.",
    },
    "/app": {
        "tool": "tools/app_lookup_check.py",
        "params": ["name (the app name to search for)", "country (optional, two letter store code, default us)",
                   "limit (optional, 1 to %d, default %d)" % (al.MAX_LIMIT, al.DEFAULT_LIMIT)],
        "sources": [al.SEARCH_URL],
    },
    "/trials": {
        "tool": "tools/clinical_trial_check.py",
        "params": ["term (a company, drug, or condition to search for)",
                   "limit (optional, 1 to %d, default %d)" % (ct.MAX_LIMIT, ct.DEFAULT_LIMIT)],
        "sources": [ct.STUDIES_URL],
        "note": "Keyless: the public ClinicalTrials.gov API v2 needs no key.",
    },
    "/upc": {
        "tool": "tools/upc_lookup.py",
        "params": ["code (a UPC or EAN barcode, 8, 12, 13 or 14 digits with a valid check digit)"],
        "sources": [ul.API_URL],
        "note": ("Keyless: the public Open Food Facts API needs no key. Facts as listed only, "
                 "with no assessment; a barcode the database does not hold is a proven not found "
                 "(its status 0 document, quoted in full), and the returned code is always "
                 "compared to the requested code with leading zeros ignored, because the API "
                 "zero pads UPCs to 13 digits."),
    },
    "/fx": {
        "tool": "tools/exchange_rate_check.py",
        "params": ["base (three letter currency code, e.g. USD)", "target (three letter currency code, e.g. EUR)",
                   "amount (optional, a positive number; the API converts it)",
                   "date (optional, YYYY-MM-DD; default latest)"],
        "sources": [fx.BASE_URL],
    },
    "/links": {
        "tool": "tools/broken_link_check.py",
        "params": ["url (the page URL, http or https)"],
        "sources": ["https://<page url> (the page itself, and each link target on it)"],
        "note": "Keyless. A link is dead on a final status of 400 or above; a request that fails is listed as a check failure, never as dead.",
    },
    "/drug": {
        "tool": "tools/fda_drug_check.py",
        "params": ["name (a drug brand or generic name, e.g. Lipitor)"],
        "sources": [fd.BASE_URL],
        "note": "Keyless. Label facts from the first returned record only; the report states the total matches the response reports. Not medical advice.",
    },
    "/safety": {
        "tool": "tools/safety_file.py",
        "params": ["make (e.g. Hyundai)", "model (e.g. Elantra)", "year (model year, four digits)"],
        "sources": [sf.BASE_URL + "SafetyRatings/modelyear/<year>/make/<make>/model/<model>",
                    sf.BASE_URL + "SafetyRatings/VehicleId/<id>",
                    sf.BASE_URL + "recalls/recallsByVehicle?make=<make>&model=<model>&modelYear=<year>",
                    sf.BASE_URL + "complaints/complaintsByVehicle?make=<make>&model=<model>&modelYear=<year>"],
        "note": "Any source answering other than HTTP 200 is a source failure (502, no report), never an empty result.",
    },
    "/epa": {
        "tool": "tools/epa_screen.py",
        "params": ["name (facility name to search for)", "state (two letter code)", "city (optional)",
                   "registry_id (optional: selects that row from the search results)"],
        "sources": [epa.BASE_URL + "get_facilities?output=JSON&p_fn=<name>&p_cty=<city>&p_st=<state>",
                    epa.BASE_URL + "get_qid?output=JSON&qid=<QueryID>"],
        "note": "Any non-200 answer or an Error in Results is a source failure (502, no report); QueryRows 0 is "
                "an empty result, never a finding that a facility is free of violations.",
    },
    "/faa": {
        "tool": "tools/faa_lookup.py",
        "params": ["n_number (the N number, e.g. N100ZT)"],
        "sources": [faa.ARCHIVE_URL],
        "note": "Answers from the FAA archive downloaded at most once per UTC day into the server's cache; every "
                "reply states the archive Last-Modified. A non-200 answer, a redirect, or an archive not in the "
                "captured shape is a source failure (502, no report), never a no match.",
    },
    "/disaster": {
        "tool": "tools/disaster_history_check.py",
        "params": ["state (two letter code as FEMA records it)",
                   "county (optional: the exact designatedArea, e.g. 'Kent (County)')",
                   "limit (optional: rows to ask for, 1 to %d, default %d)" % (dh.MAX_LIMIT, dh.DEFAULT_LIMIT)],
        "sources": [dh.BASE_URL + "?$filter=state eq '<state>'[ and designatedArea eq '<county>']"
                    "&$orderby=declarationDate desc&$top=<limit>&$count=true"],
        "note": "Distinct disasterNumber values are listed, since one disaster appears once per designated area. "
                "Any non-200 answer, a failed fetch or an unreadable body is a source failure (502, no report); "
                "an empty result is reported only for the exact filter sent, never as no disasters.",
    },
    "/uksanctions": {
        "tool": "tools/uk_sanctions_check.py",
        "params": ["name (person or company name; at least %d letters or digits)" % uks.MIN_QUERY_CHARS],
        "sources": [uks.LIST_URL],
        "note": "Keyless: one public CSV file read per call and matched locally under the OFAC tool's rule. A no match "
                "is proven by the file's bytes, SHA-256, record count and list date line; a failed fetch or a file "
                "not in the captured shape is a source failure (502, no report).",
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
