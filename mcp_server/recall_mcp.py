#!/usr/bin/env python3
"""Recall check MCP server core (B1 of issue #33).

A Model Context Protocol server, stdio transport, that exposes one tool,
`recall_check`, wrapping the merged recall fetchers in tools/ through the
same host-free dispatcher the pay per call API uses (api/recall_api.py).
A call takes a product name (CPSC SaferProducts) or a vehicle form
(NHTSA recalls: make, model, year) and returns the recall check as
Markdown in the fixed delivery format from AGENT-BRIEF.md: the claim
lines, the exact query, the UTC retrieval time, the source link, and
the complete raw response directly beneath the link. The text is the
fetchers' own output, byte for byte the same as the API returns for the
same query; this server adds nothing to it.

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
                            in the tool description. Never written to a
                            file here.

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

from api import recall_api  # noqa: E402
from tools import cpsc_recalls  # noqa: E402

SERVER_NAME = "hojo-recall-check"
SERVER_VERSION = "0.1.0"
# Protocol revisions this server knows. The client's requested version is
# echoed when it is one of these; otherwise the newest known is offered,
# as the MCP version negotiation rule says.
PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
TOOL_NAME = "recall_check"

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


def arguments_to_query(arguments):
    """Turn tool arguments into the dict-of-lists query api.recall_api.recall
    expects, so both surfaces share one dispatcher and one output."""
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise recall_api.BadRequest("arguments must be an object")
    allowed = {"product", "exact_name", "near", "make", "model", "year", "exclude"}
    unknown = sorted(set(arguments) - allowed)
    if unknown:
        raise recall_api.BadRequest("unknown argument(s): %s" % ", ".join(unknown))
    query = {}
    for key, value in arguments.items():
        if key in ("near", "exclude"):
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise recall_api.BadRequest("%s must be an array of strings" % key)
            query[key] = list(value)
        else:
            if not isinstance(value, str):
                raise recall_api.BadRequest("%s must be a string" % key)
            query[key] = [value]
    return query


def call_tool(name, arguments):
    """Run a tool call. Returns the MCP tools/call result object."""
    if name != TOOL_NAME:
        raise ToolNotFound(name)
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


def error_result(message):
    return {"content": [{"type": "text", "text": message}], "isError": True}


class ToolNotFound(Exception):
    pass


# ----------------------------------------------------------------------
# JSON-RPC handling
# ----------------------------------------------------------------------

def instructions(wallet):
    text = ("One tool, recall_check, answers a product name or a vehicle (make, model, "
            "year) with a sourced recall check in the fixed evidence format: claims, exact "
            "query, UTC retrieval time, source link, and the complete raw response beneath "
            "the link. Results are the public sources' records as returned; an empty result "
            "is not a safety clearance.")
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
        return rpc_result(req_id, {"tools": [tool_definition(wallet)]})
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
