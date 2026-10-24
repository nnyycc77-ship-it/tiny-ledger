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
from tools import broken_link_check as bl  # noqa: E402
from tools import clinical_trial_check as ct  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import domain_trust_check as dt  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import epa_screen as epa  # noqa: E402
from tools import exchange_rate_check as fx  # noqa: E402
from tools import disaster_history_check as dh  # noqa: E402
from tools import faa_lookup as faa  # noqa: E402
from tools import fda_drug_check as fd  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import safety_file as sf  # noqa: E402
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
                         ["/app", "/awards", "/bank", "/carrier", "/csl", "/disaster", "/domain", "/drug", "/epa",
                          "/faa", "/fda", "/flood", "/formd", "/fx", "/github", "/insider", "/links", "/litigation",
                          "/meta", "/nonprofit", "/npi", "/ofac", "/oig", "/pagespeed", "/recall", "/safety",
                          "/trials", "/vin", "/weather"])
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
            "/trials": ["", "term=Zolgensma&limit=0", "term=Zolgensma&limit=101", "term=Zolgensma&limit=x",
                        "term=a&term=b"],
            "/vin": ["", "vin=1HGCM/2633A004352", "vin=1HGCM82633A0043521", "vin=1HGCM82633A004352&model_year=03",
                     "vin=1HGCM82633A004352&vin=1HGCM82643A004352"],
            "/fx": ["", "base=USD", "target=EUR", "base=US&target=EUR", "base=USD&target=usd",
                    "base=USD&target=EUR&amount=0", "base=USD&target=EUR&date=2024-13-01"],
            "/safety": ["", "make=Hyundai&model=Elantra", "make=Hyundai&year=2021", "model=Elantra&year=2021",
                        "make=Hyundai&model=Elantra&year=21", "make=Hyundai&model=Elan/tra&year=2021"],
            "/epa": ["", "name=BAYTOWN+OLEFINS", "state=TX", "name=BAYTOWN+OLEFINS&state=Texas",
                     "name=BAYTOWN+OLEFINS&state=TX&registry_id=abc"],
            "/links": ["", "url=notaurl", "url=ftp://example.com/", "url=https://a.example/&url=https://b.example/"],
            "/drug": ["", "name=", "name=Lipitor&name=Tylenol", 'name=say%20"cheese"'],
            "/faa": ["", "n_number=N", "n_number=N10-0Z", "n_number=N1234567", "n_number=N1&n_number=N2"],
            "/disaster": ["", "state=R", "state=RIX", "state=RI&state=CT", "state=RI&limit=0", "state=RI&limit=1001",
                          "state=RI&limit=x", "state=RI&county=Prince+George%27s+(County)"],
        }
        patches = [patch.object(mod, "fetch", side_effect=AssertionError("no fetch expected"))
                   for mod in (fc, cl, ua, pp, ps, ef, vd, fx, sf, epa, bl, fd)]
        patches += [patch.object(dt, name, side_effect=AssertionError("no fetch expected"))
                    for name in ("fetch_doh", "fetch_site")]
        patches.append(patch.object(al, "fetch", side_effect=AssertionError("no fetch expected")))
        patches.append(patch.object(ct, "fetch", side_effect=AssertionError("no fetch expected")))
        patches.append(patch.object(faa, "download", side_effect=AssertionError("no fetch expected")))
        patches.append(patch.object(dh, "fetch", side_effect=AssertionError("no fetch expected")))
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
# /trials
# ----------------------------------------------------------------------

class TrialsTests(unittest.TestCase):
    """Served from the real captures in tools/tests/fixtures/clinical-trials/."""

    PROV = json.loads((FIXTURES / "clinical-trials" / "provenance.json").read_text(encoding="utf-8"))

    def served(self, name):
        meta = self.PROV[name]
        transcript = (FIXTURES / "clinical-trials" / name).read_text(encoding="utf-8")
        head, _, body = transcript.partition("\n\n")
        lines = head.split("\n")
        cap = ct.Capture(meta["url"], meta["retrieved_utc"], lines[0], lines[1:], body)

        def fetch(url):
            if url != meta["url"]:
                raise AssertionError("unexpected url %s" % url)
            return cap
        return fetch

    def test_hit_from_the_recorded_response(self):
        with patch.object(ct, "fetch", side_effect=self.served("search-elivaldogene-5.http")):
            status, headers, text = get("/trials", "term=elivaldogene&limit=5", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Clinical trial search: elivaldogene\n"))
        self.assertIn("tools/clinical_trial_check.py", text)
        self.assertIn("Trial count (totalCount) as shown: 4. Studies in this response: 4.", text)
        self.assertIn("- Overall status (statusModule.overallStatus) as shown: `ACTIVE_NOT_RECRUITING`", text)

    def test_empty_from_the_recorded_response(self):
        with patch.object(ct, "fetch", side_effect=self.served("search-zqxflorp-medicine-5.http")):
            status, _, text = get("/trials", "term=zqxflorp%20medicine&limit=5")
        self.assertEqual(status, "200 OK", text)
        self.assertIn("Trial count (totalCount) as shown: 0. Studies in this response: 0.", text)
        self.assertIn("The search returned no trials.", text)

    def test_source_failure_is_502_with_no_report(self):
        with patch.object(ct, "fetch", side_effect=ct.FetchError("SYNTHETIC 503; no report")):
            status, _, text = get("/trials", "term=Zolgensma")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("## Clinical trial search", text)



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




# ----------------------------------------------------------------------
# /links
# ----------------------------------------------------------------------

class BrokenLinkTests(unittest.TestCase):
    """Served from the captures in tools/tests/fixtures/broken-links (issue #164)."""

    def captured(self, name):
        import json as _json
        import re as _re
        fix = FIXTURES / "broken-links"
        prov = _json.loads((fix / "provenance.json").read_text(encoding="utf-8"))
        text = (fix / name).read_text(encoding="utf-8")
        head, _, body = text.partition("\n\n")
        lines = head.split("\n")
        headers = [tuple(line.split(": ", 1)) for line in lines[1:] if line]
        entry = prov[name]
        return bl.Capture(entry["url"], entry.get("final_url", entry["url"]), "2026-10-24T04:55:23Z",
                          int(_re.findall(r" (\d{3}) ", lines[0] + " ")[0]), lines[0], headers, body)

    def fetcher(self, url, want_body=True):
        pages = {"https://example.com/synthetic-broken-link-page": "page-with-dead.http",
                 "https://www.iana.org/robots.txt": "page-no-links.http"}
        targets = {"https://example.com/": "link-example-com.http",
                   "https://www.iana.org/domains/example": "link-iana-example.http",
                   "https://example.com/no-such-page-broken-link-check": "link-example-com-404.http"}
        if url in pages:
            return self.captured(pages[url])
        if url in targets:
            return self.captured(targets[url])
        raise AssertionError("unexpected url %s" % url)

    def test_page_with_a_dead_link_renders_the_report(self):
        # The fixture page and its recorded example targets.
        with patch.object(bl, "fetch", side_effect=self.fetcher):
            status, headers, text = get("/links", "url=https://example.com/synthetic-broken-link-page", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Broken link check: https://example.com/synthetic-broken-link-page\n"))
        self.assertIn("Dead links (final status 400 or above): 1", text)
        self.assertIn("- https://example.com/no-such-page-broken-link-check -> HTTP/1.1 404 Not Found", text)

    def test_page_fetch_failure_is_502_with_no_report(self):
        # An example page URL; the fetch is patched to fail.
        with patch.object(bl, "fetch", side_effect=bl.FetchError("request failed (test); no answer")):
            status, _, text = get("/links", "url=https://example.com/")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("Dead links", text)


# ----------------------------------------------------------------------
# /drug
# ----------------------------------------------------------------------

class DrugLabelTests(unittest.TestCase):
    """Served from H6's keyless live captures on issue #163
    (tools/tests/fixtures/openfda, provenance there)."""

    def served(self, name):
        transcript = (FIXTURES / "openfda" / name).read_text(encoding="utf-8")
        return "2026-10-24T04:59:59Z", transcript, transcript.partition("\n\n")[2]

    def test_hit_renders_the_fetchers_section(self):
        url = "https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22Tylenol%22+OR+openfda.generic_name:%22Tylenol%22&limit=1"
        cap = self.served("tylenol-hit.http")
        with patch.object(fd, "fetch", side_effect=lambda u: cap if u == url else AssertionError(u)) as fetch:
            status, headers, text = get("/drug", "name=Tylenol", WALLET)
        self.assertEqual(status, "200 OK", text)
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(text.startswith("# FDA drug label: Tylenol\n"))
        self.assertIn("tools/fda_drug_check.py", text)
        self.assertIn("\n".join(fd.render_section("Tylenol", url, *cap)), text)
        self.assertIn("- maker (openfda.manufacturer_name) as shown: Kenvue Brands LLC", text)
        self.assertIn("- warnings present: the record carries warnings.", text)

    def test_no_match_is_a_report_not_an_error(self):
        cap = self.served("no-match-404.http")
        with patch.object(fd, "fetch", return_value=cap) as fetch:
            status, _, text = get("/drug", "name=Zqxwvnotadrug")
        fetch.assert_called_once_with(
            "https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22Zqxwvnotadrug%22+OR+openfda.generic_name:%22Zqxwvnotadrug%22&limit=1")
        self.assertEqual(status, "200 OK", text)
        self.assertIn('LABEL: no drug label record matched "Zqxwvnotadrug".', text)
        self.assertIn("HTTP/1.1 404 Not Found", text)

    def test_failed_fetch_is_502_with_no_report(self):
        import urllib.error
        with patch.object(fd, "fetch", side_effect=urllib.error.URLError("refused (test)")):
            status, _, text = get("/drug", "name=Lipitor")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertNotIn("LABEL:", text)


# ----------------------------------------------------------------------
# /safety
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

class SafetyTests(unittest.TestCase):
    """Served from the coordinator's keyless Option B captures on issue #176
    (tools/tests/fixtures/nhtsa-safety, provenance there)."""

    PROV = json.loads((FIXTURES / "nhtsa-safety" / "provenance.json").read_text(encoding="utf-8"))

    def served(self, *names):
        by_url = {self.PROV[n]["url"]: n for n in names}

        def fetch(url):
            if url not in by_url:
                raise AssertionError("unexpected fetch: %s" % url)
            transcript = (FIXTURES / "nhtsa-safety" / by_url[url]).read_text(encoding="utf-8")
            return "2026-10-24T03:51:27Z", transcript, transcript.partition("\n\n")[2]
        return fetch

    def test_elantra_file_renders_every_section(self):
        fetch = self.served("ratings-2021-hyundai-elantra.http", "ratings-vehicle-15697.http",
                            "recalls-2021-hyundai-elantra.http", "complaints-2021-hyundai-elantra.http")
        with patch.object(sf, "fetch", fetch):
            status, headers, text = get("/safety", "make=Hyundai&model=Elantra&year=2021", WALLET)
        self.assertEqual(status, "200 OK", text[:500])
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Safety file: 2021 Hyundai Elantra\n"))
        self.assertIn("tools/safety_file.py", text)
        self.assertIn("- OverallRating as shown: 5", text)
        self.assertIn("RECALLS: 6 campaigns in the results array", text)
        self.assertIn("COMPLAINTS: 132 complaint records in the results array", text)

    def test_http_400_with_a_success_message_is_502_with_no_report(self):
        fetch = self.served("ratings-2021-hyundai-nosuchmodel-empty.http", "recalls-2021-hyundai-nosuchmodel-400.http",
                            "complaints-2021-hyundai-nosuchmodel-400.http")
        with patch.object(sf, "fetch", fetch):
            status, _, text = get("/safety", "make=Hyundai&model=Nosuchmodel&year=2021")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("source failure, no report emitted", text)
        self.assertIn("Recalls source failed: %s answered HTTP/1.1 400 Bad Request"
                      % self.PROV["recalls-2021-hyundai-nosuchmodel-400.http"]["url"], text)
        self.assertNotIn("RATINGS:", text)



# ----------------------------------------------------------------------
# /epa
# ----------------------------------------------------------------------

class EpaTests(unittest.TestCase):
    """Served from the coordinator's keyless Option B captures on issue #178
    (tools/tests/fixtures/epa-echo, provenance there), read as bytes so their
    CRLF line ends stay as recorded."""

    PROV = json.loads((FIXTURES / "epa-echo" / "provenance.json").read_text(encoding="utf-8"))

    def served(self, *names, as_url=None):
        by_url = {(as_url or self.PROV[n]["url"]): n for n in names}

        def fetch(url):
            if url not in by_url:
                raise AssertionError("unexpected fetch: %s" % url)
            text = (FIXTURES / "epa-echo" / by_url[url]).read_bytes().decode("utf-8")
            return "2026-10-24T05:10:25Z", text, text.split("\r\n\r\n", 2)[2]
        return fetch

    def test_registry_filter_answers_the_row_as_shown(self):
        fetch = self.served("search-baytown-olefins.http", "qid-baytown-olefins.http")
        with patch.object(epa, "fetch", fetch):
            status, headers, text = get("/epa", "name=BAYTOWN+OLEFINS&city=BAYTOWN&state=TX&registry_id=110000463178",
                                        WALLET)
        self.assertEqual(status, "200 OK", text[:500])
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# EPA compliance screen: BAYTOWN OLEFINS, TX\n"))
        self.assertIn('FacComplianceStatus "Significant Violation"; FacSNCFlg "Y"; FacQtrsWithNC "12"', text)

    def test_200_with_an_error_body_is_502_with_no_report(self):
        url = epa.search_url("BAYTOWN OLEFINS", "TX")
        with patch.object(epa, "fetch", self.served("facilities-by-id.http", as_url=url)):
            status, _, text = get("/epa", "name=BAYTOWN+OLEFINS&state=TX")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("source failure, no report emitted", text)
        self.assertIn("(Results carries an Error)", text)
        self.assertNotIn("ANSWER", text)


# ----------------------------------------------------------------------
# /faa
# ----------------------------------------------------------------------

class FaaTests(unittest.TestCase):
    """The archive is assembled from the coordinator's verbatim excerpt lines
    on issue #181 (tools/tests/fixtures/faa-registry) by the faa test
    module's own helper, a test arrangement; it stands in for the 73 MB
    download and is served through faa.run's fetch argument."""

    def test_hit_and_failure(self):
        import tempfile
        import test_faa_lookup as fx_faa
        with tempfile.TemporaryDirectory() as tmp:
            source = fx_faa.assemble(tempfile.mkdtemp(dir=tmp))

            def fetch(url, dest):
                dest.write_bytes(source.read_bytes())
                return fx_faa.captured_meta(dest)
            real_run = faa.run
            with patch.object(faa, "run", lambda n: real_run(n, folder=tmp, fetch=fetch)):
                status, headers, text = get("/faa", "n_number=n100zt", WALLET)
            self.assertEqual(status, "200 OK", text[:400])
            self.assertTrue(text.startswith("# Aircraft registration: N100ZT\n"))
            self.assertIn("- Registrant name (MASTER NAME): BANK OF UTAH TRUSTEE", text)
            self.assertIn("archive Last-Modified Sat, 24 Oct 2026 04:58:32 GMT", text)

        def failing(n):
            raise faa.SourceFailed("https://registry.faa.gov/database/ReleasableAircraft.zip answered HTTP/1.1 403 "
                                   "Forbidden (test)")
        with patch.object(faa, "run", failing):
            status, _, text = get("/faa", "n_number=N100ZT")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("source failure, no report emitted", text)


# ----------------------------------------------------------------------
# /disaster
# ----------------------------------------------------------------------

class DisasterTests(unittest.TestCase):
    """Served from the coordinator's Option B captures on issue #312
    (tools/tests/fixtures/openfema, provenance there). They carry bodies
    only, so the status line here is a test harness, not a recording."""

    PROV = json.loads((FIXTURES / "openfema" / "provenance.json").read_text(encoding="utf-8"))

    def served(self, name, status=200, url=None):
        want = url or self.PROV[name]["url"]
        text = (FIXTURES / "openfema" / name).read_bytes().decode("utf-8")

        def fetch(asked):
            if asked != want:
                raise AssertionError("unexpected fetch: %s" % asked)
            return "2026-10-24T12:10:00Z", status, "HTTP/1.1 %d (test harness line)\n\n%s" % (status, text), text
        return fetch

    def test_state_query_renders_the_fetchers_section(self):
        with patch.object(dh, "fetch", self.served("state-RI-top5-count.json")):
            status, headers, text = get("/disaster", "state=ri&limit=5", WALLET)
        self.assertEqual(status, "200 OK", text[:500])
        self.assertEqual(headers["Content-Type"], recall_api.TEXT_MD)
        self.assertTrue(text.startswith("# Disaster declarations: RI\n"))
        self.assertIn("tools/disaster_history_check.py", text)
        self.assertIn("FEMA's total of matching rows (metadata count, $count=true) as shown: 123.", text)
        self.assertIn("DISASTERS: 2 distinct disasterNumber values among the 5 rows returned", text)

    def test_county_goes_into_the_filter(self):
        url = dh.build_url("RI", "Kent (County)", 5)
        with patch.object(dh, "fetch", self.served("county-RI-Kent-top5.json", url=url)):
            status, _, text = get("/disaster", "state=RI&county=Kent+(County)&limit=5")
        self.assertEqual(status, "200 OK", text[:500])
        self.assertTrue(text.startswith("# Disaster declarations: Kent (County), RI\n"))

    def test_a_400_answer_is_502_with_no_report(self):
        url = dh.build_url("RI", None, 5)
        with patch.object(dh, "fetch", self.served("bad-field-400.json", status=400, url=url)):
            status, _, text = get("/disaster", "state=RI&limit=5")
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("source failure, no report emitted", text)
        self.assertIn("the answer is unknown", text)
        self.assertNotIn("DISASTERS", text)


if __name__ == "__main__":
    unittest.main()
