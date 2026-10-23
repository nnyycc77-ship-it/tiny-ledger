"""Placeholder media writers for the offline stub providers (issue #78).

Standard library only. Every file written here is a PLACEHOLDER: it is a
valid file of the requested format, sized and timed as the brief asks, and
it carries the generation prompt in its metadata, but it is not real
generated media. The delivery note says so for every stub output.

    png_image(path, width, height, prompt, seed)     PNG with a tEXt prompt chunk
    gif_video(path, width, height, seconds, fps, prompt, seed)
                                                     animated GIF with a comment extension
    wav_voice(path, seconds, prompt, seed)           16 bit mono WAV tone, prompt in a LIST/INFO chunk

The readers below are what the brief check uses: they parse only these
three formats and fail on anything else.
"""

import hashlib
import struct
import wave
import zlib

# ----------------------------------------------------------------------
# colour pattern derived from the prompt, so different prompts differ
# ----------------------------------------------------------------------

def _palette(prompt, seed):
    digest = hashlib.sha256(("%s|%d" % (prompt, seed)).encode("utf-8")).digest()
    return [(digest[i], digest[i + 1], digest[i + 2]) for i in range(0, 24, 3)]


# ----------------------------------------------------------------------
# PNG
# ----------------------------------------------------------------------

def _chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def png_image(path, width, height, prompt, seed=0):
    colours = _palette(prompt, seed)
    rows = []
    band = max(1, width // len(colours))
    for y in range(height):
        row = bytearray([0])  # filter type 0
        for x in range(width):
            r, g, b = colours[(x // band + y // band) % len(colours)]
            row += bytes((r, g, b))
        rows.append(bytes(row))
    raw = b"".join(rows)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += _chunk(b"tEXt", b"Description\x00" + prompt.encode("latin-1", "replace"))
    data += _chunk(b"tEXt", b"Software\x00tiny-ledger media-generator stub (placeholder, not generated media)")
    data += _chunk(b"IDAT", zlib.compress(raw, 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


def read_png(path):
    """(width, height, {key: text}, distinct colours sampled) or raise ValueError."""
    with open(path, "rb") as fh:
        data = fh.read()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG file")
    pos, width, height, texts, idat = 8, None, None, {}, b""
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated PNG chunk header")
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if len(body) != length:
            raise ValueError("truncated PNG chunk")
        if kind == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"tEXt" and b"\x00" in body:
            k, v = body.split(b"\x00", 1)
            texts[k.decode("latin-1")] = v.decode("latin-1")
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
        if kind == b"IEND":
            break
    if width is None:
        raise ValueError("PNG has no IHDR")
    try:
        raw = zlib.decompress(idat)
    except zlib.error as exc:
        raise ValueError("PNG image data does not decompress: %s" % exc)
    stride = 1 + width * 3
    if len(raw) != stride * height:
        raise ValueError("PNG image data has the wrong size for %dx%d RGB" % (width, height))
    colours = set()
    for y in range(0, height, max(1, height // 8)):
        row = raw[y * stride + 1:(y + 1) * stride]
        for x in range(0, width, max(1, width // 8)):
            colours.add(row[x * 3:x * 3 + 3])
    return width, height, texts, len(colours)


# ----------------------------------------------------------------------
# GIF (uncompressed LZW: 8 bit codes with a clear code every 100 pixels)
# ----------------------------------------------------------------------

_LZW_MIN = 7          # 128 colour palette; codes are 8 bits wide
_CLEAR, _END = 128, 129
_RUN = 100            # literals between clear codes, well below the width change at 256


def _lzw_bytes(indices):
    codes = bytearray()
    for i in range(0, len(indices), _RUN):
        codes.append(_CLEAR)
        codes += bytes(indices[i:i + _RUN])
    codes.append(_END)
    out = bytearray([_LZW_MIN])
    for i in range(0, len(codes), 255):
        block = codes[i:i + 255]
        out.append(len(block))
        out += block
    out.append(0)
    return bytes(out)


def gif_video(path, width, height, seconds, fps, prompt, seed=0):
    colours = _palette(prompt, seed)
    table = bytearray()
    for i in range(128):
        r, g, b = colours[i % len(colours)]
        table += bytes(((r + i) % 256, (g + 2 * i) % 256, (b + 3 * i) % 256))
    frames = max(1, int(round(seconds * fps)))
    delay = max(2, int(round(100.0 / fps)))  # hundredths of a second
    data = bytearray(b"GIF89a")
    data += struct.pack("<HHBBB", width, height, 0xF6, 0, 0)  # global table, 128 entries
    data += table
    data += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00"    # loop forever
    comment = ("prompt: %s | tiny-ledger media-generator stub (placeholder, not generated media)" % prompt).encode("latin-1", "replace")
    data += b"\x21\xFE"
    for i in range(0, len(comment), 255):
        block = comment[i:i + 255]
        data += bytes([len(block)]) + block
    data += b"\x00"
    band = max(1, width // 8)
    for f in range(frames):
        data += b"\x21\xF9\x04\x04" + struct.pack("<H", delay) + b"\x00\x00"
        data += b"\x2C" + struct.pack("<HHHHB", 0, 0, width, height, 0)
        indices = [((x + f * 3) // band + y // band) % 128 for y in range(height) for x in range(width)]
        data += _lzw_bytes(indices)
    data += b"\x3B"
    with open(path, "wb") as fh:
        fh.write(bytes(data))


def read_gif(path):
    """(width, height, frames, seconds, comment text) or raise ValueError."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:6] not in (b"GIF89a", b"GIF87a"):
        raise ValueError("not a GIF file")
    width, height, flags = struct.unpack("<HHB", data[6:11])
    pos = 13
    if flags & 0x80:
        pos += 3 * (2 ** ((flags & 0x07) + 1))
    frames, centis, comment = 0, 0, ""
    pending_delay = 0

    def sub_blocks(p):
        out = bytearray()
        while True:
            if p >= len(data):
                raise ValueError("truncated GIF sub blocks")
            size = data[p]
            p += 1
            if size == 0:
                return bytes(out), p
            out += data[p:p + size]
            p += size

    while pos < len(data):
        tag = data[pos]
        if tag == 0x3B:
            break
        if tag == 0x21:
            label = data[pos + 1]
            body, pos = sub_blocks(pos + 2)
            if label == 0xF9 and len(body) >= 3:
                pending_delay = struct.unpack("<H", body[1:3])[0]
            elif label == 0xFE:
                comment += body.decode("latin-1")
        elif tag == 0x2C:
            iflags = data[pos + 9]
            pos += 10
            if iflags & 0x80:
                pos += 3 * (2 ** ((iflags & 0x07) + 1))
            pos += 1  # LZW minimum code size
            _, pos = sub_blocks(pos)
            frames += 1
            centis += pending_delay
            pending_delay = 0
        else:
            raise ValueError("unexpected GIF block 0x%02x at %d" % (tag, pos))
    else:
        raise ValueError("GIF has no trailer")
    if frames == 0:
        raise ValueError("GIF has no frames")
    return width, height, frames, centis / 100.0, comment


# ----------------------------------------------------------------------
# WAV
# ----------------------------------------------------------------------

def wav_voice(path, seconds, prompt, seed=0, rate=16000):
    import math
    base = 180 + (hashlib.sha256(("%s|%d" % (prompt, seed)).encode()).digest()[0] % 120)
    n = int(seconds * rate)
    frames = bytearray()
    for i in range(n):
        envelope = min(1.0, i / 800.0, (n - i) / 800.0)
        v = int(12000 * envelope * math.sin(2 * math.pi * base * i / rate))
        frames += struct.pack("<h", v)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    # append a LIST/INFO chunk carrying the prompt, then fix the RIFF size
    text = ("%s | tiny-ledger media-generator stub (placeholder tone, not speech)" % prompt).encode("latin-1", "replace") + b"\x00"
    if len(text) % 2:
        text += b"\x00"
    info = b"INFO" + b"ICMT" + struct.pack("<I", len(text)) + text
    chunk = b"LIST" + struct.pack("<I", len(info)) + info
    with open(path, "r+b") as fh:
        fh.seek(0, 2)
        fh.write(chunk)
        size = fh.tell() - 8
        fh.seek(4)
        fh.write(struct.pack("<I", size))


def read_wav(path):
    """(seconds, peak amplitude, comment text) or raise ValueError."""
    try:
        with wave.open(path, "rb") as w:
            frames = w.readframes(w.getnframes())
            seconds = w.getnframes() / float(w.getframerate())
            width = w.getsampwidth()
    except (wave.Error, EOFError) as exc:
        raise ValueError("not a readable WAV file: %s" % exc)
    if width != 2:
        raise ValueError("expected 16 bit samples")
    peak = 0
    for i in range(0, len(frames) - 1, 64):
        peak = max(peak, abs(struct.unpack("<h", frames[i:i + 2])[0]))
    with open(path, "rb") as fh:
        data = fh.read()
    comment = ""
    idx = data.find(b"ICMT")
    if idx != -1:
        length = struct.unpack("<I", data[idx + 4:idx + 8])[0]
        comment = data[idx + 8:idx + 8 + length].rstrip(b"\x00").decode("latin-1")
    return seconds, peak, comment
