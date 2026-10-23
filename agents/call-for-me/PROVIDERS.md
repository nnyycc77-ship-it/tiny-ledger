# Provider evaluation: programmable voice for the Call-for-Me agent

Issue #79, item 2. Two providers compared on the facts this agent needs: outbound calling, speech recognition and synthesis, per call cost shape, and recording controls. No account was created, no trial started and no key used. Every claim below is sourced from the provider's own API definition, published in the provider's own GitHub organisation and pinned to one commit, in the AGENT-BRIEF evidence format: the claim, the source link, and the raw lines printed directly beneath.

## What could be read from the build container

The providers' documentation and pricing sites are refused by this container's network gateway. Raw output of the probe, exactly as printed:

```
probe started 2026-10-23T13:51:19Z
curl: (56) CONNECT tunnel failed, response 403 000  https://www.twilio.com/docs/voice  
curl: (56) CONNECT tunnel failed, response 403 000  https://www.twilio.com/en-us/voice/pricing/us  
curl: (56) CONNECT tunnel failed, response 403 000  https://telnyx.com/pricing/call-control  
curl: (56) CONNECT tunnel failed, response 403 000  https://developers.telnyx.com/docs/voice/programmable-voice/get-started  
curl: (56) CONNECT tunnel failed, response 403 000  https://developer.vonage.com/en/voice/voice-api/overview  
curl: (56) CONNECT tunnel failed, response 403 000  https://docs.plivo.com/docs/voice/  
```

GitHub raw content is reachable, and both Twilio and Telnyx publish their API definitions there as OpenAPI files: `twilio/twilio-oai` and `team-telnyx/openapi`. Those files are the providers' own machine-readable API documentation, so they are the source for every claim below. They are 1.9 MB and 8.4 MB, so they are not committed. `sources/provenance.json` records each file's pinned URL, retrieval time, size and sha256, plus every quoted line by number. `python3 call_sources.py fetch --out DIR` then `python3 call_sources.py verify --captures DIR` re-checks all of it.

| Capture | Pinned URL | Retrieved (UTC) | Bytes | sha256 |
| --- | --- | --- | --- | --- |
| twilio_api_v2010.json | <https://raw.githubusercontent.com/twilio/twilio-oai/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json> | 2026-10-23T13:36:18Z | 1878657 | `bfdf249a129819af274d6bdc7672156ea3416ad48670a6f0544def6ef386ba87` |
| twilio_pricing_v2.json | <https://raw.githubusercontent.com/twilio/twilio-oai/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_pricing_v2.json> | 2026-10-23T13:36:18Z | 51833 | `5f6cd2972bd77516708b86cbe3b4bfb6ffe381fb7b918d5815bb5d25d939b83b` |
| telnyx_spec3.json | <https://raw.githubusercontent.com/team-telnyx/openapi/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json> | 2026-10-23T13:36:19Z | 8425641 | `49c60b9ee81d9ab1992e27e8bea7e7a1389020b8182f5168719ddd4a66a24ade` |

Vonage and Plivo were considered and not evaluated. The Vonage API specification paths tried on GitHub returned 404, and Plivo was found only as an SDK, which is not documentation.

## Comparison

| Fact this agent needs | Twilio | Telnyx |
| --- | --- | --- |
| Outbound calls through an API | yes [twilio-outbound] | yes [telnyx-outbound] |
| Caller ID needs a provider number or verified ID | yes [twilio-caller-id] | awaiting capture |
| Recording off unless requested | yes, `Record` default `false` [twilio-record-default] | yes, disabled by default [telnyx-record-default] |
| Recording deletable through the API | yes [twilio-recording-delete] | yes, permanent [telnyx-recording-delete] |
| Transcription off unless requested | not stated in the spec | yes, default `false` [telnyx-transcription-default] |
| Real-time speech recognition | yes, engine and model selectable, names not listed [twilio-transcription-engine] [twilio-speech-model] | yes, named engines, default Google [telnyx-transcription-engines] |
| Speech synthesis voices | awaiting capture (TwiML `<Say>` is not in the REST spec) | named providers per command [telnyx-tts-voice], quality tier setting [telnyx-tts-service-level] |
| Ring timeout per call | default 60 s, max 600 s [twilio-ring-timeout] | default 30 s, 5 to 600 s [telnyx-ring-timeout] |
| Call time limit per call | yes [twilio-time-limit] | yes, max 14400 s [telnyx-time-limit] |
| Answering machine detection | yes [twilio-machine-detection] | yes, Premium and Standard [telnyx-machine-detection] |
| Attempt results reported | progress events to a callback [twilio-progress-events] | webhooks with a hang-up cause [telnyx-ring-timeout] [telnyx-time-limit] |
| Cost shape | per destination number, base and current price, currency; billing unit not stated [twilio-price-fields] [twilio-price-unit] | per product rate entries with unit and direction [telnyx-pricing] |
| Price figures | awaiting capture | awaiting capture |

## What these sources cannot settle

- **Price figures and billing unit.** The specs give price fields, not figures. Awaiting capture of each provider's US voice pricing page.
- **Speech recognition and synthesis quality.** No documentation can show this. It needs a listening test on real calls, which needs an account. That is an owner decision at award, so it is not assessed here.
- **Retention on the provider side.** Recording is off by default on both, and both can delete recordings. Whether real-time transcription text is retained by the provider after delivery is not stated in either spec. The design's "no transcript kept" rule depends on this, so it is an open item, awaiting capture.
- **Rules on automated calls.** These are law, not provider facts. They are not sourced here and stay with the owner, as the job's limitations say.

Pages to capture, named for the coordinator per the Option B pattern. These URLs are candidates. They could not be opened from here, so whether each one exists is unverified:

- Twilio US voice pricing: <https://www.twilio.com/en-us/voice/pricing/us>
- Twilio `<Say>` and `<Gather>` speech docs: <https://www.twilio.com/docs/voice/twiml/say>, <https://www.twilio.com/docs/voice/twiml/gather>
- Twilio real-time transcription data handling: <https://www.twilio.com/docs/voice/api/realtime-transcription-resource>
- Telnyx Call Control pricing: <https://telnyx.com/pricing/call-control>
- Telnyx transcription data handling: <https://developers.telnyx.com/docs/voice/programmable-voice/get-started>

## Recommendation for the award stage

Either provider covers the call flow in DESIGN.md: outbound dial, ring timeout, time limit, machine detection, recording off by default and deletable, and real-time recognition. Telnyx's spec states more of the defaults this agent relies on: transcription off by default, and named recognition engines and synthesis voices. That makes it slightly easier to show the no-transcript rule from documentation. The choice should wait for the price figures and the retention answers above. Choosing, buying a number and opening an account are owner decisions.

## Evidence

### Twilio

**[twilio-outbound]** Twilio's Calls resource places outgoing calls to phone numbers.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13324> (pinned commit, line 13324; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
        "description": "Create a new outgoing call to phones, SIP-enabled endpoints or Twilio Client connections",
```

**[twilio-caller-id]** The caller ID (`From`) must be a Twilio number or a verified outgoing caller ID on the account, so live calling needs a number bought or verified on an account. That is spend and an account, both owner decisions at award.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13494> (pinned commit, line 13494; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "The phone number or client identifier to use as the caller id. If using a phone number, it must be a Twilio number or a Verified [outgoing caller id](https://www.twilio.com/docs/voice/api/outgoing-caller-ids) for your account. If the `to` parameter is a phone number, `From` must also be a phone number."
```

**[twilio-record-default]** Recording is off unless asked for: `Record` defaults to `false`.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13550> (pinned commit, line 13550; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "Whether to record the call. Can be `true` to record the phone call, or `false` to not. The default is `false`. The `recording_url` is sent to the `status_callback` URL."
```

**[twilio-ring-timeout]** Ring time before treating the call as unanswered is set per call: default 60 seconds, maximum 600.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13546> (pinned commit, line 13546; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "The integer number of seconds that we should allow the phone to ring before assuming there is no answer. The default is `60` seconds and the maximum is `600` seconds. For some call flows, we will add a 5-second buffer to the timeout value you provide. For this reason, a timeout value of 10 seconds could result in an actual timeout closer to 15 seconds. You can set this to a short time, such as `15` seconds, to hang up before reaching an answering machine or voicemail."
```

**[twilio-time-limit]** A maximum call duration can be set per call (`TimeLimit`); the spec says constraints depend on account and configuration.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13659> (pinned commit, line 13659; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "The maximum duration of the call in seconds. Constraints depend on account and configuration."
```

**[twilio-machine-detection]** Answering machine detection is available per call (`Enable` or `DetectMessageEnd`), which the agent needs to tell voicemail from a person.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13583> (pinned commit, line 13583; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "Whether to detect if a human, answering machine, or fax has picked up the call. Can be: `Enable` or `DetectMessageEnd`. Use `Enable` if you would like us to return `AnsweredBy` as soon as the called party is identified. Use `DetectMessageEnd`, if you would like to leave a message on an answering machine. If `send_digits` is provided, this parameter is ignored. For more information, see [Answering Machine Detection](https://www.twilio.com/docs/voice/answering-machine-detection)."
```

**[twilio-progress-events]** Call progress events (`initiated`, `ringing`, `answered`, `completed`) are sent to a status callback, which is where each attempt's result comes from.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L13529> (pinned commit, line 13529; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "The call progress events that we will send to the `status_callback` URL. Can be: `initiated`, `ringing`, `answered`, and `completed`. If no event is specified, we send the `completed` status. If you want to receive multiple events, specify each one in a separate `status_callback_event` parameter. See the code sample for [monitoring call progress](https://www.twilio.com/docs/voice/api/call-resource?code-sample=code-create-a-call-resource-and-specify-a-statuscallbackevent&code-sdk-version=json). If an `application_sid` is present, this parameter is ignored."
```

**[twilio-recording-delete]** A recording can be deleted through the API.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L30632> (pinned commit, line 30632; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
        "description": "Delete a recording from your account",
```

**[twilio-transcription-engine]** Real-time transcription of a call can be started through the API with a chosen transcription engine. The spec does not list the engines.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L30197> (pinned commit, line 30197; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "Definition of the transcription engine to be used, among those supported by Twilio"
```

**[twilio-speech-model]** The recognition model is also selectable per transcription. The spec does not list the models.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_api_v2010.json#L30205> (pinned commit, line 30205; captured 2026-10-23T13:36:18Z, file sha256 `bfdf249a129819af…`)

```
                    "description": "Recognition model used by the transcription engine, among those supported by the provider"
```

**[twilio-price-fields]** Voice pricing is published per destination number as `outbound_call_prices` records with `base_price` and `current_price`. The spec does not state the billing unit (per minute or otherwise) and gives no figures.

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_pricing_v2.json#L386-L403> (pinned commit, line 386 to 403; captured 2026-10-23T13:36:18Z, file sha256 `5f6cd2972bd77516…`)

```
          "outbound_call_prices": {
            "type": "array",
            "items": {
              "type": "object",
              "format": "outbound-call-price-with-origin",
              "properties": {
                "base_price": {
                  "type": "number",
                  "x-twilio": {
                    "overrideType": "string"
                  }
                },
                "current_price": {
                  "type": "number",
                  "x-twilio": {
                    "overrideType": "string"
                  }
                },
```

**[twilio-price-unit]** Prices carry a currency (`price_unit`).

Source: <https://github.com/twilio/twilio-oai/blob/d9775142962ea67d5f3d50c5021a23ae6d330c5b/spec/json/twilio_pricing_v2.json#L442> (pinned commit, line 442; captured 2026-10-23T13:36:18Z, file sha256 `5f6cd2972bd77516…`)

```
            "description": "The currency in which prices are measured, specified in [ISO 4127](https://www.iso.org/iso/home/standards/currency_codes.htm) format (e.g. `usd`, `eur`, `jpy`)."
```

### Telnyx

**[telnyx-outbound]** Telnyx's Call Control `Dial` command places outgoing calls to a number from a Call Control connection.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L28271> (pinned commit, line 28271; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
        "description": "Dial a number or SIP URI from a given connection. A successful response will include a `call_leg_id` which can be used to correlate the command with subsequent webhooks.\n\nTo place the call with an AI assistant from the start, include `assistant.id` and any per-call overrides in the `assistant` object; Telnyx attempts to warm up the assistant before placing the call and starts it automatically when the called party answers.\n\n**Expected Webhooks:**\n\n- `call.initiated`\n- `call.answered` or `call.hangup`\n- `call.conversation.created` when the requested assistant conversation is created, or `call.conversation.start_failed` when it could not be started after the called party answered\n- `call.hold` and `call.unhold` if the call is held/unheld\n- `call.machine.detection.ended` if `answering_machine_detection` was requested\n- `call.machine.greeting.ended` if `answering_machine_detection` was requested to detect the end of machine greeting\n- `call.machine.premium.detection.ended` if `answering_machine_detection=premium` was requested\n- `call.machine.premium.greeting.ended` if `answering_machine_detection=premium` was requested and a beep was detected\n- `call.machine.premium.call_screening.detected` if `answering_machine_detection=premium_ios_call_screening_detection` was requested and an Apple Call Screening tone was detected\n- `call.deepfake_detection.result` if `deepfake_detection` was enabled\n- `call.deepfake_detection.error` if `deepfake_detection` was enabled and an error occurred\n- `streaming.started`, `streaming.stopped` or `streaming.failed` if `stream_url` was set\n\nWhen the `record` parameter is set to `record-from-answer`, the response will include a `recording_id` field.\n",
```

**[telnyx-record-default]** Automatic recording on dial is disabled by default.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L129548> (pinned commit, line 129548; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Start recording automatically after an event. Disabled by default.",
```

**[telnyx-transcription-default]** Transcription on answer is off by default (`transcription` defaults to `false`).

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L129640> (pinned commit, line 129640; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Enable transcription upon call answer. The default value is false.",
```

**[telnyx-ring-timeout]** Ring time before hang-up is set per call: default 30 seconds, minimum 5, maximum 600, and a `call.hangup` webhook reports `timeout`.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L129024> (pinned commit, line 129024; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "The number of seconds that Telnyx will wait for the call to be answered by the destination to which it is being called. If the timeout is reached before an answer is received, the call will hangup and a `call.hangup` webhook with a `hangup_cause` of `timeout` will be sent. Minimum value is 5 seconds. Maximum value is 600 seconds.",
```

**[telnyx-time-limit]** A maximum call duration is set per call: default and maximum 14400 seconds, and a `call.hangup` webhook reports `time_limit`.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L129037> (pinned commit, line 129037; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Sets the maximum duration of a Call Control Leg in seconds. If the time limit is reached, the call will hangup and a `call.hangup` webhook with a `hangup_cause` of `time_limit` will be sent. For example, by setting a time limit of 120 seconds, a Call Leg will be automatically terminated two minutes after being answered. The default time limit is 14400 seconds or 4 hours and this is also the maximum allowed call length.",
```

**[telnyx-machine-detection]** Answering machine detection is available in Premium and Standard forms, with results such as `human_business` and `machine`.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L129046> (pinned commit, line 129046; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Enables Answering Machine Detection. Telnyx offers Premium and Standard detections. With Premium detection, when a call is answered, Telnyx runs real-time detection and sends a `call.machine.premium.detection.ended` webhook with one of the following results: `human_residence`, `human_business`, `machine`, `silence` or `fax_detected`. If we detect a beep, we also send a `call.machine.premium.greeting.ended` webhook with the result of `beep_detected`. If we detect a beep before `call.machine.premium.detection.ended` we only send `call.machine.premium.greeting.ended`, and if we detect a beep after `call.machine.premium.detection.ended`, we send both webhooks. With Standard detection, when a call is answered, Telnyx runs real-time detection to determine if it was picked up by a human or a machine and sends an `call.machine.detection.ended` webhook with the analysis result. If `greeting_end` or `detect_words` is used and a `machine` is detected, you will receive another `call.machine.greeting.ended` webhook when the answering machine greeting ends with a beep or silence. If `detect_beep` is used, you will only receive `call.machine.greeting.ended` if a beep is detected. If `answering_machine_detection` is set to `premium_ios_call_screening_detection`, Premium AMD runs with iOS Call Screening support: after an initial `machine` result, Telnyx listens for the iOS call-screening prompt to end or for an Apple Call Screening tone, sends `call.machine.premium.greeting.ended` with `result=prompt_ended` or `call.machine.premium.call_screening.detected` with `result=screening` respectively. When the Apple Call Screening tone is detected, Premium AMD is restarted on the screened call and a `call.machine.premium.detection.ended` webhook with the post-screening classification follows.",
```

**[telnyx-transcription-engines]** Real-time speech recognition can use one of several named engines (Google, Telnyx, Deepgram, Azure and others), default Google.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L205171-L205188> (pinned commit, line 205171 to 205188; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Engine to use for speech recognition. Legacy values `A` - `Google`, `B` - `Telnyx` are supported for backward compatibility.",
            "type": "string",
            "enum": [
              "Google",
              "Telnyx",
              "Deepgram",
              "Azure",
              "xAI",
              "AssemblyAI",
              "Speechmatics",
              "Soniox",
              "Parakeet",
              "Humain",
              "Reson8",
              "Cohere",
              "A",
              "B"
            ],
```

**[telnyx-tts-voice]** Speech synthesis voices are chosen per command from named providers (the excerpt lists AWS Polly, Azure, ElevenLabs and Telnyx, among others).

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L191709> (pinned commit, line 191709; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "Specifies the voice used in speech synthesis.\n\n- Define voices using the format `<Provider>.<Model>.<VoiceId>`. Specifying only the provider will give default values for voice_id and model_id.\n\n **Supported Providers:**\n- **AWS:** Use `AWS.Polly.<VoiceId>` (e.g., `AWS.Polly.Joanna`). For neural voices, which provide more realistic, human-like speech, append `-Neural` to the `VoiceId` (e.g., `AWS.Polly.Joanna-Neural`). Check the [available voices](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html) for compatibility.\n- **Azure:** Use `Azure.<VoiceId>` (e.g., `Azure.en-CA-ClaraNeural`, `Azure.en-US-BrianMultilingualNeural`, `Azure.en-US-Ava:DragonHDLatestNeural`). For a complete list of voices, go to [Azure Voice Gallery](https://speech.microsoft.com/portal/voicegallery). Use `voice_settings` to configure custom deployments, regions, or API keys.\n- **ElevenLabs:** Use `ElevenLabs.<ModelId>.<VoiceId>` (e.g., `ElevenLabs.eleven_multilingual_v2.21m00Tcm4TlvDq8ikWAM`). The `ModelId` part is optional. To use ElevenLabs, you must provide your ElevenLabs API key as an integration identifier secret in `\"voice_settings\": {\"api_key_ref\": \"<secret_identifier>\"}`. See [integration secrets documentation](https://developers.telnyx.com/api/secrets-manager/integration-secrets/create-integration-secret) for details. Check [available voices](https://elevenlabs.io/docs/api-reference/get-voices).\n- **Telnyx:** Use `Telnyx.<model_id>.<voice_id>` (e.g., `Telnyx.KokoroTTS.af`). Use `voice_settings` to configure voice_speed and other synthesis parameters. `Bayan` provides Arabic (multiple dialects) and English voices (e.g., `Telnyx.Bayan.Ahmed`, `Telnyx.Bayan.Amanda`). `Sukhan` provides Urdu voices (e.g., `Telnyx.Sukhan.urdu-professor`); `voice_speed` is not supported.\n- **Minimax:** Use `Minimax.<ModelId>.<VoiceId>` (e.g., `Minimax.speech-02-hd.Wise_Woman`). Supported models: `speech-02-turbo`, `speech-02-hd`, `speech-2.6-turbo`, `speech-2.8-turbo`. Use `voice_settings` to configure speed, volume, pitch, and language_boost.\n- **Resemble:** Use `Resemble.Turbo.<voice_id>` (e.g., `Resemble.Turbo.my_voice`). Only `Turbo` model is supported. Use `voice_settings` to configure precision, sample_rate, and format.\n- **Inworld:** Use `Inworld.<ModelId>.<VoiceId>` (e.g., `Inworld.Mini.Loretta`, `Inworld.Max.Oliver`, `Inworld.TTS2.Loretta`). Supported models: `Mini`, `Max`, `TTS2`. Use `voice_settings` to configure `delivery_mode` (`STABLE`, `BALANCED`, `CREATIVE`), supported by `TTS2` only.\n- **Fish Audio:** Use `FishAudio.<ModelId>.<VoiceId>` (e.g., `FishAudio.s2.1-pro.<reference_id>`). Supported models: `s2.1-pro`, `s2-pro`, `s1`. `VoiceId` is a Fish Voice-Library reference ID.\n- **Soniox:** Use `Soniox.<ModelId>.<VoiceId>` (e.g., `Soniox.tts-rt-v2.Emma`). Supported model: `tts-rt-v2`. Browse the catalog via the [Voices API](https://developers.telnyx.com/api-reference/text-to-speech-commands/list-available-voices). Every voice speaks all supported languages; set `language` to the two-letter ISO 639-1 code of the text, for example `it`. SSML is not supported. Use `voice_settings` to configure `speed` (0.7 to 1.3) and `reduce_silence`.\n- **xAI:** Use `xAI.<VoiceId>` (e.g., `xAI.eve`). Available voices: `eve`, `ara`, `rex`, `sal`, `leo`.\n- **Humain:** Use `Humain.<VoiceId>` (e.g., `Humain.sara-ar`). Available voices: `sara-en`, `abdulaziz-en`, `sara-ar`, `abdulaziz-ar`, `nourah-ar`, `abdullah-ar`. Native Arabic (Saudi dialect) and English voices only \u2014 no `ModelId` segment.\n\nFor service_level basic, you may define the gender of the speaker (male or female).",
```

**[telnyx-tts-service-level]** A `service_level` setting affects speech quality; `basic` allows only `en-US` and plain text.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L191694> (pinned commit, line 191694; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
            "description": "This parameter impacts speech quality, language options and payload types. When using `basic`, only the `en-US` language and payload type `text` are allowed.",
```

**[telnyx-recording-delete]** A call recording can be permanently deleted through the API.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L78567> (pinned commit, line 78567; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
        "description": "Permanently deletes the specified call recording and returns the deleted recording resource. The media is removed and can no longer be downloaded.",
```

**[telnyx-pricing]** Pricing is published per product through the API, as rate entries with fields such as rate, unit, country and direction. The spec gives no figures.

Source: <https://github.com/team-telnyx/openapi/blob/5f12994582345f12feb4fd4dbe5ef80ad3693243/openapi/spec3.json#L76278> (pinned commit, line 76278; captured 2026-10-23T13:36:19Z, file sha256 `49c60b9ee81d9ab1…`)

```
        "description": "Returns pricing entries for a single product. Most products return standard rate entries with fields like rate, unit, country_iso, direction, and tiers. Inference products return model-specific fields (model, input_rate, output_rate, cached_input_rate) with tiered pricing. Some products use rate decks (pricing_type: rate_deck) where rates are determined dynamically.",
```
