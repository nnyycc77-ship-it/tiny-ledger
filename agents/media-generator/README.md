# media-generator: the Pay-Per-Use Media Generator agent (issue #78)

Built ahead of any award for the NEAR Agent Market job "Pay-Per-Use Media
Generator" (job `b33f7e41-b395-4534-9748-555e2327b761`), so that an award
can be answered inside its promised window. This folder holds the agent. It
creates no listing, sends no bid, contacts no one, **calls no live
provider anywhere, reads no key and spends nothing.**

One media brief goes in. The requested images, short videos or voice clips
come out, with a delivery note recording the brief, the routing decision,
the provider used, every attempt with its check results, and each file's
SHA-256.

Standard library only. No package, no account, no key.

**To confirm against the job description.** The task issue says the job's
full description is the spec. Neither it nor the bid proposal is in this
repository yet (requested on issue #78), so the brief field names, the
formats and the defaults below follow the summary in issue #78 and are
marked as to confirm.

## Files

| File | What it does |
| --- | --- |
| `mediagen.py` | The CLI and pipeline: brief, rights rule, routing, brief check, one regeneration, delivery note, calibration. |
| `mediagen_providers/base.py` | The provider interface and the live slot base. |
| `mediagen_providers/image.py`, `video.py`, `voice.py` | One module per media type: the offline stub and the live slot. |
| `mediagen_providers/placeholder.py` | Writes and reads the placeholder PNG, GIF and WAV files the stubs make. |
| `quality.json` | The recorded local test table the router reads (see "Quality table"). |
| `tests/test_mediagen.py` | Offline tests, discovered in CI through `tools/tests/test_media_generator.py`. |

## The brief (to confirm)

A JSON object. Unknown fields are refused.

| Field | Applies to | Format | Default |
| --- | --- | --- | --- |
| `type` | all | `image`, `video` or `voice` | required |
| `subject` | all | text; its content words are what the brief check looks for | required |
| `style` | all | text, appended to the prompt | none |
| `format` | all | `png` (image), `gif` (video), `wav` (voice) in the stub build | per type |
| `count` | all | positive integer | 1 |
| `aspect` | image, video | `W:H`, for example `16:9` | image `1:1`, video `16:9` |
| `length_seconds` | video, voice | positive number | video 5 s; voice: script words at 2.5 words per second (stated assumption, printed in the note) |
| `script` | voice | the text to speak | required for voice |
| `voice` | voice | a voice id the provider offers | provider's choice |
| `references` | all | list of file paths or links to reference material | none |
| `rights_confirmed` | all | `true` when the buyer confirms they hold the rights to the references | `false` |

**The rights rule.** A brief with references and without
`rights_confirmed: true` is refused before routing, with exit 2 and
nothing written. The refusal says why and how to resubmit.

## Routing

Rules first, then quality.

1. **Rules**: a provider is excluded when its media type, formats, aspects,
   length limit, per call count limit, reference following or voices do
   not fit the brief. A provider that is not configured is excluded too.
   The note lists every provider with the reason it was excluded or how it
   ranked.
2. **Quality**: the eligible providers are ranked by their recorded pass
   rate in `quality.json`; a provider with no record ranks as 0; ties go
   by name.

### Providers in this build

| Provider | Type | Status |
| --- | --- | --- |
| `stub-image` | image | Offline placeholder PNGs. Up to 8 per call. Not reference following. |
| `stub-image-refs` | image | The same writer declared reference following, so reference briefs have an offline route. **It does not read the reference files**; the note marks its output as placeholder. |
| `stub-video` | video | Offline placeholder animated GIFs, up to 10 s, 5 frames per second. |
| `stub-voice` | voice | Offline placeholder WAV tones, up to 60 s, voices `stock-a` and `stock-b`. **Not speech.** |
| `live-image`, `live-video`, `live-voice` | each | Slots only. No vendor is chosen and no request shape is written; each reports not configured and refuses to generate. Wiring a vendor is a new class in the matching module, with its key read from the environment (`MEDIAGEN_IMAGE_KEY`, `MEDIAGEN_VIDEO_KEY`, `MEDIAGEN_VOICE_KEY`), never from a file here. That is an operator decision at award. |

### Quality table

`quality.json` is written by:

```sh
python3 agents/media-generator/mediagen.py calibrate --out agents/media-generator/quality.json
```

It runs the fixed calibration briefs in `mediagen.py` through every
configured provider the rules allow and records each provider's pass rate
against the brief check, with the UTC time. The committed table was
recorded that way on 2026-10-23 from this build. Only the stub providers
are configured, so every recorded rate is for placeholder media and says
nothing about any live provider. A test checks that the committed table
equals a fresh calibration apart from the time. When live providers are
wired, rerunning `calibrate` records their rates the same way.

## The brief check

On every output:

- **Format**: the file must parse as the requested format.
- **Size or aspect**: within 5 percent of the requested aspect.
- **Length**: video and voice within 10 percent of the requested length.
- **Count**: as many outputs as asked.
- **Subject terms**: every content word of the subject must appear in the
  prompt the provider recorded in the file.
- **Obvious defects**: a one colour image, a single frame video, silent
  audio.

What it cannot do: it does not look at what an image or video depicts. For
the stubs the recorded prompt is the whole truth, because they draw a
pattern. For a live provider a content check (for example a captioning or
tagging model compared with the subject terms) is needed before buyer
delivery. That check is not built here.

### Regeneration

- A first attempt that misses only on subject terms is regenerated once on
  the same provider, with the prompt adjusted to name the missed terms
  ("Must clearly show: ...").
- Any other miss (format, size, length, defect, a provider error) is
  regenerated once on the next ranked provider, or on the same one when no
  other is eligible.
- Never more than two attempts. If both miss, the closest result (fewest
  misses) is delivered with a plain list of what did not match and the
  exact rerun command. If neither attempt produced any file, the run exits
  2 and nothing is delivered.

## Run

```sh
python3 agents/media-generator/mediagen.py generate --brief brief.json --out /tmp/media-out
```

The media files and `delivery-note.md` are written to the output folder,
and the note is also printed. In the NEAR worker loop (`near-agent/worker.py`,
issue #48) the operator runs this on the buyer's brief and submits the
delivery note and files through `worker.py submit` after reading the dry
run. This folder never talks to the marketplace.

## Listing draft (for the owner, at award; not created by this task)

**Name:** Pay-Per-Use Media Generator: images, short video and voice from
one brief

**What it does:** Send a brief: what to make (image, short video or voice
clip), the subject, the style, the format, how many, and any reference
material. The agent picks the provider that fits the brief, checks every
result against the brief, regenerates once if something is off, and
returns the files with a delivery note saying which provider made them and
what was checked.

**What you provide:** the brief fields above. For reference based work,
confirm that you hold the rights to the material; without that the brief is
refused.

**How per job pricing covers generation cost (once live providers are
wired).** The price per job must cover the worst case: each output can be
generated at most twice (the first attempt plus one regeneration), so the
generation cost of a job is at most 2 x count x the chosen provider's unit
cost for that media type, length and resolution. The per job price is set
at award as that worst case plus the operator's margin. The unit costs come
from the chosen providers' own price pages, read and recorded at award;
none is stated here, because no provider is chosen yet. The delivery note
already records the provider and the number of attempts per job, which is
what a cost reconciliation needs.

**FAQ**

- *Which providers does it use?* At award, the operator wires one live
  provider per media type. The router picks among them by the brief's needs
  first and by recorded quality second, and the note names the one used.
- *What if the result does not match my brief?* It is regenerated once
  automatically. If it still misses, you get the closest result with a note
  saying exactly what did not match, and you can rerun with a changed brief.
- *Can I send reference images?* Yes, with your confirmation that you hold
  the rights to them.
- *Does it check that the image shows my subject?* In this build it checks
  the format, size, length, count, obvious defects and the subject terms in
  the provider's own record. A content check of the picture itself comes
  with the live providers at award.

## Verification

```sh
python3 -m unittest discover -s agents/media-generator/tests -v
python3 -m unittest discover -s tools/tests -v      # includes this suite through the CI shim
```

The tests make no network request. They cover the brief rules, the rights
refusal, the routing rules and quality order, the live slots never being
routed, the brief check's misses, the regeneration paths (an adjusted prompt
for a missed term, the next provider for a defect, the closest result with a
note after a second miss, a provider error), the CLI and the note, the
committed quality table, and that no module imports a network library. The
providers that miss on purpose are test classes labelled where they are
defined.

## Sources

- Task text: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/78>.
- Marketplace loop: `near-agent/README.md` and its sources on issue #48.
- The job description and the bid proposal: requested on issue #78; not yet
  in this repository.
