"""Acceptance self test: Field Service Route Planner & Schedule Backfill (issue #124).

Runs the planner the way a marketplace tester would: the documented `plan`
command on CSV inputs, offline, with the fixture places provider. It then
checks the written report against the job posting's Acceptance Criteria,
quoted by the coordinator on issue #73 (comment 6365291384). Each criterion
is printed as PASS, FAIL or UNTESTABLE with its evidence.

The checks recompute what they can from the inputs, rather than trusting
the report:
- shift hours, windows and skills come from the CSV files;
- drive minutes come from the fixture places file (great circle distance
  at its stated speed);
- due dates come from the customer rows.

Times in the report are whole minutes, so comparisons allow the report's
own one minute display rounding and nothing more.

Run:  python3 agents/field-service-planner/acceptance/acceptance.py
"""

import csv
import json
import math
import re
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "field-service-planner"
SOURCE = "job posting, Acceptance Criteria, issue #73 comment 6365291384"
TESTS = HERE.parent / "tests" / "fixtures"
FIX = HERE / "fixtures"
ROUNDING = 1  # minutes: the report prints whole minutes

CRITERIA = {
    "1": "Every job in the input is assigned to a crew member, or listed as unassigned with the reason.",
    "2": "No crew member is scheduled outside their working hours, no job falls outside its time window, "
         "and every job goes to a crew member with the required skill.",
    "3": "Drive times come from a maps or routing service, and the report names which one.",
    "4": "Total drive time is lower than visiting the jobs in the order they were given, or the report "
         "explains why not.",
    "5": "Every open slot of at least the minimum length (set by the buyer, with a default stated in the "
         "listing) is listed with the crew member, time and area.",
    "6": "Adding any suggested customer to their gap keeps every later job in that crew member's day "
         "inside its time window.",
    "7": "Every suggested customer is due for service according to the data provided, and the report says why.",
    "8": "No customer marked as do-not-contact or opted out appears in the suggestions.",
    "9": "Every suggested customer has a draft message, and no message is sent.",
}

CASES = [
    {"name": "standard day (sample: standard plan and backfill; opt-out rule)",
     "args": ["--date", "2026-11-03"], "jobs": TESTS / "jobs.csv",
     "sample": ("S3", "Sample 'Customer list includes customers marked do-not-contact near a gap', expected: those "
                      "customers never appear in suggestions", None)},
    {"name": "unreachable window (sample: unassignable job)",
     "args": ["--date", "2026-11-03"], "jobs": FIX / "jobs-unreachable.csv",
     "sample": ("S2", "Sample 'A job with a time window no crew member can reach', expected: job listed as "
                      "unassigned, with the reason", "U1")},
    {"name": "one week plan (sample: multi-day gaps)",
     "args": ["--date", "2026-11-03", "--date-to", "2026-11-09"], "jobs": TESTS / "jobs-week.csv"},
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def yes(value):
    return (value or "").strip().lower() in ("yes", "true", "1", "y")


class Places:
    """Drive minutes from the committed fixture places file."""

    def __init__(self, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.places = data["places"]
        self.speed = float(data["travel"].get("speed_kmh", 40.0))

    def minutes(self, a, b):
        pa, pb = self.places.get(a), self.places.get(b)
        if pa is None or pb is None:
            return None
        la1, lo1, la2, lo2 = map(math.radians, (pa["lat"], pa["lon"], pb["lat"], pb["lon"]))
        h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
        km = 2 * 6371.0088 * math.asin(math.sqrt(h))
        return km / self.speed * 60.0


def parse_report(text):
    """The report's day sections: schedule rows, unassigned, gaps, suggestions."""
    days = {}
    for block in re.split(r"^## Day ", text, flags=re.M)[1:]:
        day = block[:10]
        sched = {}
        for m in re.finditer(r"^#### ([^\n]+?) \((\w+)\), (\d\d:\d\d) to (\d\d:\d\d), skills: ([^\n]*)\n\n(.*?)(?=^#### |^Total drive time, all crew|\Z)",
                             block, re.M | re.S):
            rows = []
            for r in re.finditer(r"^\| (\d+) \| (\S+) \| (.*?) \| (.*?) \| (\d+) \| (\d\d:\d\d) \| (\d\d:\d\d) \| (\d\d:\d\d) \| (\d\d:\d\d) to (\d\d:\d\d) \|$",
                                 m.group(6), re.M):
                rows.append({"job": r.group(2), "address": r.group(4), "drive": int(r.group(5)),
                             "start": ac.hhmm(r.group(7)), "end": ac.hhmm(r.group(8))})
            start = re.search(r"^Start: (.*?)\. Total drive time", m.group(6), re.M)
            sched[m.group(2)] = {"name": m.group(1), "rows": rows, "start_address": start.group(1) if start else None,
                                 "no_route": "No route:" in m.group(6)}
        total = re.search(r"^Total drive time, all crew: (\d+) min, against (\d+) min(.*)$", block, re.M)
        unassigned = re.findall(r"^- Job (\S+) \((.*?)\): (.+)$", block.split("### Unassigned jobs", 1)[1].split("### Gaps", 1)[0], re.M)
        gaps = []
        for g in re.finditer(r"^- (.+?) \((\w+)\): (\d\d:\d\d) to (\d\d:\d\d), (\d+) min free after driving; area: (.+)$",
                             block.split("### Gaps", 1)[1].split("### Ranked backfill suggestions", 1)[0], re.M):
            gaps.append({"crew": g.group(2), "from": ac.hhmm(g.group(3)), "to": ac.hhmm(g.group(4)),
                         "free": int(g.group(5)), "area": g.group(6)})
        sugg = []
        part = block.split("### Ranked backfill suggestions", 1)[1]
        for s in re.finditer(r"^#### ([^\n]+?) \((\w+)\), gap (\d\d:\d\d) to (\d\d:\d\d):[^\n]*\n\n(.*?)(?=^#### |\Z)", part, re.M | re.S):
            for item in re.finditer(r"^\d+\. \*\*(.+?)\*\* \((\w+)\), (.*?)\. Certainty: .*?Could arrive about (\d\d:\d\d)\. Reason: (.*)$",
                                    s.group(5), re.M):
                sugg.append({"crew": s.group(2), "gap_from": ac.hhmm(s.group(3)), "gap_to": ac.hhmm(s.group(4)),
                             "name": item.group(1), "id": item.group(2), "address": item.group(3),
                             "arrive": ac.hhmm(item.group(4)), "reason": item.group(5), "day": day})
        days[day] = {"sched": sched, "total": total, "unassigned": unassigned, "gaps": gaps, "sugg": sugg}
    return days


def settings(text):
    m = re.search(r"gaps of at least (\d+) min are reported; a backfill visit is assumed to take (\d+) min", text)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def new_result(case):
    res = ac.Result(AGENT, case["name"], SOURCE)
    return res, {k: res.criterion(k, v) for k, v in CRITERIA.items()}


def check_case(case, planner):
    res, c = new_result(case)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "plan.report.md"
        attempts = []
        argv = ["plan"] + case["args"] + ["--jobs", str(case["jobs"]), "--crew", str(TESTS / "crew.csv"),
                                          "--customers", str(TESTS / "customers.csv"),
                                          "--places", str(TESTS / "places.json"), "--out", str(out)]
        code, _, err = ac.run_main(lambda a: planner.main(a, env={}), argv, attempts=attempts)
        if code != 0 or not out.is_file():
            for k in c:
                c[k].fail("plan exited %s with no report: %s" % (code, err.strip()[:200]))
            return res
        text = out.read_text(encoding="utf-8")
    return evaluate(res, c, text, case, attempts)


def evaluate(res, c, text, case, attempts):
    """Check one written report against every criterion (split out so a
    test can feed a tampered report and see the check fail)."""
    jobs = read_csv(case["jobs"])
    crew = {r["crew_id"]: r for r in read_csv(TESTS / "crew.csv")}
    customers = {r["customer_id"]: r for r in read_csv(TESTS / "customers.csv")}
    places = Places(TESTS / "places.json")
    days = parse_report(text)
    min_gap, visit = settings(text)

    # 1. every job scheduled or unassigned with a reason
    scheduled = {r["job"] for d in days.values() for s in d["sched"].values() for r in s["rows"]}
    unassigned = {u[0]: u[2] for d in days.values() for u in d["unassigned"]}
    for row in jobs:
        jid = row["job_id"]
        if jid in scheduled:
            continue
        if jid in unassigned and unassigned[jid].strip():
            c["1"].ok("%s unassigned: %s" % (jid, unassigned[jid][:80]))
            continue
        dp = re.search(r"^- jobs row \d+ \(%s\) dropped: (.*)$" % re.escape(jid), text, re.M)
        c["1"].fail("job %s is in neither a schedule nor the unassigned list%s"
                    % (jid, "; it appears only under Data problems: %s" % dp.group(1) if dp else ""))
    c["1"].ok("%d of %d input jobs scheduled, %d listed as unassigned" % (len(scheduled), len(jobs), len(unassigned)))

    # 2. hours, windows, skills, recomputed from the CSV rows
    by_id = {r["job_id"]: r for r in jobs}
    n = 0
    for d in days.values():
        for cid, s in d["sched"].items():
            cr = crew[cid]
            have = {x.strip() for x in cr["skills"].split(";") if x.strip()}
            for r in s["rows"]:
                n += 1
                j = by_id[r["job"]]
                need = {x.strip() for x in j["skills"].split(";") if x.strip()}
                if r["start"] < ac.hhmm(cr["shift_start"]) or r["end"] > ac.hhmm(cr["shift_end"]):
                    c["2"].fail("%s on %s %s to %s is outside shift %s to %s" % (r["job"], cid, *map(fmt, (r["start"], r["end"])), cr["shift_start"], cr["shift_end"]))
                if not ac.hhmm(j["window_start"]) <= r["start"] <= ac.hhmm(j["window_end"]):
                    c["2"].fail("%s starts %s, outside its window %s to %s" % (r["job"], fmt(r["start"]), j["window_start"], j["window_end"]))
                if r["end"] - r["start"] != int(j["duration_minutes"]):
                    c["2"].fail("%s runs %d min, the input says %s" % (r["job"], r["end"] - r["start"], j["duration_minutes"]))
                if not need <= have:
                    c["2"].fail("%s needs %s; %s has %s" % (r["job"], sorted(need), cid, sorted(have)))
    c["2"].ok("%d scheduled stops checked against crew.csv hours and skills and the job windows and durations" % n)

    # 3. provider named; a live routing service cannot be exercised offline
    prov = re.search(r"^- Geocoding and drive times: (.*?)(?: \(|;)", text, re.M)
    c["3"].check(bool(prov), "report names the provider: %s" % (prov.group(1) if prov else ""),
                 "no 'Geocoding and drive times' line naming the provider")
    c["3"].cannot("offline run on the fixture places file; whether live drive times come from a routing "
                  "service needs a --live run, which this offline test does not make")

    # 4. plan total vs the given order, recomputed from the places file
    for day, d in days.items():
        plan_total = sum(r["drive"] for s in d["sched"].values() for r in s["rows"])
        given = 0.0
        order = [j["job_id"] for j in jobs]
        for cid, s in d["sched"].items():
            here = s["start_address"]
            for jid in sorted((r["job"] for r in s["rows"]), key=order.index):
                given += places.minutes(here, by_id[jid]["address"]) or 0
                here = by_id[jid]["address"]
        t = d["total"]
        if not t:
            c["4"].fail("%s: no 'Total drive time, all crew' line" % day)
            continue
        rep_plan, rep_given, tail = int(t.group(1)), int(t.group(2)), t.group(3)
        if abs(rep_plan - plan_total) > len(d["sched"]) * ROUNDING + 1:
            c["4"].fail("%s: report total %d min, the stop drives add to %d" % (day, rep_plan, plan_total))
        if abs(rep_given - given) > len([r for s in d["sched"].values() for r in s["rows"]]) * ROUNDING + 1:
            c["4"].fail("%s: report gives %d min for the file order, recomputed %.1f" % (day, rep_given, given))
        if rep_plan < rep_given:
            c["4"].ok("%s: plan %d min against %d min in the given order" % (day, rep_plan, rep_given))
        elif "shortest" in tail or "because" in tail or "not lower" in tail:
            c["4"].ok("%s: not lower (%d against %d), explained: %s" % (day, rep_plan, rep_given, tail.strip()[:120]))
        else:
            c["4"].fail("%s: plan %d min is not lower than %d and no explanation follows" % (day, rep_plan, rep_given))

    # 5. every free stretch of at least the minimum is listed, recomputed from the schedule
    if min_gap is None:
        c["5"].fail("the report does not print the minimum gap setting")
    for day, d in days.items():
        listed = {(g["crew"], g["from"], g["to"]) for g in d["gaps"]}
        for g in d["gaps"]:
            if not g["area"].strip():
                c["5"].fail("%s gap %s on %s has no area" % (day, fmt(g["from"]), g["crew"]))
        for cid, s in d["sched"].items():
            if s["no_route"]:
                continue
            cr = crew[cid]
            t, here = ac.hhmm(cr["shift_start"]), s["start_address"]
            for r in s["rows"] + [None]:
                if r is None:
                    end, drive, nxt = ac.hhmm(cr["shift_end"]), 0, None
                else:
                    end, drive, nxt = r["start"], places.minutes(here, by_id[r["job"]]["address"]) or 0, r
                free = end - t - drive
                if min_gap is not None and free >= min_gap + ROUNDING:
                    if (cid, t, end) not in listed:
                        c["5"].fail("%s %s: %s to %s has about %d free min (minimum %d) and is not listed"
                                    % (day, cid, fmt(t), fmt(end), free, min_gap))
                if nxt:
                    t, here = nxt["end"], by_id[nxt["job"]]["address"]
        c["5"].ok("%s: %d gap(s) listed, each with crew, time and area" % (day, len(d["gaps"])))
    c["5"].ok("minimum gap printed in the report: %s min" % min_gap)

    # 6. a suggestion keeps the next job's planned start, recomputed
    sugg = [x for d in days.values() for x in d["sugg"]]
    for x in sugg:
        s = days[x["day"]]["sched"][x["crew"]]
        nxt = next((r for r in s["rows"] if r["start"] >= x["gap_to"] and r["start"] == x["gap_to"]), None)
        done = x["arrive"] + (visit or 0)
        if nxt is None:
            limit = ac.hhmm(crew[x["crew"]]["shift_end"])
            ok = done <= limit + ROUNDING
            c["6"].check(ok, "%s ends %s, inside the shift end %s" % (x["id"], fmt(done), fmt(limit)),
                         "%s ends %s, after the shift end %s" % (x["id"], fmt(done), fmt(limit)))
            continue
        drive = places.minutes(x["address"], by_id[nxt["job"]]["address"])
        if drive is None:
            c["6"].cannot("%s: address not in the places file, so the onward drive cannot be recomputed" % x["id"])
            continue
        reach = done + drive
        c["6"].check(reach <= nxt["start"] + ROUNDING,
                     "%s: arrive %s, %d min visit, %.0f min on, reaches %s by %s (planned %s)"
                     % (x["id"], fmt(x["arrive"]), visit, drive, nxt["job"], fmt(reach), fmt(nxt["start"])),
                     "%s: reaches %s at %s, after its planned start %s" % (x["id"], nxt["job"], fmt(reach), fmt(nxt["start"])))
    if not sugg:
        c["6"].cannot("this case produced no suggestions")

    # 7. due according to the data, with the reason
    for x in sugg:
        row = customers.get(x["id"])
        if row is None:
            c["7"].fail("suggested %s is not in customers.csv" % x["id"])
            continue
        reason = x["reason"]
        if (row.get("open_quote") or "").strip():
            c["7"].check(row["open_quote"].strip() in reason, "%s: open quote %r on record and in the reason" % (x["id"], row["open_quote"]),
                         "%s: open quote not stated in the reason" % x["id"])
            continue
        if reason.startswith("assumption based"):
            c["7"].cannot("%s: ranked as assumption based (%s); whether an assumed interval counts as 'due according "
                          "to the data provided' is not settled by the posting" % (x["id"], reason.split(";")[0][:110]))
            continue
        m = re.search(r"due since (\d{4}-\d\d-\d\d) \((\w+) plan, last service (\d{4}-\d\d-\d\d)\)", reason)
        if not m:
            c["7"].fail("%s: reason gives no due arithmetic: %s" % (x["id"], reason[:100]))
            continue
        due, plan, last = date.fromisoformat(m.group(1)), m.group(2), m.group(3)
        if last != (row.get("last_service_date") or "").strip() or plan != (row.get("service_plan") or "").strip().lower():
            c["7"].fail("%s: reason says %s plan, last %s; customers.csv says %r, %r"
                        % (x["id"], plan, last, row.get("service_plan"), row.get("last_service_date")))
        elif due > date.fromisoformat(x["day"]):
            c["7"].fail("%s: due %s, after the day %s" % (x["id"], due, x["day"]))
        else:
            c["7"].ok("%s: last service %s on a %s plan, due %s, on or before %s" % (x["id"], last, plan, due, x["day"]))
    if not sugg:
        c["7"].cannot("this case produced no suggestions")

    # 8. never a do-not-contact or opted-out customer
    blocked = {k for k, r in customers.items() if yes(r.get("do_not_contact")) or yes(r.get("opted_out"))}
    hit = [x["id"] for x in sugg if x["id"] in blocked]
    names = [customers[k]["name"] for k in blocked]
    tail = text.split("## Outreach drafts", 1)[-1]
    in_drafts = [n for n in names if ("Draft for %s (" % n) in tail]
    c["8"].check(not hit and not in_drafts,
                 "%d flagged customer(s) in customers.csv (%s); none suggested or drafted" % (len(blocked), ", ".join(sorted(blocked))),
                 "flagged customer(s) suggested: %s; drafted: %s" % (hit, in_drafts))

    # 9. a draft per suggestion, nothing sent
    drafts = set(re.findall(r"^### Draft for .*? \((\w+)\), suggestion \d+ in", text, re.M))
    missing = sorted({x["id"] for x in sugg} - drafts)
    c["9"].check(not missing, "%d suggestion(s), %d draft(s), one per suggested customer" % (len(sugg), len(drafts)),
                 "suggested with no draft: %s" % missing)
    c["9"].check(not attempts, "no network access attempted during the run (guard recorded none)",
                 "network access attempted: %s" % attempts[:3])
    sample = case.get("sample")
    if sample:
        s = res.criterion(sample[0], sample[1])
        if sample[0] == "S2":
            reason = unassigned.get(sample[2], "")
            s.check(bool(reason.strip()), "%s listed as unassigned: %s" % (sample[2], reason[:100]),
                    "%s is not in the unassigned list" % sample[2])
        if sample[0] == "S3":
            near = [k for k in blocked if customers[k]["address"] in places.places]
            s.check(bool(near) and not hit, "flagged customer(s) %s are placed in the area and none is suggested" % sorted(near),
                    "flagged customers placed in the area: %s; suggested: %s" % (sorted(near), hit))
    return res


def fmt(minutes):
    minutes = int(round(minutes))
    return "%02d:%02d" % divmod(minutes, 60)


def run():
    planner = ac.load("acceptance_planner", HERE.parent / "planner.py")
    return [check_case(case, planner) for case in CASES]


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
