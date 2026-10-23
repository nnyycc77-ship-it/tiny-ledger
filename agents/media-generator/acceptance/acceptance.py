"""Acceptance self test: Pay-Per-Use Media Generator (issue #124).

Runs the media generator the way a marketplace tester would, offline:
- `generate` on a brief holding the job posting's four sample scenarios,
  plus a copyrighted character request;
- `revise` on one delivered file.

It checks the delivery against the job posting's Acceptance Criteria,
quoted by the coordinator on issue #78 (comment 6366897388). Each
criterion is printed as PASS, FAIL or UNTESTABLE with its evidence.

File checks read the files themselves with this script's own readers,
not the agent's:
- PNG width and height;
- GIF size and frame delays;
- WAV duration;
- SHA-256 before and after a revision.

Only the offline stub providers run, so the files are placeholders. The
criteria that need a human to look or listen are UNTESTABLE, with that
reason.

Run:  python3 agents/media-generator/acceptance/acceptance.py
"""

import hashlib
import json
import re
import struct
import sys
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "media-generator"
SOURCE = "job posting, Acceptance Criteria, issue #78 comment 6366897388"
FIX = HERE / "fixtures"
BRIEF = FIX / "brief-samples.json"

CRITERIA = {
    "1": "Delivers the requested number of files of each requested type, within the delivery time stated in the listing.",
    "2": "Every file has the requested size or aspect ratio, and every video or voiceover is within one second of the "
         "requested length.",
    "3": "Every subject, object and setting named in the brief is visible (or, for voiceovers, audible) in the result.",
    "4": "Voiceovers read the buyer's script word for word.",
    "5": "The report names the provider and model used for each file.",
    "6": "Requests for real identifiable people without consent, copyrighted characters, or other content against the "
         "rules are declined, and the report says why.",
    "7": "When asked to change specific files, it changes only those files and keeps the rest as delivered.",
}
EXT = {"image": ".png", "video": ".gif", "voice": ".wav"}


def png_size(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def gif_info(path):
    """(width, height, seconds) from the logical screen and the frame delays."""
    data = Path(path).read_bytes()
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("not a GIF")
    w, h = struct.unpack("<HH", data[6:10])
    centis = sum(struct.unpack("<H", data[m.start() + 4:m.start() + 6])[0]
                 for m in re.finditer(re.escape(b"\x21\xf9\x04"), data))
    return w, h, centis / 100.0


def wav_info(path):
    with wave.open(str(path), "rb") as w:
        seconds = w.getnframes() / float(w.getframerate())
    data = Path(path).read_bytes()
    m = re.search(rb"ICMT(....)", data, re.S)
    note = ""
    if m:
        n = struct.unpack("<I", m.group(1))[0]
        note = data[m.end():m.end() + n].decode("latin-1").rstrip("\x00")
    return seconds, note


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def aspect_ok(w, h, aspect):
    """Exact ratio up to one pixel of integer rounding."""
    aw, ah = [int(x) for x in aspect.split(":")]
    return abs(w * ah - h * aw) <= max(aw, ah)


def new_result(case):
    res = ac.Result(AGENT, case, SOURCE)
    return res, {k: res.criterion(k, v) for k, v in CRITERIA.items()}


def run():
    gen = ac.load("acceptance_mediagen", HERE.parent / "mediagen.py")
    call = lambda a: gen.main(a, env={})  # noqa: E731
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        out, rev = Path(tmp) / "out", Path(tmp) / "revised"
        attempts = []
        code, _, err = ac.run_main(call, ["generate", "--brief", str(BRIEF), "--out", str(out)], attempts=attempts)
        res, c = new_result("four sample scenarios plus a copyrighted character (samples 1 to 4)")
        if code != 0:
            for k in c:
                c[k].fail("generate exited %s: %s" % (code, err.strip()[:200]))
            return [res]
        evaluate(c, out, attempts)
        c["7"].cannot("this case makes no change request; see the revision case")
        results.append(res)

        manifest = json.loads((out / "delivery.json").read_text(encoding="utf-8"))
        target = manifest["files"][1]["file"]
        before = {f["file"]: sha(out / f["file"]) for f in manifest["files"]}
        attempts2 = []
        code, _, err = ac.run_main(call, ["revise", "--from", str(out), "--files", target, "--out", str(rev),
                                          "--note", "brighter light"], attempts=attempts2)
        res2, c2 = new_result("change one delivered file (criterion 7)")
        if code != 0:
            for k in c2:
                c2[k].fail("revise exited %s: %s" % (code, err.strip()[:200]))
            return results + [res2]
        evaluate(c2, rev, attempts2, revision=True)
        after = {p.name: sha(p) for p in rev.iterdir() if p.suffix in (".png", ".gif", ".wav")}
        changed = sorted(f for f in before if after.get(f) != before[f])
        c2["7"].check(changed == [target] and set(after) == set(before),
                      "asked to change %s: only that file's SHA-256 differs; the other %d file(s) are byte identical"
                      % (target, len(before) - 1),
                      "asked to change %s; files that differ: %s; files missing or added: %s"
                      % (target, changed, sorted(set(after) ^ set(before))))
        results.append(res2)
    return results


def evaluate(c, out, attempts, revision=False):
    brief = json.loads(BRIEF.read_text(encoding="utf-8"))["requests"]
    note = (out / "delivery-note.md").read_text(encoding="utf-8")
    manifest = json.loads((out / "delivery.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    declined = {r["index"]: r["declined"] for r in manifest["requests"] if r["declined"]}

    # 1. count per request and type; the delivery time is the listing's, not testable offline
    for i, req in enumerate(brief, 1):
        mine = [f for f in files if f["request"] == i]
        if i in declined:
            c["1"].check(not mine, "request %d declined, no file made" % i, "request %d declined yet files were made" % i)
            continue
        want = req.get("count", 1)
        types_ok = all(f["file"].endswith(EXT[req["type"]]) and (out / f["file"]).is_file() for f in mine)
        c["1"].check(len(mine) == want and types_ok, "request %d (%s): %d of %d file(s), all %s"
                     % (i, req["type"], len(mine), want, EXT[req["type"]]),
                     "request %d (%s): %d file(s) for a count of %d, or wrong type" % (i, req["type"], len(mine), want))
    c["1"].cannot("the listing's delivery time cannot be measured by an offline run on stub providers")

    # 2. size or aspect, and length within one second, read from the files
    for f in files:
        req, path = brief[f["request"] - 1], out / f["file"]
        try:
            if req["type"] == "image":
                w, h = png_size(path)
                aspect = req.get("aspect", "1:1")
                c["2"].check(aspect_ok(w, h, aspect), "%s: %dx%d, aspect %s" % (f["file"], w, h, aspect),
                             "%s: %dx%d is not aspect %s" % (f["file"], w, h, aspect))
            elif req["type"] == "video":
                w, h, secs = gif_info(path)
                aspect, length = req.get("aspect", "16:9"), req.get("length_seconds", 5)
                c["2"].check(aspect_ok(w, h, aspect) and abs(secs - length) <= 1.0,
                             "%s: %dx%d (%s), %.2f s against %s s" % (f["file"], w, h, aspect, secs, length),
                             "%s: %dx%d, %.2f s; asked %s and %s s" % (f["file"], w, h, secs, aspect, length))
            else:
                secs, _ = wav_info(path)
                length = req.get("length_seconds")
                if length is None:
                    c["2"].cannot("%s: no length in the brief, so the one second check has no target" % f["file"])
                else:
                    c["2"].check(abs(secs - length) <= 1.0, "%s: %.2f s against %s s" % (f["file"], secs, length),
                                 "%s: %.2f s, more than one second from %s s" % (f["file"], secs, length))
        except (ValueError, OSError, wave.Error, struct.error) as exc:
            c["2"].fail("%s: cannot be read as %s: %s" % (f["file"], req["type"], exc))

    # 3. subjects visible or audible: needs a person to look or listen
    c["3"].cannot("the files are offline placeholders, and whether a subject is visible or audible needs a person (or a "
                  "vision or speech check) on real provider output; the agent's own check reads what the provider "
                  "recorded it made: %s" % ("all files 'matches the brief'" if all(f.get("matches_brief") for f in files)
                                            else "some files do not match"))

    # 4. script word for word: the placeholder tone is not speech
    for f in files:
        req = brief[f["request"] - 1]
        if req["type"] != "voice":
            continue
        _, recorded = wav_info(out / f["file"])
        words = lambda s: re.findall(r"[\w']+", s.lower())  # noqa: E731
        same = words(req["script"]) == words(recorded.split("|")[0].split(":", 1)[-1]) or req["script"] in recorded
        c["4"].ok("%s: the script the provider recorded it read matches the brief word for word: %s"
                  % (f["file"], "yes" if same else "no")) if same else \
            c["4"].fail("%s: the recorded script differs from the brief's script" % f["file"])
    c["4"].cannot("the stub voice is a tone, not speech; whether a voice reads the script word for word needs a listener "
                  "or speech recognition on a live provider's audio")

    # 5. provider and model for each file
    # delivery table: File | Provider | Model | Attempt | SHA-256; revision table: File | Status | Provider | Model | SHA-256
    rows = dict((m.group(1), (m.group(2), m.group(3))) for m in
                re.finditer(r"^\| `([^`]+)` \| (\S+) \| (\S+) \| \d+ \|", note, re.M))
    rows.update((m.group(1), (m.group(2), m.group(3))) for m in
                re.finditer(r"^\| `([^`]+)` \| (?:changed \(was `[0-9a-f]+`\)|kept as delivered) \| (\S+) \| (\S+) \|", note, re.M))
    for f in files:
        prov = rows.get(f["file"])
        c["5"].check(bool(prov and prov[0] and prov[1]), "%s: %s / %s" % (f["file"], *(prov or ("", ""))),
                     "%s: the report names no provider and model" % f["file"])
    media = [p.name for p in out.iterdir() if p.suffix in (".png", ".gif", ".wav")]
    stray = sorted(set(media) - set(rows))
    c["5"].check(not stray, "every media file in the delivery folder (%d) has a report row" % len(media),
                 "media file(s) with no report row: %s" % stray)

    # 6. rule breaking requests declined with the reason
    if revision:
        c["6"].cannot("a revision regenerates only the named files; the declines stand in the original delivery's report")
        c["6"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])
        return
    for i, req in enumerate(brief, 1):
        txt = req["subject"].lower()
        expect = "celebrity" in txt or "pikachu" in txt
        if not expect:
            continue
        sec = note.split("## Request %d:" % i, 1)[1].split("\n## ", 1)[0] if ("## Request %d:" % i) in note else ""
        why = re.search(r"### Declined\n\n.*?\n\n- \*\*(.+?)\*\*: (.+)$", sec, re.S | re.M)
        c["6"].check(i in declined and bool(why), "request %d (%r) declined: %s: %s"
                     % (i, req["subject"], why.group(1) if why else "", (why.group(2) if why else "")[:90]),
                     "request %d (%r) was not declined with a reason in the report" % (i, req["subject"]))
    c["6"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
