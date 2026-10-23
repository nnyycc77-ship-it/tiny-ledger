# local-quotes: the Local Services Quote agent

Task: issue #76, prebuild wave for NEAR Agent Market job
481516a5-6030-43f3-a419-67d580a71002 ("Local Services Quote Agent", bid
pending at 250 USDC, five days promised from award). Built ahead of any
award so an award can be answered inside its promised window. One module,
`local_quotes.py`, standard library only; its tests live in `tests/` and
are discovered by the CI job through `tools/tests/test_local_quotes.py`.

Reconciled against the job description and the bid proposal as posted
verbatim by the coordinator on issue #76 (comments 6366190586 and 6366191119,
read live from the market on 2026-10-23; sha256 03fa1d4e… and 230afee6…,
both checked before use). `market.near.ai` itself is not reachable from the
build container.

| Job description or proposal | Where it is met |
| --- | --- |
| Understands the request: service, location, job details, timing, budget limits | The request JSON; the report header restates it |
| Finds providers; criterion 1: every provider contacted offers the service in the area | The hard filter below; only verified providers get a draft |
| Contacts by email, phone or contact form; the proposal adds directory messaging and "a further email attempt at a different time" | Channels and follow up below; phone only providers are flagged and listed, no calls are placed |
| Collects price, availability, what is included or excluded, whether a site visit is needed | The comparison columns, each quoted |
| Criterion 2: every price and detail exactly as stated | Quoted from the reply or the page; nothing totalled or estimated |
| Known limitation: say when a quote is an estimate | The price type column, from the provider's own words |
| Criterion 3: providers who did not reply or declined are included | Status column, "No response after the attempts listed", declined rows |
| Criterion 4: quotes covering different things are pointed out | "What the quotes cover" |
| Sample, budget limit: over-budget quotes marked clearly | The "Against budget" column and a next step |
| Sample, thin coverage: say how many exist and responded | The counts line: candidates checked, verified, contacted, replied |
| Criterion 5 and rules: on behalf of a customer, never book or share contact details, stop on request | Every draft; `send` gate; `record-reply --stop` |
| Criterion 6: delivered at the end of the window even with non responders | `run` after the window marks every non responder "no response after" |
| Reports with clear next steps | "Next steps for the buyer" |

## What it does

Given a plain language service request, the agent:
- reads each candidate provider's published page;
- keeps only the providers whose own page shows both the service and the area;
- reads the contact channels each provider publishes;
- builds one structured quote request and drafts it for each provider's published channels;
- drafts follow-ups for non responders on their other published channels;
- renders one comparison report.

| Command | Does | Sends anything |
| --- | --- | --- |
| `run --request R --store S [--log L] [--now UTC] [--out FILE]` | render the comparison report | no |
| `draft --request R --store S --log L [--now UTC]` | record a first draft for every verified provider with a written channel; flag phone only providers | no |
| `follow-up --request R --store S --log L [--now UTC]` | record a follow up on the next published channel for providers past the follow up interval with no reply | no |
| `record-sent PROVIDER --log L --channel C --when UTC` | record that the operator sent a draft through that published channel | no |
| `record-reply PROVIDER --log L --when UTC --text "..." [--stop]` | record the provider's answer verbatim | no |
| `send PROVIDER --log L [--hire-id ID] [--execute]` | refused: live sending needs a hire id and `--execute`, and no transport is part of this build | no |
| `capture URL --store S --id ID --name "..."` | fetch one live provider page into a store with provenance (status, headers without cookies, sha256) | GET only |

The dry run on the fixture store, run from the repository root:

```sh
python3 agents/local-quotes/local_quotes.py run \
  --request agents/local-quotes/tests/fixtures/request.json \
  --store agents/local-quotes/tests/fixtures \
  --log agents/local-quotes/tests/fixtures/outreach-log.json \
  --now 2026-11-05T09:00:00Z
```

### The request

A JSON object with these required fields:
- `service` (for example "plumbing")
- `location` ("Austin, TX", optionally with a ZIP)
- `job_details`
- `timing`
- `response_deadline_utc`, the end of the collection window

Optional fields:
- `budget_min_usd` and `budget_max_usd`
- `follow_up_after_hours`, default 48

Anything missing or malformed stops the run. Common service names are
matched on their usual phrasings ("plumbing" also matches "plumber");
any other service is matched on its own words.

### The hard filter (issue #76 item 2)

A provider is verified, and only then contacted, when its own page has:
- a line offering the service, and
- a line naming the place: the city, or a ZIP given in the request.

Each line is quoted as a claim with its source link and the raw page line
directly beneath, in the fixed format from `AGENT-BRIEF.md`.

These never verify:
- a title or heading that only repeats the business name;
- a line that names the service only to deny it ("We do not do plumbing").

A page silent on the area is excluded as "not verified, not inferred": the
agent does not conclude the provider is out of area, only that the page
does not say.

### Channels, outreach and follow up (items 3 and 4)

The agent reads the channels each provider publishes, in this order:
email, web form (contact or quote form), directory messaging ("message us
on our directory profile"), and phone.
- **First draft:** goes to the first written channel the provider publishes.
- **Follow-up:** a provider with a sent attempt older than
  `follow_up_after_hours` and no reply gets a follow-up drafted for the
  next written channel it publishes that was not yet tried. No follow-up is
  drafted after the collection window, after a reply, or for a provider who
  asked to stop.
- **Phone only:** a provider that publishes only a phone number is flagged
  "phone only" and gets no written draft. The report lists it for the
  customer with the number as published.

Every draft:
- says it is sent on behalf of a customer by an automated assistant;
- invites the provider to ask us to stop;
- carries the job details, timing and budget;
- asks for the price and whether it is fixed, an estimate or hourly, the
  earliest availability, what the price includes, and what the provider
  needs from the customer;
- names the reply deadline;
- asks for a quote only and carries no customer contact details.

Drafts are recorded, never sent. Under a real hire the operator sends each
draft through the published channel (the page line is quoted in the
report) and runs `record-sent` and `record-reply`. The agent never books,
accepts a quote or pays anything.

Rules from the job that bind the operator under a hire: if a provider asks
whether they are talking to an AI, answer yes, and where local law
requires saying so upfront, say so in the first message (every draft
already does). This build places no calls; if calls are added later, no
call may be recorded or stored and only the details needed for the report
are kept.

### The report (items 4 and 5)

One Markdown file with these parts:
- **Header:** the request, the window end and whether it is open or closed
  at the run, and the run time.
- **Counts line:** verified, contacted, replied, phone only, excluded.
- **Counts line:** candidates checked, verified for the service and area,
  contacted, replied, phone only, excluded. Thin coverage is stated, not
  padded.
- **Comparison table:** price as stated, price type, against budget,
  availability, site visit, included, not included, requirements, status.
  Each value is either quoted from the provider's reply (labelled `reply:`)
  or from its published page (labelled `published:`); otherwise it reads
  "not stated". Nothing is totalled or estimated.
  - *Price type* comes from the provider's own words: hourly rate,
    estimate ("about", "estimate", "starting", "subject to"), or fixed or
    total as stated.
  - *Against budget:* a total, fixed price or estimate whose stated figure
    is above `budget_max_usd` is marked **OVER**. An hourly rate is marked
    not comparable. A published fee is never presented as under budget,
    because it is not a quote for the job.
  - *Availability* reads "available as stated", "declined" or "not
    confirmed", from the reply's own words.
- **What the quotes cover:** for the providers who quoted, every item
  (parts, materials, labor, permit, disposal of the old unit, warranty,
  installation) that one quote states as included and another as excluded
  or does not mention, each with the quoted sentence. A price stated "for
  the new heater and labor" counts as covering those items.
- **One section per verified provider:** the verification claims, the
  published channels, published pricing, inclusions and requirements (each
  quoted with its line), every attempt with its draft and send dates, and
  the reply quoted as recorded.
- **"No response after the attempts listed":** once the window has closed,
  each non responder with every attempt, its channel and its send date.
  While the window is open these providers read "awaiting reply".
- **Next steps for the buyer:** who replied with a price and availability,
  who needs a site visit, who is phone only, which quotes are over budget,
  and whether the quotes cover different things. The agent books nothing.
- **Phone only, Checked and excluded** (with the reason, and the denial
  line when the page denies the service), **the drafts recorded**, and
  **Sources**.

### The store

A folder with:
- `index.json`: `{"providers": [{"id", "name", "url"}]}` plus an optional
  `source` note;
- `providers/<id>.html`: each page as captured;
- `provenance.json`: url, retrieval time and sha256 per page.

The loader checks every page against its recorded sha256 and refuses an
edited page rather than quote it. `capture` builds a real store one page at
a time.

## Fixtures

Everything under `tests/fixtures` is SYNTHETIC. No provider directory or
provider site is reachable from the build container (`yelp.com`,
`angi.com` and `market.near.ai` answered a gateway CONNECT 403; the probe
is on issue #76), so this follows the coordinator's #75 ruling for
labelled synthetic pages.

What the fixtures are:
- **Seven provider pages, the candidate index and the request:** written by
  hand. Each page says SYNTHETIC in its first line, and `provenance.json`
  repeats the label with a sha256 per page. The `.invalid` hostnames cannot
  resolve, and no business, price, number or address in them is real.
- **The outreach log:** its drafts were generated by `local_quotes.py`
  itself. Its send times, replies and reply dates were entered by hand to
  simulate a collection window. No message was sent and no provider
  replied. The test `test_cli_timeline_reproduces_the_fixture_log` replays
  the timeline through the CLI and requires the same log.

What the dry run exercises:
- **Matched, replied:** an email provider that replies with a quote,
  availability and requirements.
- **Matched, estimate:** an email provider that replies with an estimate
  that is over the budget limit, needs a site visit, and excludes the permit
  and disposal that the first quote includes.
- **Matched, declined:** an email provider that declines.
- **Matched, no response:** a web form and directory messaging provider
  that never replies, with one follow-up on the second channel. It is
  reported as no response after both attempts, with dates.
- **Phone only:** a matched provider that publishes only a phone number.
- **Mismatched area:** a provider whose page names other towns only.
- **Service denied:** an electrician whose page says it does not do
  plumbing.

To use real providers, run `capture` against live provider pages into a
new store folder; the loader and the report work unchanged.

## Where this sits in the NEAR worker loop

The marketplace side is `near-agent/worker.py` (PR #52):
- `poll` shows assignments.
- `start`, `message` and `submit` are dry runs until `--execute`.

On an award the operator runs this agent on the buyer's request, sends the
recorded drafts through each provider's published channel under the hire,
and submits the comparison report through `worker.py submit` after reading
its dry run. This folder itself never talks to the marketplace.

## Listing draft (for the owner, at award; not created by this task)

**Category:** Research (as the job description requires)

**Name:** Local Services Quote Agent

**What it does:** Tell it what you need done, where, when and your budget.
It finds local providers whose own listing or site shows they offer that
service in your area, sends each one the same clear quote request through
the channels they publish, follows up with those who don't answer, and
gives you one side-by-side comparison of price, availability, requirements
and what's included. Every figure is quoted from the provider's own reply
or published pricing.

**What you provide:** the service, your location, the job details, your
timing and any budget limits. Your contact details are never shared with
providers unless you approve it.

**Service types:** home and small business services from providers who
publish their service and service area: plumbing, electrical, HVAC,
cleaning, lawn care and landscaping, painting, roofing, moving, pest
control and handyman work, and other trades named in your request.

**Locations covered:** wherever providers publish their own service area,
in the United States; you name the city (and ZIP if you like). Coverage
is thinner in small towns, and the report says how many providers were
found and how many replied.

**Collection window:** the reply deadline set in your request (three days
from the first message is the suggested window; every request states its
own deadline). The comparison is delivered at the end of the window even
if some providers have not replied. Providers who have not answered by then
are listed as "no response after" every attempt made, with dates, so you
see the whole field and not only the answers.

**FAQ**

- *Does it contact providers?* Under a hire it sends the quote request
  through each provider's published email, web form or directory messaging,
  and every message says it is from an automated assistant acting for a
  customer. Providers who publish only a phone number are listed for you to
  call.
- *Does it book or pay anything?* No. It collects quotes; you decide.
- *How does it choose providers?* Only providers whose own page shows they
  offer the service in your area. Others are listed as checked and
  excluded, with the reason.
- *Where do the numbers come from?* Each one is quoted from the provider's
  reply or from the pricing on their page, with the source. Nothing is
  estimated, and a provider's estimate is labelled as an estimate.
- *What if quotes cover different things?* The report lists each
  difference (for example, one includes the permit and another does not).
- *What if a quote is over my budget?* It is marked over budget, not
  hidden.

## Verification

```sh
python3 -m unittest discover -s agents/local-quotes/tests -v
python3 -m unittest discover -s tools/tests -v        # includes the loader
python3 tools/pregate.py                              # secrets, honesty, provenance
```

Not verified from this folder:
- any live provider page capture or discovery run (no provider host is
  reachable from the build container);
- the live `send` path (no transport exists in this build, by design).
