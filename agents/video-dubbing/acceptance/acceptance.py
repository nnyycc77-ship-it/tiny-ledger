"""Acceptance self test: Video Dubbing Agent (issue #124).

Runs the dubber the way a marketplace tester would, offline:
- `run` on the fixture video that the dubber's own test suite generates
  from committed code: a test pattern, two flite stock-voice speakers and
  a two tone music bed;
- the four timed segments and the glossary from that suite.

It checks the outputs against the job posting's Acceptance Criteria,
quoted by the coordinator on issue #77 (comment 6365954974). Each
criterion is printed as PASS, FAIL or UNTESTABLE with its evidence.

Independent checks:
- files on disk;
- SRT cues against the source segments;
- the protected terms in every subtitle and voiced wording;
- ffmpeg volumedetect on a stretch with no dialogue, original against
  dub, so a background that is gone shows as silence.

Line timing comes from the dubber's own placement record (manifest.json),
which is the agent's claim; it is cross-checked against the SRT. Only the
offline stub voice runs: a tone per speaker, not speech.

Needs ffmpeg with the flite filter. Without them every criterion is
UNTESTABLE with that reason.

Run:  python3 agents/video-dubbing/acceptance/acceptance.py
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "video-dubbing"
SOURCE = "job posting, Acceptance Criteria, issue #77 comment 6365954974"
FIX = HERE / "fixtures"
QUIET = (15.0, 19.5)  # seconds with no dialogue in the fixture (last line ends at 14.0 s of 20 s)

CRITERIA = {
    "1": "Delivers one finished video and one subtitle file per requested language, within the delivery time stated in the listing.",
    "2": "Every spoken line in the original has a dubbed line. Any line left untranslated is listed in the report with the reason.",
    "3": "Each dubbed line starts within one second of the original line, and no dubbed line runs over the next speaker.",
    "4": "Background music and sound effects from the original are still audible in the dubbed version.",
    "5": "Names and terms on the buyer's list appear unchanged in the audio and subtitles.",
    "6": "A fluent speaker of the target language confirms each line means the same as the original, with nothing added or missing.",
    "7": "The subtitle file matches the dubbed audio line by line.",
    "8": "When no consent is confirmed, the dubbed audio uses a stock voice, not the speaker's own voice.",
}

CASES = [
    {"name": "two-speaker interview with music, stock voices (sample: multiple speakers, audio mixing)",
     "args": ["--languages", "es", "--voice", "stub"]},
    {"name": "term list, two languages, spoken subtitles (sample: term list, subtitles)",
     "args": ["--languages", "es,fr", "--voice", "stub", "--subtitles", "spoken"]},
    {"name": "own voice requested without and with a consent record (sample: voice recreation)",
     "own_voice": True, "only": ["8"]},
]
TERMS = ["Hojo", "NEAR"]


def srt(path):
    cues = []
    for block in Path(path).read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        m = re.match(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})", lines[1])
        g = [int(x) for x in m.groups()]
        cues.append({"start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
                     "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0, "text": " ".join(lines[2:])})
    return cues


def loudness(path, start, end):
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-ss", str(start), "-to", str(end), "-i", str(path),
                        "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True, timeout=120)
    mean = re.search(r"mean_volume: (-?[\d.]+|-inf) dB", p.stderr)
    peak = re.search(r"max_volume: (-?[\d.]+|-inf) dB", p.stderr)
    as_f = lambda m: float("-inf") if not m or m.group(1) == "-inf" else float(m.group(1))  # noqa: E731
    return as_f(mean), as_f(peak)


def new_result(case):
    res = ac.Result(AGENT, case["name"], SOURCE)
    keys = case.get("only") or list(CRITERIA)
    return res, {k: res.criterion(k, CRITERIA[k]) for k in keys}


def make_inputs(fx, folder):
    holder = type("Holder", (), {})()
    holder.dir, holder.video = folder, folder / "guide.mp4"
    fx.FixtureRunTests._make_video.__func__(holder)
    segments = folder / "segments.json"
    segments.write_text(json.dumps({"segments": [{"start": a, "end": b, "text": t, "speaker": s}
                                                 for a, b, t, s in fx.SEGMENTS]}), encoding="utf-8")
    glossary = folder / "glossary.json"
    glossary.write_text(json.dumps(fx.GLOSSARY), encoding="utf-8")
    return holder.video, segments, glossary


def run():
    fx = ac.load("acceptance_dub_fixture", HERE.parent / "tests" / "test_dubber.py")
    dub = ac.load("acceptance_dubber", HERE.parent / "dubber.py")
    results = []
    if not fx.HAVE_MEDIA:
        for case in CASES:
            res, c = new_result(case)
            for k in c:
                c[k].cannot("ffmpeg, ffprobe or ffmpeg's flite filter is missing, so the fixture video cannot be made")
            results.append(res)
        return results
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        video, segments, glossary = make_inputs(fx, tmp)
        base = ["--video", str(video), "--segments", str(segments), "--glossary", str(glossary), "--dnt", ",".join(TERMS)]
        for n, case in enumerate(CASES):
            res, c = new_result(case)
            attempts = []
            if case.get("own_voice"):
                own_voice(c, dub, base, tmp / ("out%d" % n), attempts)
                results.append(res)
                continue
            out = tmp / ("out%d" % n)
            code, stdout, err = ac.run_main(dub.main, ["run"] + base + case["args"] + ["--out", str(out)], attempts=attempts)
            if code != 0:
                for k in c:
                    c[k].fail("run exited %s: %s" % (code, err.strip()[:200]))
                results.append(res)
                continue
            evaluate(c, case, out, video, fx, attempts)
            results.append(res)
    return results


def own_voice(c, dub, base, out, attempts):
    consent_ok = out.parent / "consent-complete.json"
    consent_ok.write_text(json.dumps({  # SYNTHETIC consent record for this test; no real person
        "basis": "buyer_is_speaker", "consent_record": "acceptance self test record (SYNTHETIC)",
        "rights_confirmed": True, "confirmed_by": "acceptance self test (SYNTHETIC)"}), encoding="utf-8")
    runs = []
    for label, extra in (("no consent record", []), ("complete consent record", ["--consent", str(consent_ok)])):
        target = out.parent / ("%s-%s" % (out.name, len(runs)))
        code, _, err = ac.run_main(dub.main, ["run"] + base + ["--languages", "es", "--voice", "own-voice"] + extra
                                   + ["--out", str(target)], attempts=attempts)
        wrote = target.exists() and any(target.iterdir())
        runs.append((label, code, err.strip().splitlines()[-1] if err.strip() else "", wrote))
    for label, code, why, wrote in runs:
        c["8"].check(code != 0 and not wrote, "%s: refused (exit %s), nothing written: %s" % (label, code, why[:110]),
                     "%s: own voice was not refused (exit %s, files written: %s)" % (label, code, wrote))
    c["8"].cannot("the posting says 'Otherwise, use a stock voice'; this agent refuses an own-voice request instead of "
                  "falling back to a stock voice, and whether a refusal meets the criterion is not settled by the posting")
    c["8"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])


def evaluate(c, case, out, video, fx, attempts):
    args = case["args"]
    langs = args[args.index("--languages") + 1].split(",")
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    report = (out / "report.md").read_text(encoding="utf-8")
    segs = fx.SEGMENTS
    stem = video.stem

    # 1. one video and one SRT per language
    for lang in langs:
        v, s = out / ("%s.%s.mp4" % (stem, lang)), out / ("%s.%s.srt" % (stem, lang))
        c["1"].check(v.is_file() and v.stat().st_size > 0 and s.is_file(),
                     "%s: %s (%d bytes) and %s" % (lang, v.name, v.stat().st_size if v.exists() else 0, s.name),
                     "%s: missing %s or %s" % (lang, v.name, s.name))
    extra = sorted(p.name for p in out.glob("*.mp4") if p.name.split(".")[-2] not in langs)
    c["1"].check(not extra, "no video for a language that was not requested", "unrequested videos: %s" % extra)
    c["1"].cannot("the listing's delivery time cannot be measured by one offline run")

    # 2. a dubbed line for every spoken line
    for lang in langs:
        cues, lines = srt(out / ("%s.%s.srt" % (stem, lang))), manifest["lines"][lang]
        c["2"].check(len(cues) == len(segs) == len(lines) and sorted(l["segment"] for l in lines) == list(range(len(segs))),
                     "%s: %d source lines, %d dubbed lines, %d subtitle cues" % (lang, len(segs), len(lines), len(cues)),
                     "%s: %d source lines but %d dubbed lines and %d cues" % (lang, len(segs), len(lines), len(cues)))
    m = re.search(r"Untranslated lines: (.*?)(?:\n|$)", report)
    c["2"].check(bool(m), "report states untranslated lines: %s" % (m.group(1)[:80] if m else ""),
                 "the report does not state untranslated lines")

    # 3. start within one second; no run over the next speaker (placement record, cross-checked with the SRT)
    for lang in langs:
        lines = sorted(manifest["lines"][lang], key=lambda l: l["segment"])
        cues = srt(out / ("%s.%s.srt" % (stem, lang)))
        for i, line in enumerate(lines):
            orig_start = segs[line["segment"]][0]
            over = re.search(r"runs ([\d.]+) s into the following pause", line.get("note", ""))
            real_end = line["end"] + (float(over.group(1)) if over else 0.0)
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            ok = abs(line["start"] - orig_start) <= 1.0 and abs(cues[i]["start"] - orig_start) <= 1.0
            ok = ok and (nxt is None or nxt["speaker"] == line["speaker"] or real_end <= nxt["start"])
            c["3"].check(ok, "%s line %d: starts %.2f s (original %.2f s), ends %.2f s%s"
                         % (lang, i, line["start"], orig_start, real_end,
                            "" if nxt is None else ", next speaker at %.2f s" % nxt["start"]),
                         "%s line %d: starts %.2f s against %.2f s, or ends %.2f s over the next speaker at %s"
                         % (lang, i, line["start"], orig_start, real_end, nxt["start"] if nxt else "-"))
    c["3"].ok("timing read from the dubber's placement record (manifest.json), cross-checked with the SRT starts")

    # 4. background still there, measured on a stretch with no dialogue
    o_mean, o_peak = loudness(video, *QUIET)
    for lang in langs:
        d_mean, d_peak = loudness(out / ("%s.%s.mp4" % (stem, lang)), *QUIET)
        c["4"].check(d_peak > -90.0, "%s: %.0f-%.0f s with no dialogue: dub mean %.1f dB (peak %.1f), original mean %.1f dB "
                     "(peak %.1f); the background is present, lowered by the ducking" % (lang, QUIET[0], QUIET[1], d_mean,
                                                                                      d_peak, o_mean, o_peak),
                     "%s: the dub is silent where the original has background (peak %.1f dB against %.1f dB)"
                     % (lang, d_peak, o_peak))

    # 5. protected terms verbatim in the subtitles and the voiced wording
    for lang in langs:
        cues = srt(out / ("%s.%s.srt" % (stem, lang)))
        lines = sorted(manifest["lines"][lang], key=lambda l: l["segment"])
        for i, (_, _, text, _) in enumerate(segs):
            for term in TERMS:
                if term in text:
                    c["5"].check(term in cues[i]["text"] and term in lines[i]["spoken"],
                                 "%s line %d: %r in the subtitle and the voiced wording" % (lang, i, term),
                                 "%s line %d: %r missing from the subtitle %r or the voiced wording %r"
                                 % (lang, i, term, cues[i]["text"], lines[i]["spoken"]))
    c["5"].cannot("the stub voice is a tone, so 'unchanged in the audio' is checked on the voiced wording only; hearing "
                  "the term needs speech from a real voice")

    # 6. meaning: a fluent speaker
    c["6"].cannot("needs a fluent speaker of the target language; no offline check can confirm meaning")

    # 7. subtitles against the dubbed audio, line by line
    mode = manifest.get("subtitles", "full")
    for lang in langs:
        cues = srt(out / ("%s.%s.srt" % (stem, lang)))
        lines = sorted(manifest["lines"][lang], key=lambda l: l["segment"])
        timing = all(abs(cu["start"] - li["start"]) < 0.01 for cu, li in zip(cues, lines)) and len(cues) == len(lines)
        c["7"].check(timing, "%s: %d cues, one per dubbed line, each at its line's start" % (lang, len(cues)),
                     "%s: cues and dubbed lines differ in number or start time" % lang)
        differ = [i for i, (cu, li) in enumerate(zip(cues, lines)) if cu["text"] != li["spoken"]]
        if mode == "spoken":
            c["7"].check(not differ, "%s: --subtitles spoken, every cue's text is the voiced wording" % lang,
                         "%s: --subtitles spoken, yet cue text differs from the voiced wording on lines %s" % (lang, differ))
        elif differ:
            c["7"].cannot("%s: default --subtitles full keeps the full translation, which differs from the tightened "
                          "voiced wording on line(s) %s; the report names them. Whether 'matches line by line' means the "
                          "wording or the cues is not settled by the posting (see the dubbing README)" % (lang, differ))
        breathe = [i for i, li in enumerate(lines) if "into the following pause" in li.get("note", "")]
        if breathe:
            c["7"].cannot("%s: line(s) %s run into the following pause, past the cue's end time; whether a cue must "
                          "cover that overrun is not settled by the posting" % (lang, breathe))

    # 8. stock voice without consent
    voice = manifest.get("voice")
    c["8"].check(voice in ("stub", "flite"), "voice used: %s (%s); no consent record was given"
                 % (voice, ", ".join("%s: %s" % kv for kv in manifest.get("speakers", {}).items())),
                 "voice used without a consent record: %s" % voice)
    c["8"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
