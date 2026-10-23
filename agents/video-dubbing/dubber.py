#!/usr/bin/env python3
"""Video dubbing agent: one video in, one dubbed video plus one SRT per language.

Takes a video, the target languages, a voice option, and the names and do
not translate terms to protect. It transcribes the speech into timed
segments, translates each segment (protected terms are checked verbatim in
every translation), keeps the music and sound under the new voice with a
background separator, voices each line, fits it to the original timing
(tighten, then stretch within a limit, then breathe into a genuine pause),
and writes for every language a finished video and an SRT carrying the
full translation. A delivery note lists every compressed line.

Two commands, run from the repository root:

  plan  transcribe, translate and fit every line; print the plan and the
        flagged lines. Writes no video.
  run   the same, then write per language: <stem>.<lang>.mp4 and
        <stem>.<lang>.srt, plus manifest.json and report.md (the delivery
        note, the body a NEAR assignment submit carries as
        deliverableMarkdown; see near-agent/README.md).

    python3 agents/video-dubbing/dubber.py run --video talk.mp4 \\
        --segments segments.json --languages es,fr --translator glossary \\
        --glossary glossary.json --voice flite --dnt "Hojo,NEAR" --out out/

Voice options: stub (offline tests only), flite (local English stock
voices), own-voice (the speaker's voice: refused without a recorded consent
and rights confirmation in the job inputs, --consent FILE; this build has
no cloning engine, so it refuses with consent too).

The program reads the source and writes into --out only. It sends nothing
and needs no account or key on its core path. It fails closed: a provider
failure, a lost protected term, a line that cannot be fitted, or a consent
refusal stops with exit 2 and writes no deliverable.

Standard library only, plus ffmpeg and ffprobe on PATH.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import providers  # noqa: E402
import sync  # noqa: E402


class DubError(RuntimeError):
    """The job cannot be done as asked."""


def srt_time(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type", "-of", "json", path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode != 0:
        raise DubError("ffprobe could not read %s: %s"
                       % (path, out.stderr.decode("utf-8", "replace").strip()))
    info = json.loads(out.stdout.decode("utf-8"))
    kinds = [s.get("codec_type") for s in info.get("streams", [])]
    if "video" not in kinds or "audio" not in kinds:
        raise DubError("%s needs both a video and an audio stream" % path)
    return float(info["format"]["duration"])


def ffmpeg(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise DubError("ffmpeg failed: %s" % proc.stderr.decode("utf-8", "replace").strip()[-800:])


def load_brief(args):
    brief = {"languages": [], "voice": "stub", "names": [], "do_not_translate": [],
             "consent": None}
    if args.brief:
        try:
            with open(args.brief, encoding="utf-8") as fh:
                given = json.load(fh)
        except (OSError, ValueError) as err:
            raise DubError("cannot read brief %s: %s" % (args.brief, err))
        unknown = set(given) - set(brief)
        if unknown:
            raise DubError("brief has unknown keys: %s" % ", ".join(sorted(unknown)))
        brief.update(given)
    if args.languages:
        brief["languages"] = providers.split_terms(args.languages)
    if args.voice:
        brief["voice"] = args.voice
    brief["names"] = list(brief["names"]) + providers.split_terms(args.names)
    brief["do_not_translate"] = list(brief["do_not_translate"]) + providers.split_terms(args.dnt)
    if args.consent:
        try:
            with open(args.consent, encoding="utf-8") as fh:
                brief["consent"] = json.load(fh)
        except (OSError, ValueError) as err:
            raise DubError("cannot read consent record %s: %s" % (args.consent, err))
    if not brief["languages"]:
        raise DubError("name at least one target language (--languages es,fr)")
    return brief


class Measurer:
    """Synthesizes a wording once and remembers its file and length."""

    def __init__(self, voice, language, work):
        self.voice, self.language, self.work = voice, language, work
        self.cache = {}

    def path_for(self, text):
        if text not in self.cache:
            path = os.path.join(self.work, "%s-line-%03d.wav" % (self.language, len(self.cache)))
            self.voice.synthesize(text, self.language, path)
            self.cache[text] = (path, providers.audio_seconds(path))
        return self.cache[text][0]

    def __call__(self, text):
        self.path_for(text)
        return self.cache[text][1]


def plan_language(segments, language, translator, voice, terms, work, max_stretch):
    measure = Measurer(voice, language, work)
    fits, subtitles = [], []
    for n, seg in enumerate(segments):
        full, shorter = translator.translate(seg, language, terms)
        following = segments[n + 1] if n + 1 < len(segments) else None
        fit = sync.fit_line(seg, following, [full] + shorter, measure, max_stretch)
        fits.append((fit, measure.path_for(fit.wording)))
        subtitles.append((seg, full))
    return fits, subtitles


def render_language(video, duration, background, fits, subtitles, out_video, out_srt, work):
    inputs = ["-i", video, "-i", background]
    chains, labels = [], ["[1:a]"]
    for k, (fit, path) in enumerate(fits):
        inputs += ["-i", path]
        delay = int(round(fit.segment.start * 1000))
        tempo = "atempo=%.4f," % fit.stretch if fit.stretch > 1.0 else ""
        chains.append("[%d:a]%sadelay=%d|%d[l%d]" % (k + 2, tempo, delay, delay, k))
        labels.append("[l%d]" % k)
    mix = "%samix=inputs=%d:normalize=0:duration=longest,apad,atrim=0:%.3f[a]" % (
        "".join(labels), len(labels), duration)
    ffmpeg(["ffmpeg", "-nostdin", "-loglevel", "error", "-y"] + inputs +
           ["-filter_complex", ";".join(chains + [mix]), "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", "%.3f" % duration,
            "-movflags", "+faststart", out_video])
    with open(out_srt, "w", encoding="utf-8") as fh:
        for n, (seg, text) in enumerate(subtitles, 1):
            fh.write("%d\n%s --> %s\n%s\n\n" % (n, srt_time(seg.start), srt_time(seg.end), text))


def build_parser():
    parser = argparse.ArgumentParser(description="Dub a video into other languages.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        p = sub.add_parser(name)
        p.add_argument("--video", required=True)
        p.add_argument("--segments", help="timed segments JSON (segments-file transcriber)")
        p.add_argument("--brief", help="brief JSON: languages, voice, names, do_not_translate, consent")
        p.add_argument("--languages", help="comma separated language codes, e.g. es,fr")
        p.add_argument("--voice", choices=("stub", "flite", "own-voice"))
        p.add_argument("--flite-voice", default="slt")
        p.add_argument("--consent", help="consent record JSON, required for own-voice")
        p.add_argument("--translator", default="glossary", choices=("glossary", "stub"))
        p.add_argument("--glossary", help="per segment translations JSON")
        p.add_argument("--names", help="comma separated names to keep as written")
        p.add_argument("--dnt", help="comma separated do not translate terms")
        p.add_argument("--separator", default="duck", choices=("duck", "demucs"))
        p.add_argument("--max-stretch", type=float, default=sync.MAX_STRETCH)
        p.add_argument("--out", default="dub-out")
    return parser


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out)
    work = tempfile.mkdtemp(prefix="dub-")
    try:
        if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
            raise DubError("ffmpeg and ffprobe are needed on PATH")
        if not 1.0 <= args.max_stretch <= 1.5:
            raise DubError("--max-stretch must be between 1.0 and 1.5")
        brief = load_brief(args)
        voice = providers.make_voice(brief["voice"], brief["consent"], args.flite_voice)
        translator = providers.make_translator(args.translator, args.glossary)
        separator = providers.make_separator(args.separator)
        duration = probe(args.video)
        segments, engine = providers.SegmentsFileTranscriber(args.segments).transcribe(args.video)
        terms = brief["names"] + brief["do_not_translate"]
        plans = {}
        for language in brief["languages"]:
            plans[language] = plan_language(segments, language, translator, voice, terms,
                                            work, args.max_stretch)
    except (DubError, providers.ProviderError, sync.SyncError) as err:
        shutil.rmtree(work, ignore_errors=True)
        stderr.write("error: %s\n" % err)
        return 2

    for language, (fits, _) in plans.items():
        for fit, _ in fits:
            stdout.write("%s seg %d  %6.2f-%6.2fs  %s%s\n" % (
                language, fit.segment.index, fit.segment.start, fit.segment.end, fit.note(),
                "  [FLAGGED]" if fit.flagged else ""))
    if args.command == "plan":
        shutil.rmtree(work, ignore_errors=True)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(args.video).stem
    try:
        background = separator.background(args.video, os.path.join(work, "background.wav"))
        files = {}
        for language, (fits, subtitles) in plans.items():
            video_out = out_dir / ("%s.%s.mp4" % (stem, language))
            srt_out = out_dir / ("%s.%s.srt" % (stem, language))
            render_language(args.video, duration, background, fits, subtitles,
                            str(video_out), str(srt_out), work)
            files[language] = {"video": video_out.name, "srt": srt_out.name}
    except (DubError, providers.ProviderError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)

    manifest = {
        "source": os.path.basename(args.video), "duration": round(duration, 3),
        "transcriber": engine, "translator": translator.name, "voice": brief["voice"],
        "separator": separator.name, "max_stretch": args.max_stretch,
        "protected_terms": terms, "files": files,
        "lines": {lang: [{"segment": f.segment.index, "start": f.segment.start,
                          "end": f.segment.end, "spoken": f.wording, "note": f.note(),
                          "flagged": f.flagged} for f, _ in fits]
                  for lang, (fits, _) in plans.items()},
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)
                                           + "\n", encoding="utf-8")
    write_report(out_dir / "report.md", manifest)
    stdout.write("wrote %d languages, manifest.json and report.md to %s\n" % (len(files), out_dir))
    return 0


def write_report(path, manifest):
    lines = ["# Dub of %s" % manifest["source"], ""]
    if manifest["translator"] == "stub":
        lines += ["**STUB TRANSLATION, offline test only. Not a deliverable.**", ""]
    sep_note = ("local ducking of the original mix (speech band cut and lowered), not true "
                "source separation" if manifest["separator"] == "duck"
                else "demucs source separation (no_vocals stem)")
    lines += ["- Voice: %s" % manifest["voice"], "- Background: %s" % sep_note,
              "- Protected terms kept as written: %s" % (", ".join(manifest["protected_terms"])
                                                         or "none given"),
              "- Subtitles carry the full translation of every line.", ""]
    for lang, entries in manifest["lines"].items():
        f = manifest["files"][lang]
        flagged = [e for e in entries if e["flagged"]]
        lines += ["## %s" % lang, "", "- Files: `%s`, `%s`" % (f["video"], f["srt"]),
                  "- Compressed lines: %s" % (len(flagged) or "none"), ""]
        for e in flagged:
            lines.append("  - segment %d (%s to %s): %s" % (
                e["segment"], srt_time(e["start"]), srt_time(e["end"]), e["note"]))
        tightened = [e for e in entries if "tightened" in e["note"]]
        if tightened:
            lines.append("- Tightened wording spoken on segments %s; the subtitles keep the "
                         "full wording." % ", ".join(str(e["segment"]) for e in tightened))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
