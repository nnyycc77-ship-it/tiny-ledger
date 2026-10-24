#!/usr/bin/env python3
"""Recall check MCP server core (B1 of issue #33), plus the carrier
vetting and litigation screen tools (issue #67), the Form D,
nonprofit, awards and PageSpeed tools (issue #97), and the tool
factory wave tools (issue #204).

A Model Context Protocol server, stdio transport, that exposes
twenty four tools wrapping merged fetchers in tools/ through the same
host-free dispatchers the pay per call API uses (api/recall_api.py and
api/endpoints.py):

    recall_check       CPSC SaferProducts (product) or NHTSA recalls
                       (make, model, year); the GET /recall dispatcher
    carrier_check      FMCSA carrier records via tools/fmcsa_carrier.py
                       (usdot or name); the GET /carrier dispatcher
    litigation_screen  CourtListener RECAP docket search via
                       tools/courtlistener_recap.py (party variants);
                       the GET /litigation dispatcher
    formd_check        SEC EDGAR Form D filings via tools/edgar_formd.py
                       (cik or issuer); the GET /formd dispatcher
    nonprofit_check    ProPublica Nonprofit Explorer via
                       tools/propublica_nonprofits.py (name and/or ein);
                       the GET /nonprofit dispatcher
    awards_search      USAspending prime contract awards via
                       tools/usaspending_awards.py (recipient or naics);
                       the GET /awards dispatcher
    pagespeed_snapshot PageSpeed Insights via tools/pagespeed_snapshot.py
                       (url, up to 5); the GET /pagespeed dispatcher
    domain_trust_check DNS records, SPF, DMARC and the HTTPS hop chain
                       via tools/domain_trust_check.py (domain);
                       the GET /domain dispatcher
    ofac_sanctions_check OFAC SDN list name check via
                       tools/ofac_sdn_check.py (name); the GET /ofac
                       dispatcher
    vin_decode_check   NHTSA vPIC VIN decode via tools/vin_decode.py
                       (vin, optional model_year); the GET /vin
                       dispatcher
    clinical_trial_check ClinicalTrials.gov study search via
                       tools/clinical_trial_check.py (term, optional
                       limit); the GET /trials dispatcher
    fda_drug_check     openFDA drug label facts via
                       tools/fda_drug_check.py (name); the GET /drug
                       dispatcher
    broken_link_check  one page's link targets via
                       tools/broken_link_check.py (url); the GET /links
                       dispatcher
    meta_tag_check     one page's meta tags via
                       tools/meta_tag_check.py (url); the GET /meta
                       dispatcher
    github_repo_check  GitHub repository facts via
                       tools/github_repo_check.py (owner, repo);
                       the GET /github dispatcher
    app_lookup_check   Apple App Store lookup via
                       tools/app_lookup_check.py (name, optional
                       country and limit); the GET /app dispatcher
    exchange_rate_check Frankfurter exchange rate via
                       tools/exchange_rate_check.py (base, target,
                       optional amount and date); the GET /fx dispatcher
    flood_check        FEMA flood zone screen via tools/flood_check.py
                       (lat and lon, or address); the GET /flood
                       dispatcher
    safety_file        NHTSA ratings, recalls and complaints via
                       tools/safety_file.py (make, model, year);
                       the GET /safety dispatcher
    fda_recall_check   openFDA enforcement recall search via
                       tools/fda_recall_check.py (name, optional field,
                       category and limit); the GET /fda dispatcher
    epa_screen         EPA ECHO facility compliance via
                       tools/epa_screen.py (name, state, optional city
                       and registry_id); the GET /epa dispatcher
    csl_screen         Consolidated Screening List name screen via
                       tools/csl_screen.py (name); the GET /csl
                       dispatcher
    oig_screen         HHS OIG LEIE exclusion screen via
                       tools/oig_screen.py (name); the GET /oig
                       dispatcher
    insider_check      SEC EDGAR insider filing listing via
                       tools/insider_check.py (cik or issuer, optional
                       max_filings); the GET /insider dispatcher

Each call returns the check as Markdown in the fixed delivery format
from AGENT-BRIEF.md: the claim lines, the exact query, the UTC
retrieval time, the source link, and the complete raw response directly
beneath the link. The text is the fetchers' own output, byte for byte
the same as the API returns for the same query; this server adds
nothing to it.

Fail closed: a failed fetch, a response the fetcher cannot read, or a
bad request is returned as a tool error (isError true) carrying only the
error message, never as an empty result or a partial report.

Protocol: JSON-RPC 2.0, one message per line on stdin and stdout, as the
MCP stdio transport specifies. Methods served: initialize, ping,
tools/list, tools/call; the notifications/initialized and
notifications/cancelled notifications are accepted and answered with
nothing, as notifications must be. Anything else is answered with the
JSON-RPC "method not found" error. Diagnostics go to stderr only; stdout
carries protocol messages and nothing else.

Configuration comes from the environment, nothing is hard coded, and no
hosting platform is assumed:

    PAYOUT_WALLET_ADDRESS   optional; the EVM address that receives USDC
                            per call. Read through api.recall_api, which
                            refuses a malformed value. When set it is
                            stated in the initialize instructions and
                            in the recall_check tool description, the
                            one tool with a recorded price. Never
                            written to a file here.
    COURTLISTENER_TOKEN     optional; read by tools/courtlistener_recap.py
                            at call time for litigation_screen and sent
                            as the Authorization header. Never printed.
    EDGAR_CONTACT           required for formd_check and insider_check
                            by SEC EDGAR fair access: the operator's
                            "Name address" contact for the User-Agent.
                            While it is unset, both tools answer a tool
                            error and fetch nothing. Never printed.
    PAGESPEED_API_KEY       optional; read at call time for
                            pagespeed_snapshot. Without it the API answers
                            429 with quota 0 and that transcript is the
                            report. The key is never printed; the recorded
                            request URL shows a redaction marker.

Run:

    python3 -m mcp_server            # from the repository root

Part 2 of the split (issue #38) attaches platform packaging around this
entry point; the core does not change for it. Standard library only.
The CPSC fetcher shells out to the system curl executable, so a host
needs curl on PATH (see tools/README.md).
"""

import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import endpoints, recall_api  # noqa: E402
from tools import app_lookup_check as al  # noqa: E402
from tools import broken_link_check as bl  # noqa: E402
from tools import clinical_trial_check as ct  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import cpsc_recalls  # noqa: E402
from tools import csl_screen as cs  # noqa: E402
from tools import domain_trust_check as dt  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import epa_screen as es  # noqa: E402
from tools import exchange_rate_check as fx  # noqa: E402
from tools import fda_drug_check as fd  # noqa: E402
from tools import fda_recall_check as fr  # noqa: E402
from tools import flood_check as fl  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
from tools import github_repo_check as gh  # noqa: E402
from tools import insider_check as ic  # noqa: E402
from tools import ofac_sdn_check as ofac  # noqa: E402
from tools import oig_screen as oig  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import safety_file as sf  # noqa: E402
from tools import usaspending_awards as ua  # noqa: E402
from tools import vin_decode as vd  # noqa: E402

SERVER_NAME = "hojo-recall-check"
SERVER_VERSION = "0.3.0"
# Protocol revisions this server knows. The client's requested version is
# echoed when it is one of these; otherwise the newest known is offered,
# as the MCP version negotiation rule says.
PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
TOOL_NAME = "recall_check"
CARRIER_TOOL = "carrier_check"
LITIGATION_TOOL = "litigation_screen"
FORMD_TOOL = "formd_check"
NONPROFIT_TOOL = "nonprofit_check"
AWARDS_TOOL = "awards_search"
PAGESPEED_TOOL = "pagespeed_snapshot"
DOMAIN_TOOL = "domain_trust_check"
OFAC_TOOL = "ofac_sanctions_check"
VIN_TOOL = "vin_decode_check"
TRIALS_TOOL = "clinical_trial_check"
DRUG_TOOL = "fda_drug_check"
LINKS_TOOL = "broken_link_check"
META_TOOL = "meta_tag_check"
GITHUB_TOOL = "github_repo_check"
APP_TOOL = "app_lookup_check"
FX_TOOL = "exchange_rate_check"
FLOOD_TOOL = "flood_check"
SAFETY_TOOL = "safety_file"
FDA_TOOL = "fda_recall_check"
EPA_TOOL = "epa_screen"
CSL_TOOL = "csl_screen"
OIG_TOOL = "oig_screen"
INSIDER_TOOL = "insider_check"
TOOL_NAMES = (TOOL_NAME, CARRIER_TOOL, LITIGATION_TOOL, FORMD_TOOL, NONPROFIT_TOOL, AWARDS_TOOL,
              PAGESPEED_TOOL, DOMAIN_TOOL, OFAC_TOOL, VIN_TOOL, TRIALS_TOOL, DRUG_TOOL, LINKS_TOOL,
              META_TOOL, GITHUB_TOOL, APP_TOOL, FX_TOOL, FLOOD_TOOL, SAFETY_TOOL, FDA_TOOL,
              EPA_TOOL, CSL_TOOL, OIG_TOOL, INSIDER_TOOL)

JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602


# ----------------------------------------------------------------------
# Tool definition
# ----------------------------------------------------------------------

def tool_description(wallet):
    text = (
        "Sourced recall check from public United States recall records, in the "
        "fixed evidence format: each claim with its source link and the raw "
        "excerpt directly beneath it, the exact query and UTC retrieval time "
        "recorded, and an empty result proven by the complete raw response. "
        "Product form: `product` searches the CPSC SaferProducts recall API "
        "(%s); optional `exact_name` marks records whose product names do not "
        "equal it as checked and excluded, and `near` (needs `exact_name`) adds "
        "broader searches checked the same way. Vehicle form: `make`, `model` "
        "and `year` search the NHTSA recalls API (%s); optional `exclude` "
        "entries of the form CAMPAIGN=reason list a returned campaign as "
        "checked and excluded with the operator's reason. Give one form, not "
        "both. The response is the fetchers' own Markdown; nothing is "
        "summarised, estimated, or added. An empty result is not a safety "
        "clearance. A failed fetch is an error, never an empty result."
        % (cpsc_recalls.ENDPOINT, recall_api.nhtsa_recalls.BASE_URL + recall_api.nhtsa_recalls.DEFAULT_ENDPOINT)
    )
    if wallet:
        text += " Payment: USDC per call to %s, collected by the platform that lists this server, not by the server." % wallet
    return text


def tool_definition(wallet):
    return {
        "name": TOOL_NAME,
        "description": tool_description(wallet),
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Product name for the CPSC SaferProducts search (product form)."},
                "exact_name": {"type": "string", "description": "Product form, optional: records whose product names do not equal this are listed as checked and excluded."},
                "near": {"type": "array", "items": {"type": "string"}, "description": "Product form, optional, needs exact_name: broader product searches to run and check the same way."},
                "make": {"type": "string", "description": "Vehicle make (vehicle form)."},
                "model": {"type": "string", "description": "Vehicle model (vehicle form)."},
                "year": {"type": "string", "description": "Vehicle model year (vehicle form)."},
                "exclude": {"type": "array", "items": {"type": "string"}, "description": "Vehicle form, optional: CAMPAIGN=reason entries listing a returned NHTSA campaign as checked and excluded, with the operator's reason."},
            },
            "additionalProperties": False,
        },
    }


def carrier_tool_definition():
    """carrier_check: tools/fmcsa_carrier.py through api.endpoints.carrier,
    the GET /carrier dispatcher. Arguments are that fetcher's own command
    line inputs; the output is its rendered Markdown."""
    return {
        "name": CARRIER_TOOL,
        "description": (
            "Sourced FMCSA carrier vetting from public United States motor carrier "
            "records, in the fixed evidence format: each claim with its source link "
            "and the raw response directly beneath it, the exact query and UTC "
            "retrieval time recorded, and an empty result proven by the complete raw "
            "response. USDOT form: `usdot` fetches the carrier's record from the FMCSA "
            "Company Census File on DOT open data (%s), the SAFER company snapshot "
            "(%s) and the Licensing and Insurance carrier list (%s); optional `source` "
            "limits the run to some of census, safer, li, in the order given. Name "
            "form: `name` runs a Census name search (`limit` rows, default 50); "
            "optional `exclude` entries of the form USDOT=reason list a returned "
            "carrier as checked and excluded with the operator's reason, and an "
            "exclusion naming a carrier the response does not contain is refused. "
            "Give one form, not both. Optional `subject` is the heading. The response "
            "is the fetcher's own Markdown, the same text GET /carrier of the pay per "
            "call API returns for the same query; nothing is summarised, estimated, or "
            "added. An empty result is not a clearance. A failed fetch is an error, "
            "never an empty result."
            % (fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "usdot": {"type": "string", "description": "USDOT number (USDOT form)."},
                "name": {"type": "string", "description": "Carrier legal name to search in the Census File (name form)."},
                "subject": {"type": "string", "description": "Optional heading; defaults to the carrier's legal name or the USDOT number."},
                "source": {"type": "array", "items": {"type": "string", "enum": list(fc.ALL_SOURCES)},
                           "description": "USDOT form, optional: which sources to fetch, in order (census, safer, li); default all three."},
                "limit": {"type": "integer", "minimum": 1, "description": "Name form, optional: Census name search row limit; default 50."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Name form, optional: USDOT=reason entries listing a returned carrier as checked and excluded, with the operator's reason."},
            },
            "additionalProperties": False,
        },
    }


def litigation_tool_definition():
    """litigation_screen: tools/courtlistener_recap.py through
    api.endpoints.litigation, the GET /litigation dispatcher."""
    return {
        "name": LITIGATION_TOOL,
        "description": (
            "Sourced federal litigation screen from the public CourtListener RECAP "
            "docket index (%s), in the fixed evidence format: each claim with its "
            "source link and the raw response directly beneath it, the exact query "
            "and UTC retrieval time recorded, and an empty result proven by the "
            "complete raw response. `party` lists the party name variants to search "
            "as party:(\"variant\") docket queries; the first is the exact name whose "
            "first page results are listed (`list` rows, default 10), the others are "
            "counted. Optional `filed_after` (YYYY-MM-DD, default five years before "
            "today) and `order_by` (default %s) set the window and order; "
            "`docket_details` true also fetches each listed docket's record; "
            "`exclude` entries of the form DOCKET_ID=reason list a returned docket as "
            "checked and excluded with the operator's reason, and an exclusion naming "
            "a docket the response does not contain is refused. Optional `subject` is "
            "the heading. %s The response is the fetcher's own Markdown, the same "
            "text GET /litigation of the pay per call API returns for the same query; "
            "nothing is summarised, estimated, or added. An empty result is not proof "
            "of no litigation. A failed fetch is an error, never an empty result."
            % (cl.SEARCH_URL, cl.DEFAULT_ORDER, cl.SCOPE_LINE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "party": {"type": "array", "items": {"type": "string"}, "minItems": 1,
                          "description": "Party name variants; the first is the exact name whose results are listed."},
                "subject": {"type": "string", "description": "Optional heading; defaults to the first party variant."},
                "filed_after": {"type": "string", "description": "Optional YYYY-MM-DD lower bound on the filing date; default five years before today."},
                "order_by": {"type": "string", "description": "Optional CourtListener order_by value; default '%s'." % cl.DEFAULT_ORDER},
                "list": {"type": "integer", "minimum": 0, "description": "Optional: how many first page results of the first variant to list; default 10."},
                "docket_details": {"type": "boolean", "description": "Optional: also fetch and print each listed docket's record; default false."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Optional: DOCKET_ID=reason entries listing a returned docket as checked and excluded, with the operator's reason."},
            },
            "required": ["party"],
            "additionalProperties": False,
        },
    }


FORMAT_SENTENCE = ("in the fixed evidence format: each claim with its source link and the raw response "
                   "directly beneath it, the exact query and UTC retrieval time recorded, and an empty "
                   "result proven by the complete raw response")
SAME_TEXT = ("The response is the fetcher's own Markdown, the same text %s of the pay per call API "
             "returns for the same query; nothing is summarised, estimated, or added.")
FAIL_SENTENCE = "A failed fetch is an error, never an empty result."


def formd_tool_definition():
    """formd_check: tools/edgar_formd.py through api.endpoints.formd."""
    return {
        "name": FORMD_TOOL,
        "description": (
            "Sourced SEC EDGAR Form D filing listing for a company, %s. Give `cik` (the company's "
            "Central Index Key, fetched from the EDGAR submissions API, %s) or `issuer` (an EDGAR "
            "company name search, %s), not both. Optional `max_filings` (default 10) limits how "
            "many Form D filings are read; optional `exclude` entries of the form ACCESSION=reason "
            "list a filing as checked and excluded with the operator's reason, and an exclusion "
            "naming a filing the response does not contain is refused. The server must have %s "
            "set (EDGAR fair access needs the operator's contact in the User-Agent); while it is "
            "unset the tool answers an error and fetches nothing. A listing of filings as indexed, "
            "not an analysis of any offering. %s %s"
            % (FORMAT_SENTENCE, ef.SUBMISSIONS_URL, ef.COMPANY_SEARCH_URL, ef.CONTACT_ENV,
               SAME_TEXT % "GET /formd", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cik": {"type": "string", "description": "Central Index Key, digits (cik form)."},
                "issuer": {"type": "string", "description": "Company name for the EDGAR company search (issuer form)."},
                "max_filings": {"type": "integer", "minimum": 0, "description": "Optional: how many Form D filings to read; default 10."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Optional: ACCESSION=reason entries listing a returned filing as checked and excluded, with the operator's reason."},
            },
            "additionalProperties": False,
        },
    }


def nonprofit_tool_definition():
    """nonprofit_check: tools/propublica_nonprofits.py through api.endpoints.nonprofit."""
    return {
        "name": NONPROFIT_TOOL,
        "description": (
            "Sourced nonprofit diligence from the ProPublica Nonprofit Explorer API (%s), %s. Give "
            "`name` (an organization search), `ein` (one or more EINs, each organization's record "
            "and Form 990 figures as the API extracts them), or both. Optional `subject` is the "
            "heading; optional `exclude` entries of the form EIN=reason (with `name`) list a "
            "search result as checked and excluded with the operator's reason, and an exclusion "
            "naming an organization the search did not return is refused. The figures are the "
            "API's extracted Form 990 values as shown, not an audit. %s %s"
            % (pp.API, FORMAT_SENTENCE, SAME_TEXT % "GET /nonprofit", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Organization name to search."},
                "ein": {"type": "array", "items": {"type": "string"}, "description": "EINs to look up, with or without the dash."},
                "subject": {"type": "string", "description": "Optional heading; defaults to the name or the EINs."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Optional, with name: EIN=reason entries listing a search result as checked and excluded, with the operator's reason."},
            },
            "additionalProperties": False,
        },
    }


def awards_tool_definition():
    """awards_search: tools/usaspending_awards.py through api.endpoints.awards."""
    return {
        "name": AWARDS_TOOL,
        "description": (
            "Sourced federal prime contract award search from the USAspending API (%s), %s. Give "
            "`recipient` (a recipient name) or `naics` (one or more NAICS codes). Optional `start` "
            "and `end` (YYYY-MM-DD, given together) set the action date window; `page` and "
            "`limit` page through the results; `exclude` entries of the form GENERATED_ID=reason "
            "list an award on the page as checked and excluded with the operator's reason, and an "
            "exclusion naming an award not on the page is refused. One page of results as "
            "returned; Award Amount is the API field as returned, not a payment or revenue "
            "estimate. %s %s"
            % (ua.ENDPOINT, FORMAT_SENTENCE, SAME_TEXT % "GET /awards", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Recipient name to search (recipient form)."},
                "naics": {"type": "array", "items": {"type": "string"}, "description": "NAICS codes to search (naics form)."},
                "start": {"type": "string", "description": "Optional YYYY-MM-DD start of the action date window; needs end."},
                "end": {"type": "string", "description": "Optional YYYY-MM-DD end of the action date window; needs start."},
                "page": {"type": "integer", "minimum": 1, "description": "Optional result page; default 1."},
                "limit": {"type": "integer", "minimum": 1, "description": "Optional results per page; default 10."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Optional: GENERATED_ID=reason entries listing an award on the page as checked and excluded, with the operator's reason."},
            },
            "additionalProperties": False,
        },
    }


def pagespeed_tool_definition():
    """pagespeed_snapshot: tools/pagespeed_snapshot.py through api.endpoints.pagespeed."""
    return {
        "name": PAGESPEED_TOOL,
        "description": (
            "Sourced PageSpeed Insights snapshot from the public API (%s), %s. `url` lists the pages "
            "to measure (up to %d); optional `strategy` is mobile (default) or desktop; optional "
            "`subject` is the heading; optional `exclude` entries of the form URL=reason list a "
            "page as checked and excluded with the operator's reason. The server uses %s when set; "
            "without it the API answers 429 with quota 0 and that transcript is the report. The key "
            "is never printed. A measurement of that moment, not a permanent grade. %s %s"
            % (ps.API_URL, FORMAT_SENTENCE, ps.MAX_PAGES, ps.KEY_ENV, SAME_TEXT % "GET /pagespeed", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": ps.MAX_PAGES,
                        "description": "Page URLs to measure, http or https."},
                "strategy": {"type": "string", "enum": list(ps.STRATEGIES), "description": "Optional: mobile (default) or desktop."},
                "subject": {"type": "string", "description": "Optional heading; defaults to the first page's host."},
                "exclude": {"type": "array", "items": {"type": "string"},
                            "description": "Optional: URL=reason entries listing a page as checked and excluded, with the operator's reason."},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    }


def domain_tool_definition():
    """domain_trust_check: tools/domain_trust_check.py through api.endpoints.domain."""
    return {
        "name": DOMAIN_TOOL,
        "description": (
            "Sourced domain trust check from the Cloudflare DNS over HTTPS API (%s) and the "
            "site itself, %s. Give `domain` (a bare domain, e.g. example.com). The report shows "
            "its A and MX records, its SPF record and ending policy, its DMARC record and "
            "policy, and the outcome of requesting the site over HTTPS with redirects not "
            "followed, up to %d hops, each hop its own source. A name that does not exist, and "
            "a record type with no answer section, are empty results, proven by the transcript. "
            "No certificate check is made, and the SPF and DMARC readings are the record's own "
            "text as shown, not a deliverability verdict. %s %s"
            % (dt.DOH_URL, FORMAT_SENTENCE, dt.MAX_HOPS, SAME_TEXT % "GET /domain", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Bare domain to check, e.g. example.com."},
            },
            "required": ["domain"],
            "additionalProperties": False,
        },
    }


def ofac_tool_definition():
    """ofac_sanctions_check: tools/ofac_sdn_check.py through api.endpoints.ofac_sdn."""
    return {
        "name": OFAC_TOOL,
        "description": (
            "Sourced OFAC sanctions list name check from the Treasury sanctions list service "
            "exports, the SDN list (%s) and its aliases (%s), %s. Give `name` (a person or "
            "company name, at least %d letters or digits). Matches are the list's own records "
            "as shown, with the list's programs, types and remarks; the search folds case and "
            "accents and matches whole words, so a near name is not a match. A name with no "
            "match is an empty result, proven by the counts, not a clearance. %s %s"
            % (ofac.SDN_URL, ofac.ALT_URL, FORMAT_SENTENCE, ofac.MIN_QUERY_CHARS,
               SAME_TEXT % "GET /ofac", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person or company name to check against the SDN list and its aliases."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def vin_tool_definition():
    """vin_decode_check: tools/vin_decode.py through api.endpoints.vin."""
    return {
        "name": VIN_TOOL,
        "description": (
            "Sourced VIN decode from the NHTSA vPIC DecodeVinValues API (%s), %s. Give `vin` "
            "(17 characters, or fewer with * standing for unknown characters); optional "
            "`model_year` (four digits) is sent with the query, as vPIC recommends. The "
            "decoded values, and vPIC's own error text and error codes where it gives them, "
            "are NHTSA's as shown. A decode describes the vehicle as manufactured, not its "
            "current condition. %s %s"
            % (vd.BASE_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /vin", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "vin": {"type": "string", "description": "Vehicle identification number, 17 characters or fewer with * for unknown ones."},
                "model_year": {"type": "string", "description": "Optional model year, four digits, sent with the query as vPIC recommends."},
            },
            "required": ["vin"],
            "additionalProperties": False,
        },
    }


def trials_tool_definition():
    """clinical_trial_check: tools/clinical_trial_check.py through api.endpoints.clinical_trials."""
    return {
        "name": TRIALS_TOOL,
        "description": (
            "Sourced clinical trial search from the ClinicalTrials.gov API v2 studies search "
            "(%s), %s. Give `term` (a company, drug, or condition to search for); optional "
            "`limit` (1 to %d, default %d) sets how many trials are asked for. The report shows "
            "the totalCount exactly as shown in the response and the trials in the response, in "
            "response order, each with its NCT number, title, status, lead sponsor, conditions "
            "and phases as shown. A listing of trials as indexed, not medical advice. %s %s"
            % (ct.STUDIES_URL, FORMAT_SENTENCE, ct.MAX_LIMIT, ct.DEFAULT_LIMIT,
               SAME_TEXT % "GET /trials", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "A company, drug, or condition to search for."},
                "limit": {"type": "integer", "minimum": 1, "maximum": ct.MAX_LIMIT,
                          "description": "Optional: how many trials to ask for; default %d." % ct.DEFAULT_LIMIT},
            },
            "required": ["term"],
            "additionalProperties": False,
        },
    }


def drug_tool_definition():
    """fda_drug_check: tools/fda_drug_check.py through api.endpoints.drug."""
    return {
        "name": DRUG_TOOL,
        "description": (
            "Sourced drug label facts from the openFDA drug label API (%s), %s. Give `name` (a "
            "drug brand or generic name, e.g. Lipitor, up to %d characters). Label facts are "
            "read from the first returned record only, and the report states the total matches "
            "the response reports. The label text is the FDA label as published; not medical "
            "advice. %s %s"
            % (fd.BASE_URL, FORMAT_SENTENCE, fd.MAX_NAME_CHARS, SAME_TEXT % "GET /drug", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Drug brand or generic name, e.g. Lipitor."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def links_tool_definition():
    """broken_link_check: tools/broken_link_check.py through api.endpoints.links."""
    return {
        "name": LINKS_TOOL,
        "description": (
            "Sourced broken link check of one page, %s. Give `url` (the page URL, http or "
            "https). The page is fetched once and every unique link target found on it is "
            "checked once, up to %d; a link is dead on a final status of 400 or above after "
            "redirects, and a request that fails is listed as a check failure, never as dead. "
            "Observation only: the report records what the page and each link target answered "
            "at the retrieval time. %s %s"
            % (FORMAT_SENTENCE, bl.MAX_LINKS, SAME_TEXT % "GET /links", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Page URL to check, http or https."},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    }


def meta_tool_definition():
    """meta_tag_check: tools/meta_tag_check.py through api.endpoints.meta_tags."""
    return {
        "name": META_TOOL,
        "description": (
            "Sourced meta tag check of one page, %s. Give `url` (the page URL, http or https). "
            "The page is fetched once, at the exact URL given, and the report states which of "
            "the title, the meta description and the standard Open Graph tags are present with "
            "their values as shown, and which are missing, never assumed. %s %s"
            % (FORMAT_SENTENCE, SAME_TEXT % "GET /meta", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Page URL to check, http or https."},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    }


def github_tool_definition():
    """github_repo_check: tools/github_repo_check.py through api.endpoints.github_repo."""
    return {
        "name": GITHUB_TOOL,
        "description": (
            "Sourced GitHub repository check from GitHub's public REST API (%s), %s. Give "
            "`owner` (a GitHub user or organization name) and `repo` (a repository name). The "
            "report shows the star count, the license, the last push date and whether the "
            "repository is archived, each exactly as shown. The call is keyless: no "
            "Authorization header is sent, and GitHub's unauthenticated limit is 60 requests "
            "per hour. %s %s"
            % (gh.API_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /github", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub user or organization name."},
                "repo": {"type": "string", "description": "Repository name."},
            },
            "required": ["owner", "repo"],
            "additionalProperties": False,
        },
    }


def app_tool_definition():
    """app_lookup_check: tools/app_lookup_check.py through api.endpoints.app."""
    return {
        "name": APP_TOOL,
        "description": (
            "Sourced App Store lookup from the public iTunes Search API (%s), %s. Give `name` "
            "(an app name to search for); optional `country` (two letter store code, default "
            "%s) and `limit` (1 to %d, default %d) set the store and how many results are "
            "asked for. Per app the seller, the average rating and rating count, and the store "
            "link, as shown, and whether the app's name matches the searched name exactly. "
            "The search matches loosely, so zero exact matches is reported in those terms, "
            "never as proof no such app exists. %s %s"
            % (al.SEARCH_URL, FORMAT_SENTENCE, al.DEFAULT_COUNTRY, al.MAX_LIMIT, al.DEFAULT_LIMIT,
               SAME_TEXT % "GET /app", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "App name to search for."},
                "country": {"type": "string", "description": "Optional two letter store code; default %s." % al.DEFAULT_COUNTRY},
                "limit": {"type": "integer", "minimum": 1, "maximum": al.MAX_LIMIT,
                          "description": "Optional: how many results to ask for; default %d." % al.DEFAULT_LIMIT},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def fx_tool_definition():
    """exchange_rate_check: tools/exchange_rate_check.py through api.endpoints.exchange_rate."""
    return {
        "name": FX_TOOL,
        "description": (
            "Sourced exchange rate from the public Frankfurter API (%s), %s. Give `base` and "
            "`target` (three letter currency codes, e.g. USD and EUR); optional `amount` (a "
            "positive number, as text) is converted by the API, and optional `date` "
            "(YYYY-MM-DD) asks for that date instead of the latest. The rate, its date and "
            "any converted amount are the API's own figures as shown, not a quote to trade "
            "at. %s %s"
            % (fx.BASE_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /fx", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "Base currency code, three letters, e.g. USD."},
                "target": {"type": "string", "description": "Target currency code, three letters, e.g. EUR."},
                "amount": {"type": "string", "description": "Optional positive amount, as text, for the API to convert."},
                "date": {"type": "string", "description": "Optional YYYY-MM-DD date; default latest."},
            },
            "required": ["base", "target"],
            "additionalProperties": False,
        },
    }


def flood_tool_definition():
    """flood_check: tools/flood_check.py through api.endpoints.flood."""
    return {
        "name": FLOOD_TOOL,
        "description": (
            "Sourced FEMA flood zone screen from the National Flood Hazard Layer (%s), with "
            "address lookup through the Census Geocoder (%s), %s. Give `lat` and `lon` "
            "(decimal degrees, as text), or `address` (a US street address), not both. The "
            "report shows the flood zone, panel and map dates for the point exactly as the "
            "layer answers. Screening only: this is not a Standard Flood Hazard "
            "Determination. %s %s"
            % (fl.NFHL_URL, fl.GEOCODER_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /flood", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat": {"type": "string", "description": "Latitude in decimal degrees, as text (with lon)."},
                "lon": {"type": "string", "description": "Longitude in decimal degrees, as text (with lat)."},
                "address": {"type": "string", "description": "US street address to geocode (address form)."},
            },
            "additionalProperties": False,
        },
    }


def safety_tool_definition():
    """safety_file: tools/safety_file.py through api.endpoints.safety."""
    return {
        "name": SAFETY_TOOL,
        "description": (
            "Sourced vehicle safety file from the public NHTSA APIs under %s, %s. Give "
            "`make`, `model` and `year` (model year, four digits). One file with the safety "
            "ratings, the recalls and the complaints for that model year, make and model, "
            "each section's records exactly as its API returns them. A section with no "
            "records is an empty result for that section only; any source answering other "
            "than HTTP 200 is a source failure, never an empty result. %s %s"
            % (sf.BASE_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /safety", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "make": {"type": "string", "description": "Vehicle make, e.g. Hyundai."},
                "model": {"type": "string", "description": "Vehicle model, e.g. Elantra."},
                "year": {"type": "string", "description": "Model year, four digits."},
            },
            "required": ["make", "model", "year"],
            "additionalProperties": False,
        },
    }


def fda_tool_definition():
    """fda_recall_check: tools/fda_recall_check.py through api.endpoints.fda_recall."""
    return {
        "name": FDA_TOOL,
        "description": (
            "Sourced FDA enforcement recall search from the openFDA enforcement APIs (%s), "
            "%s. Give `name` (a product, device or firm name); optional `field` is product "
            "(default) or firm, `category` is food, device or both (default), and `limit` "
            "(1 to %d, default %d) sets results per category. An empty result is proven by "
            "openFDA's own 404 NOT_FOUND answer, printed in full; it is never a clearance. "
            "%s %s"
            % (fr.API_URL, FORMAT_SENTENCE, fr.MAX_LIMIT, fr.DEFAULT_LIMIT,
               SAME_TEXT % "GET /fda", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Product, device or firm name to search for."},
                "field": {"type": "string", "enum": list(fr.FIELDS), "description": "Optional: search the product description or the recalling firm; default product."},
                "category": {"type": "string", "enum": ["food", "device", "both"], "description": "Optional: which enforcement endpoint or endpoints to search; default both."},
                "limit": {"type": "integer", "minimum": 1, "maximum": fr.MAX_LIMIT,
                          "description": "Optional results per category; default %d." % fr.DEFAULT_LIMIT},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def epa_tool_definition():
    """epa_screen: tools/epa_screen.py through api.endpoints.epa_screen."""
    return {
        "name": EPA_TOOL,
        "description": (
            "Sourced EPA facility compliance screen from the EPA ECHO services (%s), %s. "
            "Give `name` (a facility name to search for) and `state` (two letter code); "
            "optional `city` narrows the search, and optional `registry_id` selects that "
            "row from the search results. The compliance status, significant noncompliance "
            "flag and quarters with noncompliance are ECHO's own fields as shown. A search "
            "with no rows is an empty result, not a finding that a facility is free of "
            "violations. %s %s"
            % (es.BASE_URL, FORMAT_SENTENCE, SAME_TEXT % "GET /epa", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Facility name to search for."},
                "state": {"type": "string", "description": "Two letter state code."},
                "city": {"type": "string", "description": "Optional city, to narrow the search."},
                "registry_id": {"type": "string", "description": "Optional: selects that registry row from the search results."},
            },
            "required": ["name", "state"],
            "additionalProperties": False,
        },
    }


def csl_tool_definition():
    """csl_screen: tools/csl_screen.py through api.endpoints.csl."""
    return {
        "name": CSL_TOOL,
        "description": (
            "Sourced Consolidated Screening List name screen against the published list "
            "file at data.trade.gov (%s), %s. Give `name` (a person or company name, at "
            "least %d letters or digits). The list file is downloaded and cached locally "
            "for a day; every report states the list publication date and how many rows "
            "were screened. Matches are the list's own rows as shown. A name with no match "
            "is an empty result, not a clearance. %s %s"
            % (cs.CSL_URL, FORMAT_SENTENCE, cs.MIN_QUERY_CHARS, SAME_TEXT % "GET /csl", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person or company name to screen against the Consolidated Screening List."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def oig_tool_definition():
    """oig_screen: tools/oig_screen.py through api.endpoints.oig_exclusions."""
    return {
        "name": OIG_TOOL,
        "description": (
            "Sourced HHS OIG exclusion screen against the LEIE database file (%s), %s. "
            "Give `name` (a person or entity name, at least %d letters or digits). The "
            "complete current LEIE file is read on every call; matches are its records as "
            "shown, with the exclusion type, basis and dates the file carries. No match is "
            "not a clearance. %s %s"
            % (oig.LEIE_URL, FORMAT_SENTENCE, oig.MIN_QUERY_CHARS, SAME_TEXT % "GET /oig", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person or entity name to screen against the LEIE."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def insider_tool_definition():
    """insider_check: tools/insider_check.py through api.endpoints.insider."""
    return {
        "name": INSIDER_TOOL,
        "description": (
            "Sourced SEC EDGAR insider filing listing for a company, %s. Give `cik` (the "
            "company's Central Index Key, fetched from the EDGAR submissions API, %s) or "
            "`issuer` (an EDGAR company name search, %s), not both. Optional `max_filings` "
            "(1 to %d, default %d) limits how many ownership filings (Forms 3, 4 and 5) are "
            "read. The server must have %s set (EDGAR fair access needs the operator's "
            "contact in the User-Agent); while it is unset the tool answers an error and "
            "fetches nothing. A listing of filings as filed, not an analysis of any trade "
            "or person. %s %s"
            % (FORMAT_SENTENCE, ef.SUBMISSIONS_URL, ef.COMPANY_SEARCH_URL, ic.MAX_FILINGS,
               ic.DEFAULT_MAX_FILINGS, ic.CONTACT_ENV, SAME_TEXT % "GET /insider", FAIL_SENTENCE)
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cik": {"type": "string", "description": "Central Index Key, digits (cik form)."},
                "issuer": {"type": "string", "description": "Company name for the EDGAR company search (issuer form)."},
                "max_filings": {"type": "integer", "minimum": 1, "maximum": ic.MAX_FILINGS,
                                "description": "Optional: how many ownership filings to read; default %d." % ic.DEFAULT_MAX_FILINGS},
            },
            "additionalProperties": False,
        },
    }


def tool_definitions(wallet):
    """The tools/list entries, recall_check first."""
    return [tool_definition(wallet), carrier_tool_definition(), litigation_tool_definition(),
            formd_tool_definition(), nonprofit_tool_definition(), awards_tool_definition(),
            pagespeed_tool_definition(), domain_tool_definition(), ofac_tool_definition(),
            vin_tool_definition(), trials_tool_definition(), drug_tool_definition(),
            links_tool_definition(), meta_tool_definition(), github_tool_definition(),
            app_tool_definition(), fx_tool_definition(), flood_tool_definition(),
            safety_tool_definition(), fda_tool_definition(), epa_tool_definition(),
            csl_tool_definition(), oig_tool_definition(), insider_tool_definition()]


# Argument kinds per tool: how each JSON argument becomes the dict-of-lists
# query the API dispatchers take, so both surfaces share one dispatcher and
# one output for the same inputs.
RECALL_ARGUMENTS = {"product": "string", "exact_name": "string", "near": "array",
                    "make": "string", "model": "string", "year": "string", "exclude": "array"}
CARRIER_ARGUMENTS = {"usdot": "string", "name": "string", "subject": "string",
                     "source": "array", "limit": "integer", "exclude": "array"}
LITIGATION_ARGUMENTS = {"party": "array", "subject": "string", "filed_after": "string",
                        "order_by": "string", "list": "integer", "docket_details": "boolean",
                        "exclude": "array"}
FORMD_ARGUMENTS = {"cik": "string", "issuer": "string", "max_filings": "integer", "exclude": "array"}
NONPROFIT_ARGUMENTS = {"name": "string", "ein": "array", "subject": "string", "exclude": "array"}
AWARDS_ARGUMENTS = {"recipient": "string", "naics": "array", "start": "string", "end": "string",
                    "page": "integer", "limit": "integer", "exclude": "array"}
PAGESPEED_ARGUMENTS = {"url": "array", "strategy": "string", "subject": "string", "exclude": "array"}
DOMAIN_ARGUMENTS = {"domain": "string"}
OFAC_ARGUMENTS = {"name": "string"}
VIN_ARGUMENTS = {"vin": "string", "model_year": "string"}
TRIALS_ARGUMENTS = {"term": "string", "limit": "integer"}
DRUG_ARGUMENTS = {"name": "string"}
LINKS_ARGUMENTS = {"url": "string"}
META_ARGUMENTS = {"url": "string"}
GITHUB_ARGUMENTS = {"owner": "string", "repo": "string"}
APP_ARGUMENTS = {"name": "string", "country": "string", "limit": "integer"}
FX_ARGUMENTS = {"base": "string", "target": "string", "amount": "string", "date": "string"}
FLOOD_ARGUMENTS = {"lat": "string", "lon": "string", "address": "string"}
SAFETY_ARGUMENTS = {"make": "string", "model": "string", "year": "string"}
FDA_ARGUMENTS = {"name": "string", "field": "string", "category": "string", "limit": "integer"}
EPA_ARGUMENTS = {"name": "string", "state": "string", "city": "string", "registry_id": "string"}
CSL_ARGUMENTS = {"name": "string"}
OIG_ARGUMENTS = {"name": "string"}
INSIDER_ARGUMENTS = {"cik": "string", "issuer": "string", "max_filings": "integer"}


def coerce_arguments(arguments, kinds, error):
    """Turn tool arguments into a dict-of-lists query by the given kinds.
    Raises `error` (a ValueError subclass) on a shape the schema rejects."""
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise error("arguments must be an object")
    unknown = sorted(set(arguments) - set(kinds))
    if unknown:
        raise error("unknown argument(s): %s" % ", ".join(unknown))
    query = {}
    for key, value in arguments.items():
        kind = kinds[key]
        if kind == "array":
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise error("%s must be an array of strings" % key)
            query[key] = list(value)
        elif kind == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise error("%s must be an integer" % key)
            query[key] = [str(value)]
        elif kind == "boolean":
            if not isinstance(value, bool):
                raise error("%s must be true or false" % key)
            query[key] = ["1" if value else "0"]
        else:
            if not isinstance(value, str):
                raise error("%s must be a string" % key)
            query[key] = [value]
    return query


def arguments_to_query(arguments):
    """recall_check arguments to the query api.recall_api.recall expects."""
    return coerce_arguments(arguments, RECALL_ARGUMENTS, recall_api.BadRequest)


def call_tool(name, arguments):
    """Run a tool call. Returns the MCP tools/call result object."""
    if name == TOOL_NAME:
        return call_recall(arguments)
    if name == CARRIER_TOOL:
        return call_endpoint(endpoints.carrier, CARRIER_ARGUMENTS, arguments)
    if name == LITIGATION_TOOL:
        return call_endpoint(endpoints.litigation, LITIGATION_ARGUMENTS, arguments)
    if name == FORMD_TOOL:
        return call_endpoint(endpoints.formd, FORMD_ARGUMENTS, arguments)
    if name == NONPROFIT_TOOL:
        return call_endpoint(endpoints.nonprofit, NONPROFIT_ARGUMENTS, arguments)
    if name == AWARDS_TOOL:
        return call_endpoint(endpoints.awards, AWARDS_ARGUMENTS, arguments)
    if name == PAGESPEED_TOOL:
        return call_endpoint(endpoints.pagespeed, PAGESPEED_ARGUMENTS, arguments)
    if name == DOMAIN_TOOL:
        return call_endpoint(endpoints.domain, DOMAIN_ARGUMENTS, arguments)
    if name == OFAC_TOOL:
        return call_endpoint(endpoints.ofac_sdn, OFAC_ARGUMENTS, arguments)
    if name == VIN_TOOL:
        return call_endpoint(endpoints.vin, VIN_ARGUMENTS, arguments)
    if name == TRIALS_TOOL:
        return call_endpoint(endpoints.clinical_trials, TRIALS_ARGUMENTS, arguments)
    if name == DRUG_TOOL:
        return call_endpoint(endpoints.drug, DRUG_ARGUMENTS, arguments)
    if name == LINKS_TOOL:
        return call_endpoint(endpoints.links, LINKS_ARGUMENTS, arguments)
    if name == META_TOOL:
        return call_endpoint(endpoints.meta_tags, META_ARGUMENTS, arguments)
    if name == GITHUB_TOOL:
        return call_endpoint(endpoints.github_repo, GITHUB_ARGUMENTS, arguments)
    if name == APP_TOOL:
        return call_endpoint(endpoints.app, APP_ARGUMENTS, arguments)
    if name == FX_TOOL:
        return call_endpoint(endpoints.exchange_rate, FX_ARGUMENTS, arguments)
    if name == FLOOD_TOOL:
        return call_endpoint(endpoints.flood, FLOOD_ARGUMENTS, arguments)
    if name == SAFETY_TOOL:
        return call_endpoint(endpoints.safety, SAFETY_ARGUMENTS, arguments)
    if name == FDA_TOOL:
        return call_endpoint(endpoints.fda_recall, FDA_ARGUMENTS, arguments)
    if name == EPA_TOOL:
        return call_endpoint(endpoints.epa_screen, EPA_ARGUMENTS, arguments)
    if name == CSL_TOOL:
        return call_endpoint(endpoints.csl, CSL_ARGUMENTS, arguments)
    if name == OIG_TOOL:
        return call_endpoint(endpoints.oig_exclusions, OIG_ARGUMENTS, arguments)
    if name == INSIDER_TOOL:
        return call_endpoint(endpoints.insider, INSIDER_ARGUMENTS, arguments)
    raise ToolNotFound(name)


def call_recall(arguments):
    """recall_check, through api.recall_api.recall, the GET /recall dispatcher."""
    try:
        text = recall_api.recall(arguments_to_query(arguments))
    except recall_api.BadRequest as err:
        return error_result("Bad request: %s" % err)
    except recall_api.SourceFailed as err:
        return error_result(str(err))
    except ValueError as err:
        if isinstance(err, cpsc_recalls.FetchError):
            return error_result("Fetch failed, no report emitted: %s" % err)
        return error_result("Bad request: %s" % err)
    except (urllib.error.URLError, OSError) as err:
        return error_result("Fetch failed, no report emitted: %s" % err)
    return {"content": [{"type": "text", "text": text}], "isError": False}


def call_endpoint(dispatcher, kinds, arguments):
    """Every tool but recall_check, through the api.endpoints dispatcher
    the API's GET path uses. The outcomes map as the API maps
    them: a bad request or an exclusion the response does not contain is an
    error with no report and (for the former) no fetch; a failed fetch or an
    unreadable response is an error with no report, never an empty result."""
    try:
        text = dispatcher(coerce_arguments(arguments, kinds, endpoints.BadRequest))
    except endpoints.BadRequest as err:
        return error_result("Bad request: %s" % err)
    except endpoints.Unavailable as err:
        return error_result("Unavailable, no report emitted: %s" % err)
    except endpoints.FetchFailed as err:
        return error_result(str(err))
    except ValueError as err:
        return error_result("Bad request: %s" % err)
    except (urllib.error.URLError, OSError) as err:
        return error_result("Fetch failed, no report emitted: %s" % err)
    return {"content": [{"type": "text", "text": text}], "isError": False}


def error_result(message):
    return {"content": [{"type": "text", "text": message}], "isError": True}


class ToolNotFound(Exception):
    pass


# ----------------------------------------------------------------------
# JSON-RPC handling
# ----------------------------------------------------------------------

def instructions(wallet):
    text = ("Twenty four tools, each answering in the fixed evidence format: claims, exact query, "
            "UTC retrieval time, source link, and the complete raw response beneath the "
            "link. recall_check answers a product name or a vehicle (make, model, year) "
            "with a sourced recall check; carrier_check answers a USDOT number or a carrier "
            "name with the public FMCSA records; litigation_screen answers party name "
            "variants with a CourtListener RECAP docket index screen; formd_check answers a "
            "CIK or issuer name with its SEC EDGAR Form D filings; nonprofit_check answers a "
            "name or EIN with ProPublica Nonprofit Explorer records; awards_search answers a "
            "recipient or NAICS codes with USAspending prime contract awards; "
            "pagespeed_snapshot answers page URLs with a PageSpeed Insights snapshot; "
            "domain_trust_check answers a domain with its DNS records, SPF, DMARC and HTTPS "
            "hop chain; ofac_sanctions_check answers a name with an OFAC SDN list check; "
            "vin_decode_check answers a VIN with the NHTSA vPIC decode; clinical_trial_check "
            "answers a company, drug or condition with a ClinicalTrials.gov study search; "
            "fda_drug_check answers a drug name with openFDA label facts; broken_link_check "
            "answers a page URL with the state of its link targets; meta_tag_check answers a "
            "page URL with its title, description and Open Graph tags; github_repo_check "
            "answers an owner and repository with GitHub's repository facts; "
            "app_lookup_check answers an app name with App Store lookup results; "
            "exchange_rate_check answers a currency pair with the Frankfurter rate; "
            "flood_check answers coordinates or a US address with a FEMA flood zone screen; "
            "safety_file answers a make, model and year with NHTSA ratings, recalls and "
            "complaints; fda_recall_check answers a product, device or firm name with an "
            "openFDA enforcement recall search; epa_screen answers a facility name and state "
            "with EPA ECHO compliance records; csl_screen answers a name with a Consolidated "
            "Screening List screen; oig_screen answers a name with an HHS OIG LEIE exclusion "
            "screen; insider_check answers a CIK or issuer name with its SEC EDGAR insider "
            "filings. Results are the public sources' records as returned; an empty result "
            "is not a clearance.")
    if wallet:
        text += " Payment: USDC per call to %s, collected by the listing platform." % wallet
    return text


def handle_request(message, wallet):
    """Handle one parsed JSON-RPC message. Returns a response object, or
    None for notifications and for anything that must not be answered."""
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
        if isinstance(message, dict) and "id" in message:
            return rpc_error(message.get("id"), JSONRPC_INVALID_REQUEST, "invalid request")
        return None
    method = message["method"]
    params = message.get("params") or {}
    has_id = "id" in message
    req_id = message.get("id")

    if method.startswith("notifications/"):
        return None  # notifications are never answered
    if not has_id:
        return None  # a request without an id is a notification by the JSON-RPC rule

    if method == "initialize":
        requested = params.get("protocolVersion") if isinstance(params, dict) else None
        version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
        return rpc_result(req_id, {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": instructions(wallet),
        })
    if method == "ping":
        return rpc_result(req_id, {})
    if method == "tools/list":
        return rpc_result(req_id, {"tools": tool_definitions(wallet)})
    if method == "tools/call":
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return rpc_error(req_id, JSONRPC_INVALID_PARAMS, "tools/call needs params.name")
        try:
            return rpc_result(req_id, call_tool(params["name"], params.get("arguments")))
        except ToolNotFound as err:
            return rpc_error(req_id, JSONRPC_INVALID_PARAMS, "unknown tool: %s" % err)
    return rpc_error(req_id, JSONRPC_METHOD_NOT_FOUND, "method not found: %s" % method)


def rpc_result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def rpc_error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def serve(stdin, stdout, wallet=None, stderr=None):
    """Read newline delimited JSON-RPC messages from stdin until EOF,
    writing one response line per answered request to stdout."""
    stderr = stderr or sys.stderr
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            response = rpc_error(None, JSONRPC_PARSE_ERROR, "parse error")
        else:
            try:
                response = handle_request(message, wallet)
            except Exception as err:  # a bug must not kill the server or leak a half report
                req_id = message.get("id") if isinstance(message, dict) else None
                stderr.write("recall_mcp: internal error handling %r: %s\n" % (message.get("method") if isinstance(message, dict) else None, err))
                response = rpc_error(req_id, -32603, "internal error") if req_id is not None else None
        if response is not None:
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()


def main(argv=None):
    try:
        wallet = recall_api.payout_wallet()
    except recall_api.ConfigError as err:
        sys.stderr.write("refusing to start: %s\n" % err)
        return 2
    sys.stderr.write("%s %s: MCP over stdio; payout wallet: %s\n" % (SERVER_NAME, SERVER_VERSION, wallet or "(not set)"))
    try:
        serve(sys.stdin, sys.stdout, wallet)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
