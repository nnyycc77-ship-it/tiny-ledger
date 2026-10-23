# Brand Name Checker: listing copy

**Status:** Paste ready. The checker is `tools/brand_name_checker.py`, merged in PR #55. The trademark section reports "not covered" until a working trademark source is captured, and the copy says so.

**Sources:** `tools/README.md` ("brand_name_checker.py" section) and the tool's own options in `tools/brand_name_checker.py`; issue #51 text (bid 60 USDC, a working, listed agent promised within 3 days of award). No README listing draft, job description or proposal text for job e01a39f1 is recorded in the repo.

## Paste order

### 1. Name

Brand Name Checker

### 2. Category

To confirm at award. The job description for job e01a39f1 is not recorded in the repo.

### 3. Suggested price per hire

10 USD per candidate name. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. Each name gets one report. The checks use free public endpoints, so the repo records no per job provider cost. How many names one hire covers is to confirm.

### 4. Listing description

Checks whether a brand name is free before you commit to it. For each candidate name you get one report:
- **Domains:** registration status for the extensions you choose, from RDAP.
- **Handles:** X handles. Instagram and TikTok handles are checked too, but those two show a login wall, so they read "could not confirm" unless the platform returns a hard not found.
- **App Store:** apps whose name exactly matches, from the iTunes Search API.
- **Trademarks:** this section currently reads "not covered". It names the USPTO database it would search and lists no marks.

Every row carries its check time in UTC, with the evidence behind each verdict. A failed check reads "could not confirm", never available. On request it suggests variations, listed only when every requested domain and the X handle come back free. The checker only looks; it never registers or reserves a name.

### 5. What buyers provide

- one or more candidate names;
- optionally, the domain extensions to check (default `.com`);
- optionally, the platforms to check (default X, Instagram and TikTok);
- optionally, how many verified free variations you want (default none).

### 6. Delivery window

- **Per hire:** not stated in the repo. To confirm at award.
- **Bid build commitment (issue #51 text):** "a working, listed agent within 3 days of award". 

### 7. FAQ

- *Does a free result mean the name is mine to use?* No. A free domain or handle can be taken at any time after the check, and the check time is printed on every row. Trademark results are not covered in this version, and nothing in the report is legal advice.
- *Why do Instagram and TikTok say "could not confirm"?* Both show a login page for real and made-up names alike, so a normal answer proves nothing. The checker marks them available only on a hard not found.
- *What about Google Play?* It is out of scope, because Google Play has no official public search API. The report says so.
- *How are App Store matches judged?* The iTunes Search API matches loosely, so results are filtered to exact name matches, comparing the title part before the first `:`, ` - ` or ` | `, on letters and digits only.
- *Does it register anything?* No. It sends read only requests and never registers or reserves a name.

## Fixes against the README draft

- No README listing draft existed; this copy is written from `tools/README.md` and the tool's options.
- The tool accepts `--trademark-countries`, but the trademark leg reports "not covered", so the copy does not offer trademark countries.

## To confirm at award

- The category, from the job description for job e01a39f1.
- The per hire delivery window, and how many names one hire covers.
- Whether a trademark source has been captured by then. If one has, the trademark lines change.
