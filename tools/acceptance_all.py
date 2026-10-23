"""Run the acceptance self test of every built NEAR agent and print one table (issue #124).

Each agent's `agents/<agent>/acceptance/acceptance.py` runs the agent the
way a marketplace tester would, offline on committed fixtures. It checks
the outputs against the job posting's own Acceptance Criteria. This runner
calls all six and prints one row per case (PASS, FAIL and UNTESTABLE
counts), then every FAIL with its evidence.

    python3 tools/acceptance_all.py              # the table and the failures
    python3 tools/acceptance_all.py --details    # every criterion with its evidence

Exit status:
- 1 when any criterion FAILs, so a person running it sees it;
- 0 otherwise.

CI does not gate on this. A failing criterion is filed as its own QUEUE
task issue with the evidence, never patched inside the test.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import acceptance_common as ac  # noqa: E402

AGENTS = ("field-service-planner", "catering-finder", "local-quotes", "media-generator", "video-clipping",
          "video-dubbing")


def script(agent):
    return ROOT / "agents" / agent / "acceptance" / "acceptance.py"


def run_all(agents=AGENTS):
    results = {}
    for agent in agents:
        mod = ac.load("acceptance_script_" + agent.replace("-", "_"), script(agent))
        results[agent] = mod.run()
    return results


def table(results):
    lines = ["| Agent | Case | PASS | FAIL | UNTESTABLE |", "| --- | --- | --- | --- | --- |"]
    total = {ac.PASS: 0, ac.FAIL: 0, ac.UNTESTABLE: 0}
    for agent, cases in results.items():
        for r in cases:
            n = r.counts()
            for k in total:
                total[k] += n[k]
            lines.append("| %s | %s | %d | %d | %d |" % (agent, r.case, n[ac.PASS], n[ac.FAIL], n[ac.UNTESTABLE]))
    lines.append("| **all** | | **%d** | **%d** | **%d** |" % (total[ac.PASS], total[ac.FAIL], total[ac.UNTESTABLE]))
    return "\n".join(lines), total


def failures(results):
    out = []
    for agent, cases in results.items():
        for r in cases:
            for c in r.criteria:
                if c.status == ac.FAIL:
                    out.append("- %s, %s, criterion %s: %s" % (agent, r.case, c.cid, c.fails[0]))
                    out.extend("    also: %s" % e for e in c.fails[1:3])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run every agent's acceptance self test, offline.")
    parser.add_argument("--details", action="store_true", help="print every criterion with its evidence")
    parser.add_argument("--agent", action="append", choices=AGENTS, help="run only this agent (repeatable)")
    args = parser.parse_args(argv)
    results = run_all(tuple(args.agent) if args.agent else AGENTS)
    if args.details:
        for cases in results.values():
            for r in cases:
                sys.stdout.write(r.render() + "\n")
    text, total = table(results)
    sys.stdout.write(text + "\n")
    fails = failures(results)
    if fails:
        sys.stdout.write("\nFailing criteria:\n" + "\n".join(fails) + "\n")
    return 1 if total[ac.FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
