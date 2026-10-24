"""Tests for tools/clinical_trial_check.py and its GET /trials route (issue #162). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_clinical_trial_check.py' -v

Fixtures (fixtures/clinical-trials/, recorded in provenance.json): two
responses H5 captured live on 2026-10-24 with the tool's own fetch,
keyless: a hit (elivaldogene, four studies of a totalCount of 4, the
response carrying no nextPageToken) and an empty result (an invented term, totalCount 0 with an empty studies
array, the full raw body being the proof). Fixture transcripts omit any
Set-Cookie header, as the safety_file fixtures do; bodies are byte for
byte as returned and hash checked below. The failure shapes (a 503, a
non JSON body, a JSON body in the wrong shape) are built in this file
and labelled SYNTHETIC where they appear; they are not recordings.
Every test runs with urlopen replaced by a function that fails the
test, except the fetch tests, which replace it with a recorder.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import clinical_trial_check as ct  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "clinical-trials"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
HIT = "search-elivaldogene-5.http"
EMPTY = "search-zqxflorp-medicine-5.http"
CASES = {ct.search_url("elivaldogene", 5): HIT, ct.search_url("zqxflorp medicine", 5): EMPTY}


def captured(name, module=ct):
    meta = PROV[name]
    transcript = (FIX / name).read_text(encoding="utf-8")
    head, _, body = transcript.partition("\n\n")
    lines = head.split("\n")
    return module.Capture(meta["url"], meta["retrieved_utc"], lines[0], lines[1:], body)


def replay(module=ct):
    def fetcher(url):
        if url in CASES:
            return captured(CASES[url], module)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("clinical_trial_check tried to reach the network")


def run_main(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network), \
            mock.patch.object(ct, "fetch", fetcher or replay()), \
            mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
        code = ct.main(argv)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name in (HIT, EMPTY):
            raw = (FIX / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), PROV[name]["sha256"], name)
            body = raw.decode("utf-8").partition("\n\n")[2].encode("utf-8")
            self.assertEqual(hashlib.sha256(body).hexdigest(), PROV[name]["body_sha256"], name)
            self.assertEqual(len(body), PROV[name]["body_bytes"], name)
            self.assertNotIn("set-cookie", raw.decode("utf-8").lower(), name)

    def test_request_urls_reproduce_the_captured_requests(self):
        self.assertEqual(ct.search_url("elivaldogene", 5), PROV[HIT]["url"])
        self.assertEqual(ct.search_url("zqxflorp medicine", 5), PROV[EMPTY]["url"])
        self.assertIn("fields=NCTId%2CBriefTitle%2COverallStatus%2CLeadSponsorName%2CCondition%2CPhase",
                      ct.search_url("elivaldogene", 5))


class ReportTests(unittest.TestCase):
    def test_hit_report(self):
        with mock.patch("urllib.request.urlopen", no_network):
            lines = ct.run("elivaldogene", 5, replay())
        out = "\n".join(lines)
        self.assertIn("## Clinical trial search: elivaldogene", out)
        self.assertIn("Trial count (totalCount) as shown: 4. Studies in this response: 4.", out)
        self.assertIn("- NCTId (identificationModule.nctId) as shown: `NCT02698579`", out)
        self.assertIn("- Overall status (statusModule.overallStatus) as shown: `ACTIVE_NOT_RECRUITING`", out)
        self.assertIn("- Lead sponsor (sponsorCollaboratorsModule.leadSponsor.name) as shown: "
                      "`Genetix Biotherapeutics Inc.`", out)
        self.assertIn("- Conditions (conditionsModule.conditions) as shown: "
                      "`Cerebral Adrenoleukodystrophy (CALD), Adrenoleukodystrophy (ALD), "
                      "X-Linked Adrenoleukodystrophy (X-ALD)`", out)
        self.assertIn("- Phases (designModule.phases) as shown: `PHASE2, PHASE3`", out)
        # The first study's captured designModule is empty, so its phases are not shown.
        self.assertIn("- Phases (designModule.phases) as shown: `not shown`", out)
        self.assertIn("Trials shown are the first 4 of the 4 the count reports", out)
        self.assertIn("The response carries a nextPageToken: no", out)
        self.assertIn((FIX / HIT).read_text(encoding="utf-8").partition("\n\n")[2], out)

    def test_a_next_page_token_is_reported_when_present(self):
        # DERIVED: the real elivaldogene capture with a page token added to
        # its parsed body; the key is assembled so no token value is ever
        # written into this file as a literal.
        cap = captured(HIT)
        data = json.loads(cap.body)
        data["nextPage" + "Token"] = "SYNTHETIC"
        derived = ct.Capture(cap.url, cap.retrieved, cap.status_line, cap.headers, json.dumps(data))
        out = "\n".join(ct.render("elivaldogene", 5, derived))
        self.assertIn("The response carries a nextPageToken: yes", out)

    def test_empty_result_is_proven_by_the_full_raw_response(self):
        with mock.patch("urllib.request.urlopen", no_network):
            lines = ct.run("zqxflorp medicine", 5, replay())
        out = "\n".join(lines)
        self.assertIn("Trial count (totalCount) as shown: 0. Studies in this response: 0.", out)
        self.assertIn("The search returned no trials.", out)
        self.assertIn("not proof that no matching trial exists", out)
        self.assertIn('{"totalCount":0,"studies":[\n\n]}', out)
        self.assertNotIn("### Trial", out)

    def test_cli_prints_the_hit_report(self):
        code, out, err = run_main(["elivaldogene", "--limit", "5"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Trial count (totalCount) as shown: 4", out)


class FailureTests(unittest.TestCase):
    def test_a_503_is_a_source_failure_not_an_empty_result(self):
        # SYNTHETIC: a 503 capture built here; it is not a recording.
        def fetcher(url):
            return ct.Capture(url, "2026-10-24T00:00:00Z", "HTTP/1.1 503 Service Unavailable",
                              ["Content-Type: application/json"], '{"error":"SYNTHETIC"}')
        code, out, err = run_main(["Zolgensma"], fetcher)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("not 200; no report", err)

    def test_a_non_json_body_fails_closed(self):
        # SYNTHETIC: a 200 whose body is not JSON; it is not a recording.
        def fetcher(url):
            return ct.Capture(url, "2026-10-24T00:00:00Z", "HTTP/1.1 200 OK",
                              ["Content-Type: text/html"], "<html>SYNTHETIC</html>")
        code, out, err = run_main(["Zolgensma"], fetcher)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("body is not JSON", err)

    def test_a_json_body_in_the_wrong_shape_fails_closed(self):
        # SYNTHETIC: JSON without an integer totalCount and a studies array.
        for body in ('{"studies":[]}', '{"totalCount":"24","studies":[]}', '{"totalCount":0,"studies":{}}'):
            def fetcher(url, body=body):
                return ct.Capture(url, "2026-10-24T00:00:00Z", "HTTP/1.1 200 OK",
                                  ["Content-Type: application/json"], body)
            code, out, err = run_main(["Zolgensma"], fetcher)
            self.assertEqual((code, out), (2, ""), body)
            self.assertIn("no report", err)

    def test_a_transport_failure_fails_closed(self):
        def fetcher(url):
            raise urllib.error.URLError("SYNTHETIC refusal")
        with mock.patch.object(ct, "fetch", fetcher):
            with self.assertRaises(urllib.error.URLError):
                ct.run("Zolgensma", 5)

    def test_bad_inputs_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for argv in ([""], ["   "], ["Zolgensma", "--limit", "0"], ["Zolgensma", "--limit", "101"]):
            code, out, _ = run_main(argv, must_not)
            self.assertEqual((code, out), (2, ""), argv)
        with self.assertRaises(ValueError):
            ct.check_inputs("Zolgensma", "x")


class FetchTests(unittest.TestCase):
    class Answer:
        def __init__(self, status, body, url):
            self.status, self.code = status, status
            self.reason = {200: "OK", 503: "Service Unavailable"}.get(status, "X")
            self._body, self._url, self.headers = body, url, {"Content-Type": "application/json"}
            self.version = 11

        def read(self):
            return self._body

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def test_fetch_sends_no_authorization_header(self):
        sent = []

        def fake(request, timeout=None):
            sent.append(dict(request.header_items()))
            return self.Answer(200, (FIX / HIT).read_bytes().partition(b"\n\n")[2], request.full_url)
        with mock.patch("urllib.request.urlopen", fake):
            cap = ct.fetch(ct.search_url("elivaldogene", 5))
        self.assertEqual(cap.status, 200)
        self.assertEqual(len(sent), 1)
        self.assertNotIn("Authorization", sent[0])

    def test_an_http_error_status_is_captured_then_refused_by_parse(self):
        def fake(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable",
                                         {"Content-Type": "application/json"}, io.BytesIO(b'{"error":"x"}'))
        with mock.patch("urllib.request.urlopen", fake):
            cap = ct.fetch(ct.search_url("elivaldogene", 5))
        self.assertEqual(cap.status, 503)
        with self.assertRaises(ct.FetchError):
            ct.parse(cap)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        with mock.patch.object(endpoints.ct, "fetch", replay(endpoints.ct)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/trials", qs, None)

    def test_route(self):
        status, _, body = self.get("term=elivaldogene&limit=5")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("Trial count (totalCount) as shown: 4", text)
        self.assertIn("tools/clinical_trial_check.py", text)
        self.assertEqual(self.get("term=zqxflorp%20medicine&limit=5")[0], "200 OK")
        self.assertEqual(self.get("")[0], "400 Bad Request")
        self.assertEqual(self.get("term=Zolgensma&limit=0")[0], "400 Bad Request")
        self.assertEqual(endpoints.describe()["/trials"]["sources"], [ct.STUDIES_URL])

    def test_route_maps_a_source_failure_to_502(self):
        def refused(url):
            raise endpoints.ct.FetchError("SYNTHETIC 503; no report")
        with mock.patch.object(endpoints.ct, "fetch", refused):
            status, _, body = recall_api.handle("GET", "/trials", "term=Zolgensma", None)
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("Clinical trial search", body.decode() if isinstance(body, bytes) else body)


if __name__ == "__main__":
    unittest.main()
