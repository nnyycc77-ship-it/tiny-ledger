"""Tests for agents/media-generator (issue #78). Offline, no keys, no spend.

Run from the repository root:
    python3 -m unittest discover -s agents/media-generator/tests -v

Every medium here is PLACEHOLDER output from the offline stub providers or
from the test providers defined below (subclasses of the stubs that miss on
purpose, labelled where they are defined). The sample scenarios are the four
in the job description quoted on issue #78 (comment 6366897388). No live
provider exists in this build, and a test checks that no module in the
folder imports a network library.
"""

import io
import json
import os
import re
import struct
import sys
import tempfile
import unittest
import wave
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

import mediagen  # noqa: E402
import mediagen_providers as mp  # noqa: E402
from mediagen_providers import image, placeholder, policy, video, voice  # noqa: E402

QUALITY = mediagen.load_quality(mediagen.QUALITY_PATH)


def job(**fields):
    data = {"type": "image", "subject": "ceramic mug on a wooden table"}
    data.update(fields)
    return mediagen.Job(data)


def vjob(**fields):
    data = {"type": "voice", "subject": "shop welcome", "script": "Welcome to the shop, we open at nine."}
    data.update(fields)
    return mediagen.Job(data)


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = self._tmp.name

    def path(self, *parts):
        return os.path.join(self.dir, *parts)

    def write_brief(self, data, name="brief.json"):
        p = self.path(name)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return p

    def main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        code = mediagen.main(argv, env={}, stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()


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
        width, height = image.stub_size(j, image.ASPECT_SIZES)
        for i in range(j.count):
            p = os.path.join(out_dir, "blank-%d-%d.png" % (i, attempt))
            raw = b"".join(b"\x00" + b"\x10\x20\x30" * width for _ in range(height))
            data = b"\x89PNG\r\n\x1a\n" + placeholder._chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            data += placeholder._chunk(b"tEXt", b"Description\x00" + j.prompt.encode())
            data += placeholder._chunk(b"IDAT", zlib.compress(raw)) + placeholder._chunk(b"IEND", b"")
            with open(p, "wb") as fh:
                fh.write(data)
            outs.append(mp.Output(p, "png", j.prompt, self.name, placeholder=True, model="test-blank-1"))
        return outs


class SkipsAWord(voice.StubVoice):
    """Test provider: records the script with its last word left out."""
    name = "test-skips-word"

    def generate(self, j, out_dir, attempt):
        saved = j.script
        j.script = " ".join(saved.split()[:-1])
        try:
            return super().generate(j, out_dir, attempt)
        finally:
            j.script = saved


class Broken(image.StubImage):
    """Test provider: raises a provider error on every attempt."""
    name = "test-broken"

    def generate(self, j, out_dir, attempt):
        raise mp.ProviderError("test provider failure")


class NoResale(image.StubImage):
    """Test provider: its recorded terms do not allow commercial use."""
    name = "test-no-resale"
    capabilities = mp.Capabilities(formats=("png",), aspects=tuple(image.ASPECT_SIZES), max_count=8, offline=True,
                                   model="t", commercial_use=False, max_side=1024)


def table(kind="image", **rates):
    """A quality table for routing tests (test values, not a recorded run)."""
    return {"source": "test table", "providers": {
        n: {kind: {"briefs": 4, "passed": int(r * 4), "pass_rate": r, "recorded_utc": "test"}} for n, r in rates.items()}}


def one(j, providers, quality, tmp):
    return mediagen.generate_request(j, tmp, providers, quality, {})


# ---------------------------------------------------------------- brief

class BriefTests(unittest.TestCase):
    def test_defaults_terms_and_kinds(self):
        j = job()
        self.assertEqual((j.format, j.aspect, j.size, j.count, j.seconds, j.kind), ("png", "1:1", None, 1, None, "image"))
        self.assertEqual(j.terms, ["ceramic", "mug", "wooden", "table"])
        v = job(type="video", subject="coffee being poured into a cup")
        self.assertEqual((v.format, v.aspect, v.seconds, v.length_assumed), ("gif", "16:9", 5.0, True))
        self.assertEqual(v.terms, ["coffee", "poured", "cup"])
        s = vjob()
        self.assertEqual((s.format, s.seconds, s.length_assumed), ("wav", 3.2, True))
        self.assertEqual(job(size="80x60").size, (80, 60))
        self.assertIsNone(job(size="80x60").aspect)
        self.assertEqual(job(references=["a.png"], rights_confirmed=True).kind, "image+refs")
        self.assertIn("brand: navy and gold", job(brand="navy and gold").base_prompt)

    def test_multi_request_brief(self):
        jobs = mediagen.parse_brief({"requests": [{"type": "image", "subject": "mug"}, {"type": "voice", "subject": "hi there", "script": "hi"}]})
        self.assertEqual([(j.index, j.type) for j in jobs], [(1, "image"), (2, "voice")])
        for data, needle in [({"requests": []}, "non empty list"), ({"requests": [{"type": "image"}]}, "request 1: subject"),
                             ({"requests": [{"type": "image", "subject": "x"}], "extra": 1}, "holds only"),
                             ({"requests": [{"type": "image", "subject": "mug"}] * 21}, "at most 20")]:
            with self.subTest(needle=needle), self.assertRaises(mediagen.BriefError) as ctx:
                mediagen.parse_brief(data)
            self.assertIn(needle, str(ctx.exception))

    def test_bad_briefs(self):
        cases = [
            ({"type": "song", "subject": "x y"}, "type must be one of"),
            ({"type": "image"}, "subject must be a non blank string"),
            ({"type": "image", "subject": "the of"}, "no content words"),
            ({"type": "image", "subject": "mug", "count": 0}, "count must be a positive integer"),
            ({"type": "image", "subject": "mug", "count": True}, "count must be a positive integer"),
            ({"type": "image", "subject": "mug", "aspect": "wide"}, "aspect must look like"),
            ({"type": "image", "subject": "mug", "size": "big"}, "size must look like"),
            ({"type": "image", "subject": "mug", "size": "100x100", "aspect": "16:9"}, "does not have the aspect"),
            ({"type": "image", "subject": "mug", "length_seconds": 3}, "applies to video and voice"),
            ({"type": "voice", "subject": "mug"}, "needs a script"),
            ({"type": "voice", "subject": "mug", "script": "hi", "aspect": "1:1"}, "aspect and size apply"),
            ({"type": "image", "subject": "mug", "script": "hi"}, "script and voice apply to voice"),
            ({"type": "image", "subject": "mug", "references": "a.png"}, "references must be a list"),
            ({"type": "image", "subject": "mug", "rights_confirmed": "yes"}, "rights_confirmed must be true or false"),
            ({"type": "image", "subject": "mug", "person_consent": 1}, "person_consent must be true or false"),
            ({"type": "image", "subject": "mug", "colour": "red"}, "unknown brief field(s): colour"),
            ({"type": "video", "subject": "mug", "length_seconds": -1}, "length_seconds must be a positive number"),
        ]
        for data, needle in cases:
            with self.subTest(data=data):
                with self.assertRaises(mediagen.BriefError) as ctx:
                    mediagen.Job(data)
                self.assertIn(needle, str(ctx.exception))


# ---------------------------------------------------------------- content rules

class PolicyTests(TempDirCase):
    def rules(self, **fields):
        return [r for r, _ in policy.screen(job(**fields))]

    def test_each_rule(self):
        self.assertEqual(self.rules(), [])
        self.assertEqual(self.rules(references=["a.png"]), ["reference rights"])
        self.assertEqual(self.rules(references=["a.png"], rights_confirmed=True), [])
        self.assertEqual(self.rules(subject="a well-known celebrity holding the product"), ["real person without consent"])
        self.assertEqual(self.rules(subject="portrait of a named athlete", depicts_real_person=True), ["real person without consent"])
        self.assertEqual(self.rules(subject="portrait of me at my desk", depicts_real_person=True, person_consent=True), [])
        self.assertEqual(self.rules(subject="Pikachu on a beach"), ["copyrighted character"])
        self.assertEqual(self.rules(subject="mug with the Starbucks logo"), ["brand or logo not owned"])
        self.assertEqual(self.rules(subject="mug with our logo", brand_owned=True), [])
        self.assertEqual(self.rules(subject="nude figure study"), ["sexual content"])
        self.assertEqual(self.rules(subject="gory battle scene"), ["graphic violence"])
        self.assertEqual(self.rules(subject="fake news footage of a flood"), ["deceptive content"])
        self.assertEqual(self.rules(subject="mug", style="in the style of a deepfake"), ["deceptive content"])
        # word boundaries: "Mario" inside "Marion" is not the character
        self.assertEqual(self.rules(subject="Marion's bakery storefront"), [])
        self.assertEqual(self.rules(subject="a knight decapitated in battle"), ["graphic violence"])
        self.assertEqual(self.rules(subject="ad impersonating a bank"), ["deceptive content"])

    def test_declined_request_writes_its_reason_and_others_go_ahead(self):
        brief = self.write_brief({"requests": [
            {"type": "image", "subject": "ceramic mug on a wooden table", "count": 2},
            {"type": "image", "subject": "a well-known celebrity holding the product"}]})
        code, note, err = self.main(["generate", "--brief", brief, "--out", self.path("out")])
        self.assertEqual(code, 0, err)
        self.assertIn("## Request 2: image \"a well-known celebrity holding the product\"", note)
        self.assertIn("### Declined", note)
        self.assertIn("**real person without consent**: the brief names a real, identifiable person (celebrity)", note)
        files = sorted(os.listdir(self.path("out")))
        self.assertEqual([f for f in files if f.startswith("r2-")], [])
        self.assertEqual(len([f for f in files if f.startswith("r1-")]), 2)
        man = json.loads(Path(self.path("out", "delivery.json")).read_text())
        self.assertEqual(man["requests"][1]["declined"][0]["rule"], "real person without consent")

    def test_all_declined_is_exit_3_with_the_report(self):
        brief = self.write_brief({"type": "image", "subject": "mug", "references": ["buyer.jpg"]})
        code, note, err = self.main(["generate", "--brief", brief, "--out", self.path("out")])
        self.assertEqual(code, 3)
        self.assertIn("**reference rights**", note)
        self.assertEqual(sorted(os.listdir(self.path("out"))), ["delivery-note.md", "delivery.json"])

    def test_declined_request_never_reaches_a_provider(self):
        res = one(job(subject="Pikachu"), [Broken()], table(**{"test-broken": 1.0}), self.dir)
        self.assertEqual(res.attempts, [])
        self.assertEqual(res.declined[0][0], "copyrighted character")


# ---------------------------------------------------------------- routing

class RoutingTests(unittest.TestCase):
    def test_rules_first(self):
        providers = mp.all_providers()
        ranked, decisions = mediagen.route(job(type="video", subject="waves", length_seconds=20), providers, QUALITY, {})
        self.assertEqual(ranked, [])
        self.assertIn("length 20.0s is over its 10s limit", dict(decisions)["stub-video"])
        ranked, decisions = mediagen.route(job(aspect="21:9"), providers, QUALITY, {})
        self.assertIn("aspect 21:9 not offered", dict(decisions)["stub-image"])
        ranked, decisions = mediagen.route(job(size="2000x2000"), providers, QUALITY, {})
        self.assertIn("size 2000x2000 is over its 1024 px limit", dict(decisions)["stub-image"])
        ranked, decisions = mediagen.route(job(format="jpg"), providers, QUALITY, {})
        self.assertIn("format jpg not offered (png)", dict(decisions)["stub-image"])
        ranked, _ = mediagen.route(job(count=6), providers, QUALITY, {})
        self.assertEqual([p.name for p in ranked], ["stub-image"])  # stub-image-refs allows 4 per call
        ranked, decisions = mediagen.route(vjob(voice="narrator-x"), providers, QUALITY, {})
        self.assertEqual(ranked, [])
        self.assertIn("voice 'narrator-x' not offered", dict(decisions)["stub-voice"])
        ranked, decisions = mediagen.route(job(references=["a"], rights_confirmed=True), providers, QUALITY, {})
        self.assertEqual([p.name for p in ranked], ["stub-image-refs"])
        self.assertIn("does not follow reference material", dict(decisions)["stub-image"])
        ranked, decisions = mediagen.route(job(), [NoResale(), image.StubImage()], QUALITY, {})
        self.assertEqual([p.name for p in ranked], ["stub-image"])
        self.assertIn("do not allow commercial use", dict(decisions)["test-no-resale"])

    def test_live_slots_are_never_routed(self):
        for j in (job(), job(type="video", subject="waves"), vjob()):
            ranked, decisions = mediagen.route(j, mp.all_providers(), QUALITY, {"MEDIAGEN_IMAGE_KEY": "set"})
            self.assertTrue(all(not p.name.startswith("live-") for p in ranked))
            self.assertIn("excluded: not configured", dict(decisions)["live-%s" % j.type])
        with self.assertRaises(mp.NotConfigured):
            image.LiveImageSlot().generate(job(), "/nonexistent", 1)

    def test_quality_second_per_request_type(self):
        providers = [image.StubImage(), image.StubImageRefs()]
        ranked, _ = mediagen.route(job(), providers, table(**{"stub-image": 0.5, "stub-image-refs": 0.9}), {})
        self.assertEqual([p.name for p in ranked], ["stub-image-refs", "stub-image"])
        ranked, decisions = mediagen.route(job(), providers, table(**{"stub-image-refs": 0.1}), {})
        self.assertEqual([p.name for p in ranked], ["stub-image-refs", "stub-image"])
        self.assertIn("no recorded quality for image requests (ranked as 0)", dict(decisions)["stub-image"])
        # a record for another request type does not count for this one
        ranked, decisions = mediagen.route(job(), providers, table(kind="image+refs", **{"stub-image": 1.0}), {})
        self.assertIn("no recorded quality for image requests", dict(decisions)["stub-image"])

    def test_no_provider_is_reported_not_delivered(self):
        with tempfile.TemporaryDirectory() as d:
            res = one(job(aspect="21:9"), mp.all_providers(), QUALITY, d)
            self.assertEqual(res.failure, "no configured provider can take this request")
            self.assertIsNone(res.chosen)


# ---------------------------------------------------------------- brief check

class CheckTests(TempDirCase):
    def test_stub_outputs_pass_for_each_type(self):
        cases = [(image.StubImage(), job(count=2, aspect="9:16")),
                 (image.StubImage(), job(size="120x90")),
                 (video.StubVideo(), job(type="video", subject="coffee being poured into a cup", aspect="9:16", length_seconds=8)),
                 (voice.StubVoice(), vjob(length_seconds=30))]
        for prov, j in cases:
            with self.subTest(provider=prov.name, size=j.size):
                outs = prov.generate(j, self.dir, 1)
                per, overall = mediagen.check_attempt(j, outs)
                self.assertEqual(overall, [])
                self.assertEqual([m for _, m in per], [[]] * j.count)
                self.assertTrue(all(o.model for o in outs))

    def test_length_within_one_second(self):
        v = job(type="video", subject="waves", length_seconds=8)
        g = self.path("v.gif")
        for seconds, ok in ((7.0, True), (9.0, True), (6.8, False), (9.4, False)):
            placeholder.gif_video(g, 64, 36, seconds, 5, "waves")
            misses = mediagen.check_output(v, mp.Output(g, "gif", "", "t", True))
            self.assertEqual(misses == [], ok, (seconds, misses))

    def test_each_miss_is_named(self):
        j = job(subject="red fox in snow", aspect="16:9")
        p = self.path("sq.png")
        placeholder.png_image(p, 64, 64, "red fox in snow")
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)), ["aspect is 64x64, not 16:9"])
        placeholder.png_image(p, 96, 54, "red fox")
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)),
                         ["subject term(s) missing from what the provider recorded it made: snow"])
        placeholder.png_image(p, 100, 75, "red fox in snow")
        self.assertEqual(mediagen.check_output(job(subject="red fox in snow", size="80x60"), mp.Output(p, "png", "", "t", True)),
                         ["size is 100x75, not 80x60"])
        with open(p, "wb") as fh:
            fh.write(b"not an image")
        self.assertTrue(mediagen.check_output(j, mp.Output(p, "png", "", "t", True))[0].startswith("not a valid png file"))
        open(p, "wb").close()
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "png", "", "t", True)), ["file is missing or empty"])
        g = self.path("v.gif")
        placeholder.gif_video(g, 64, 36, 0.2, 5, "waves")
        self.assertIn("video is a single frame", mediagen.check_output(job(type="video", subject="waves", length_seconds=0.2),
                                                                     mp.Output(g, "gif", "", "t", True)))
        w = self.path("s.wav")
        with wave.open(w, "wb") as fh:
            fh.setnchannels(1)
            fh.setsampwidth(2)
            fh.setframerate(16000)
            fh.writeframes(b"\x00\x00" * 16000)
        misses = mediagen.check_output(vjob(length_seconds=1), mp.Output(w, "wav", "", "t", True))
        self.assertIn("audio is silent", misses)
        self.assertTrue(any(m.startswith("script not read word for word") for m in misses))

    def test_script_word_for_word(self):
        j = vjob(length_seconds=3)
        outs = SkipsAWord().generate(j, self.dir, 1)
        misses = mediagen.check_output(j, outs[0])
        self.assertEqual(misses, ["script not read word for word (recorded 7 word(s), script has 8)"])
        # punctuation and case do not count as changed words
        p = self.path("ok.wav")
        placeholder.wav_voice(p, 3, j.prompt, script="welcome to the SHOP we open at nine")
        self.assertEqual(mediagen.check_output(j, mp.Output(p, "wav", "", "t", True)), [])

    def test_count_mismatch(self):
        outs = image.StubImage().generate(job(count=2), self.dir, 1)
        _, overall = mediagen.check_attempt(job(count=3), outs)
        self.assertEqual(overall, ["count is 2, not 3"])


# ---------------------------------------------------------------- regeneration

class RegenerationTests(TempDirCase):
    def test_first_attempt_passes_no_regeneration(self):
        res = one(job(), [image.StubImage()], QUALITY, self.dir)
        self.assertEqual(len(res.attempts), 1)
        self.assertTrue(res.chosen.passed)

    def test_missed_subject_term_regenerates_once_with_an_adjusted_prompt(self):
        res = one(job(), [DropsTermFirst()], table(**{"test-drops-term": 1.0}), self.dir)
        a1, a2 = res.attempts
        self.assertFalse(a1.passed)
        self.assertEqual(a2.provider.name, "test-drops-term")
        self.assertEqual(a2.prompt, "ceramic mug on a wooden table. Must clearly show: table")
        self.assertIn("prompt adjusted to name the missed subject terms", a2.why)
        self.assertTrue(a2.passed)
        self.assertIs(res.chosen, a2)

    def test_defect_switches_to_the_next_ranked_provider(self):
        res = one(job(), [BlankImage(), image.StubImage()], table(**{"test-blank": 0.9, "stub-image": 0.5}), self.dir)
        a1, a2 = res.attempts
        self.assertEqual(a1.provider.name, "test-blank")
        self.assertIn("image is blank (one colour)", a1.per[0][1])
        self.assertEqual(a2.provider.name, "stub-image")
        self.assertIn("next ranked provider", a2.why)
        self.assertIs(res.chosen, a2)

    def test_second_miss_delivers_the_closest_with_a_note_and_rerun(self):
        results = mediagen.run([job(count=2)], self.path("out"), providers=[AlwaysDropsTerm()],
                               quality=table(**{"test-always-drops": 1.0}), env={})
        res = results[0]
        self.assertEqual(len(res.attempts), 2)  # one regeneration only
        self.assertFalse(res.chosen.passed)
        self.assertEqual(len(res.files), 2)
        note = mediagen.render_note(results, "my brief.json", self.path("out"), QUALITY, "T")
        self.assertIn("**Did not fully match the brief.** Both attempts missed; this is the closest result", note)
        self.assertIn("subject term(s) missing from what the provider recorded it made: table", note)
        self.assertIn("python3 agents/media-generator/mediagen.py generate --brief 'my brief.json' --out", note)
        self.assertIn("mediagen.py revise --from", note)
        man = mediagen.manifest(results, QUALITY, "T")
        self.assertEqual([f["matches_brief"] for f in man["files"]], [False, False])

    def test_provider_errors(self):
        res = one(job(), [Broken(), image.StubImage()], table(**{"test-broken": 1.0, "stub-image": 0.1}), self.dir)
        self.assertIsNotNone(res.attempts[0].error)
        self.assertEqual(res.chosen.provider.name, "stub-image")
        res = one(job(), [Broken()], table(**{"test-broken": 1.0}), self.dir)
        self.assertIsNone(res.chosen)
        self.assertIn("no attempt produced any output", res.failure)

    def test_never_more_than_two_attempts(self):
        for providers in ([AlwaysDropsTerm()], [BlankImage(), AlwaysDropsTerm(), image.StubImage()]):
            self.assertLessEqual(len(one(job(), providers, table(), self.dir).attempts), 2)


# ---------------------------------------------------------------- the job description's sample scenarios

class SampleScenarioTests(TempDirCase):
    """The four sample scenarios of the job description, run through the CLI."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        d = cls._tmp.name
        brief = os.path.join(d, "brief.json")
        script = ("Welcome to Harbor Coffee. Our beans are roasted every morning, our cups are made by hand, and every "
                  "visit comes with a smile. Stop by this week and try the new autumn blend, served hot or iced, "
                  "with a free pastry for every regular who brings a friend along.")
        with open(brief, "w", encoding="utf-8") as fh:
            json.dump({"requests": [
                {"type": "image", "subject": "ceramic mug on a wooden table", "count": 3, "aspect": "1:1"},
                {"type": "video", "subject": "coffee being poured into a cup", "aspect": "9:16", "length_seconds": 8},
                {"type": "voice", "subject": "coffee shop promo", "script": script, "voice": "stock-warm-female",
                 "length_seconds": 30},
                {"type": "image", "subject": "a well-known celebrity holding the product"},
            ]}, fh)
        cls.out = os.path.join(d, "out")
        o, e = io.StringIO(), io.StringIO()
        cls.code = mediagen.main(["generate", "--brief", brief, "--out", cls.out], env={}, stdout=o, stderr=e)
        cls.note, cls.err = o.getvalue(), e.getvalue()
        cls.man = json.loads(Path(cls.out, "delivery.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_files_per_request(self):
        self.assertEqual(self.code, 0, self.err)
        by_req = {}
        for f in self.man["files"]:
            by_req.setdefault(f["request"], []).append(f)
        self.assertEqual({k: len(v) for k, v in by_req.items()}, {1: 3, 2: 1, 3: 1})
        for f in self.man["files"]:
            self.assertTrue(f["matches_brief"], f)
            self.assertTrue(f["provider"] and f["model"])  # acceptance 5: provider and model per file
            self.assertEqual(mediagen.sha256_file(os.path.join(self.out, f["file"])), f["sha256"])

    def test_square_images_vertical_video_and_voice_length(self):
        for f in self.man["files"]:
            p = os.path.join(self.out, f["file"])
            if p.endswith(".png"):
                w, h, _, _ = placeholder.read_png(p)
                self.assertEqual(w, h)
            elif p.endswith(".gif"):
                w, h, _, seconds, _ = placeholder.read_gif(p)
                self.assertLess(w, h)
                self.assertTrue(7 <= seconds <= 9, seconds)
            else:
                seconds, _, comment = placeholder.read_wav(p)
                self.assertTrue(29 <= seconds <= 31, seconds)
                self.assertIn("Welcome to Harbor Coffee.", comment)

    def test_celebrity_is_declined_with_the_reason(self):
        self.assertEqual(self.man["requests"][3]["declined"][0]["rule"], "real person without consent")
        self.assertIn("### Declined", self.note)
        self.assertNotIn("r4-", " ".join(os.listdir(self.out)))

    def test_report_names_provider_and_model_for_each_file(self):
        for f in self.man["files"]:
            self.assertIn("| `%s` | %s | %s | %d | `%s` |" % (f["file"], f["provider"], f["model"], f["attempt"], f["sha256"]), self.note)
        self.assertIn("**Placeholder media.**", self.note)
        self.assertIn("checked to within 1 s", self.note)


# ---------------------------------------------------------------- revise

class ReviseTests(TempDirCase):
    def setUp(self):
        super().setUp()
        brief = self.write_brief({"requests": [{"type": "image", "subject": "ceramic mug on a wooden table", "count": 3},
                                               {"type": "voice", "subject": "shop welcome", "script": "Welcome in.", "length_seconds": 2}]})
        code, _, err = self.main(["generate", "--brief", brief, "--out", self.path("v1")])
        self.assertEqual(code, 0, err)
        self.man = json.loads(Path(self.path("v1", "delivery.json")).read_text())

    def test_changes_only_the_named_files(self):
        target = "r1-ceramic-mug-on-a-wooden-table-2.png"
        code, _, err = self.main(["revise", "--from", self.path("v1"), "--files", target, "--out", self.path("v2"),
                                  "--note", "brighter light"])
        self.assertEqual(code, 0, err)
        for f in self.man["files"]:
            old = os.path.join(self.path("v1"), f["file"])
            new = os.path.join(self.path("v2"), f["file"])
            if f["file"] == target:
                self.assertNotEqual(mediagen.sha256_file(old), mediagen.sha256_file(new))
            else:
                self.assertEqual(Path(old).read_bytes(), Path(new).read_bytes())
        note = Path(self.path("v2", "delivery-note.md")).read_text()
        self.assertIn("| `%s` | changed (was `" % target, note)
        self.assertEqual(note.count("kept as delivered"), len(self.man["files"]) - 1)
        self.assertIn("Change request: brighter light", note)
        w, h, texts, _ = placeholder.read_png(self.path("v2", target))
        self.assertIn("Revision: brighter light", texts["Description"])
        man2 = json.loads(Path(self.path("v2", "delivery.json")).read_text())
        changed = [f for f in man2["files"] if f.get("revised_from")]
        self.assertEqual([f["file"] for f in changed], [target])

    def test_refusals(self):
        code, _, err = self.main(["revise", "--from", self.path("v1"), "--files", "nope.png", "--out", self.path("v2")])
        self.assertEqual(code, 2)
        self.assertIn("not in the earlier delivery: nope.png", err)
        code, _, err = self.main(["revise", "--from", self.path("v1"), "--files", self.man["files"][0]["file"], "--out", self.path("v1")])
        self.assertEqual(code, 2)
        self.assertIn("--out must differ from --from", err)
        with open(os.path.join(self.path("v1"), self.man["files"][1]["file"]), "ab") as fh:
            fh.write(b"x")
        code, _, err = self.main(["revise", "--from", self.path("v1"), "--files", self.man["files"][0]["file"], "--out", self.path("v3")])
        self.assertEqual(code, 2)
        self.assertIn("no longer matches its recorded SHA-256", err)
        self.assertFalse(os.path.exists(self.path("v3")))


# ---------------------------------------------------------------- CLI, recorded table, offline rule

class CliTests(TempDirCase):
    def test_single_request_brief_and_bad_brief(self):
        brief = self.write_brief({"type": "video", "subject": "waves on a beach", "length_seconds": 3})
        code, note, err = self.main(["generate", "--brief", brief, "--out", self.path("out")])
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(os.listdir(self.path("out"))), ["delivery-note.md", "delivery.json", "waves-on-a-beach-1.gif"])
        self.assertEqual(Path(self.path("out", "delivery-note.md")).read_text(encoding="utf-8"), note)
        for heading in ("## Request 1:", "### Brief", "### Routing", "### Attempts", "### Delivered", "## What the check covers"):
            self.assertIn(heading, note)
        self.assertIn("live-video: excluded: not configured", note)
        bad = self.path("bad.json")
        Path(bad).write_text("{not json")
        code, _, err = self.main(["generate", "--brief", bad, "--out", self.path("o2")])
        self.assertEqual(code, 2)
        self.assertIn("is not valid JSON", err)
        self.assertFalse(os.path.exists(self.path("o2")))


class RecordedTableTests(unittest.TestCase):
    def test_committed_table_matches_a_fresh_calibration_apart_from_the_time(self):
        fresh = mediagen.calibrate(env={}, now="T")
        committed = json.loads(Path(mediagen.QUALITY_PATH).read_text())

        def strip(t):
            out = json.loads(json.dumps(t))
            out.pop("source", None)
            for kinds in out["providers"].values():
                for rec in kinds.values():
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
            placeholder.wav_voice(os.path.join(d, "s.wav"), 1.0, "hello", script="hello there")
            seconds, peak, comment = placeholder.read_wav(os.path.join(d, "s.wav"))
            self.assertEqual(seconds, 1.0)
            self.assertEqual(mediagen.recorded_script(comment), "hello there")
            self.assertIn("placeholder tone, not speech", comment)


if __name__ == "__main__":
    unittest.main()
