#!/usr/bin/env python3
"""Pay-Per-Use Media Generator agent (issue #78).

Built ahead of any award for the NEAR Agent Market job "Pay-Per-Use Media
Generator" (job b33f7e41-b395-4534-9748-555e2327b761). One run takes a media
brief (JSON) and an output folder, and produces the requested media plus a
delivery note:

  1. Brief: type (image, video or voice), subject, style, format, count,
     aspect, length, script and voice for voice work, reference material,
     and the buyer's rights confirmation for that material. Reference based
     work is refused without the confirmation, before anything is generated.
  2. Routing: rules first (media type, format, aspect, length, count,
     reference following, voice), then quality from the recorded local test
     table (quality.json, written by the calibrate command). A provider that
     is not configured is never chosen, and the note says why.
  3. Brief check on every output: format, size or aspect, length, count,
     subject terms, obvious defects (blank image, frozen video, silent audio).
     A miss triggers one regeneration, with an adjusted prompt for missed
     subject terms or a different provider for format or defect misses. A
     second miss delivers the closest result with a plain note on what did not
     match and the exact rerun command.
  4. Delivery note (Markdown): brief parameters, routing decision, provider
     used, every attempt and its check results, and each file's SHA-256.

No live provider is called anywhere in this build. The offline stub
providers write labelled PLACEHOLDER media (valid PNG, GIF and WAV files),
and the delivery note says so on every stub output. Live provider slots are
interfaces only. Standard library only.

    python3 agents/media-generator/mediagen.py generate --brief brief.json --out DIR
    python3 agents/media-generator/mediagen.py calibrate --out agents/media-generator/quality.json

Exit 2 with the reason on stderr, and nothing written, for a bad brief, a
refused brief, or a run where no attempt produced any output.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import mediagen_providers as mp  # noqa: E402
from mediagen_providers import placeholder  # noqa: E402

AGENT_NAME = "Pay-Per-Use Media Generator"
AGENT_VERSION = "0.1.0"
QUALITY_PATH = os.path.join(HERE, "quality.json")

MEDIA_TYPES = ("image", "video", "voice")
DEFAULT_FORMAT = {"image": "png", "video": "gif", "voice": "wav"}
DEFAULT_ASPECT = {"image": "1:1", "video": "16:9"}
DEFAULT_VIDEO_SECONDS = 5
WORDS_PER_SECOND = 2.5          # stated assumption for a voice length when the brief gives none
LENGTH_TOLERANCE = 0.10         # an output may be up to 10 percent off the requested length
ASPECT_TOLERANCE = 0.05
MIN_VOICE_PEAK = 500            # 16 bit peak below this is treated as silence
STOPWORDS = frozenset("a an and the of in on at to with for from by or as is are be this that it its into over under".split())
BRIEF_FIELDS = ("type", "subject", "style", "format", "count", "aspect", "length_seconds", "script", "voice",
                "references", "rights_confirmed")


class BriefError(ValueError):
    """The brief is not usable as given. Nothing is generated."""


class Refused(Exception):
    """The brief is refused by rule. Nothing is generated."""


# ----------------------------------------------------------------------
# the brief
# ----------------------------------------------------------------------

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "media")[:40]


def subject_terms(subject):
    words = re.findall(r"[a-z0-9]+", subject.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


class Job(object):
    """A checked brief, ready to route."""

    def __init__(self, data):
        if not isinstance(data, dict):
            raise BriefError("the brief must be a JSON object")
        unknown = sorted(set(data) - set(BRIEF_FIELDS))
        if unknown:
            raise BriefError("unknown brief field(s): %s (known: %s)" % (", ".join(unknown), ", ".join(BRIEF_FIELDS)))
        self.type = data.get("type")
        if self.type not in MEDIA_TYPES:
            raise BriefError("type must be one of %s, got %r" % (", ".join(MEDIA_TYPES), self.type))
        self.subject = (data.get("subject") or "").strip()
        if not self.subject or not isinstance(data.get("subject"), str):
            raise BriefError("subject must be a non blank string")
        self.terms = subject_terms(self.subject)
        if not self.terms:
            raise BriefError("subject %r has no content words to check against" % self.subject)
        self.style = (data.get("style") or "").strip()
        self.format = (data.get("format") or DEFAULT_FORMAT[self.type]).lower()
        count = data.get("count", 1)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise BriefError("count must be a positive integer, got %r" % (count,))
        self.count = count
        self.aspect = None
        if self.type in ("image", "video"):
            self.aspect = data.get("aspect") or DEFAULT_ASPECT[self.type]
            if not re.match(r"^\d+:\d+$", str(self.aspect)):
                raise BriefError("aspect must look like 16:9, got %r" % (self.aspect,))
        elif data.get("aspect"):
            raise BriefError("aspect applies to image and video briefs")
        self.script = (data.get("script") or "").strip()
        self.voice = (data.get("voice") or "").strip() or None
        self.length_assumed = False
        self.seconds = None
        raw_len = data.get("length_seconds")
        if raw_len is not None and (isinstance(raw_len, bool) or not isinstance(raw_len, (int, float)) or raw_len <= 0):
            raise BriefError("length_seconds must be a positive number, got %r" % (raw_len,))
        if self.type == "image":
            if raw_len is not None:
                raise BriefError("length_seconds applies to video and voice briefs")
        elif self.type == "video":
            self.seconds = float(raw_len) if raw_len is not None else float(DEFAULT_VIDEO_SECONDS)
            self.length_assumed = raw_len is None
        else:
            if not self.script:
                raise BriefError("a voice brief needs a script to speak")
            if raw_len is not None:
                self.seconds = float(raw_len)
            else:
                words = len(self.script.split())
                self.seconds = max(1.0, round(words / WORDS_PER_SECOND, 1))
                self.length_assumed = True
        if self.type != "voice" and (self.script or self.voice):
            raise BriefError("script and voice apply to voice briefs")
        refs = data.get("references") or []
        if not isinstance(refs, list) or not all(isinstance(r, str) and r.strip() for r in refs):
            raise BriefError("references must be a list of non blank strings (file paths or links)")
        self.references = [r.strip() for r in refs]
        rights = data.get("rights_confirmed", False)
        if not isinstance(rights, bool):
            raise BriefError("rights_confirmed must be true or false")
        self.rights_confirmed = rights
        self.slug = slugify(self.subject)
        self.base_prompt = self.subject + (", %s" % self.style if self.style else "")
        if self.type == "voice":
            self.base_prompt = "%s: %s" % (self.subject, self.script)
        self.prompt = self.base_prompt
        self.raw = dict(data)

    def check_rights(self):
        """The rights rule: reference based work only with the buyer's confirmation."""
        if self.references and not self.rights_confirmed:
            raise Refused("the brief includes %d reference item(s) but rights_confirmed is not true: reference based "
                          "work needs the buyer's confirmation that they hold the rights to use that material. Nothing "
                          "was generated. Resubmit with rights_confirmed true, or without references."
                          % len(self.references))


def load_brief(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        raise BriefError("cannot read brief %s: %s" % (path, exc))
    except ValueError as exc:
        raise BriefError("brief %s is not valid JSON: %s" % (path, exc))
    return Job(data)


# ----------------------------------------------------------------------
# routing
# ----------------------------------------------------------------------

def load_quality(path=QUALITY_PATH):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError:
        return {"providers": {}, "source": "no quality table at %s" % path}
    except ValueError as exc:
        raise BriefError("quality table %s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict) or not isinstance(data.get("providers"), dict):
        raise BriefError("quality table %s needs a \"providers\" object" % path)
    return data


def rule_misses(provider, job):
    """Why a provider cannot take this job by the rules; empty when it can."""
    cap = provider.capabilities
    misses = []
    if provider.media_type != job.type:
        misses.append("makes %s, not %s" % (provider.media_type, job.type))
        return misses
    if job.format not in cap.formats:
        misses.append("format %s not offered (%s)" % (job.format, ", ".join(cap.formats)))
    if job.aspect and job.aspect not in cap.aspects:
        misses.append("aspect %s not offered" % job.aspect)
    if job.seconds is not None and cap.max_seconds is not None and job.seconds > cap.max_seconds:
        misses.append("length %.1fs is over its %ss limit" % (job.seconds, cap.max_seconds))
    if job.count > cap.max_count:
        misses.append("count %d is over its %d per call limit" % (job.count, cap.max_count))
    if job.references and not cap.follows_references:
        misses.append("does not follow reference material")
    if job.voice and job.voice not in cap.voices:
        misses.append("voice %r not offered (%s)" % (job.voice, ", ".join(cap.voices) or "none listed"))
    return misses


def route(job, providers, quality, env):
    """Rules first, then quality. Returns (ranked providers, decisions) where
    decisions is a list of (provider name, outcome text) for the note."""
    decisions, eligible = [], []
    table = quality.get("providers", {})
    for prov in providers:
        if prov.media_type != job.type:
            continue
        misses = rule_misses(prov, job)
        if misses:
            decisions.append((prov.name, "excluded by rules: " + "; ".join(misses)))
            continue
        ok, why = prov.configured(env)
        if not ok:
            decisions.append((prov.name, "excluded: not configured (%s)" % why))
            continue
        record = table.get(prov.name)
        if record is None:
            decisions.append((prov.name, "eligible; no recorded quality (ranked as 0)"))
            eligible.append((0.0, prov))
        else:
            decisions.append((prov.name, "eligible; recorded pass rate %.2f over %d calibration brief(s), %s"
                              % (record["pass_rate"], record["briefs"], record["recorded_utc"])))
            eligible.append((float(record["pass_rate"]), prov))
    eligible.sort(key=lambda item: (-item[0], item[1].name))
    return [p for _, p in eligible], decisions


# ----------------------------------------------------------------------
# the brief check
# ----------------------------------------------------------------------

def aspect_ratio(aspect):
    a, b = aspect.split(":")
    return float(a) / float(b)


def check_output(job, output):
    """A list of plain misses for one output; empty when it matches the brief.

    It reads the file itself (format, size, length, defects) and the prompt the
    provider recorded in the file's metadata (subject terms). It cannot see
    what an image or video depicts: for a live provider a content check is
    needed before delivery (see README)."""
    misses = []
    path = output.path
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ["file is missing or empty"]
    recorded = ""
    try:
        if job.format == "png":
            width, height, texts, colours = placeholder.read_png(path)
            recorded = texts.get("Description", "")
            if abs(width / float(height) - aspect_ratio(job.aspect)) > ASPECT_TOLERANCE * aspect_ratio(job.aspect):
                misses.append("aspect is %dx%d, not %s" % (width, height, job.aspect))
            if colours < 2:
                misses.append("image is blank (one colour)")
        elif job.format == "gif":
            width, height, frames, seconds, recorded = placeholder.read_gif(path)
            if abs(width / float(height) - aspect_ratio(job.aspect)) > ASPECT_TOLERANCE * aspect_ratio(job.aspect):
                misses.append("aspect is %dx%d, not %s" % (width, height, job.aspect))
            if abs(seconds - job.seconds) > LENGTH_TOLERANCE * job.seconds:
                misses.append("length is %.1fs, not %.1fs" % (seconds, job.seconds))
            if frames < 2:
                misses.append("video is a single frame")
        elif job.format == "wav":
            seconds, peak, recorded = placeholder.read_wav(path)
            if abs(seconds - job.seconds) > LENGTH_TOLERANCE * job.seconds:
                misses.append("length is %.1fs, not %.1fs" % (seconds, job.seconds))
            if peak < MIN_VOICE_PEAK:
                misses.append("audio is silent")
        else:
            misses.append("format %s has no reader in this build" % job.format)
    except ValueError as exc:
        return ["not a valid %s file: %s" % (job.format, exc)]
    missing = [t for t in job.terms if t not in set(re.findall(r"[a-z0-9]+", recorded.lower()))]
    if missing:
        misses.append("subject term(s) missing from what the provider recorded it made: %s" % ", ".join(missing))
    return misses


def check_attempt(job, outputs):
    """(per output misses, attempt level misses)."""
    per = [(o, check_output(job, o)) for o in outputs]
    overall = []
    if len(outputs) != job.count:
        overall.append("count is %d, not %d" % (len(outputs), job.count))
    return per, overall


def miss_total(per, overall):
    return len(overall) + sum(len(m) for _, m in per)


# ----------------------------------------------------------------------
# the run
# ----------------------------------------------------------------------

class Attempt(object):
    def __init__(self, number, provider, prompt, outputs, per, overall, error=None, why=""):
        self.number = number
        self.provider = provider
        self.prompt = prompt
        self.outputs = outputs
        self.per = per
        self.overall = overall
        self.error = error
        self.why = why

    @property
    def misses(self):
        if self.error:
            return 1 << 20
        return miss_total(self.per, self.overall)

    @property
    def passed(self):
        return self.error is None and self.misses == 0


def adjusted_prompt(job, per):
    """Name the missed subject terms explicitly for the regeneration."""
    missed = []
    for _, misses in per:
        for m in misses:
            if m.startswith("subject term(s) missing"):
                for t in m.split(": ", 1)[1].split(", "):
                    if t not in missed:
                        missed.append(t)
    if not missed:
        return job.base_prompt
    return "%s. Must clearly show: %s" % (job.base_prompt, ", ".join(missed))


def only_subject_misses(per, overall):
    if overall:
        return False
    return all(m.startswith("subject term(s) missing") for _, ms in per for m in ms)


def run(job, out_dir, providers=None, quality=None, env=None):
    """Generate, check, regenerate once, pick the result. Returns a dict for the
    note. Raises Refused, BriefError, or mp.ProviderError when nothing at all
    could be produced; in those cases out_dir is left untouched."""
    env = os.environ if env is None else env
    providers = mp.all_providers() if providers is None else providers
    quality = load_quality() if quality is None else quality
    job.check_rights()
    ranked, decisions = route(job, providers, quality, env)
    if not ranked:
        raise BriefError("no configured provider can take this brief: " +
                         "; ".join("%s %s" % (n, o) for n, o in decisions if o.startswith("excluded")))
    work = tempfile.mkdtemp(prefix="mediagen-")
    attempts = []
    try:
        first = ranked[0]
        job.prompt = job.base_prompt
        attempts.append(_attempt(1, first, job, work, "top ranked provider"))
        if not attempts[0].passed:
            a1 = attempts[0]
            if a1.error is None and only_subject_misses(a1.per, a1.overall):
                job.prompt = adjusted_prompt(job, a1.per)
                prov, why = first, "same provider, prompt adjusted to name the missed subject terms"
            elif len(ranked) > 1:
                job.prompt = adjusted_prompt(job, a1.per) if a1.error is None else job.base_prompt
                prov, why = ranked[1], "next ranked provider, because the first attempt's misses were not only subject terms"
            else:
                job.prompt = adjusted_prompt(job, a1.per) if a1.error is None else job.base_prompt
                prov, why = first, "same provider (no other eligible provider), prompt adjusted"
            attempts.append(_attempt(2, prov, job, work, why))
        usable = [a for a in attempts if a.error is None and a.outputs]
        if not usable:
            raise mp.ProviderError("no attempt produced any output: " + "; ".join(
                "attempt %d (%s): %s" % (a.number, a.provider.name, a.error) for a in attempts))
        chosen = min(usable, key=lambda a: (a.misses, -a.number))
        os.makedirs(out_dir, exist_ok=True)
        delivered = []
        for i, o in enumerate(chosen.outputs, start=1):
            target = os.path.join(out_dir, "%s-%d.%s" % (job.slug, i, o.format))
            shutil.copyfile(o.path, target)
            delivered.append((target, sha256_file(target), o))
        return {"job": job, "decisions": decisions, "ranked": ranked, "attempts": attempts, "chosen": chosen,
                "delivered": delivered, "quality": quality}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _attempt(number, provider, job, work, why):
    try:
        outputs = provider.generate(job, work, number)
    except mp.ProviderError as exc:
        return Attempt(number, provider, job.prompt, [], [], [], error=str(exc), why=why)
    per, overall = check_attempt(job, outputs)
    return Attempt(number, provider, job.prompt, outputs, per, overall, why=why)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------
# the delivery note
# ----------------------------------------------------------------------

def rerun_command(brief_path, out_dir):
    return "python3 agents/media-generator/mediagen.py generate --brief %s --out %s" % (
        shlex.quote(brief_path), shlex.quote(out_dir))


def render_note(result, brief_path, out_dir, now=None):
    job, chosen = result["job"], result["chosen"]
    now = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L = ["# %s: delivery note" % AGENT_NAME, ""]
    L.append("Produced by `agents/media-generator/mediagen.py` %s at %s (UTC)." % (AGENT_VERSION, now))
    L.append("")
    if any(o.placeholder for _, _, o in result["delivered"]):
        L.append("**Placeholder media.** The delivered files come from an offline stub provider: valid %s files "
                 "sized and timed as the brief asks, carrying the prompt in their metadata, but not generated "
                 "media. They are not a deliverable for a buyer." % job.format.upper())
        L.append("")
    L.append("## Brief")
    L.append("")
    for field in BRIEF_FIELDS:
        if field in job.raw:
            L.append("- %s: %s" % (field, json.dumps(job.raw[field], ensure_ascii=False)))
    L.append("- Format used: %s" % job.format)
    if job.aspect:
        L.append("- Aspect used: %s" % job.aspect)
    if job.seconds is not None:
        if job.length_assumed:
            basis = ("default for video" if job.type == "video"
                     else "assumed from the script at %.1f words per second" % WORDS_PER_SECOND)
        else:
            basis = "from the brief"
        L.append("- Length used: %.1f s (%s)" % (job.seconds, basis))
    L.append("- Subject terms checked: %s" % ", ".join(job.terms))
    if job.references:
        L.append("- Reference material: %d item(s); rights confirmed by the buyer: yes" % len(job.references))
    L.append("")
    L.append("## Routing")
    L.append("")
    L.append("Rules first (media type, format, aspect, length, count, reference following, voice), then the recorded "
             "pass rate from the local test table (%s)." % result["quality"].get("source", "quality.json"))
    L.append("")
    for name, outcome in result["decisions"]:
        L.append("- %s: %s" % (name, outcome))
    L.append("")
    L.append("Ranked: %s." % ", ".join(p.name for p in result["ranked"]))
    L.append("")
    L.append("## Attempts")
    L.append("")
    for a in result["attempts"]:
        L.append("### Attempt %d: %s (%s)" % (a.number, a.provider.name, a.why))
        L.append("")
        L.append("- Prompt: %s" % a.prompt)
        if a.error:
            L.append("- Provider error, no output: %s" % a.error)
        else:
            for o, misses in a.per:
                L.append("- `%s`: %s" % (os.path.basename(o.path), "matches the brief" if not misses else "; ".join(misses)))
            for m in a.overall:
                L.append("- Attempt: %s" % m)
        L.append("")
    if len(result["attempts"]) == 1:
        L.append("No regeneration was needed.")
    else:
        L.append("One regeneration was made, as the brief check allows.")
    L.append("")
    L.append("## Delivered")
    L.append("")
    L.append("From attempt %d, provider %s." % (chosen.number, chosen.provider.name))
    L.append("")
    for target, digest, o in result["delivered"]:
        L.append("- `%s`, SHA-256 `%s`%s" % (os.path.basename(target), digest, " (placeholder)" if o.placeholder else ""))
    L.append("")
    if not chosen.passed:
        L.append("**Did not fully match the brief.** Both attempts missed. This is the closest result (fewest "
                 "misses). What did not match:")
        L.append("")
        for o, misses in chosen.per:
            for m in misses:
                L.append("- `%s`: %s" % (os.path.basename(o.path), m))
        for m in chosen.overall:
            L.append("- %s" % m)
        L.append("")
        L.append("Rerun option, after adjusting the brief:")
        L.append("")
        L.append("```")
        L.append(rerun_command(brief_path, out_dir))
        L.append("```")
        L.append("")
    L.append("## What the check covers")
    L.append("")
    L.append("Format, size or aspect, length (within %d percent), count, obvious defects (blank image, single frame "
             "video, silent audio), and the subject terms in what the provider recorded it made. It does not look at "
             "what an image or video depicts." % int(LENGTH_TOLERANCE * 100))
    L.append("")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------
# calibration: the recorded local test table
# ----------------------------------------------------------------------

CALIBRATION_BRIEFS = [
    {"type": "image", "subject": "red fox in snow", "style": "watercolour", "count": 2, "aspect": "1:1"},
    {"type": "image", "subject": "city skyline at dusk", "count": 1, "aspect": "16:9"},
    {"type": "image", "subject": "portrait of a lighthouse", "count": 1, "aspect": "9:16"},
    {"type": "image", "subject": "product shot of a teapot", "count": 1, "aspect": "4:3",
     "references": ["buyer-sketch.png"], "rights_confirmed": True},
    {"type": "video", "subject": "waves on a beach", "count": 1, "aspect": "16:9", "length_seconds": 3},
    {"type": "video", "subject": "spinning globe", "count": 1, "aspect": "1:1", "length_seconds": 2},
    {"type": "voice", "subject": "welcome message", "script": "Welcome to the shop, we open at nine.", "count": 1},
    {"type": "voice", "subject": "safety notice", "script": "Please hold the handrail.", "voice": "stock-b",
     "length_seconds": 2},
]


def calibrate(providers=None, env=None, now=None):
    """Run the calibration briefs through every configured provider that the
    rules allow for each brief, and record each provider's pass rate."""
    env = os.environ if env is None else env
    providers = mp.all_providers() if providers is None else providers
    now = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = {}
    work = tempfile.mkdtemp(prefix="mediagen-cal-")
    try:
        for data in CALIBRATION_BRIEFS:
            job = Job(data)
            for prov in providers:
                if prov.media_type != job.type or rule_misses(prov, job) or not prov.configured(env)[0]:
                    continue
                rec = records.setdefault(prov.name, {"briefs": 0, "passed": 0})
                rec["briefs"] += 1
                attempt = _attempt(1, prov, job, work, "calibration")
                if attempt.passed:
                    rec["passed"] += 1
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for name, rec in records.items():
        rec["pass_rate"] = round(rec["passed"] / float(rec["briefs"]), 4)
        rec["recorded_utc"] = now
    return {"label": ("Recorded by `mediagen.py calibrate` from a local run of the calibration briefs in mediagen.py "
                      "against every provider configured at that time. In this build only the offline stub providers "
                      "are configured, so the table measures placeholder media against the brief check and says "
                      "nothing about any live provider."),
            "source": "quality.json recorded %s by mediagen.py calibrate" % now,
            "providers": dict(sorted(records.items()))}


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command")
    gen = sub.add_parser("generate", help="generate media for one brief and write the delivery note")
    gen.add_argument("--brief", required=True, help="brief JSON file")
    gen.add_argument("--out", required=True, help="output folder for the media and the delivery note")
    gen.add_argument("--quality", default=QUALITY_PATH, help="recorded quality table (default: quality.json here)")
    cal = sub.add_parser("calibrate", help="record the local quality table")
    cal.add_argument("--out", required=True, help="where to write the table")
    return parser


def main(argv=None, env=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "calibrate":
        table = calibrate(env=env)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(table, fh, indent=2)
            fh.write("\n")
        stderr.write("quality table written to %s\n" % args.out)
        return 0
    if args.command != "generate":
        parser.print_help(stderr)
        return 2
    try:
        job = load_brief(args.brief)
        result = run(job, args.out, quality=load_quality(args.quality), env=env)
    except Refused as exc:
        stderr.write("mediagen: refused: %s\n" % exc)
        return 2
    except (BriefError, mp.ProviderError) as exc:
        stderr.write("mediagen: %s\nnothing delivered\n" % exc)
        return 2
    note = render_note(result, args.brief, args.out)
    note_path = os.path.join(args.out, "delivery-note.md")
    with open(note_path, "w", encoding="utf-8") as fh:
        fh.write(note)
    stderr.write("delivered %d file(s) and %s\n" % (len(result["delivered"]), note_path))
    stdout.write(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
