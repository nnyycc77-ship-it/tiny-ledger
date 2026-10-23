"""Transcription engines for the video clipping agent.

Every engine returns the same shape, a Transcript: a list of words, each
with its text and its start and end time in seconds. The rest of the agent
only ever sees that shape, so a hosted engine can replace the local one by
adding one class here and naming it on the command line; nothing else
changes.

Engines:

  transcript-file  Reads word timings from a JSON file that another
                   engine (or a hosted service) already produced:
                   {"engine": "...", "words": [{"w": "...", "start": 0.0,
                   "end": 0.4}, ...]}. No model, no network. The offline
                   tests use this engine with a synthetic transcript they
                   build themselves.
  vosk             Local speech recognition with word level timing through
                   the vosk package and a model directory on disk, named by
                   the VOSK_MODEL_PATH environment value. Optional: the
                   package and the model are not part of this repo and are
                   only imported when this engine is chosen. Audio is
                   decoded to 16 kHz mono PCM with ffmpeg.

A failure is never turned into an empty transcript: a missing file, a
malformed JSON body, a missing model, or a recogniser error raises
EngineError, and the agent stops without cutting anything.
"""

import json
import os
import subprocess


class EngineError(RuntimeError):
    """The engine could not produce a transcript."""


class Word:
    __slots__ = ("text", "start", "end")

    def __init__(self, text, start, end):
        self.text = text
        self.start = float(start)
        self.end = float(end)

    def to_dict(self):
        return {"w": self.text, "start": round(self.start, 3), "end": round(self.end, 3)}


class Transcript:
    def __init__(self, words, engine):
        self.words = words
        self.engine = engine


def _words_from_json(payload, where):
    if not isinstance(payload, dict) or not isinstance(payload.get("words"), list):
        raise EngineError("%s: expected an object with a 'words' list" % where)
    words = []
    for i, item in enumerate(payload["words"]):
        try:
            word = Word(str(item["w"]), item["start"], item["end"])
        except (KeyError, TypeError, ValueError) as err:
            raise EngineError("%s: word %d is malformed (%s)" % (where, i, err))
        if word.end < word.start:
            raise EngineError("%s: word %d ends before it starts" % (where, i))
        words.append(word)
    words.sort(key=lambda w: w.start)
    return words


class TranscriptFileEngine:
    name = "transcript-file"

    def __init__(self, path):
        if not path:
            raise EngineError("the transcript-file engine needs --transcript FILE")
        self.path = path

    def transcribe(self, video_path):
        try:
            with open(self.path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, ValueError) as err:
            raise EngineError("cannot read transcript %s: %s" % (self.path, err))
        engine = payload.get("engine", self.name) if isinstance(payload, dict) else self.name
        return Transcript(_words_from_json(payload, self.path), str(engine))


class VoskEngine:
    name = "vosk"
    SAMPLE_RATE = 16000

    def __init__(self, model_path=None):
        self.model_path = model_path or os.environ.get("VOSK_MODEL_PATH", "")
        if not self.model_path or not os.path.isdir(self.model_path):
            raise EngineError(
                "the vosk engine needs VOSK_MODEL_PATH set to a model directory")

    def transcribe(self, video_path):
        try:
            import vosk  # optional dependency, imported only for this engine
        except ImportError:
            raise EngineError("the vosk engine needs the vosk package installed")
        model = vosk.Model(self.model_path)
        recogniser = vosk.KaldiRecognizer(model, self.SAMPLE_RATE)
        recogniser.SetWords(True)
        proc = subprocess.Popen(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", video_path,
             "-ac", "1", "-ar", str(self.SAMPLE_RATE), "-f", "s16le", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        results = []
        while True:
            chunk = proc.stdout.read(8000)
            if not chunk:
                break
            if recogniser.AcceptWaveform(chunk):
                results.append(json.loads(recogniser.Result()))
        results.append(json.loads(recogniser.FinalResult()))
        err = proc.stderr.read().decode("utf-8", "replace")
        if proc.wait() != 0:
            raise EngineError("ffmpeg could not decode the audio: %s" % err.strip())
        words = [Word(r["word"], r["start"], r["end"])
                 for res in results for r in res.get("result", [])]
        return Transcript(words, self.name)


ENGINES = {"transcript-file": TranscriptFileEngine, "vosk": VoskEngine}


def make_engine(name, transcript_path=None):
    if name == "transcript-file":
        return TranscriptFileEngine(transcript_path)
    if name == "vosk":
        return VoskEngine()
    raise EngineError("unknown engine %r; known: %s" % (name, ", ".join(sorted(ENGINES))))
