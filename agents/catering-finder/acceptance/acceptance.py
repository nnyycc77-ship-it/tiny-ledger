"""Acceptance self test: Catering & Group Dining Finder (issue #124).

Runs the catering finder the way a marketplace tester would, offline, on
the committed synthetic vendor store:
- `draft`, then the operator's `record-sent` and `record-reply` steps into
  a temporary log;
- `run` for the report.

It then checks the report against the job posting's Acceptance Criteria,
quoted by the coordinator on issue #75 (comment 6365588905). Each
criterion is printed as PASS, FAIL or UNTESTABLE with its evidence.

The checks go back to the sources rather than trusting the report:
- every quoted excerpt must be the vendor page's own line, or the reply
  text recorded in the log;
- every figure must appear in that excerpt;
- every draft must carry the on behalf of a customer and automated
  assistant disclosure;
- the brief's synthetic buyer contact must appear nowhere.

Run:  python3 agents/catering-finder/acceptance/acceptance.py
"""

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "catering-finder"
SOURCE = "job posting, Acceptance Criteria, issue #75 comment 6365588905"
STORE = HERE.parent / "tests" / "fixtures"
FIX = HERE / "fixtures"

CRITERIA = {
    "1": "Every vendor in the report offers the requested service style in the requested area, and the report "
         "lists every vendor contacted.",
    "2": "Every price, minimum spend and deposit in the report is exactly what the vendor stated. No estimated "
         "or invented numbers.",
    "3": "For each vendor, the report shows whether each dietary need in the brief can be covered, and marks it "
         "\"not confirmed\" when the vendor didn't say.",
    "4": "The report separates vendors who confirmed availability for the date from those who didn't.",
    "5": "The report includes vendors who didn't reply or declined, not only those who quoted.",
    "6": "Every message or call says it is on behalf of a customer, and the agent never books, pays a deposit, "
         "or shares the buyer's contact details without approval.",
    "7": "The report is delivered at the end of the collection window stated in the listing, even if some "
         "vendors haven't replied.",
}

CASES = [
    {"name": "office buffet, 60 guests (sample: catering, dietary needs)",
     "brief": STORE / "brief.json", "log": STORE / "outreach-log.json"},
    {"name": "dinner for 150 (sample: thin coverage, large headcount)",
     "brief": FIX / "brief-150.json", "log": None, "replies": FIX / "replies-150.json",
     "sample": ("S3", "Sample 'Dinner for 150 guests in a small town', expected: report says how many vendors can "
                      "handle that size and how many responded, no padding")},
    {"name": "budget per head below some prices (sample: set budget)",
     "brief": FIX / "brief-budget.json", "log": None,
     "sample": ("S2", "Sample 'set budget per person', expected: over-budget options marked clearly")},
]

NUM = re.compile(r"\d+(?:\.\d+)?")


def page_lines(vendor_id):
    return (STORE / "vendors" / ("%s.html" % vendor_id)).read_text(encoding="utf-8").splitlines()


def build_log(case, finder, tmp, attempts):
    """The committed log, or a fresh one built through the agent's commands."""
    if case["log"] is not None:
        return case["log"]
    log = Path(tmp) / "outreach-log.json"
    steps = [["draft", "--brief", str(case["brief"]), "--store", str(STORE), "--log", str(log)]]
    if case.get("replies"):
        rec = json.loads(case["replies"].read_text(encoding="utf-8"))
        steps += [["record-sent", s["vendor"], "--log", str(log), "--when", s["when"]] for s in rec["sent"]]
        steps += [["record-reply", r["vendor"], "--log", str(log), "--when", r["when"], "--text", r["text"]]
                  for r in rec["replies"]]
    for argv in steps:
        code, _, err = ac.run_main(lambda a: finder.main(a, env={}), argv, attempts=attempts)
        if code != 0:
            raise RuntimeError("%s exited %s: %s" % (argv[0], code, err.strip()[:200]))
    return log


def new_result(case):
    res = ac.Result(AGENT, case["name"], SOURCE)
    return res, {k: res.criterion(k, v) for k, v in CRITERIA.items()}


def check_case(case, finder):
    res, c = new_result(case)
    attempts = []
    with tempfile.TemporaryDirectory() as tmp:
        try:
            log = build_log(case, finder, tmp, attempts)
        except RuntimeError as exc:
            for k in c:
                c[k].fail(str(exc))
            return res
        out = Path(tmp) / "report.md"
        code, _, err = ac.run_main(lambda a: finder.main(a, env={}),
                                   ["run", "--brief", str(case["brief"]), "--store", str(STORE), "--log", str(log),
                                    "--out", str(out)], attempts=attempts)
        if code != 0 or not out.is_file():
            for k in c:
                c[k].fail("run exited %s with no report: %s" % (code, err.strip()[:200]))
            return res
        text = out.read_text(encoding="utf-8")
        log_data = json.loads(Path(log).read_text(encoding="utf-8"))
        send_refusals = [ac.run_main(lambda a: finder.main(a, env={}), argv, attempts=attempts)[0]
                         for argv in (["send", "pecan-grove", "--log", str(log)],
                                      ["send", "pecan-grove", "--log", str(log), "--hire-id", "acceptance-probe",
                                       "--execute"])]
    return evaluate(res, c, text, case, log_data, send_refusals, attempts)


def evaluate(res, c, text, case, log_data, send_refusals, attempts):
    brief = json.loads(Path(case["brief"]).read_text(encoding="utf-8"))
    index = {v["name"]: v for v in json.loads((STORE / "index.json").read_text(encoding="utf-8"))["vendors"]}
    drafts = log_data.get("drafts", {})
    summary = text.split("## Summary", 1)[1].split("## Availability for", 1)[0]
    rows = [r for r in summary.splitlines() if r.startswith("| ") and not r.startswith("| Vendor") and not r.startswith("| ---")]
    header = [h.strip() for h in summary.split("\n| Vendor", 1)[1].split("\n", 1)[0].split("|")[1:-1]] if rows else []
    header = ["Vendor"] + header
    table = [dict(zip(header, [x.strip() for x in r.split(" | ")])) for r in rows]
    compared = [t["Vendor"].lstrip("| ").strip() for t in table]
    sections = dict(re.findall(r"^### (.+?)\n(.*?)(?=^### |^## )", text.split("## Vendors compared", 1)[1] + "\n## ",
                               re.M | re.S))

    # 1. style and area verified on the vendor's own page; every contacted vendor listed
    city = brief["location"].split(",")[0].strip().lower()
    style = brief["service_style"].lower()
    for name in compared:
        sec, v = sections.get(name, ""), index.get(name)
        lines = page_lines(v["id"]) if v else []
        sm = re.search(r"Service style match as shown: .*?\n  Source: <.*?> \(line (\d+)\)", sec)
        am = re.search(r"Area match as shown: .*?\n  Source: <.*?> \(line (\d+)\)", sec)
        s_line = lines[int(sm.group(1)) - 1].lower() if sm and v else ""
        a_line = lines[int(am.group(1)) - 1].lower() if am and v else ""
        c["1"].check(style in s_line and city in a_line,
                     "%s: page line %s names %r, line %s names %r" % (name, sm.group(1) if sm else "?", style,
                                                                     am.group(1) if am else "?", city),
                     "%s: the page lines quoted do not name both %r and %r" % (name, style, city))
    contacted = [d["vendor"] for d in drafts.values() if d.get("sent_utc")]
    missing = [n for n in contacted if n not in text]
    c["1"].check(not missing, "%d contacted vendor(s) in the log, all named in the report" % len(contacted),
                 "contacted but not in the report: %s" % missing)

    # 2. every quoted excerpt is the vendor's own words; every figure is in it
    replies = {d["vendor"]: (d.get("reply") or {}).get("text", "") for d in drafts.values()}
    nquotes = 0
    for name, sec in sections.items():
        v = index.get(name)
        lines = page_lines(v["id"]) if v else []
        for claim, src, line_no, block in re.findall(
                r"^- ([^\n]*)\n  Source: (<[^\n]*?> \(line (\d+)\)|vendor reply recorded in the outreach log)\n  ```\n  ([^\n]*)\n  ```",
                sec, re.M | re.S):
            nquotes += 1
            source_text = lines[int(line_no) - 1].strip() if line_no else replies.get(name, "")
            if block.strip() != source_text.strip():
                c["2"].fail("%s: excerpt is not the source's own text: %r" % (name, block[:80]))
                continue
            if re.search(r"price|minimum|deposit|capacity", claim, re.I):
                for n in NUM.findall(claim.split("as shown:", 1)[-1] if "as shown:" in claim else claim.split(":", 1)[-1]):
                    val = float(n)
                    if not any(abs(float(x) - val) < 1e-9 for x in NUM.findall(source_text)):
                        c["2"].fail("%s: figure %s in %r is not in the quoted source" % (name, n, claim[:80]))
    for t in table:
        cell = t.get("Price per person (as stated)", "")
        name = t["Vendor"].lstrip("| ").strip()
        for n in NUM.findall(cell):
            sec = sections.get(name, "")
            if n not in sec:
                c["2"].fail("%s: summary price %s is not stated anywhere in the vendor's section" % (name, n))
    c["2"].ok("%d quoted excerpt(s) matched the vendor page line or the recorded reply verbatim; every price, "
              "minimum, deposit and capacity figure appears in its excerpt" % nquotes)
    if re.search(r"(?i)\btotal (?:of|for) \$?\d|\bestimated? (?:price|total|cost)", text.split("## Outreach drafts", 1)[0]):
        c["2"].fail("the report states a total or an estimate outside the drafts")

    # 3. one of three states per vendor and need; silence is "not confirmed"
    needs = brief["dietary_needs"]
    for name, sec in sections.items():
        states = re.findall(r"^- Dietary, (.*?): (CONFIRMED|STATED|NOT CONFIRMED)", sec, re.M)
        if len(states) != len(needs):
            c["3"].fail("%s: %d dietary line(s) for %d need(s) in the brief" % (name, len(states), len(needs)))
            continue
        for need_label, state in states:
            if state == "CONFIRMED":
                m = re.search(r"^- Dietary, %s: CONFIRMED by the vendor's page.*?\n  Source: <.*?> \(line (\d+)\)"
                              % re.escape(need_label), sec, re.M | re.S)
                if not m:
                    c["3"].fail("%s: %s marked confirmed with no page line quoted" % (name, need_label))
            elif state == "STATED":
                if not replies.get(name):
                    c["3"].fail("%s: %s marked stated but no reply is recorded" % (name, need_label))
        c["3"].ok("%s: %s" % (name, "; ".join("%s %s" % s for s in states)))
    if "not confirmed" not in text.lower():
        c["3"].cannot("no vendor in this case was silent on a need, so the 'not confirmed' path is not exercised")

    # 4. availability separated, confirmed only from an answer
    avail = text.split("## Availability for", 1)[1].split("## Vendors compared", 1)[0]
    conf = re.search(r"^- Confirmed by the vendor's answer: (.*)$", avail, re.M)
    notc = re.search(r"^- Not confirmed .*?: (.*)$", avail, re.M)
    if not (conf and notc):
        c["4"].fail("the availability section does not separate confirmed from not confirmed")
    else:
        for name in [x.strip() for x in conf.group(1).split(",") if x.strip() and x.strip() != "none"]:
            entry = next((d for d in drafts.values() if d["vendor"] == name), {})
            c["4"].check(bool((entry.get("reply") or {}).get("text")),
                         "%s listed as confirmed, with a recorded answer" % name,
                         "%s listed as confirmed with no recorded answer" % name)
        c["4"].ok("confirmed: %s | not confirmed: %s" % (conf.group(1).strip(), notc.group(1).strip()))

    # 5. non responders and decliners kept
    no_reply = [d["vendor"] for d in drafts.values() if d.get("sent_utc") and not d.get("reply")]
    nr_sec = text.split("## Contacted with no reply", 1)[1].split("## Declined", 1)[0] if "## Contacted with no reply" in text else ""
    for name in no_reply:
        c["5"].check(name in nr_sec, "%s (contacted, no reply) listed under Contacted with no reply" % name,
                     "%s was contacted with no reply and is not listed" % name)
    dec = re.findall(r"^- (.+?): answer received", text.split("## Declined", 1)[1].split("## Checked and excluded", 1)[0], re.M) \
        if "## Declined" in text else []
    declined_rows = [t["Vendor"].lstrip("| ").strip() for t in table if "declined" in t.get(
        [h for h in header if h.startswith("Availability for")][0] if any(h.startswith("Availability for") for h in header) else "", "")]
    for name in declined_rows:
        c["5"].check(name in dec, "%s (declined) listed under Declined" % name, "%s declined and is not listed" % name)
    if not no_reply and not declined_rows:
        c["5"].cannot("no vendor in this case was contacted without reply or declined")

    # 6. disclosure in every draft; no booking; no buyer contact
    for d in drafts.values():
        msg = d.get("message", "")
        c["6"].check("on behalf of a customer" in msg and "automated assistant" in msg,
                     "%s: draft says 'on behalf of a customer' and 'automated assistant'" % d["vendor"],
                     "%s: draft lacks the on behalf of a customer or automated assistant disclosure" % d["vendor"])
    contact = brief.get("_buyer_contact")
    if contact:
        everywhere = text + json.dumps(log_data)
        c["6"].check(contact not in everywhere, "the brief's buyer contact %r appears in no draft and not in the report" % contact,
                     "the buyer contact %r leaked into the drafts or the report" % contact)
    c["6"].check(all(code != 0 for code in send_refusals),
                 "send refused without a hire id, and refused again with --hire-id and --execute (exit %s)" % send_refusals,
                 "send did not refuse: exit codes %s" % send_refusals)
    c["6"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])
    own_words = re.sub(r"```.*?```", "", text, flags=re.S)  # vendor excerpts and drafts are not the agent's claims
    if re.search(r"(?i)\b(we booked|booking (?:is )?confirmed|deposit (?:was )?paid|quote accepted)\b", own_words):
        c["6"].fail("the report says the agent booked, paid a deposit or accepted a quote")

    # 7. delivered at the end of the window even with vendors outstanding
    window = re.search(r"Collection window: (.*?)\.", text)
    deadline = brief.get("response_deadline_utc")
    if deadline:
        c["7"].check(window and deadline in window.group(1), "report states the window: %s" % (window.group(1) if window else ""),
                     "report does not state the brief's window end %s" % deadline)
    pending = len(no_reply) + len([d for d in drafts.values() if not d.get("sent_utc")])
    c["7"].ok("a complete report was produced with %d vendor(s) still without an answer" % pending)
    c["7"].cannot("sending the report at the window's end is a scheduling step outside one offline run; the listing's "
                  "default window is the README's three days, not something a run can show")
    sample = case.get("sample")
    if sample:
        s = res.criterion(*sample)
        if sample[0] == "S3":
            m = re.search(r"^Counts: (\d+) vendor\(s\) compared; (\d+) state a capacity of at least %d on their page; "
                          r"(\d+) contacted; (\d+) replied" % brief["headcount"], text, re.M)
            fits = [t["Vendor"].lstrip("| ").strip() for t in table if "(fits)" in t.get("Capacity", "")]
            s.check(bool(m) and int(m.group(2)) == len(fits),
                    "counts line: %s" % (m.group(0) if m else ""),
                    "no counts line giving capacity at %d and replies, or it disagrees with the table" % brief["headcount"])
        if sample[0] == "S2":
            per_head = brief["budget_usd"] / brief["headcount"]
            for t in table:
                name, cell = t["Vendor"].lstrip("| ").strip(), t.get("Against budget per head", "")
                prices = [float(x) for x in NUM.findall(t.get("Price per person (as stated)", ""))]
                if prices and min(prices) > per_head:
                    s.check(cell.startswith("over budget"), "%s: %s" % (name, cell),
                            "%s: stated %s above %.2f per head but not marked over budget: %s" % (name, prices, per_head, cell))
            if not s.passes and not s.fails:
                s.cannot("no vendor's stated price is above the budget per head in this case")
    return res


def run():
    finder = ac.load("acceptance_catering", HERE.parent / "catering_finder.py")
    return [check_case(case, finder) for case in CASES]


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
