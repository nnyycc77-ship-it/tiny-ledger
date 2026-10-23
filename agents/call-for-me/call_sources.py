#!/usr/bin/env python3
"""Provider evaluation sources for the Call-for-Me Booking agent (issue #79).

Every claim in PROVIDERS.md quotes raw lines from a provider's own API
definition, pinned to an exact commit of the provider's public repository.
The spec files are large (Twilio 1.9 MB, Telnyx 8.4 MB), so they are not
committed. Instead sources/provenance.json records, per capture, the pinned
URL, retrieval time, byte count and sha256, and per claim the line numbers
and the raw lines. Anyone can re-fetch the pinned URLs and check both.

Commands (standard library only):
  python3 call_sources.py fetch  --out DIR    download the pinned files into DIR
  python3 call_sources.py build  --captures DIR [--retrieved FILE]
                                         locate every claim's lines in DIR and
                                         write sources/provenance.json
  python3 call_sources.py verify --captures DIR
                                         re-hash DIR and re-check every line

Only GitHub raw content is reachable from the build container; the providers'
documentation sites are refused there (recorded in PROVIDERS.md). No account,
key or trial is involved: these files are public.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROVENANCE = os.path.join(HERE, "sources", "provenance.json")

TWILIO_COMMIT = "d9775142962ea67d5f3d50c5021a23ae6d330c5b"
TELNYX_COMMIT = "5f12994582345f12feb4fd4dbe5ef80ad3693243"

CAPTURES = {
    "twilio_api_v2010.json": {
        "provider": "Twilio",
        "repo": "https://github.com/twilio/twilio-oai",
        "url": "https://raw.githubusercontent.com/twilio/twilio-oai/%s/spec/json/twilio_api_v2010.json" % TWILIO_COMMIT,
    },
    "twilio_pricing_v2.json": {
        "provider": "Twilio",
        "repo": "https://github.com/twilio/twilio-oai",
        "url": "https://raw.githubusercontent.com/twilio/twilio-oai/%s/spec/json/twilio_pricing_v2.json" % TWILIO_COMMIT,
    },
    "telnyx_spec3.json": {
        "provider": "Telnyx",
        "repo": "https://github.com/team-telnyx/openapi",
        "url": "https://raw.githubusercontent.com/team-telnyx/openapi/%s/openapi/spec3.json" % TELNYX_COMMIT,
    },
}

# Each claim: id, capture file, an anchor line (the first line containing it
# opens the endpoint or schema the claim is about), a needle (the first line
# after the anchor containing it is the excerpt), and how many lines to quote.
CLAIMS = [
    # Twilio, Programmable Voice REST API 2010-04-01
    ("twilio-outbound", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "Create a new outgoing call', 1),
    ("twilio-caller-id", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "The phone number or client identifier to use as the caller id.', 1),
    ("twilio-record-default", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "Whether to record the call.', 1),
    ("twilio-ring-timeout", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "The integer number of seconds that we should allow the phone to ring', 1),
    ("twilio-time-limit", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "The maximum duration of the call in seconds.', 1),
    ("twilio-machine-detection", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "Whether to detect if a human, answering machine, or fax has picked up the call.', 1),
    ("twilio-progress-events", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls.json": {',
     '"description": "The call progress events that we will send', 1),
    ("twilio-recording-delete", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Recordings/{Sid}.json": {',
     '"description": "Delete a recording from your account"', 1),
    ("twilio-transcription-engine", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Transcriptions.json": {',
     '"description": "Definition of the transcription engine to be used', 1),
    ("twilio-speech-model", "twilio_api_v2010.json", '"/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Transcriptions.json": {',
     '"description": "Recognition model used by the transcription engine', 1),
    ("twilio-price-fields", "twilio_pricing_v2.json", '"pricing.v2.voice.voice_number": {',
     '"outbound_call_prices": {', 18),
    ("twilio-price-unit", "twilio_pricing_v2.json", '"pricing.v2.voice.voice_number": {',
     '"description": "The currency in which prices are measured', 1),
    # Telnyx, API v2 Call Control
    ("telnyx-outbound", "telnyx_spec3.json", '"/calls": {',
     '"description": "Dial a number or SIP URI from a given connection.', 1),
    ("telnyx-record-default", "telnyx_spec3.json", '"CallRequest": {',
     '"description": "Start recording automatically after an event. Disabled by default."', 1),
    ("telnyx-transcription-default", "telnyx_spec3.json", '"CallRequest": {',
     '"description": "Enable transcription upon call answer. The default value is false."', 1),
    ("telnyx-ring-timeout", "telnyx_spec3.json", '"CallRequest": {',
     '"description": "The number of seconds that Telnyx will wait for the call to be answered', 1),
    ("telnyx-time-limit", "telnyx_spec3.json", '"CallRequest": {',
     '"description": "Sets the maximum duration of a Call Control Leg in seconds.', 1),
    ("telnyx-machine-detection", "telnyx_spec3.json", '"CallRequest": {',
     '"description": "Enables Answering Machine Detection.', 1),
    ("telnyx-transcription-engines", "telnyx_spec3.json", '"TranscriptionStartRequest": {',
     '"description": "Engine to use for speech recognition.', 18),
    ("telnyx-tts-voice", "telnyx_spec3.json", '"SpeakRequest": {',
     '"description": "Specifies the voice used in speech synthesis.', 1),
    ("telnyx-tts-service-level", "telnyx_spec3.json", '"SpeakRequest": {',
     '"description": "This parameter impacts speech quality', 1),
    ("telnyx-recording-delete", "telnyx_spec3.json", '"/recordings/{recording_id}": {',
     '"description": "Permanently deletes the specified call recording', 1),
    ("telnyx-pricing", "telnyx_spec3.json", '"/pricing/products/{slug}": {',
     '"description": "Returns pricing entries for a single product.', 1),
]


class SourceError(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().split("\n")


def locate(lines, anchor, needle, count):
    """Return (first line number, raw lines) for the claim, 1-based."""
    start = next((i for i, l in enumerate(lines) if anchor in l), None)
    if start is None:
        raise SourceError("anchor not found: %r" % anchor)
    hit = next((i for i in range(start, len(lines)) if needle in lines[i]), None)
    if hit is None:
        raise SourceError("needle not found after anchor %r: %r" % (anchor, needle))
    return hit + 1, lines[hit:hit + count]


def build(captures_dir, retrieved=None):
    retrieved = retrieved or {}
    out = {"_about": (
        "Captures of the providers' own OpenAPI definitions, pinned to a commit. "
        "The files are not committed (size); re-fetch the url and compare sha256. "
        "Each claim quotes raw lines from the capture by line number."),
        "captures": {}, "claims": []}
    cache = {}
    for name, meta in CAPTURES.items():
        path = os.path.join(captures_dir, name)
        if not os.path.exists(path):
            raise SourceError("capture missing: %s" % path)
        out["captures"][name] = dict(meta, sha256=sha256_file(path),
                                     bytes=os.path.getsize(path),
                                     retrieved_utc=retrieved.get(name, "not recorded"))
        cache[name] = read_lines(path)
    for cid, name, anchor, needle, count in CLAIMS:
        line_no, raw = locate(cache[name], anchor, needle, count)
        out["claims"].append({"id": cid, "file": name, "line": line_no,
                              "anchor": anchor, "raw": raw})
    return out


def load_provenance(path=PROVENANCE):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def verify(captures_dir, prov=None):
    """Re-hash every capture and re-check every quoted line. Returns problems."""
    prov = prov or load_provenance()
    problems = []
    for name, meta in prov["captures"].items():
        path = os.path.join(captures_dir, name)
        if not os.path.exists(path):
            problems.append("missing capture %s" % name)
            continue
        got = sha256_file(path)
        if got != meta["sha256"]:
            problems.append("sha256 mismatch for %s: %s != %s" % (name, got, meta["sha256"]))
            continue
        lines = read_lines(path)
        for claim in prov["claims"]:
            if claim["file"] != name:
                continue
            start = claim["line"] - 1
            if lines[start:start + len(claim["raw"])] != claim["raw"]:
                problems.append("claim %s: lines differ at %s:%d" % (claim["id"], name, claim["line"]))
    return problems


def source_link(prov, claim):
    """GitHub blob link to the quoted lines at the pinned commit."""
    meta = prov["captures"][claim["file"]]
    end = claim["line"] + len(claim["raw"]) - 1
    lines = "#L%d" % claim["line"] if end == claim["line"] else "#L%d-L%d" % (claim["line"], end)
    owner, repo, rest = meta["url"][len("https://raw.githubusercontent.com/"):].split("/", 2)
    return "https://github.com/%s/%s/blob/%s%s" % (owner, repo, rest, lines)


def fetch(out_dir, opener=None):
    opener = opener or urllib.request.urlopen
    os.makedirs(out_dir, exist_ok=True)
    stamps = {}
    import datetime
    for name, meta in CAPTURES.items():
        with opener(meta["url"], timeout=120) as resp:
            data = resp.read()
        with open(os.path.join(out_dir, name), "wb") as fh:
            fh.write(data)
        stamps[name] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return stamps


def main(argv=None, stdout=sys.stdout, stderr=sys.stderr):
    ap = argparse.ArgumentParser(prog="call_sources.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--out", required=True)
    b = sub.add_parser("build"); b.add_argument("--captures", required=True)
    b.add_argument("--retrieved", help="JSON file mapping capture name to retrieval time (UTC)")
    v = sub.add_parser("verify"); v.add_argument("--captures", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "fetch":
            stamps = fetch(args.out)
            print(json.dumps(stamps, indent=2), file=stdout)
        elif args.cmd == "build":
            retrieved = None
            if args.retrieved:
                with open(args.retrieved, "r", encoding="utf-8") as fh:
                    retrieved = json.load(fh)
            prov = build(args.captures, retrieved)
            with open(PROVENANCE, "w", encoding="utf-8") as fh:
                json.dump(prov, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("wrote %s: %d captures, %d claims" % (PROVENANCE, len(prov["captures"]), len(prov["claims"])), file=stdout)
        else:
            problems = verify(args.captures)
            for p in problems:
                print("FAIL " + p, file=stdout)
            if problems:
                return 1
            print("PASS every capture hash and quoted line matches", file=stdout)
    except (SourceError, OSError) as exc:
        print("error: %s" % exc, file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
