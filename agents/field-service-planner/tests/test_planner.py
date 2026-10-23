"""Tests for agents/field-service-planner (issue #73). No network.

Run from the repository root:
    python3 -m unittest discover -s agents/field-service-planner/tests -v

Every input here is SYNTHETIC: the CSV files and the places file under
fixtures/ are invented sample data, labelled as such in fixtures/
provenance.json and in the places file's own "label" field, and the
response bodies handed to the live provider's parser below are hand
written shapes, labelled synthetic where they appear. No figure in this
suite was fetched from a buyer, a geocoder or a routing service.
"""

import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

import planner  # noqa: E402
import routing  # noqa: E402

FIX = HERE / "fixtures"
DATE = "2026-11-03"


def fixture_args(**extra):
    args = ["plan", "--date", DATE, "--jobs", str(FIX / "jobs.csv"), "--crew", str(FIX / "crew.csv"),
            "--customers", str(FIX / "customers.csv"), "--places", str(FIX / "places.json")]
    for key, value in extra.items():
        args += ["--" + key.replace("_", "-"), str(value)]
    return args


def run(argv, env=None):
    out, err = io.StringIO(), io.StringIO()
    with patch.object(routing.UrllibTransport, "get", side_effect=AssertionError("no network call may happen in tests")):
        code = planner.main(argv, env=env or {}, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def build_period(run_it=True, **overrides):
    """The Period object after a fixture run, for structural assertions."""
    args = planner.build_parser().parse_args(fixture_args(**overrides))
    period, _ = planner.load(args, env={})
    return period.run() if run_it else period


# ---------------------------------------------------------------- parsing

class ParsingTests(unittest.TestCase):
    def test_times_dates_flags_plans(self):
        self.assertEqual(planner.parse_hhmm("08:30", "x"), 510)
        self.assertEqual(planner.parse_hhmm("24:00", "x"), 1440)
        for bad in ("8.30", "25:00", "08:60", "", "noon"):
            with self.assertRaises(ValueError):
                planner.parse_hhmm(bad, "x")
        self.assertEqual(planner.fmt_hhmm(510), "08:30")
        self.assertEqual(planner.parse_skills(" HVAC; plumbing ;;"), frozenset({"hvac", "plumbing"}))
        self.assertTrue(planner.parse_flag("Yes", "x"))
        self.assertFalse(planner.parse_flag("", "x"))
        with self.assertRaises(ValueError):
            planner.parse_flag("maybe", "x")
        self.assertEqual(planner.parse_plan("quarterly"), 91)
        self.assertEqual(planner.parse_plan("every 45 days"), 45)
        for bad in ("every 0 days", "sometimes", ""):
            with self.assertRaises(ValueError):
                planner.parse_plan(bad)
        self.assertEqual(planner.normalize_key("Maple Court Apartments", "15 Maple Court, Sampletown"),
                         planner.normalize_key("maple court apartments", "15 MAPLE COURT, Sampletown"))

    def test_row_level_problems_are_dropped_and_named_not_fatal(self):
        p = build_period()
        self.assertIn("jobs row 9 (J8) dropped: duration_minutes must be an integer, got 'ninety'", p.problems)
        self.assertIn("customers row 10 (K9) dropped: last_service_date must be YYYY-MM-DD, got 'last week'", p.problems)
        self.assertNotIn("J8", [j.id for j in p.jobs])
        self.assertNotIn("K9", [c.id for c in p.customers])
        self.assertEqual(next(c for c in p.customers if c.id == "K11").open_quote, "Q-77 compressor replacement")
        k18 = next(c for c in p.customers if c.id == "K18")
        self.assertEqual((k18.interval, k18.interval_assumed, k18.plan_label), (91, True, "typical pest control interval"))
        self.assertTrue(next(c for c in p.customers if c.id == "K19").opted_out)
        self.assertIsNone(next(c for c in p.customers if c.id == "K20").interval)

    def test_similarity_rule(self):
        row = {"customer_id": "x", "name": "", "address": "", "last_service_date": "", "service_plan": "", "do_not_contact": ""}
        def cust(name, address, cid="x"):
            r = dict(row, customer_id=cid, name=name, address=address)
            return planner.Customer(r, 2)
        a = cust("Maple Court Apartments", "15 Maple Court, Sampletown")
        self.assertEqual(planner.similar_customers(a, cust("maple court apartments", "15 MAPLE COURT, Sampletown")), 1.0)
        self.assertGreaterEqual(planner.similar_customers(a, cust("Maple Court Apts", "15 Maple Court, Sampletown")), planner.NAME_SIMILARITY)
        self.assertIsNone(planner.similar_customers(a, cust("Maple Court Apartments", "16 Maple Court, Sampletown")))
        self.assertIsNone(planner.similar_customers(a, cust("Riverbend Bakery", "15 Maple Court, Sampletown")))
        with self.assertRaises(ValueError):
            cust("Z", "1 Street", "z").__class__(dict(row, customer_id="z", name="Z", address="1 Street", service_type="juggling"), 3)


# ---------------------------------------------------------------- fail closed

class FailClosedTests(unittest.TestCase):
    def _tmp(self, name, text):
        path = os.path.join(self.dir.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.out = os.path.join(self.dir.name, "report.md")

    def test_missing_column_is_exit_2_and_no_report(self):
        bad = self._tmp("jobs.csv", "job_id,customer,address\nJ1,x,y\n")
        argv = fixture_args(out=self.out)
        argv[argv.index("--jobs") + 1] = bad
        code, out, err = run(argv)
        self.assertEqual(code, 2)
        self.assertIn("lacks column(s): duration_minutes, window_start, window_end, skills", err)
        self.assertIn("no report written", err)
        self.assertFalse(os.path.exists(self.out))
        self.assertEqual(out, "")

    def test_missing_file_bad_date_and_bad_places_file(self):
        argv = fixture_args(out=self.out)
        argv[argv.index("--crew") + 1] = os.path.join(self.dir.name, "absent.csv")
        code, _, err = run(argv)
        self.assertEqual(code, 2)
        self.assertIn("cannot read crew file", err)
        code, _, err = run(fixture_args(out=self.out, date="3 Nov"))
        self.assertEqual(code, 2)
        self.assertIn("--date must be YYYY-MM-DD", err)
        places = self._tmp("places.json", "{not json")
        argv = fixture_args(out=self.out)
        argv[argv.index("--places") + 1] = places
        code, _, err = run(argv)
        self.assertEqual(code, 2)
        self.assertIn("cannot read places file", err)
        self.assertFalse(os.path.exists(self.out))

    def test_provider_failure_stops_the_run_with_no_report(self):
        with patch.object(routing.FixtureProvider, "matrix", side_effect=routing.RoutingError("table refused")):
            code, out, err = run(fixture_args(out=self.out))
        self.assertEqual(code, 2)
        self.assertIn("table refused", err)
        self.assertFalse(os.path.exists(self.out))
        self.assertEqual(out, "")

    def test_live_without_contact_is_refused_before_any_request(self):
        argv = fixture_args(out=self.out)
        i = argv.index("--places")
        del argv[i:i + 2]
        argv.append("--live")
        code, _, err = run(argv, env={})
        self.assertEqual(code, 2)
        self.assertIn(routing.CONTACT_ENV, err)
        self.assertIn("refuses to run without it", err)

    def test_empty_crew_file_is_fatal(self):
        crew = self._tmp("crew.csv", "crew_id,name,start_address,shift_start,shift_end,skills\n")
        argv = fixture_args(out=self.out)
        argv[argv.index("--crew") + 1] = crew
        code, _, err = run(argv)
        self.assertEqual(code, 2)
        self.assertIn("has no data rows", err)

    def test_period_without_a_date_column_and_bad_periods(self):
        code, _, err = run(fixture_args(out=self.out, date_to="2026-11-04"))
        self.assertEqual(code, 2)
        self.assertIn("needs a 'date' column when --date-to is given", err)
        code, _, err = run(fixture_args(out=self.out, date_to="2026-11-01"))
        self.assertEqual(code, 2)
        self.assertIn("is before --date", err)
        code, _, err = run(fixture_args(out=self.out, date_to="2026-12-31"))
        self.assertEqual(code, 2)
        self.assertIn("longer than 31 days", err)
        self.assertFalse(os.path.exists(self.out))


# ---------------------------------------------------------------- schedule

class ScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = build_period()
        cls.day = cls.p.days[0]

    def crew(self, cid):
        return next(m for m in self.p.crew if m.id == cid)

    def test_every_stop_respects_window_hours_skills_and_sequence(self):
        scheduled = set()
        for cid, (stops, total) in self.day.routes.items():
            member = self.crew(cid)
            t, here, drive_sum = member.shift[0], member.place, 0.0
            for s in stops:
                self.assertTrue(s.job.skills <= member.skills, (cid, s.job.id))
                self.assertAlmostEqual(s.drive, self.p.minutes(here, s.job.place))
                self.assertAlmostEqual(s.arrive, t + s.drive)
                self.assertGreaterEqual(s.start, s.job.window[0])
                self.assertLessEqual(s.start, s.job.window[1])
                self.assertEqual(s.end, s.start + s.job.duration)
                self.assertGreaterEqual(s.start, member.shift[0])
                self.assertLessEqual(s.end, member.shift[1])
                self.assertNotIn(s.job.id, scheduled)
                scheduled.add(s.job.id)
                drive_sum += s.drive
                t, here = s.end, s.job.place
            self.assertAlmostEqual(total, drive_sum)
        self.assertEqual(scheduled, {"J1", "J2", "J3", "J4", "J5"})
        self.assertNotIn("C3", self.day.routes)  # unplaced start address: no route
        # every job is either scheduled or listed as unassigned (job description, acceptance 1)
        listed = scheduled | {job.id for job, _ in self.day.unassigned}
        self.assertEqual(listed, {j.id for j in self.p.jobs})

    def test_baseline_comparison_is_computed(self):
        self.assertIsNotNone(self.day.baseline)
        self.assertLess(self.day.total_drive, self.day.baseline)

    def test_unassigned_jobs_carry_their_reason(self):
        reasons = {job.id: reason for job, reason in self.day.unassigned}
        self.assertEqual(set(reasons), {"J6", "J7"})
        self.assertEqual(reasons["J6"], "address could not be placed")
        self.assertIn("skills: welding", reasons["J7"])
        self.assertIn("job J6: address '77 Nowhere Road, Sampletown' could not be placed", " ".join(self.p.problems))
        self.assertIn("crew C3: start address '9 Unplaced Lane, Sampletown' could not be placed", " ".join(self.p.problems))

    def test_plumbing_jobs_go_to_the_only_plumber_with_a_placed_start(self):
        stops, _ = self.day.routes["C1"]
        self.assertEqual({s.job.id for s in stops} & {"J2", "J5"}, {"J2", "J5"})
        stops2, _ = self.day.routes["C2"]
        self.assertIn("J3", [s.job.id for s in stops2])

    def test_infeasible_slot_is_reported_not_forced(self):
        # Shrink C1's shift so the two plumbing jobs cannot both fit, then one
        # of them must be unassigned with the slot reason rather than placed
        # outside hours.
        p = build_period(run_it=False)
        c1 = next(m for m in p.crew if m.id == "C1")
        c1.shift = (planner.parse_hhmm("08:00", "x"), planner.parse_hhmm("12:00", "x"))
        p.run()
        day = p.days[0]
        reasons = {job.id: reason for job, reason in day.unassigned}
        self.assertIn("J5", reasons)
        self.assertIn("no feasible slot", reasons["J5"])
        for s in day.routes["C1"][0]:
            self.assertLessEqual(s.end, c1.shift[1])


# ---------------------------------------------------------------- gaps and backfill

class BackfillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = build_period()
        cls.day = cls.p.days[0]
        cls.excluded = {c.id: reason for c, reason in cls.p.excluded}
        cls.suggested = [s.customer.id for s in cls.p.suggestions]

    def test_gaps_are_at_least_min_gap_and_carry_context(self):
        self.assertTrue(self.day.gaps)
        for g in self.day.gaps:
            self.assertGreaterEqual(g.free, planner.DEFAULT_MIN_GAP)
            self.assertLess(g.start, g.end)
            self.assertIsNotNone(g.prev_place)
            self.assertTrue(g.prev_label)
            self.assertTrue(g.next_label)
        tails = [g for g in self.day.gaps if g.next_place is None]
        self.assertTrue(tails, "the end of shift tail must be a gap")
        starts = [g.start for g in self.day.gaps]
        self.assertEqual(starts, sorted(starts))

    def test_hard_exclusions_in_order_and_never_suggested(self):
        self.assertEqual(self.excluded["K5"], "do not contact flag is set")
        self.assertEqual(self.excluded["K19"], "opted out flag is set")
        self.assertEqual(self.excluded["K1"], "already has a job in the planning period")
        self.assertEqual(self.excluded["K6"], "duplicate of customer K2 (same address, name similarity 1.00): merged into K2")
        self.assertTrue(self.excluded["K15"].startswith("duplicate of customer K2 (same address, name similarity 0.8"))
        self.assertEqual(self.excluded["K16"], "duplicate of customer K17 (same address, name similarity 0.89): merged into K17, which has more filled fields")
        self.assertEqual(self.excluded["K20"], "no service plan, no known service type and no open quote: due date cannot be judged")
        self.assertEqual(self.excluded["K8"], "address could not be placed")
        self.assertTrue(self.excluded["K7"].startswith("not yet due: due on 2027-01-01"))
        # K4 is due on 2026-11-19, after the day: not due according to the data, so not suggested by default
        self.assertEqual(self.excluded["K4"], "not yet due: due on 2026-11-19 (monthly plan, last service 2026-10-20), 16 day(s) after 2026-11-03")
        for cid in ("K1", "K4", "K5", "K6", "K7", "K8", "K9", "K15", "K16", "K19", "K20"):
            self.assertNotIn(cid, self.suggested)

    def test_each_customer_suggested_once_with_reason_and_certainty(self):
        self.assertEqual(len(self.suggested), len(set(self.suggested)))
        self.assertEqual(set(self.suggested), {"K2", "K3", "K10", "K11", "K12", "K13", "K14", "K17", "K18"})
        for s in self.p.suggestions:
            self.assertIn(s.certainty, ("high", "medium", "low"))
            self.assertIn("adds", s.reason)
            self.assertIn("confidence", s.reason)
            if s.gap.next_place is None:
                self.assertIn("inside the shift that ends", s.reason)
            else:
                self.assertIn("its planned start, so every later job keeps its time", s.reason)
            self.assertFalse(s.not_yet_due)
            self.assertTrue(s.reason.startswith("due") or s.reason.startswith("assumption based") or s.reason.startswith("open quote"), s.reason)
        by_id = {s.customer.id: s for s in self.p.suggestions}
        self.assertTrue(by_id["K3"].assumed)
        self.assertEqual(by_id["K3"].certainty, "low")
        self.assertIn("assumption based: no last service date recorded, so the monthly plan (30 day interval)", by_id["K3"].reason)
        self.assertFalse(by_id["K2"].assumed)
        self.assertEqual(by_id["K2"].certainty, "high")
        self.assertIn("due since 2026-09-14 (quarterly plan, last service 2026-06-15), 50 day(s) overdue", by_id["K2"].reason)
        self.assertEqual(by_id["K10"].certainty, "medium")  # placed with medium confidence in the fixture
        self.assertTrue(by_id["K18"].assumed)
        self.assertEqual(by_id["K18"].certainty, "low")
        self.assertIn("assumption based: no service plan stated, the typical pest control interval of 91 days is applied; due since 2026-08-31", by_id["K18"].reason)
        self.assertIn("ranked below every customer with real due evidence", by_id["K18"].reason)
        self.assertIn("; merged duplicate row(s): K6 (name similarity 1.00), K15 (name similarity 0.8", by_id["K2"].reason)
        self.assertEqual(by_id["K17"].customer.merged_from[0][0].id, "K16")
        self.assertFalse(by_id["K11"].assumed)  # an open quote is due according to the data, not an assumption
        self.assertEqual(by_id["K11"].certainty, "high")
        self.assertTrue(by_id["K11"].reason.startswith("open quote on record (Q-77 compressor replacement); treated as due"))

    def test_ranking_in_the_first_gap(self):
        first = self.day.gaps[0]
        ranked = [s for s in self.p.suggestions if s.gap is first]
        self.assertEqual([s.customer.id for s in ranked], ["K2", "K12", "K10"])
        self.assertEqual([s.rank for s in ranked], [1, 2, 3])
        scores = [s.score for s in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertLessEqual(len(ranked), planner.DEFAULT_PER_GAP)

    def test_assumption_based_suggestions_rank_below_evidence_in_every_gap(self):
        # K3 (no last service date) has the highest raw score in the fixture, yet
        # it must never outrank a customer with real due evidence.
        by_gap = {}
        for sg in self.p.suggestions:
            by_gap.setdefault(id(sg.gap), []).append(sg)
        for seq in by_gap.values():
            tiers = [1 if sg.assumed else 0 for sg in sorted(seq, key=lambda sg: sg.rank)]
            self.assertEqual(tiers, sorted(tiers))
        k3 = next(sg for sg in self.p.suggestions if sg.customer.id == "K3")
        evidence = [sg for sg in self.p.suggestions if not sg.assumed]
        self.assertGreater(k3.score, min(sg.score for sg in evidence))  # a higher raw score than some evidence, still ranked after all of it
        self.assertTrue(all(sg.rank < k3.rank for sg in evidence if sg.gap is k3.gap))

    def test_suggestion_fits_the_gap(self):
        for s in self.p.suggestions:
            g = s.gap
            to = self.p.minutes(g.prev_place, s.customer.place)
            if g.next_place is None:
                needed = to + self.p.settings.visit
                self.assertLessEqual(s.back_by, g.member.shift[1] + 1e-9)
            else:
                back = self.p.minutes(s.customer.place, g.next_place)
                needed = to + self.p.settings.visit + back - self.p.minutes(g.prev_place, g.next_place)
                # acceptance 6: back at the next job no later than its planned start
                self.assertLessEqual(s.back_by, g.end + 1e-9)
            self.assertLessEqual(needed, g.free + 1e-9)
            self.assertAlmostEqual(s.arrive, g.start + to)

    def test_per_gap_limit_and_lookahead_are_settings(self):
        p = build_period(suggestions_per_gap=1)
        per_gap = {}
        for s in p.suggestions:
            per_gap[id(s.gap)] = per_gap.get(id(s.gap), 0) + 1
        self.assertTrue(all(n == 1 for n in per_gap.values()))
        p = build_period(lookahead_days=30)
        self.assertNotIn("K4", {c.id for c, _ in p.excluded})  # 16 days ahead is inside a 30 day window
        self.assertTrue(any(c.id == "K7" and reason.startswith("not due within 30 days of 2026-11-03") for c, reason in p.excluded))
        k4 = [s for s in p.suggestions if s.customer.id == "K4"]
        self.assertEqual(len(k4), 1)
        self.assertTrue(k4[0].not_yet_due)
        self.assertIn("included only because the buyer set the lookahead to 30 day(s)", k4[0].reason)


class PeriodTests(unittest.TestCase):
    """A range of days with a dated jobs file (the job description's one week scenario)."""

    @classmethod
    def setUpClass(cls):
        argv = fixture_args(date_to="2026-11-05")
        argv[argv.index("--jobs") + 1] = str(FIX / "jobs-week.csv")
        cls.argv = argv
        args = planner.build_parser().parse_args(argv)
        cls.p, _ = planner.load(args, env={})
        cls.p.run()

    def test_days_jobs_and_dropped_rows(self):
        self.assertEqual([d.date.isoformat() for d in self.p.days], ["2026-11-03", "2026-11-04", "2026-11-05"])
        by_day = {d.date.isoformat(): {s.job.id for stops, _ in d.routes.values() for s in stops} for d in self.p.days}
        self.assertEqual(by_day["2026-11-04"], {"W1", "W2"})
        self.assertEqual(by_day["2026-11-05"], {"W3"})
        self.assertIn("jobs row 13 (W4) dropped: date 2026-11-09 is outside the planning period", self.p.problems)
        self.assertIn("jobs row 14 (W5) dropped: date is blank but the file has a date column", self.p.problems)

    def test_customers_suggested_once_across_the_period_and_light_days_get_suggestions(self):
        ids = [s.customer.id for s in self.p.suggestions]
        self.assertEqual(len(ids), len(set(ids)))
        light = [d for d in self.p.days if d.date.isoformat() in ("2026-11-04", "2026-11-05")]
        self.assertTrue(all(d.gaps for d in light))
        self.assertTrue(all(d.suggestions for d in light))
        for day in self.p.days:
            ranks = {}
            for sg in day.suggestions:
                ranks.setdefault(id(sg.gap), []).append(sg.rank)
            for seq in ranks.values():
                self.assertEqual(seq, list(range(1, len(seq) + 1)))
                self.assertLessEqual(len(seq), planner.DEFAULT_PER_GAP)

    def test_report_has_one_block_per_day(self):
        code, text, err = run(self.argv)
        self.assertEqual(code, 0, err)
        self.assertIn("plan for 2026-11-03 to 2026-11-05", text)
        for d in ("2026-11-03", "2026-11-04", "2026-11-05"):
            self.assertIn("## Day %s\n" % d, text)
        self.assertEqual(text.count("## Day "), 3)


# ---------------------------------------------------------------- report

class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.text, cls.err = run(fixture_args())

    def test_dry_run_writes_the_full_report_shape(self):
        self.assertEqual(self.code, 0, self.err)
        for heading in ("# Field Service Route Planner & Schedule Backfill: plan for 2026-11-03", "## Brief and inputs",
                        "## Data problems", "## Day 2026-11-03", "### Schedule per crew member", "### Unassigned jobs", "### Gaps",
                        "### Ranked backfill suggestions", "## Checked and excluded customers", "## Outreach drafts", "## Method"):
            self.assertIn(heading + "\n", self.text)
        for cid in ("C1", "C2", "C3"):
            self.assertIn("(%s)" % cid, self.text)
        self.assertIn("No route: the start address could not be placed", self.text)
        self.assertRegex(self.text, r"Total drive time, all crew: \d+ min, against \d+ min if each crew member visited the same jobs in the order the file gave them; the plan is shorter by \d+ min\.")
        self.assertIn("only customers due on or before the last day are suggested", self.text)
        self.assertRegex(self.text, r"- Jobs: `jobs.csv`, 8 data row\(s\), SHA-256 `[0-9a-f]{64}`")
        self.assertIn("SYNTHETIC fixture", self.text)  # the places file label is printed with the provider
        self.assertRegex(self.text, r"placed at \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z \(UTC\)")
        self.assertIn("Drafts only: this agent contacted nobody.", self.text)

    def test_schedule_table_rows_and_flagged_rows(self):
        self.assertIn("| 1 | J1 | Northside Dental | 10 Oak Street, Sampletown |", self.text)
        self.assertIn("- jobs row 9 (J8) dropped", self.text)
        self.assertIn("- Job J6 (Westfield Garage, 77 Nowhere Road, Sampletown", self.text)

    def test_suggestions_and_drafts_match_and_exclude_do_not_contact(self):
        drafts = re.findall(r"^### Draft for .* \((K\d+)\)", self.text, re.M)
        suggestions = re.findall(r"^\d+\. \*\*.*\*\* \((K\d+)\)", self.text, re.M)
        self.assertEqual(drafts, suggestions)
        self.assertEqual(len(drafts), 9)
        self.assertNotIn("Quiet Inn", self.text.split("## Checked and excluded customers")[0].split("### Gaps")[1])
        self.assertNotIn("K5", self.text.split("## Outreach drafts")[1].split("## Method")[0])
        self.assertIn("Certainty: **low** (assumption based)", self.text)
        self.assertIn("> Hello Cedar Diner, this is a message from [buyer's company name]", self.text)
        self.assertIn("Our technician Lee Okafor is scheduled near 8 Cedar Street, Sampletown on 2026-11-03", self.text)
        self.assertIn("You have an open quote with us (Q-77 compressor replacement)", self.text)
        self.assertIn("about your pest control service. Your last service was on 2026-06-01.", self.text)
        self.assertIn("merged into K17, which has more filled fields", self.text)
        self.assertIn("- Duplicates: customers at the same normalized address", self.text)
        self.assertIn("; area: from start (1 Depot Road, Sampletown) to job J3 (5 Summit Avenue, Sampletown)", self.text)
        self.assertIn("Drafts only. Nothing here was sent", self.text)

    def test_out_file_and_stdout_are_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "r.md")
            code, text, err = run(fixture_args(out=out))
            self.assertEqual(code, 0)
            self.assertEqual(text, "")
            self.assertIn("report written to", err)
            with open(out, encoding="utf-8") as fh:
                written = fh.read()
        # Same content apart from the placement time stamp.
        strip = lambda t: re.sub(r"placed at \S+ \(UTC\)", "placed at T (UTC)", t)
        self.assertEqual(strip(written), strip(self.text))


# ---------------------------------------------------------------- routing

class FakeTransport(object):
    def __init__(self, answers):
        self.answers = answers  # url -> (status, body bytes)
        self.calls = []

    def get(self, url, headers):
        self.calls.append((url, headers))
        if url not in self.answers:
            raise AssertionError("unexpected url " + url)
        return self.answers[url]


class RoutingTests(unittest.TestCase):
    def test_fixture_provider_places_and_drive_times(self):
        prov = routing.FixtureProvider(str(FIX / "places.json"))
        depot = prov.geocode("1 Depot Road, Sampletown")
        oak = prov.geocode("10 Oak Street, Sampletown")
        self.assertIsNone(prov.geocode("77 Nowhere Road, Sampletown"))
        self.assertIsNone(prov.geocode("an address not in the file"))
        self.assertEqual(oak.confidence, "high")
        table = prov.matrix([depot, oak])
        self.assertEqual(table[0][0], 0.0)
        self.assertEqual(table[0][1], table[1][0])
        # 0.01 degrees of latitude is about 1.11 km; at 40 km/h that is about 100 s
        self.assertAlmostEqual(table[0][1], 100, delta=2)
        self.assertIn("SYNTHETIC", prov.describe)

    def test_fixture_overrides_are_directional(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.json")
            with open(path, "w") as fh:
                json.dump({"label": "synthetic test file", "places": {"A": {"lat": 1, "lon": 1}, "B": {"lat": 1, "lon": 1.01}},
                           "travel": {"speed_kmh": 40, "overrides": {"A|B": 999}}}, fh)
            prov = routing.FixtureProvider(path)
            a, b = prov.geocode("A"), prov.geocode("B")
            table = prov.matrix([a, b])
            self.assertEqual(table[0][1], 999.0)
            self.assertNotEqual(table[1][0], 999.0)
            with open(path, "w") as fh:
                json.dump({"places": {"A": {"lat": 1, "lon": 1}}, "travel": {"speed_kmh": 0}}, fh)
            with self.assertRaises(routing.RoutingError):
                routing.FixtureProvider(path)

    def test_live_provider_requests_and_parsing(self):
        place_a = routing.Place(40.0, -75.0, "high", "t")
        place_b = routing.Place(40.01, -75.0, "high", "t")
        geo_url = routing.NOMINATIM_URL + "?q=10+Oak+Street%2C+Sampletown&format=jsonv2&limit=1"
        table_url = routing.OSRM_TABLE_URL + "-75.000000,40.000000;-75.000000,40.010000?annotations=duration"
        # Synthetic response bodies in the documented shapes; not recordings.
        answers = {
            geo_url: (200, json.dumps([{"lat": "40.0100000", "lon": "-75.0000000", "display_name": "synthetic"}]).encode()),
            table_url: (200, json.dumps({"code": "Ok", "durations": [[0, 100.5], [101.2, 0]]}).encode()),
        }
        transport = FakeTransport(answers)
        sleeps = []
        clock = iter([0.0, 0.2, 0.2, 5.0])  # first geocode at t=0; the second asks the clock at t=0.2
        prov = routing.LiveProvider("Operator Name operator@placeholder.invalid", transport=transport,
                                    sleep=sleeps.append, clock=lambda: next(clock))
        self.assertEqual(prov.geocode_url("10 Oak Street, Sampletown"), geo_url)
        place = prov.geocode("10 Oak Street, Sampletown")
        self.assertEqual((place.lat, place.lon, place.confidence), (40.01, -75.0, "medium"))
        self.assertTrue(place.source.startswith("nominatim:"))
        self.assertEqual(dict(transport.calls[0][1])["User-Agent"], "tiny-ledger field-service-planner (Operator Name operator@placeholder.invalid)")
        prov.geocode("10 Oak Street, Sampletown")  # second call 0.2 s later must wait for the 1 s interval
        self.assertEqual(len(sleeps), 1)
        self.assertAlmostEqual(sleeps[0], 0.8)
        self.assertEqual(prov.matrix_url([place_a, place_b]), table_url)
        self.assertEqual(prov.matrix([place_a, place_b]), [[0.0, 100.5], [101.2, 0.0]])
        self.assertEqual(prov.matrix([]), [])

    def test_live_provider_fails_closed_on_every_unexpected_answer(self):
        a = routing.Place(40.0, -75.0, "high", "t")
        b = routing.Place(40.01, -75.0, "high", "t")
        geo = routing.NOMINATIM_URL + "?q=x&format=jsonv2&limit=1"
        table = routing.OSRM_TABLE_URL + "-75.000000,40.000000;-75.000000,40.010000?annotations=duration"
        cases = [
            (geo, (429, b"too many"), "HTTP 429"),
            (geo, (200, b"<html>"), "not JSON"),
            (geo, (200, b"{}"), "expected a JSON array"),
            (geo, (200, b"[{\"lat\": \"north\"}]"), "lacks numeric lat/lon"),
            (table, (200, json.dumps({"code": "NoTable"}).encode()), "expected {\"code\": \"Ok\""),
            (table, (200, json.dumps({"code": "Ok", "durations": [[0]]}).encode()), "not a 2 by 2 table"),
            (table, (200, json.dumps({"code": "Ok", "durations": [[0, None], [1, 0]]}).encode()), "no route"),
        ]
        for url, answer, needle in cases:
            with self.subTest(needle=needle):
                prov = routing.LiveProvider("Operator placeholder", transport=FakeTransport({url: answer}),
                                            sleep=lambda s: None, clock=lambda: 0.0)
                with self.assertRaises(routing.RoutingError) as ctx:
                    if url == geo:
                        prov.geocode("x")
                    else:
                        prov.matrix([a, b])
                self.assertIn(needle, str(ctx.exception))
        # An empty result list is "not placed", never an error and never a guess.
        prov = routing.LiveProvider("Operator placeholder", transport=FakeTransport({geo: (200, b"[]")}),
                                    sleep=lambda s: None, clock=lambda: 0.0)
        self.assertIsNone(prov.geocode("x"))

    def test_transport_pins_https_and_the_two_hosts(self):
        t = routing.UrllibTransport()
        for url in ("http://nominatim.openstreetmap.org/search?q=x", "https://example.invalid/search",
                    "https://router.project-osrm.org.evil.test/table/v1/driving/1,1;2,2"):
            with self.subTest(url=url), self.assertRaises(routing.RoutingError):
                t.get(url, [])

    def test_live_provider_from_env(self):
        with self.assertRaises(routing.ConfigError):
            routing.LiveProvider.from_env({})
        prov = routing.LiveProvider.from_env({routing.CONTACT_ENV: " Operator placeholder "})
        self.assertIn("(Operator placeholder)", prov.user_agent)


if __name__ == "__main__":
    unittest.main()
