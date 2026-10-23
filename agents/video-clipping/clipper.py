#!/usr/bin/env python3
"""Video clipping agent: one long video in, short platform clips out.

Takes a source video and a brief (how many clips, which platform shapes,
captions or not, the clip length range), transcribes the speech with word
timing, scores candidate moments with no retention data, and cuts the
chosen moments with ffmpeg: resized per platform, reframed to keep the
speaker in frame, captions burned in only when the brief asks. Every chosen
moment carries a one line reason.

Two commands, both run from the repository root:

  plan  transcribe and score, then print the chosen moments, their reasons,
        and the exact ffmpeg command for every clip. Encodes nothing.
  run   the same, then cut every clip and write, in the output folder, the
        clips, manifest.json (moments, reasons, files) and report.md (the
        deliverable Markdown, the body a NEAR assignment submit carries as
        deliverableMarkdown; see near-agent/README.md).

    python3 agents/video-clipping/clipper.py plan --video in.mp4 \\
        --transcript words.json --clips 3 --platforms tiktok,landscape
    python3 agents/video-clipping/clipper.py run --video in.mp4 \\
        --engine vosk --clips 3 --platforms tiktok --captions --out out/

The brief can also come from a JSON file (--brief FILE) with the keys
clips, platforms, captions, min_seconds, max_seconds; flags override it.

This program only reads the source video and writes into --out. It sends
nothing anywhere and needs no account or key for its core path; the local
vosk engine needs its own model directory (see transcribe.py). It fails
closed: a probe, transcription or encode failure, or a brief it cannot
meet (fewer good moments than clips asked for), stops with a message and
exit 2, and no partial deliverable is written as if it were complete.

Standard library only, plus ffmpeg and ffprobe on PATH.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import media  # noqa: E402
import scoring  # noqa: E402
import transcribe  # noqa: E402

DEFAULTS = {"clips": 3, "platforms": ["tiktok"], "captions": False,
            "min_seconds": 15.0, "max_seconds": 60.0}


class ClipError(RuntimeError):
    """The brief cannot be met from this source."""


def load_brief(args):
    brief = dict(DEFAULTS)
    if args.brief:
        try:
            with open(args.brief, encoding="utf-8") as fh:
                given = json.load(fh)
        except (OSError, ValueError) as err:
            raise ClipError("cannot read brief %s: %s" % (args.brief, err))
        unknown = set(given) - set(DEFAULTS)
        if unknown:
            raise ClipError("brief has unknown keys: %s" % ", ".join(sorted(unknown)))
        brief.update(given)
    for key in ("clips", "min_seconds", "max_seconds"):
        if getattr(args, key) is not None:
            brief[key] = getattr(args, key)
    if args.platforms:
        brief["platforms"] = [p.strip() for p in args.platforms.split(",") if p.strip()]
    if args.captions:
        brief["captions"] = True
    if isinstance(brief["platforms"], str):
        brief["platforms"] = [brief["platforms"]]
    bad = [p for p in brief["platforms"] if p not in media.PLATFORMS]
    if bad or not brief["platforms"]:
        raise ClipError("unknown platform %s; known: %s"
                        % (", ".join(bad) or "(none)", ", ".join(sorted(media.PLATFORMS))))
    if int(brief["clips"]) < 1:
        raise ClipError("clips must be at least 1")
    if not 0 < float(brief["min_seconds"]) <= float(brief["max_seconds"]):
        raise ClipError("need 0 < min_seconds <= max_seconds")
    brief["clips"] = int(brief["clips"])
    brief["min_seconds"] = float(brief["min_seconds"])
    brief["max_seconds"] = float(brief["max_seconds"])
    brief["captions"] = bool(brief["captions"])
    return brief


def plan(video, engine, brief, out_dir, preset):
    media.require_tools()
    info = media.probe(video)
    if not info["has_audio"]:
        raise ClipError("%s has no audio stream to transcribe" % video)
    transcript = engine.transcribe(video)
    if not transcript.words:
        raise ClipError("the transcript has no words; nothing to score")
    energy = media.audio_energy(video)
    candidates = scoring.score_candidates(transcript.words, energy, media.ENERGY_STEP,
                                          brief["min_seconds"], brief["max_seconds"])
    moments = scoring.choose(candidates, brief["clips"])
    if len(moments) < brief["clips"]:
        raise ClipError("asked for %d clips of %.0f to %.0f seconds; this source has %d "
                        "non overlapping moments that fit" % (
                            brief["clips"], brief["min_seconds"], brief["max_seconds"],
                            len(moments)))
    jobs = []
    for n, moment in enumerate(moments, 1):
        focus = media.horizontal_focus(video, moment.start, moment.duration,
                                       info["width"], info["height"])
        for platform in brief["platforms"]:
            out_w, out_h = media.PLATFORMS[platform]
            box = media.crop_box(info["width"], info["height"], out_w, out_h, focus)
            name = "clip_%02d_%s.mp4" % (n, platform)
            srt = "clip_%02d.srt" % n if brief["captions"] else None
            jobs.append({
                "clip": n, "platform": platform, "file": name, "srt": srt,
                "size": [out_w, out_h], "crop": list(box), "focus_x": round(focus, 3),
                "command": media.cut_command(video, moment.start, moment.duration, box,
                                             out_w, out_h, name, srt, preset),
            })
    return info, transcript, moments, jobs


def write_outputs(out_dir, video, info, transcript, brief, moments, jobs):
    manifest = {
        "source": os.path.basename(video), "source_duration": round(info["duration"], 3),
        "source_size": [info["width"], info["height"]], "engine": transcript.engine,
        "brief": brief,
        "moments": [{"clip": n, "start": round(m.start, 3), "end": round(m.end, 3),
                     "duration": round(m.duration, 3), "score": round(m.score, 2),
                     "reason": m.reason_line(), "text": m.text}
                    for n, m in enumerate(moments, 1)],
        "files": [{k: j[k] for k in ("clip", "platform", "file", "srt", "size", "crop",
                                     "focus_x")} for j in jobs],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                           encoding="utf-8")
    lines = ["# Clips from %s" % manifest["source"], "",
             "%d clips, %s, captions %s. Transcription engine: %s. Moments are chosen "
             "from the transcript and the audio, with no retention data." % (
                 len(moments), ", ".join(brief["platforms"]),
                 "burned in" if brief["captions"] else "off", transcript.engine), ""]
    for m in manifest["moments"]:
        files = ", ".join("`%s`" % f["file"] for f in manifest["files"] if f["clip"] == m["clip"])
        lines += ["## Clip %d: %s to %s (%.1f s)" % (m["clip"], media.srt_time(m["start"]),
                                                     media.srt_time(m["end"]), m["duration"]),
                  "", "- Why this moment: %s" % m["reason"],
                  "- Transcript: \"%s\"" % (m["text"] if len(m["text"]) <= 160
                                             else m["text"][:157] + "..."),
                  "- Files: %s" % files, ""]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return manifest


def build_parser():
    parser = argparse.ArgumentParser(description="Cut short platform clips from a long video.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("plan", "score and print the plan; encode nothing"),
                            ("run", "score, then cut every clip")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--video", required=True)
        p.add_argument("--engine", default="transcript-file",
                       choices=sorted(transcribe.ENGINES))
        p.add_argument("--transcript", help="word timing JSON for the transcript-file engine")
        p.add_argument("--brief", help="brief JSON: clips, platforms, captions, min/max_seconds")
        p.add_argument("--clips", type=int)
        p.add_argument("--platforms", help="comma separated: " + ", ".join(sorted(media.PLATFORMS)))
        p.add_argument("--captions", action="store_true", help="burn in captions")
        p.add_argument("--min-seconds", dest="min_seconds", type=float)
        p.add_argument("--max-seconds", dest="max_seconds", type=float)
        p.add_argument("--out", default="clips-out")
        p.add_argument("--preset", default="veryfast", help="libx264 preset")
    return parser


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out)
    try:
        brief = load_brief(args)
        engine = transcribe.make_engine(args.engine, args.transcript)
        info, transcript, moments, jobs = plan(args.video, engine, brief, out_dir, args.preset)
    except (ClipError, transcribe.EngineError, media.MediaError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    for n, m in enumerate(moments, 1):
        stdout.write("clip %d  %7.2f-%7.2fs  score %5.2f  %s\n"
                     % (n, m.start, m.end, m.score, m.reason_line()))
    if args.command == "plan":
        for job in jobs:
            stdout.write("  %s: %s\n" % (job["file"], " ".join(job["command"])))
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        for n, m in enumerate(moments, 1):
            if brief["captions"]:
                media.write_srt(out_dir / ("clip_%02d.srt" % n), transcript.words, m.start, m.end)
        for job in jobs:
            media.run_in(job["command"], cwd=str(out_dir))
    except (media.MediaError, OSError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    write_outputs(out_dir, args.video, info, transcript, brief, moments, jobs)
    stdout.write("wrote %d files, manifest.json and report.md to %s\n" % (len(jobs), out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
