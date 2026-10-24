"""Tests for api/endpoints.py and its routing in api/recall_api.py. No network.

Run from the repository root: python3 -m unittest discover -s api -v

Every fetcher is patched at its module `fetch` to serve recorded material
that already lives in this repo with its provenance: the USAspending,
ProPublica, EDGAR, PageSpeed and vPIC captures under tools/tests/fixtures, and
the FMCSA and CourtListener excerpts carried by their test modules (copied
from the published deliveries, with the test harness parts labelled there).
Where a recorded body is served in answer to a differently shaped query for
the sake of exercising a code path, the test says so where it happens.
No source figure is invented here.
"""

import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "tests"))

from api import endpoints, recall_api  # noqa: E402
from tools import app_lookup_check as al  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import domain_trust_check as dt  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import exchange_rate_check as fx  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import usaspending_awards as ua  # noqa: E402
from tools import vin_decode as vd  # noqa: E402
import test_courtlistener_recap as cl_fixtures  # noqa: E402
import test_fmcsa_carrier as fc_fixtures  # noqa: E402

FIXTURES = ROOT / "tools" / "tests" / "fixtures"
WALLET = "0x" + "ab" * 20


def get(path, query_string="", wallet=None):
    status, headers, body = recall_api.handle("GET", path, query_string, wallet)
    return status, dict(headers), body.decode("utf-8")


# ----------------------------------------------------------------------
# Routing and descriptor
# ----------------------------------------------------------------------

class RoutingTests(unittest.TestCase):
    def test_descriptor_lists_every_endpoint_with_tool_params_and_sources(self):
        doc = recall_api.descriptor(WALLET)
        self.assertEqual(sorted(doc["endpoints"]),
                         ["/app", "/awards", "/carrier", "/domain", "/formd", "/fx", "/github", "/litigation",
                          "/nonprofit", "/ofac", "/pagespeed", "/recall", "/vin"])
        for path, entry in doc["endpoints"].items():
            self.assertEqual(entry["method"], "GET", path)
            self.assertTrue(entry["tool"].startswith("tools/"), path)
            self.assertTrue(entry["params"], path)
            self.assertTrue(all(s.startswith("https://") for s in entry["sources"]), path)
        self.assertIn(fc.CENSUS_URL, doc["endpoints"]["/carrier"]["sources"])
        self.assertIn(ua.ENDPOINT, doc["endpoints"]["/awards"]["sources"])
        # The pre existing keys are untouched for existing clients.
        self.assertEqual(doc["endpoint"], "/recall")
        self.assertEqual(doc["payout_wallet"], WALLET)

    def test_method_and_unknown_path_rules_match_recall(self):
        for path in endpoints.ROUTES:
            self.assertEqual(recall_api.handle("POST", path, "", None)[0], "405 Method Not Allowed", path)
        self.assertEqual(recall_api.handle("GET", "/nope", "", None)[0], "404 Not Found")

    def test_bad_queries_are_400_with_no_fetch(self):
        cases = {
            "/carrier": ["", "usdot=2046&name=x", "usdot=abc", "name=x&source=census", "usdot=2046&source=bogus"],
            "/litigation": ["", "party=Jabil&filed_after=nope", "party=Jabil&list=-1", "party=Jabil&docket_details=maybe"],
            "/awards": ["", "recipient=Boeing&limit=0", "recipient=Boeing&start=2026-01-01", "naics=abc"],
            "/nonprofit": ["", "exclude=1=x", "ein=12"],
            "/pagespeed": ["", "url=notaurl", "url=https://a.example/&strategy=tablet",
                           "url=https://a.example/&exclude=https://b.example/=reason"],
            "/domain": ["", "domain=https://example.com/", "domain=example", "domain=a.example&domain=b.example"],
            "/app": ["", "name=Nike&country=usa", "name=Nike&limit=0", "name=Nike&limit=201", "name=Nike&limit=x"],
            "/vin": ["", "vin=1HGCM/2633A004352", "vin=1HGCM82633A0043521", "vin=1HGCM82633A004352&model_year=03",
                     "vin=1HGCM82633A004352&vin=1HGCM82643A004352"],
            "/fx": ["", "base=USD", "target=EUR", "base=US&target=EUR", "base=USD&target=usd",
                    "base=USD&target=EUR&amount=0", "base=USD&target=EUR&date=2024-13-01"],
        }
        patches = [patch.object(mod, "fetch", side_effect=AssertionError("no fetch expected"))
                   for mod in (fc, cl, ua, pp, ps, ef, vd, fx)]
        patches += [patch.object(dt, name, side_effect=AssertionError("no fetch expected"))
                    for name in ("fetch_doh", "fetch_site")]
        patches.append(patch.object(al, "fetch", side_effect=AssertionError("no fetch expected")))
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        for path, queries in cases.items():
            for qs in queries:
                status, headers, text = get(path, qs)
                self.assertEqual(status, "400 Bad Request", (path, qs, text))
                self.assertTrue(text.startswith("Bad request: "), (path, qs))
                self.assertEqual(headers["Content-Type"], recall_api.TEXT_PLAIN)


# ----------------------------------------------------------------------
# /carrier
# ----------------------------------------------------------------------

def fc_capture(url, body, status_line="HTTP/1.1 200 OK"):
    # Plain test headers; not a recording of any FMCSA header.
    return fc.Capture(url, "2026-10-22T21:37:45Z", status_line, ["Content-Type: application/json"], body, "utf-8")


class CarrierTests(unittest.TestCase):
    def test_census_source_for_a_usdot_renders_the_record_and_transcript(self):
        url = fc.census_record_url("2046")
        cap = fc_capture(url, fc_fixtures.CENSUS_BODY_2046)
        with patch.object(fc, "fetch", side_effect=lambda u: cap if u == url else AssertionError(u)) as fetch:
            status, headers, text = get("/carrier", "usdot=2046&source=census&subject=GARDA+CL+CENTRAL+INC", WALLET)
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertEqual(headers["X-Payout-Wallet"], WALLET)
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(text.startswith("# Carrier vetting: GARDA CL CENTRAL INC\n"))
        self.assertIn("tools/fmcsa_carrier.py", text)
        self.assertIn("## Carrier: GARDA CL CENTRAL INC", text)
        self.assertIn("- legal_name as shown: GARDA CL CENTRAL INC", text)
        self.assertIn("- Query URL: " + url + "\n- Retrieved (UTC): 2026-10-22T21:37:45Z", text)
        self.assertIn(cap.transcript, text)

    def test_name_search_exclusion_not_in_response_is_400(self):
        # The recorded USDOT 2046 Census record is served here as the body of a
        # name search response, to exercise the exclusion rule; this pairing of
        # query and body is a test arrangement, not a recording.
        url = fc.census_name_url("GARDA", 50)
        cap = fc_capture(url, fc_fixtures.CENSUS_BODY_2046)
        with patch.object(fc, "fetch", return_value=cap):
            status, _, text = get("/carrier", "name=GARDA&exclude=999999=not+the+subject")
        self.assertEqual(status, "400 Bad Request", text)
        with patch.object(fc, "fetch", return_value=cap):
            status, _, text = get("/carrier", "name=GARDA&exclude=2046=a+different+carrier+with+a+similar+name")
        self.assertEqual(status, "200 OK", text)
        self.assertIn("## Carrier search: GARDA", text)

    def test_transport_failure_is_502_with_no_report(self):
        with patch.object(fc, "fetch", side_effect=OSError("connection refused")):
            status, _, text = get("/carrier", "usdot=2046")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("no report emitted", text)
        self.assertNotIn("## Carrier", text)


# ----------------------------------------------------------------------
# /litigation
# ----------------------------------------------------------------------

class LitigationTests(unittest.TestCase):
    def setUp(self):
        self.body = cl_fixtures.envelope([cl_fixtures.RECORD_D1, cl_fixtures.RECORD_D5, cl_fixtures.RECORD_D9], count=15)
        self.calls = []

        def fake_fetch(url, token=None):
            self.calls.append((url, token))
            if url != cl_fixtures.Q1_URL:
                raise AssertionError("unexpected url " + url)
            return cl.Capture(url, cl_fixtures.RETRIEVED, "HTTP/1.1 200 OK", ["Content-Type: application/json"], self.body)
        self.fake_fetch = fake_fetch

    def test_party_search_renders_table_and_transcript_beneath_the_query_url(self):
        with patch.object(cl, "fetch", side_effect=self.fake_fetch), patch.dict(os.environ, {}, clear=False):
            os.environ.pop(cl.TOKEN_ENV, None)
            status, headers, text = get("/litigation", "party=Jabil+Inc.&filed_after=2021-10-22")
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(self.calls, [(cl_fixtures.Q1_URL, None)])
        self.assertTrue(text.startswith("# Litigation screen: Jabil Inc.\n"))
        self.assertIn(cl.SCOPE_LINE, text)
        self.assertIn("| 1 | 0:26-cv-03269 | District Court, D. Minnesota | Andresen v. Jabil, Inc. |", text)
        self.assertIn("- Query URL: " + cl_fixtures.Q1_URL + "\n- Retrieved (UTC): " + cl_fixtures.RETRIEVED, text)
        self.assertIn("\n" + self.body + "\n```", text)

    def test_token_from_the_environment_is_sent_and_never_printed(self):
        with patch.object(cl, "fetch", side_effect=self.fake_fetch), \
             patch.dict(os.environ, {cl.TOKEN_ENV: "fake-token-for-tests-only-not-a-real-credential"}):
            status, _, text = get("/litigation", "party=Jabil+Inc.&filed_after=2021-10-22&list=2")
        self.assertEqual(status, "200 OK")
        self.assertEqual(self.calls[0][1], "fake-token-for-tests-only-not-a-real-credential")
        self.assertNotIn("fake-token", text)
        self.assertNotIn("| 3 |", text)  # list=2 limits the rows

    def test_exclusion_not_listed_is_400_and_transport_failure_is_502(self):
        with patch.object(cl, "fetch", side_effect=self.fake_fetch):
            status, _, text = get("/litigation", "party=Jabil+Inc.&filed_after=2021-10-22&exclude=1=not+listed")
        self.assertEqual(status, "400 Bad Request", text)
        with patch.object(cl, "fetch", side_effect=OSError("name resolution failed")):
            status, _, text = get("/litigation", "party=Jabil+Inc.")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## Subject", text)


# ----------------------------------------------------------------------
# /awards
# ----------------------------------------------------------------------

class AwardsTests(unittest.TestCase):
    META = json.loads((FIXTURES / "usaspending" / "recipient.meta.json").read_text(encoding="utf-8"))
    RAW = (FIXTURES / "usaspending" / "recipient.json").read_text(encoding="utf-8")

    def fake_fetch(self, request_body):
        self.assertEqual(request_body, self.META["request_body"])
        return ua.Capture(request_body, self.META["retrieved_utc"], self.RAW)

    def test_recipient_page_renders_with_the_exact_request_body_and_raw_response(self):
        with patch.object(ua, "fetch", side_effect=self.fake_fetch):
            status, headers, text = get("/awards", "recipient=Boeing&limit=2")
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Contract awards: Boeing\n"))
        self.assertIn("Exact query: POST " + ua.ENDPOINT, text)
        self.assertIn(self.META["request_body"], text)
        self.assertIn("Retrieved (UTC): " + self.META["retrieved_utc"], text)
        self.assertIn("Source: <%s>\n" % ua.ENDPOINT, text)
        self.assertIn(self.RAW.rstrip("\n"), text)

    def test_exclusion_not_on_the_page_is_400_and_fetch_failures_are_502(self):
        with patch.object(ua, "fetch", side_effect=self.fake_fetch):
            status, _, text = get("/awards", "recipient=Boeing&limit=2&exclude=NOT_ON_PAGE=reason")
        self.assertEqual(status, "400 Bad Request", text)
        self.assertNotIn("--exclude", text)
        for failure in (ValueError("unexpected HTTP status 500"), OSError("timed out"), TimeoutError("slow")):
            with patch.object(ua, "fetch", side_effect=failure):
                status, _, text = get("/awards", "recipient=Boeing&limit=2")
            self.assertEqual(status, "502 Bad Gateway", failure)
            self.assertNotIn("## USAspending", text)


# ----------------------------------------------------------------------
# /nonprofit
# ----------------------------------------------------------------------

class NonprofitTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "propublica" / "provenance.json").read_text(encoding="utf-8"))
    ORG = (FIXTURES / "propublica" / "organization-530196605.json").read_text(encoding="utf-8")
    SEARCH = (FIXTURES / "propublica" / "search-american-red-cross.json").read_text(encoding="utf-8")

    def setUp(self):
        self.org_url = self.PROVENANCE["organization-530196605.json"]["url"]
        self.search_url = self.PROVENANCE["search-american-red-cross.json"]["url"]
        bodies = {self.org_url: self.ORG, self.search_url: self.SEARCH}

        def fake_fetch(url):
            if url not in bodies:
                raise AssertionError("unexpected fetch " + url)
            return pp.Capture(url, "2026-10-23T03:35:58Z", "HTTP/1.1 200 OK", 200,
                              ["Content-Type: application/json"], bodies[url])
        self.fake_fetch = fake_fetch

    def test_ein_lookup_renders_identity_figures_and_transcript(self):
        self.assertEqual(hashlib.sha256(self.ORG.encode("utf-8")).hexdigest(),
                         self.PROVENANCE["organization-530196605.json"]["sha256"])
        with patch.object(pp, "fetch", side_effect=self.fake_fetch):
            status, _, text = get("/nonprofit", "ein=53-0196605")
        self.assertEqual(status, "200 OK", text)
        self.assertTrue(text.startswith("# Nonprofit diligence: 530196605\n"))
        self.assertIn("## ProPublica Nonprofit Explorer: 530196605", text)
        self.assertIn("Organization: EIN 530196605", text)
        self.assertIn(self.org_url, text)
        self.assertIn(self.ORG.rstrip("\n"), text)

    def test_name_search_then_organization_and_fetch_failure_is_502(self):
        with patch.object(pp, "fetch", side_effect=self.fake_fetch):
            status, _, text = get("/nonprofit", "name=American+Red+Cross&ein=530196605")
        self.assertEqual(status, "200 OK", text)
        self.assertIn(self.search_url, text)
        with patch.object(pp, "fetch", side_effect=pp.FetchError("connection refused")):
            status, _, text = get("/nonprofit", "ein=530196605")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## ProPublica", text)


# ----------------------------------------------------------------------
# /formd
# ----------------------------------------------------------------------

class FormDTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "edgar" / "provenance.json").read_text(encoding="utf-8"))
    CONTACT = "Test Operator operator@example.com"  # placeholder contact for tests, not a real address

    def captured(self, name):
        meta = self.PROVENANCE[name]
        transcript = (FIXTURES / "edgar" / name).read_bytes().decode("utf-8")
        return ef.Capture(meta["url"], meta["retrieved_utc"], transcript, transcript.partition("\n\n")[2])

    def fake_fetcher(self, *names):
        by_url = {self.PROVENANCE[n]["url"]: self.captured(n) for n in names}
        calls = []

        def fetch(url, contact):
            calls.append((url, contact))
            if url not in by_url:
                raise ef.FetchError("no recorded capture for %s" % url)
            return by_url[url]
        fetch.calls = calls
        return fetch

    def test_unset_contact_is_503_and_fetches_nothing(self):
        with patch.object(ef, "fetch", side_effect=AssertionError("no fetch expected")), \
             patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ef.CONTACT_ENV, None)
            status, headers, text = get("/formd", "cik=2156237")
        self.assertEqual(status, "503 Service Unavailable")
        self.assertIn(ef.CONTACT_ENV, text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_PLAIN)

    def test_cik_report_renders_filings_with_transcripts_and_sends_the_contact(self):
        fetch = self.fake_fetcher("submissions-2156237.http", "formd-0002156237-26-000001.http")
        with patch.object(ef, "fetch", side_effect=fetch), patch.object(ef, "pace"), \
             patch.dict(os.environ, {ef.CONTACT_ENV: self.CONTACT}):
            status, _, text = get("/formd", "cik=2156237")
        self.assertEqual(status, "200 OK", text)
        self.assertTrue(text.startswith("# Form D filings: CIK 2156237\n"))
        self.assertIn("#### Form D 0002156237-26-000001", text)
        self.assertIn('- Total offering amount as shown: "400000000"', text)
        for name in ("submissions-2156237.http", "formd-0002156237-26-000001.http"):
            cap = self.captured(name)
            self.assertIn("\nSource: <%s>\n```\n%s\n```" % (cap.url, cap.transcript), text)
        self.assertTrue(all(c == self.CONTACT for _, c in fetch.calls))
        self.assertNotIn(self.CONTACT, text)

    def test_bad_cik_is_400_and_fetch_failure_is_502(self):
        with patch.dict(os.environ, {ef.CONTACT_ENV: self.CONTACT}):
            self.assertEqual(get("/formd", "cik=2156237&issuer=x")[0], "400 Bad Request")
            self.assertEqual(get("/formd", "cik=notdigits")[0], "400 Bad Request")
            with patch.object(ef, "fetch", side_effect=ef.FetchError("HTTP 403")), patch.object(ef, "pace"):
                status, _, text = get("/formd", "cik=2156237")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## SEC EDGAR", text)


# ----------------------------------------------------------------------
# /pagespeed
# ----------------------------------------------------------------------

class PageSpeedTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "pagespeed" / "provenance.json").read_text(encoding="utf-8"))
    TRANSCRIPT = (FIXTURES / "pagespeed" / "keyless-429.http").read_text(encoding="utf-8")
    PAGE = "https://example.com/"  # the page named in the recorded keyless capture (an example domain)

    def fake_fetch(self, url, key=None, recorded=None):
        self.calls.append((url, key, recorded))
        head, body = self.TRANSCRIPT.split("\n\n", 1)
        lines = head.split("\n")
        return ps.Capture(recorded or url, self.PROVENANCE["keyless-429.http"]["retrieved_utc"], lines[0], lines[1:], body)

    def setUp(self):
        self.calls = []

    def test_keyless_429_capture_is_the_report_not_an_empty_result(self):
        with patch.object(ps, "fetch", side_effect=self.fake_fetch), patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ps.KEY_ENV, None)
            # The page is the example domain the recorded keyless capture was made for.
            status, _, text = get("/pagespeed", "url=https://example.com/")
        self.assertEqual(status, "200 OK", text)
        # example domain, as in the recorded capture
        self.assertTrue(text.startswith("# PageSpeed snapshot: example.com\n"))
        self.assertEqual(self.calls[0][0], ps.request_url(self.PAGE, "mobile"))
        self.assertIsNone(self.calls[0][1])
        self.assertIn("The API could not measure this page", text)
        self.assertIn("Quota exceeded", text)
        self.assertIn("HTTP/1.1 429 Too Many Requests", text)

    def test_key_from_the_environment_is_sent_but_never_printed(self):
        with patch.object(ps, "fetch", side_effect=self.fake_fetch), \
             patch.dict(os.environ, {ps.KEY_ENV: "fake-key-for-tests-only-not-a-real-credential"}):
            # example domain page, as in the recorded capture
            status, _, text = get("/pagespeed", "url=https://example.com/&strategy=desktop")
        self.assertEqual(status, "200 OK")
        self.assertEqual(self.calls[0][1], "fake-key-for-tests-only-not-a-real-credential")
        self.assertIn("key=" + ps.KEY_MARKER, self.calls[0][2])
        self.assertNotIn("fake-key", text)

    def test_too_many_pages_is_400_and_transport_failure_is_502(self):
        # Six example domain page URLs, one over the limit; none is fetched.
        six = "&".join("url=https://example.com/p%d" % i for i in range(6))
        with patch.object(ps, "fetch", side_effect=AssertionError("no fetch expected")):
            self.assertEqual(get("/pagespeed", six)[0], "400 Bad Request")
        with patch.object(ps, "fetch", side_effect=OSError("connection refused")):
            # example domain page; the fake transport fails before any fetch
            status, _, text = get("/pagespeed", "url=https://example.com/")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## Page", text)


# ----------------------------------------------------------------------
# /domain
# ----------------------------------------------------------------------

import test_domain_trust_check as dt_fixtures  # noqa: E402


class DomainTests(unittest.TestCase):
    """Served from the real captures in tools/tests/fixtures/domain-trust/."""

    def test_example_com_report_from_the_recorded_answers(self):
        with patch.object(dt, "fetch_doh", side_effect=dt_fixtures.by_url(*dt_fixtures.EXAMPLE_DNS)), \
             patch.object(dt, "fetch_site", side_effect=dt_fixtures.by_url("site-example.com.http")):
            status, headers, text = get("/domain", "domain=example.com", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Domain trust check: example.com\n"))  # example domain fixture
        self.assertIn("- SPF ending policy: `-all`, the final all mechanism of the record (source S3).", text)
        self.assertIn("- DMARC policy (p= tag as shown): `reject` (source S4).", text)

    def test_dns_transport_failure_is_502_with_no_report(self):
        with patch.object(dt, "fetch_doh", side_effect=OSError("connection refused")), \
             patch.object(dt, "fetch_site", side_effect=AssertionError("no site fetch expected")):
            status, _, text = get("/domain", "domain=example.com")  # example domain fixture
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## Domain", text)


# ----------------------------------------------------------------------
# /vin
# ----------------------------------------------------------------------

class VinTests(unittest.TestCase):
    """The vPIC bodies are the coordinator's Option B captures on issue #161
    (tools/tests/fixtures/vpic, provenance there). They carry bodies only, so
    the status and header lines here are a test harness, not a recording."""

    def served(self, name):
        body = (FIXTURES / "vpic" / name).read_text(encoding="utf-8")
        return "2026-10-24T01:38:00Z", "HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + body, body

    def test_clean_decode_renders_the_fetchers_section(self):
        prov = json.loads((FIXTURES / "vpic" / "provenance.json").read_text(encoding="utf-8"))
        url = prov["clean-1HGCM82633A004352.json"]["url"]
        cap = self.served("clean-1HGCM82633A004352.json")
        with patch.object(vd, "fetch", side_effect=lambda u: cap if u == url else AssertionError(u)) as fetch:
            status, headers, text = get("/vin", "vin=1hgcm82633a004352", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(text.startswith("# VIN decode: 1HGCM82633A004352\n"))
        self.assertIn("tools/vin_decode.py", text)
        section = "\n".join(vd.render_section("1HGCM82633A004352", None, url, *cap))
        self.assertIn(section, text)
        self.assertIn("DECODE: vehicle as shown: 2003 HONDA Accord EX-V6", text)

    def test_model_year_goes_into_the_query(self):
        cap = self.served("example-partial-5UXWX7C5-BA.json")
        with patch.object(vd, "fetch", return_value=cap) as fetch:
            status, _, text = get("/vin", "vin=5UXWX7C5*BA&model_year=2011")
        self.assertEqual(status, "200 OK", text)
        fetch.assert_called_once_with(
            "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/5UXWX7C5*BA?format=json&modelyear=2011")
        self.assertIn('"6 - Incomplete VIN"', text)

    def test_failed_fetch_is_502_with_no_report(self):
        import urllib.error
        with patch.object(vd, "fetch", side_effect=urllib.error.URLError("refused (test)")):
            status, _, text = get("/vin", "vin=1HGCM82633A004352")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("DECODE", text)


# ----------------------------------------------------------------------
# /app
# ----------------------------------------------------------------------

import test_app_lookup_check as al_fixtures  # noqa: E402


class AppTests(unittest.TestCase):
    """Served from the real captures in tools/tests/fixtures/app-lookup/."""

    def test_nike_search_from_the_recorded_response(self):
        with patch.object(al, "fetch", side_effect=al_fixtures.serve(al_fixtures.NIKE)):
            status, headers, text = get("/app", "name=Nike&limit=5", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# App lookup: Nike\n"))
        self.assertIn("- Seller (sellerName) as shown: `Nike, Inc`", text)
        self.assertIn("Exact name matches among the returned apps: 0 of 5 (source S1).", text)

    def test_transport_failure_is_502_with_no_report(self):
        with patch.object(al, "fetch", side_effect=OSError("connection refused")):
            status, _, text = get("/app", "name=Nike")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## App search", text)



# ----------------------------------------------------------------------
# /fx
# ----------------------------------------------------------------------

class ExchangeRateTests(unittest.TestCase):
    """Served from the coordinator's keyless Option B captures on issue #168
    (tools/tests/fixtures/frankfurter, provenance there)."""

    def served(self, name):
        transcript = (FIXTURES / "frankfurter" / name).read_text(encoding="utf-8")
        return "2026-10-24T03:06:03Z", transcript, transcript.partition("\n\n")[2]

    def test_amount_renders_the_fetchers_section(self):
        url = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR&amount=100"
        cap = self.served("latest-USD-EUR-amount-100.http")
        with patch.object(fx, "fetch", side_effect=lambda u: cap if u == url else AssertionError(u)) as fetch:
            status, headers, text = get("/fx", "base=usd&target=eur&amount=100", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(text.startswith("# Exchange rate: USD to EUR\n"))
        self.assertIn("tools/exchange_rate_check.py", text)
        self.assertIn("\n".join(fx.render_section("USD", "EUR", "100", None, url, *cap)), text)
        self.assertIn("RATE: 100.0 USD = 89.34 EUR, rate date 2026-10-23", text)

    def test_unknown_code_is_a_report_not_an_error(self):
        cap = self.served("latest-USD-XYZ-404.http")
        with patch.object(fx, "fetch", return_value=cap) as fetch:
            status, _, text = get("/fx", "base=USD&target=XYZ")
        fetch.assert_called_once_with("https://api.frankfurter.dev/v1/latest?base=USD&symbols=XYZ")
        self.assertEqual(status, "200 OK", text)
        self.assertIn("RATE: none returned for USD to XYZ.", text)
        self.assertIn("HTTP/1.1 404 Not Found", text)

    def test_failed_fetch_is_502_with_no_report(self):
        import urllib.error
        with patch.object(fx, "fetch", side_effect=urllib.error.URLError("refused (test)")):
            status, _, text = get("/fx", "base=USD&target=EUR")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("RATE:", text)


if __name__ == "__main__":
    unittest.main()
