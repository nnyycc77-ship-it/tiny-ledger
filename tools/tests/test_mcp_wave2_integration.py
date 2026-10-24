"""Offline integration pass over the wave 2 MCP tools (issue #224).

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcp_wave2_integration.py' -v

In the pattern of tools/tests/test_wave2_integration.py (issue #212), which
ran the same checks through recall_api.handle for the API routes: every check
here runs through the MCP server's own call path, recall_mcp.call_tool, for
the wave 2 tools as registered in the server code on main:

    flood_check, fda_drug_check, safety_file, epa_screen, csl_screen,
    oig_screen, faa_lookup, insider_check

plus fda_recall_check, the fetcher behind the /fda route of the #212 pass,
registered on the same surface in the same wave; the pass covers it too so
the whole wave 2 MCP surface is proven, nine tools in all.

For each tool, three things are checked against the recorded fixtures that
already live in this repo, served by each tool test module's own replay
helper, exactly as the #212 pass served them (its route classes are reused
here, so every body is the same capture, with its provenance, that the tool's
own tests use):

1. Same text (one test per tool). The tool call's text is the fetcher's own
   Markdown, byte for byte: it equals what the tool's command line prints
   for the same inputs on the same replayed fixtures. For the tools whose
   dispatcher adds a title block, the text is exactly that block followed by
   the command line's output. The byte equality assertions are the #212
   ones, unchanged.
2. Refused arguments. Arguments the tool must refuse answer a tool error
   (isError true) carrying the refusal, and no fetch is made: the source
   fetch is replaced by one that fails the test if it is called.
3. Unavailable source. A source failure answers a tool error with no report
   in the text (and insider_check without an operator contact answers a
   tool error naming it, with no fetch).

No network is used: urllib.request.urlopen is replaced, for the whole
module, by a function that fails the test. Where a check needs a source
failure, the failure is raised by the test (labelled "test failure"), not
recorded.

Offline exceptions, named and counted in the pattern the #212 module used
for its drift marks: OFFLINE_EXCEPTIONS below maps a tool name to the reason
it cannot be driven offline from the existing fixtures. It is empty for
this pass: every one of the nine tools is driven offline below, and the
coverage test accounts for each name exactly once, as a case or as a named
exception, so a tool can never silently drop out of the pass.
"""

import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
for path in (str(ROOT), str(ROOT / "tools" / "tests")):
    if path not in sys.path:
        sys.path.insert(0, path)

from api import endpoints  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
import test_wave1_integration as w1  # noqa: E402
import test_wave2_integration as w2  # noqa: E402

t_drug = w1.t_drug

# The nine tools this pass covers: the eight named in issue #224, with the
# exact names registered in the server code, plus fda_recall_check (see the
# module docstring).
ALL_TOOLS = ("flood_check", "fda_drug_check", "fda_recall_check", "safety_file",
             "epa_screen", "csl_screen", "oig_screen", "faa_lookup", "insider_check")

# Named, counted offline exceptions: tool name -> why it cannot be driven
# offline from the existing fixtures. Empty for this pass (see docstring).
OFFLINE_EXCEPTIONS = {}


def no_network(*args, **kwargs):
    raise AssertionError("the MCP wave 2 integration pass tried to reach the network")


def call(name, arguments, env=None):
    """One MCP tool call through the server's own call path."""
    if env is None:
        return recall_mcp.call_tool(name, arguments)
    with mock.patch.dict(os.environ, env):
        return recall_mcp.call_tool(name, arguments)


def text_of(result):
    return result["content"][0]["text"]


# The fda_drug_check case, in the pattern of the Drug route of
# test_wave1_integration.py: the Tylenol capture from the openFDA fixtures,
# served through a fetch that answers only the URL the tool builds.

def drug_fetcher():
    return w1.only(endpoints.fd.build_url("Tylenol"), t_drug.capture(t_drug.HIT))


def drug_serve():
    return mock.patch.object(endpoints.fd, "fetch", drug_fetcher())


def drug_own():
    with drug_serve():
        return w1.cli(endpoints.fd.main, ["Tylenol"])


def drug_break_source():
    def refused(url):
        raise urllib.error.URLError("test failure: refused")
    return mock.patch.object(endpoints.fd, "fetch", refused)


def drug_block_fetch():
    return mock.patch.object(endpoints.fd, "fetch", w2.never)


DRUG_HEAD = endpoints._head(
    "FDA drug label: Tylenol",
    "Observation only: this report records what the public openFDA drug label API returned for this "
    "name at the retrieval time stated below; the facts are the first returned label record's as shown, "
    "and the report is not medical advice.", "tools/fda_drug_check.py")


# Each case: the MCP tool name, the arguments that carry the #212 pass's
# query, the route object whose serve/own/break/block helpers replay the
# fixtures, the title block its dispatcher adds if any, the environment the
# call needs if any, and the argument sets the tool must refuse.

class Case:
    env = None
    head = None
    broken_arguments = None  # arguments for the source failure check, if not the case's own

    def __init__(self, route):
        self.route = route

    def serve(self):
        return self.route.serve()

    def own(self):
        return self.route.own()

    def break_source(self):
        return self.route.break_source()

    def block_fetch(self):
        return self.route.block_fetch()


class DrugCase:
    name, arguments = "fda_drug_check", {"name": "Tylenol"}
    head, env, broken_arguments = DRUG_HEAD, None, None
    bad = ({}, {"name": ""}, {"name": 'say "cheese"'})

    def serve(self):
        return drug_serve()

    def own(self):
        return drug_own()

    def break_source(self):
        return drug_break_source()

    def block_fetch(self):
        return drug_block_fetch()


def route_case(name, arguments, route, bad, env=None, broken_arguments=None):
    case = Case(route)
    case.name, case.arguments, case.bad, case.env = name, arguments, bad, env
    case.head = route.head
    case.broken_arguments = broken_arguments
    return case


_flood = w2.Flood()
_safety = w2.Safety()
_fda = w2.Fda()
_epa = w2.Epa()
_csl = w2.Csl()
_oig = w2.Oig()
_insider = w2.Insider()
_faa = w2.Faa()

CASES = [
    route_case("flood_check", {"lat": "27.9235", "lon": "-82.4515"}, _flood,
               ({}, {"lat": "27.9"}, {"lat": "95", "lon": "0"}, {"lat": "1", "lon": "2", "address": "x"})),
    DrugCase(),
    route_case("fda_recall_check", {"name": "peanut butter", "category": "food", "limit": 3}, _fda,
               ({}, {"name": "a"}, {"name": "ok", "category": "drug"}, {"name": "ok", "limit": 0})),
    route_case("safety_file", {"make": "Hyundai", "model": "Elantra", "year": "2021"}, _safety,
               ({}, {"make": "Hyundai", "model": "Elantra"},
                {"make": "Hyundai", "model": "Elantra", "year": "21"}),
               broken_arguments={"make": "Hyundai", "model": "Nosuchmodel", "year": "2021"}),
    route_case("epa_screen", {"name": "BAYTOWN OLEFINS", "city": "BAYTOWN", "state": "TX"}, _epa,
               ({}, {"name": "BAYTOWN OLEFINS"}, {"name": "BAYTOWN OLEFINS", "state": "Texas"})),
    route_case("csl_screen", {"name": "Mohammed Abu Teir"}, _csl,
               ({}, {"name": "ab"})),
    route_case("oig_screen", {"name": "Aaron Smith"}, _oig,
               ({}, {"name": "ab"}, {"name": "a.b"})),
    route_case("faa_lookup", {"n_number": "N100ZT"}, _faa,
               ({}, {"n_number": "N"}, {"n_number": "N10-0Z"}, {"n_number": "N1234567"})),
    route_case("insider_check", {"cik": "320193", "max_filings": 2}, _insider,
               ({}, {"cik": "320193", "issuer": "Apple"}, {"cik": "abc"},
                {"cik": "320193", "max_filings": 0}), env=_insider.env),
]


class McpWave2Integration(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_the_pass_covers_the_wave2_mcp_tools(self):
        covered = sorted([c.name for c in CASES] + sorted(OFFLINE_EXCEPTIONS))
        self.assertEqual(covered, sorted(ALL_TOOLS))
        for name in ALL_TOOLS:
            self.assertIn(name, recall_mcp.TOOL_NAMES)

    def test_each_refused_argument_is_a_tool_error_with_no_fetch(self):
        for case in CASES:
            for arguments in case.bad:
                with self.subTest(tool=case.name, arguments=arguments), case.block_fetch():
                    result = call(case.name, arguments, case.env)
                self.assertTrue(result["isError"], text_of(result)[:300])
                self.assertTrue(text_of(result).startswith("Bad request: "), text_of(result)[:300])

    def test_an_unknown_argument_is_a_tool_error_with_no_fetch(self):
        case = CASES[0]
        with case.block_fetch():
            result = call(case.name, dict(case.arguments, bogus="x"), case.env)
        self.assertTrue(result["isError"])
        self.assertIn("unknown argument", text_of(result))

    def test_each_source_failure_is_a_tool_error_with_no_report(self):
        for case in CASES:
            with self.subTest(tool=case.name), case.break_source():
                result = call(case.name, case.broken_arguments or case.arguments, case.env)
            self.assertTrue(result["isError"], text_of(result)[:300])
            self.assertNotIn("\n## ", text_of(result))
            self.assertFalse(text_of(result).startswith("#"), text_of(result)[:300])

    def test_insider_without_an_operator_contact_is_a_tool_error_with_no_fetch(self):
        case = [c for c in CASES if c.name == "insider_check"][0]
        with case.block_fetch(), mock.patch.dict(os.environ, {}, clear=True):
            result = recall_mcp.call_tool("insider_check", {"cik": "320193"})
        self.assertTrue(result["isError"])
        self.assertIn("EDGAR_CONTACT", text_of(result))
        self.assertNotIn("\n## ", text_of(result))


def same_text(case):
    def test(self):
        code, own, err = case.own()
        self.assertEqual(code, 0, err)
        with case.serve():
            result = call(case.name, case.arguments, case.env)
        self.assertFalse(result["isError"], text_of(result)[:300])
        expected = own if case.head is None else "\n".join(case.head) + "\n" + own
        self.assertEqual(text_of(result), expected)
    test.__doc__ = "%s: the tool text is the fetcher's own Markdown" % case.name
    return test


for _case in CASES:
    if _case.name not in OFFLINE_EXCEPTIONS:
        setattr(McpWave2Integration, "test_tool_text_is_the_fetchers_own_markdown_%s" % _case.name,
                same_text(_case))


if __name__ == "__main__":
    unittest.main()
