# Video Clipping Agent: listing copy

**Status:** Paste ready once two operator steps are done:
- The host has a local speech engine. The `vosk` package and a model named by `VOSK_MODEL_PATH` are not in the repo, or a hosted engine class is added.
- The route by which clip files reach the buyer is confirmed. The README marks it "to confirm on award", because the worker loop sends no files field.

**Sources:** `agents/video-clipping/README.md` (listing draft, runbook); issue #74 text (bid 150 USDC, working agent promised within 5 days of award). No job description or proposal text for job 06d8adcb is recorded in the repo.

## Paste order

### 1. Name

Video Clipping Agent

### 2. Category

To confirm at award. The job description for job 06d8adcb is not recorded in the repo.

### 3. Suggested price per hire

10 USD. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. One hire returns one report: one report plus the clip files. The core path needs no account or key, so the repo records no per job provider cost.

### 4. Listing description

Turns one long talking video into short, captioned clips for vertical, square and landscape feeds, each with a stated reason it was picked.

Clips are chosen from what is in the video itself, with no view data:
- questions with their answers, and claims with their payoff;
- strong opening lines, louder delivery, and possible audience reactions;
- natural topic breaks.

Clips that open mid-thought are marked down. The vertical crop follows the part of the frame with the most movement, which is usually the speaker. If the video does not have enough good moments, you are told plainly, and no padding clips are cut.

### 5. What buyers provide

- the source video file (any file ffmpeg can read that has an audio track);
- how many clips you want;
- which shapes: vertical 9:16, square 1:1, or landscape 16:9;
- whether you want captions burned in;
- optionally, a clip length range (15 to 60 seconds unless you say otherwise).

### 6. Delivery window

- **Per hire:** not stated in the README. To confirm at award.
- **Bid build commitment (issue #74 text):** "The proposal promised a working agent within 5 days of award." 

### 7. FAQ

- *What do I get?* The clips as MP4 (H.264 video, AAC audio) in each shape you asked for. You also get a caption file per clip when captions are on, and a short report listing each clip's time range, the reason it was chosen, and its transcript.
- *How are clips chosen without view data?* From what is in the video itself: questions with their answers, claims with their payoff, strong opening lines, louder delivery, possible audience reactions, and natural topic breaks. Clips that open mid-thought are marked down.
- *Will the speaker stay in frame on vertical clips?* The crop follows the part of the frame with the most movement, which is usually the speaker. Wide shots with several moving people can pull it off centre, and the report shows each crop.
- *How accurate are the captions?* As accurate as the transcription engine. The clip report includes the transcript, so it can be checked.
- *What if my video does not have enough good moments?* You are told plainly how many fitting moments there are. Padding clips are not cut to make up the number.

## Fixes against the README draft

- "Vertical and square feeds" now reads "vertical, square and landscape feeds", because the build has a landscape 16:9 preset and the draft's own "What you provide" offers it.
- "Audience reactions" now reads "possible audience reactions", matching the build's own label ("Possible laughter or applause", because the agent cannot tell which).
- Added the delivery window line.

## To confirm at award

- The category, from the job description for job 06d8adcb.
- The per hire delivery window.
- The speech engine on the host.
- How clip files reach the buyer.
