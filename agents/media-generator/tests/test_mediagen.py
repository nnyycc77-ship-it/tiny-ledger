"""Tests for agents/media-generator (issue #78). Offline, no keys, no spend.

Run from the repository root:
    python3 -m unittest discover -s agents/media-generator/tests -v

Every medium here is PLACEHOLDER output from the offline stub providers or
from the test providers defined below (subclasses of the stubs that miss on
purpose, labelled where they are defined). No live provider exists in this
build, and a test below checks that no module in the folder imports a
network library.
"""

import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

import mediagen  # noqa: E402
import mediagen_providers as mp  # noqa: E402
from mediagen_providers import image, placeholder, video, voice  # noqa: E402

QUALITY = mediagen.load_quality(mediagen.QUALITY_PATH)


def job(**fields):
    data = {"type": "image", "subject": "red fox in snow"}
    data.update(fields)
    return mediagen.Job(data)


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = self._tmp.name

    def path(self, *parts):
        return os.path.join(self.dir, *parts)


# ---------------------------------------------------------------- test providers
# Test only providers that miss on purpose, to drive the regeneration path.
# They are subclasses of the offline stubs and write placeholder media.

class DropsTermFirst(image.StubImage):
    """Test provider: on attempt 1 records a prompt without the subject's last
    term; on later attempts behaves like the stub."""
    name = "test-drops-term"

    def generate(self, j, out_dir, attempt):
        if attempt == 1:
            saved = j.prompt
            j.prompt = " ".join(w for w in saved.split() if w.strip(",.").lower() != j.terms[-1])
            try:
                return super().generate(j, out_dir, attempt)
            finally:
                j.prompt = saved
        return super().generate(j, out_dir, attempt)


class AlwaysDropsTerm(DropsTermFirst):
    """Test provider: drops the last subject term on every attempt."""
    name = "test-always-drops"

    def generate(self, j, out_dir, attempt):
        return DropsTermFirst.generate(self, j, out_dir, 1)


class BlankImage(image.StubImage):
    """Test provider: writes a one colour PNG (an obvious defect)."""
    name = "test-blank"

    def generate(self, j, out_dir, attempt):
        outs = []
        width, height = image.ASPECT_SIZES[j.aspect]
        for i in range(j.count):
            p = os.path.join(out_dir, "blank-%d-%d.png" % (i, attempt))
            import struct, zlib
            raw = b"".join(b"\x00" + b"\x10\x20\x30" * width for _ in range(height))
            data = b"\x89PNG\r\n\x1a\n" + placeholder._chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            data += placeholder._chunk(b"tEXt", b"Description\x00" + j.prompt.encode())
            data += placeholder._chunk(b"IDAT", zlib.compress(raw)) + placeholder._chunk(b"IEND", b"")
            with open(p, "wb") as fh:
                fh.write(data)
            outs.append(mp.Output(p, "png", j.prompt, self.name, placeholder=True))
        return outs


class Broken(image.StubImage):
    """Test provider: raises a provider error on every attempt."""
    name = "test-broken"

    def generate(self, j, out_dir, attempt):
        raise mp.ProviderError("test provider failure")


def table(**rates):
    """A quality table for routing tests (test values, not a recorded run)."""
    return {"source": "test table", "providers": {
        n: {"briefs": 4, "passed": int(r * 4), "pass_rate": r, "recorded_utc": "test"} for n, r in rates.items()}}


# ---------------------------------------------------------------- brief

class BriefTests(unittest.TestCase):
    def test_defaults_and_terms(self):
        j = job()
        self.assertEqual((j.format, j.aspect, j.count, j.seconds), ("png", "1:1", 1, None))
        self.assertEqual(j.terms, ["red", "fox", "snow"])
        v = job(type="video", subject="waves on a beach")
        self.assertEqual((v.format, v.aspect, v.seconds, v.length_assumed), ("gif", "16:9", 5.0, True))
        s = mediagen.Job({"type": "voice", "subject": "greeting", "script": "one two three four five"})
        self.assertEqual((s.format, s.seconds, s.length_assumed), ("wav", 2.0, True))
        self.assertEqual(s.prompt, "greeting: one two three four five")

    def test_bad_briefs(self):
        cases = [
            ({"type": "song", "subject": "x y"}, "type must be one of"),
            ({"type": "image"}, "subject must be a non blank string"),
            ({"type": "image", "subject": "the of"}, "no content words"),
            ({"type": "image", "subject": "fox", "count": 0}, "count must be a positive integer"),
            ({"type": "image", "subject": "fox", "count": True}, "count must be a positive integer"),
            ({"type": "image", "subject": "fox", "aspect": "wide"}, "aspect must look like"),
            ({"type": "image", "subject": "fox", "length_seconds": 3}, "applies to video and voice"),
            ({"type": "voice", "subject": "fox"}, "needs a script"),
            ({"type": "voice", "subject": "fox", "script": "hi", "aspect": "1:1"}, "aspect applies to image and video"),
            ({"type": "image", "subject": "fox", "script": "hi"}, "script and voice apply to voice"),
            ({"type": "image", "subject": "fox", "references": "a.png"}, "references must be a list"),
            ({"type": "image", "subject": "fox", "rights_confirmed": "yes"}, "rights_confirmed must be true or false"),
            ({"type": "image", "subject": "fox", "colour": "red"}, "unknown brief field(s): colour"),
            ({"type": "video", "subject": "fox", "length_seconds": -1}, "length_seconds must be a positive number"),
        ]
        for data, needle in cases:
            with self.subTest(data=data):
                with self.assertRaises(mediagen.BriefError) as ctx:
                    mediagen.Job(data)
                self.assertIn(needle, str(ctx.exception))


# ---------------------------------------------------------------- rights

class RightsTests(TempDirCase):
    def test_reference_work_without_confirmation_is_refused_before_generating(self):
        j = job(references=["buyer-photo.jpg"])
        out = self.path("out")
        with self.assertRaises(mediagen.Refused) as ctx:
            mediagen.run(j, out, providers=[Broken(), image.StubImageRefs()], quality=QUALITY, env={})
        self.assertIn("rights_confirmed is not true", str(ctx.exception))
        self.assertFalse(os.path.exists(out))  # nothing written, and the Broken provider was never called

    def test_cli_refusal_exit_2_and_nothing_written(self):
        brief = self.path("brief.json")
        with open(brief, "w") as fh:
            json.dump({"type": "image", "subject": "fox", "references": ["a.png"], "rights_confirmed": False}, fh)
        err = io.StringIO()
        code = mediagen.main(["generate", "--brief", brief, "--out", self.path("out")], env={}, stdout=io.StringIO(), stderr=err)
        self.assertEqual(code, 2)
        self.assertIn("refused", err.getvalue())
        self.assertFalse(os.path.exists(self.path("out")))

    def test_confirmed_reference_work_routes_to_a_reference_following_provider(self):
        j = job(references=["buyer-photo.jpg"], rights_confirmed=True)
        result = mediagen.run(j, self.path("out"), quality=QUALITY, env={})
        self.assertEqual(result["chosen"].provider.name, "stub-image-refs")
        decisions = dict(result["decisions"])
        self.assertIn("does not follow reference material", decisions["stub-image"])
        note = mediagen.render_note(result, "brief.json", self.path("out"))
        self.assertIn("Reference material: 1 item(s); rights confirmed by the buyer: yes", note)


# ---------------------------------------------------------------- routing

class RoutingTests(unittest.TestCase):
    def test_rules_first(self):
        providers = mp.all_providers()
        ranked, decisions = mediagen.route(job(type="video", subject="waves", length_seconds=20), providers, QUALITY, {})
        self.assertEqual(ranked, [])
        self.assertIn("length 20.0s is over its 10s limit", dict(decisions)["stub-video"])
        ranked, decisions = mediagen.route(job(aspect="21:9"), providers, QUALITY, {})
        self.assertEqual(ranked, [])
        self.assertIn("aspect 21:9 not offered", dict(decisions)["stub-image"])
        ranked, decisions = mediagen.route(job(format="jpg"), providers, QUALITY, {})
        self.assertIn("format jpg not offered (png)", dict(decisions)["stub-image"])
        ranked, decisions = mediagen.route(job(count=6), providers, QUALITY, {})
        self.assertEqual([p.name for p in ranked], ["stub-image"])  # stub-image-refs allows 4 per call
        v = mediagen.Job({"type": "voice", "subject": "notice", "script": "hold the rail", "voice": "narrator-x"})
        ranked, decisions = mediagen.route(v, providers, QUALITY, {})
        self.assertEqual(ranked, [])
        self.assertIn("voice 'narrator-x' not offered (stock-a, stock-b)", dict(decisions)["stub-voice"])

    def test_live_slots_are_never_routed(self):
        for t in ("image", "video", "voice"):
            data = {"type": t, "subject": "fox"}
            if t == "voice":
                data["script"] = "hello"
            ranked, decisions = mediagen.route(mediagen.Job(data), mp.all_providers(), QUALITY, {"MEDIAGEN_IMAGE_KEY": "set"})
            self.assertTrue(all(not p.name.startswith("live-") for p in ranked))
            self.assertIn("excluded: not configured", dict(decisions)["live-%s" % t])
        with self.assertRaises(mp.NotConfigured):
            image.LiveImageSlot().generate(job(), "/nonexistent", 1)

    def test_quality_second(self):
        providers = [image.StubImage(), image.StubImageRefs()]
        ranked, _ = mediagen.route(job(), providers, table(**{"stub-image": 0.5, "stub-image-refs": 0.9}), {})
        self.assertEqual([p.name for p in ranked], ["stub-image-refs", "stub-image"])
        ranked, decisions = mediagen.route(job(), providers, table(**{"stub-image-refs": 0.1}), {})
        self.assertEqual([p.name for p in ranked], ["stub-image-refs", "stub-image"])
        self.assertIn("no recorded quality (ranked as 0)", dict(decisions)["stub-image"])

    def test_no_provider_is_a_brief_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(mediagen.BriefError) as ctx:
                mediagen.run(job(aspect="21:9"), os.path.join(d, "out"), quality=QUALITY, env={})
            self.assertIn("no configured provider can take this brief", str(ctx.exception))
            self.assertFalse(os.path.exists(os.path.join(d, "out")))


# ---------------------------------------------------------------- brief check

class CheckTests(TempDirCase):
    def test_stub_outputs_pass_for_each_type(self):
        cases = [(image.StubImage(), job(count=2, aspect="9:16")),
                 (video.StubVideo(), job(type="video", subject="waves on a beach", length_seconds=3)),
                 (voice.StubVoice(), mediagen.Job({"type": "voice", "subject": "welcome", "script": "welcome in", "length_seconds": 2}))]
        for prov, j in cases:
            with self.subTest(provider=prov.name):
                outs = prov.generate(j, self.dir, 1)
                per, overall = mediagen.check_attempt(j, outs)
                self.assertEqual(overall, [])
                self.assertEqual([m for _, m in per], [[]] * j.count)

    def test_each_miss_is_named(self):
        j = job(aspect="16:9")
        p = self.path("sq.png")
        placeholder.png_image(p, 64, 64, "red fox in snow")
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)), ["aspect is 64x64, not 16:9"])
        placeholder.png_image(p, 96, 54, "red fox")
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)),
                         ["subject term(s) missing from what the provider recorded it made: snow"])
        with open(p, "wb") as fh:
            fh.write(b"not an image")
        self.assertTrue(mediagen.check_output(j, mp.Output(p, "png", "", "t", True))[0].startswith("not a valid png file"))
        open(p, "wb").close()
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)), ["file is missing or empty"])
        v = job(type="video", subject="waves", length_seconds=4)
        g = self.path("v.gif")
        placeholder.gif_video(g, 64, 36, 2, 5, "waves")
        self.assertEqual(mediagen.check_output(v, mp.Output(g, "gif", "", "t", True)), ["length is 2.0s, not 4.0s"])
        placeholder.gif_video(g, 64, 36, 0.2, 5, "waves")
        self.assertIn("video is a single frame", mediagen.check_output(job(type="video", subject="waves", length_seconds=0.2),
                                                                     mp.Output(g, "gif", "", "t", True)))
        s = mediagen.Job({"type": "voice", "subject": "welcome", "script": "hi", "length_seconds": 1})
        w = self.path("s.wav")
        import wave
        with wave.open(w, "wb") as fh:
            fh.setnchannels(1)
            fh.setsampwidth(2)
            fh.setframerate(16000)
            fh.writeframes(b"\x00\x00" * 16000)
        self.assertIn("audio is silent", mediagen.check_output(s, mp.Output(w, "wav", "", "t", True)))

    def test_count_mismatch(self):
        j = job(count=3)
        outs = image.StubImage().generate(job(count=2), self.dir, 1)
        _, overall = mediagen.check_attempt(j, outs)
        self.assertEqual(overall, ["count is 2, not 3"])


# ---------------------------------------------------------------- regeneration

class RegenerationTests(TempDirCase):
    def run_with(self, providers, quality, **fields):
        return mediagen.run(job(**fields), self.path("out"), providers=providers, quality=quality, env={})

    def test_first_attempt_passes_no_regeneration(self):
        r = self.run_with([image.StubImage()], QUALITY)
        self.assertEqual(len(r["attempts"]), 1)
        self.assertTrue(r["chosen"].passed)
        self.assertIn("No regeneration was needed.", mediagen.render_note(r, "b.json", self.path("out")))

    def test_missed_subject_term_regenerates_once_with_an_adjusted_prompt(self):
        r = self.run_with([DropsTermFirst()], table(**{"test-drops-term": 1.0}))
        a1, a2 = r["attempts"]
        self.assertFalse(a1.passed)
        self.assertIn("snow", "; ".join(m for _, ms in a1.per for m in ms))
        self.assertEqual(a2.provider.name, "test-drops-term")
        self.assertEqual(a2.prompt, "red fox in snow. Must clearly show: snow")
        self.assertIn("prompt adjusted to name the missed subject terms", a2.why)
        self.assertTrue(a2.passed)
        self.assertIs(r["chosen"], a2)

    def test_defect_switches_to_the_next_ranked_provider(self):
        r = self.run_with([BlankImage(), image.StubImage()], table(**{"test-blank": 0.9, "stub-image": 0.5}))
        a1, a2 = r["attempts"]
        self.assertEqual(a1.provider.name, "test-blank")
        self.assertIn("image is blank (one colour)", a1.per[0][1])
        self.assertEqual(a2.provider.name, "stub-image")
        self.assertIn("next ranked provider", a2.why)
        self.assertIs(r["chosen"], a2)

    def test_second_miss_delivers_the_closest_with_a_note_and_rerun(self):
        r = self.run_with([AlwaysDropsTerm()], table(**{"test-always-drops": 1.0}), count=2)
        self.assertEqual(len(r["attempts"]), 2)  # one regeneration only
        self.assertFalse(r["chosen"].passed)
        self.assertEqual(len(r["delivered"]), 2)
        note = mediagen.render_note(r, "my brief.json", self.path("out"))
        self.assertIn("**Did not fully match the brief.** Both attempts missed.", note)
        self.assertIn("subject term(s) missing from what the provider recorded it made: snow", note)
        self.assertIn("python3 agents/media-generator/mediagen.py generate --brief 'my brief.json' --out", note)

    def test_provider_error_then_success_and_error_twice(self):
        r = self.run_with([Broken(), image.StubImage()], table(**{"test-broken": 1.0, "stub-image": 0.1}))
        self.assertIsNotNone(r["attempts"][0].error)
        self.assertEqual(r["chosen"].provider.name, "stub-image")
        out = self.path("out2")
        with self.assertRaises(mp.ProviderError) as ctx:
            mediagen.run(job(), out, providers=[Broken()], quality=table(**{"test-broken": 1.0}), env={})
        self.assertIn("no attempt produced any output", str(ctx.exception))
        self.assertFalse(os.path.exists(out))

    def test_never_more_than_two_attempts(self):
        for providers in ([AlwaysDropsTerm()], [BlankImage(), AlwaysDropsTerm(), image.StubImage()]):
            r = self.run_with(providers, table())
            self.assertLessEqual(len(r["attempts"]), 2)


# ---------------------------------------------------------------- CLI and note

class CliTests(TempDirCase):
    def test_generate_writes_media_and_a_note_with_hashes(self):
        brief = self.path("brief.json")
        with open(brief, "w") as fh:
            json.dump({"type": "video", "subject": "waves on a beach", "count": 1, "length_seconds": 3}, fh)
        out, err = io.StringIO(), io.StringIO()
        code = mediagen.main(["generate", "--brief", brief, "--out", self.path("out")], env={}, stdout=out, stderr=err)
        self.assertEqual(code, 0, err.getvalue())
        files = sorted(os.listdir(self.path("out")))
        self.assertEqual(files, ["delivery-note.md", "waves-on-a-beach-1.gif"])
        note = Path(self.path("out", "delivery-note.md")).read_text(encoding="utf-8")
        self.assertEqual(note, out.getvalue())
        digest = mediagen.sha256_file(self.path("out", "waves-on-a-beach-1.gif"))
        self.assertIn("`waves-on-a-beach-1.gif`, SHA-256 `%s` (placeholder)" % digest, note)
        for heading in ("## Brief", "## Routing", "## Attempts", "## Delivered", "## What the check covers"):
            self.assertIn(heading + "\n", note)
        self.assertIn("**Placeholder media.**", note)
        self.assertIn("- Length used: 3.0 s (from the brief)", note)
        self.assertIn("live-video: excluded: not configured", note)

    def test_bad_brief_file_is_exit_2(self):
        brief = self.path("brief.json")
        with open(brief, "w") as fh:
            fh.write("{not json")
        err = io.StringIO()
        self.assertEqual(mediagen.main(["generate", "--brief", brief, "--out", self.path("o")], env={},
                                       stdout=io.StringIO(), stderr=err), 2)
        self.assertIn("is not valid JSON", err.getvalue())
        self.assertFalse(os.path.exists(self.path("o")))


# ---------------------------------------------------------------- the recorded table and the offline rule

class RecordedTableTests(unittest.TestCase):
    def test_committed_table_matches_a_fresh_calibration_apart_from_the_time(self):
        fresh = mediagen.calibrate(env={}, now="T")
        committed = json.loads(Path(mediagen.QUALITY_PATH).read_text())
        def strip(t):
            out = json.loads(json.dumps(t))
            out.pop("source", None)
            for rec in out["providers"].values():
                rec.pop("recorded_utc", None)
            return out
        self.assertEqual(strip(committed), strip(fresh))
        self.assertIn("says nothing about any live provider", committed["label"])
        self.assertTrue(all(not n.startswith("live-") for n in committed["providers"]))

    def test_no_module_imports_a_network_library(self):
        pattern = re.compile(r"^\s*(?:import|from)\s+(urllib|http|socket|ssl|requests|ftplib|smtplib)\b", re.M)
        for path in list(FOLDER.glob("*.py")) + list((FOLDER / "mediagen_providers").glob("*.py")):
            with self.subTest(path=path.name):
                self.assertIsNone(pattern.search(path.read_text()), path)

    def test_placeholder_readers_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            placeholder.png_image(os.path.join(d, "a.png"), 40, 30, "lighthouse")
            w, h, texts, colours = placeholder.read_png(os.path.join(d, "a.png"))
            self.assertEqual((w, h, texts["Description"]), (40, 30, "lighthouse"))
            self.assertIn("placeholder", texts["Software"])
            placeholder.gif_video(os.path.join(d, "v.gif"), 40, 30, 1.0, 5, "globe")
            self.assertEqual(placeholder.read_gif(os.path.join(d, "v.gif"))[:4], (40, 30, 5, 1.0))
            placeholder.wav_voice(os.path.join(d, "s.wav"), 1.0, "hello")
            seconds, peak, comment = placeholder.read_wav(os.path.join(d, "s.wav"))
            self.assertEqual(seconds, 1.0)
            self.assertIn("placeholder tone, not speech", comment)


if __name__ == "__main__":
    unittest.main()
