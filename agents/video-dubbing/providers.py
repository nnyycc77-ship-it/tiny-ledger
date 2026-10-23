"""Provider interfaces for the video dubbing agent.

Four tasks, each behind one small interface so a hosted service can replace
the local implementation by adding one class:

  Transcriber  video -> timed segments          segments-file (local)
  Translator   segment text -> target text      glossary (operator table),
                                                stub (offline tests only)
  Separator    video -> background audio track  duck (ffmpeg, local),
                                                demucs (optional library)
  Voice        text -> speech audio file        stub (tone, offline tests),
                                                flite (local English stock
                                                voices), own-voice (consent
                                                gated; see OwnVoice)

Names and do not translate terms are protected for every translator: a
machine translator only ever sees them masked as numbered placeholders,
and after any translator runs, every protected term in the source segment
must appear verbatim in the target or the run stops (ProtectedTermError).

Nothing here fails open: a missing file, a malformed table, a missing
translation, or a provider that cannot run raises ProviderError, and the
agent stops without writing a deliverable.
"""

import json
import os
import re
import shutil
import subprocess


class ProviderError(RuntimeError):
    """A provider could not do its job."""


class ProtectedTermError(ProviderError):
    """A name or do not translate term did not survive translation."""


class ConsentError(ProviderError):
    """The speaker's own voice was requested without recorded consent."""


def _ffmpeg(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise ProviderError("ffmpeg failed: %s"
                            % proc.stderr.decode("utf-8", "replace").strip()[-600:])
    return proc.stdout


# ----------------------------------------------------------------------
# Transcription
# ----------------------------------------------------------------------

class Segment:
    __slots__ = ("index", "start", "end", "text", "speaker")

    def __init__(self, index, start, end, text, speaker="S1"):
        self.index, self.start, self.end, self.text = index, float(start), float(end), text
        self.speaker = str(speaker)

    @property
    def slot(self):
        return self.end - self.start


class SegmentsFileTranscriber:
    """Timed segments another engine (or a hosted service) produced, with the
    speaker of each line when the engine identifies speakers:
    {"engine": "...", "segments": [{"start": 0.0, "end": 2.1, "text": "...",
    "speaker": "A"}]}. A segment without a speaker is speaker S1."""

    name = "segments-file"

    def __init__(self, path):
        if not path:
            raise ProviderError("the segments-file transcriber needs --segments FILE")
        self.path = path

    def transcribe(self, video_path):
        try:
            with open(self.path, encoding="utf-8") as fh:
                payload = json.load(fh)
            raw = payload["segments"]
            segs = [Segment(i, s["start"], s["end"], str(s["text"]).strip(),
                            s.get("speaker", "S1"))
                    for i, s in enumerate(raw)]
        except (OSError, ValueError, KeyError, TypeError) as err:
            raise ProviderError("cannot read segments %s: %s" % (self.path, err))
        for s in segs:
            if s.end <= s.start or not s.text:
                raise ProviderError("segment %d is empty or ends before it starts" % s.index)
        for a, b in zip(segs, segs[1:]):
            if b.start < a.end:
                raise ProviderError("segments %d and %d overlap" % (a.index, b.index))
        return segs, str(payload.get("engine", self.name))


# ----------------------------------------------------------------------
# Translation, with protected terms
# ----------------------------------------------------------------------

def protected_in(text, terms):
    return [t for t in terms if t and t in text]


def mask(text, terms):
    """Replace each protected term with a numbered placeholder, longest first."""
    mapping = {}
    for n, term in enumerate(sorted(set(t for t in terms if t), key=len, reverse=True)):
        token = "[[%d]]" % n
        if term in text:
            text = text.replace(term, token)
            mapping[token] = term
    return text, mapping


def unmask(text, mapping):
    for token, term in mapping.items():
        if token not in text:
            raise ProtectedTermError("placeholder for %r was lost in translation" % term)
        text = text.replace(token, term)
    return text


def check_protected(source, target, terms, where):
    missing = [t for t in protected_in(source, terms) if t not in target]
    if missing:
        raise ProtectedTermError("%s: protected term(s) missing from the translation: %s"
                                 % (where, ", ".join(missing)))


class GlossaryTranslator:
    """Operator supplied translations, one entry per segment and language:
    {"es": {"0": {"text": "...", "shorter": ["..."], "note": "..."}, "1": "..."}}.
    `shorter` lists tightened wordings with the same meaning, tried in order
    when the full wording does not fit its slot. `note` records why a line
    was hard to translate (an idiom, wordplay); notes go in the report.
    Protected terms are not masked here (a person wrote the table) but are
    checked after."""

    name = "glossary"
    last_note = ""

    def __init__(self, path):
        if not path:
            raise ProviderError("the glossary translator needs --glossary FILE")
        try:
            with open(path, encoding="utf-8") as fh:
                self.table = json.load(fh)
        except (OSError, ValueError) as err:
            raise ProviderError("cannot read glossary %s: %s" % (path, err))

    def translate(self, segment, language, terms):
        entry = self.table.get(language, {}).get(str(segment.index))
        if entry is None:
            raise ProviderError("glossary has no %s translation for segment %d"
                                % (language, segment.index))
        if isinstance(entry, str):
            entry = {"text": entry}
        full = str(entry.get("text", "")).strip()
        if not full:
            raise ProviderError("glossary %s translation for segment %d is empty"
                                % (language, segment.index))
        shorter = [str(s) for s in entry.get("shorter", [])]
        for wording in [full] + shorter:
            check_protected(segment.text, wording, terms,
                            "segment %d (%s)" % (segment.index, language))
        self.last_note = str(entry.get("note", "")).strip()
        return full, shorter


class StubTranslator:
    """OFFLINE TEST STUB, not a translation. Tags the text with the language
    code and keeps it otherwise, so tests can follow the masking path that a
    real machine translator would take. Never use for a delivery."""

    name = "stub"
    last_note = ""

    def translate(self, segment, language, terms):
        masked, mapping = mask(segment.text, terms)
        out = unmask("[%s] %s" % (language, masked), mapping)
        check_protected(segment.text, out, terms, "segment %d (%s)" % (segment.index, language))
        return out, []


# ----------------------------------------------------------------------
# Background separation
# ----------------------------------------------------------------------

class DuckSeparator:
    """Local fallback, not true separation. Keeps the original mix, cuts the
    main speech band, and lowers it, so music and effects stay audible under
    the new voice while the original speech is pushed well back. Stated as
    such in the delivery note."""

    name = "duck"

    def background(self, video_path, out_path):
        _ffmpeg(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", video_path, "-vn",
                 "-af", "bandreject=f=1000:width_type=h:w=2400,volume=0.35",
                 "-ac", "2", "-ar", "44100", out_path])
        return out_path


class DemucsSeparator:
    """Optional: music source separation with the demucs library, keeping
    the no_vocals stem. Needs the demucs package and its model weights,
    neither of which is in this repo."""

    name = "demucs"

    def background(self, video_path, out_path):
        if shutil.which("demucs") is None:
            raise ProviderError("the demucs separator needs the demucs command installed")
        work = os.path.dirname(out_path)
        wav = os.path.join(work, "source.wav")
        _ffmpeg(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", video_path,
                 "-vn", "-ac", "2", "-ar", "44100", wav])
        proc = subprocess.run(["demucs", "--two-stems=vocals", "-o", work, wav],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise ProviderError("demucs failed: %s" % proc.stderr.decode("utf-8", "replace")[-600:])
        for root, _, files in os.walk(work):
            if "no_vocals.wav" in files:
                shutil.copy(os.path.join(root, "no_vocals.wav"), out_path)
                return out_path
        raise ProviderError("demucs produced no no_vocals stem")


# ----------------------------------------------------------------------
# Voices
# ----------------------------------------------------------------------

def audio_seconds(path):
    out = _ffmpeg(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=nw=1:nk=1", path])
    return float(out.decode().strip())


class StubVoice:
    """OFFLINE TEST VOICE, not speech: a soft tone whose length follows the
    text (SECONDS_PER_CHAR per character plus a short tail), at a different
    pitch per speaker. Lets tests exercise timing, speakers and sync without
    any speech engine."""

    name = "stub"
    SECONDS_PER_CHAR = 0.06
    TAIL = 0.2
    PITCHES = (330, 220, 440, 275)

    def __init__(self):
        self.assigned = {}

    def voice_for(self, speaker):
        if speaker not in self.assigned:
            self.assigned[speaker] = "tone %d Hz" % self.PITCHES[len(self.assigned) % len(self.PITCHES)]
        return self.assigned[speaker]

    def synthesize(self, text, language, out_path, speaker="S1"):
        pitch = int(self.voice_for(speaker).split()[1])
        seconds = round(len(text) * self.SECONDS_PER_CHAR + self.TAIL, 3)
        _ffmpeg(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
                 "-i", "sine=f=%d:d=%s" % (pitch, seconds), "-af", "volume=0.3",
                 "-ac", "2", "-ar", "44100", out_path])
        return out_path


class FliteVoice:
    """Local stock voices from libflite through ffmpeg's flite filter. The
    first speaker gets the chosen voice and each further speaker the next
    distinct one. English only; any other language is refused rather than
    mispronounced."""

    name = "flite"
    VOICES = ("slt", "kal", "awb", "rms", "kal16")

    def __init__(self, voice="slt"):
        if voice not in self.VOICES:
            raise ProviderError("unknown flite voice %r; known: %s" % (voice, ", ".join(self.VOICES)))
        self.order = [voice] + [v for v in self.VOICES if v != voice]
        self.assigned = {}

    def voice_for(self, speaker):
        if speaker not in self.assigned:
            if len(self.assigned) >= len(self.order):
                raise ProviderError("more speakers than distinct flite voices (%d)" % len(self.order))
            self.assigned[speaker] = self.order[len(self.assigned)]
        return self.assigned[speaker]

    def synthesize(self, text, language, out_path, speaker="S1"):
        if not language.lower().startswith("en"):
            raise ProviderError("the flite voices speak English only, not %r" % language)
        text_file = out_path + ".txt"
        with open(text_file, "w", encoding="utf-8") as fh:
            fh.write(text)
        _ffmpeg(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
                 "-i", "flite=textfile='%s':voice=%s" % (text_file.replace("'", ""),
                                                         self.voice_for(speaker)),
                 "-ac", "2", "-ar", "44100", out_path])
        return out_path


# The job's rule: "Only recreate a speaker's own voice when the buyer
# confirms they are that speaker or have the speaker's consent." The buyer
# also "confirms they have the rights to use" the video (job text, issue #77
# comment 6365954974).
CONSENT_FIELDS = ("basis", "consent_record", "rights_confirmed", "confirmed_by")
CONSENT_BASES = ("buyer_is_speaker", "speaker_consent")


def check_consent(consent):
    """Raise ConsentError unless the job inputs carry a recorded consent and a
    rights confirmation: basis is buyer_is_speaker or speaker_consent, a non
    empty consent_record (where the confirmation is kept), rights_confirmed
    true (the buyer has the rights to use the video), and a non empty
    confirmed_by."""
    if not isinstance(consent, dict):
        raise ConsentError("the own-voice option needs a consent record in the job inputs "
                           "(%s); none was given" % ", ".join(CONSENT_FIELDS))
    problems = []
    if consent.get("basis") not in CONSENT_BASES:
        problems.append("basis is not one of %s" % ", ".join(CONSENT_BASES))
    if not str(consent.get("consent_record", "")).strip():
        problems.append("consent_record is empty")
    if consent.get("rights_confirmed") is not True:
        problems.append("rights_confirmed is not true")
    if not str(consent.get("confirmed_by", "")).strip():
        problems.append("confirmed_by is empty")
    if problems:
        raise ConsentError("own-voice refused: " + "; ".join(problems))


class OwnVoice:
    """The speaker's own voice, as a consent gated branch only.

    It refuses at construction unless check_consent passes. This build ships
    no voice cloning engine, so even with consent it then refuses with a
    plain message; a cloning provider would be added here, behind the same
    consent check, only after an award and an owner decision."""

    name = "own-voice"

    def __init__(self, consent):
        check_consent(consent)
        raise ProviderError("consent recorded, but this build has no voice cloning engine; "
                            "use a stock voice")


def make_voice(name, consent=None, flite_voice="slt"):
    if name == "stub":
        return StubVoice()
    if name == "flite":
        return FliteVoice(flite_voice)
    if name == "own-voice":
        return OwnVoice(consent)
    raise ProviderError("unknown voice %r; known: stub, flite, own-voice" % name)


def make_translator(name, glossary=None):
    if name == "glossary":
        return GlossaryTranslator(glossary)
    if name == "stub":
        return StubTranslator()
    raise ProviderError("unknown translator %r; known: glossary, stub" % name)


def make_separator(name):
    if name == "duck":
        return DuckSeparator()
    if name == "demucs":
        return DemucsSeparator()
    raise ProviderError("unknown separator %r; known: duck, demucs" % name)


def split_terms(value):
    return [t.strip() for t in re.split(r"[,\n]", value or "") if t.strip()]
