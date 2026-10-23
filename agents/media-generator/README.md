# media-generator: the Pay-Per-Use Media Generator agent (issue #78)

Built ahead of any award for the NEAR Agent Market job "Pay-Per-Use Media
Generator" (job `b33f7e41-b395-4534-9748-555e2327b761`), so that an award
can be answered inside its promised window. This folder holds the agent. It
creates no listing, sends no bid, contacts no one, **calls no live
provider anywhere, reads no key and spends nothing.**

One brief goes in: one request, or several under `requests`. The requested
images, short videos and voiceovers come out with a report naming the
provider and model of every file, plus a manifest that lets a later change
request touch only the files the buyer names.

Standard library only. No package, no account, no key.

**Spec.** The job description and the bid proposal are quoted verbatim by
the coordinator on issue #78. This build was reconciled against both; both
hashes were checked against the comment bodies (see Sources). Where they
leave a number open (the size tolerance, the default lengths, the keyword
lists), the number here is this build's stated choice and is printed in
every report.

## Files

| File | What it does |
| --- | --- |
| `mediagen.py` | The CLI and pipeline: brief, content rules, routing, brief check, one regeneration, report and manifest, revise, calibrate. |
| `mediagen_providers/base.py` | The provider interface and the live slot base. |
| `mediagen_providers/image.py`, `video.py`, `voice.py` | One module per media type: the offline stub and the live slot. |
| `mediagen_providers/policy.py` | The job's content rules, screened before any generation. |
| `mediagen_providers/placeholder.py` | Writes and reads the placeholder PNG, GIF and WAV files the stubs make. |
| `quality.json` | The recorded local test table the router reads (see "Quality table"). |
| `tests/test_mediagen.py` | Offline tests, discovered in CI through `tools/tests/test_media_generator.py`. |

## The brief

A JSON object for one request, or `{"requests": [ ... ]}` for up to 20.
Unknown fields are refused.

| Field | Applies to | Format | Default |
| --- | --- | --- | --- |
| `type` | all | `image`, `video` or `voice` | required |
| `subject` | all | text; its content words are what the brief check looks for | required |
| `style` | all | text, added to the prompt | none |
| `brand` | all | brand colours or fonts, free text, added to the prompt | none |
| `format` | all | `png` (image), `gif` (video), `wav` (voice) in the stub build | per type |
| `count` | all | number of variations, a positive integer | 1 |
| `size` | image, video | exact `WxH`, for example `1024x1024` | none |
| `aspect` | image, video | `W:H`, for example `9:16`; must agree with `size` when both are given | image `1:1`, video `16:9` when no size |
| `length_seconds` | video, voice | positive number | video 5 s; voice: script words at 2.5 words per second (a stated assumption, printed in the report) |
| `script` | voice | the text to read, word for word | required for voice |
| `voice` | voice | a voice id the provider offers | provider's choice |
| `references` | all | reference images or material, file paths or links | none |
| `rights_confirmed` | all | `true` when the buyer confirms they hold the rights to the references | `false` |
| `depicts_real_person` | all | `true` when the request shows a real, identifiable person | `false` |
| `person_consent` | all | `true` when the buyer confirms they are that person or have their consent | `false` |
| `brand_owned` | all | `true` when the buyer confirms they own the logo or brand asked for | `false` |

## The content rules

Screened per request before routing (`mediagen_providers/policy.py`). The
rules are the job description's, quoted there. A request that breaks one
is **declined**: nothing is generated for it, the report gives the rule and
the reason, and the other requests in the same brief go ahead.

| Rule | Declined when |
| --- | --- |
| Reference rights | references are given and `rights_confirmed` is not true |
| Real person without consent | `depicts_real_person` is true, or the text names a real person in words ("celebrity", "politician", "influencer", and the like), and `person_consent` is not true |
| Copyrighted character | the text names a well known character from a stated list |
| Brand or logo not owned | the text names a logo or a brand from a stated list and `brand_owned` is not true |
| Sexual content, graphic violence, deceptive content | the text uses a word from the stated list for that rule ("fake news", "deepfake", and the like) |

What it cannot do: a keyword list cannot recognise every real person,
character or brand by name. It catches the categories a brief names in
words and the listed names. A live build adds the chosen providers' own
moderation and a name recognition step before buyer work; neither is built
here.

## Routing

Rules first, then quality.

1. **Rules**: a provider is excluded when its media type, formats, size
   limit or aspects, length limit, per call count limit, reference
   following, voices or recorded terms of use (`commercial_use`, the
   operator's reading of the provider's terms on commercial use and
   resale) do not fit. A provider that is not configured is excluded too.
   The report lists every provider with the reason it was excluded or how
   it ranked.
2. **Quality**: the eligible providers are ranked by their recorded pass
   rate in `quality.json` for that request type (`image`, `image+refs`,
   `video`, `voice`). A provider with no record for the type ranks as 0, and
   ties go by name. The job description's example, a provider that accepts
   per request payment, is a rule the operator records when wiring a live
   provider.

### Providers in this build

| Provider | Type | Model id reported | Status |
| --- | --- | --- | --- |
| `stub-image` | image | `placeholder-png-1` | Offline placeholder PNGs, any size up to 1024 px, up to 8 per call. Not reference following. |
| `stub-image-refs` | image | `placeholder-png-refs-1` | The same writer declared reference following, so reference briefs have an offline route. **It does not read the reference files**; its output is a placeholder like the rest. |
| `stub-video` | video | `placeholder-gif-1` | Offline placeholder animated GIFs, up to 10 s, 5 frames per second, up to 256 px. |
| `stub-voice` | voice | `placeholder-wav-1` | Offline placeholder WAV tones that record the script given, up to 60 s, voices `stock-warm-female` and `stock-calm-male`. **Not speech.** |
| `live-image`, `live-video`, `live-voice` | each | (chosen at award) | Slots only. No vendor is chosen and no request shape is written; each reports not configured and refuses to generate. Wiring a vendor is a new class in the matching module, with its key read from the environment (`MEDIAGEN_IMAGE_KEY`, `MEDIAGEN_VIDEO_KEY`, `MEDIAGEN_VOICE_KEY`), never from a file here. That is an operator decision at award, as is recording each vendor's terms of use. |

### Quality table

`quality.json` is written by:

```sh
python3 agents/media-generator/mediagen.py calibrate --out agents/media-generator/quality.json
```

It runs the fixed calibration briefs in `mediagen.py` (built on the job
description's sample scenarios) through every configured provider the rules
allow, and records each provider's pass rate per request type against the
brief check, with the UTC time. The committed table was recorded that way
on 2026-10-23 from this build. Only the stub providers are configured, so
every recorded rate is for placeholder media and says nothing about any
live provider. A test checks that the committed table equals a fresh
calibration apart from the time.

## The brief check

On every file:

- **Format**: the file must parse as the requested format.
- **Size or aspect**: exactly the requested `size`, or within 5 percent of
  the requested aspect.
- **Length**: video and voice within one second of the requested length
  (the job description's acceptance criterion 2).
- **Count**: as many files as variations asked for.
- **Script**: a voiceover's recorded script must match the brief's script
  word for word; case and punctuation are not counted as changes.
- **Subject terms**: every content word of the subject must appear in the
  prompt the provider recorded.
- **Obvious defects**: a one colour image, a single frame video, silent
  audio.

What it cannot do: it does not look at what an image or video depicts, and
it does not listen to what a voice says; for the stubs it reads what the
provider recorded. For a live provider, two checks are needed before buyer
delivery: a content check of each image and video against the subject
terms (for example a captioning or tagging model), and a transcript of each
voiceover compared with the script word for word. Neither is built here.

### Regeneration

- A first attempt that misses only on subject terms is regenerated once on
  the same provider, with the prompt adjusted to name the missed terms
  ("Must clearly show: ...").
- Any other miss (format, size, length, script, defect, a provider error) is
  regenerated once on the next ranked provider, or on the same one when no
  other is eligible.
- Never more than two attempts per request. If both miss, the closest
  result (fewest misses) is delivered with a plain list of what did not
  match, the rerun command, and the revise command for just those files.
  It is never a silent substitution. If neither attempt produced a file,
  nothing is delivered for that request and the report says why.

## Revisions

```sh
python3 agents/media-generator/mediagen.py revise --from DIR --files r1-mug-2.png --out DIR-revised --note "brighter light"
```

Regenerates only the named files of an earlier delivery, with the note
added to the prompt, and copies every other file byte for byte into the new
folder (the job description's acceptance criterion 7). The revision report
lists each file as changed (with its old SHA-256) or kept as delivered. It
refuses a file name that was not delivered, an output folder equal to the
input, and a delivery whose files no longer match their recorded hashes.

## Run

```sh
python3 agents/media-generator/mediagen.py generate --brief brief.json --out /tmp/media-out
```

The files, `delivery-note.md` (the report) and `delivery.json` (the
manifest) are written to the output folder, and the report is also
printed. Exit 0 when at least one file was delivered, 3 when a report was
written but no file was delivered (every request declined or failed), and 2
with nothing written for an unreadable or invalid brief.

In the NEAR worker loop (`near-agent/worker.py`, issue #48) the operator
runs this on the buyer's brief and submits the report and files through
`worker.py submit` after reading the dry run. This folder never talks to
the marketplace.

## How the job description's acceptance criteria are met

| Criterion | Where |
| --- | --- |
| 1. The requested number of files of each type, within the stated delivery time | count check per request; the sample scenario test counts files per request. Delivery time is stated at award, see the listing draft |
| 2. Every file the requested size or aspect, every video or voiceover within one second | size, aspect and length checks; length tolerance is 1 s |
| 3. Every subject, object and setting named is visible or audible | subject terms are checked against what the provider recorded; a content check for live providers is still owed (see "The brief check") |
| 4. Voiceovers read the script word for word | script check against what the provider recorded; a transcript check for live providers is still owed |
| 5. The report names the provider and model of each file | the Delivered table in the report and the manifest |
| 6. Requests against the rules are declined, and the report says why | the content rules screen and the Declined section |
| 7. Changing specific files keeps the rest as delivered | the revise command |

The four sample scenarios in the job description (three square mug images,
an 8 second vertical pour video, a 30 second voiceover from a script, a
celebrity request) run as one brief in `tests/test_mediagen.py`.

## Listing draft (for the owner, at award; not created by this task)

**Category:** Creative.

**Name:** AI Image, Video & Voiceover Generator (pay per job)

**What it creates:** product photos and other still images, short videos,
and voiceovers from a plain language brief. You do not need an account
with any generation service.

**What you provide:** what to make (image, video or voiceover), the
subject, the style, the format (size or aspect ratio, and length for video
and voice), how many variations, and optionally reference images, brand
colours or fonts, and the voiceover script. For reference material, confirm
you hold the rights to it. For a real person, confirm you are that person
or have their consent. For a logo or brand, confirm you own it.

**Formats and lengths:** stated at award from the live providers wired
then; this build's offline stubs make PNG, GIF and WAV only, which are not
the listed formats.

**Typical delivery time:** stated at award from measured provider times.
Not measured here, because no live provider is wired.

**How per job pricing covers generation cost.** The price per job must
cover the worst case: each file can be generated at most twice (the first
attempt plus one regeneration), so a job's generation cost is at most
2 x the number of files x the chosen provider's unit cost for that media
type, size and length. The per job price is set at award as that worst case
plus the operator's margin. The unit costs come from the chosen providers'
own price pages, read and recorded at award; none is stated here, because
no provider is chosen yet. The manifest records the provider, model and
attempt of every file, which is what a cost check needs.

**FAQ**

- *Which models does it use?* The report names the provider and model of
  every file. The agent picks the provider that fits your brief first and
  the one that scored best in its own tests for that kind of request second.
- *What if a file does not match my brief?* It is regenerated once
  automatically. If it still misses, you get the closest result with a note
  saying exactly what did not match, and you can rerun.
- *Can I change one file and keep the others?* Yes. Name the files to
  change; every other file stays exactly as delivered.
- *What will it not make?* Real, identifiable people without consent,
  copyrighted characters, logos and brands you don't own, sexual content,
  graphic violence, or content meant to deceive. Those parts of a request
  are declined and the report says why; the rest of the request goes ahead.

## Verification

```sh
python3 -m unittest discover -s agents/media-generator/tests -v
python3 -m unittest discover -s tools/tests -v      # includes this suite through the CI shim
```

The tests make no network request. They cover the brief rules, the content
rules and declines, the routing rules and quality per request type, the
live slots never being routed, the brief check's misses (including length
within one second and the word for word script), the regeneration paths,
the four sample scenarios, revisions, the committed quality table, and that
no module imports a network library. The providers that miss on purpose
are test classes labelled where they are defined.

## Sources

- Task text: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/78>.
- Job description, quoted verbatim by the coordinator from the NEAR Agent
  Market board on 2026-10-23:
  <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/78#issuecomment-6366897388>
  (7941 characters, SHA-256
  `89b6834a9e64c78493f512347943034fee6e2546a07fcb10dc9683b3c9fbb219`).
- Bid proposal as placed (bid 35f71935, 150 USDC), quoted verbatim by the
  coordinator from the agent's own bids on 2026-10-23:
  <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/78#issuecomment-6366897988>
  (1614 characters, SHA-256
  `eeadb717beff377d4eba52c6095115ab2da58e0754e022cfd19be0963c4d5280`).
- Marketplace loop: `near-agent/README.md` and its sources on issue #48.
