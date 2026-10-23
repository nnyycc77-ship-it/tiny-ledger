"""Cross agent offline integration pass (issue #100).

For every agent in agents/ plus the brand checker, this suite runs the
agent's documented offline entry point on its committed or test generated
fixtures, in process, and asserts:

  1. the run completes with the documented success exit code;
  2. the report (or output file set) the README promises exists;
  3. the sections that agent's README promises are present in it, in
     the README's own words (each list below cites its README section);
  4. no network call is attempted: every run is wrapped in no_network(),
     which makes any socket connection or name lookup to a host other than
     loopback raise NetworkAttempt and fail the test.

Loopback stays open because the brand checker's documented offline path
replays its captured fixtures from a local server, exactly as its own suite
does. Proxy environment settings are cleared inside the guard, because a
proxy listening on loopback would otherwise carry an outside request past
the loopback allowance (the guard's own self test caught exactly that in a
proxied container). The guard covers sockets opened by Python in this process; the media
agents also run ffmpeg and ffprobe as subprocesses on local files only,
which the guard cannot see (they are given no URLs).

A failure here means a shared foundation or an agent drifted from what its
README promises. Fix the cause; never loosen an assertion to make it pass.

Run alone:  python3 -m unittest discover -s tools/tests -p 'test_agents_integration.py' -v
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
HAVE_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
LOOPBACK = {"127.0.0.1", "localhost", "::1"}
PROXY_VARS = {"http_proxy", "https_proxy", "all_proxy", "ftp_proxy"}


class NetworkAttempt(AssertionError):
    """An agent reached for a host other than loopback during an offline run."""


@contextlib.contextmanager
def no_network():
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_getaddrinfo = socket.getaddrinfo

    def check(address):
        if isinstance(address, tuple) and address and str(address[0]) not in LOOPBACK:
            raise NetworkAttempt("network call attempted to %r" % (address,))

    def connect(self, address):
        check(address)
        return real_connect(self, address)

    def connect_ex(self, address):
        check(address)
        return real_connect_ex(self, address)

    def getaddrinfo(host, *args, **kwargs):
        if host is not None and str(host) not in LOOPBACK:
            raise NetworkAttempt("name lookup attempted for %r" % (host,))
        return real_getaddrinfo(host, *args, **kwargs)

    # A proxy on loopback would otherwise carry an outside request past the
    # loopback allowance, so proxy settings are cleared for the run: any
    # outside request then has to resolve its real host, which is blocked.
    saved_env = {k: os.environ.pop(k) for k in list(os.environ) if k.lower() in PROXY_VARS}
    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
    try:
        yield
    finally:
        socket.socket.connect = real_connect
        socket.socket.connect_ex = real_connect_ex
        socket.getaddrinfo = real_getaddrinfo
        os.environ.update(saved_env)


def load(name, path):
    """Import an agent module by file path (agent folders are not packages)."""
    folder = str(Path(path).parent)
    if folder not in sys.path:
        sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(fn, *args, **kwargs):
    """Call an agent entry point under the network guard, capturing output."""
    out, err = io.StringIO(), io.StringIO()
    with no_network(), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fn(*args, **kwargs)
    return code, out.getvalue(), err.getvalue()


class GuardSelfTest(unittest.TestCase):
    """The guard itself: blocks the outside world, keeps loopback."""

    def test_external_lookup_and_connect_are_blocked(self):
        # SYNTHETIC example targets (example.com and its documentation IP);
        # the guard refuses them, so they are never contacted.
        with no_network():
            with self.assertRaises(NetworkAttempt):
                urllib.request.urlopen("https://example.com/", timeout=2)
            with self.assertRaises(NetworkAttempt):
                socket.create_connection(("93.184.216.34", 443), timeout=2)

    def test_an_agent_live_mode_is_caught(self):
        # catering-finder's documented live command fetches a page; under the
        # guard that reach must fail the run, not slip through.
        # SYNTHETIC example URL below; the guard refuses it, never contacted.
        mod = load("integ_catering_finder", AGENTS / "catering-finder" / "catering_finder.py")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NetworkAttempt):
                run(mod.main, ["capture", "https://example.com/menu", "--store", tmp,
                               "--id", "probe", "--name", "Probe"])

    def test_loopback_is_allowed(self):
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        try:
            with no_network():
                client = socket.create_connection(server.getsockname(), timeout=2)
                client.close()
        finally:
            server.close()


class Section:
    def assertSections(self, text, sections, where):
        missing = [s for s in sections if s not in text]
        self.assertEqual(missing, [], "%s is missing README promised section(s): %s"
                         % (where, missing))


class CateringFinder(unittest.TestCase, Section):
    # agents/catering-finder/README.md, "Run" and "### The report"
    SECTIONS = ["## Summary", "Counts:", "## Availability for", "## Vendors compared",
                "## Contacted with no reply", "## Declined", "## Checked and excluded",
                "## Outreach drafts", "## Sources"]

    def test_dry_run_on_fixture_store(self):
        mod = load("integ_catering_finder", AGENTS / "catering-finder" / "catering_finder.py")
        fx = AGENTS / "catering-finder" / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.md"
            code, _, err = run(mod.main, ["run", "--brief", str(fx / "brief.json"),
                                          "--store", str(fx), "--log", str(fx / "outreach-log.json"),
                                          "--out", str(report)])
            self.assertEqual(code, 0, err)
            self.assertSections(report.read_text(encoding="utf-8"), self.SECTIONS, "catering report")


class LocalQuotes(unittest.TestCase, Section):
    # agents/local-quotes/README.md, "What it does" and "### The report"
    SECTIONS = ["# Quote comparison:", "Collection window ends:", "Report run:",
                "Candidates checked:", "## Comparison", "## What the quotes cover",
                "## No response after the attempts listed", "## Phone only",
                "## Checked and excluded", "## Next steps for the buyer",
                "## Drafts recorded", "## Sources"]

    def test_dry_run_on_fixture_store(self):
        mod = load("integ_local_quotes", AGENTS / "local-quotes" / "local_quotes.py")
        fx = AGENTS / "local-quotes" / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.md"
            code, _, err = run(mod.main, ["run", "--request", str(fx / "request.json"),
                                          "--store", str(fx), "--log", str(fx / "outreach-log.json"),
                                          "--now", "2026-11-05T09:00:00Z", "--out", str(report)])
            self.assertEqual(code, 0, err)
            self.assertSections(report.read_text(encoding="utf-8"), self.SECTIONS, "quotes report")


class FieldServicePlanner(unittest.TestCase, Section):
    # agents/field-service-planner/README.md, "Run" and "What the report contains"
    SECTIONS = ["## Brief and inputs", "## Data problems", "### Schedule per crew member",
                "### Unassigned jobs", "### Gaps", "### Ranked backfill suggestions",
                "## Checked and excluded customers", "## Outreach drafts", "## Method"]

    def test_plan_on_fixture_places(self):
        mod = load("integ_planner", AGENTS / "field-service-planner" / "planner.py")
        fx = AGENTS / "field-service-planner" / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "plan.report.md"
            code, _, err = run(mod.main, ["plan", "--date", "2026-11-03",
                                          "--jobs", str(fx / "jobs.csv"), "--crew", str(fx / "crew.csv"),
                                          "--customers", str(fx / "customers.csv"),
                                          "--places", str(fx / "places.json"), "--out", str(report)],
                               env={})
            self.assertEqual(code, 0, err)
            self.assertSections(report.read_text(encoding="utf-8"), self.SECTIONS, "planner report")


class CallForMe(unittest.TestCase, Section):
    # agents/call-for-me/README.md, "Commands" (simulate) and "Simulation scenarios"
    SECTIONS = ["# Booking report:", "## Booking details", "## Alternatives the business offered",
                "## Every attempt", "## Next steps", "## What was kept"]

    def test_simulate_every_scenario(self):
        mod = load("integ_call_for_me", AGENTS / "call-for-me" / "call_for_me.py")
        scenarios = sorted((AGENTS / "call-for-me" / "scenarios").glob("*.json"))
        self.assertGreaterEqual(len(scenarios), 8)
        out, err = io.StringIO(), io.StringIO()
        with no_network():
            code = mod.main(["simulate"] + [str(s) for s in scenarios], stdout=out, stderr=err)
        text = out.getvalue()
        self.assertEqual(code, 0, err.getvalue())
        for s in scenarios:
            self.assertIn("PASS %s" % s.name, text)
        self.assertNotIn("FAIL", text)
        self.assertSections(text, self.SECTIONS, "booking reports")

    def test_call_command_always_refuses(self):
        mod = load("integ_call_for_me", AGENTS / "call-for-me" / "call_for_me.py")
        out, err = io.StringIO(), io.StringIO()
        with no_network():
            code = mod.main(["call"], stdout=out, stderr=err)
        self.assertEqual(code, 2)


class MediaGenerator(unittest.TestCase, Section):
    # agents/media-generator/README.md, "Run" and the acceptance table
    # (Delivered table names provider and model; Declined section says why).
    def test_generate_sample_scenarios_with_stubs(self):
        mod = load("integ_mediagen", AGENTS / "media-generator" / "mediagen.py")
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.json"
            # Example data: the README's four sample scenarios as one brief.
            brief.write_text(json.dumps({"requests": [
                {"type": "image", "subject": "ceramic mug on a wooden table", "count": 3,
                 "aspect": "1:1"},
                {"type": "video", "subject": "coffee pouring into a mug", "length_seconds": 8,
                 "aspect": "9:16"},
                {"type": "voice", "subject": "product voiceover",
                 "script": " ".join(["Fresh coffee every morning."] * 15)},
                {"type": "image", "subject": "a famous film star holding the mug",
                 "depicts_real_person": True},
            ]}), encoding="utf-8")
            out_dir = Path(tmp) / "out"
            code, _, err = run(mod.main, ["generate", "--brief", str(brief), "--out", str(out_dir)],
                               env={})
            self.assertEqual(code, 0, err)
            note = (out_dir / "delivery-note.md").read_text(encoding="utf-8")
            manifest = json.loads((out_dir / "delivery.json").read_text(encoding="utf-8"))
            self.assertSections(note, ["Delivered", "Declined"], "delivery note")
            self.assertTrue(manifest, "delivery.json is empty")
            media = [p for p in out_dir.iterdir() if p.suffix in (".png", ".gif", ".wav")]
            self.assertEqual(len(media), 5, sorted(p.name for p in out_dir.iterdir()))


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are needed for the video agents")
class VideoClipping(unittest.TestCase, Section):
    # agents/video-clipping/README.md, "Runbook" step 4 (manifest.json, report.md)
    def test_run_on_generated_fixture(self):
        clipper = load("integ_clipper", AGENTS / "video-clipping" / "clipper.py")
        fixture = load("integ_clipper_fixture", AGENTS / "video-clipping" / "tests" / "test_clipper.py")
        with tempfile.TemporaryDirectory() as tmp:
            video, words = fixture.make_fixture(Path(tmp))
            out_dir = Path(tmp) / "out"
            code, _, err = run(clipper.main, ["run", "--video", str(video), "--transcript", str(words),
                                              "--clips", "2", "--platforms", "tiktok",
                                              "--min-seconds", "8", "--max-seconds", "15",
                                              "--out", str(out_dir), "--preset", "ultrafast"])
            self.assertEqual(code, 0, err)
            report = (out_dir / "report.md").read_text(encoding="utf-8")
            self.assertTrue((out_dir / "manifest.json").is_file())
            self.assertSections(report, ["# Clips from", "## Clip 1:", "- Why this moment:",
                                         "- Transcript:", "- Files:"], "clipping report")
            self.assertEqual(len(list(out_dir.glob("clip_*_tiktok.mp4"))), 2)


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are needed for the video agents")
class VideoDubbing(unittest.TestCase, Section):
    # agents/video-dubbing/README.md, "Runbook" step 2 and the delivery note
    def test_run_on_generated_fixture(self):
        dubber = load("integ_dubber", AGENTS / "video-dubbing" / "dubber.py")
        fx = load("integ_dubber_fixture", AGENTS / "video-dubbing" / "tests" / "test_dubber.py")
        if not fx.HAVE_MEDIA:
            self.skipTest("ffmpeg flite filter is needed for the dubbing fixture")
        with tempfile.TemporaryDirectory() as tmp:
            holder = type("Holder", (), {})()
            holder.dir = Path(tmp)
            holder.video = holder.dir / "guide.mp4"
            fx.FixtureRunTests._make_video.__func__(holder)
            segments = holder.dir / "segments.json"
            segments.write_text(json.dumps({"segments": [
                {"start": a, "end": b, "text": t, "speaker": s} for a, b, t, s in fx.SEGMENTS]}),
                encoding="utf-8")
            glossary = holder.dir / "glossary.json"
            glossary.write_text(json.dumps(fx.GLOSSARY), encoding="utf-8")
            out_dir = holder.dir / "out"
            code, _, err = run(dubber.main, ["run", "--video", str(holder.video),
                                             "--segments", str(segments), "--glossary", str(glossary),
                                             "--languages", "es", "--voice", "stub",
                                             "--dnt", "Hojo,NEAR", "--out", str(out_dir)])
            self.assertEqual(code, 0, err)
            self.assertTrue((out_dir / "guide.es.mp4").is_file())
            self.assertTrue((out_dir / "guide.es.srt").is_file())
            self.assertSections((out_dir / "report.md").read_text(encoding="utf-8"),
                                ["# Dub of", "- Voice:", "- Background:", "- Subtitles:",
                                 "- Lines:", "## es", "- Compressed lines:"], "dubbing note")


class BrandNameChecker(unittest.TestCase, Section):
    # tools/README.md, "brand_name_checker.py": a domains table, a handles
    # table, App Store matches and a trademark section, replayed offline from
    # the captured fixtures through the same loopback server its suite uses.
    SECTIONS = ["nike.com", "| x |", "| instagram |", "| tiktok |", "exact name match",
                "### Trademarks", "Not covered."]

    def test_replay_from_captured_fixtures(self):
        tests_dir = str(ROOT / "tools" / "tests")
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        harness = load("integ_bnc_harness", ROOT / "tools" / "tests" / "test_brand_name_checker.py")
        bnc = harness.bnc
        import threading
        server = harness.Server(("127.0.0.1", 0), harness.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        saved = (bnc.RDAP_BASE, bnc.X_BASE, bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH)
        bnc.RDAP_BASE, bnc.X_BASE = base + "/rdap/domain/", base + "/x/"
        bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH = (
            base + "/ig/", base + "/tt/@", base + "/itunes/search")
        try:
            code, out, err = run(bnc.main, ["Nike", "--app-limit", "2"])
        finally:
            bnc.RDAP_BASE, bnc.X_BASE, bnc.INSTAGRAM_BASE, bnc.TIKTOK_BASE, bnc.ITUNES_SEARCH = saved
            server.shutdown()
            server.server_close()
        self.assertEqual(code, 0, err)
        self.assertSections(out, self.SECTIONS, "brand report")


class Coverage(unittest.TestCase):
    """Every agent folder has a case here, so a new agent cannot ship untested."""

    COVERED = {"call-for-me", "catering-finder", "field-service-planner", "local-quotes",
               "media-generator", "video-clipping", "video-dubbing"}

    def test_every_agent_folder_is_covered(self):
        present = {p.name for p in AGENTS.iterdir() if p.is_dir() and not p.name.startswith(".")}
        self.assertEqual(present - self.COVERED, set(),
                         "agent folder(s) with no integration case: add one to this suite")


if __name__ == "__main__":
    unittest.main()
