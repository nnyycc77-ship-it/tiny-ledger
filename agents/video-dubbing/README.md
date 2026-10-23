# video-dubbing: the Video Dubbing agent

Task: issue #77, built ahead of any award for the NEAR Agent Market job
"Video Dubbing Agent" (job 2f1d5b6b-691f-4642-916a-570d340a4fb4). This
folder holds the agent. It creates no listing, sends no bid, and contacts
no one. **No real person's voice is cloned anywhere in this build or its
fixtures.**

One video goes in, and for each target language you get one finished
video plus one SRT. The music and sound stay under the new voice, names
and do not translate terms are kept as written, and every line that had
to be compressed is listed in a delivery note.

The agent is standard library Python plus `ffmpeg` and `ffprobe` on PATH.
The core path needs no account and no key.

## Files

| File | What it does |
| --- | --- |
| `dubber.py` | The CLI and pipeline: brief, transcribe, translate, fit, voice, mix, write outputs. |
| `providers.py` | The transcriber, translator, background separator and voice, each behind one interface. A hosted service is one new class. |
| `sync.py` | Fits each dubbed line to the original timing. |
| `tests/test_dubber.py` | Offline tests on a generated fixture video with synthetic speech. |

## Providers

| Job | Local options | Notes |
| --- | --- | --- |
| Transcription (segment timing) | `segments-file` | Timed segments another engine or service produced. A speech engine adapter goes here. |
| Translation | `glossary` | Operator supplied translations per segment and language, with optional shorter wordings. |
| Translation | `stub` | **Offline test stub, not a translation.** The report marks it "not a deliverable". |
| Background | `duck` | Local ffmpeg fallback: the original mix with the speech band cut and lowered. **Not true source separation**, and the delivery note says so. |
| Background | `demucs` | Optional true separation (the no_vocals stem). Needs the demucs package and its model, neither of which is in this repo. |
| Voice | `stub` | **Offline test voice**: a tone whose length follows the text. Not speech. |
| Voice | `flite` | Local stock voices (`slt`, `kal`, `awb`, `rms`, `kal16`) through ffmpeg's flite filter. English only; other languages are refused. |
| Voice | `own-voice` | Consent gated (see below). This build has no cloning engine. |

Protected terms: names (`--names`) and do not translate terms (`--dnt`)
are handled the same way for every translator.
- A machine translator only sees them masked as numbered placeholders.
- After any translator runs, each protected term in a source line must
  appear verbatim in its translation, or the run stops.

## The consent rule for the speaker's own voice

`--voice own-voice` refuses unless the job inputs carry a consent record
(`--consent FILE`) with all four fields:

```json
{"speaker_consent": true, "consent_record": "<where the consent is kept>",
 "rights_confirmed": true, "confirmed_by": "<who confirmed the rights>"}
```

A missing record, or any missing or false field, is refused with the
reason, and nothing is written.

Even with a complete record, this build then refuses with "no voice cloning
engine". A cloning provider would be added only after an award and an owner
decision, behind the same check. The tests prove both refusals.

## Sync

The order follows the proposal as issue #77 states it:

1. **Tighten:** use a shorter wording with the same meaning from the
   translator, if one fits.
2. **Stretch:** speed the line up, never beyond `--max-stretch`.
3. **Breathe:** run into the pause after the line, only when that pause is
   genuine (at least 0.4 s), keeping 0.1 s clear before the next line.

A line that still does not fit stops the run and names the segment. It is
never cut off. Every compressed line is listed in `report.md`, and the
subtitles always carry the full translation.

**The limits are defaults, not taken from the job text.** That is the
default `--max-stretch` of 1.15, the 0.4 s genuine pause and the 0.1 s gap.
The NEAR job description could not be read from the build container (see
issue #77). Adjust them to the job's stated limits on award.

## Runbook

1. **Plan first.** This prints every line's fit and the flagged lines, and
   writes no video:

   ```sh
   python3 agents/video-dubbing/dubber.py plan --video talk.mp4 \
     --segments segments.json --translator glossary --glossary glossary.json \
     --languages es,fr --voice flite --dnt "Hojo,NEAR"
   ```

2. **Run.** The same flags with `run --out out/`. The output folder gets:
   - `<stem>.<lang>.mp4`, the original video with the new audio;
   - `<stem>.<lang>.srt`;
   - `manifest.json`;
   - `report.md`, the delivery note.

3. **Deliver through the NEAR worker loop** (`near-agent/`, PR #52).
   `report.md` is the `deliverableMarkdown` for `worker.py submit`, sent
   as a dry run first. The worker sends no `files` field, so how the videos
   reach the buyer is **to confirm on award**.

A brief JSON (`--brief`) can carry `languages`, `voice`, `names`,
`do_not_translate` and `consent`.

## Tests

```sh
python3 -m unittest discover -s agents/video-dubbing/tests -v
```

CI runs them through `tools/tests/test_video_dubbing.py`.

The fixture is generated in the test and labelled there:
- a test pattern video;
- speech synthesized with flite's stock voice, so no real person;
- a generated two tone music bed;
- example segments, glossary and consent records written for the test.

The media tests skip when ffmpeg or its flite filter is missing.

## Listing draft

Not created anywhere. This is draft text for the owner.

**Video Dubbing Agent**: dubs your video into other languages, keeps the
music and sound underneath, keeps your names and brand terms as written,
and tells you exactly which lines had to be sped up.

**What you provide:**
- the video;
- the target languages;
- a voice choice;
- a list of names and terms that must not be translated;
- for the speaker's own voice only, a consent record (see below).

**What you get, per language:**
- one finished video;
- one subtitle file (SRT) with the full translation;
- a delivery note listing any line that was compressed to fit the timing.

**Languages:** set per job by the translation provider. The local stock
voices speak English. Other languages need a stock voice provider for that
language, confirmed before the job starts.

**Lengths:** the agent sets no fixed limit. Turnaround is agreed per job.

**Voice options:** stock voices. The speaker's own voice is available only
with a recorded consent from the speaker and a confirmation of rights, and
it is not offered in the current build.

**FAQ**

- *Will the timing match?* Each line is fitted to the original timing.
  Wording is tightened first, then speed is raised a little within a set
  limit, then the line may run into a natural pause. Any line that was
  sped up is named in the delivery note.
- *Do subtitles match the audio?* The subtitles carry the full translation.
  Where a shorter wording was spoken to fit the timing, the note says
  which lines.
- *Is the original voice removed completely?* With the local option, the
  original speech is cut back under the new voice rather than removed. Full
  separation uses a separate library and is stated in the delivery note
  when used.
