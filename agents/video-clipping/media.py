"""ffmpeg and ffprobe wrappers: probing, audio energy, speaker tracking, cutting.

Everything here shells out to ffmpeg or ffprobe and fails closed: a non
zero exit raises MediaError with ffmpeg's own message, and nothing is
guessed in its place.
"""

import array
import json
import math
import os
import shutil
import subprocess


class MediaError(RuntimeError):
    """ffmpeg or ffprobe failed, or the media is not usable."""


# Output size presets: width, height. These are encoding presets for the
# shapes buyers ask for, not statements of any platform's rules.
PLATFORMS = {
    "tiktok": (1080, 1920),
    "reels": (1080, 1920),
    "shorts": (1080, 1920),
    "square": (1080, 1080),
    "landscape": (1920, 1080),
}

ENERGY_STEP = 0.25  # seconds per audio energy frame
ENERGY_RATE = 8000  # Hz, mono, for energy only


def require_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        raise MediaError("missing on PATH: %s" % ", ".join(missing))


def _run(cmd, cwd=None):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    if proc.returncode != 0:
        raise MediaError("%s failed: %s" % (cmd[0], proc.stderr.decode("utf-8", "replace").strip()[-800:]))
    return proc.stdout


def probe(path):
    """Duration in seconds, video width and height, and whether audio exists."""
    out = _run(["ffprobe", "-v", "error", "-show_entries",
                "format=duration:stream=codec_type,width,height", "-of", "json", path])
    info = json.loads(out.decode("utf-8"))
    video = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    audio = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not video:
        raise MediaError("%s has no video stream" % path)
    try:
        duration = float(info["format"]["duration"])
    except (KeyError, ValueError):
        raise MediaError("%s reports no duration" % path)
    return {"duration": duration, "width": int(video[0]["width"]),
            "height": int(video[0]["height"]), "has_audio": bool(audio)}


def audio_energy(path):
    """RMS energy per ENERGY_STEP second frame, as a list of floats (0 to 1)."""
    raw = _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-vn",
                "-ac", "1", "-ar", str(ENERGY_RATE), "-f", "s16le", "-"])
    samples = array.array("h")
    samples.frombytes(raw[: len(raw) - len(raw) % 2])
    step = int(ENERGY_RATE * ENERGY_STEP)
    energy = []
    for i in range(0, len(samples), step):
        frame = samples[i:i + step]
        if not frame:
            break
        energy.append(math.sqrt(sum(s * s for s in frame) / len(frame)) / 32768.0)
    return energy


def horizontal_focus(path, start, duration, width, height):
    """Where the action is across the frame, as a fraction 0 to 1 of the width.

    Samples low resolution grey frames from the clip and sums the frame to
    frame change in each column; the centroid of that motion is taken as
    the speaker's position. With no motion at all the centre (0.5) is used.
    """
    small_w = 96
    small_h = max(2, int(round(small_w * height / width / 2.0)) * 2)
    raw = _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", "%.3f" % start,
                "-t", "%.3f" % duration, "-i", path,
                "-vf", "fps=4,scale=%d:%d,format=gray" % (small_w, small_h),
                "-f", "rawvideo", "-"])
    size = small_w * small_h
    frames = [raw[i:i + size] for i in range(0, len(raw) - size + 1, size)]
    columns = [0.0] * small_w
    for prev, cur in zip(frames, frames[1:]):
        for idx in range(size):
            diff = cur[idx] - prev[idx]
            if diff:
                columns[idx % small_w] += abs(diff)
    total = sum(columns)
    if total == 0:
        return 0.5
    return sum((x + 0.5) * v for x, v in enumerate(columns)) / total / small_w


def crop_box(src_w, src_h, out_w, out_h, focus_x):
    """The crop rectangle (w, h, x, y) that matches the output aspect and
    keeps focus_x (fraction of width) as near the centre as the frame allows."""
    target = out_w / float(out_h)
    if src_w / float(src_h) > target:
        crop_h = src_h - src_h % 2
        crop_w = int(crop_h * target) // 2 * 2
        x = int(round(focus_x * src_w - crop_w / 2.0))
        x = max(0, min(src_w - crop_w, x))
        return crop_w, crop_h, x, 0
    crop_w = src_w - src_w % 2
    crop_h = min(src_h, int(crop_w / target) // 2 * 2)
    return crop_w, crop_h, 0, (src_h - crop_h) // 2


def srt_time(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def write_srt(path, words, clip_start, clip_end, max_words=6):
    """Caption lines for the words inside the clip, times relative to it."""
    inside = [w for w in words if w.start >= clip_start and w.end <= clip_end]
    cues = [inside[i:i + max_words] for i in range(0, len(inside), max_words)]
    with open(path, "w", encoding="utf-8") as fh:
        for n, cue in enumerate(cues, 1):
            fh.write("%d\n%s --> %s\n%s\n\n" % (
                n, srt_time(cue[0].start - clip_start), srt_time(cue[-1].end - clip_start),
                " ".join(w.text for w in cue)))
    return len(cues)


def cut_command(src, start, duration, box, out_w, out_h, out_name, srt_name=None,
                preset="veryfast"):
    """The ffmpeg command for one clip, run with cwd set to the output folder."""
    crop_w, crop_h, x, y = box
    vf = "crop=%d:%d:%d:%d,scale=%d:%d,setsar=1" % (crop_w, crop_h, x, y, out_w, out_h)
    if srt_name:
        vf += (",subtitles=%s:force_style='FontName=DejaVu Sans,FontSize=14,"
               "Outline=2,Alignment=2,MarginV=40'" % srt_name)
    return ["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-ss", "%.3f" % start, "-t", "%.3f" % duration, "-i", os.path.abspath(src),
            "-vf", vf, "-c:v", "libx264", "-preset", preset, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_name]


def run_in(cmd, cwd):
    _run(cmd, cwd=cwd)
