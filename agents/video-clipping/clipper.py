#!/usr/bin/env python3
"""Video clipping agent: one long video in, short platform clips out.

Takes a source video and a brief (how many clips, which platform shapes,
captions or not, the clip length range), transcribes the speech with word
timing, scores candidate moments (by retention data too, when given), and cuts the
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

Retention or "most replayed" data for the source, when the buyer has it,
goes in with --retention FILE (issue #130), a JSON object:

    {"kind": "most_replayed" or "audience_retention",
     "source": "where the data came from, in the operator's words",
     "points": [{"t": seconds, "value": number}, ...]}

The moments are then ranked by it first (scoring.py), every reason line
cites it, and the report lists the data's top moments with the clip that
covers each one, or why none does. Without the file the report says the
moments came from content analysis with no retention data. This program
does not fetch retention data from any platform; it reads the file given.

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


def load_retention(path, duration):
    """The Retention curve from --retention FILE, or None without one."""
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        retention = scoring.Retention.from_json(data)
    except (OSError, ValueError) as err:
        raise ClipError("cannot use retention file %s: %s" % (path, err))
    last = retention.points[-1][0]
    if last > duration + 1.0:
        raise ClipError("retention file %s runs to %.1f s but the video is %.1f s long; is it for this video?"
                        % (path, last, duration))
    return retention


def peak_notes(retention, duration, candidates, moments, brief):
    """For each top retention moment: the clip that covers it, or why none does."""
    peaks, median = retention.peaks(duration, brief["clips"])
    notes = []
    for t, value in peaks:
        clip = next((n for n, m in enumerate(moments, 1) if m.start <= t <= m.end), None)
        if clip is not None:
            why = "covered by clip %d" % clip
        else:
            covering = [c for c in candidates if c.start <= t <= c.end]
            if not covering:
                why = ("not covered: no run of whole sentences %.0f to %.0f seconds long contains it"
                       % (brief["min_seconds"], brief["max_seconds"]))
            else:
                best = max(covering, key=lambda c: c.score)
                clash = [n for n, m in enumerate(moments, 1) if not (best.end <= m.start or best.start >= m.end)]
                if clash:
                    why = ("not covered: the best span containing it (%.2f to %.2f s) overlaps clip %s, which scored "
                           "higher" % (best.start, best.end, ", ".join(str(n) for n in clash)))
                else:
                    why = ("not covered: the best span containing it (%.2f to %.2f s) scored %.2f, below the %d "
                           "clips chosen" % (best.start, best.end, best.score, len(moments)))
        notes.append({"t": round(t, 2), "value": round(value, 4), "lift": round(value / median, 2) if median else None,
                      "result": why})
    return notes


def plan(video, engine, brief, out_dir, preset, retention_path=None):
    media.require_tools()
    info = media.probe(video)
    retention = load_retention(retention_path, info["duration"])
    if not info["has_audio"]:
        raise ClipError("%s has no audio stream to transcribe" % video)
    transcript = engine.transcribe(video)
    if not transcript.words:
        raise ClipError("the transcript has no words; nothing to score")
    energy = media.audio_energy(video)
    candidates = scoring.score_candidates(transcript.words, energy, media.ENERGY_STEP,
                                          brief["min_seconds"], brief["max_seconds"],
                                          retention, info["duration"])
    moments = scoring.choose(candidates, brief["clips"])
    if len(moments) < brief["clips"]:
        raise ClipError("asked for %d clips of %.0f to %.0f seconds; this source has %d "
                        "non overlapping moments that fit" % (
                            brief["clips"], brief["min_seconds"], brief["max_seconds"],
                            len(moments)))
    info["retention"] = None
    if retention is not None:
        info["retention"] = {"kind": retention.kind, "source": retention.source,
                             "points": len(retention.points),
                             "median": round(retention.median(info["duration"]), 4),
                             "peaks": peak_notes(retention, info["duration"], candidates, moments, brief)}
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
        "brief": brief, "retention": info.get("retention"),
        "moments": [{"clip": n, "start": round(m.start, 3), "end": round(m.end, 3),
                     "duration": round(m.duration, 3), "score": round(m.score, 2),
                     "retention_lift": None if m.retention_lift is None else round(m.retention_lift, 2),
                     "reason": m.reason_line(), "text": m.text}
                    for n, m in enumerate(moments, 1)],
        "files": [{k: j[k] for k in ("clip", "platform", "file", "srt", "size", "crop",
                                     "focus_x")} for j in jobs],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                           encoding="utf-8")
    ret = manifest["retention"]
    if ret is None:
        basis = "Moments are chosen from the transcript and the audio, with no retention data."
    else:
        basis = ("Moments are ranked first by the %s data supplied (%d points; source as given: %s), then by the "
                 "transcript and the audio." % (ret["kind"].replace("_", " "), ret["points"], ret["source"]))
    lines = ["# Clips from %s" % manifest["source"], "",
             "%d clips, %s, captions %s. Transcription engine: %s. %s" % (
                 len(moments), ", ".join(brief["platforms"]),
                 "burned in" if brief["captions"] else "off", transcript.engine, basis), ""]
    if ret is not None:
        lines += ["## Retention data", "",
                  "The data's highest moments above its median (%s), and what became of each:" % ret["median"], ""]
        lines += ["- %s (value %s, %sx the median): %s" % (media.srt_time(p["t"]), p["value"], p["lift"], p["result"])
                  for p in ret["peaks"]] or ["- none: no moment rises above the median"]
        lines.append("")
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
        p.add_argument("--retention", help="retention or most replayed data for this video, JSON "
                                            "{kind, source, points: [{t, value}]}")
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
        info, transcript, moments, jobs = plan(args.video, engine, brief, out_dir, args.preset, args.retention)
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
