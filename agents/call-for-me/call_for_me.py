#!/usr/bin/env python3
"""Call-for-Me Booking agent: design-stage core and simulation harness.

Issue #79, prebuild for NEAR Agent Market job 92332aa9 ("Call-for-Me
Booking Agent"). Standard library only. This build places no calls: the only
line it can dial is a scripted business used by the simulation. `call`
always refuses.

The agent is split in two so the hard rules never depend on speech
understanding:
  * understand(text) turns one business utterance into intents and slots.
    Here it is a small rule set good enough for scripted scenarios; the live
    stage swaps in real-time speech recognition plus a classifier.
  * CallSession applies the policy: it speaks only fixed templates, books
    only a slot inside the window or a pre-approved alternative, answers
    "yes" whenever asked if it is an AI, declines every payment request,
    and stores structured fields only (no transcript, no business speech).

Commands:
  check     --brief FILE                  print the confirmed brief
  plan      --brief FILE --start UTC      print the permitted call times
  simulate  SCENARIO.json... [--json] [--dialogue]
                                          run scripted scenarios, print the
                                          report, check expectations and the
                                          invariants; exit 1 on any failure
  call      ...                           always refuses (no telephony here)
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ---------------------------------------------------------------- policy ----
# Values the listing states. They are owner decisions at award time; the
# simulation and tests read them from here so the listing and the code match.
POLICY = {
    "max_attempts": 3,            # calls per business per job, first call included
    "retry_gap_minutes": 30,      # minimum time between two attempts
    "calling_hours": ("09:00", "20:00"),  # business local time, also inside opening hours
    "lead_minutes": 60,           # last call no later than this before the window opens
    "ring_timeout_s": 30,         # live stage: give up ringing after this
    "call_time_limit_s": 600,     # live stage: hang up after this
    "max_unclear": 2,             # "could you repeat that" at most this many times per call
    "operating_country": "US",
    "languages": ("en",),
}

STATUS_BOOKED = "booked"
STATUS_NOT_AVAILABLE = "not available"
STATUS_NO_ANSWER = "no answer"
STATUS_NOT_BOOKED = "not booked"

REASONS = {
    "payment_required": "The business would not hold the booking without a card, deposit, prepayment or fee agreement. The agent declined and gave no payment details.",
    "declined_ai_caller": "The business declined to take a booking from an AI caller.",
    "hung_up": "The business ended the call before a booking was made.",
    "asked_not_to_call": "The business asked not to be called again. No further attempt was made.",
    "unclear": "The agent could not understand the business well enough to book on any attempt.",
    "no_call_window": "No permitted calling time (opening hours and calling hours) was left before the booking window.",
    "contact_required": "The business required a callback number and the brief did not provide one.",
}

RETRYABLE = {"no answer", "busy", "voicemail", "phone menu", "unclear", "dropped"}

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
FORBIDDEN_BRIEF_KEYS = re.compile(r"card|cvv|cvc|iban|account_number|payment|deposit|billing|expiry|ssn", re.I)


class BriefError(Exception):
    pass


class ScenarioError(Exception):
    pass


# ----------------------------------------------------------------- brief ----
def parse_hhmm(text, what):
    m = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", str(text or ""))
    if not m:
        raise BriefError("%s must be HH:MM (24 hour), got %r" % (what, text))
    return int(m.group(1)) * 60 + int(m.group(2))


def fmt_hhmm(minutes):
    return "%02d:%02d" % divmod(minutes, 60)


def fmt_time(minutes):
    h, m = divmod(minutes, 60)
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return "%d:%02d %s" % (h12, m, suffix)


def parse_date(text, what):
    try:
        return dt.date.fromisoformat(str(text))
    except ValueError:
        raise BriefError("%s must be YYYY-MM-DD, got %r" % (what, text))


def fmt_date(d):
    return "%s %s %d, %d" % (d.strftime("%A"), d.strftime("%B"), d.day, d.year)


def _walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path + k, k
            yield from _walk_keys(v, path + k + ".")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_keys(v, path + "%d." % i)


def _window(obj, what):
    if not isinstance(obj, dict):
        raise BriefError("%s must be an object with date, start and end" % what)
    d = parse_date(obj.get("date"), what + ".date")
    s = parse_hhmm(obj.get("start"), what + ".start")
    e = parse_hhmm(obj.get("end"), what + ".end")
    if e <= s:
        raise BriefError("%s.end must be after %s.start" % (what, what))
    return {"date": d, "start": s, "end": e}


def validate_brief(raw):
    """Return the confirmed brief or raise BriefError. Fails closed."""
    if not isinstance(raw, dict):
        raise BriefError("brief must be a JSON object")
    for path, key in _walk_keys(raw):
        if FORBIDDEN_BRIEF_KEYS.search(key):
            raise BriefError("brief field %r looks like payment data; the agent never takes or gives payment details" % path)
    biz = raw.get("business")
    if not isinstance(biz, dict) or not str(biz.get("name") or "").strip():
        raise BriefError("business.name is required")
    phone = str(biz.get("phone") or "")
    if not re.fullmatch(r"\+1\d{10}", phone):
        raise BriefError("business.phone must be a +1 number in E.164 form (operating country %s)" % POLICY["operating_country"])
    if biz.get("country") != POLICY["operating_country"]:
        raise BriefError("business.country must be %r; this agent calls only there" % POLICY["operating_country"])
    if not re.match(r"https?://", str(biz.get("phone_source") or "")):
        raise BriefError("business.phone_source must be the http(s) page where the business publishes this number (business numbers only)")
    try:
        tz = ZoneInfo(str(biz.get("timezone") or ""))
    except (ZoneInfoNotFoundError, ValueError):
        raise BriefError("business.timezone must be an IANA zone name, got %r" % biz.get("timezone"))
    hours_raw = biz.get("opening_hours")
    if not isinstance(hours_raw, dict):
        raise BriefError("business.opening_hours is required (calls happen only during opening hours)")
    hours = {}
    for key in DAY_KEYS:
        spans = hours_raw.get(key, [])
        if spans == "closed":
            spans = []
        if not isinstance(spans, list):
            raise BriefError("opening_hours.%s must be a list of [open, close] or \"closed\"" % key)
        out = []
        for span in spans:
            if not (isinstance(span, list) and len(span) == 2):
                raise BriefError("opening_hours.%s entries must be [open, close]" % key)
            o, c = parse_hhmm(span[0], "opening_hours." + key), parse_hhmm(span[1], "opening_hours." + key)
            if c <= o:
                raise BriefError("opening_hours.%s closes before it opens" % key)
            out.append((o, c))
        hours[key] = out
    booking = raw.get("booking")
    if not isinstance(booking, dict):
        raise BriefError("booking is required")
    window = _window(booking, "booking")
    party = booking.get("party_size")
    service = str(booking.get("service") or "").strip()
    if (party is None) == (not service):
        raise BriefError("booking needs exactly one of party_size or service")
    if party is not None and (not isinstance(party, int) or isinstance(party, bool) or not 1 <= party <= 50):
        raise BriefError("booking.party_size must be a whole number from 1 to 50")
    name = str(booking.get("name") or "").strip()
    if not name:
        raise BriefError("booking.name is required")
    alternatives = [_window(a, "alternatives[%d]" % i) for i, a in enumerate(raw.get("alternatives") or [])]
    callback = raw.get("callback_number")
    if callback is not None and not re.fullmatch(r"\+1\d{10}", str(callback)):
        raise BriefError("callback_number, if given, must be a +1 E.164 number the buyer approved for sharing")
    lang = raw.get("report_language", "en")
    if lang not in POLICY["languages"]:
        raise BriefError("report_language %r is not supported; this build calls and reports in English only" % lang)
    requests = raw.get("special_requests") or []
    if not isinstance(requests, list) or not all(isinstance(r, str) for r in requests):
        raise BriefError("special_requests must be a list of strings")
    return {
        "business": {"name": biz["name"].strip(), "phone": phone, "phone_source": biz["phone_source"],
                     "timezone": str(biz["timezone"]), "tz": tz, "hours": hours},
        "window": window, "party_size": party, "service": service or None, "name": name,
        "alternatives": alternatives, "callback_number": callback,
        "special_requests": requests, "report_language": lang,
    }


def what_phrase(brief):
    if brief["party_size"] is not None:
        return "a table for %d" % brief["party_size"]
    return "a %s appointment" % brief["service"] if not brief["service"].lower().startswith(("a ", "an ")) else brief["service"]


def window_phrase(w):
    return "%s between %s and %s" % (fmt_date(w["date"]), fmt_time(w["start"]), fmt_time(w["end"]))


def confirmed_brief_text(brief):
    lines = ["Confirmed brief (nothing is called before this is confirmed):",
             "- Business: %s, %s (number as published at %s), time zone %s" % (
                 brief["business"]["name"], brief["business"]["phone"], brief["business"]["phone_source"], brief["business"]["timezone"]),
             "- Booking: %s on %s, under the name %s" % (what_phrase(brief), window_phrase(brief["window"]), brief["name"])]
    if brief["alternatives"]:
        for a in brief["alternatives"]:
            lines.append("- Pre-approved alternative: %s" % window_phrase(a))
    else:
        lines.append("- Pre-approved alternatives: none (anything outside the window is reported, not booked)")
    lines.append("- Callback number: %s" % ("%s (approved by the buyer for sharing)" % brief["callback_number"]
                                             if brief["callback_number"] else "none given; the agent will not share one"))
    if brief["special_requests"]:
        lines.append("- Special requests: %s" % "; ".join(brief["special_requests"]))
    lines.append("- Calls and report in English; at most %d attempts, %d minutes apart, within opening hours and %s to %s local time" % (
        POLICY["max_attempts"], POLICY["retry_gap_minutes"], POLICY["calling_hours"][0], POLICY["calling_hours"][1]))
    return "\n".join(lines)


# -------------------------------------------------------------- schedule ----
def _local(brief, when_utc):
    return when_utc.astimezone(brief["business"]["tz"])


def call_allowed(brief, when_utc):
    """True when when_utc is inside opening hours, calling hours and before the deadline."""
    local = _local(brief, when_utc)
    minute = local.hour * 60 + local.minute
    lo, hi = (parse_hhmm(x, "calling_hours") for x in POLICY["calling_hours"])
    if not lo <= minute < hi:
        return False
    spans = brief["business"]["hours"][DAY_KEYS[local.weekday()]]
    if not any(o <= minute < c for o, c in spans):
        return False
    return when_utc < call_deadline(brief)


def call_deadline(brief):
    w = brief["window"]
    tz = brief["business"]["tz"]
    start = dt.datetime.combine(w["date"], dt.time(*divmod(w["start"], 60)), tzinfo=tz)
    return (start - dt.timedelta(minutes=POLICY["lead_minutes"])).astimezone(dt.timezone.utc)


def next_allowed(brief, after_utc):
    """First minute at or after after_utc when a call is allowed, else None."""
    t = after_utc.replace(second=0, microsecond=0)
    if t < after_utc:
        t += dt.timedelta(minutes=1)
    deadline = call_deadline(brief)
    while t < deadline:
        if call_allowed(brief, t):
            return t
        t += dt.timedelta(minutes=1)
    return None


def plan_attempts(brief, start_utc):
    """The times the agent would call if every attempt failed."""
    times, t = [], next_allowed(brief, start_utc)
    while t is not None and len(times) < POLICY["max_attempts"]:
        times.append(t)
        t = next_allowed(brief, t + dt.timedelta(minutes=POLICY["retry_gap_minutes"]))
    return times


# ------------------------------------------------------------ understand ----
P = lambda s: re.compile(s, re.I)
INTENT_PATTERNS = [
    ("do_not_call", P(r"\b(don'?t|do not|never) call (us|here|this number)( again)?\b|\bstop calling\b|\bremove (this|our) number\b")),
    ("refuse_ai", P(r"\b(don'?t|do not|won'?t|can'?t|cannot)\b[^.?!]*\b(book|take|accept|deal|talk)\b[^.?!]*\b(robots?|bots?|ai|machines?|computers?|automated)\b"
                    r"|\b(no|not) (robots?|bots?|ai|machines?|automated (calls?|callers?))\b")),
    # No question mark required: speech recognition output often has none, and
    # answering "yes, I am an AI" when it was not quite asked is harmless,
    # while missing the question is a fail signal.
    ("ask_ai", P(r"\b(robots?|bots?|a\.i\.?|ai|artificial intelligence|machine|computer|automated|recording|real person|live person|human)\b"
                 r"|\bam i (talking|speaking) (to|with)\b|\b(talking|speaking) (to|with) (a )?(person|someone real)\b"
                 r"|\bare you (real|a real|human|a person)\b")),
    ("ask_payment", P(r"\b(credit|debit)? ?card\b|\bdeposit\b|\bpre-?pa(y|id|yment)\b|\bpa(y|id) (now|upfront|up front|in advance|ahead)\b"
                      r"|\bcancellation fee\b|\bno-?show fee\b|\bcard details\b|\bcard number\b")),
    ("payment_required", P(r"\b(can'?t|cannot|won'?t|unable to|not able to)\b[^.?!]*\b(hold|book|reserve|keep)\b[^.?!]*\bwithout\b"
                           r"|\bno card,? no\b|\b(need|require|have to have|must have)\b[^.?!]*\b(card|deposit|prepayment)\b[^.?!]*\b(to|or)\b[^.?!]*\b(hold|book|reserve)\b")),
    ("payment_waived", P(r"\b(that'?s (fine|ok|okay)|no problem|we can(?!'?t|not)|we'?ll|sure)\b[^.?!]*\bwithout\b"
                         r"|\b(don'?t|do not) need (a|the|any) (card|deposit|prepayment)\b|\bno (card|deposit) (needed|required)\b")),
    ("no_availability", P(r"\bfully booked\b|\bbooked up\b|\bno (tables?|availability|openings?|slots?|appointments?|space)\b"
                          r"|\bnothing (available|left|open|in)\b|\b(don'?t|do not) have anything\b|\bnothing\b[^.?!]*\b(morning|evening|afternoon|between|then)\b")),
    ("ask_name", P(r"\b(what|which) name\b|\bname (for|on) the (booking|reservation|appointment)\b|\bunder what name\b|\bcan i (get|have|take) (a|the|your) name\b|\band the name\b")),
    ("ask_party", P(r"\bhow many (people|guests|of you|in your party)\b|\bparty size\b|\bfor how many\b")),
    ("ask_service", P(r"\bwhat (service|kind of (appointment|service)|are you looking to (have|book))\b|\bwhich service\b")),
    ("ask_callback", P(r"\b(phone|contact|callback|call-?back) number\b|\bnumber (to|we can) (reach|call)\b|\bbest number\b")),
    ("ask_requests", P(r"\b(any )?special requests?\b|\banything else (we should know|for the booking)\b|\b(allergies|occasion|high ?chair)\b[^.!]*\?")),
    ("hold", P(r"\b(hold on|please hold|one moment|bear with me|let me (check|look|see))\b")),
    ("confirmed", P(r"\b(you'?re|you are) (all set|booked|confirmed|in)\b|\b(i'?ve|we'?ve) (booked|got|put) you\b|\bthat'?s (booked|confirmed)\b"
                    r"|\bconfirmation (number|code) is\b|\bsee you (then|on)\b")),
    ("goodbye", P(r"\b(good ?bye|bye|have a (good|nice) (one|day|evening|night))\b")),
]
CONFIRMATION_RE = P(r"\bconfirmation (?:number|code) is ([A-Z0-9][A-Z0-9-]{1,15})\b")
TIME_RE = P(r"\b(noon|midday)\b|\b(\d{1,2})(?::([0-5]\d))?\s*(a\.?m\.?|p\.?m\.?|o'?clock)?(?![\w:])")
NON_OFFER_SPAN_RE = P(r"\bbetween\b[^.?!]*?\band\b\s*\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)?"
                      r"|\b(?:open|opens|close|closes|closed|until|till|from)\b\s*(?:at\s*)?\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)?")
DATE_RE = P(r"\b(?:(next|this)\s+)?(" + "|".join(WEEKDAYS) + r")\b"
            r"|\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?\b"
            r"|\bthe\s+(\d{1,2})(?:st|nd|rd|th)\b"
            r"|\b(same (?:day|night|evening)|that (?:day|night|evening))\b")


class Slot(object):
    """One time the business offered. date may be None; minutes lists readings."""

    def __init__(self, date, readings, stated):
        self.date, self.readings, self.stated = date, readings, stated

    def __repr__(self):
        return "Slot(%s, %s, %r)" % (self.date, self.readings, self.stated)


class Heard(object):
    def __init__(self):
        self.intents, self.slots, self.confirmation, self.dates = set(), [], None, []


def resolve_date(match, context_date, requested_date, today=None):
    nxt, wd, month, mday, the_day, same = match.groups()
    if wd:
        target = WEEKDAYS.index(wd.lower())
        if nxt and nxt.lower() == "next":
            d = requested_date + dt.timedelta(days=1)
            while d.weekday() != target:
                d += dt.timedelta(days=1)
            return d
        for delta in (0, 1, -1, 2, -2, 3, -3, 4, 5, 6):
            d = requested_date + dt.timedelta(days=delta)
            if d.weekday() == target and (today is None or d >= today):
                return d
    if month:
        try:
            return dt.date(requested_date.year, MONTHS.index(month.lower()) + 1, int(mday))
        except ValueError:
            return None
    if the_day:
        try:
            return requested_date.replace(day=int(the_day))
        except ValueError:
            return None
    if same:
        return context_date
    return None


def time_readings(m):
    if m.group(1):
        return [12 * 60]
    hour, minute, suffix = int(m.group(2)), int(m.group(3) or 0), (m.group(4) or "").lower().replace(".", "")
    if suffix in ("am", "pm"):
        if not 1 <= hour <= 12:
            return []
        h = hour % 12 + (12 if suffix == "pm" else 0)
        return [h * 60 + minute]
    if hour > 23:
        return []
    if hour == 0 or hour >= 13:
        return [hour * 60 + minute]
    return sorted({(hour % 12) * 60 + minute, (hour % 12 + 12) * 60 + minute})


def understand(text, context_date, requested_date, today=None):
    """Intents and offered slots in one business utterance."""
    heard = Heard()
    for name, pattern in INTENT_PATTERNS:
        if pattern.search(text):
            heard.intents.add(name)
    if "refuse_ai" in heard.intents:
        heard.intents.discard("ask_ai")
    if "payment_required" in heard.intents:
        heard.intents.discard("payment_waived")
    m = CONFIRMATION_RE.search(text)
    # a code holds a digit or is written in capitals; "is in your email" is not a code
    if m and (any(ch.isdigit() for ch in m.group(1)) or m.group(1).isupper()):
        heard.confirmation = m.group(1)
        heard.intents.add("confirmed")
    masked = NON_OFFER_SPAN_RE.sub(lambda x: " " * len(x.group(0)), text)
    if heard.confirmation:
        masked = masked.replace(heard.confirmation, " " * len(heard.confirmation))
    events = []
    for dm in DATE_RE.finditer(masked):
        events.append((dm.start(), "date", dm))
    for tm in TIME_RE.finditer(masked):
        if tm.group(1) or tm.group(3) or tm.group(4) or re.search(r"\b(at|around|by)\s*$", masked[:tm.start()], re.I):
            events.append((tm.start(), "time", tm))
    dates = sorted((e for e in events if e[1] == "date"), key=lambda e: e[0])
    times = sorted((e for e in events if e[1] == "time"), key=lambda e: e[0])
    resolved = {}
    current = context_date
    for start, _, dm in dates:
        current = resolve_date(dm, current, requested_date, today)
        resolved[start] = current
        heard.dates.append(current)
    for start, _, tm in times:
        # a day named right after the time ("7:30 Friday", "8 on Saturday") binds to it;
        # otherwise the last day named before it in this utterance; otherwise the context
        after = [d for d in dates if d[0] >= tm.end() and re.fullmatch(r"[\s,]*(?:on\s+)?", masked[tm.end():d[0]], re.I)]
        before = [d for d in dates if d[0] < start]
        if after:
            pick = after[0]
        elif before:
            pick = before[-1]
        else:
            pick = None
        date = resolved[pick[0]] if pick else context_date
        readings = time_readings(tm)
        if readings:
            lo, hi = tm.start(), tm.end()
            if pick and (pick in after or start - pick[2].end() <= 12):
                lo, hi = min(lo, pick[2].start()), max(hi, pick[2].end())
            stated = text[lo:hi].strip().rstrip(".,")
            heard.slots.append(Slot(date, readings, stated))
    if heard.slots:
        heard.intents.add("offer")
    return heard


# --------------------------------------------------------------- session ----
TEMPLATES = {
    "OPENING": "Hello, this is an automated booking assistant, an AI, calling on behalf of {name}. "
               "I'd like to book {what} on {window}.",
    "AI_ANSWER": "Yes, I am an AI. I'm an automated booking assistant calling on behalf of {name}.",
    "AI_CONTINUE": "I'd still like to book {what} if that's all right with you.",
    "POLITE_END": "I understand. Thank you for your time, goodbye.",
    "STOP_END": "Understood, we won't call again. Goodbye.",
    "PAYMENT_DECLINE": "I'm not able to give card details or agree to a deposit, prepayment or cancellation fee. "
                       "I'll pass the request on to {name}. Can the booking be made without it?",
    "PAYMENT_END": "Understood. Then please don't book it, and I'll let {name} know about the request. Thank you, goodbye.",
    "ACCEPT": "That works. Please book {what} on {date} at {time} under the name {name}.",
    "ASK_IN_WINDOW": "Thank you. I can only book {allowed}. Is anything available in that time?",
    "ASK_OTHER_TIMES": "Do you have any other times you could offer? I won't book them now, I'll pass them on.",
    "ASK_DATE": "Sorry, which day is that for?",
    "NOT_BOOKED_END": "Thank you. I won't book anything now, and I'll pass the times you offered on to {name}. Goodbye.",
    "NOTHING_END": "Thank you for checking. I won't book anything now. Goodbye.",
    "GIVE_NAME": "The name is {name}.",
    "GIVE_PARTY": "It's for {party} people.",
    "GIVE_SERVICE": "It's for {service}.",
    "GIVE_CALLBACK": "The callback number is {callback}.",
    "NO_CALLBACK": "I'm not able to share a phone number. Could the booking be held under the name {name}?",
    "GIVE_REQUESTS": "One request: {requests}.",
    "NO_REQUESTS": "No special requests, thank you.",
    "REPEAT": "Sorry, could you say that again?",
    "UNCLEAR_END": "I'm sorry, I'm having trouble understanding. I'll try again later. Goodbye.",
    "WAIT": "Of course, I'll hold.",
    "ASK_TIME": "Sorry, which time is the booking for?",
    "CONFIRM_END": "Thank you. So that's {what} on {date} at {time} under {name}{ref}. Goodbye.",
}


class CallSession(object):
    """One answered call. Keeps structured fields only; never the business's words."""

    def __init__(self, brief, today=None):
        self.brief = brief
        self.today = today        # the business's local date during the call
        self.context_date = brief["window"]["date"]
        self.said = []            # template ids spoken, in order (no text stored)
        self.done = False
        self.end = None           # how the call ended: booked, not_available, payment_required, ...
        self.pending = None       # (date, minutes, used_alternative) accepted, awaiting confirmation
        self.booked = None
        self.confirmation = None
        self.alternatives = []    # {"date", "time", "stated"}
        self.payment_requests = []
        self.payment_open = False
        self.conditional = None   # bookable slot the business offered only with a payment condition
        self.asked_if_ai = 0
        self.callback_requested = False
        self.callback_shared = False
        self.asked_in_window = False
        self.asked_other_times = False
        self.unclear = 0

    # --- speaking: only fixed templates ---
    def _say(self, out, key, **extra):
        b = self.brief
        fields = {"name": b["name"], "what": what_phrase(b), "window": window_phrase(b["window"]),
                  "party": b["party_size"], "service": b["service"], "callback": spoken_number(b["callback_number"]),
                  "requests": "; ".join(b["special_requests"]), "allowed": self.allowed_phrase()}
        fields.update(extra)
        self.said.append(key)
        out.append(TEMPLATES[key].format(**fields))

    def allowed_phrase(self):
        parts = [window_phrase(self.brief["window"])]
        parts += [window_phrase(a) for a in self.brief["alternatives"]]
        return " or ".join(parts)

    def start(self):
        out = []
        self._say(out, "OPENING")
        return out

    # --- policy ---
    def classify_slot(self, slot):
        """Return (date, minutes, used_alternative) when bookable, else None."""
        if slot.date is None:
            return None
        windows = [(self.brief["window"], False)] + [(a, True) for a in self.brief["alternatives"]]
        for w, alt in windows:
            if slot.date != w["date"]:
                continue
            inside = [r for r in slot.readings if w["start"] <= r <= w["end"]]
            if len(inside) == 1:
                return (slot.date, inside[0], alt)
        return None

    def display_time(self, slot):
        if len(slot.readings) == 1:
            return fmt_time(slot.readings[0])
        hours = self.brief["business"]["hours"][DAY_KEYS[slot.date.weekday()]] if slot.date else []
        open_ = [r for r in slot.readings if any(o <= r < c for o, c in hours)]
        if len(open_) == 1:
            return fmt_time(open_[0])
        return "%s (am or pm not stated)" % fmt_hhmm(slot.readings[0])

    def record_alternative(self, slot):
        entry = {"date": slot.date.isoformat() if slot.date else None,
                 "time": self.display_time(slot), "stated": slot.stated}
        if entry not in self.alternatives:
            self.alternatives.append(entry)

    def _finish(self, out, end, template=None, **extra):
        if template:
            self._say(out, template, **extra)
        self.end, self.done = end, True

    def hear(self, text):
        """React to one business utterance. Returns the agent's lines.

        The steps run in a fixed order so a rule can never be skipped by an
        utterance that carries several intents at once.
        """
        out = []
        if self.done:
            return out
        h = understand(text, self.context_date, self.brief["window"]["date"], self.today)
        if h.dates and h.dates[-1] is not None:
            self.context_date = h.dates[-1]
        i = h.intents
        # 1. stop requests and refusals end the call at once
        if "do_not_call" in i:
            self._finish(out, "asked_not_to_call", "STOP_END")
            return out
        if "refuse_ai" in i:
            self._finish(out, "declined_ai_caller", "POLITE_END")
            return out
        # 2. asked if it is an AI: always yes, always who it calls for
        if "ask_ai" in i:
            self.asked_if_ai += 1
            self._say(out, "AI_ANSWER")
        bookable = [(s, self.classify_slot(s)) for s in h.slots]
        # 3. payment: decline, never agree, ask whether it can be booked without
        if ("ask_payment" in i or "payment_required" in i) and not ("payment_waived" in i and self.payment_open):
            for k in payment_kinds(text):
                if k not in self.payment_requests:
                    self.payment_requests.append(k)
            for s, ok in bookable:
                if ok:
                    self.pending = ok
                else:
                    self.record_alternative(s)
            if self.payment_open and "payment_required" in i:
                self.conditional, self.pending = self.pending, None
                self._finish(out, "payment_required", "PAYMENT_END")
                return out
            self.payment_open = True
            self._say(out, "PAYMENT_DECLINE")
            return out
        if self.payment_open:
            if "payment_waived" in i:
                self.payment_open = False
                if self.pending and not any(ok for _, ok in bookable):
                    self._say(out, "ACCEPT", date=fmt_date(self.pending[0]), time=fmt_time(self.pending[1]))
            elif "confirmed" not in i or "no_availability" in i or "goodbye" in i:
                self.conditional, self.pending = self.pending, None
                self._finish(out, "payment_required", "PAYMENT_END")
                return out
        # 4. offered times: accept only inside the window or a pre-approved alternative
        outside = []
        for s, ok in bookable:
            if ok:
                if self.pending != ok or "ACCEPT" not in self.said:
                    self.pending = ok
                    self._say(out, "ACCEPT", date=fmt_date(ok[0]), time=fmt_time(ok[1]))
            else:
                outside.append(s)
                self.record_alternative(s)
        if any(s.date is None for s in outside) and "ASK_DATE" not in self.said:
            self._say(out, "ASK_DATE")
        # 5. standard questions
        if "ask_name" in i:
            self._say(out, "GIVE_NAME")
        if "ask_party" in i and self.brief["party_size"] is not None:
            self._say(out, "GIVE_PARTY")
        if "ask_service" in i and self.brief["service"]:
            self._say(out, "GIVE_SERVICE")
        if "ask_callback" in i:
            self.callback_requested = True
            if self.brief["callback_number"]:
                self.callback_shared = True
                self._say(out, "GIVE_CALLBACK")
            else:
                self._say(out, "NO_CALLBACK")
        if "ask_requests" in i:
            self._say(out, "GIVE_REQUESTS" if self.brief["special_requests"] else "NO_REQUESTS")
        # 6. the business confirms: booked only the slot the agent accepted
        if "confirmed" in i and not outside:
            if h.confirmation:
                self.confirmation = h.confirmation
            if self.pending:
                self.booked = self.pending
                ref = (", confirmation number %s" % self.confirmation) if self.confirmation else ""
                self._finish(out, "booked", "CONFIRM_END", date=fmt_date(self.booked[0]),
                             time=fmt_time(self.booked[1]), ref=ref)
                return out
            self._say(out, "ASK_TIME")
            return out
        # 7. nothing in the window: ask once, collect what is offered, book nothing
        if not self.pending and ("no_availability" in i or outside):
            if outside or self.alternatives:
                if not self.asked_in_window:
                    self.asked_in_window = True
                    self._say(out, "ASK_IN_WINDOW")
                    return out
                self._finish(out, "not_available", "NOT_BOOKED_END")
                return out
            if not self.asked_other_times:
                self.asked_other_times = self.asked_in_window = True
                self._say(out, "ASK_OTHER_TIMES")
                return out
            self._finish(out, "not_available", "NOTHING_END")
            return out
        # 8. hold, goodbye, or not understood
        if "hold" in i and not out:
            self._say(out, "WAIT")
        if "goodbye" in i:
            self._finish(out, "not_available" if self.alternatives else "hung_up",
                         "NOT_BOOKED_END" if self.alternatives else None)
            return out
        if not out:
            self.unclear += 1
            if self.unclear > POLICY["max_unclear"]:
                self._finish(out, "unclear", "UNCLEAR_END")
            else:
                self._say(out, "REPEAT")
            return out
        if out == [TEMPLATES["AI_ANSWER"].format(name=self.brief["name"])]:
            self._say(out, "AI_CONTINUE")
        return out

    def hung_up(self):
        if not self.done:
            self.end, self.done = ("not_available" if self.alternatives else "hung_up"), True


def spoken_number(e164):
    """Example with a synthetic number: +15125550142 -> '512 555 0142'. US numbers only in this build."""
    if not e164:
        return None
    d = e164[2:]
    return "%s %s %s" % (d[:3], d[3:6], d[6:])


def payment_kinds(text):
    t = text.lower()
    kinds = []
    if re.search(r"\bcard\b", t):
        kinds.append("card details")
    if "deposit" in t:
        kinds.append("deposit")
    if re.search(r"pre-?pa(y|id)|pa(y|id) (now|upfront|up front|in advance|ahead)", t):
        kinds.append("prepayment")
    if re.search(r"cancellation fee|no-?show fee", t):
        kinds.append("cancellation fee")
    return kinds or ["payment"]


# ------------------------------------------------------------------- job ----
class ScriptedLine(object):
    """The simulation's only phone line: scripted business answers, one entry per attempt.

    SIMULATION ONLY. It keeps the dialogue so the harness can print and check
    it; the agent itself (CallSession, run_job's outcome) keeps no transcript.
    """

    def __init__(self, attempts):
        self.attempts = list(attempts)
        self.dialogue = []

    def dial(self, number, at_utc):
        if not self.attempts:
            raise ScenarioError("the scenario has no scripted answer for attempt %d" % (len(self.dialogue) + 1))
        return self.attempts.pop(0)


def run_job(brief, line, start_utc):
    """Run every permitted attempt against line. Returns the outcome record."""
    attempts, final, sessions = [], None, []
    t = next_allowed(brief, start_utc)
    if t is None:
        return outcome_record(brief, attempts, sessions, None, "no_call_window")
    while t is not None and len(attempts) < POLICY["max_attempts"]:
        script = line.dial(brief["business"]["phone"], t)
        rec = {"n": len(attempts) + 1, "at_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "at_local": _local(brief, t).strftime("%Y-%m-%d %H:%M %Z"), "result": script.get("result", "answered")}
        if rec["result"] not in RETRYABLE | {"answered"}:
            raise ScenarioError("unknown attempt result %r" % rec["result"])
        log = {"attempt": rec["n"], "result": rec["result"], "turns": []}
        line.dialogue.append(log)
        attempts.append(rec)
        if rec["result"] == "answered":
            session = CallSession(brief, today=_local(brief, t).date())
            sessions.append(session)
            for turn in script.get("turns", []):
                turn = {"say": turn} if isinstance(turn, str) else turn
                if turn.get("say"):
                    log["turns"].append(("business", turn["say"]))
                    lines = session.start() if len(log["turns"]) == 1 else session.hear(turn["say"])
                    log["turns"] += [("agent", l) for l in lines]
                if turn.get("hangup") and not session.done:
                    log["turns"].append(("business", "[hangs up]"))
                    session.hung_up()
                if session.done:
                    break
            if not session.done:
                session.end, session.done = "dropped", True
            rec.update({"ended": session.end,
                        "disclosed_ai_at_start": bool(session.said) and session.said[0] == "OPENING",
                        "asked_if_ai": session.asked_if_ai, "answered_ai_yes": session.said.count("AI_ANSWER"),
                        "said": list(session.said)})
            if session.end not in RETRYABLE:
                final = session
                break
        t = next_allowed(brief, t + dt.timedelta(minutes=POLICY["retry_gap_minutes"]))
    return outcome_record(brief, attempts, sessions, final, None)


def outcome_record(brief, attempts, sessions, final, reason):
    w = brief["window"]
    alternatives, payments = [], []
    for s in sessions:
        for a in s.alternatives:
            if dict(a, booked=False) not in alternatives:
                alternatives.append(dict(a, booked=False))
        for k in s.payment_requests:
            if k not in payments:
                payments.append(k)
    out = {
        "business": brief["business"]["name"],
        "requested": {"what": what_phrase(brief), "date": w["date"].isoformat(), "start": fmt_time(w["start"]),
                      "end": fmt_time(w["end"]), "name": brief["name"], "party_size": brief["party_size"],
                      "service": brief["service"],
                      "alternatives": [{"date": a["date"].isoformat(), "start": fmt_time(a["start"]), "end": fmt_time(a["end"])}
                                       for a in brief["alternatives"]]},
        "status": None, "reason": None, "booking": None,
        "alternatives_offered": alternatives,
        "payment_requests_declined": payments,
        "offered_only_with_payment": [{"date": s.conditional[0].isoformat(), "time": fmt_time(s.conditional[1])}
                                      for s in sessions if s.conditional],
        "callback": {"requested": any(s.callback_requested for s in sessions),
                     "shared": any(s.callback_shared for s in sessions)},
        "attempts": attempts,
        "kept": "Status, booking details, confirmation number, attempts and the alternatives offered. "
                "No recording, no transcript, no business speech is stored.",
    }
    if final is None:
        if reason:
            out["status"], out["reason"] = STATUS_NOT_BOOKED, reason
        elif any(a.get("ended") in ("unclear", "dropped") for a in attempts):
            out["status"], out["reason"] = STATUS_NOT_BOOKED, "unclear"
        else:
            out["status"] = STATUS_NO_ANSWER
        return out
    if final.end == "booked":
        d, minutes, alt = final.booked
        out["status"] = STATUS_BOOKED
        out["booking"] = {"date": d.isoformat(), "time": fmt_time(minutes), "name": brief["name"],
                          "party_size": brief["party_size"], "service": brief["service"],
                          "confirmation": final.confirmation, "used_pre_approved_alternative": alt}
    elif final.end == "not_available":
        out["status"] = STATUS_NOT_AVAILABLE
    else:
        out["status"], out["reason"] = STATUS_NOT_BOOKED, final.end
    return out


# ---------------------------------------------------------------- report ----
def render_report(outcome):
    r = outcome["requested"]
    L = ["# Booking report: %s" % outcome["business"], ""]
    L.append("**Status: %s**" % outcome["status"].upper())
    if outcome["reason"]:
        L.append("")
        L.append(REASONS.get(outcome["reason"], outcome["reason"]))
    L += ["", "Requested: %s on %s between %s and %s, under the name %s." % (r["what"], r["date"], r["start"], r["end"], r["name"])]
    if r["alternatives"]:
        L.append("Pre-approved alternatives: %s." % "; ".join("%s %s to %s" % (a["date"], a["start"], a["end"]) for a in r["alternatives"]))
    else:
        L.append("Pre-approved alternatives: none.")
    L += ["", "## Booking details", ""]
    b = outcome["booking"]
    if b:
        L += ["| Date | Time | Name | %s | Confirmation number |" % ("Party size" if b["party_size"] is not None else "Service"),
              "| --- | --- | --- | --- | --- |",
              "| %s | %s | %s | %s | %s |" % (b["date"], b["time"], b["name"], b["party_size"] if b["party_size"] is not None else b["service"],
                                            b["confirmation"] or "none given by the business")]
        if b["used_pre_approved_alternative"]:
            L += ["", "This booking uses one of the pre-approved alternatives from the brief, not the first-choice window."]
    else:
        L.append("Nothing was booked.")
    L += ["", "## Alternatives the business offered", ""]
    if outcome["alternatives_offered"]:
        for a in outcome["alternatives_offered"]:
            L.append("- %s at %s (as stated: \"%s\"). Not booked." % (a["date"] or "date not stated", a["time"], a["stated"]))
    else:
        L.append("None offered.")
    if outcome["payment_requests_declined"]:
        asked = ", ".join(outcome["payment_requests_declined"])
        L += ["", "## Payment requests", ""]
        if outcome["status"] == STATUS_BOOKED:
            L.append("The business asked for: %s. The agent declined and agreed to nothing, and the business booked without it. "
                     "Its own policy may still apply; check with the business before you go." % asked)
        else:
            L.append("The business asked for: %s. The agent declined, gave no payment details and agreed to no fee. "
                     "It does not ask you for payment details either; if you want to proceed, contact the business yourself." % asked)
        for c in outcome["offered_only_with_payment"]:
            L.append("- Offered only with that condition: %s at %s. Not booked." % (c["date"], c["time"]))
    if outcome["callback"]["requested"]:
        L += ["", "The business asked for a callback number: %s." % (
            "the number from your brief was given" if outcome["callback"]["shared"] else "none was shared")]
    L += ["", "## Every attempt", "", "| # | Time (business local) | Result | AI disclosed at start | Asked if AI | Answered yes |",
          "| --- | --- | --- | --- | --- | --- |"]
    for a in outcome["attempts"]:
        answered = "ended" in a
        L.append("| %d | %s | %s | %s | %s | %s |" % (
            a["n"], a["at_local"], a["result"] if not answered else "answered, " + a["ended"].replace("_", " "),
            ("yes" if a.get("disclosed_ai_at_start") else "no") if answered else "n/a",
            a.get("asked_if_ai", 0) if answered else "n/a", a.get("answered_ai_yes", 0) if answered else "n/a"))
    if not outcome["attempts"]:
        L.append("| - | no call placed | - | - | - | - |")
    L += ["", "## Next steps", "", next_steps(outcome), "", "## What was kept", "", outcome["kept"]]
    return "\n".join(L) + "\n"


def next_steps(outcome):
    s = outcome["status"]
    if s == STATUS_BOOKED:
        return ("The booking is yours to keep or cancel. The agent does not cancel or change bookings; "
                "contact the business directly to do that.")
    if s == STATUS_NOT_AVAILABLE:
        return ("Nothing was booked. If one of the offered times suits you, book it directly, or hire the agent again "
                "with that time listed as a pre-approved alternative.")
    if s == STATUS_NO_ANSWER:
        return "The business did not answer within the attempt limit. Try another business or a later date."
    return "Nothing was booked. See the reason above."


# ------------------------------------------------------------ invariants ----
def check_invariants(brief, outcome, dialogue, script_texts):
    """Rules that must hold in every simulated job. Returns a list of failures."""
    fails = []
    attempts = outcome["attempts"]
    if len(attempts) > POLICY["max_attempts"]:
        fails.append("more attempts than the limit: %d" % len(attempts))
    for a in attempts:
        t = dt.datetime.strptime(a["at_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        if not call_allowed(brief, t):
            fails.append("attempt %d placed outside opening or calling hours" % a["n"])
        if "said" in a:
            if not a["said"] or a["said"][0] != "OPENING":
                fails.append("attempt %d did not open with the AI disclosure" % a["n"])
            if a["asked_if_ai"] != a["answered_ai_yes"]:
                fails.append("attempt %d: asked if AI %d times, answered yes %d times" % (a["n"], a["asked_if_ai"], a["answered_ai_yes"]))
    for log in dialogue:
        for who, text in log["turns"]:
            if who != "agent":
                continue
            if re.search(r"\d{4}[ -]?\d{4}[ -]?\d{4}", text):
                fails.append("agent spoke a card-like number: %r" % text)
            if re.search(r"\b(i'?m|i am) (not an? (ai|robot|bot|machine)|a (real )?(person|human))\b", text, re.I):
                fails.append("agent denied being an AI: %r" % text)
            if re.search(r"\b(i|we) (agree|accept)\b[^.]*\b(deposit|fee|prepayment|card)\b", text, re.I):
                fails.append("agent agreed to a payment term: %r" % text)
            if not brief["callback_number"] and re.search(r"\+?\d[\d -]{9,}", text):
                fails.append("agent shared a number with no approved callback: %r" % text)
    if outcome["status"] == STATUS_BOOKED:
        b = outcome["booking"]
        if not (b and b["date"] and b["time"] and b["name"]):
            fails.append("booked without date, time or name")
        else:
            d = dt.date.fromisoformat(b["date"])
            minutes = _parse_ampm(b["time"])
            windows = [brief["window"]] + brief["alternatives"]
            if not any(w["date"] == d and w["start"] <= minutes <= w["end"] for w in windows):
                fails.append("booked %s %s outside the window and the alternatives" % (b["date"], b["time"]))
    for a in outcome["alternatives_offered"]:
        if a["booked"]:
            fails.append("an offered alternative is marked booked")
    blob = json.dumps(outcome).lower()
    for text in script_texts:
        if len(text) > 25 and text.lower() in blob:
            fails.append("outcome stores business speech: %r" % text)
    return fails


def _parse_ampm(text):
    m = re.fullmatch(r"(\d{1,2}):(\d{2}) (am|pm)", text)
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0)
    return h * 60 + int(m.group(2))


# -------------------------------------------------------------- scenario ----
def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def run_scenario(scn, base_dir="."):
    brief_raw = scn["brief"] if isinstance(scn["brief"], dict) else load_json(os.path.join(base_dir, scn["brief"]))
    brief = validate_brief(brief_raw)
    start = dt.datetime.strptime(scn["start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    line = ScriptedLine(scn["attempts"])
    outcome = run_job(brief, line, start)
    texts = [t if isinstance(t, str) else t.get("say", "") for a in scn["attempts"] for t in a.get("turns", [])]
    fails = check_invariants(brief, outcome, line.dialogue, texts)
    fails += check_expect(outcome, scn.get("expect", {}), line.dialogue)
    return brief, outcome, line.dialogue, fails


def check_expect(outcome, expect, dialogue):
    fails = []
    for key in ("status", "reason"):
        if key in expect and outcome[key] != expect[key]:
            fails.append("expected %s %r, got %r" % (key, expect[key], outcome[key]))
    if "booking" in expect:
        got = outcome["booking"] or {}
        for k, v in expect["booking"].items():
            if got.get(k) != v:
                fails.append("expected booking.%s %r, got %r" % (k, v, got.get(k)))
    if "alternatives" in expect:
        got = [(a["date"], a["time"]) for a in outcome["alternatives_offered"]]
        want = [tuple(x) for x in expect["alternatives"]]
        if got != want:
            fails.append("expected alternatives %r, got %r" % (want, got))
    if "payment_requests_declined" in expect and outcome["payment_requests_declined"] != expect["payment_requests_declined"]:
        fails.append("expected payment requests %r, got %r" % (expect["payment_requests_declined"], outcome["payment_requests_declined"]))
    if "attempt_results" in expect:
        got = [a["result"] if "ended" not in a else "answered:" + a["ended"] for a in outcome["attempts"]]
        if got != expect["attempt_results"]:
            fails.append("expected attempts %r, got %r" % (expect["attempt_results"], got))
    said = [k for a in outcome["attempts"] for k in a.get("said", [])]
    for key in expect.get("agent_said", []):
        if key not in said:
            fails.append("agent never said %s" % key)
    for key in expect.get("agent_never_said", []):
        if key in said:
            fails.append("agent said %s" % key)
    return fails


def render_dialogue(dialogue):
    L = ["## Simulated dialogue (SYNTHETIC script; simulation output only, the live agent keeps no transcript)", ""]
    for log in dialogue:
        L.append("Attempt %d: %s" % (log["attempt"], log["result"]))
        for who, text in log["turns"]:
            L.append("  %s: %s" % ("Business" if who == "business" else "Agent", text))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------- cli ----
def main(argv=None, stdout=sys.stdout, stderr=sys.stderr):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["call"]:
        print("error: call: refused. This build has no telephony provider, account or number; it places no calls. "
              "Live calling is an owner decision at award time. No call was placed.", file=stderr)
        return 2
    ap = argparse.ArgumentParser(prog="call_for_me.py", description="Call-for-Me Booking agent (design and simulation stage)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--brief", required=True)
    p = sub.add_parser("plan"); p.add_argument("--brief", required=True); p.add_argument("--start", required=True)
    s = sub.add_parser("simulate"); s.add_argument("scenarios", nargs="+")
    s.add_argument("--json", action="store_true"); s.add_argument("--dialogue", action="store_true")
    sub.add_parser("call", help="always refuses: no telephony in this build")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "check":
            print(confirmed_brief_text(validate_brief(load_json(args.brief))), file=stdout)
            return 0
        if args.cmd == "plan":
            brief = validate_brief(load_json(args.brief))
            start = dt.datetime.strptime(args.start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            times = plan_attempts(brief, start)
            if not times:
                print("No permitted call time before the deadline %s." % call_deadline(brief).strftime("%Y-%m-%dT%H:%M:%SZ"), file=stdout)
            for i, t in enumerate(times, 1):
                print("attempt %d: %s (%s)" % (i, t.strftime("%Y-%m-%dT%H:%M:%SZ"), _local(brief, t).strftime("%a %Y-%m-%d %H:%M %Z")), file=stdout)
            return 0
        failed = 0
        for path in args.scenarios:
            scn = load_json(path)
            brief, outcome, dialogue, fails = run_scenario(scn, os.path.dirname(os.path.abspath(path)))
            print("<!-- scenario: %s (%s) -->" % (os.path.basename(path), scn.get("label", "")), file=stdout)
            if args.json:
                print(json.dumps(outcome, indent=2), file=stdout)
            else:
                print(render_report(outcome), file=stdout)
            if args.dialogue:
                print(render_dialogue(dialogue), file=stdout)
            for f in fails:
                print("FAIL %s: %s" % (os.path.basename(path), f), file=stdout)
            print("%s %s" % ("FAIL" if fails else "PASS", os.path.basename(path)), file=stdout)
            failed += bool(fails)
        return 1 if failed else 0
    except (BriefError, ScenarioError, OSError, ValueError, KeyError) as exc:
        print("error: %s: %s. No report emitted." % (args.cmd, exc), file=stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
