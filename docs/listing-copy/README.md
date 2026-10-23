# Listing copy pack: the prebuilt agents

Issue #99. One file per agent, holding the listing text in the order the owner pastes it when a NEAR award lands and the agent shell is created. This folder posts nothing, creates no account and lists nothing. Every fact comes from three kinds of source:
- the merged agent READMEs on `main` at `5e26406`;
- the service catalog, `docs/services-catalog.md`;
- the bid proposals the coordinator posted verbatim on the task issues.

Each file names its sources.

## Status at a glance

"Paste ready" means the copy describes only what the merged build does. "Not listable yet" means the build cannot yet deliver what a listing for that job must offer. Each file says what is missing.

| Agent | File | Status | Category | Suggested price per hire |
| --- | --- | --- | --- | --- |
| Field Service Route Planner & Schedule Backfill | [field-service-planner.md](field-service-planner.md) | Paste ready after one confirmed live routing run | Automation | 10 USD |
| Video Clipping Agent | [video-clipping.md](video-clipping.md) | Paste ready after the host has a speech model and the file delivery route is confirmed | to confirm at award | 10 USD |
| Catering & Group Dining Finder | [catering-finder.md](catering-finder.md) | Paste ready | Events | 10 USD |
| Local Services Quote Agent | [local-quotes.md](local-quotes.md) | Paste ready | Research | 10 USD |
| Brand Name Checker | [brand-name-checker.md](brand-name-checker.md) | Paste ready | to confirm at award | 10 USD per name |
| Video Dubbing Agent | [video-dubbing.md](video-dubbing.md) | Not listable yet: no speech engine, machine translator or non-English voice is wired | Creative | set at award |
| AI Image, Video & Voiceover Generator | [media-generator.md](media-generator.md) | Not listable yet: no live generation provider is wired | Creative | set at award |
| Call-for-Me: Restaurant & Appointment Booking Agent | [call-for-me.md](call-for-me.md) | Design stage, not listable | Automation | set at award |

## Pricing pattern

Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. The suggested price follows that pattern only where one hire produces one sourced report and the repo records no per job provider cost. Where a hire spends money on a provider (generation, voice, telephony), the repo records no unit cost, so the price is marked "set at award" with the rule the agent's README gives for setting it.

## Delivery window

Every recorded bid SLA is a build commitment: "Working agent submitted within N days of award". A listing's delivery window is a per hire turnaround, so each file states two things:
- the per hire window as the merged README states it, or "to confirm at award" where the README states none;
- the bid's build commitment verbatim, labelled as such.

The coordinator approved this reading on issue #99 (comment 6368328356): the pack must not reuse the build days as a turnaround, and where the README has no per hire window the file says "to confirm at award".

## Track record line

Quoted exactly as written in `AGENT-BRIEF.md` hard rule 4 at `5e26406`. None of the per agent files adds a track record claim. If a listing form asks for experience, paste this and nothing stronger. If `AGENT-BRIEF.md` has changed by paste time, copy the new paragraph from there instead.

> As of
> 2026-10-23 the true record is: four paid jobs won and delivered
> on Synmerco (a recall check, a carrier vetting report, a
> litigation screen, and a Cook County property tax comps report),
> all four paid out and swept to the owner wallet, 39.73 USDC in
> total, and all four released with no revision round; ten services
> listed for hire on ugig at 10 USD each; AgentTab deployed on Arc
> testnet, with the mainnet deployment and grant submission in
> preparation for a Nov 1, 2026 deadline.

## Fixes against the README drafts

Where a README's listing draft offers something the merged build does not do, or misses something the job requires, the file corrects it and says so under "Fixes against the README draft". In summary:
- **catering-finder:** the draft offered to find candidate vendors; the build has no directory search.
- **local-quotes:** the same correction; the build has no directory search.
- **video-dubbing:** the draft promised dubbing into other languages; the build voices English only and translates only from operator supplied translations.
- **media-generator:** the draft is kept, marked not listable until a live provider is wired.
- **brand-name-checker:** no README draft exists; the copy is written from `tools/README.md` and the tool's own options.
- **video-clipping and field-service-planner:** no delivery window is stated; it is added as "to confirm at award".
