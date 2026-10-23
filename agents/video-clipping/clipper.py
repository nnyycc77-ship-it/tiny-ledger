#!/usr/bin/env python3
"""Video clipping agent: one long video in, short platform clips out.

Takes a source video and a brief (how many clips, which platform shapes,
captions or not, the clip length range), transcribes the speech with word
timing, scores candidate moments (by retention data too, when given), and cuts the
chosen moments with ffmpeg: resized per platform, reframed to keep the
speaker in frame, captions burned in only when the brief asks. Every chosen
moment carries a one line reason.

Three commands, all run from the repository root:

  plan  transcribe and score, then print the chosen moments, their reasons,
        and the exact ffmpeg command for every clip. Encodes nothing.
  run   the same, then cut every clip and write, in the output folder, the
        clips, manifest.json (moments, reasons, files) and report.md (the
        deliverable Markdown, the body a NEAR assignment submit carries as
        deliverableMarkdown; see near-agent/README.md).
  revise
        change only the named clips of an earlier delivery: the next best
        moment that overlaps no clip, or bounds the buyer gives (never
        through a word). Every other clip is copied byte for byte into a new
        folder, and the report lists each file's status and SHA-256.

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
import hashlib
import json
import os
import shutil
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
    jobs = make_jobs(video, info, brief, list(enumerate(moments, 1)), preset)
    return info, transcript, moments, jobs


def make_jobs(video, info, brief, numbered, preset):
    """One ffmpeg job per (clip number, moment) and platform."""
    jobs = []
    for n, moment in numbered:
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
    return jobs


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


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def revise_plan(args, video, engine, preset):
    """Read an earlier delivery and choose the replacement moments for the
    named clips. Every other clip is kept exactly as delivered."""
    src_dir, out_dir = Path(args.from_dir), Path(args.out)
    try:
        with open(src_dir / "manifest.json", encoding="utf-8") as fh:
            old = json.load(fh)
    except (OSError, ValueError) as err:
        raise ClipError("cannot read %s: %s" % (src_dir / "manifest.json", err))
    if out_dir.resolve() == src_dir.resolve():
        raise ClipError("--out must be a new folder; the earlier delivery is never overwritten")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise ClipError("--out %s already holds files; give an empty or new folder" % out_dir)
    numbers = [m["clip"] for m in old["moments"]]
    try:
        named = sorted({int(x) for x in args.clips_to_change.split(",") if x.strip()})
    except ValueError:
        raise ClipError("--clips takes clip numbers, for example 2 or 1,3")
    unknown = [n for n in named if n not in numbers]
    if not named or unknown:
        raise ClipError("no clip %s in the earlier delivery; it has clips %s"
                        % (", ".join(map(str, unknown)) or "(none)", ", ".join(map(str, numbers))))
    if os.path.basename(video) != old["source"]:
        raise ClipError("the earlier delivery was cut from %s, not %s" % (old["source"], os.path.basename(video)))
    media.require_tools()
    info = media.probe(video)
    if abs(info["duration"] - old["source_duration"]) > 0.05:
        raise ClipError("%s is %.3f s long; the earlier delivery's source was %.3f s, so it is not the same file"
                        % (video, info["duration"], old["source_duration"]))
    retention = load_retention(getattr(args, "retention", None), info["duration"])
    if old.get("retention") and retention is None:
        raise ClipError("the earlier delivery ranked moments by %s data (%s); pass the same --retention file"
                        % (old["retention"]["kind"], old["retention"]["source"]))
    if retention is not None and not old.get("retention"):
        raise ClipError("the earlier delivery used no retention data; a revision keeps the original basis")
    brief = old["brief"]
    transcript = engine.transcribe(video)
    energy = media.audio_energy(video)
    candidates = scoring.score_candidates(transcript.words, energy, media.ENERGY_STEP,
                                          brief["min_seconds"], brief["max_seconds"],
                                          retention, info["duration"])
    kept = [m for m in old["moments"] if m["clip"] not in named]
    replaced = [m for m in old["moments"] if m["clip"] in named]

    def clear_of(cand, others):
        return all(cand.end <= o["start"] or cand.start >= o["end"] for o in others)

    if args.start is not None or args.end is not None:
        if len(named) != 1 or args.start is None or args.end is None:
            raise ClipError("--start and --end set one clip's bounds: name exactly one clip and give both")
        start, end = float(args.start), float(args.end)
        if not 0 <= start < end <= info["duration"]:
            raise ClipError("need 0 <= start < end <= %.3f" % info["duration"])
        cut = [w.text for w in transcript.words if w.start < start < w.end or w.start < end < w.end]
        if cut:
            raise ClipError("those bounds cut through the word(s) %s; move them to a gap between words"
                            % ", ".join(repr(w) for w in cut))
        inside = [w for w in transcript.words if w.start >= start and w.end <= end]
        if not inside:
            raise ClipError("no words between %.3f and %.3f s" % (start, end))
        new = [scoring.Moment(start, end, " ".join(w.text for w in inside), 0.0,
                              ["bounds set by the change request"])]
        if not clear_of(new[0], kept):
            raise ClipError("those bounds overlap a clip that is kept")
    else:
        free = [c for c in candidates if clear_of(c, kept + replaced)]
        new = scoring.choose(free, len(named))
        if len(new) < len(named):
            raise ClipError("asked to change %d clip(s); this source has %d other non overlapping moments "
                            "that fit %.0f to %.0f seconds" % (len(named), len(new), brief["min_seconds"],
                                                               brief["max_seconds"]))
        for m in new:
            m.reasons = ["next best moment after the change request"] + m.reasons
    numbered = list(zip(named, new))
    jobs = make_jobs(video, info, brief, numbered, preset)
    return old, info, transcript, brief, kept, numbered, jobs, retention, candidates


def revise(args, stdout, stderr):
    src_dir, out_dir = Path(args.from_dir), Path(args.out)
    try:
        engine = transcribe.make_engine(args.engine, args.transcript)
        old, info, transcript, brief, kept, numbered, jobs, retention, candidates = revise_plan(
            args, args.video, engine, args.preset)
    except (ClipError, transcribe.EngineError, media.MediaError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    named = [n for n, _ in numbered]
    kept_files = [f for f in old["files"] if f["clip"] not in named]
    kept_srts = sorted({f["srt"] for f in kept_files if f.get("srt")})
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        for name in [f["file"] for f in kept_files] + kept_srts:
            shutil.copyfile(src_dir / name, out_dir / name)
        for n, m in numbered:
            if brief["captions"]:
                media.write_srt(out_dir / ("clip_%02d.srt" % n), transcript.words, m.start, m.end)
        for job in jobs:
            media.run_in(job["command"], cwd=str(out_dir))
    except (media.MediaError, OSError) as err:
        stderr.write("error: %s\n" % err)
        return 2
    by_clip = dict(numbered)
    for m in kept:
        by_clip[m["clip"]] = scoring.Moment(m["start"], m["end"], m["text"], m["score"],
                                            m["reason"].split("; "))
        by_clip[m["clip"]].retention_lift = m.get("retention_lift")
    ordered = [by_clip[n] for n in sorted(by_clip)]
    info["retention"] = None
    if retention is not None:
        info["retention"] = {"kind": retention.kind, "source": retention.source,
                             "points": len(retention.points),
                             "median": round(retention.median(info["duration"]), 4),
                             "peaks": peak_notes(retention, info["duration"], candidates, ordered, brief)}
    all_jobs = sorted([dict(f) for f in kept_files] + jobs, key=lambda j: (j["clip"], j["file"]))
    manifest = write_outputs(out_dir, args.video, info, transcript, brief, ordered, all_jobs)
    clip_of = {f["file"]: f["clip"] for f in manifest["files"]}
    clip_of.update({f["srt"]: f["clip"] for f in manifest["files"] if f.get("srt")})
    before = {name: _sha256(src_dir / name) for name in clip_of if (src_dir / name).is_file()}
    manifest["revision"] = {"from": os.path.basename(os.path.abspath(src_dir)), "changed_clips": named,
                            "note": args.note, "files": [
                                {"file": name, "status": "changed" if clip_of[name] in named else "kept as delivered",
                                 "sha256_before": before.get(name), "sha256": _sha256(out_dir / name)}
                                for name in sorted(clip_of)]}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines = ["", "## Revision", "",
             "Change request: %s" % (args.note or "(no note given)"),
             "Changed clip(s): %s. Every other clip is copied byte for byte from the earlier delivery."
             % ", ".join(map(str, named)), "",
             "| File | Status | SHA-256 |", "| --- | --- | --- |"]
    for row in manifest["revision"]["files"]:
        status = row["status"] + (" (was `%s`)" % row["sha256_before"] if row["status"] == "changed" else "")
        lines.append("| `%s` | %s | `%s` |" % (row["file"], status, row["sha256"]))
    with open(out_dir / "report.md", "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    stdout.write("changed clip(s) %s, kept %d file(s), in %s\n"
                 % (", ".join(map(str, named)), len(kept_files) + len(kept_srts), out_dir))
    return 0


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
    r = sub.add_parser("revise", help="change only the named clips of an earlier delivery; keep the rest")
    r.add_argument("--from", dest="from_dir", required=True, help="the earlier delivery folder (its manifest.json)")
    r.add_argument("--clips", dest="clips_to_change", required=True, help="clip numbers to change, for example 2 or 1,3")
    r.add_argument("--video", required=True, help="the same source video the delivery was cut from")
    r.add_argument("--engine", default="transcript-file", choices=sorted(transcribe.ENGINES))
    r.add_argument("--transcript", help="word timing JSON for the transcript-file engine")
    r.add_argument("--retention", help="the same retention file the earlier delivery used, when it used one")
    r.add_argument("--start", type=float, help="new start, seconds (one named clip only, with --end)")
    r.add_argument("--end", type=float, help="new end, seconds (one named clip only, with --start)")
    r.add_argument("--note", default="", help="the buyer's change request, quoted in the report")
    r.add_argument("--out", required=True, help="a new folder for the revised delivery")
    r.add_argument("--preset", default="veryfast", help="libx264 preset")
    return parser


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    if args.command == "revise":
        return revise(args, stdout, stderr)
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
