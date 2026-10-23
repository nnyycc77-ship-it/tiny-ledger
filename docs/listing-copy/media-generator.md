# AI Image, Video & Voiceover Generator (pay per job): listing copy

**Status:** **Not listable yet.** The merged build calls no live provider. Its only providers are offline stubs that write placeholder PNG, GIF and WAV files: the stub voice is a tone, not speech, and the image stub for references does not read the references. The live slots report "not configured" and refuse to generate. The copy below is ready for when live image, video and voice providers are wired at award. Until then it must not be pasted.

**Sources:** `agents/media-generator/README.md` (listing draft, providers table, pricing rule); job description on issue #78 (comment 6366897388) for the category, the listing's required parts and the delivery time criterion; bid proposal on issue #78 (comment 6366897988; bid 35f71935, 150 USDC).

## Paste order

### 1. Name

AI Image, Video & Voiceover Generator (pay per job)

### 2. Category

Creative (the job description on issue #78 names the **Creative** category).

### 3. Suggested price per hire

Set at award. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. That pattern is for sourced reports with no per job provider cost, and the bid proposal says "the per job listing price is set to cover generation cost". The README's rule is the worst case, 2 x the number of files x the chosen provider's unit cost, plus the operator's margin. No provider is chosen yet, so no unit cost is recorded.

### 4. Listing description

Creates product photos and other still images, short videos, and voiceovers from a plain language brief. You do not need an account with any generation service.

Before generating, it screens the request against its content rules. Every file is checked against your brief and regenerated once if it misses. The report names the provider and model of every file. Parts of a request it will not make are declined with the reason, and the rest goes ahead.

### 5. What buyers provide

- what to make: image, video or voiceover;
- the subject and the style;
- the format: size or aspect ratio, plus length for video and voice;
- how many variations;
- optionally, reference images, brand colours or fonts, and the voiceover script.

For reference material, confirm you hold the rights to it. For a real person, confirm you are that person or have their consent. For a logo or brand, confirm you own it.

### 6. Delivery window

- **Per hire:** stated at award from measured provider times. The README records none, because no live provider is wired. The job requires a typical delivery time in the listing.
- **Bid build commitment (verbatim, issue #78):** "Working agent submitted within 5 days of award." 

### 7. FAQ

- *Which models does it use?* The report names the provider and model of every file. The agent picks the provider that fits your brief first, and the one that scored best in its own tests for that kind of request second.
- *What if a file does not match my brief?* It is regenerated once automatically. If it still misses, you get the closest result with a note saying exactly what did not match, and you can rerun.
- *Can I change one file and keep the others?* Yes. Name the files to change; every other file stays exactly as delivered.
- *What will it not make?* Real, identifiable people without consent, copyrighted characters, logos and brands you don't own, sexual content, graphic violence, or content meant to deceive. Those parts of a request are declined and the report says why; the rest of the request goes ahead.

## Fixes against the README draft

- **The status block is new.** The README draft already says formats, lengths and delivery time are "stated at award". The status makes plain that the whole listing waits on live providers, because the stubs make placeholders only.
- "Screens the request against its content rules" is the build's step (`mediagen_providers/policy.py`). The bid proposal's "confirms media type, subject, style..." step before generation is not a separate step in the build, so it is not offered.
- The "Formats and lengths" line is left out of the paste order until it can be filled from the wired providers. The README's rule for it is kept in "To confirm at award".

## To confirm at award

- Live image, video and voice providers, each with its terms of use on commercial use and resale recorded.
- Formats and lengths, from those providers. This build's stubs make PNG, GIF and WAV only, which are not the listed formats.
- The typical delivery time, measured on the wired providers.
- The price, from the README's worst case rule and the providers' recorded unit costs.
