# Local Services Quote Agent: listing copy

**Status:** Paste ready. Under a hire, the operator gathers the candidate provider pages and sends the drafted requests and follow-ups through each provider's published channel. This build has no directory search and no live send.

**Sources:** `agents/local-quotes/README.md` (listing draft, "What it does", channels section); job description on issue #76 (comment 6366190586) for the category and the listing's required parts; bid proposal on issue #76 (comment 6366191119; bid 9ec6f418, 250 USDC).

## Paste order

### 1. Name

Local Services Quote Agent

### 2. Category

Research (the job description on issue #76 names the **Research** category).

### 3. Suggested price per hire

10 USD. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. One hire returns one report: one comparison. The repo records no per job provider cost.

### 4. Listing description

Tell it what you need done, where, when and your budget. It checks each candidate provider's own listing or site, keeps only the providers who show they offer that service in your area, and drafts the same clear quote request for each through the channels they publish. It follows up with those who don't answer on their next published channel. You get one side by side comparison of:
- price, and whether it is fixed, an estimate or hourly;
- earliest availability;
- requirements, and what is included.

Every figure is quoted from the provider's own reply or published pricing. Quotes over your budget are marked, not hidden.

### 5. What buyers provide

- the service, your location, the job details, your timing and any budget limits;
- the candidate providers to check, as links to their own listing or site.

This build does not search directories for candidates. Your contact details are never shared with providers unless you approve it.

### 6. Delivery window

- **Per hire:** the collection window is the reply deadline set in your request. Three days from the first message is the suggested window, and every request states its own deadline. The comparison is delivered at the end of the window even if some providers have not replied. Those providers are listed as "no response after" every attempt made, with dates.
- **Bid build commitment (verbatim, issue #76):** "Working agent submitted within 5 days of award." 

### 7. FAQ

- *Does it contact providers?* Under a hire, the quote request goes through each provider's published email, web form or directory messaging. Every message says it is from an automated assistant acting for a customer. Providers who publish only a phone number are listed for you to call.
- *Does it book or pay anything?* No. It collects quotes; you decide.
- *How does it choose providers?* Only providers whose own page shows they offer the service in your area. Others are listed as checked and excluded, with the reason.
- *Where do the numbers come from?* Each one is quoted from the provider's reply or from the pricing on their page, with the source. Nothing is estimated, and a provider's own estimate is labelled as an estimate.
- *What if quotes cover different things?* The report lists each difference, for example that one includes the permit and another does not.
- *What if a quote is over my budget?* It is marked over budget, not hidden.
- *Which services and places?* Home and small business services from providers who publish their service and service area: plumbing, electrical, HVAC, cleaning, lawn care and landscaping, painting, roofing, moving, pest control, handyman work, and other trades named in your request. Providers must be in the United States; you name the city, and the ZIP if you like. Coverage is thinner in small towns, and the report says how many providers were checked, verified, contacted and replied.

## Fixes against the README draft

- **"It finds local providers" now reads "It checks each candidate provider's own listing or site".** The merged build verifies the provider pages it is given and has no directory search. The bid proposal describes discovery through map and trade directories, but that part is not built.
- Added the candidate provider links to what buyers provide, for the same reason.
- The draft's "Service types" and "Locations covered" lines moved into the FAQ. Their wording is unchanged, apart from naming the four counts the build's counts line reports.

## To confirm at award

- Whether the owner wants to offer candidate gathering as an operator step under a hire. If so, the listing must say a person gathers the candidates, because the agent does not.
