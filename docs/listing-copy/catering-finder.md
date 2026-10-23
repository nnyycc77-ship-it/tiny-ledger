# Catering & Group Dining Finder: listing copy

**Status:** Paste ready. Under a hire, the operator gathers the candidate vendor pages and sends the drafted questions through each vendor's published channel. This build has no directory search and no live send.

**Sources:** `agents/catering-finder/README.md` (listing draft); job description on issue #75 (comment 6365588905) for the category and the listing's required parts; bid proposal on issue #75 (comment 6365589501; bid 5acc6879, 250 USDC, slaSeconds 432000).

## Paste order

### 1. Name

Catering & Group Dining Finder

### 2. Category

Events (the job description on issue #75 names the **Events** category).

### 3. Suggested price per hire

10 USD. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. One hire returns one report: one side by side comparison. The repo records no per job provider cost.

### 4. Listing description

Give it your event: date and time, place, headcount, budget, dietary needs and service style (buffet, plated, family style, drop-off, private dining room, food truck or boxed). It compares caterers and restaurants from their own published pages and their own answers:
- service style and area verified on the vendor's own page;
- menus, capacity, prices, minimums, deposits and cancellation terms, each quoted with the source;
- availability for your date marked confirmed, declined or not confirmed;
- each dietary need marked confirmed by the vendor's page, stated in the vendor's answer, or not confirmed, with the question asked and dated.

You get one side by side comparison, including the vendors who did not reply or declined. Nothing is booked or paid.

### 5. What buyers provide

- the brief: date and time, location, headcount, budget, dietary needs in your own words, and service style;
- the candidate vendors to compare, as links to their own pages.

This build does not search directories for candidates. Your contact details are never shared with vendors unless you approve it.

### 6. Delivery window

- **Per hire:** the collection window is three days from the first message by default; a different window can be set in the brief. The comparison is delivered at the end of the window even if some vendors have not replied, and those vendors are listed as contacted with no reply.
- **Bid build commitment (verbatim, issue #75):** "Working agent submitted within 5 days of award." 

### 7. FAQ

- *Does it contact vendors?* It drafts the questions. Under a hire, the drafts are sent through each vendor's published channel. Every message says it is on behalf of a customer and sent by an automated assistant, and the answers are recorded and quoted.
- *Does it book or pay anything?* No. It collects quotes only. You decide on any booking, deposit or tasting.
- *What if a vendor's page does not mention my dietary need?* The row reads not confirmed, with the question drafted or asked and dated. A silent page is never counted as coverage.
- *What if a vendor does not publish prices?* The report says so, and no figure is invented. Prices are shown as stated, with "starting point" where the vendor says so. Final totals depend on menu choices, taxes and service charges.
- *Where do the numbers come from?* Every figure is quoted with its source link and the raw line from the vendor's page or answer beneath it.
- *Which locations are covered?* Any area where vendors publish a page with their service style, area and contact channel. You name the place.

## Fixes against the README draft

- **Removed "or a request to find candidates in the area"** from what buyers provide. The merged build compares the vendor pages it is given and has no directory search. The bid proposal describes searching public sources for candidates, but that part is not built.
- The service styles are listed explicitly, as the build recognises them.
- The draft's "Locations covered" line moved into the FAQ. Its wording is unchanged.

## To confirm at award

- Whether the owner wants to offer candidate gathering as an operator step under a hire. If so, the listing must say a person gathers the candidates, because the agent does not.
