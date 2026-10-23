#!/usr/bin/env python3
"""Recall check MCP server core (B1 of issue #33), plus the carrier
vetting and litigation screen tools (issue #67).

A Model Context Protocol server, stdio transport, that exposes three
tools wrapping merged fetchers in tools/ through the same host-free
dispatchers the pay per call API uses (api/recall_api.py and
api/endpoints.py):

    recall_check       CPSC SaferProducts (product) or NHTSA recalls
                       (make, model, year); the GET /recall dispatcher
    carrier_check      FMCSA carrier records via tools/fmcsa_carrier.py
                       (usdot or name); the GET /carrier dispatcher
    litigation_screen  CourtListener RECAP docket search via
                       tools/courtlistener_recap.py (party variants);
                       the GET /litigation dispatcher

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
from tools import courtlistener_recap as cl  # noqa: E402
from tools import cpsc_recalls  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402

SERVER_NAME = "hojo-recall-check"
SERVER_VERSION = "0.2.0"
# Protocol revisions this server knows. The client's requested version is
# echoed when it is one of these; otherwise the newest known is offered,
# as the MCP version negotiation rule says.
PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
TOOL_NAME = "recall_check"
CARRIER_TOOL = "carrier_check"
LITIGATION_TOOL = "litigation_screen"
TOOL_NAMES = (TOOL_NAME, CARRIER_TOOL, LITIGATION_TOOL)

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


def tool_definitions(wallet):
    """The tools/list entries, recall_check first."""
    return [tool_definition(wallet), carrier_tool_definition(), litigation_tool_definition()]


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
    raise ToolNotFound(name)


def call_recall(arguments):
    """recall_check, through api.recall_api.recall, the GET /recall dispatcher."""
    try:
        text = recall_api.recall(arguments_to_query(arguments))
    except recall_api.BadRequest as err:
        return error_result("Bad request: %s" % err)
    except ValueError as err:
        if isinstance(err, cpsc_recalls.FetchError):
            return error_result("Fetch failed, no report emitted: %s" % err)
        return error_result("Bad request: %s" % err)
    except (urllib.error.URLError, OSError) as err:
        return error_result("Fetch failed, no report emitted: %s" % err)
    return {"content": [{"type": "text", "text": text}], "isError": False}


def call_endpoint(dispatcher, kinds, arguments):
    """carrier_check and litigation_screen, through the api.endpoints
    dispatcher the API's GET path uses. The outcomes map as the API maps
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
    text = ("Three tools, each answering in the fixed evidence format: claims, exact query, "
            "UTC retrieval time, source link, and the complete raw response beneath the "
            "link. recall_check answers a product name or a vehicle (make, model, year) "
            "with a sourced recall check; carrier_check answers a USDOT number or a carrier "
            "name with the public FMCSA records; litigation_screen answers party name "
            "variants with a CourtListener RECAP docket index screen. Results are the "
            "public sources' records as returned; an empty result is not a clearance.")
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
