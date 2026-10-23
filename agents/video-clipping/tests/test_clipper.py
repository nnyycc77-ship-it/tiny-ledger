"""Offline tests for the video clipping agent.

FIXTURE LABEL: every input here is generated media made by this test. The
video is an ffmpeg test pattern (a grey frame with a moving testsrc2 panel
on the right, standing in for the speaker) over a sine tone whose loudness
changes by segment; the "transcript" is a synthetic word timing list built
below, labelled as such in its engine field. It is not the output of any
speech recognition and contains no third party content. Nothing is
downloaded and no network is used.

Needs ffmpeg and ffprobe on PATH; the suite is skipped, not failed, when
they are missing.
"""

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT = HERE.parent
sys.path.insert(0, str(AGENT))

import clipper  # noqa: E402
import media  # noqa: E402
import scoring  # noqa: E402
import transcribe  # noqa: E402

HAVE_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
WORD_STEP = 0.4

# Synthetic script: (start second, text). Example data built for this test.
SCRIPT = [
    (1.0, "Welcome back everyone, today we look at home batteries and how to keep "
          "them healthy for a long time at home."),
    (14.0, "What is the biggest mistake people make with home batteries? The biggest "
           "mistake is charging to full every night, because heat and a full charge "
           "wear the cells."),
    (29.0, "And that is also the reason the warranty matters so much, it covers the "
           "cells for years if you register."),
    (44.0, "Here's the secret most people miss about storage."),
    (50.6, "Store it half charged, so the cells last twice as long."),
]
BURST = (48.6, 50.2)  # loud, no words over it: the "applause" stand-in


def synthetic_words():
    words = []
    for start, text in SCRIPT:
        t = start
        for token in text.split():
            words.append({"w": token, "start": round(t, 3), "end": round(t + WORD_STEP - 0.05, 3)})
            t += WORD_STEP
    return words


def make_fixture(folder):
    video = folder / "fixture.mp4"
    loud = "between(t,14,27)"
    burst = "between(t,%s,%s)" % BURST
    audio = ("aevalsrc=exprs='(0.08+0.5*%s+0.8*%s)*sin(2*PI*220*t)':s=8000:d=60"
             % (loud, burst))
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "color=c=0x404040:s=320x180:r=15:d=60",
         "-f", "lavfi", "-i", "testsrc2=s=80x120:r=15:d=60",
         "-f", "lavfi", "-i", audio,
         "-filter_complex", "[0][1]overlay=x=220:y=30[v]", "-map", "[v]", "-map", "2",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", str(video)],
        check=True)
    transcript = folder / "fixture-words.json"
    transcript.write_text(json.dumps({
        "engine": "synthetic-test-transcript (generated in this test, not speech recognition output)",
        "words": synthetic_words()}), encoding="utf-8")
    return video, transcript


class PureLogicTests(unittest.TestCase):
    def test_crop_box_keeps_focus_and_aspect(self):
        w, h, x, y = media.crop_box(320, 180, 1080, 1920, focus_x=0.85)
        self.assertEqual((h, y), (180, 0))
        self.assertAlmostEqual(w / h, 1080 / 1920, delta=0.02)
        self.assertEqual(x, 320 - w)  # clamped to the right edge
        self.assertEqual(media.crop_box(320, 180, 1920, 1080, 0.5), (320, 180, 0, 0))

    def test_sentences_split_on_punctuation_and_pauses(self):
        words = [transcribe.Word("Hi.", 0, 0.3), transcribe.Word("Next", 0.4, 0.7),
                 transcribe.Word("one", 0.8, 1.0), transcribe.Word("later", 2.0, 2.3)]
        self.assertEqual([len(g) for g in scoring.sentences(words)], [1, 2, 1])

    def test_malformed_transcript_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"words": [{"w": "x"}]}', encoding="utf-8")
            with self.assertRaises(transcribe.EngineError):
                transcribe.TranscriptFileEngine(str(bad)).transcribe("unused.mp4")

    def test_vosk_engine_refuses_without_model(self):
        with self.assertRaises(transcribe.EngineError):
            transcribe.VoskEngine(model_path="/nonexistent/model")


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are needed for the media tests")
class FixtureRunTests(unittest.TestCase):
    MIN, MAX = 8.0, 15.0

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.video, cls.transcript = make_fixture(cls.folder)
        cls.out = cls.folder / "out"
        cls.stdout = io.StringIO()
        cls.code = clipper.main(
            ["run", "--video", str(cls.video), "--transcript", str(cls.transcript),
             "--clips", "3", "--platforms", "tiktok,landscape", "--captions",
             "--min-seconds", str(cls.MIN), "--max-seconds", str(cls.MAX),
             "--out", str(cls.out), "--preset", "ultrafast"],
            stdout=cls.stdout, stderr=io.StringIO())
        cls.manifest = json.loads((cls.out / "manifest.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_run_succeeds_with_requested_clip_count(self):
        self.assertEqual(self.code, 0)
        self.assertEqual(len(self.manifest["moments"]), 3)
        self.assertEqual(len(self.manifest["files"]), 6)

    def test_every_file_has_the_platform_size_and_a_fitting_duration(self):
        moments = {m["clip"]: m for m in self.manifest["moments"]}
        for entry in self.manifest["files"]:
            info = media.probe(str(self.out / entry["file"]))
            self.assertEqual([info["width"], info["height"]],
                             list(media.PLATFORMS[entry["platform"]]), entry["file"])
            self.assertAlmostEqual(info["duration"], moments[entry["clip"]]["duration"],
                                   delta=0.5, msg=entry["file"])
            self.assertGreaterEqual(info["duration"], self.MIN - 0.5)
            self.assertLessEqual(info["duration"], self.MAX + 0.5)

    def test_every_moment_has_a_one_line_reason(self):
        for m in self.manifest["moments"]:
            self.assertTrue(m["reason"].strip())
            self.assertNotIn("\n", m["reason"])

    def test_scoring_picks_the_signals_and_skips_the_context_cut(self):
        reasons = " | ".join(m["reason"] for m in self.manifest["moments"])
        self.assertIn("question and answer", reasons)
        self.assertIn("speech energy peak", reasons)
        self.assertIn("claim with its payoff", reasons)
        self.assertIn("possible laughter or applause", reasons)
        for m in self.manifest["moments"]:
            self.assertFalse(m["text"].startswith("And "), m["text"])

    def test_vertical_reframe_follows_the_speaker(self):
        tall = [f for f in self.manifest["files"] if f["platform"] == "tiktok"]
        for f in tall:
            crop_w, _, x, _ = f["crop"]
            self.assertGreater(f["focus_x"], 0.6)
            self.assertGreater(x, (320 - crop_w) // 2)

    def test_captions_written_and_burned_when_asked(self):
        for n in range(1, 4):
            srt = (self.out / ("clip_%02d.srt" % n)).read_text(encoding="utf-8")
            self.assertIn(" --> ", srt)
        self.assertTrue(all(f["srt"] for f in self.manifest["files"]))

    def test_report_lists_every_file_and_reason(self):
        report = (self.out / "report.md").read_text(encoding="utf-8")
        for f in self.manifest["files"]:
            self.assertIn(f["file"], report)
        self.assertEqual(report.count("- Why this moment: "), 3)

    def test_plan_encodes_nothing(self):
        out = self.folder / "plan-out"
        stdout = io.StringIO()
        code = clipper.main(["plan", "--video", str(self.video), "--transcript",
                             str(self.transcript), "--clips", "2", "--platforms", "square",
                             "--min-seconds", "8", "--max-seconds", "15", "--out", str(out)],
                            stdout=stdout, stderr=io.StringIO())
        self.assertEqual(code, 0)
        self.assertIn("ffmpeg", stdout.getvalue())
        self.assertFalse(out.exists())

    def test_unmeetable_brief_fails_closed(self):
        out = self.folder / "too-many"
        stderr = io.StringIO()
        code = clipper.main(["run", "--video", str(self.video), "--transcript",
                             str(self.transcript), "--clips", "10", "--min-seconds", "8",
                             "--max-seconds", "15", "--out", str(out)],
                            stdout=io.StringIO(), stderr=stderr)
        self.assertEqual(code, 2)
        self.assertIn("asked for 10 clips", stderr.getvalue())
        self.assertFalse(out.exists())

    def test_unknown_platform_fails_closed(self):
        code = clipper.main(["plan", "--video", str(self.video), "--transcript",
                             str(self.transcript), "--platforms", "fax"],
                            stdout=io.StringIO(), stderr=io.StringIO())
        self.assertEqual(code, 2)



# SYNTHETIC retention curve for the fixture video (issue #130): flat at 0.2
# except a plateau at 1.0 over 32 to 40 s, inside the sentence that starts at
# 29 s with "And", which content analysis alone penalises. Example data built
# for this test, not any platform's export.
RETENTION_PEAK = {"kind": "most_replayed", "source": "SYNTHETIC test curve built in test_clipper.py",
                  "points": [{"t": 0, "value": 0.2}, {"t": 28, "value": 0.2}, {"t": 32, "value": 1.0},
                             {"t": 40, "value": 1.0}, {"t": 43, "value": 0.2}, {"t": 60, "value": 0.2}]}


class RetentionLogicTests(unittest.TestCase):
    def curve(self, **change):
        return scoring.Retention.from_json(dict(RETENTION_PEAK, **change))

    def test_the_stated_shape_is_enforced(self):
        good = self.curve()
        self.assertEqual((good.kind, len(good.points)), ("most_replayed", 6))
        bad = [[], {"kind": "views", "source": "x", "points": RETENTION_PEAK["points"]},
               dict(RETENTION_PEAK, source=" "), dict(RETENTION_PEAK, points=[{"t": 0, "value": 1}]),
               dict(RETENTION_PEAK, points=[{"t": 0, "value": 1}, {"t": 0, "value": 2}]),
               dict(RETENTION_PEAK, points=[{"t": 0, "value": 1}, {"t": 5, "value": -1}]),
               dict(RETENTION_PEAK, points=[{"t": 0, "value": 1}, {"t": 5, "value": True}]),
               dict(RETENTION_PEAK, points=[{"t": 0, "value": 1}, {"t": 5, "value": float("nan")}]),
               dict(RETENTION_PEAK, points=[{"t": 0, "value": 0}, {"t": 5, "value": 0}])]
        for data in bad:
            with self.assertRaises(scoring.RetentionError, msg=data):
                scoring.Retention.from_json(data)

    def test_curve_is_linear_between_points_and_flat_outside(self):
        r = self.curve()
        self.assertAlmostEqual(r.at(30), 0.6)
        self.assertAlmostEqual(r.at(-5), 0.2)
        self.assertAlmostEqual(r.at(99), 0.2)
        self.assertAlmostEqual(r.mean(33, 39), 1.0)
        self.assertAlmostEqual(r.median(60), 0.2)

    def test_one_peak_per_stretch_above_the_median(self):
        r = scoring.Retention.from_json(dict(RETENTION_PEAK, points=[
            {"t": 0, "value": 0.2}, {"t": 10, "value": 0.6}, {"t": 12, "value": 0.2},
            {"t": 30, "value": 0.2}, {"t": 34, "value": 0.9}, {"t": 40, "value": 0.9}, {"t": 42, "value": 0.2},
            {"t": 60, "value": 0.2}]))
        peaks, median = r.peaks(60, 5)
        self.assertAlmostEqual(median, 0.2)
        self.assertEqual(len(peaks), 2)
        self.assertGreater(peaks[0][1], peaks[1][1])
        self.assertTrue(34 <= peaks[0][0] <= 40)
        self.assertTrue(9 <= peaks[1][0] <= 11)
        self.assertEqual(r.peaks(60, 1)[0][0], peaks[0])

    def test_lift_outranks_content_and_is_named_in_the_reason(self):
        words = [transcribe.Word(w, i * 0.5, i * 0.5 + 0.4) for i, w in
                 enumerate("What is it? It is this. and then more words here. Later on we talk.".split())]
        energy = [1.0] * 40
        flat = scoring.score_candidates(words, energy, 0.25, 1.0, 3.0)
        r = scoring.Retention.from_json({"kind": "audience_retention", "source": "SYNTHETIC", "points": [
            {"t": 0, "value": 0.1}, {"t": 4.9, "value": 0.1}, {"t": 5.0, "value": 1.0}, {"t": 7.4, "value": 1.0},
            {"t": 7.5, "value": 0.1}, {"t": 10, "value": 0.1}]})
        ranked = scoring.score_candidates(words, energy, 0.25, 1.0, 3.0, r, 10.0)
        top_flat = max(flat, key=lambda c: c.score)
        top = max(ranked, key=lambda c: c.score)
        self.assertNotEqual((top_flat.start, top_flat.end), (top.start, top.end))
        self.assertGreaterEqual(top.start, 4.9)
        self.assertTrue(top.reasons[0].startswith("high retention: "))
        self.assertIn("audience retention data", top.reasons[0])
        self.assertGreater(top.retention_lift, 1.0)
        self.assertTrue(all(c.retention_lift is None for c in flat))


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are needed for the media tests")
class RetentionRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.video, cls.transcript = make_fixture(cls.folder)
        cls.retention = cls.folder / "retention.json"
        cls.retention.write_text(json.dumps(RETENTION_PEAK), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_clipper(self, name, min_seconds, retention=True, extra=()):
        out = self.folder / name
        argv = ["run", "--video", str(self.video), "--transcript", str(self.transcript), "--clips", "2",
                "--platforms", "square", "--min-seconds", str(min_seconds), "--max-seconds", "15",
                "--out", str(out), "--preset", "ultrafast"] + list(extra)
        if retention:
            argv += ["--retention", str(self.retention)]
        stderr = io.StringIO()
        code = clipper.main(argv, stdout=io.StringIO(), stderr=stderr)
        return code, out, stderr.getvalue()

    def test_clip_comes_from_the_retention_peak_and_says_so(self):
        code, out, err = self.run_clipper("peak", 6)
        self.assertEqual(code, 0, err)
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        report = (out / "report.md").read_text(encoding="utf-8")
        peak = [m for m in manifest["moments"] if m["start"] <= 32.12 <= m["end"]]
        self.assertEqual(len(peak), 1, manifest["moments"])
        self.assertTrue(peak[0]["text"].startswith("And that is also the reason"))
        self.assertTrue(peak[0]["reason"].startswith("high retention: "))
        self.assertGreater(peak[0]["retention_lift"], 1.0)
        self.assertIn("ranked first by the most replayed data supplied (6 points; source as given: SYNTHETIC "
                      "test curve built in test_clipper.py)", report)
        self.assertIn(": covered by clip %d" % peak[0]["clip"], report)
        self.assertNotIn("no retention data", report)
        self.assertEqual(manifest["retention"]["kind"], "most_replayed")

    def test_a_peak_no_clip_can_hold_is_explained(self):
        code, out, err = self.run_clipper("short", 8)
        self.assertEqual(code, 0, err)
        report = (out / "report.md").read_text(encoding="utf-8")
        self.assertIn("## Retention data", report)
        self.assertIn("not covered: no run of whole sentences 8 to 15 seconds long contains it", report)

    def test_without_the_file_the_report_says_content_analysis(self):
        code, out, err = self.run_clipper("none", 8, retention=False)
        self.assertEqual(code, 0, err)
        report = (out / "report.md").read_text(encoding="utf-8")
        self.assertIn("Moments are chosen from the transcript and the audio, with no retention data.", report)
        self.assertNotIn("## Retention data", report)
        self.assertIsNone(json.loads((out / "manifest.json").read_text(encoding="utf-8"))["retention"])

    def test_bad_or_mismatched_retention_file_fails_closed(self):
        for name, body in (("broken", "{not json"),
                           ("long", json.dumps(dict(RETENTION_PEAK, points=RETENTION_PEAK["points"] + [
                               {"t": 600, "value": 0.2}])))):
            self.retention.write_text(body, encoding="utf-8")
            try:
                code, out, err = self.run_clipper(name, 8)
            finally:
                self.retention.write_text(json.dumps(RETENTION_PEAK), encoding="utf-8")
            self.assertEqual(code, 2, name)
            self.assertIn("retention file", err)
            self.assertFalse(out.exists(), name)


if __name__ == "__main__":
    unittest.main()
