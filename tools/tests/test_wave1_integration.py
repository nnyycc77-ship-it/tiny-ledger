"""Offline integration pass over the wave 1 API endpoints (issue #219).

Run:  python3 -m unittest discover -s tools/tests -p 'test_wave1_integration.py' -v

In the pattern of tools/tests/test_wave2_integration.py (issue #212): every
check runs through recall_api.handle, the host-free entry point the WSGI app
serves, for the ten wave 1 routes from parent issue #158:

    /domain /ofac /vin /trials /drug /links /meta /github /app /fx

For each route, three things are checked against the recorded fixtures that
already live in this repo, served by each tool test module's own capture
helper (so every body is the same capture, with its provenance, that the
tool's own tests use):

1. Same text (one test per route). The endpoint's 200 body is the fetcher's
   own Markdown, byte for byte: it equals what the tool's command line prints
   for the same inputs on the same replayed fixtures. For the routes whose
   dispatcher adds a title block (endpoints._head), the body is exactly that
   block followed by the command line's output.
2. Bad query. A query the route must refuse answers 400 with a plain text
   reason, and no fetch is made: the source fetch is replaced by one that
   fails the test if it is called.
3. Unavailable source. A source failure answers 502 with no report in the
   body.

Both the command line and the endpoint read the same module object
(api/endpoints.py imports each tool as tools.<name>), and its fetch functions
are patched for both, so the two sides see the same capture.

No network is used: urllib.request.urlopen is replaced, for every test, by a
function that fails the test. Where a check needs a source failure, the
failure is raised by the test (labelled "test failure"), not recorded.
"""

import contextlib
import io
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

from api import endpoints, recall_api  # noqa: E402
import test_app_lookup_check as t_app  # noqa: E402
import test_broken_link_check as t_links  # noqa: E402
import test_clinical_trial_check as t_trials  # noqa: E402
import test_domain_trust_check as t_domain  # noqa: E402
import test_exchange_rate_check as t_fx  # noqa: E402
import test_fda_drug_check as t_drug  # noqa: E402
import test_github_repo_check as t_github  # noqa: E402
import test_meta_tag_check as t_meta  # noqa: E402
import test_ofac_sdn_check as t_ofac  # noqa: E402
import test_vin_decode as t_vin  # noqa: E402

WAVE1 = ("/domain", "/ofac", "/vin", "/trials", "/drug", "/links", "/meta", "/github", "/app", "/fx")


def no_network(*args, **kwargs):
    raise AssertionError("the wave 1 integration pass tried to reach the network")


def never(*args, **kwargs):
    raise AssertionError("no fetch expected for a refused query")


def body_text(body):
    return body.decode("utf-8") if isinstance(body, bytes) else body


def cli(main, argv):
    """Run a tool's main with stdout and stderr captured; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def get(path, query):
    status, _, body = recall_api.handle("GET", path, query, None)
    return status, body_text(body)


def only(url, capture):
    """A fetch that answers one URL with one capture and fails the test on any other."""
    def fetch(asked):
        if asked != url:
            raise AssertionError("unexpected url %s" % asked)
        return capture
    return fetch


def patches(module, **fetchers):
    stack = contextlib.ExitStack()
    for name, fetch in fetchers.items():
        stack.enter_context(mock.patch.object(module, name, fetch))
    return stack


# Each route: the module's fetch functions served from the fixtures, how the
# tool's own command line prints the same inputs, the refused queries, and a
# source failure. FETCHES names every fetch function the dispatcher can reach.

class Route:
    head = None  # title block lines the dispatcher adds, if any
    FETCHES = ("fetch",)

    def serve(self):
        return patches(self.module, **self.fetchers())

    def own(self):
        with self.serve():
            return cli(self.module.main, self.argv)

    def block_fetch(self):
        return patches(self.module, **{name: never for name in self.FETCHES})


class Domain(Route):
    module = endpoints.dt
    path, query, argv = "/domain", "domain=example.com", ["example.com"]  # example domain fixture
    bad = ("", "domain=https://example.com/", "domain=example", "domain=a.example&domain=b.example")
    FETCHES = ("fetch_doh", "fetch_site")
    head = endpoints._head(
        "Domain trust check: example.com",
        "Observation only: this report records what the Cloudflare DNS over HTTPS API and the site itself "
        "returned at the retrieval times stated below; it is not a security audit or a mail delivery "
        "assessment.", "tools/domain_trust_check.py")

    def fetchers(self):
        return {"fetch_doh": t_domain.by_url(*t_domain.EXAMPLE_DNS),
                "fetch_site": t_domain.by_url("site-example.com.http")}  # example domain fixture

    def break_source(self):
        def refused(url):
            raise OSError("test failure: connection refused")
        return patches(self.module, fetch_doh=refused, fetch_site=never)


class Ofac(Route):
    module = endpoints.ofac
    path, query, argv = "/ofac", "name=National+Bank+of+Cuba", ["National Bank of Cuba"]
    bad = ("", "name=ab", "name=a.b")

    def fetchers(self):
        return {"fetch": t_ofac.replay()}

    def break_source(self):
        def broken(url):
            raise self.module.FetchError("test failure: download failed")
        return patches(self.module, fetch=broken)


class Vin(Route):
    module = endpoints.vd
    path, query, argv = "/vin", "vin=1HGCM82633A004352", ["1HGCM82633A004352"]
    bad = ("", "vin=1HGCM/2633A004352", "vin=1HGCM82633A0043521", "vin=1HGCM82633A004352&model_year=03")
    head = endpoints._head(
        "VIN decode: 1HGCM82633A004352",
        "Observation only: this report records what the public NHTSA vPIC API returned for this VIN at the "
        "retrieval time stated below; the values and the error codes are vPIC's as shown, not an inspection "
        "of the vehicle.", "tools/vin_decode.py")

    def fetchers(self):
        return {"fetch": only(t_vin.PROVENANCE[t_vin.CLEAN]["url"], t_vin.capture(t_vin.CLEAN))}

    def break_source(self):
        def refused(url):
            raise urllib.error.URLError("test failure: refused")
        return patches(self.module, fetch=refused)


class Trials(Route):
    module = endpoints.ct
    path, query, argv = "/trials", "term=elivaldogene&limit=5", ["elivaldogene", "--limit", "5"]
    bad = ("", "term=Zolgensma&limit=0", "term=Zolgensma&limit=101", "term=Zolgensma&limit=x", "term=a&term=b")
    head = endpoints._head(
        "Clinical trial search: elivaldogene",
        "Observation only: this report records what the public ClinicalTrials.gov API v2 returned for this "
        "search at the retrieval time stated below, in the order returned; trial statuses and listings "
        "change, and it is not a review of any trial, drug, or sponsor.", "tools/clinical_trial_check.py")

    def fetchers(self):
        return {"fetch": t_trials.replay(module=self.module)}

    def break_source(self):
        def broken(url):
            raise self.module.FetchError("test failure: HTTP 503")
        return patches(self.module, fetch=broken)


class Drug(Route):
    module = endpoints.fd
    path, query, argv = "/drug", "name=Tylenol", ["Tylenol"]
    bad = ("", "name=", "name=Lipitor&name=Tylenol", 'name=say%20"cheese"')
    head = endpoints._head(
        "FDA drug label: Tylenol",
        "Observation only: this report records what the public openFDA drug label API returned for this "
        "name at the retrieval time stated below; the facts are the first returned label record's as shown, "
        "and the report is not medical advice.", "tools/fda_drug_check.py")

    def fetchers(self):
        return {"fetch": only(self.module.build_url("Tylenol"), t_drug.capture(t_drug.HIT))}

    def break_source(self):
        def refused(url):
            raise urllib.error.URLError("test failure: refused")
        return patches(self.module, fetch=refused)


class Links(Route):
    module = endpoints.bl
    path, argv = "/links", [t_links.PAGE_URL]
    query = "url=" + t_links.PAGE_URL
    bad = ("", "url=notaurl", "url=ftp://example.com/", "url=https://a.example/&url=https://b.example/")

    def fetchers(self):
        return {"fetch": t_links.replay()}

    def break_source(self):
        def broken(url, want_body=True):
            raise self.module.FetchError("test failure: request failed; no answer")
        return patches(self.module, fetch=broken)


class Meta(Route):
    module = endpoints.mt
    path, query, argv = "/meta", "url=https%3A%2F%2Fogp.me%2F", ["https://ogp.me/"]
    bad = ("", "url=notaurl", "url=https%3A%2F%2Fa.example%2F&url=https%3A%2F%2Fb.example%2F")

    def fetchers(self):
        return {"fetch": t_meta.replay(module=self.module)}

    def break_source(self):
        def broken(url):
            raise self.module.FetchError("test failure: HTTP 500")
        return patches(self.module, fetch=broken)


class Github(Route):
    module = endpoints.gh
    path, query, argv = "/github", "owner=psf&repo=requests", ["psf", "requests"]
    bad = ("", "owner=psf", "owner=psf/x&repo=y")

    def fetchers(self):
        return {"fetch": t_github.replay(module=self.module)}

    def break_source(self):
        def broken(url):
            raise self.module.FetchError("test failure: HTTP 403")
        return patches(self.module, fetch=broken)


class App(Route):
    module = endpoints.al
    path, query, argv = "/app", "name=Nike&limit=5", ["Nike", "--limit", "5"]
    bad = ("", "name=Nike&country=usa", "name=Nike&limit=0", "name=Nike&limit=201", "name=Nike&limit=x")
    head = endpoints._head(
        "App lookup: Nike",
        "Observation only: this report records what the public iTunes Search API returned for this search "
        "at the retrieval time stated below, in the order returned; it is not a review of any app.",
        "tools/app_lookup_check.py")

    def fetchers(self):
        return {"fetch": t_app.serve(t_app.NIKE)}

    def break_source(self):
        def refused(url):
            raise OSError("test failure: connection refused")
        return patches(self.module, fetch=refused)


class Fx(Route):
    module = endpoints.fx
    path, query, argv = "/fx", "base=USD&target=EUR", ["USD", "EUR"]
    bad = ("", "base=USD", "target=EUR", "base=US&target=EUR", "base=USD&target=usd",
           "base=USD&target=EUR&amount=0", "base=USD&target=EUR&date=2024-13-01")
    head = endpoints._head(
        "Exchange rate: USD to EUR",
        "Observation only: this report records what the public Frankfurter API returned at the retrieval "
        "time stated below; the rate, its date and any converted amount are the API's own figures as shown, "
        "not a quote to trade at.", "tools/exchange_rate_check.py")

    def fetchers(self):
        return {"fetch": only(self.module.build_url("USD", "EUR", None, None), t_fx.capture(t_fx.LATEST))}

    def break_source(self):
        def refused(url):
            raise urllib.error.URLError("test failure: refused")
        return patches(self.module, fetch=refused)


ROUTES = [Domain(), Ofac(), Vin(), Trials(), Drug(), Links(), Meta(), Github(), App(), Fx()]


class Wave1Integration(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_the_pass_covers_every_wave1_route_on_main(self):
        self.assertEqual(sorted(r.path for r in ROUTES), sorted(WAVE1))
        for path in WAVE1:
            self.assertIn(path, endpoints.ROUTES)

    def test_each_refused_query_is_400_with_no_fetch(self):
        for route in ROUTES:
            for query in route.bad:
                with self.subTest(route=route.path, query=query), route.block_fetch():
                    status, body = get(route.path, query)
                    self.assertEqual(status, "400 Bad Request", body[:300])
                    self.assertTrue(body.startswith("Bad request: "), body[:300])

    def test_each_source_failure_is_502_with_no_report(self):
        for route in ROUTES:
            with self.subTest(route=route.path), route.break_source():
                status, body = get(route.path, route.query)
            self.assertEqual(status, "502 Bad Gateway", body[:300])
            self.assertNotIn("\n## ", body)
            self.assertFalse(body.startswith("#"), body[:300])


# Drift is filed as its own issue, not patched here (#219 rules). A route
# listed here keeps its byte for byte assertion, marked as an expected failure
# citing the issue; when the issue is fixed it reports "unexpected success"
# and the entry is removed.
KNOWN_DRIFT = {}


def same_text(route):
    def test(self):
        code, own, err = route.own()
        self.assertEqual(code, 0, err)
        with route.serve():
            status, body = get(route.path, route.query)
        self.assertEqual(status, "200 OK", body[:300])
        expected = own if route.head is None else "\n".join(route.head) + "\n" + own
        self.assertEqual(body, expected)
    test.__doc__ = "%s: the 200 body is the fetcher's own Markdown" % route.path
    return unittest.expectedFailure(test) if route.path in KNOWN_DRIFT else test


for _route in ROUTES:
    setattr(Wave1Integration, "test_200_body_is_the_fetchers_own_markdown_%s" % _route.path.strip("/"),
            same_text(_route))


if __name__ == "__main__":
    unittest.main()
