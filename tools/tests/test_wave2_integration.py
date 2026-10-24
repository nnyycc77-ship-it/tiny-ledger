"""Offline integration pass over the wave 2 API endpoints (issue #212).

Run:  python3 -m unittest discover -s tools/tests -p 'test_wave2_integration.py' -v

In the pattern of tools/tests/test_agents_integration.py (issue #100): every
check runs through recall_api.handle, the host-free entry point the WSGI app
serves, for the eight wave 2 routes on main:

    /flood /safety /fda /epa /csl /oig /insider /faa

For each route, three things are checked against the recorded fixtures that
already live in this repo, served by each tool test module's own replay
helper (so every body is the same capture, with its provenance, that the
tool's own tests use):

1. Same text (one test per route). The endpoint's 200 body is the fetcher's own Markdown, byte for
   byte: it equals what the tool's command line prints for the same inputs on
   the same replayed fixtures. For the routes whose dispatcher adds a title
   block (api/endpoints.py says "This module adds a title block and nothing
   else"), the body is exactly that block followed by the command line's
   output.
2. Bad query. A query the route must refuse answers 400 with a plain text
   reason, and no fetch is made: the source fetch is replaced by one that
   fails the test if it is called.
3. Unavailable source. A source failure answers 502 (and /insider without an
   operator contact answers 503) with no report in the body.

No network is used: urllib.request.urlopen is replaced, for the whole module,
by a function that fails the test. Where a check needs a source failure, the
failure is raised by the test (labelled "test failure"), not recorded.
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
for path in (str(ROOT), str(ROOT / "tools" / "tests")):
    if path not in sys.path:
        sys.path.insert(0, path)

from api import endpoints, recall_api  # noqa: E402
import test_csl_screen as t_csl  # noqa: E402
import test_epa_screen as t_epa  # noqa: E402
import test_faa_lookup as t_faa  # noqa: E402
import test_fda_recall_check as t_fda  # noqa: E402
import test_flood_check as t_flood  # noqa: E402
import test_insider_check as t_ins  # noqa: E402
import test_oig_screen as t_oig  # noqa: E402
import test_safety_file as t_safety  # noqa: E402

WAVE2 = ("/flood", "/safety", "/fda", "/epa", "/csl", "/oig", "/insider", "/faa")


def no_network(*args, **kwargs):
    raise AssertionError("the wave 2 integration pass tried to reach the network")


def never(*args, **kwargs):
    raise AssertionError("no fetch expected for a refused query")


def body_text(body):
    return body.decode("utf-8") if isinstance(body, bytes) else body


def cli(main, argv, streams=False, **kwargs):
    """Run a tool's main; returns (exit code, stdout, stderr).

    streams=True hands the capture buffers to a main that takes stdout and
    stderr arguments; the others print to sys.stdout, which is redirected.
    """
    out, err = io.StringIO(), io.StringIO()
    if streams:
        kwargs.update(stdout=out, stderr=err)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv, **kwargs)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def get(path, query, env=None):
    with mock.patch.dict(os.environ, env or {}, clear=env is not None):
        status, _, body = recall_api.handle("GET", path, query, None)
    return status, body_text(body)


# Each route: how to serve its fixtures to the dispatcher, how the tool's own
# command line prints the same inputs, a refused query, and how its source fails.

class Route:
    head = None  # title block lines the dispatcher adds, if any
    env = None  # environment the request is served under, if the route needs one

    def own(self):
        raise NotImplementedError


class Flood(Route):
    path, query = "/flood", "lat=27.9235&lon=-82.4515"
    bad = ("", "lat=27.9", "lat=95&lon=0", "lat=1&lon=2&address=x")

    def serve(self):
        return mock.patch.object(endpoints.fl, "fetch", t_flood.replay(endpoints.fl))

    def own(self):
        return cli(endpoints.fl.main, ["27.9235", "-82.4515"], fetcher=t_flood.replay(endpoints.fl), streams=True)

    def break_source(self):
        def refused(url):
            raise endpoints.fl.FetchError("test failure: connection closed")
        return mock.patch.object(endpoints.fl, "fetch", refused)

    def block_fetch(self):
        return mock.patch.object(endpoints.fl, "fetch", never)


class Fda(Route):
    path, query = "/fda", "name=peanut+butter&category=food&limit=3"
    bad = ("", "name=a", "name=ok&category=drug", "name=ok&limit=0")

    def serve(self):
        return mock.patch.object(endpoints.fda, "fetch", t_fda.replay(endpoints.fda))

    def own(self):
        return cli(endpoints.fda.main, ["peanut butter", "--category", "food", "--limit", "3"],
                   fetcher=t_fda.replay(endpoints.fda), streams=True)

    def break_source(self):
        def refused(url):
            raise endpoints.fda.FetchError("test failure: HTTP 500")
        return mock.patch.object(endpoints.fda, "fetch", refused)

    def block_fetch(self):
        return mock.patch.object(endpoints.fda, "fetch", never)


class Csl(Route):
    path, query = "/csl", "name=Mohammed%20Abu%20Teir"
    bad = ("", "name=ab")

    def __init__(self):
        self.tmp = tempfile.mkdtemp()

    def cache(self):
        return mock.patch.dict(os.environ, {"CSL_CACHE_DIR": tempfile.mkdtemp(dir=self.tmp)})

    @contextlib.contextmanager
    def serve(self):
        with self.cache(), mock.patch.object(endpoints.cs, "fetch", t_csl.replay()):
            yield

    def own(self):
        with self.cache():
            return cli(endpoints.cs.main, ["Mohammed Abu Teir"], fetcher=t_csl.replay(), streams=True)

    @contextlib.contextmanager
    def break_source(self):
        def refused(url):
            raise endpoints.cs.FetchError("test failure: HTTP 503")
        with self.cache(), mock.patch.object(endpoints.cs, "fetch", refused):
            yield

    @contextlib.contextmanager
    def block_fetch(self):
        with self.cache(), mock.patch.object(endpoints.cs, "fetch", never):
            yield


class Oig(Route):
    path, query = "/oig", "name=Aaron+Smith"
    bad = ("", "name=ab", "name=a.b")

    def serve(self):
        return mock.patch.object(endpoints.oig, "fetch", t_oig.replay(module=endpoints.oig))

    def own(self):
        return cli(endpoints.oig.main, ["Aaron Smith"], fetcher=t_oig.replay(module=endpoints.oig), streams=True)

    def break_source(self):
        def broken(url):
            raise endpoints.oig.FetchError("test failure: download failed")
        return mock.patch.object(endpoints.oig, "fetch", broken)

    def block_fetch(self):
        return mock.patch.object(endpoints.oig, "fetch", never)


class Insider(Route):
    path, query = "/insider", "cik=320193&max_filings=2"
    bad = ("", "cik=320193&issuer=Apple", "cik=abc", "cik=320193&max_filings=0")
    env = {"EDGAR_CONTACT": t_ins.CONTACT}

    def serve(self):
        return mock.patch.object(endpoints.ins, "fetch", t_ins.Fake(module=endpoints.ef))

    def own(self):
        return cli(endpoints.ins.main, ["--cik", "320193", "--max-filings", "2", "--contact", t_ins.CONTACT],
                   fetcher=t_ins.Fake(module=endpoints.ef), streams=True, env={})

    def break_source(self):
        def broken(url, contact):
            raise endpoints.ins.FetchError("test failure: download failed")
        return mock.patch.object(endpoints.ins, "fetch", broken)

    def block_fetch(self):
        return mock.patch.object(endpoints.ins, "fetch", never)


class Safety(Route):
    path, query = "/safety", "make=Hyundai&model=Elantra&year=2021"
    bad = ("", "make=Hyundai&model=Elantra", "make=Hyundai&model=Elantra&year=21")
    head = endpoints._head(
        "Safety file: 2021 Hyundai Elantra",
        "Observation only: this report records what the public NHTSA APIs returned for this model year at the "
        "retrieval times stated below; ratings, recalls and complaints are NHTSA's records as shown, not an "
        "inspection or a judgement of any vehicle.", "tools/safety_file.py")

    def serve(self):
        return mock.patch.object(endpoints.sf, "fetch", t_safety.served(t_safety.ELANTRA))

    def own(self):
        with mock.patch.object(endpoints.sf, "fetch", t_safety.served(t_safety.ELANTRA)):
            return cli(endpoints.sf.main, ["--make", "Hyundai", "--model", "Elantra", "--year", "2021"])

    def break_source(self):
        return mock.patch.object(endpoints.sf, "fetch", t_safety.served(t_safety.by_url(
            t_safety.RATINGS_EMPTY, t_safety.RECALLS_400, t_safety.COMPLAINTS_400)))

    def broken_query(self):
        return "make=Hyundai&model=Nosuchmodel&year=2021"

    def block_fetch(self):
        return mock.patch.object(endpoints.sf, "fetch", never)


class Epa(Route):
    path, query = "/epa", "name=BAYTOWN+OLEFINS&city=BAYTOWN&state=TX"
    bad = ("", "name=BAYTOWN+OLEFINS", "name=BAYTOWN+OLEFINS&state=Texas")
    head = endpoints._head(
        "EPA compliance screen: BAYTOWN OLEFINS, TX",
        "Observation only: this report records what the public EPA ECHO facility search returned at the "
        "retrieval times stated below; the status fields are ECHO's as shown, not a compliance finding of this "
        "service.", "tools/epa_screen.py")

    def fetcher(self):
        return t_epa.served(t_epa.SEARCH_HIT, t_epa.ROWS_HIT)

    def serve(self):
        return mock.patch.object(endpoints.epa, "fetch", self.fetcher())

    def own(self):
        with mock.patch.object(endpoints.epa, "fetch", self.fetcher()):
            return cli(endpoints.epa.main, ["--name", "BAYTOWN OLEFINS", "--city", "BAYTOWN", "--state", "TX"])

    def break_source(self):
        url = endpoints.epa.search_url("BAYTOWN OLEFINS", "TX", "BAYTOWN")
        return mock.patch.object(endpoints.epa, "fetch", t_epa.served(t_epa.DFR_500, as_url=url))

    def block_fetch(self):
        return mock.patch.object(endpoints.epa, "fetch", never)


class Faa(Route):
    path, query = "/faa", "n_number=N100ZT"
    bad = ("", "n_number=N", "n_number=N10-0Z", "n_number=N1234567")
    head = endpoints._head(
        "Aircraft registration: N100ZT",
        "Observation only: this report records what the FAA releasable aircraft database download, as retrieved "
        "at the time stated below, holds for this N number; the registration is a public record shown as the "
        "record states it.", "tools/faa_lookup.py")

    def __init__(self):
        self.tmp = tempfile.mkdtemp()
        self.source = t_faa.assemble(tempfile.mkdtemp(dir=self.tmp))

    def download(self, url, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)  # as faa_lookup.download does
        dest.write_bytes(self.source.read_bytes())
        return t_faa.captured_meta(dest)

    @contextlib.contextmanager
    def fresh_cache(self, download):
        # run() binds download as a default argument, so the fetch is handed
        # to it the way api/test_endpoints.py does, not patched on the module.
        real_run = endpoints.faa.run
        with mock.patch.dict(os.environ, {endpoints.faa.CACHE_ENV: tempfile.mkdtemp(dir=self.tmp)}), \
                mock.patch.object(endpoints.faa, "run", lambda n, *a, **kw: real_run(n, *a, **dict(kw, fetch=download))):
            yield

    def serve(self):
        return self.fresh_cache(self.download)

    def own(self):
        with self.fresh_cache(self.download):
            return cli(endpoints.faa.main, ["N100ZT"])

    def break_source(self):
        def refused(url, dest):
            raise endpoints.faa.SourceFailed("%s answered HTTP/1.1 403 Forbidden (test failure)" % url)
        return self.fresh_cache(refused)

    def block_fetch(self):
        return self.fresh_cache(never)


ROUTES = [Flood(), Safety(), Fda(), Epa(), Csl(), Oig(), Insider(), Faa()]


class Wave2Integration(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_the_pass_covers_every_wave2_route_on_main(self):
        self.assertEqual(sorted(r.path for r in ROUTES), sorted(WAVE2))
        for path in WAVE2:
            self.assertIn(path, endpoints.ROUTES)

    def test_each_refused_query_is_400_with_no_fetch(self):
        for route in ROUTES:
            for query in route.bad:
                with self.subTest(route=route.path, query=query), route.block_fetch():
                    status, body = get(route.path, query, route.env)
                    self.assertEqual(status, "400 Bad Request", body[:300])
                    self.assertTrue(body.startswith("Bad request: "), body[:300])

    def test_each_source_failure_is_502_with_no_report(self):
        for route in ROUTES:
            query = route.broken_query() if hasattr(route, "broken_query") else route.query
            with self.subTest(route=route.path), route.break_source():
                status, body = get(route.path, query, route.env)
            self.assertEqual(status, "502 Bad Gateway", body[:300])
            self.assertNotIn("\n## ", body)
            self.assertFalse(body.startswith("#"), body[:300])

    def test_insider_without_an_operator_contact_is_503_with_no_fetch(self):
        with Insider().block_fetch():
            status, body = get("/insider", "cik=320193", {})
        self.assertEqual(status, "503 Service Unavailable", body[:300])
        self.assertNotIn("\n## ", body)


# Drift filed as its own issue, not patched here (#212 rules): these routes'
# bodies end with one more "\n" than the command line prints. The assertion
# is unchanged; when #215 is fixed they report "unexpected success" and the
# entry is removed.
KNOWN_DRIFT = {"/flood": "#215", "/fda": "#215", "/oig": "#215"}


def same_text(route):
    def test(self):
        code, own, err = route.own()
        self.assertEqual(code, 0, err)
        with route.serve():
            status, body = get(route.path, route.query, route.env)
        self.assertEqual(status, "200 OK", body[:300])
        expected = own if route.head is None else "\n".join(route.head) + "\n" + own
        self.assertEqual(body, expected)
    test.__doc__ = "%s: the 200 body is the fetcher's own Markdown" % route.path
    return unittest.expectedFailure(test) if route.path in KNOWN_DRIFT else test


for _route in ROUTES:
    setattr(Wave2Integration, "test_200_body_is_the_fetchers_own_markdown_%s" % _route.path.strip("/"),
            same_text(_route))


if __name__ == "__main__":
    unittest.main()
