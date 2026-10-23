# video-clipping: the Video Clipping agent

Task: issue #74, built ahead of any award for the NEAR Agent Market job
"Video Clipping Agent" (job 06d8adcb-4635-4d54-83df-4ef7bbbc8344). This
folder holds the agent. It creates no listing, sends no bid, and contacts
no one.

One long video and a brief go in. Short clips come out, sized per platform,
reframed to keep the speaker in frame, with captions burned in only when
the brief asks. Every clip comes with a one line reason it was chosen.

The agent is standard library Python plus `ffmpeg` and `ffprobe` on PATH.
The core path needs no account and no key.

## Files

| File | What it does |
| --- | --- |
| `clipper.py` | The CLI and pipeline: brief, transcribe, score, choose, cut, write outputs. |
| `transcribe.py` | The transcription engines, behind one interface. A hosted engine is one new class here. |
| `scoring.py` | Moment scoring from the source's own signals, and from retention data when supplied. |
| `media.py` | The ffmpeg and ffprobe wrappers: probe, audio energy, speaker tracking, crop, captions, cut. |
| `tests/test_clipper.py` | Offline tests on a fixture video the test generates itself. |

## Runbook

1. **Brief.** Pass flags, or a JSON file with
   `{"clips": 3, "platforms": ["tiktok", "landscape"], "captions": true, "min_seconds": 15, "max_seconds": 60}`.
   - Platform shapes: `tiktok`, `reels` and `shorts` (1080x1920), `square`
     (1080x1080), and `landscape` (1920x1080).
   - These are encoding presets for the shapes buyers ask for. They are not
     statements of any platform's rules.

2. **Transcription engine.**
   - `--engine vosk` runs local speech recognition with word timing. It
     needs the `vosk` package and a model directory named by
     `VOSK_MODEL_PATH`. Neither is in this repo.
   - `--engine transcript-file --transcript words.json` reads word timings
     another engine already produced, in the shape `{"words": [{"w", "start", "end"}]}`.
   - To use a hosted engine, add one class to `transcribe.py`. Nothing else
     changes.

3. **Plan first.** This prints the chosen moments, their reasons and every
   ffmpeg command, and encodes nothing:

   ```sh
   python3 agents/video-clipping/clipper.py plan --video talk.mp4 --engine vosk \
     --clips 3 --platforms tiktok,landscape --captions
   ```

4. **Run.** The same flags with `run --out out/`. The output folder gets
   these files:
   - `clip_NN_<platform>.mp4`;
   - `clip_NN.srt` when captions are on;
   - `manifest.json`: moments, scores, reasons, crop boxes and files;
   - `report.md`: the deliverable text.

5. **Change specific clips** (issue #129, job criterion 7: "When asked to
   change specific clips, it changes only those clips and keeps the rest as
   delivered"). This writes a new folder and leaves the earlier delivery
   untouched:

   ```sh
   python3 agents/video-clipping/clipper.py revise --from out/ --clips 2 \
     --video talk.mp4 --engine vosk --note "a different moment for clip 2" --out out-rev1/
   ```

   - Without bounds, each named clip gets the next best moment. That moment
     overlaps neither a kept clip nor the clip it replaces, and its reason
     line starts "next best moment after the change request".
   - With `--start S --end E`, for one clip only, the buyer sets the bounds.
     Bounds that cut through a word, or overlap a kept clip, are refused.
   - The source must be the same file: same name and same duration as in
     the earlier `manifest.json`.
   - A delivery made with `--retention FILE` is revised with the same file,
     so the new moment is ranked on the same basis. Without the file it is
     refused. A retention file for a delivery that had none is refused too.
   - Every file of the other clips is copied byte for byte. The changed
     clips are cut again in every platform of the original brief, with
     captions if the brief had them.
   - `report.md` gains a "Revision" section. It quotes the change request
     and lists every file as changed (with its old SHA-256) or kept as
     delivered.
   - `manifest.json` gains a `revision` block.
   - A refusal writes nothing.

6. **Deliver through the NEAR worker loop** (`near-agent/`, PR #52).
   1. `worker.py poll` shows the assignment.
   2. The operator runs this agent on the buyer's file.
   3. `report.md` is the `deliverableMarkdown` that `worker.py submit`
      carries, as a dry run first, per `near-agent/README.md`.

   The worker sends no `files` field, so how the clip files reach the buyer
   (a link, or the market's attachment route) is **to confirm on award**.

**Fails closed.** The agent stops with exit 2 and writes no deliverable on
any of these:
- a probe, transcription or encode failure;
- a source with no audio;
- an empty transcript;
- a brief it cannot meet, such as fewer good moments than clips asked for.

## How moments are chosen

Each candidate is a run of whole sentences that fits the length range. It
scores on these signals:

| Signal | What scores it |
| --- | --- |
| Self contained question and answer | A question sentence followed by its answer. |
| Claim and payoff | A claim cue early and a payoff cue later, both inside the clip. |
| Strong opening line | A short first sentence that asks, hooks, or addresses the viewer. |
| Speech energy peak | Speech louder than the file's median, measured over spoken frames only. |
| Possible laughter or applause | A burst of sound with no words over it. It is named "possible" because the agent cannot tell which. |
| Topic boundary | A long pause before or after the clip. |
| Needs context (penalised) | The clip opens on a word that refers back, such as "and", "but" or "it". |

The best non overlapping candidates win. Each one's reason line names the
signals that scored it.

**Retention or "most replayed" data** (issue #130). When the buyer has this
data for the video, pass it with `--retention FILE`. The file is a JSON
object in this repo's own stated shape:

```json
{"kind": "most_replayed",
 "source": "where the data came from, in the operator's words",
 "points": [{"t": 0, "value": 0.2}, {"t": 32, "value": 1.0}]}
```

- **Shape.** `kind` is `most_replayed` or `audience_retention`. `t` is
  seconds into this video. `value` is any non-negative number. At least two
  points are needed, with strictly increasing times.
- **Converting.** This is not any platform's export format. The operator
  converts what the buyer supplies, such as an analytics export, into
  these pairs. The agent fetches nothing.
- **Fails closed.** A malformed file, or one that runs past the video's
  end, stops the run with exit 2.
- **Scoring.** The curve is linear between points. Each candidate scores
  8 points per unit of its mean retention above the video's median, which
  outranks every content signal together. The clips therefore come from the
  high retention parts wherever a run of whole sentences fits there. Each
  reason line opens with the lift, such as "high retention: 1.80x the
  video's median in the most replayed data".
- **Report.** The report's opening line says the moments were ranked first
  by the data, and quotes its `source`. A "Retention data" section then
  lists the data's top moments, one per stretch above the median and as
  many as clips asked for. Each entry names the clip that covers it, or
  says why none does:
  - no run of whole sentences of the requested length contains it;
  - it overlaps a clip that scored higher;
  - it scored below the chosen clips.

**Without the file**, the report says "Moments are chosen from the
transcript and the audio, with no retention data."

The vertical reframe tracks motion. It samples small grey frames across
the clip and centres the crop on where the frame changes most. With no
motion it uses the centre.

## Tests

```sh
python3 -m unittest discover -s agents/video-clipping/tests -v
```

The CI job runs the suite through `tools/tests/test_video_clipping.py`,
with no workflow change.

The fixture is generated media, made in the test and labelled there:
- an ffmpeg test pattern panel on the right of a grey frame, standing in
  for the speaker;
- a sine tone whose loudness changes by segment;
- a synthetic word timing transcript.

It contains no third party content, uses no network, and is not the output
of any speech recognition. The suite skips when ffmpeg is missing.

## Listing draft

Not created anywhere. This is draft text for the owner, in the job's naming
style.

**Video Clipping Agent**: turns one long talking video into short, captioned
clips for vertical and square feeds, each with a stated reason it was
picked.

**What you provide:**
- the source video file;
- how many clips you want;
- which shapes (vertical 9:16, square 1:1, landscape 16:9);
- whether you want captions burned in;
- optionally, a clip length range;
- optionally, your video's retention or "most replayed" data, if you have
  it. Clips are then picked from the most watched moments, and the report
  says which.

**What you get:**
- the clips as MP4 (H.264 video, AAC audio) in each shape you asked for;
- a caption file per clip when captions are on;
- a short report listing each clip's time range, the reason it was chosen,
  and its transcript.

**Supported input:** any video file ffmpeg can read that has an audio
track. The clip length range is set by the brief (15 to 60 seconds unless
you say otherwise).

**FAQ**

- *How are clips chosen without view data?* From what is in the video
  itself: questions with their answers, claims with their payoff, strong
  opening lines, louder delivery, audience reactions, and natural topic
  breaks. Clips that open mid-thought are marked down.
- *Will the speaker stay in frame on vertical clips?* The crop follows the
  part of the frame with the most movement, which is usually the speaker.
  Wide shots with several moving people can pull it off centre. The report
  shows each crop.
- *How accurate are the captions?* As accurate as the transcription engine.
  The clip report includes the transcript, so it can be checked.
- *What if my video does not have enough good moments?* You are told plainly
  how many fitting moments there are. Padding clips are not cut to make up
  the number.
