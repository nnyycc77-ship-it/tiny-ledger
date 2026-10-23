#!/usr/bin/env python3
"""Field Service Route Planner and Schedule Backfill agent (issue #73).

Built ahead of any award for the NEAR Agent Market job "Field Service Route
Planner & Schedule Backfill" (job 5b3baff9-bb38-4a0f-9c52-89cf54af95b6,
description quoted on issue #73). One run takes three CSV files the buyer
provides (jobs, crew, customers), a planning period (one day, or a range of
days when the jobs carry a date column), and a routing provider, and writes
one Markdown report:

  1. the schedule per crew member per day, respecting working hours, time
     windows and skills, built by the documented insertion heuristic;
  2. the total drive time, compared with visiting the same jobs in the
     order the file gave them;
  3. the gaps left in each finished day, with the crew member, time and
     the area (where the crew member is before and after the gap);
  4. ranked backfill suggestions for those gaps, drawn from the customer
     list, each with its reason and a certainty label, and each checked so
     that every later job of that day stays inside its time window;
  5. one outreach draft per suggestion, for the buyer to send or not.

Rules that bind this agent (job description and task issue): it never
contacts the buyer's customers, it only drafts; it never suggests a
customer whose do not contact flag is set; an address the geocoder cannot
place is reported as a data problem and never guessed; a missing last
service date falls back on the stated service plan's interval and the
suggestion is labelled assumption based; hard exclusions are applied
before ranking; every suggestion carries its reason and a certainty label;
only customers due according to the data are suggested, unless the buyer
widens the window with --lookahead-days, in which case the report marks
every not yet due suggestion as such.

Fail closed: a missing file, a missing column, or a provider failure
stops the run with the reason on stderr and exit 2; no partial report is
written. A row with an unusable field (a bad time, a bad date, a bad
duration) is dropped from planning and listed under data problems in the
report, with the row and the field named; a dropped jobs row is also listed
under a day's unassigned jobs with that reason, so no job is missing from
both the schedule and the unassigned list.

Standard library only. Run from the repository root:

    python3 agents/field-service-planner/planner.py plan --date 2026-11-03 \
        --jobs jobs.csv --crew crew.csv --customers customers.csv \
        --places agents/field-service-planner/tests/fixtures/places.json \
        --out report.md

`--places FILE` uses the offline fixture provider (no network); `--live`
uses the open routing services through routing.LiveProvider, which needs
the environment variable FIELD_PLANNER_CONTACT. Exactly one of the two.
`--date-to` extends the period; the jobs file then needs a `date` column.
Input column names and formats are listed in README.md.
"""

import argparse
import csv
import datetime as dt
import difflib
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import routing  # noqa: E402

AGENT_NAME = "Field Service Route Planner & Schedule Backfill"
AGENT_VERSION = "0.3.0"

JOB_COLUMNS = ("job_id", "customer", "address", "duration_minutes", "window_start", "window_end", "skills")
JOB_DATE_COLUMN = "date"                      # optional; required with --date-to
CREW_COLUMNS = ("crew_id", "name", "start_address", "shift_start", "shift_end", "skills")
CUSTOMER_COLUMNS = ("customer_id", "name", "address", "last_service_date", "service_plan", "do_not_contact")
CUSTOMER_QUOTE_COLUMN = "open_quote"          # optional
CUSTOMER_TYPE_COLUMN = "service_type"         # optional; a typical interval when service_plan is blank
CUSTOMER_OPTOUT_COLUMN = "opted_out"          # optional; a hard exclusion like do_not_contact
CUSTOMER_OPTIONAL = (CUSTOMER_QUOTE_COLUMN, CUSTOMER_TYPE_COLUMN, CUSTOMER_OPTOUT_COLUMN)

PLAN_INTERVALS = {"weekly": 7, "biweekly": 14, "monthly": 30, "bimonthly": 61, "quarterly": 91,
                  "semiannual": 182, "annual": 365, "yearly": 365}
# Stated assumptions, used only when a customer's service_plan is blank: a
# typical interval by service type (the bid proposal's examples are HVAC twice
# a year and pest control quarterly). Every suggestion built on one of these is
# labelled assumption based and ranks below customers with real due evidence.
TYPICAL_INTERVALS = {"hvac": 182, "pest control": 91, "pest": 91, "cleaning": 30, "landscaping": 30,
                     "lawn care": 30, "plumbing": 365, "electrical": 365, "window cleaning": 91, "pool": 30}
NAME_SIMILARITY = 0.80        # SequenceMatcher ratio on normalized names for a duplicate at the same address
EVERY_N_DAYS = re.compile(r"^every\s+(\d+)\s+days?$")
TRUE_WORDS = ("yes", "y", "true", "1")
FALSE_WORDS = ("no", "n", "false", "0", "")

DEFAULT_MIN_GAP = 30          # minutes of idle time before a gap is reported
DEFAULT_VISIT = 60            # assumed minutes for a backfill visit
DEFAULT_LOOKAHEAD = 0         # days: only customers due on or before the day are suggested unless the buyer widens this
DEFAULT_PER_GAP = 3
CONFIDENCE_BONUS = {"high": 0.2, "medium": 0.1, "low": 0.0}
DRIVE_WEIGHT_PER_HOUR = 0.5   # score lost per hour of added drive time
RANK_NOTE = ("Ranking: two tiers. Every pair with real due evidence (a recorded last service date with a stated plan, "
             "or an open quote) is taken before any assumption based pair, whatever the scores. Within a tier, score = "
             "due_strength - added_drive_hours * %.1f + confidence bonus (high %.1f, medium %.1f, low %.1f), computed "
             "for every gap in the period a customer fits; the pairs are taken best first (ties by less added drive "
             "time, then customer id, then the earlier gap), each customer once in the whole period and at most the "
             "configured number of suggestions per gap, so a customer lands in the gap where it scores best rather "
             "than the first gap of the period."
             % (DRIVE_WEIGHT_PER_HOUR, CONFIDENCE_BONUS["high"], CONFIDENCE_BONUS["medium"], CONFIDENCE_BONUS["low"]))
SEQUENCE_NOTE = ("Cheapest feasible insertion: jobs in order of window end (then window start, then longer first); each "
                 "is inserted at the position, on the eligible crew member, that adds the least drive time while every "
                 "window and every shift stays feasible. Ties go to the crew member with fewer stops, then the lower "
                 "crew id. A job with no eligible crew member or no feasible slot is listed as unassigned with the "
                 "reason. Insertion is greedy, so the result is a feasible schedule, not a proven optimum.")
GAP_NOTE = ("Idle time in each finished day: before the first stop, between stops after the drive is taken out, and "
            "after the last stop until the shift ends. A gap is reported when at least the minimum free minutes "
            "remain. Each gap names where the crew member is before it and where they must be next (the area), so a "
            "backfill is costed by added drive time and checked against the next job's planned start.")


class InputError(Exception):
    """A file level problem. Nothing is planned, no report is written."""


# ---------------------------------------------------------------- parsing

def parse_hhmm(value, what):
    m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*$", value or "")
    if not m or int(m.group(1)) > 24 or int(m.group(2)) > 59:
        raise ValueError("%s must be HH:MM (24 hour), got %r" % (what, value))
    minutes = int(m.group(1)) * 60 + int(m.group(2))
    if minutes > 24 * 60:
        raise ValueError("%s must be at most 24:00, got %r" % (what, value))
    return minutes


def fmt_hhmm(minutes):
    minutes = int(round(minutes))
    return "%02d:%02d" % divmod(minutes, 60)


def parse_date(value, what):
    try:
        return dt.date.fromisoformat((value or "").strip())
    except ValueError:
        raise ValueError("%s must be YYYY-MM-DD, got %r" % (what, value))


def parse_skills(value):
    return frozenset(s.strip().lower() for s in (value or "").split(";") if s.strip())


def parse_flag(value, what):
    v = (value or "").strip().lower()
    if v in TRUE_WORDS:
        return True
    if v in FALSE_WORDS:
        return False
    raise ValueError("%s must be yes or no, got %r" % (what, value))


def parse_plan(value):
    """Service plan -> interval in days. Known words or 'every N days'."""
    v = (value or "").strip().lower()
    if v in PLAN_INTERVALS:
        return PLAN_INTERVALS[v]
    m = EVERY_N_DAYS.match(v)
    if m and int(m.group(1)) > 0:
        return int(m.group(1))
    raise ValueError("service_plan must be one of %s or 'every N days', got %r" % (", ".join(sorted(PLAN_INTERVALS)), value))


def norm_text(s):
    """Lower case, punctuation removed, whitespace collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def normalize_key(name, address):
    """Exact dedupe key: normalized name plus normalized address."""
    return norm_text(name) + "|" + norm_text(address)


def similar_customers(a, b):
    """The proposal's duplicate rule: the same normalized address and names
    that are equal or similar (SequenceMatcher ratio at least NAME_SIMILARITY)
    after normalization. Returns the ratio when they match, else None."""
    if norm_text(a.address) != norm_text(b.address):
        return None
    na, nb = norm_text(a.name), norm_text(b.name)
    if na == nb:
        return 1.0
    ratio = difflib.SequenceMatcher(None, na, nb).ratio()
    return ratio if ratio >= NAME_SIMILARITY else None


def read_csv(path, columns, what, optional=()):
    """Rows as (line number, dict). Returns (rows, present optional columns)."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise InputError("%s file %s is empty" % (what, path))
            fields = [f.strip() for f in reader.fieldnames]
            missing = [c for c in columns if c not in fields]
            if missing:
                raise InputError("%s file %s lacks column(s): %s (has: %s)" % (what, path, ", ".join(missing), ", ".join(fields)))
            rows = []
            for number, row in enumerate(reader, start=2):
                rows.append((number, {k.strip(): (v or "").strip() for k, v in row.items() if k is not None}))
    except OSError as exc:
        raise InputError("cannot read %s file %s: %s" % (what, path, exc))
    return rows, [c for c in optional if c in fields]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- records

class Job(object):
    def __init__(self, row, number):
        self.row = number
        self.id = row["job_id"]
        self.customer = row["customer"]
        self.address = row["address"]
        try:
            self.duration = int(row["duration_minutes"])
        except ValueError:
            raise ValueError("duration_minutes must be an integer, got %r" % row["duration_minutes"])
        if self.duration <= 0:
            raise ValueError("duration_minutes must be positive, got %r" % row["duration_minutes"])
        self.window = (parse_hhmm(row["window_start"], "window_start"), parse_hhmm(row["window_end"], "window_end"))
        if self.window[0] >= self.window[1]:
            raise ValueError("window_start %s must be before window_end %s" % (row["window_start"], row["window_end"]))
        self.skills = parse_skills(row["skills"])
        self.date = parse_date(row[JOB_DATE_COLUMN], JOB_DATE_COLUMN) if row.get(JOB_DATE_COLUMN) else None
        if not self.id:
            raise ValueError("job_id must not be blank")
        if not self.address:
            raise ValueError("address must not be blank")
        self.place = None


class Crew(object):
    def __init__(self, row, number):
        self.row = number
        self.id = row["crew_id"]
        self.name = row["name"] or row["crew_id"]
        self.start_address = row["start_address"]
        self.shift = (parse_hhmm(row["shift_start"], "shift_start"), parse_hhmm(row["shift_end"], "shift_end"))
        if self.shift[0] >= self.shift[1]:
            raise ValueError("shift_start %s must be before shift_end %s" % (row["shift_start"], row["shift_end"]))
        self.skills = parse_skills(row["skills"])
        if not self.id:
            raise ValueError("crew_id must not be blank")
        if not self.start_address:
            raise ValueError("start_address must not be blank")
        self.place = None


class Customer(object):
    def __init__(self, row, number):
        self.row = number
        self.id = row["customer_id"]
        self.name = row["name"]
        self.address = row["address"]
        self.last_service = parse_date(row["last_service_date"], "last_service_date") if row["last_service_date"] else None
        self.plan_text = row["service_plan"]
        self.service_type = row.get(CUSTOMER_TYPE_COLUMN, "")
        self.interval = None
        self.interval_assumed = False
        if self.plan_text:
            self.interval = parse_plan(self.plan_text)
        elif norm_text(self.service_type) in TYPICAL_INTERVALS:
            self.interval = TYPICAL_INTERVALS[norm_text(self.service_type)]
            self.interval_assumed = True
        elif self.service_type:
            raise ValueError("service_plan is blank and service_type %r has no typical interval (known: %s)"
                             % (self.service_type, ", ".join(sorted(TYPICAL_INTERVALS))))
        self.do_not_contact = parse_flag(row["do_not_contact"], "do_not_contact")
        self.opted_out = parse_flag(row.get(CUSTOMER_OPTOUT_COLUMN, ""), CUSTOMER_OPTOUT_COLUMN)
        self.open_quote = row.get(CUSTOMER_QUOTE_COLUMN, "")
        self.merged_from = []   # duplicate rows folded into this record, with the ratio
        if not self.id:
            raise ValueError("customer_id must not be blank")
        if not self.address:
            raise ValueError("address must not be blank")
        self.place = None

    @property
    def key(self):
        return normalize_key(self.name, self.address)

    @property
    def richness(self):
        """How many fields that matter for backfill are filled; the richest
        record is kept when duplicates merge (the proposal's rule)."""
        return sum(1 for v in (self.last_service, self.plan_text, self.open_quote, self.service_type) if v)

    @property
    def plan_label(self):
        if self.plan_text:
            return "%s plan" % self.plan_text
        return "typical %s interval" % self.service_type

    def merge_from(self, other, ratio):
        """Fold a duplicate into this record: fill blanks from it, carry its
        exclusions, and remember the merge for the report."""
        if self.last_service is None and other.last_service is not None:
            self.last_service = other.last_service
        if not self.plan_text and other.plan_text:
            self.plan_text, self.interval, self.interval_assumed = other.plan_text, other.interval, False
        if self.interval is None and other.interval is not None:
            self.interval, self.interval_assumed = other.interval, other.interval_assumed
        if not self.service_type and other.service_type:
            self.service_type = other.service_type
        if not self.open_quote and other.open_quote:
            self.open_quote = other.open_quote
        self.do_not_contact = self.do_not_contact or other.do_not_contact
        self.opted_out = self.opted_out or other.opted_out
        self.merged_from.append((other, ratio))


def load_records(rows, cls, label, problems, dropped=None):
    out = []
    for number, row in rows:
        try:
            out.append(cls(row, number))
        except ValueError as exc:
            ident = row.get("job_id") or row.get("crew_id") or row.get("customer_id") or "(no id)"
            problems.append("%s row %d (%s) dropped: %s" % (label, number, ident, exc))
            if dropped is not None:
                dropped.append(DroppedJob(number, ident, row.get("customer", ""), row.get("address", ""),
                                          row.get(JOB_DATE_COLUMN, ""), str(exc)))
    return out


class DroppedJob(object):
    """A jobs row that was not planned: it could not be read, or its date
    is blank or outside the period. It is listed under the unassigned jobs
    of a day as well as under data problems (job posting acceptance 1)."""

    def __init__(self, row, job_id, customer, address, raw_date, reason):
        self.row = row
        self.id = job_id
        self.customer = customer
        self.address = address
        self.reason = reason
        try:
            self.date = parse_date(raw_date, JOB_DATE_COLUMN) if (raw_date or "").strip() else None
        except ValueError:
            self.date = None


# ---------------------------------------------------------------- settings

class Settings(object):
    def __init__(self, min_gap=DEFAULT_MIN_GAP, visit=DEFAULT_VISIT, lookahead=DEFAULT_LOOKAHEAD, per_gap=DEFAULT_PER_GAP):
        for name, value in (("--min-gap-minutes", min_gap), ("--visit-minutes", visit),
                            ("--lookahead-days", lookahead), ("--suggestions-per-gap", per_gap)):
            if value < 0:
                raise InputError("%s must not be negative" % name)
        self.min_gap = min_gap
        self.visit = visit
        self.lookahead = lookahead
        self.per_gap = per_gap


# ---------------------------------------------------------------- the period

class Period(object):
    """Everything shared across the days of one run: the placed records, the
    drive time table, the customer exclusions, and which customers have
    already been suggested."""

    def __init__(self, dates, jobs, crew, customers, provider, settings):
        self.dates = list(dates)
        self.jobs = jobs
        self.crew = crew
        self.customers = customers
        self.provider = provider
        self.settings = settings
        self.problems = []
        self.drive = {}
        self.geocoded_utc = None
        self.excluded = []
        self.candidates = []
        self.used = set()
        self.days = []
        self.dropped_jobs = []

    # ---- geocoding and the drive time matrix

    def place_everything(self):
        self.geocoded_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache = {}

        def place(address):
            if address not in cache:
                cache[address] = self.provider.geocode(address)
            return cache[address]

        for job in self.jobs:
            job.place = place(job.address)
            if job.place is None:
                self.problems.append("job %s: address %r could not be placed by the geocoder; the job is not scheduled" % (job.id, job.address))
        for member in self.crew:
            member.place = place(member.start_address)
            if member.place is None:
                self.problems.append("crew %s: start address %r could not be placed; no route is built for this crew member" % (member.id, member.start_address))
        for customer in self.customers:
            customer.place = place(customer.address)
            if customer.place is None:
                self.problems.append("customer %s: address %r could not be placed; not considered for backfill" % (customer.id, customer.address))
        placed, seen = [], set()
        for p in [x.place for x in self.jobs + self.crew + self.customers if x.place is not None]:
            if p.key() not in seen:
                seen.add(p.key())
                placed.append(p)
        table = self.provider.matrix(placed)
        if len(table) != len(placed) or any(len(r) != len(placed) for r in table):
            raise routing.RoutingError("drive time matrix is not %d by %d" % (len(placed), len(placed)))
        for i, a in enumerate(placed):
            for j, b in enumerate(placed):
                self.drive[(a.key(), b.key())] = table[i][j] / 60.0  # minutes

    def minutes(self, a, b):
        return self.drive[(a.key(), b.key())]

    # ---- customers: due arithmetic and the hard exclusions

    def due(self, customer, date):
        """(due_strength, assumption_based, note) on `date`. Strength 1.0 means
        a full interval overdue; negative means not yet due."""
        if customer.open_quote:
            return 1.0, False, "open quote on record (%s); treated as due" % customer.open_quote
        if customer.last_service is None:
            return 1.0, True, ("assumption based: no last service date recorded, so the %s (%d day interval) is treated "
                               "as one full interval elapsed" % (customer.plan_label, customer.interval))
        next_due = customer.last_service + dt.timedelta(days=customer.interval)
        overdue = (date - next_due).days
        assumed = customer.interval_assumed
        if overdue >= 0:
            note = "due since %s (%s, last service %s), %d day(s) overdue on %s" % (
                next_due.isoformat(), customer.plan_label, customer.last_service.isoformat(), overdue, date.isoformat())
        else:
            note = "not yet due: due on %s (%s, last service %s), %d day(s) after %s" % (
                next_due.isoformat(), customer.plan_label, customer.last_service.isoformat(), -overdue, date.isoformat())
        if assumed:
            note = "assumption based: no service plan stated, the %s of %d days is applied; %s" % (customer.plan_label, customer.interval, note)
        return overdue / float(customer.interval), assumed, note

    def exclude_customers(self):
        """Hard exclusions, in this order, before any ranking: duplicate
        (merged into the richest record, flagged); do not contact or opted
        out; address not placed; no plan or type to judge due by; already has
        a job in the period; not due within the lookahead window (measured
        from the last day of the period). The rest are candidates."""
        scheduled = {normalize_key(j.customer, j.address) for j in self.jobs}
        last_day = self.dates[-1]
        kept = []
        for c in sorted(self.customers, key=lambda c: c.row):
            match = None
            for k in kept:
                ratio = similar_customers(k, c)
                if ratio is not None:
                    match = (k, ratio)
                    break
            if match is None:
                kept.append(c)
                continue
            k, ratio = match
            if c.richness > k.richness:
                # the later row is richer: it becomes the kept record and absorbs the earlier one
                kept[kept.index(k)] = c
                c.merge_from(k, ratio)
                self.excluded.append((k, "duplicate of customer %s (same address, name similarity %.2f): merged into %s, "
                                      "which has more filled fields" % (c.id, ratio, c.id)))
            else:
                k.merge_from(c, ratio)
                self.excluded.append((c, "duplicate of customer %s (same address, name similarity %.2f): merged into %s"
                                      % (k.id, ratio, k.id)))
        for c in kept:
            key = c.key
            if c.do_not_contact or c.opted_out:
                flags = [f for f, v in (("do not contact", c.do_not_contact), ("opted out", c.opted_out)) if v]
                self.excluded.append((c, "%s flag is set%s" % (" and ".join(flags), self.merge_note(c))))
                continue
            if c.place is None:
                self.excluded.append((c, "address could not be placed" + self.merge_note(c)))
                continue
            if c.interval is None and not c.open_quote:
                self.excluded.append((c, "no service plan, no known service type and no open quote: due date cannot be judged" + self.merge_note(c)))
                continue
            if key in scheduled:
                self.excluded.append((c, "already has a job in the planning period" + self.merge_note(c)))
                continue
            strength, assumed, note = self.due(c, last_day)
            if strength < 0 and (-strength * c.interval) > self.settings.lookahead:
                if self.settings.lookahead:
                    self.excluded.append((c, "not due within %d days of %s: %s%s" % (self.settings.lookahead, last_day.isoformat(), note, self.merge_note(c))))
                else:
                    self.excluded.append((c, "%s%s" % (note, self.merge_note(c))))
                continue
            self.candidates.append(c)

    @staticmethod
    def merge_note(c):
        if not c.merged_from:
            return ""
        return "; merged duplicate row(s): %s" % ", ".join("%s (name similarity %.2f)" % (o.id, r) for o, r in c.merged_from)

    def rank(self):
        """Backfill across the whole period (RANK_NOTE): score every
        (candidate, gap) pair that fits, then assign best first."""
        pairs = []
        for day_index, day in enumerate(self.days):
            for gap_index, gap in enumerate(day.gaps):
                for c in self.candidates:
                    scored = day.score(gap, c)
                    if scored is not None:
                        pairs.append((scored, day_index, gap_index, gap, c))
        # assumption based pairs (tier 1) always sort after evidence based pairs (tier 0): the proposal's rule
        pairs.sort(key=lambda item: (1 if item[0]["assumed"] else 0, -item[0]["score"], item[0]["added"], item[4].id, item[1], item[2]))
        count = {}
        for scored, day_index, gap_index, gap, c in pairs:
            if c.id in self.used or count.get(id(gap), 0) >= self.settings.per_gap:
                continue
            self.used.add(c.id)
            count[id(gap)] = count.get(id(gap), 0) + 1
            self.days[day_index].suggestions.append(Suggestion(gap, 0, c, **scored))
        for day in self.days:
            order = {id(g): i for i, g in enumerate(day.gaps)}
            day.suggestions.sort(key=lambda sg: (order[id(sg.gap)], 1 if sg.assumed else 0, -sg.score, sg.added, sg.customer.id))
            rank, current = 0, None
            for sg in day.suggestions:
                rank = rank + 1 if sg.gap is current else 1
                current = sg.gap
                sg.rank = rank

    def run(self):
        self.place_everything()
        self.exclude_customers()
        for date in self.dates:
            jobs = [j for j in self.jobs if j.date is None or j.date == date]
            day = Day(self, date, jobs)
            # A dropped row goes on its own day when its date is readable and
            # in the period, otherwise on the first day, so each is listed once.
            day.dropped = [d for d in self.dropped_jobs
                           if d.date == date or (date == self.dates[0] and d.date not in self.dates)]
            self.days.append(day.run())
        self.rank()
        return self

    @property
    def suggestions(self):
        return [s for day in self.days for s in day.suggestions]


# ---------------------------------------------------------------- one day

class Stop(object):
    def __init__(self, job, drive, arrive, start, end):
        self.job = job
        self.drive = drive      # minutes from the previous location
        self.arrive = arrive    # minutes since midnight
        self.start = start
        self.end = end


class Gap(object):
    def __init__(self, day, member, start, end, free, prev_place, prev_label, next_place, next_label):
        self.day = day
        self.member = member
        self.start = start
        self.end = end
        self.free = free
        self.prev_place = prev_place
        self.prev_label = prev_label
        self.next_place = next_place
        self.next_label = next_label


class Suggestion(object):
    def __init__(self, gap, rank, customer, score, added, arrive, back_by, reason, certainty, assumed, not_yet_due):
        self.gap = gap
        self.rank = rank
        self.customer = customer
        self.score = score
        self.added = added
        self.arrive = arrive
        self.back_by = back_by
        self.reason = reason
        self.certainty = certainty
        self.assumed = assumed
        self.not_yet_due = not_yet_due


class Day(object):
    def __init__(self, period, date, jobs):
        self.period = period
        self.date = date
        self.jobs = jobs
        self.crew = period.crew
        self.settings = period.settings
        self.routes = {}
        self.unassigned = []
        self.dropped = []
        self.gaps = []
        self.suggestions = []
        self.baseline = None

    def minutes(self, a, b):
        return self.period.minutes(a, b)

    # ---- sequencing: cheapest feasible insertion (SEQUENCE_NOTE)

    def timeline(self, member, route):
        """Drive the route from the crew start at shift start. Returns
        (stops, total_drive_minutes) or None when a window or the shift is
        missed."""
        t, here, stops, total = member.shift[0], member.place, [], 0.0
        for job in route:
            drive = self.minutes(here, job.place)
            arrive = t + drive
            start = max(arrive, job.window[0])
            if start > job.window[1]:
                return None
            end = start + job.duration
            if end > member.shift[1]:
                return None
            stops.append(Stop(job, drive, arrive, start, end))
            total += drive
            t, here = end, job.place
        return stops, total

    def sequence(self):
        able = [m for m in self.crew if m.place is not None]
        routes = {m.id: [] for m in able}
        totals = {m.id: 0.0 for m in able}
        for job in sorted(self.jobs, key=lambda j: (j.window[1], j.window[0], -j.duration, j.id)):
            if job.place is None:
                self.unassigned.append((job, "address could not be placed"))
                continue
            eligible = [m for m in able if job.skills <= m.skills]
            if not eligible:
                self.unassigned.append((job, "no crew member with a placed start address has the skills: %s"
                                        % (", ".join(sorted(job.skills)) or "(none required)")))
                continue
            best = None
            for m in sorted(eligible, key=lambda m: (len(routes[m.id]), m.id)):
                route = routes[m.id]
                for pos in range(len(route) + 1):
                    trial = route[:pos] + [job] + route[pos:]
                    result = self.timeline(m, trial)
                    if result is None:
                        continue
                    added = result[1] - totals[m.id]
                    if best is None or added < best[0] - 1e-9:
                        best = (added, m, trial, result[1])
            if best is None:
                self.unassigned.append((job, "no feasible slot: every insertion misses the time window or the crew member's hours"))
                continue
            _, m, trial, total = best
            routes[m.id] = trial
            totals[m.id] = total
        for m in able:
            self.routes[m.id] = self.timeline(m, routes[m.id])
        # Baseline for the comparison the job description asks for: the same
        # jobs on the same crew member, visited in the order the file gave
        # them, drive time only (windows and hours not checked).
        baseline = 0.0
        for m in able:
            here = m.place
            for job in sorted(routes[m.id], key=lambda j: j.row):
                baseline += self.minutes(here, job.place)
                here = job.place
        self.baseline = baseline

    @property
    def total_drive(self):
        return sum(total for _, total in self.routes.values())

    # ---- gaps (GAP_NOTE)

    def find_gaps(self):
        for member in self.crew:
            if member.id not in self.routes:
                continue
            stops, _ = self.routes[member.id]
            prev_place, prev_label, t = member.place, "start (%s)" % member.start_address, member.shift[0]
            for stop in stops:
                free = stop.start - t - stop.drive
                if free >= self.settings.min_gap:
                    self.gaps.append(Gap(self, member, t, stop.start, free, prev_place, prev_label, stop.job.place,
                                         "job %s (%s)" % (stop.job.id, stop.job.address)))
                prev_place, prev_label, t = stop.job.place, "job %s (%s)" % (stop.job.id, stop.job.address), stop.end
            free = member.shift[1] - t
            if free >= self.settings.min_gap:
                self.gaps.append(Gap(self, member, t, member.shift[1], free, prev_place, prev_label, None, "end of shift"))
        self.gaps.sort(key=lambda g: (g.start, g.member.id))

    # ---- backfill scoring for one (gap, customer) pair; Period.rank assigns

    def score(self, gap, c):
        """The Suggestion fields for customer `c` in `gap`, or None when the
        visit does not fit before the next job's planned start (or the shift
        end), so that no later job moves."""
        period, visit = self.period, self.settings.visit
        to = self.minutes(gap.prev_place, c.place)
        if gap.next_place is None:
            added, back = to, 0.0
            needed = to + visit
        else:
            back = self.minutes(c.place, gap.next_place)
            direct = self.minutes(gap.prev_place, gap.next_place)
            added = to + back - direct
            needed = to + visit + back - direct
        if needed > gap.free + 1e-9:
            return None
        strength, assumed, note = period.due(c, self.date)
        not_yet_due = strength < 0
        if not_yet_due and (-strength * c.interval) > self.settings.lookahead:
            # Due is judged per day: a customer due later in the period is not
            # a valid pair for this day's gap (issue #87, item 3).
            return None
        confidence = c.place.confidence
        certainty = "low" if assumed else ("high" if confidence == "high" else "medium")
        score = strength - (added / 60.0) * DRIVE_WEIGHT_PER_HOUR + CONFIDENCE_BONUS[confidence]
        arrive = gap.start + to
        back_by = arrive + visit + back
        if gap.next_place is None:
            later = "a %d min visit ends by %s, inside the shift that ends %s" % (visit, fmt_hhmm(arrive + visit), fmt_hhmm(gap.end))
        else:
            later = "a %d min visit leaves time to reach %s by %s, its planned start, so every later job keeps its time" % (
                visit, gap.next_label, fmt_hhmm(gap.end))
        reason = "%s; adds %d min of driving; %s; address placed with %s confidence (%s)" % (
            note, round(added), later, confidence, c.place.source)
        if not_yet_due:
            reason += ("; not yet due on %s and included only because the buyer set the lookahead to %d day(s)"
                       % (self.date.isoformat(), self.settings.lookahead))
        if assumed:
            reason += "; ranked below every customer with real due evidence"
        reason += period.merge_note(c)
        return {"score": score, "added": added, "arrive": arrive, "back_by": back_by, "reason": reason,
                "certainty": certainty, "assumed": assumed, "not_yet_due": not_yet_due}

    def run(self):
        self.sequence()
        self.find_gaps()
        return self


# ---------------------------------------------------------------- report

def outreach_draft(s):
    c, gap = s.customer, s.gap
    when = "between %s and %s" % (fmt_hhmm(gap.start), fmt_hhmm(gap.end))
    if c.open_quote:
        history = "You have an open quote with us (%s)" % c.open_quote
    elif c.last_service is None:
        history = "We have no record of your last service"
    else:
        history = "Your last service was on %s" % c.last_service.isoformat()
    service = ("%s service plan" % c.plan_text) if c.plan_text else ("%s service" % (c.service_type or "scheduled"))
    return ("Hello %s, this is a message from [buyer's company name] about your %s. %s. Our technician %s "
            "is scheduled near %s on %s %s and could visit at about %s. Would that time suit you? Reply yes to confirm, "
            "or tell us a better time. If you would rather not be contacted about scheduling, reply stop and we will "
            "mark your record."
            % (c.name or "there", service, history, gap.member.name, c.address, gap.day.date.isoformat(), when, fmt_hhmm(s.arrive)))


def render_day(day):
    L = []
    p = day.period
    L.append("## Day %s" % day.date.isoformat())
    L.append("")
    L.append("### Schedule per crew member")
    L.append("")
    for member in sorted(day.crew, key=lambda m: m.id):
        L.append("#### %s (%s), %s to %s, skills: %s" % (member.name, member.id, fmt_hhmm(member.shift[0]), fmt_hhmm(member.shift[1]),
                                                        ", ".join(sorted(member.skills)) or "(none listed)"))
        L.append("")
        if member.id not in day.routes:
            L.append("No route: the start address could not be placed (see data problems).")
            L.append("")
            continue
        stops, total = day.routes[member.id]
        L.append("Start: %s. Total drive time: %d min over %d stop(s)." % (member.start_address, round(total), len(stops)))
        L.append("")
        if stops:
            L.append("| # | Job | Customer | Address | Drive (min) | Arrive | Start | End | Window |")
            L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
            for i, s in enumerate(stops, start=1):
                L.append("| %d | %s | %s | %s | %d | %s | %s | %s | %s to %s |" % (
                    i, s.job.id, s.job.customer, s.job.address, round(s.drive), fmt_hhmm(s.arrive), fmt_hhmm(s.start),
                    fmt_hhmm(s.end), fmt_hhmm(s.job.window[0]), fmt_hhmm(s.job.window[1])))
        else:
            L.append("No stops assigned.")
        L.append("")
    total = day.total_drive
    line = "Total drive time, all crew: %d min, against %d min if each crew member visited the same jobs in the order the file gave them" % (
        round(total), round(day.baseline))
    if total < day.baseline - 0.5:
        line += "; the plan is shorter by %d min." % round(day.baseline - total)
    elif abs(total - day.baseline) <= 0.5:
        line += "; the same. The given order was already the shortest among the orders the insertion tried, within the windows and hours."
    else:
        line += ("; the plan is longer by %d min. Why: sequencing is a greedy insertion constrained by every time window and "
                 "shift, and the given order (which was not checked against windows and hours) happened to be shorter."
                 % round(total - day.baseline))
    L.append(line + " Drive times exclude the return to the start address.")
    L.append("")
    L.append("### Unassigned jobs")
    L.append("")
    if day.unassigned or day.dropped:
        for job, reason in day.unassigned:
            L.append("- Job %s (%s, %s, window %s to %s, %d min, skills: %s): %s" % (
                job.id, job.customer, job.address, fmt_hhmm(job.window[0]), fmt_hhmm(job.window[1]), job.duration,
                ", ".join(sorted(job.skills)) or "none", reason))
        for d in day.dropped:
            L.append("- Job %s (jobs row %d, %s, %s): not planned, %s (see data problems)" % (
                d.id, d.row, d.customer or "no customer given", d.address or "no address given", d.reason))
    else:
        L.append("- None: every job of this day that parsed and was placed is scheduled.")
    L.append("")
    L.append("### Gaps")
    L.append("")
    if day.gaps:
        for g in day.gaps:
            L.append("- %s (%s): %s to %s, %d min free after driving; area: from %s to %s" % (
                g.member.name, g.member.id, fmt_hhmm(g.start), fmt_hhmm(g.end), round(g.free), g.prev_label, g.next_label))
    else:
        L.append("- None of at least %d min." % day.settings.min_gap)
    L.append("")
    L.append("### Ranked backfill suggestions")
    L.append("")
    if day.suggestions:
        current = None
        for s in day.suggestions:
            if s.gap is not current:
                if current is not None:
                    L.append("")
                current = s.gap
                L.append("#### %s (%s), gap %s to %s: alternatives for this gap, best first" % (
                    s.gap.member.name, s.gap.member.id, fmt_hhmm(s.gap.start), fmt_hhmm(s.gap.end)))
                L.append("")
            flags = []
            if s.assumed:
                flags.append("assumption based")
            if s.not_yet_due:
                flags.append("not yet due")
            L.append("%d. **%s** (%s), %s. Certainty: **%s**%s. Could arrive about %s. Reason: %s." % (
                s.rank, s.customer.name, s.customer.id, s.customer.address, s.certainty,
                " (%s)" % ", ".join(flags) if flags else "", fmt_hhmm(s.arrive), s.reason))
        L.append("")
    else:
        L.append("- None: no remaining customer fits a reported gap." if day.gaps else "- None: there are no gaps to fill.")
        L.append("")
    return L


def render(period, inputs):
    p = period
    s = p.settings
    L = []
    first, last = p.dates[0].isoformat(), p.dates[-1].isoformat()
    span = first if first == last else "%s to %s" % (first, last)
    L.append("# %s: plan for %s" % (AGENT_NAME, span))
    L.append("")
    L.append("Produced by `agents/field-service-planner/planner.py` %s. Drafts only: this agent contacted nobody. "
             "Every suggestion below is for the buyer to act on or discard." % AGENT_VERSION)
    L.append("")
    L.append("## Brief and inputs")
    L.append("")
    L.append("- Planning period: %s (%d day(s))" % (span, len(p.dates)))
    for label, path, count, digest in inputs:
        L.append("- %s: `%s`, %d data row(s), SHA-256 `%s`" % (label, os.path.basename(path), count, digest))
    L.append("- Crew planned: %s" % ", ".join("%s (%s, %s to %s, %s)" % (m.name, m.id, fmt_hhmm(m.shift[0]), fmt_hhmm(m.shift[1]),
                                                                       ", ".join(sorted(m.skills)) or "no skills listed")
                                              for m in sorted(p.crew, key=lambda m: m.id)))
    L.append("- Geocoding and drive times: %s; placed at %s (UTC)" % (p.provider.describe, p.geocoded_utc))
    lookahead = ("only customers due on or before the last day are suggested" if not s.lookahead
                 else "customers due up to %d day(s) after the last day are also suggested and marked not yet due" % s.lookahead)
    L.append("- Settings: gaps of at least %d min are reported; a backfill visit is assumed to take %d min; %s; "
             "at most %d suggestion(s) per gap." % (s.min_gap, s.visit, lookahead, s.per_gap))
    L.append("")
    L.append("## Data problems")
    L.append("")
    if p.problems:
        for item in p.problems:
            L.append("- %s" % item)
    else:
        L.append("- None: every row parsed and every address was placed.")
    L.append("")
    for day in p.days:
        L.extend(render_day(day))
    L.append("## Checked and excluded customers")
    L.append("")
    if p.excluded:
        for c, reason in p.excluded:
            L.append("- %s (%s), %s: %s" % (c.name, c.id, c.address, reason))
    else:
        L.append("- None.")
    L.append("")
    L.append("## Outreach drafts")
    L.append("")
    L.append("Drafts only. Nothing here was sent; the buyer decides whether to contact anyone. "
             "Customers with the do not contact flag never appear here.")
    L.append("")
    suggestions = p.suggestions
    for sg in suggestions:
        L.append("### Draft for %s (%s), suggestion %d in %s's gap %s to %s on %s" % (
            sg.customer.name, sg.customer.id, sg.rank, sg.gap.member.name, fmt_hhmm(sg.gap.start), fmt_hhmm(sg.gap.end),
            sg.gap.day.date.isoformat()))
        L.append("")
        L.append("> " + outreach_draft(sg))
        L.append("")
    if not suggestions:
        L.append("No drafts: there are no suggestions.")
        L.append("")
    L.append("## Method")
    L.append("")
    L.append("- Sequencing: " + SEQUENCE_NOTE)
    L.append("- Gaps: " + GAP_NOTE)
    L.append("- Duplicates: customers at the same normalized address whose normalized names are equal or similar "
             "(sequence ratio at least %.2f) are merged into the record with the most filled fields; blanks are filled "
             "from the merged row, a do not contact or opted out flag on either row carries over, and every merge is "
             "flagged in the excluded list and in the kept customer's reason." % NAME_SIMILARITY)
    L.append("- Exclusions before ranking, in order: duplicate (merged); do not contact or opted out flag; address not "
             "placed; no service plan, known service type or open quote; already has a job in the planning period; not due "
             "(within the lookahead window, when one is set).")
    L.append("- Due: a customer is due when the last service date plus the interval is on or before the day, or an open "
             "quote is on record. The interval is the stated service plan, or, when the plan is blank, a typical interval "
             "by service type (%s), which is a stated assumption. Due strength is (day minus next due date) divided by the "
             "interval. With no last service date the customer is treated as one full interval elapsed. Every suggestion "
             "that rests on an assumed interval or an assumed last service is labelled assumption based with certainty low "
             "and ranks below every suggestion with real due evidence."
             % ", ".join("%s %d days" % (k, v) for k, v in sorted(TYPICAL_INTERVALS.items())))
    L.append("- " + RANK_NOTE)
    L.append("- Fit: a suggestion is made only when the drive to the customer, the assumed visit and the drive on to the "
             "next job all fit before that job's planned start (or before the shift ends), so no later job moves.")
    L.append("- Per day: due and the lookahead window are judged against each gap's own day, so a customer due later in "
             "the period is suggested only from the day it is due (or within the lookahead window of that day).")
    L.append("- Certainty: high when a last service date or open quote is recorded and the address was placed with high "
             "confidence; medium when recorded and placed with medium or low confidence; low when assumption based.")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- CLI

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command")
    plan = sub.add_parser("plan", help="plan the period and write the report")
    plan.add_argument("--date", required=True, help="planning date, YYYY-MM-DD (the first day when --date-to is given)")
    plan.add_argument("--date-to", help="last day of the period, YYYY-MM-DD; the jobs file then needs a date column")
    plan.add_argument("--jobs", required=True, help="jobs CSV")
    plan.add_argument("--crew", required=True, help="crew CSV")
    plan.add_argument("--customers", required=True, help="customers CSV")
    source = plan.add_mutually_exclusive_group(required=True)
    source.add_argument("--places", help="offline fixture provider: JSON file of places (no network)")
    source.add_argument("--live", action="store_true", help="open routing services; needs %s" % routing.CONTACT_ENV)
    plan.add_argument("--out", help="write the report here instead of stdout")
    plan.add_argument("--min-gap-minutes", type=int, default=DEFAULT_MIN_GAP)
    plan.add_argument("--visit-minutes", type=int, default=DEFAULT_VISIT)
    plan.add_argument("--lookahead-days", type=int, default=DEFAULT_LOOKAHEAD)
    plan.add_argument("--suggestions-per-gap", type=int, default=DEFAULT_PER_GAP)
    return parser


def period_dates(first, last):
    if last < first:
        raise InputError("--date-to %s is before --date %s" % (last.isoformat(), first.isoformat()))
    if (last - first).days > 31:
        raise InputError("the period is longer than 31 days; split the run")
    return [first + dt.timedelta(days=i) for i in range((last - first).days + 1)]


def load(args, env=None, provider=None):
    """Read the files and build the Period (not yet run)."""
    first = parse_date(args.date, "--date")
    last = parse_date(args.date_to, "--date-to") if args.date_to else first
    dates = period_dates(first, last)
    settings = Settings(args.min_gap_minutes, args.visit_minutes, args.lookahead_days, args.suggestions_per_gap)
    problems = []
    jobs_rows, job_optional = read_csv(args.jobs, JOB_COLUMNS, "jobs", optional=(JOB_DATE_COLUMN,))
    crew_rows, _ = read_csv(args.crew, CREW_COLUMNS, "crew")
    cust_rows, _ = read_csv(args.customers, CUSTOMER_COLUMNS, "customers", optional=CUSTOMER_OPTIONAL)
    if len(dates) > 1 and JOB_DATE_COLUMN not in job_optional:
        raise InputError("jobs file %s needs a %r column when --date-to is given" % (args.jobs, JOB_DATE_COLUMN))
    if not crew_rows:
        raise InputError("crew file %s has no data rows; nothing can be scheduled" % args.crew)
    dropped_jobs = []
    jobs = load_records(jobs_rows, Job, "jobs", problems, dropped_jobs)
    crew = load_records(crew_rows, Crew, "crew", problems)
    customers = load_records(cust_rows, Customer, "customers", problems)
    kept = []
    for job in jobs:
        if JOB_DATE_COLUMN in job_optional and job.date is None:
            reason = "date is blank but the file has a date column"
        elif job.date is not None and job.date not in dates:
            reason = "date %s is outside the planning period" % job.date.isoformat()
        else:
            reason = None
        if reason:
            problems.append("jobs row %d (%s) dropped: %s" % (job.row, job.id, reason))
            dropped_jobs.append(DroppedJob(job.row, job.id, job.customer, job.address,
                                           job.date.isoformat() if job.date else "", reason))
        else:
            kept.append(job)
    if provider is None:
        provider = routing.FixtureProvider(args.places) if args.places else routing.LiveProvider.from_env(env)
    period = Period(dates, kept, crew, customers, provider, settings)
    period.problems.extend(problems)
    period.dropped_jobs = sorted(dropped_jobs, key=lambda d: d.row)
    inputs = [("Jobs", args.jobs, len(jobs_rows), sha256_file(args.jobs)),
              ("Crew", args.crew, len(crew_rows), sha256_file(args.crew)),
              ("Customers", args.customers, len(cust_rows), sha256_file(args.customers))]
    return period, inputs


def plan(args, env=None, provider=None):
    """Load, plan, render. Returns the report text. Raises InputError,
    routing.RoutingError or routing.ConfigError; writes nothing on error."""
    period, inputs = load(args, env, provider)
    period.run()
    return render(period, inputs)


def main(argv=None, env=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "plan":
        parser.print_help(stderr)
        return 2
    try:
        text = plan(args, env)
    except (InputError, ValueError, routing.RoutingError, routing.ConfigError) as exc:
        stderr.write("planner: %s\nno report written\n" % exc)
        return 2
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        stderr.write("report written to %s\n" % args.out)
    else:
        stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
