"""OpenAPI entry alignment for the seven routes added by PR #253 (issue #263). No network.

Run from the repository root: python3 -m unittest discover -s api -v

For /domain, /ofac, /github, /flood, /fda, /oig and /insider, this proves
that the api/openapi.json entry and the route's dispatcher in
api/endpoints.py agree, so neither can drift silently:

* parameter names: the set of query keys the dispatcher reads (recorded
  by a query object that notes every key asked for) equals the set of
  parameter names in the entry;
* required flags: a parameter marked required is in every valid sample
  query, and dropping it from any of them is answered 400; a parameter not
  marked required is absent from at least one valid sample, which is not
  answered 400 (alternatives such as lat and lon or address are two
  samples);
* response codes: the codes the route actually answers equal the codes
  the entry declares. 200 is a valid sample with the tool's entry point
  patched to return a SYNTHETIC report; 400 is the bare path; 502 is a
  valid sample with the entry point patched to raise the tool's own
  FetchError; 503 is the same valid sample on a server without
  EDGAR_CONTACT, which only /insider answers.

Every report and failure here is SYNTHETIC: the tools' entry points are
patched, and urlopen is replaced by a function that fails the test, so no
source is called and no source figure is used.
"""

import json
import os
import sys
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import endpoints, recall_api  # noqa: E402

OPENAPI = json.loads((ROOT / "api" / "openapi.json").read_text(encoding="utf-8"))
CONTACT = "Test Operator operator@example.com"  # placeholder contact for the tests
SYNTHETIC_LINES = ["# SYNTHETIC report", "", "SYNTHETIC body for the alignment test."]

# Valid sample queries per route. Every parameter the entry names appears in
# at least one; alternatives (lat and lon, or address; cik, or issuer) are
# separate samples.
SAMPLES = {
    "/domain": ["domain=example.com"],
    "/ofac": ["name=Cimex"],
    "/github": ["owner=psf&repo=requests"],
    "/flood": ["lat=27.9235&lon=-82.4515", "address=1600+Pennsylvania+Ave+NW%2C+Washington%2C+DC"],
    "/fda": ["name=peanut+butter", "name=peanut+butter&field=firm&category=food&limit=3"],
    "/oig": ["name=Aaron+Smith"],
    "/insider": ["cik=320193", "issuer=Apple+Inc&max_filings=2"],
}


def entry_points(fail):
    """The patches that stand in for each route's tool: a SYNTHETIC report,
    or the tool's own FetchError when `fail` is true."""
    def make(module, returns):
        def stand_in(*args, **kwargs):
            if fail:
                raise module.FetchError("SYNTHETIC failure for the alignment test; no report")
            return returns
        return stand_in
    dt, ofac, gh, fl, fda, oig, ins = (endpoints.dt, endpoints.ofac, endpoints.gh, endpoints.fl, endpoints.fda,
                                       endpoints.oig, endpoints.ins)
    return [
        patch.object(dt, "run", make(dt, SYNTHETIC_LINES)),
        patch.object(ofac, "fetch", make(ofac, object())),
        patch.object(ofac, "render", lambda *a, **k: "\n".join(SYNTHETIC_LINES)),
        patch.object(gh, "fetch", make(gh, object())),
        patch.object(gh, "render", lambda *a, **k: SYNTHETIC_LINES),
        patch.object(fl, "report", make(fl, SYNTHETIC_LINES)),
        patch.object(fda, "report", make(fda, SYNTHETIC_LINES)),
        patch.object(oig, "fetch", make(oig, object())),
        patch.object(oig, "render", lambda *a, **k: SYNTHETIC_LINES),
        patch.object(ins, "run", make(ins, SYNTHETIC_LINES)),
    ]


def no_network(*args, **kwargs):
    raise AssertionError("the alignment test tried to reach the network")


class RecordingQuery(dict):
    """A parsed query that notes every key the dispatcher asks for."""

    def __init__(self, *args):
        super().__init__(*args)
        self.asked = set()

    def get(self, key, default=None):
        self.asked.add(key)
        return super().get(key, default)


def status_of(path, query_string, fail=False, contact=True):
    """The status code the route answers, through recall_api.handle()."""
    env = {"EDGAR_CONTACT": CONTACT} if contact else {}
    patches = entry_points(fail) + [patch("urllib.request.urlopen", no_network),
                                    patch.dict(os.environ, env, clear=True)]
    for p in patches:
        p.start()
    try:
        status = recall_api.handle("GET", path, query_string, None)[0]
    finally:
        for p in reversed(patches):
            p.stop()
    return int(status.split()[0])


def parameters(path):
    return {p["name"]: p.get("required", False) for p in OPENAPI["paths"][path]["get"]["parameters"]}


def without(query_string, name):
    pairs = [(k, v) for k, v in urllib.parse.parse_qsl(query_string, keep_blank_values=True) if k != name]
    return urllib.parse.urlencode(pairs)


class AlignmentTests(unittest.TestCase):
    def test_the_seven_routes_are_in_the_document_and_dispatched(self):
        for path in SAMPLES:
            self.assertIn(path, OPENAPI["paths"], path)
            self.assertIn(path, endpoints.ROUTES, path)

    def test_every_valid_sample_is_answered_200(self):
        for path, samples in SAMPLES.items():
            for qs in samples:
                with self.subTest(path=path, query=qs):
                    self.assertEqual(status_of(path, qs), 200)

    def test_parameter_names_match_the_keys_the_dispatcher_reads(self):
        for path, samples in SAMPLES.items():
            with self.subTest(path=path):
                read = set()
                for qs in samples:
                    query = RecordingQuery(urllib.parse.parse_qs(qs))
                    with patch.dict(os.environ, {"EDGAR_CONTACT": CONTACT}, clear=True), \
                            patch("urllib.request.urlopen", no_network):
                        for p in entry_points(fail=False):
                            p.start()
                        try:
                            endpoints.ROUTES[path](query, None)
                        finally:
                            patch.stopall()
                    read |= query.asked
                self.assertEqual(read, set(parameters(path)))
                # every documented parameter is exercised by some sample
                used = {k for qs in samples for k in urllib.parse.parse_qs(qs)}
                self.assertEqual(used, set(parameters(path)))

    def test_required_flags_match_what_the_dispatcher_refuses(self):
        for path, samples in SAMPLES.items():
            for name, required in parameters(path).items():
                with self.subTest(path=path, parameter=name, required=required):
                    holding = [qs for qs in samples if name in urllib.parse.parse_qs(qs)]
                    if required:
                        self.assertEqual(len(holding), len(samples), "a required parameter is in every sample")
                        for qs in samples:
                            self.assertEqual(status_of(path, without(qs, name)), 400, qs)
                    else:
                        lacking = [qs for qs in samples if name not in urllib.parse.parse_qs(qs)]
                        self.assertTrue(lacking, "an optional parameter is absent from some valid sample")
                        for qs in lacking:
                            self.assertNotEqual(status_of(path, qs), 400, qs)

    def test_response_codes_match_the_codes_the_route_answers(self):
        for path, samples in SAMPLES.items():
            with self.subTest(path=path):
                declared = {int(code) for code in OPENAPI["paths"][path]["get"]["responses"]}
                observed = {status_of(path, samples[0]), status_of(path, ""),
                            status_of(path, samples[0], fail=True), status_of(path, samples[0], contact=False)}
                self.assertEqual(observed, declared)


if __name__ == "__main__":
    unittest.main()
