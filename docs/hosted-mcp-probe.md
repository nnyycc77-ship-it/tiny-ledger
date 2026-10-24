# `hosted_mcp_probe`: hosted MCP verification probe

The outside verification from
[`docs/mcpize-redeploy-runbook.md`](mcpize-redeploy-runbook.md), built as
one offline tested script (issue #218). After the owner redeploys the
hosted server, this probe is the check the runbook describes, run the
same way every time.

- **Code:** [`tools/hosted_mcp_probe.py`](../tools/hosted_mcp_probe.py).
  Run it with the hosted endpoint URL, or with no argument for the
  default, `https://recallcheck.mcpize.run/mcp`:

  ```bash
  python3 tools/hosted_mcp_probe.py
  python3 tools/hosted_mcp_probe.py https://recallcheck.mcpize.run/mcp
  ```

- **What it does:** sends an anonymous `initialize`, then
  `notifications/initialized`, then `tools/list`, then one unpaid
  `recall_check` `tools/call` for `{"product": "VH101"}`, and prints one
  section per step in the repo's fixed evidence format: a PASS or FAIL
  claim line per check with the observed value, the exact request, the
  UTC retrieval time, and the complete raw response transcript beneath.

- **What it checks** (the runbook's "after the redeploy" column):
  - `initialize` answered HTTP 200 and its body parses; `serverInfo`
    version is `0.3.0`, the server version on main; the gateway's name
    form is printed as observed.
  - `tools/list` answered HTTP 200 and its body parses; the tool count is
    twenty five and the names stand in the order `tool_definitions()`
    returns them on main, `recall_check` first.
  - The unpaid call answered HTTP 402 with an x402 demand JSON body, not
    a JSON-RPC error: `x402Version` 1, exactly one `accepts` entry with
    `scheme` "exact", `network` "base", `maxAmountRequired` "50000", and
    `payTo` equal to the `recipient` in
    [`mcpize.yaml`](../mcpize.yaml), which the probe reads at run time.

- **Price context, stated only as the runbook states it:** the expected
  `maxAmountRequired` "50000" is 0.05 USDC at 6 decimals, the
  `recall_check` price the runbook keeps in `mcpize.yaml` for this
  redeploy. The 0.25 USDC shelf price is the wave tools' shelf price,
  recorded on their docs pages; it is not what this probe expects the
  hosted `recall_check` demand to show. The probe reports the observed
  amount and sets no price.

- **It never pays.** The probe never sends an X-PAYMENT header, and no
  private key, token, or signing wallet is read or printed. The only
  wallet value the probe handles is the public recipient recorded in
  `mcpize.yaml`, read for the payTo comparison and printed as part of
  that check. The unpaid call is the whole design: the 402 demand is the
  evidence.

- **Exit codes:** 0 when every check passes, 1 when any check fails, 2
  when the probe cannot run (a transport failure before a step's status
  arrives, an unreadable `mcpize.yaml`). A step whose status arrived but
  whose body cannot be read is judged on that evidence: its parse check
  fails, and the run continues.

- **Gateway behaviour observed while building (2026-10-24):** the hosted
  gateway is unsteady in bursts, as the runbook's issue history already
  records for the minutes after a deploy: 403 answers in one burst, a
  dropped connection on another step, and a `tools/list` step that
  answers HTTP 200 with its body never arriving. The probe treats each of
  those as the observed state and reports it plainly, which is what the
  live run in the opening PR for this tool shows.
