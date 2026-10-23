#!/usr/bin/env python3
"""Pay-Per-Use Media Generator agent (issue #78).

Built ahead of any award for the NEAR Agent Market job "Pay-Per-Use Media
Generator" (job b33f7e41-b395-4534-9748-555e2327b761). The job description
and the bid proposal are quoted on issue #78 (comments 6366897388 and
6366897988). One run takes a brief file (one request, or several under
"requests") and an output folder, and produces the media plus a report:

  1. Brief: media type, subject, style, format, size or aspect, length,
     number of variations, reference material with the buyer's rights
     confirmation, a voiceover script and voice, and brand colours or fonts.
  2. Content rules, before anything is generated: real identifiable people
     without consent, copyrighted characters, logos and brands the buyer does
     not own, sexual content, graphic violence, deceptive content, and
     reference material without the rights confirmation. A request that
     breaks a rule is declined, and the report says why; the other requests
     in the same brief go ahead.
  3. Routing: rules first (media type, format, aspect or size, length, count,
     reference following, voice, recorded terms of use), then quality from the
     recorded local test table for that request type (quality.json, written by
     the calibrate command). A provider that is not configured is never chosen.
  4. Brief check on every file: format, exact size or aspect, length within one
     second, count, subject terms, word for word script, obvious defects. A miss
     triggers one regeneration (an adjusted prompt, or a different provider); a
     second miss delivers the closest result with a plain note on what did not
     match and the rerun command, never a silent substitution.
  5. Report (delivery-note.md) naming the provider and model of every file,
     and a manifest (delivery.json) that the revise command reads to change
     only the files a buyer names, keeping the rest byte for byte.

No live provider is called anywhere in this build. The offline stub providers
write labelled PLACEHOLDER media (valid PNG, GIF and WAV files), and the
report says so. Live provider slots are interfaces only. Standard library only.

    python3 agents/media-generator/mediagen.py generate --brief brief.json --out DIR
    python3 agents/media-generator/mediagen.py revise --from DIR --files NAME[,NAME] --out NEWDIR [--note TEXT]
    python3 agents/media-generator/mediagen.py calibrate --out agents/media-generator/quality.json

Exit 0 when at least one file was delivered, 3 when a report was written but
no file was delivered (every request declined or failed), 2 with nothing
written for an unreadable or invalid brief.
"""

import argparse
import copy
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
from mediagen_providers import placeholder, policy  # noqa: E402

AGENT_NAME = "Pay-Per-Use Media Generator"
AGENT_VERSION = "0.2.0"
QUALITY_PATH = os.path.join(HERE, "quality.json")
NOTE_NAME = "delivery-note.md"
MANIFEST_NAME = "delivery.json"

MEDIA_TYPES = ("image", "video", "voice")
DEFAULT_FORMAT = {"image": "png", "video": "gif", "voice": "wav"}
DEFAULT_ASPECT = {"image": "1:1", "video": "16:9"}
DEFAULT_VIDEO_SECONDS = 5
WORDS_PER_SECOND = 2.5          # stated assumption for a voiceover length when the brief gives none
LENGTH_TOLERANCE_SECONDS = 1.0  # job description, acceptance 2: within one second of the requested length
ASPECT_TOLERANCE = 0.05
MIN_VOICE_PEAK = 500            # 16 bit peak below this is treated as silence
MAX_REQUESTS = 20
STOPWORDS = frozenset("a an and the of in on at to with for from by or as is are be this that it its into over under "
                      "being some".split())
BRIEF_FIELDS = ("type", "subject", "style", "format", "count", "aspect", "size", "length_seconds", "script", "voice",
                "references", "rights_confirmed", "brand", "depicts_real_person", "person_consent", "brand_owned")


class BriefError(ValueError):
    """The brief is not usable as given. Nothing is generated."""


# ----------------------------------------------------------------------
# the brief
# ----------------------------------------------------------------------

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "media")[:40]


def words_of(text):
    return re.findall(r"[a-z0-9']+", (text or "").lower().replace("’", "'"))


def subject_terms(subject):
    return [w for w in words_of(subject) if w not in STOPWORDS and len(w) > 1 and "'" not in w]


def _bool(data, key):
    v = data.get(key, False)
    if not isinstance(v, bool):
        raise BriefError("%s must be true or false" % key)
    return v


class Job(object):
    """One checked request, ready to screen and route."""

    def __init__(self, data, index=1):
        if not isinstance(data, dict):
            raise BriefError("request %d: must be a JSON object" % index)
        self.index = index
        unknown = sorted(set(data) - set(BRIEF_FIELDS))
        if unknown:
            raise BriefError("unknown brief field(s): %s (known: %s)" % (", ".join(unknown), ", ".join(BRIEF_FIELDS)))
        self.type = data.get("type")
        if self.type not in MEDIA_TYPES:
            raise BriefError("type must be one of %s, got %r" % (", ".join(MEDIA_TYPES), self.type))
        if not isinstance(data.get("subject"), str) or not data["subject"].strip():
            raise BriefError("subject must be a non blank string")
        self.subject = data["subject"].strip()
        self.terms = subject_terms(self.subject)
        if not self.terms:
            raise BriefError("subject %r has no content words to check against" % self.subject)
        self.style = (data.get("style") or "").strip()
        self.brand = (data.get("brand") or "").strip()
        self.format = (data.get("format") or DEFAULT_FORMAT[self.type]).lower()
        count = data.get("count", 1)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise BriefError("count must be a positive integer, got %r" % (count,))
        self.count = count
        self.aspect, self.size = None, None
        if self.type in ("image", "video"):
            if data.get("size"):
                m = re.match(r"^(\d+)x(\d+)$", str(data["size"]))
                if not m or int(m.group(1)) < 2 or int(m.group(2)) < 2:
                    raise BriefError("size must look like 1024x1024, got %r" % (data["size"],))
                self.size = (int(m.group(1)), int(m.group(2)))
            self.aspect = data.get("aspect") or (None if self.size else DEFAULT_ASPECT[self.type])
            if self.aspect is not None and not re.match(r"^\d+:\d+$", str(self.aspect)):
                raise BriefError("aspect must look like 16:9, got %r" % (self.aspect,))
            if self.size and self.aspect and abs(self.size[0] / float(self.size[1]) - aspect_ratio(self.aspect)) > \
                    ASPECT_TOLERANCE * aspect_ratio(self.aspect):
                raise BriefError("size %dx%d does not have the aspect %s" % (self.size[0], self.size[1], self.aspect))
        elif data.get("aspect") or data.get("size"):
            raise BriefError("aspect and size apply to image and video briefs")
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
                raise BriefError("a voice brief needs a script to read")
            if raw_len is not None:
                self.seconds = float(raw_len)
            else:
                self.seconds = max(1.0, round(len(self.script.split()) / WORDS_PER_SECOND, 1))
                self.length_assumed = True
        if self.type != "voice" and (self.script or self.voice):
            raise BriefError("script and voice apply to voice briefs")
        refs = data.get("references") or []
        if not isinstance(refs, list) or not all(isinstance(r, str) and r.strip() for r in refs):
            raise BriefError("references must be a list of non blank strings (file paths or links)")
        self.references = [r.strip() for r in refs]
        self.rights_confirmed = _bool(data, "rights_confirmed")
        self.depicts_real_person = _bool(data, "depicts_real_person")
        self.person_consent = _bool(data, "person_consent")
        self.brand_owned = _bool(data, "brand_owned")
        self.slug = slugify(self.subject)
        self.kind = self.type + ("+refs" if self.references else "")
        prompt = self.subject + (", %s" % self.style if self.style else "") + (", brand: %s" % self.brand if self.brand else "")
        self.base_prompt = prompt
        self.prompt = prompt
        self.seed = 0
        self.raw = dict(data)


def aspect_ratio(aspect):
    a, b = aspect.split(":")
    return float(a) / float(b)


def parse_brief(data):
    """A brief is one request object, or {"requests": [object, ...]}."""
    if isinstance(data, dict) and "requests" in data:
        if set(data) != {"requests"}:
            raise BriefError("a multi request brief holds only \"requests\"")
        reqs = data["requests"]
        if not isinstance(reqs, list) or not reqs:
            raise BriefError("requests must be a non empty list")
        if len(reqs) > MAX_REQUESTS:
            raise BriefError("at most %d requests per brief" % MAX_REQUESTS)
        jobs = []
        for i, r in enumerate(reqs, start=1):
            try:
                jobs.append(Job(r, i))
            except BriefError as exc:
                raise BriefError("request %d: %s" % (i, exc))
        return jobs
    return [Job(data, 1)]


def load_brief(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        raise BriefError("cannot read brief %s: %s" % (path, exc))
    except ValueError as exc:
        raise BriefError("brief %s is not valid JSON: %s" % (path, exc))
    return parse_brief(data)


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
    """Why a provider cannot take this request by the rules; empty when it can."""
    cap = provider.capabilities
    if provider.media_type != job.type:
        return ["makes %s, not %s" % (provider.media_type, job.type)]
    misses = []
    if job.format not in cap.formats:
        misses.append("format %s not offered (%s)" % (job.format, ", ".join(cap.formats)))
    if job.size:
        if cap.max_side is not None and max(job.size) > cap.max_side:
            misses.append("size %dx%d is over its %d px limit" % (job.size[0], job.size[1], cap.max_side))
    elif job.aspect and job.aspect not in cap.aspects:
        misses.append("aspect %s not offered" % job.aspect)
    if job.seconds is not None and cap.max_seconds is not None and job.seconds > cap.max_seconds:
        misses.append("length %.1fs is over its %ss limit" % (job.seconds, cap.max_seconds))
    if job.count > cap.max_count:
        misses.append("count %d is over its %d per call limit" % (job.count, cap.max_count))
    if job.references and not cap.follows_references:
        misses.append("does not follow reference material")
    if job.voice and job.voice not in cap.voices:
        misses.append("voice %r not offered (%s)" % (job.voice, ", ".join(cap.voices) or "none listed"))
    if cap.commercial_use is False:
        misses.append("its terms as recorded do not allow commercial use and resale of the output")
    return misses


def route(job, providers, quality, env):
    """Rules first, then the recorded pass rate for this request type.
    Returns (ranked providers, [(provider name, outcome text)])."""
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
        record = (table.get(prov.name) or {}).get(job.kind)
        if record is None:
            decisions.append((prov.name, "eligible; no recorded quality for %s requests (ranked as 0)" % job.kind))
            eligible.append((0.0, prov))
        else:
            decisions.append((prov.name, "eligible; recorded pass rate %.2f over %d %s calibration brief(s), %s"
                              % (record["pass_rate"], record["briefs"], job.kind, record["recorded_utc"])))
            eligible.append((float(record["pass_rate"]), prov))
    eligible.sort(key=lambda item: (-item[0], item[1].name))
    return [p for _, p in eligible], decisions


# ----------------------------------------------------------------------
# the brief check
# ----------------------------------------------------------------------

def _size_misses(job, width, height):
    if job.size:
        if (width, height) != job.size:
            return ["size is %dx%d, not %dx%d" % (width, height, job.size[0], job.size[1])]
        return []
    if abs(width / float(height) - aspect_ratio(job.aspect)) > ASPECT_TOLERANCE * aspect_ratio(job.aspect):
        return ["aspect is %dx%d, not %s" % (width, height, job.aspect)]
    return []


def _length_misses(job, seconds):
    if abs(seconds - job.seconds) > LENGTH_TOLERANCE_SECONDS + 1e-9:
        return ["length is %.1fs, not within %.0f s of %.1fs" % (seconds, LENGTH_TOLERANCE_SECONDS, job.seconds)]
    return []


def recorded_script(comment):
    m = re.search(r"script: (.*?) \| tiny-ledger", comment)
    return m.group(1) if m else ""


def check_output(job, output):
    """Plain misses for one file; empty when it matches the brief.

    It reads the file itself (format, size, length, defects) and what the
    provider recorded in the file's metadata (subject terms, the script read).
    It cannot see what an image or video depicts, or hear what a voice says:
    for a live provider a content check and a transcript check are needed
    before delivery (see README)."""
    path = output.path
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ["file is missing or empty"]
    misses, recorded = [], ""
    try:
        if job.format == "png":
            width, height, texts, colours = placeholder.read_png(path)
            recorded = texts.get("Description", "")
            misses += _size_misses(job, width, height)
            if colours < 2:
                misses.append("image is blank (one colour)")
        elif job.format == "gif":
            width, height, frames, seconds, recorded = placeholder.read_gif(path)
            misses += _size_misses(job, width, height)
            misses += _length_misses(job, seconds)
            if frames < 2:
                misses.append("video is a single frame")
        elif job.format == "wav":
            seconds, peak, recorded = placeholder.read_wav(path)
            misses += _length_misses(job, seconds)
            if peak < MIN_VOICE_PEAK:
                misses.append("audio is silent")
            said = words_of(recorded_script(recorded))
            wanted = words_of(job.script)
            if said != wanted:
                misses.append("script not read word for word (recorded %d word(s), script has %d)" % (len(said), len(wanted)))
        else:
            misses.append("format %s has no reader in this build" % job.format)
    except ValueError as exc:
        return ["not a valid %s file: %s" % (job.format, exc)]
    have = set(words_of(recorded))
    missing = [t for t in job.terms if t not in have]
    if missing:
        misses.append("subject term(s) missing from what the provider recorded it made: %s" % ", ".join(missing))
    return misses


def check_attempt(job, outputs):
    per = [(o, check_output(job, o)) for o in outputs]
    overall = ["count is %d, not %d" % (len(outputs), job.count)] if len(outputs) != job.count else []
    return per, overall


# ----------------------------------------------------------------------
# generating one request
# ----------------------------------------------------------------------

class Attempt(object):
    def __init__(self, number, provider, prompt, outputs, per, overall, error=None, why=""):
        self.number, self.provider, self.prompt = number, provider, prompt
        self.outputs, self.per, self.overall = outputs, per, overall
        self.error, self.why = error, why

    @property
    def misses(self):
        if self.error:
            return 1 << 20
        return len(self.overall) + sum(len(m) for _, m in self.per)

    @property
    def passed(self):
        return self.error is None and self.misses == 0


def adjusted_prompt(job, per):
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
    return not overall and all(m.startswith("subject term(s) missing") for _, ms in per for m in ms)


def _attempt(number, provider, job, work, why):
    try:
        outputs = provider.generate(job, work, number)
    except mp.ProviderError as exc:
        return Attempt(number, provider, job.prompt, [], [], [], error=str(exc), why=why)
    per, overall = check_attempt(job, outputs)
    return Attempt(number, provider, job.prompt, outputs, per, overall, why=why)


class RequestResult(object):
    def __init__(self, job):
        self.job = job
        self.declined = []      # [(rule, reason)]
        self.decisions = []
        self.ranked = []
        self.attempts = []
        self.chosen = None
        self.failure = None     # text when no attempt produced output or no provider fits
        self.files = []         # [(name, sha256, Output)]


def generate_request(job, work, providers, quality, env):
    """Screen, route, generate, check, regenerate once. Files stay in work."""
    res = RequestResult(job)
    res.declined = policy.screen(job)
    if res.declined:
        return res
    res.ranked, res.decisions = route(job, providers, quality, env)
    if not res.ranked:
        res.failure = "no configured provider can take this request"
        return res
    first = res.ranked[0]
    job.prompt = job.base_prompt
    res.attempts.append(_attempt(1, first, job, work, "top ranked provider"))
    a1 = res.attempts[0]
    if not a1.passed:
        if a1.error is None and only_subject_misses(a1.per, a1.overall):
            job.prompt, prov, why = adjusted_prompt(job, a1.per), first, "same provider, prompt adjusted to name the missed subject terms"
        elif len(res.ranked) > 1:
            job.prompt = adjusted_prompt(job, a1.per) if a1.error is None else job.base_prompt
            prov, why = res.ranked[1], "next ranked provider, because the first attempt's misses were not only subject terms"
        else:
            job.prompt = adjusted_prompt(job, a1.per) if a1.error is None else job.base_prompt
            prov, why = first, "same provider (no other eligible provider), prompt adjusted"
        res.attempts.append(_attempt(2, prov, job, work, why))
    usable = [a for a in res.attempts if a.error is None and a.outputs]
    if not usable:
        res.failure = "no attempt produced any output: " + "; ".join(
            "attempt %d (%s): %s" % (a.number, a.provider.name, a.error) for a in res.attempts)
        return res
    res.chosen = min(usable, key=lambda a: (a.misses, -a.number))
    return res


def file_name(job, position, fmt, multi):
    prefix = "r%d-" % job.index if multi else ""
    return "%s%s-%d.%s" % (prefix, job.slug, position, fmt)


def run(jobs, out_dir, providers=None, quality=None, env=None):
    """Run every request; copy the chosen files into out_dir. Returns the
    list of RequestResult. out_dir is created only here, after generation."""
    env = os.environ if env is None else env
    providers = mp.all_providers() if providers is None else providers
    quality = load_quality() if quality is None else quality
    work = tempfile.mkdtemp(prefix="mediagen-")
    multi = len(jobs) > 1
    try:
        results = [generate_request(j, work, providers, quality, env) for j in jobs]
        os.makedirs(out_dir, exist_ok=True)
        for res in results:
            if res.chosen is None:
                continue
            for pos, o in enumerate(res.chosen.outputs, start=1):
                name = file_name(res.job, pos, o.format, multi)
                target = os.path.join(out_dir, name)
                shutil.copyfile(o.path, target)
                res.files.append((name, sha256_file(target), o))
        return results
    finally:
        shutil.rmtree(work, ignore_errors=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------
# manifest, report
# ----------------------------------------------------------------------

def manifest(results, quality, now):
    files, requests = [], []
    for res in results:
        requests.append({"index": res.job.index, "brief": res.job.raw, "seed": res.job.seed,
                         "declined": [{"rule": r, "reason": why} for r, why in res.declined],
                         "failure": res.failure})
        for pos, (name, digest, o) in enumerate(res.files, start=1):
            files.append({"file": name, "request": res.job.index, "position": pos, "provider": o.provider,
                          "model": o.model, "attempt": res.chosen.number, "sha256": digest,
                          "placeholder": o.placeholder,
                          "matches_brief": not dict((id(x), m) for x, m in res.chosen.per).get(id(o))})
    return {"agent": "%s %s" % (AGENT_NAME, AGENT_VERSION), "written_utc": now,
            "quality_table": quality.get("source", ""), "requests": requests, "files": files}


def rerun_command(brief_path, out_dir):
    return "python3 agents/media-generator/mediagen.py generate --brief %s --out %s" % (
        shlex.quote(brief_path), shlex.quote(out_dir))


def revise_command(out_dir, names):
    return "python3 agents/media-generator/mediagen.py revise --from %s --files %s --out %s" % (
        shlex.quote(out_dir), shlex.quote(",".join(names)), shlex.quote(out_dir.rstrip("/") + "-revised"))


def render_request(res, brief_path, out_dir):
    job = res.job
    L = ["## Request %d: %s %s" % (job.index, job.type, json.dumps(job.subject)), ""]
    L.append("### Brief")
    L.append("")
    for field in BRIEF_FIELDS:
        if field in job.raw:
            L.append("- %s: %s" % (field, json.dumps(job.raw[field], ensure_ascii=False)))
    L.append("- Format used: %s" % job.format)
    if job.size:
        L.append("- Size used: %dx%d" % job.size)
    elif job.aspect:
        L.append("- Aspect used: %s" % job.aspect)
    if job.seconds is not None:
        basis = ("from the brief" if not job.length_assumed else
                 "default for video" if job.type == "video" else
                 "assumed from the script at %.1f words per second" % WORDS_PER_SECOND)
        L.append("- Length used: %.1f s (%s), checked to within %.0f s" % (job.seconds, basis, LENGTH_TOLERANCE_SECONDS))
    L.append("- Subject terms checked: %s" % ", ".join(job.terms))
    L.append("")
    if res.declined:
        L.append("### Declined")
        L.append("")
        L.append("Nothing was generated for this request. It breaks the job's content rules:")
        L.append("")
        for rule, why in res.declined:
            L.append("- **%s**: %s." % (rule, why))
        L.append("")
        return L
    L.append("### Routing")
    L.append("")
    for name, outcome in res.decisions:
        L.append("- %s: %s" % (name, outcome))
    if res.ranked:
        L.append("")
        L.append("Ranked: %s." % ", ".join(p.name for p in res.ranked))
    L.append("")
    if res.attempts:
        L.append("### Attempts")
        L.append("")
        for a in res.attempts:
            L.append("- Attempt %d, %s (%s). Prompt: %s" % (a.number, a.provider.name, a.why, a.prompt))
            if a.error:
                L.append("  - provider error, no output: %s" % a.error)
            for o, misses in a.per:
                L.append("  - `%s`: %s" % (os.path.basename(o.path), "matches the brief" if not misses else "; ".join(misses)))
            for m in a.overall:
                L.append("  - %s" % m)
        L.append("")
        L.append("No regeneration was needed." if len(res.attempts) == 1 else "One regeneration was made.")
        L.append("")
    if res.failure:
        L.append("### Not delivered")
        L.append("")
        L.append("No file is delivered for this request: %s." % res.failure)
        L.append("")
        return L
    L.append("### Delivered")
    L.append("")
    L.append("| File | Provider | Model | Attempt | SHA-256 |")
    L.append("| --- | --- | --- | --- | --- |")
    for name, digest, o in res.files:
        L.append("| `%s` | %s | %s | %d | `%s` |" % (name, o.provider, o.model, res.chosen.number, digest))
    L.append("")
    if any(o.placeholder for _, _, o in res.files):
        L.append("These files are **placeholders** from an offline stub provider, not generated media.")
        L.append("")
    if not res.chosen.passed:
        names = [n for n, _, _ in res.files]
        L.append("**Did not fully match the brief.** Both attempts missed; this is the closest result (fewest "
                 "misses), not a substitute. What did not match:")
        L.append("")
        by_out = dict((id(o), m) for o, m in res.chosen.per)
        for name, _, o in res.files:
            for m in by_out.get(id(o), []):
                L.append("- `%s`: %s" % (name, m))
        for m in res.chosen.overall:
            L.append("- %s" % m)
        L.append("")
        L.append("Rerun options: change the brief and run again, or regenerate only these files:")
        L.append("")
        L.append("```")
        L.append(rerun_command(brief_path, out_dir))
        L.append(revise_command(out_dir, names))
        L.append("```")
        L.append("")
    return L


def render_note(results, brief_path, out_dir, quality, now):
    delivered = sum(len(r.files) for r in results)
    L = ["# %s: delivery report" % AGENT_NAME, ""]
    L.append("Produced by `agents/media-generator/mediagen.py` %s at %s (UTC). %d request(s), %d file(s) delivered, "
             "%d request(s) declined." % (AGENT_VERSION, now, len(results), delivered, sum(1 for r in results if r.declined)))
    L.append("")
    if any(o.placeholder for r in results for _, _, o in r.files):
        L.append("**Placeholder media.** Files from an offline stub provider are valid files sized and timed as the "
                 "brief asks, carrying the prompt in their metadata, but not generated media and not a deliverable "
                 "for a buyer.")
        L.append("")
    L.append("Routing: rules first (media type, format, size or aspect, length, count, reference following, voice, "
             "recorded terms of use), then the recorded pass rate for the request type (%s)."
             % quality.get("source", "quality.json"))
    L.append("")
    for res in results:
        L.extend(render_request(res, brief_path, out_dir))
    L.append("## What the check covers")
    L.append("")
    L.append("Format, exact size or aspect (within %d percent), video and voice length within %.0f s, count, obvious "
             "defects (blank image, single frame video, silent audio), the subject terms in what the provider recorded "
             "it made, and the voiceover script word for word against what the provider recorded it read. It does not "
             "look at what an image or video depicts or listen to what a voice says."
             % (int(ASPECT_TOLERANCE * 100), LENGTH_TOLERANCE_SECONDS))
    L.append("")
    return "\n".join(L) + "\n"


def write_outputs(results, brief_path, out_dir, quality):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = render_note(results, brief_path, out_dir, quality, now)
    with open(os.path.join(out_dir, NOTE_NAME), "w", encoding="utf-8") as fh:
        fh.write(note)
    with open(os.path.join(out_dir, MANIFEST_NAME), "w", encoding="utf-8") as fh:
        json.dump(manifest(results, quality, now), fh, indent=2)
        fh.write("\n")
    return note


# ----------------------------------------------------------------------
# revise: change only the named files
# ----------------------------------------------------------------------

def revise(from_dir, names, out_dir, note_text="", providers=None, quality=None, env=None):
    """Regenerate only the named files of an earlier delivery into out_dir;
    copy every other file byte for byte. Returns (changed, kept, results)."""
    env = os.environ if env is None else env
    providers = mp.all_providers() if providers is None else providers
    quality = load_quality() if quality is None else quality
    try:
        with open(os.path.join(from_dir, MANIFEST_NAME), "r", encoding="utf-8") as fh:
            man = json.load(fh)
    except (OSError, ValueError) as exc:
        raise BriefError("cannot read %s in %s: %s" % (MANIFEST_NAME, from_dir, exc))
    by_name = {f["file"]: f for f in man.get("files", [])}
    unknown = [n for n in names if n not in by_name]
    if unknown:
        raise BriefError("not in the earlier delivery: %s (delivered: %s)" % (", ".join(unknown), ", ".join(sorted(by_name))))
    if os.path.abspath(out_dir) == os.path.abspath(from_dir):
        raise BriefError("revise writes to a new folder; --out must differ from --from")
    requests = {r["index"]: r for r in man["requests"]}
    for name, entry in by_name.items():
        if sha256_file(os.path.join(from_dir, name)) != entry["sha256"]:
            raise BriefError("%s no longer matches its recorded SHA-256; refusing to build on a changed delivery" % name)
    work = tempfile.mkdtemp(prefix="mediagen-rev-")
    changed, results = [], []
    try:
        regenerated = {}
        for name in names:
            entry = by_name[name]
            req = requests[entry["request"]]
            job = Job(dict(req["brief"], count=1), entry["request"])
            job.seed = int(req.get("seed", 0)) + 1000 * (1 + len(results)) + entry["position"]
            if note_text:
                job.base_prompt = "%s. Revision: %s" % (job.base_prompt, note_text)
            res = generate_request(job, work, providers, quality, env)
            results.append((name, res))
            if res.chosen is None:
                raise mp.ProviderError("revision of %s produced no output: %s" % (name, res.failure or res.declined))
            regenerated[name] = res.chosen.outputs[0]
        os.makedirs(out_dir, exist_ok=True)
        kept = []
        for name, entry in sorted(by_name.items()):
            target = os.path.join(out_dir, name)
            if name in regenerated:
                shutil.copyfile(regenerated[name].path, target)
                changed.append((name, entry["sha256"], sha256_file(target), regenerated[name]))
            else:
                shutil.copyfile(os.path.join(from_dir, name), target)
                kept.append((name, sha256_file(target)))
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new_files = []
        for f in man["files"]:
            g = dict(f)
            for name, old, new, o in changed:
                if name == f["file"]:
                    g.update({"sha256": new, "provider": o.provider, "model": o.model, "revised_from": old})
            new_files.append(g)
        man2 = dict(man, files=new_files, written_utc=now, revision_of=os.path.abspath(from_dir))
        with open(os.path.join(out_dir, MANIFEST_NAME), "w", encoding="utf-8") as fh:
            json.dump(man2, fh, indent=2)
            fh.write("\n")
        L = ["# %s: revision report" % AGENT_NAME, ""]
        L.append("Produced at %s (UTC) from the delivery in `%s`. Only the files named in the change request were "
                 "regenerated; every other file is copied byte for byte." % (now, from_dir))
        if note_text:
            L.append("")
            L.append("Change request: %s" % note_text)
        L.append("")
        L.append("| File | Status | Provider | Model | SHA-256 |")
        L.append("| --- | --- | --- | --- | --- |")
        for name, old, new, o in changed:
            L.append("| `%s` | changed (was `%s`) | %s | %s | `%s` |" % (name, old, o.provider, o.model, new))
        kept_entries = {f["file"]: f for f in man["files"]}
        for name, digest in kept:
            L.append("| `%s` | kept as delivered | %s | %s | `%s` |" % (name, kept_entries[name]["provider"],
                                                                       kept_entries[name]["model"], digest))
        L.append("")
        with open(os.path.join(out_dir, NOTE_NAME), "w", encoding="utf-8") as fh:
            fh.write("\n".join(L) + "\n")
        return changed, kept, results
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ----------------------------------------------------------------------
# calibration: the recorded local test table, per request type
# ----------------------------------------------------------------------

CALIBRATION_BRIEFS = [
    {"type": "image", "subject": "ceramic mug on a wooden table", "count": 3, "aspect": "1:1"},
    {"type": "image", "subject": "city skyline at dusk", "count": 1, "aspect": "16:9"},
    {"type": "image", "subject": "portrait of a lighthouse", "count": 1, "aspect": "9:16"},
    {"type": "image", "subject": "product shot of a teapot", "count": 1, "size": "80x60"},
    {"type": "image", "subject": "teapot in the buyer's sketch style", "count": 1, "aspect": "4:3",
     "references": ["buyer-sketch.png"], "rights_confirmed": True},
    {"type": "video", "subject": "coffee being poured into a cup", "count": 1, "aspect": "9:16", "length_seconds": 8},
    {"type": "video", "subject": "spinning globe", "count": 1, "aspect": "1:1", "length_seconds": 2},
    {"type": "voice", "subject": "shop welcome", "script": "Welcome to the shop, we open at nine.", "count": 1},
    {"type": "voice", "subject": "safety notice", "script": "Please hold the handrail.", "voice": "stock-calm-male",
     "length_seconds": 2},
]


def calibrate(providers=None, env=None, now=None):
    """Run the calibration briefs through every configured provider the rules
    allow and record each provider's pass rate per request type."""
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
                rec = records.setdefault(prov.name, {}).setdefault(job.kind, {"briefs": 0, "passed": 0})
                rec["briefs"] += 1
                if _attempt(1, prov, job, work, "calibration").passed:
                    rec["passed"] += 1
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for kinds in records.values():
        for rec in kinds.values():
            rec["pass_rate"] = round(rec["passed"] / float(rec["briefs"]), 4)
            rec["recorded_utc"] = now
    return {"label": ("Recorded by `mediagen.py calibrate` from a local run of the calibration briefs in mediagen.py "
                      "against every provider configured at that time, per request type. In this build only the "
                      "offline stub providers are configured, so the table measures placeholder media against the "
                      "brief check and says nothing about any live provider."),
            "source": "quality.json recorded %s by mediagen.py calibrate" % now,
            "providers": {k: dict(sorted(v.items())) for k, v in sorted(records.items())}}


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command")
    gen = sub.add_parser("generate", help="generate media for a brief and write the report")
    gen.add_argument("--brief", required=True, help="brief JSON file")
    gen.add_argument("--out", required=True, help="output folder for the media, the report and the manifest")
    gen.add_argument("--quality", default=QUALITY_PATH, help="recorded quality table (default: quality.json here)")
    rev = sub.add_parser("revise", help="regenerate only the named files of an earlier delivery")
    rev.add_argument("--from", dest="from_dir", required=True, help="the earlier delivery folder")
    rev.add_argument("--files", required=True, help="comma separated file names to change")
    rev.add_argument("--out", required=True, help="new folder for the revised delivery")
    rev.add_argument("--note", default="", help="what to change, appended to the prompt")
    rev.add_argument("--quality", default=QUALITY_PATH)
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
    if args.command == "revise":
        names = [n.strip() for n in args.files.split(",") if n.strip()]
        try:
            changed, kept, _ = revise(args.from_dir, names, args.out, args.note, quality=load_quality(args.quality), env=env)
        except (BriefError, mp.ProviderError) as exc:
            stderr.write("mediagen: %s\nnothing revised\n" % exc)
            return 2
        stderr.write("changed %d file(s), kept %d, in %s\n" % (len(changed), len(kept), args.out))
        return 0
    if args.command != "generate":
        parser.print_help(stderr)
        return 2
    try:
        jobs = load_brief(args.brief)
        quality = load_quality(args.quality)
    except BriefError as exc:
        stderr.write("mediagen: %s\nnothing written\n" % exc)
        return 2
    results = run(jobs, args.out, quality=quality, env=env)
    note = write_outputs(results, args.brief, args.out, quality)
    stdout.write(note)
    delivered = sum(len(r.files) for r in results)
    stderr.write("delivered %d file(s); report in %s\n" % (delivered, os.path.join(args.out, NOTE_NAME)))
    return 0 if delivered else 3


if __name__ == "__main__":
    sys.exit(main())
