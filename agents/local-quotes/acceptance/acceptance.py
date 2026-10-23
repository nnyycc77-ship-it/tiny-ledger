"""Acceptance self test: Local Services Quote Agent (issue #124).

Runs the quote agent the way a marketplace tester would, offline, on the
committed synthetic provider store: `draft` into a temporary log, or the
committed log, then `run` with a fixed report time after the collection
window closed. It checks the report against the job posting's Acceptance
Criteria, quoted by the coordinator on issue #76 (comment 6366190586). Each
criterion is printed as PASS, FAIL or UNTESTABLE with its evidence.

The checks go back to the sources:
- every quoted excerpt must be the provider page's own line, or the reply
  recorded in the log;
- every price in the comparison must be in its source;
- every draft must carry the on behalf of a customer disclosure;
- the request's synthetic buyer contact must appear nowhere.

Run:  python3 agents/local-quotes/acceptance/acceptance.py
"""

import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENT = "local-quotes"
SOURCE = "job posting, Acceptance Criteria, issue #76 comment 6366190586"
STORE = HERE.parent / "tests" / "fixtures"
FIX = HERE / "fixtures"
NOW = "2026-11-05T09:00:00Z"  # after both requests' window end, 2026-11-04T17:00:00Z

CRITERIA = {
    "1": "Every provider contacted offers the requested service in the requested area, and the report lists all of them.",
    "2": "Every price and detail in the report is exactly what a provider stated. No estimated or invented numbers.",
    "3": "The report includes providers who didn't reply or declined, not only those who quoted.",
    "4": "When quotes cover different things (for example, one includes materials and another doesn't), the report "
         "points out the difference.",
    "5": "Every message or call says it is on behalf of a customer, and the agent never accepts a quote, books, or "
         "shares the buyer's contact details without approval.",
    "6": "The report is delivered at the end of the collection window stated in the listing, even if some providers "
         "haven't replied.",
}

CASES = [
    {"name": "water heater replacement (sample: standard request; budget limit)",
     "request": STORE / "request.json", "log": STORE / "outreach-log.json",
     "sample": ("S2", "Sample 'quotes within budget', expected: over-budget quotes marked clearly, not hidden")},
    {"name": "drain cleaning, few providers (sample: thin coverage)",
     "request": FIX / "request-thin.json", "log": None,
     "sent": [["record-sent", "riverside-rooter", "--channel", "web_form", "--when", "2026-11-01T15:00:00Z"]],
     "sample": ("S3", "Sample 'Rare service in a small town with few providers', expected: report says how many "
                      "providers exist and responded, no padding")},
]

MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)")


def page_lines(pid):
    return (STORE / "providers" / ("%s.html" % pid)).read_text(encoding="utf-8").splitlines()


def new_result(case):
    res = ac.Result(AGENT, case["name"], SOURCE)
    return res, {k: res.criterion(k, v) for k, v in CRITERIA.items()}


def check_case(case, agent):
    res, c = new_result(case)
    attempts = []
    call = lambda a: agent.main(a, env={})  # noqa: E731
    with tempfile.TemporaryDirectory() as tmp:
        log = case["log"]
        if log is None:
            log = Path(tmp) / "outreach-log.json"
            code, _, err = ac.run_main(call, ["draft", "--request", str(case["request"]), "--store", str(STORE),
                                              "--log", str(log), "--now", "2026-11-01T14:00:00Z"], attempts=attempts)
            for argv in case.get("sent", []):  # SYNTHETIC operator records, nothing is sent
                if code == 0:
                    code, _, err = ac.run_main(call, argv + ["--log", str(log)], attempts=attempts)
            if code != 0:
                for k in c:
                    c[k].fail("draft or record-sent exited %s: %s" % (code, err.strip()[:200]))
                return res
        out = Path(tmp) / "report.md"
        code, _, err = ac.run_main(call, ["run", "--request", str(case["request"]), "--store", str(STORE),
                                          "--log", str(log), "--now", NOW, "--out", str(out)], attempts=attempts)
        if code != 0 or not out.is_file():
            for k in c:
                c[k].fail("run exited %s with no report: %s" % (code, err.strip()[:200]))
            return res
        text = out.read_text(encoding="utf-8")
        log_data = json.loads(Path(log).read_text(encoding="utf-8"))
        first = next(iter(log_data.get("providers", {})), "barton-creek")
        refusals = [ac.run_main(call, argv, attempts=attempts)[0] for argv in
                    (["send", first, "--log", str(log)],
                     ["send", first, "--log", str(log), "--hire-id", "acceptance-probe", "--execute"])]
    return evaluate(res, c, text, case, log_data, refusals, attempts)


def evaluate(res, c, text, case, log_data, refusals, attempts):
    request = json.loads(Path(case["request"]).read_text(encoding="utf-8"))
    index = {p["id"]: p for p in json.loads((STORE / "index.json").read_text(encoding="utf-8"))["providers"]}
    by_name = {p["name"]: pid for pid, p in index.items()}
    providers = log_data.get("providers", {})
    replies = {pid: (p.get("reply") or {}).get("text", "") for pid, p in providers.items()}
    contacted = [pid for pid, p in providers.items() if any(a.get("sent_utc") for a in p.get("attempts", []))]
    sections = dict(re.findall(r"^## (.+?)\n(.*?)(?=^## )", text + "\n## ", re.M | re.S))
    table = text.split("## Comparison", 1)[1].split("\n\n", 2)[1] if "## Comparison" in text else ""
    rows = [r for r in table.splitlines() if r.startswith("| ") and not r.startswith("| Provider") and not r.startswith("| ---")]
    head = ["Provider", "Price as stated", "Price type", "Against budget", "Availability", "Site visit", "Included",
            "Not included", "Requirements", "Status"]
    table_rows = [dict(zip(head, [x.strip() for x in r.strip("| ").split(" | ")])) for r in rows]

    # 1. verified service and area on the provider's own page; every contacted provider listed
    service_words = request["service"].lower().split()
    city = request["location"].split(",")[0].strip().lower()
    for pid in contacted:
        name = index[pid]["name"]
        sec = sections.get(name, "")
        lines = page_lines(pid)
        sv = re.search(r"Service offered as shown: .*?\n  Source: <.*?> \(line (\d+)\)", sec)
        ar = re.search(r"Area served as shown: .*?\n  Source: <.*?> \(line (\d+)\)", sec)
        s_line = lines[int(sv.group(1)) - 1].lower() if sv else ""
        a_line = lines[int(ar.group(1)) - 1].lower() if ar else ""
        ok = bool(sec) and any(w in s_line for w in service_words) and city in a_line
        c["1"].check(ok, "%s: page line %s names the service, line %s names %r" % (name, sv.group(1) if sv else "?",
                                                                                   ar.group(1) if ar else "?", city),
                     "%s was contacted but its section does not show the service and area from its own page" % name)
    if not contacted:
        c["1"].ok("no provider contacted in this case; %d drafted" % len(providers))
    for pid in providers:
        c["1"].check(index[pid]["name"] in text, "%s (in the log) is in the report" % index[pid]["name"],
                     "%s is in the outreach log but not in the report" % index[pid]["name"])

    # 2. excerpts verbatim; prices only as stated
    n = 0
    for name, sec in sections.items():
        pid = by_name.get(name)
        if not pid:
            continue
        lines = page_lines(pid)
        for line_no, block in re.findall(r"^  Source: <[^\n]*?> \(line (\d+)\)\n  ```\n  ([^\n]*)\n  ```", sec, re.M):
            n += 1
            c["2"].check(block.strip() == lines[int(line_no) - 1].strip(), "",
                         "%s: excerpt for line %s is not the page's own line: %r" % (name, line_no, block[:80]))
        quoted = re.search(r"quoted as recorded:\n\n```\n(.*?)\n```", sec, re.S)
        if quoted:
            n += 1
            c["2"].check(quoted.group(1).strip() == replies.get(pid, "").strip(), "",
                         "%s: reply quoted is not the recorded reply" % name)
    for row in table_rows:
        pid = by_name.get(row["Provider"])
        for col in ("Price as stated", "Included", "Not included", "Site visit", "Requirements"):
            cell = row.get(col, "")
            for kind, quote in re.findall(r"(reply|published): (.*?)(?=(?: ; )?(?:reply|published): |$)", cell):
                src = replies.get(pid, "") if kind == "reply" else "\n".join(page_lines(pid))
                for part in quote.split(" / "):  # the comparison joins several quoted sentences with " / "
                    if part.strip().rstrip(";").strip() not in src:
                        c["2"].fail("%s %s: %r is not in the %s" % (row["Provider"], col, part[:80], kind))
        for amount in MONEY.findall(row.get("Against budget", "") + " " + row.get("Price as stated", "")):
            src = replies.get(pid, "") + "\n" + "\n".join(page_lines(pid))
            if ("$" + amount) not in src and ("$ " + amount) not in src:
                c["2"].fail("%s: $%s is not stated by the provider" % (row["Provider"], amount))
    c["2"].ok("%d excerpt(s) and replies matched their sources verbatim; every comparison cell quote and dollar "
              "figure appears in the provider's reply or page" % n)

    # 3. non responders and decliners included
    for pid in contacted:
        name = index[pid]["name"]
        row = next((r for r in table_rows if r["Provider"] == name), None)
        if not replies.get(pid):
            nr = text.split("## No response after the attempts listed", 1)[-1].split("\n## ", 1)[0]
            c["3"].check(name in nr and row is not None, "%s (no reply) is in the comparison and under No response" % name,
                         "%s was contacted with no reply and is missing from the comparison or the No response list" % name)
        elif row and row.get("Availability") == "declined":
            c["3"].ok("%s (declined) is in the comparison with status %r" % (name, row["Status"][:60]))
    if not contacted:
        c["3"].cannot("no provider was contacted in this case (drafts only), so no non responder exists to include")

    # 4. coverage differences pointed out
    quoting = [pid for pid in contacted if replies.get(pid) and MONEY.search(replies[pid])]
    if len(quoting) < 2:
        c["4"].cannot("fewer than two providers quoted in this case, so there is nothing to compare")
    else:
        cover = text.split("## What the quotes cover", 1)[1].split("\n## ", 1)[0] if "## What the quotes cover" in text else ""
        items = re.findall(r"^- \*\*(.+?)\*\*: (.*)$", cover, re.M)
        quotes = re.findall(r"^  - (.+?) \((reply|published)\): \"(.*)\"$", cover, re.M)
        bad = [q for q in quotes if q[2] not in (replies.get(by_name.get(q[0], ""), "") if q[1] == "reply"
                                                else "\n".join(page_lines(by_name.get(q[0], "barton-creek"))))]
        c["4"].check(bool(items) and not bad,
                     "%d coverage difference(s) named (%s), each backed by the providers' own words"
                     % (len(items), ", ".join(i[0] for i in items)),
                     "no coverage differences named, or quotes not from the source: %s" % bad[:2])

    # 5. disclosure in every draft; no buyer contact; no acceptance or booking
    for pid, p in providers.items():
        for a in p.get("attempts", []):
            c["5"].check("on behalf of a customer" in a.get("text", "") and "automated assistant" in a.get("text", ""),
                         "", "%s %s draft lacks the on behalf of a customer or automated assistant disclosure"
                         % (index[pid]["name"], a.get("channel")))
    c["5"].ok("every recorded draft (%d) says 'on behalf of a customer' and 'automated assistant'"
              % sum(len(p.get("attempts", [])) for p in providers.values()))
    contact = request.get("_buyer_contact")
    if contact:
        c["5"].check(contact not in text + json.dumps(log_data), "the request's buyer contact %r is in no draft and not in the report" % contact,
                     "buyer contact %r leaked into a draft or the report" % contact)
    c["5"].check(all(r != 0 for r in refusals), "send refused without a hire id, and with --hire-id and --execute (exit %s)" % refusals,
                 "send did not refuse: exit codes %s" % refusals)
    c["5"].check(not attempts, "no network access attempted (guard recorded none)", "network access attempted: %s" % attempts[:3])
    own = re.sub(r"```.*?```", "", text, flags=re.S)
    if re.search(r"(?i)\b(we booked|booking (?:is )?confirmed|quote accepted|we accepted)\b", own):
        c["5"].fail("the report says the agent booked or accepted a quote")

    # 6. report at the end of the window with non responders marked
    closed = re.search(r"^- Collection window ends: (\S+) \((closed at this run)\)", text, re.M)
    c["6"].check(bool(closed) and closed.group(1) == request["response_deadline_utc"],
                 "report run %s states the window %s closed" % (NOW, closed.group(1) if closed else ""),
                 "the report does not state that the window %s closed" % request["response_deadline_utc"])
    c["6"].cannot("delivering the report at the window's end is a scheduling step outside one offline run; this run "
                  "only shows the report is complete when run after the window")

    sample = case.get("sample")
    if sample:
        s = res.criterion(*sample)
        if sample[0] == "S2":
            limit = request.get("budget_max_usd")
            for row in table_rows:
                amounts = [float(a.replace(",", "")) for a in MONEY.findall(row.get("Price as stated", ""))]
                if limit and row.get("Price as stated", "").startswith("reply:") and amounts and min(amounts) > limit:
                    s.check(row["Against budget"].startswith("OVER"), "%s: %s" % (row["Provider"], row["Against budget"][:90]),
                            "%s quoted above %s but is not marked over budget" % (row["Provider"], limit))
            if not s.passes and not s.fails:
                s.cannot("no quote above the budget limit in this case")
        if sample[0] == "S3":
            m = re.search(r"^Candidates checked: (\d+)\. Verified for the service and area: (\d+)\. Contacted: (\d+)\. "
                          r"Replied: (\d+)\.", text, re.M)
            s.check(bool(m) and int(m.group(2)) == len(table_rows),
                    "counts line: %s; comparison rows %d" % (m.group(0) if m else "", len(table_rows)),
                    "no counts line, or the verified count differs from the comparison rows (%d)" % len(table_rows))
    return res


def run():
    agent = ac.load("acceptance_local_quotes", HERE.parent / "local_quotes.py")
    return [check_case(case, agent) for case in CASES]


def main():
    total = ac.print_results(run())
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
