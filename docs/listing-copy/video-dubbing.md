# Video Dubbing Agent: listing copy

**Status:** **Not listable yet.** The listing the job asks for offers dubbing into other languages. The merged build cannot do that on its own yet:
- **Transcription:** it reads timed segments another engine produced, and no speech engine is bundled.
- **Translation:** it uses operator supplied translations (`glossary`) or a test stub marked not a deliverable.
- **Voices:** they speak English only (`flite`), and other languages are refused.

The copy below is ready for when a speech engine, a translation provider and voices for the target languages are wired. Until then it must not be pasted.

**Sources:** `agents/video-dubbing/README.md` (listing draft, Providers table, consent rule); job description on issue #77 (comment 6365954974) for the category and the delivery time criterion; bid proposal on issue #77 (comment 6365955553; bid 53e41b06, 125 USDC, slaSeconds 432000).

## Paste order

### 1. Name

Video Dubbing Agent

### 2. Category

Creative (the job description on issue #77 names the **Creative** category).

### 3. Suggested price per hire

Set at award. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. That pattern is for sourced reports with no per job provider cost. A dub needs paid transcription, translation and voice services, and the repo records no unit cost for any of them.

### 4. Listing description

Dubs your video into other languages. It keeps the music and sound underneath, keeps your names and brand terms as written, and tells you exactly which lines had to be sped up.

You get, per language:
- one finished video, with a distinct voice for each speaker;
- one subtitle file (SRT);
- a delivery note listing any line that was compressed to fit the timing, and any line that was hard to translate.

Lip-sync is not offered.

### 5. What buyers provide

- the video;
- the target languages;
- a voice choice;
- a list of names and terms that must not be translated.

The speaker's own voice is not offered in the current build.

### 6. Delivery window

- **Per hire:** not stated. The README says "Turnaround is agreed per job", but the job's first acceptance criterion requires a delivery time stated in the listing. To confirm at award.
- **Bid build commitment (verbatim, issue #77):** "Working agent submitted within 5 days of award." 

### 7. FAQ

- *Will the timing match?* Each line is fitted to the original timing. Wording is tightened first, then speed is raised a little within a set limit, then the line may run into a natural pause. Any line that was sped up is named in the delivery note.
- *Do subtitles match the audio?* There is one subtitle per dubbed line, at the same time. By default the subtitles carry the full translation. Where a shorter wording was spoken to fit the timing, the note says which lines. Subtitles that match the spoken wording exactly are available on request.
- *Is the original voice removed completely?* With the local option, the original speech is cut back under the new voice rather than removed. Full separation uses a separate library, and the delivery note says when it was used.
- *Can it use my own voice?* Not in the current build. It would need you to confirm you are the speaker or have their consent, and that you hold the rights to the video.

## Fixes against the README draft

- **The status block is new.** The README draft reads as a live offer ("dubs your video into other languages"), but its own Providers table shows English-only voices, no bundled speech engine, and translations supplied by the operator. The draft is kept as the target copy and marked not listable until those three are wired.
- The consent record was dropped from what buyers provide, because the own-voice option is not offered in the build. It moved to the FAQ.
- Added the delivery window line, which the job requires and the README leaves per job.

## To confirm at award

- A speech engine with speaker identification, a translation provider, and stock voices for each listed language.
- The languages the listing names, from the providers chosen.
- The per hire delivery time, measured on the wired providers.
- The price, from those providers' unit costs.
