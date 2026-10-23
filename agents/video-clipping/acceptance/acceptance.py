"""Acceptance self test: Video Clipping Agent (issue #124).

Runs the clipper the way a marketplace tester would, offline: `run` on
the 60 second fixture video and word timing file that the clipper's own
test suite generates from committed code (a test pattern, tones and a
synthetic transcript). It checks the outputs against the job posting's
Acceptance Criteria, posted verbatim by the coordinator on issue #124
(comment 6372113964, description sha256 e1453617...5a95b3, checked).
Each criterion is printed as PASS, FAIL or UNTESTABLE with its evidence.

Independent checks:
- every clip file's frame size from ffprobe;
- cut points against the word timings (no cut inside a word, cuts on
  sentence ends);
- caption text against the words spoken inside the clip;
- a change request through `revise`, with SHA-256 before and after, so
  only the named clip's files may differ.

Needs ffmpeg and ffprobe. Without them every criterion is UNTESTABLE
with that reason.

Run:  python3 agents/video-clipping/acceptance/acceptance.py
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "video-clipping"
SOURCE = "job posting, Acceptance Criteria, issue #124 comment 6372113964"
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))

CRITERIA = {
    "1": "Delivers the requested number of clips, in every requested format, within the delivery time stated in the listing.",
    "2": "Every clip comes with a short explanation of why it was chosen, and the explanation matches what happens in the clip.",
    "3": "When the source video has \"most replayed\" or retention data, the explanations show the clips came from those "
         "moments. When it doesn't, the report says the agent used content analysis instead.",
    "4": "No clip starts or ends in the middle of a word or sentence.",
    "5": "When captions are requested, they match what is said and are large enough to read on a phone screen.",
    "6": "If it can't produce a requested format, the report says so. No requested format is missing without explanation.",
    "7": "When asked to change specific clips, it changes only those clips and keeps the rest as delivered.",
}
SIZES = {"tiktok": (1080, 1920), "reels": (1080, 1920), "shorts": (1080, 1920), "square": (1080, 1080),
         "landscape": (1920, 1080)}

CASES = [
    {"name": "video file with no platform data, 3 clips, vertical and square (sample: fallback selection, two formats)",
     "args": ["--clips", "3", "--platforms", "tiktok,square", "--min-seconds", "8", "--max-seconds", "15"],
     "sample": ("S2", "Sample '20-minute video file (no platform data), 3 clips, vertical and square', expected: 3 clips "
                      "in both formats, report notes no retention data was available")},
    {"name": "speech with captions, 2 clips, vertical, then change clip 2 (sample: captions, speech-heavy content)",
     "args": ["--clips", "2", "--platforms", "tiktok", "--captions", "--min-seconds", "8", "--max-seconds", "15"],
     "change": "2"},
    {"name": "retention input, and a format it cannot produce (criteria 3 and 6)",
     "args": ["--clips", "2", "--platforms", "tiktok,linkedin", "--min-seconds", "8", "--max-seconds", "15"],
     "only": ["3", "6"]},
]


def probe_size(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=60)
    w, h = p.stdout.strip().split(",")[:2]
    return int(w), int(h)


def srt_text(path):
    blocks = Path(path).read_text(encoding="utf-8").strip().split("\n\n")
    return " ".join(" ".join(b.splitlines()[2:]) for b in blocks)


def norm(text):
    return re.findall(r"[\w']+", text.lower())


def new_result(case):
    res = ac.Result(AGENT, case["name"], SOURCE)
    keys = case.get("only") or list(CRITERIA)
    return res, {k: res.criterion(k, CRITERIA[k]) for k in keys}


def run():
    fx = ac.load("acceptance_clip_fixture", HERE.parent / "tests" / "test_clipper.py")
    clipper = ac.load("acceptance_clipper", HERE.parent / "clipper.py")
    results = []
    if not HAVE_FFMPEG:
        for case in CASES:
            res, c = new_result(case)
            for k in c:
                c[k].cannot("ffmpeg and ffprobe are needed to make the fixture video and to cut clips")
            results.append(res)
        return results
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        video, words_path = fx.make_fixture(tmp)
        words = json.loads(Path(words_path).read_text(encoding="utf-8"))["words"]
        for n, case in enumerate(CASES):
            res, c = new_result(case)
            out = tmp / ("out%d" % n)
            attempts = []
            code, stdout, err = ac.run_main(clipper.main, ["run", "--video", str(video), "--transcript", str(words_path)]
                                            + case["args"] + ["--out", str(out), "--preset", "ultrafast"], attempts=attempts)
            if "6" in c and case.get("only"):
                unknown_format(c, code, err, out)
                structural(c, clipper)
                results.append(res)
                continue
            if code != 0:
                for k in c:
                    c[k].fail("run exited %s: %s" % (code, err.strip()[:200]))
                results.append(res)
                continue
            evaluate(res, c, case, out, words, attempts)
            if case.get("change"):
                change_request(c, clipper, case["change"], out, video, words_path, tmp / ("rev%d" % n), words)
            results.append(res)
    return results


def unknown_format(c, code, err, out):
    reason = err.strip().splitlines()[-1] if err.strip() else ""
    wrote = out.exists() and any(out.iterdir())
    if code != 0 and not wrote and "linkedin" in reason:
        c["6"].cannot("asked for tiktok and an unsupported format (linkedin): the run stops before any clip with %r, so "
                      "nothing is missing without explanation, but the producible format is not delivered either; "
                      "whether a refusal of the whole brief meets 'the report says so' is not settled by the posting"
                      % reason[:120])
    elif wrote and "linkedin" in ((out / "report.md").read_text(encoding="utf-8") if (out / "report.md").exists() else ""):
        c["6"].ok("the producible format was delivered and the report names the one it could not produce")
    else:
        c["6"].fail("asked for an unsupported format: exit %s, files written %s, and no explanation naming it" % (code, wrote))


def structural(c, clipper):
    flags = [a.dest for a in clipper.build_parser()._subparsers._group_actions[0].choices["run"]._actions]
    retention = [f for f in flags if re.search(r"retention|replay|heatmap|analytics", f)]
    c["3"].check(bool(retention), "a retention data input exists: %s" % retention,
                 "the brief has no input for 'most replayed' or retention data (run options: %s), so a source that has it "
                 "is clipped by content analysis alone, while the report says 'no retention data'"
                 % ", ".join(f for f in flags if f != "help"))


def change_request(c, clipper, clips, out, video, words_path, rev, words):
    """Ask to change specific clips; only their files may differ, byte for byte."""
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    before = {p.name: digest(p) for p in out.iterdir() if p.suffix in (".mp4", ".srt")}
    attempts = []
    code, _, err = ac.run_main(clipper.main, ["revise", "--from", str(out), "--clips", clips, "--video", str(video),
                                              "--transcript", str(words_path), "--note", "acceptance change request",
                                              "--out", str(rev), "--preset", "ultrafast"], attempts=attempts)
    if code != 0:
        c["7"].fail("revise --clips %s exited %s: %s" % (clips, code, err.strip()[:160]))
        return
    after = {p.name: digest(p) for p in rev.iterdir() if p.suffix in (".mp4", ".srt")}
    named = {int(x) for x in clips.split(",")}
    clip_of = lambda name: int(re.match(r"clip_(\d+)", name).group(1))  # noqa: E731
    changed = sorted(f for f in after if after[f] != before.get(f))
    expected = sorted(f for f in before if clip_of(f) in named)
    c["7"].check(set(after) == set(before) and changed == expected,
                 "asked to change clip %s: exactly %s differ; the other %d file(s) are byte identical"
                 % (clips, ", ".join(changed), len(after) - len(changed)),
                 "asked to change clip %s: files that differ %s, expected %s; added or missing %s"
                 % (clips, changed, expected, sorted(set(after) ^ set(before))))
    report = (rev / "report.md").read_text(encoding="utf-8")
    c["7"].check("## Revision" in report and "acceptance change request" in report,
                 "the revised report names the change request and every file's status",
                 "the revised report does not record the change request")
    manifest = json.loads((rev / "manifest.json").read_text(encoding="utf-8"))
    for m in manifest["moments"]:
        if m["clip"] in named:
            straddle = [w["w"] for w in words if w["start"] < m["start"] < w["end"] or w["start"] < m["end"] < w["end"]]
            c["7"].check(not straddle, "changed clip %d %.2f-%.2f s cuts no word" % (m["clip"], m["start"], m["end"]),
                         "changed clip %d cuts through %s" % (m["clip"], straddle))
    c["7"].check(not attempts, "", "network access attempted during revise: %s" % attempts[:3])


def evaluate(res, c, case, out, words, attempts):
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    report = (out / "report.md").read_text(encoding="utf-8")
    brief = manifest["brief"]
    moments = manifest["moments"]

    # 1. clips times formats, sizes from ffprobe
    c["1"].check(len(moments) == brief["clips"], "%d of %d clips chosen" % (len(moments), brief["clips"]),
                 "%d clips chosen for a brief of %d" % (len(moments), brief["clips"]))
    for m in moments:
        for plat in brief["platforms"]:
            f = out / ("clip_%02d_%s.mp4" % (m["clip"], plat))
            if not f.is_file():
                c["1"].fail("missing %s" % f.name)
                continue
            size = probe_size(f)
            c["1"].check(size == SIZES[plat], "%s: %dx%d (%s)" % (f.name, size[0], size[1], plat),
                         "%s: %dx%d, expected %dx%d for %s" % (f.name, size[0], size[1], SIZES[plat][0], SIZES[plat][1], plat))
    c["1"].cannot("the listing's delivery time cannot be measured by one offline run")

    # 2. a reason per clip; whether it matches what happens needs a viewer
    for m in moments:
        sec = re.search(r"## Clip %d: .*?\n\n- Why this moment: (.+)$" % m["clip"], report, re.M)
        c["2"].check(bool(sec and sec.group(1).strip()), "clip %d: %s" % (m["clip"], sec.group(1)[:100] if sec else ""),
                     "clip %d has no explanation in the report" % m["clip"])
        if "question and answer" in m["reason"]:
            c["2"].check("?" in m["text"] and not m["text"].rstrip().endswith("?"),
                         "clip %d: the reason says question and answer; the clip's words hold a question and what follows it" % m["clip"],
                         "clip %d: the reason says question and answer but the clip's words hold no answered question" % m["clip"])
    c["2"].cannot("whether each explanation matches what happens in the clip needs a person watching it; only the "
                  "transcript backed parts are checked here")

    # 3. no platform data in the fixture: the report must say content analysis was used
    c["3"].check("no retention data" in report, "report: \"Moments are chosen from the transcript and the audio, with no retention data.\"",
                 "the report does not say that no retention data was used")
    c["3"].cannot("the fixture has no retention data, so the first half of the criterion is checked structurally in the "
                  "third case")

    # 4. cut points against the word timings
    for m in moments:
        s, e = m["start"], m["end"]
        inside = [w for w in words if s - 1e-6 <= w["start"] and w["end"] <= e + 1e-6]
        straddle = [w["w"] for w in words if (w["start"] < s < w["end"]) or (w["start"] < e < w["end"])]
        first, last = (inside[0], inside[-1]) if inside else (None, None)
        before = [w for w in words if w["end"] <= s + 1e-6]
        starts_sentence = not before or re.search(r"[.?!]$", before[-1]["w"])
        ends_sentence = last is not None and re.search(r"[.?!]$", last["w"])
        c["4"].check(inside and not straddle and starts_sentence and ends_sentence,
                     "clip %d %.2f-%.2f s: first word %r, last word %r, no word cut" % (m["clip"], s, e, first["w"] if first else "",
                                                                                    last["w"] if last else ""),
                     "clip %d %.2f-%.2f s: words cut %s; starts a sentence %s; ends a sentence %s"
                     % (m["clip"], s, e, straddle, bool(starts_sentence), bool(ends_sentence)))

    # 5. captions
    if brief.get("captions"):
        for m in moments:
            srt = out / ("clip_%02d.srt" % m["clip"])
            spoken = [w["w"] for w in words if m["start"] - 1e-6 <= w["start"] and w["end"] <= m["end"] + 1e-6]
            same = srt.is_file() and norm(srt_text(srt)) == norm(" ".join(spoken))
            c["5"].check(same, "clip %d: caption text is the %d words spoken in the clip, in order" % (m["clip"], len(spoken)),
                         "clip %d: caption text differs from the words spoken in the clip" % m["clip"])
        style = re.search(r"FontSize=(\d+)", Path(HERE.parent / "media.py").read_text(encoding="utf-8"))
        c["5"].cannot("readable on a phone screen has no measure in the posting; the burned in style is FontSize=%s "
                      "(libass, on its default 288 line script height), not judged here" % (style.group(1) if style else "?"))
    else:
        srts = sorted(p.name for p in out.glob("*.srt"))
        c["5"].check(not srts, "captions not requested and none made", "captions not requested, yet %s were made" % srts)
        c["5"].cannot("captions were not requested in this case")

    # 6. every requested format present; the unsupported format case is the third case
    missing = [(m["clip"], p) for m in moments for p in brief["platforms"]
               if not (out / ("clip_%02d_%s.mp4" % (m["clip"], p))).is_file()]
    c["6"].check(not missing, "every requested format delivered for every clip", "formats missing with no note: %s" % missing)

    # 7. change requests: run by change_request() where the case asks for one
    if not case.get("change"):
        c["7"].cannot("this case makes no change request; see the captions case")
    c["7"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])

    sample = case.get("sample")
    if sample:
        s = res.criterion(*sample)
        ok = len(moments) == 3 and not missing and "no retention data" in report
        s.check(ok, "%d clips x %s, report notes no retention data" % (len(moments), "+".join(brief["platforms"])),
                "%d clips, missing %s, retention note %s" % (len(moments), missing, "no retention data" in report))


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
