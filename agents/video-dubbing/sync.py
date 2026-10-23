"""Sync handling: fit each dubbed line into the time the original line used.

The order follows the bid proposal (issue #77, comment 6365955553):

  1. tighten   try the shorter wordings the translator offers (same meaning),
               shortest last, and keep the first that fits;
  2. stretch   speed the line up with ffmpeg atempo, never beyond
               MAX_STRETCH;
  3. breathe   let the line run into the pause after it, only when that pause
               is a genuine one (at least GENUINE_PAUSE seconds), keeping
               MIN_GAP of silence before the next line.

A line that still does not fit is not cut short: the run stops and names
the segment, so a shorter wording can be supplied. Any line that was
stretched is flagged in the delivery note. Placement is at the original
start time, so the job's "starts within one second" criterion holds by
construction, and breathing never reaches the next line.

The three limits are configurable defaults: neither the job text nor the
proposal gives a number ("mild time stretching inside safe limits").
"""

MAX_STRETCH = 1.15     # at most 15% faster than the synthesized line
GENUINE_PAUSE = 0.4    # seconds of silence that count as a real pause
MIN_GAP = 0.1          # seconds kept free before the next line


class SyncError(RuntimeError):
    """A line cannot be fitted within the limits."""


class Fit:
    def __init__(self, segment, wording, tightened, natural, stretch, window, breathed):
        self.segment = segment
        self.wording = wording
        self.tightened = tightened
        self.natural = natural        # seconds as synthesized
        self.stretch = stretch        # atempo factor, 1.0 if none
        self.window = window          # seconds the line may occupy
        self.breathed = breathed      # seconds borrowed from the next pause

    @property
    def flagged(self):
        return self.stretch > 1.0

    def note(self):
        parts = []
        if self.tightened:
            parts.append("tightened wording used")
        if self.stretch > 1.0:
            parts.append("compressed %.2fx" % self.stretch)
        if self.breathed > 0:
            parts.append("runs %.2f s into the following pause" % self.breathed)
        return "; ".join(parts) or "fits as spoken"


def available_window(segment, following, max_stretch=MAX_STRETCH):
    """Seconds this line may use: its own slot plus a genuine following pause."""
    slot = segment.slot
    if following is None:
        return slot, 0.0
    pause = following.start - segment.end
    if pause >= GENUINE_PAUSE:
        return slot, max(0.0, pause - MIN_GAP)
    return slot, 0.0


def fit_line(segment, following, wordings, measure, max_stretch=MAX_STRETCH):
    """wordings: full wording first, then shorter ones. measure(text) returns
    the synthesized length in seconds. Returns a Fit or raises SyncError."""
    slot, spare = available_window(segment, following, max_stretch)
    lengths = []
    for n, wording in enumerate(wordings):            # 1. tighten
        natural = measure(wording)
        lengths.append(natural)
        if natural <= slot:
            return Fit(segment, wording, n > 0, natural, 1.0, slot, 0.0)
    for n, wording in enumerate(wordings):            # 2. stretch
        natural = lengths[n]
        if natural / max_stretch <= slot:
            return Fit(segment, wording, n > 0, natural, natural / slot, slot, 0.0)
    for n, wording in enumerate(wordings):            # 3. breathe
        natural = lengths[n]
        if spare and natural / max_stretch <= slot + spare:
            stretch = max(1.0, natural / (slot + spare))
            used = natural / stretch - slot
            return Fit(segment, wording, n > 0, natural, stretch, slot + used, used)
    raise SyncError(
        "segment %d (%.2f-%.2fs) cannot fit: shortest wording needs %.2f s, the slot is "
        "%.2f s, at most %.2fx compression and %.2f s of following pause; supply a "
        "shorter wording" % (segment.index, segment.start, segment.end, min(lengths), slot,
                             max_stretch, spare))
