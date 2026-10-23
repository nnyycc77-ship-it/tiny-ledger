"""Moment scoring, from the source's own signals and, when supplied, its
retention or "most replayed" data.

The transcript is split into sentences: a sentence ends at terminal
punctuation (. ? !) or at a pause of PAUSE_SPLIT seconds or more. Every run
of consecutive sentences whose span fits the requested length is a
candidate, so a candidate always starts and ends on a sentence boundary.
Each candidate is scored on signals the source itself carries:

  question and answer   a question sentence followed by its answer
  claim and payoff      a claim cue early and a payoff cue later
  strong opening        a short first sentence that is a question, a hook
                        cue, or addresses the viewer
  energy peak           the speech in the candidate is louder than the
                        file's median
  laughter or applause  a burst of non speech sound inside the candidate
                        (an energy spike with no words over it), named as
                        "possible" because the agent cannot tell which
  topic boundary        a long pause before the candidate starts or after
                        it ends
  needs context         penalised: the first word refers back to something
                        said before the cut ("and", "but", "it", ...)

When retention data is supplied (issue #130), every candidate also gets
the mean of that curve over its span, as a multiple of the curve's median
over the whole video. A lift above the median adds RETENTION_WEIGHT per
unit of lift, enough to outrank every content signal together, so the
chosen moments come from the high retention parts wherever a sentence
bounded span fits there, and each reason line says so with the number.

The best non overlapping candidates are chosen in score order. Every chosen
moment carries one reason line built from the signals that scored it.
"""

import math
import re
import statistics

PAUSE_SPLIT = 0.7          # seconds of silence that end a sentence
TOPIC_PAUSE = 1.5          # seconds of silence that mark a topic boundary
BURST_FACTOR = 2.0         # non speech frame this many times the median is a burst

CLAIM_CUES = ("the secret", "here's why", "here is why", "the truth", "most people",
              "the mistake", "the biggest", "number one", "nobody tells", "never", "always")
PAYOFF_CUES = ("so ", "because", "that's why", "that is why", "the answer", "turns out",
               "which means", "the result")
HOOK_CUES = ("what if", "here's", "here is", "stop", "imagine", "the secret", "did you know")
CONTEXT_WORDS = {"and", "but", "so", "because", "that", "this", "these", "those", "he",
                 "she", "they", "it", "which", "also", "then", "or", "plus", "anyway"}

RETENTION_WEIGHT = 8.0    # score per unit of lift over the curve's median
RETENTION_STEP = 0.25     # seconds between samples of the retention curve

WEIGHTS = {
    "qa": 2.0, "claim": 1.5, "opening": 1.0, "energy": 1.5,
    "burst": 0.5, "boundary": 0.5, "context": -2.0,
}


class Moment:
    def __init__(self, start, end, text, score, reasons):
        self.start = start
        self.end = end
        self.text = text
        self.score = score
        self.reasons = reasons
        self.retention_lift = None

    @property
    def duration(self):
        return self.end - self.start

    def reason_line(self):
        return "; ".join(self.reasons) if self.reasons else "fits the requested length"


class RetentionError(ValueError):
    """The retention file is not in the stated shape."""


class Retention:
    """A retention or "most replayed" curve over the source video.

    Points are (seconds, value) pairs, ascending in time; the curve is
    linear between points and flat before the first and after the last.
    `kind` and `source` are the operator's own description of the data
    (for example a creator analytics export), printed as given.
    """

    def __init__(self, points, kind, source):
        self.points = points
        self.kind = kind
        self.source = source

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict):
            raise RetentionError("the retention file must be a JSON object")
        kind, source, raw = data.get("kind"), data.get("source"), data.get("points")
        if kind not in ("most_replayed", "audience_retention"):
            raise RetentionError("kind must be \"most_replayed\" or \"audience_retention\", got %r" % (kind,))
        if not isinstance(source, str) or not source.strip():
            raise RetentionError("source must say where the data came from (a non empty string)")
        if not isinstance(raw, list) or len(raw) < 2:
            raise RetentionError("points must be a list of at least two {\"t\": seconds, \"value\": number} objects")
        points = []
        for n, item in enumerate(raw):
            t = item.get("t") if isinstance(item, dict) else None
            v = item.get("value") if isinstance(item, dict) else None
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (t, v)):
                raise RetentionError("point %d: t and value must be finite numbers" % n)
            if t < 0 or v < 0:
                raise RetentionError("point %d: t and value must not be negative" % n)
            if points and t <= points[-1][0]:
                raise RetentionError("point %d: times must strictly increase" % n)
            points.append((float(t), float(v)))
        if not any(v > 0 for _, v in points):
            raise RetentionError("every value is zero; there is no retention signal to use")
        return cls(points, kind, source.strip())

    def at(self, t):
        pts = self.points
        if t <= pts[0][0]:
            return pts[0][1]
        if t >= pts[-1][0]:
            return pts[-1][1]
        for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
        return pts[-1][1]

    def mean(self, start, end):
        n = max(1, int(round((end - start) / RETENTION_STEP)))
        return sum(self.at(start + (k + 0.5) * (end - start) / n) for k in range(n)) / n

    def median(self, duration):
        n = max(1, int(duration / RETENTION_STEP))
        return statistics.median(self.at((k + 0.5) * duration / n) for k in range(n))

    def peaks(self, duration, count):
        """Up to `count` high retention moments, highest first: the top of each
        stretch where the curve stays above its median over the video."""
        median = self.median(duration)
        n = max(1, int(duration / RETENTION_STEP))
        found, best = [], None
        for k in range(n + 1):
            t = (k + 0.5) * duration / n
            v = self.at(t) if k < n else median
            if v > median:
                if best is None or v > best[1]:
                    best = (t, v)
            elif best is not None:
                found.append(best)
                best = None
        found.sort(key=lambda p: (-p[1], p[0]))
        return found[:count], median


def _clean(word):
    return re.sub(r"[^\w']", "", word.lower())


def sentences(words):
    groups, current = [], []
    for i, word in enumerate(words):
        current.append(word)
        nxt = words[i + 1] if i + 1 < len(words) else None
        ends = word.text.rstrip().endswith((".", "?", "!"))
        pause = nxt is not None and nxt.start - word.end >= PAUSE_SPLIT
        if ends or pause or nxt is None:
            groups.append(current)
            current = []
    return groups


def _sentence_text(group):
    return " ".join(w.text for w in group)


def _speech_energy(energy, speech, step, start, end):
    """Mean energy over the frames inside [start, end] that carry words, so a
    non speech burst (scored on its own) never inflates the speech level."""
    lo, hi = int(start / step), min(len(energy), max(int(start / step) + 1, int(end / step)))
    window = [energy[f] for f in range(lo, hi) if speech[f]]
    return sum(window) / len(window) if window else 0.0


def _speech_frames(words, step, n_frames):
    covered = [False] * n_frames
    for w in words:
        for f in range(int(w.start / step), min(n_frames, int(w.end / step) + 1)):
            covered[f] = True
    return covered


def score_candidates(words, energy, step, min_len, max_len, retention=None, duration=None):
    groups = sentences(words)
    if retention is not None:
        r_median = retention.median(duration if duration else words[-1].end)
    median = statistics.median(energy) if energy else 0.0
    speech = _speech_frames(words, step, len(energy))
    position = {id(w): n for n, w in enumerate(words)}
    candidates = []
    for i in range(len(groups)):
        for j in range(i, len(groups)):
            start, end = groups[i][0].start, groups[j][-1].end
            span = end - start
            if span > max_len:
                break
            if span < min_len:
                continue
            run = groups[i:j + 1]
            texts = [_sentence_text(g) for g in run]
            lowered = [t.lower() for t in texts]
            score, reasons = 0.0, []

            if any(t.rstrip().endswith("?") for t in texts[:-1]):
                score += WEIGHTS["qa"]
                reasons.append("self contained question and answer")
            if any(c in lowered[0] for c in CLAIM_CUES) and \
                    any(c in " ".join(lowered[1:]) + " " for c in PAYOFF_CUES):
                score += WEIGHTS["claim"]
                reasons.append("claim with its payoff inside the clip")
            first = run[0]
            if len(first) <= 12 and (texts[0].rstrip().endswith("?")
                                     or any(lowered[0].startswith(c) for c in HOOK_CUES)
                                     or _clean(first[0].text) in ("you", "your")):
                score += WEIGHTS["opening"]
                reasons.append("strong opening line")
            level = _speech_energy(energy, speech, step, start, end)
            if median > 0 and level > median * 1.2:
                score += WEIGHTS["energy"] * min(1.0, (level / median - 1.0))
                reasons.append("speech energy peak (%.1fx the median)" % (level / median))
            lo, hi = int(start / step), min(len(energy), int(end / step) + 1)
            if median > 0 and any(not speech[f] and energy[f] > median * BURST_FACTOR
                                  for f in range(lo, hi)):
                score += WEIGHTS["burst"]
                reasons.append("possible laughter or applause (non speech sound burst)")
            first_idx = position[id(first[0])]
            before = start - (words[first_idx - 1].end if first_idx > 0 else 0.0)
            last_idx = position[id(run[-1][-1])]
            after = (words[last_idx + 1].start - end) if last_idx + 1 < len(words) else TOPIC_PAUSE
            if before >= TOPIC_PAUSE or after >= TOPIC_PAUSE:
                score += WEIGHTS["boundary"]
                reasons.append("starts or ends on a topic boundary")
            if _clean(first[0].text) in CONTEXT_WORDS:
                score += WEIGHTS["context"]
                reasons.append("penalised: opens on '%s', which needs earlier context"
                               % _clean(first[0].text))
            lift = None
            if retention is not None:
                level = retention.mean(start, end)
                lift = level / r_median if r_median > 0 else None
                if lift is not None and lift > 1.0:
                    score += RETENTION_WEIGHT * (lift - 1.0)
                    reasons.insert(0, "high retention: %.2fx the video's median in the %s data"
                                   % (lift, retention.kind.replace("_", " ")))
                else:
                    reasons.append("retention at or below the video's median (%s)"
                                   % ("%.2fx" % lift if lift is not None else "median is zero"))
            moment = Moment(start, end, " ".join(texts), score, reasons)
            moment.retention_lift = lift
            candidates.append(moment)
    return candidates


def choose(candidates, count):
    chosen = []
    for cand in sorted(candidates, key=lambda c: (-c.score, c.start)):
        if all(cand.end <= m.start or cand.start >= m.end for m in chosen):
            chosen.append(cand)
        if len(chosen) == count:
            break
    return sorted(chosen, key=lambda m: m.start)
