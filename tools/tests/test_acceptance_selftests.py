"""Checks the agent acceptance self tests (issue #124) run and report honestly.

Run:  python3 -m unittest discover -s tools/tests -p 'test_acceptance_selftests.py' -v

The tests do not gate on the agents passing. A failing criterion is a
finding, filed as its own QUEUE issue, never something to hide. They
check that:
- every agent's script runs offline;
- every case reports a PASS, FAIL or UNTESTABLE status;
- an UNTESTABLE carries its reason and a FAIL carries its evidence;
- every posting criterion is covered by at least one case;
- the runner prints its table.

The tamper tests then feed each script a deliberately broken output and
require the matching criterion to FAIL, so a check cannot pass vacuously.
"""

import copy
import io
import json
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402
import acceptance_all  # noqa: E402

RESULTS = {}


def results():
    if not RESULTS:
        RESULTS.update(acceptance_all.run_all())
    return RESULTS


def script(agent):
    return ac.load("acceptance_script_" + agent.replace("-", "_"), acceptance_all.script(agent))


class EveryScript(unittest.TestCase):
    def test_six_agents_each_with_cases(self):
        self.assertEqual(sorted(results()), sorted(acceptance_all.AGENTS))
        for agent, cases in results().items():
            self.assertGreaterEqual(len(cases), 2, agent)

    def test_status_reason_and_evidence(self):
        for agent, cases in results().items():
            for r in cases:
                self.assertTrue(r.criteria, (agent, r.case))
                for c in r.criteria:
                    self.assertIn(c.status, (ac.PASS, ac.FAIL, ac.UNTESTABLE))
                    if c.status == ac.UNTESTABLE:
                        self.assertTrue(any(u.strip() for u in c.untestable), (agent, r.case, c.cid, "no reason"))
                    if c.status == ac.FAIL:
                        self.assertTrue(all(f.strip() for f in c.fails), (agent, r.case, c.cid, "no evidence"))

    def test_every_posting_criterion_is_covered(self):
        for agent, cases in results().items():
            wanted = set(script(agent).CRITERIA)
            seen = {c.cid for r in cases for c in r.criteria}
            self.assertEqual(wanted - seen, set(), agent)

    def test_runner_table(self):
        text, total = acceptance_all.table(results())
        self.assertIn("| Agent | Case | PASS | FAIL | UNTESTABLE |", text)
        self.assertEqual(sum(total.values()), sum(len(r.criteria) for cases in results().values() for r in cases))
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = acceptance_all.main(["--agent", "local-quotes"])
        self.assertIn("local-quotes", buf.getvalue())
        self.assertIn(code, (0, 1))


class Tamper(unittest.TestCase):
    """A broken output must turn the matching criterion to FAIL."""

    def test_planner_missing_job_fails_criterion_1(self):
        mod = script("field-service-planner")
        planner = ac.load("acceptance_planner", mod.HERE.parent / "planner.py")
        case = mod.CASES[1]
        text = self.planner_report(mod, planner, case)
        broken = re.sub(r"^- Job U1 .*$\n", "", text, flags=re.M)
        res, c = mod.new_result(case)
        mod.evaluate(res, c, broken, case, [])
        self.assertEqual(c["1"].status, ac.FAIL)

    def test_planner_job_outside_window_fails_criterion_2(self):
        mod = script("field-service-planner")
        planner = ac.load("acceptance_planner", mod.HERE.parent / "planner.py")
        case = mod.CASES[0]
        text = self.planner_report(mod, planner, case)
        broken = text.replace("| 08:02 | 08:30 | 10:00 | 08:30 to 10:30 |", "| 08:02 | 08:10 | 09:40 | 08:30 to 10:30 |")
        self.assertNotEqual(broken, text)
        res, c = mod.new_result(case)
        mod.evaluate(res, c, broken, case, [])
        self.assertEqual(c["2"].status, ac.FAIL)

    def planner_report(self, mod, planner, case):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.md"
            argv = ["plan"] + case["args"] + ["--jobs", str(case["jobs"]), "--crew", str(mod.TESTS / "crew.csv"),
                                              "--customers", str(mod.TESTS / "customers.csv"),
                                              "--places", str(mod.TESTS / "places.json"), "--out", str(out)]
            code, _, err = ac.run_main(lambda a: planner.main(a, env={}), argv)
            self.assertEqual(code, 0, err)
            return out.read_text(encoding="utf-8")

    def test_catering_altered_price_fails_criterion_2(self):
        mod = script("catering-finder")
        finder = ac.load("acceptance_catering", mod.HERE.parent / "catering_finder.py")
        case = mod.CASES[0]
        log = json.loads(case["log"].read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.md"
            code, _, err = ac.run_main(lambda a: finder.main(a, env={}),
                                       ["run", "--brief", str(case["brief"]), "--store", str(mod.STORE),
                                        "--log", str(case["log"]), "--out", str(out)])
            self.assertEqual(code, 0, err)
            text = out.read_text(encoding="utf-8")
        broken = text.replace("<p>From $35 per person for buffet service;", "<p>From $31 per person for buffet service;", 1)
        self.assertNotEqual(broken, text)
        res, c = mod.new_result(case)
        mod.evaluate(res, c, broken, case, log, [2, 2], [])
        self.assertEqual(c["2"].status, ac.FAIL)

    def test_catering_missing_disclosure_fails_criterion_6(self):
        mod = script("catering-finder")
        case = mod.CASES[0]
        log = json.loads(case["log"].read_text(encoding="utf-8"))
        broken = copy.deepcopy(log)
        first = next(iter(broken["drafts"].values()))
        first["message"] = first["message"].replace("on behalf of a customer", "for a client")
        res, c = mod.new_result(case)
        mod.evaluate(res, c, "## Summary\n\n## Availability for x\n- Confirmed by the vendor's answer: none\n"
                     "- Not confirmed (x): none\n\n## Vendors compared\n\n## Outreach drafts\n", case, broken, [2, 2], [])
        self.assertEqual(c["6"].status, ac.FAIL)

    def test_quotes_dropped_non_responder_fails_criterion_3(self):
        mod = script("local-quotes")
        agent = ac.load("acceptance_local_quotes", mod.HERE.parent / "local_quotes.py")
        case = mod.CASES[0]
        log = json.loads(case["log"].read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.md"
            code, _, err = ac.run_main(lambda a: agent.main(a, env={}),
                                       ["run", "--request", str(case["request"]), "--store", str(mod.STORE), "--log",
                                        str(case["log"]), "--now", mod.NOW, "--out", str(out)])
            self.assertEqual(code, 0, err)
            text = out.read_text(encoding="utf-8")
        broken = re.sub(r"^- Riverside Rooter: no response after.*$\n", "", text, flags=re.M)
        self.assertNotEqual(broken, text)
        res, c = mod.new_result(case)
        mod.evaluate(res, c, broken, case, log, [2, 2], [])
        self.assertEqual(c["3"].status, ac.FAIL)

    def test_media_wrong_aspect_is_rejected(self):
        mod = script("media-generator")
        self.assertTrue(mod.aspect_ok(144, 256, "9:16"))
        self.assertFalse(mod.aspect_ok(256, 144, "9:16"))
        self.assertFalse(mod.aspect_ok(64, 48, "1:1"))

    def test_network_reach_is_recorded(self):
        attempts = []
        import socket
        with self.assertRaises(ac.NetworkAttempt):
            with ac.no_network(attempts):
                socket.getaddrinfo("example.invalid", 443)  # SYNTHETIC host, refused before any lookup
        self.assertEqual(attempts, ["example.invalid"])


if __name__ == "__main__":
    unittest.main()
