"""Tests for tools/faa_lookup.py (issue #181). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_faa_lookup.py' -v

Fixtures: fixtures/faa-registry/ holds verbatim excerpts the coordinator
captured from the live FAA releasable aircraft download under Option B on
issue #181 (this container cannot reach registry.faa.gov): the archive
response headers, its member list, the MASTER.txt and ACFTREF.txt header
lines, the complete raw rows for N-NUMBER 100ZT and its ACFTREF code
2076628, and the 302 answer for a wrong URL. Each file's SHA-256 is in
fixtures/faa-registry/provenance.json and is checked here, with the posted
SHA-256 of the 302 body.

The real archive is about 73 MB and is not stored. The tests ASSEMBLE a
small ZIP in a temporary folder from those exact excerpt lines, with the
byte order mark the coordinator states precedes each header restored, and
nothing else in it. That assembled archive is a test arrangement: its
sizes and hashes are its own, not the real archive's, which the docs page
quotes from the capture.

The download tests run against a local HTTP server on 127.0.0.1 and
nothing else.
"""

import contextlib
import hashlib
import http.server
import io
import json
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import faa_lookup as fa  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "faa-registry"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
BOM = b"\xef\xbb\xbf"
CRLF = b"\r\n"  # test arrangement: the line end used in the assembled archive


def fixture(name):
    return (FIXTURES / name).read_bytes()


def line(name):
    return fixture(name).rstrip(b"\n")


def assemble(folder, master_rows=("master-row-100ZT.csv",), members=(fa.MASTER, fa.ACFTREF)):
    """Write a small archive from the verbatim excerpt lines (a test arrangement)."""
    path = Path(folder) / "ReleasableAircraft.zip"
    with zipfile.ZipFile(path, "w") as zf:
        if fa.MASTER in members:
            zf.writestr(fa.MASTER, BOM + line("master-header.csv") + CRLF
                        + b"".join(line(r) + CRLF for r in master_rows))
        if fa.ACFTREF in members:
            zf.writestr(fa.ACFTREF, BOM + line("acftref-header.csv") + CRLF + line("acftref-row-2076628.csv") + CRLF)
    return path


def captured_meta(path):
    """The record download() would keep, with the captured Last-Modified and
    the assembled archive's own size and hash."""
    headers = fixture("archive-200-headers.http").decode().rstrip("\n").split("\n")
    lm = [h.split(": ", 1)[1] for h in headers if h.startswith("Last-Modified: ")][0]
    return {"url": fa.ARCHIVE_URL, "retrieved_utc": "2026-10-24T06:51:07Z", "status": headers[0],
            "headers": headers[1:], "last_modified": lm, "bytes": path.stat().st_size,
            "sha256": fa.file_sha256(path)}


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.iterdir() if p.name != "provenance.json"))
        for name, entry in PROVENANCE.items():
            self.assertEqual(hashlib.sha256(fixture(name)).hexdigest(), entry["sha256"], name)
        body = fixture("bad-url-302.http").decode().rstrip("\n").split("\n\n", 1)[1].encode()
        self.assertEqual(hashlib.sha256(body).hexdigest(), PROVENANCE["bad-url-302.http"]["body_sha256"])

    def test_rows_have_one_field_per_header_name(self):
        import csv
        for header, row in (("master-header.csv", "master-row-100ZT.csv"), ("acftref-header.csv", "acftref-row-2076628.csv")):
            names = next(csv.reader([line(header).decode()]))
            self.assertEqual(len(next(csv.reader([line(row).decode()]))), len(names), row)


class Query(unittest.TestCase):
    def test_n_numbers(self):
        self.assertEqual(fa.check_n_number("n100zt"), ("N100ZT", "100ZT"))
        self.assertEqual(fa.check_n_number(" N 100ZT "), ("N100ZT", "100ZT"))
        self.assertEqual(fa.check_n_number("100ZT"), ("N100ZT", "100ZT"))
        for bad in ("", "N", "N1234567", "N10-0Z", "N100Z!"):
            with self.assertRaises(ValueError, msg=bad):
                fa.check_n_number(bad)


class Lookup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def report(self, n, **kw):
        archive = assemble(self.folder, **kw)
        meta = captured_meta(archive)
        fetch = lambda url, dest: (_ for _ in ()).throw(AssertionError("no download expected"))  # noqa: E731
        (self.folder / "ReleasableAircraft.json").write_text(json.dumps(dict(meta, retrieved_utc="2026-10-24T06:51:07Z")))
        archive2, meta2 = fa.ensure_archive(self.folder, fetch=fetch, today="2026-10-24")
        display, value = fa.check_n_number(n)
        return "\n".join(fa.render(display, value, meta2, fa.lookup(archive2, value))), archive2

    def test_hit_names_the_four_values_and_prints_both_rows(self):
        text, _ = self.report("N100ZT")
        self.assertIn("- Make (ACFTREF MFR): TEXTRON AVIATION INC", text)
        self.assertIn("- Model (ACFTREF MODEL): 525C", text)
        self.assertIn("- Year (MASTER YEAR MFR): 2022", text)
        self.assertIn("- Registrant name (MASTER NAME): BANK OF UTAH TRUSTEE", text)
        self.assertIn("```\n%s\n```" % line("master-row-100ZT.csv").decode(), text)
        self.assertIn("```\n%s\n```" % line("acftref-row-2076628.csv").decode(), text)

    def test_every_reply_states_the_archive_last_modified(self):
        text, _ = self.report("N100ZT")
        self.assertIn("archive Last-Modified Sat, 24 Oct 2026 04:58:32 GMT, retrieved 2026-10-24T06:51:07Z (UTC) "
                      "from the cache", text)

    def test_no_match_is_proven_by_the_file_as_read(self):
        text, archive = self.report("N00000")
        with zipfile.ZipFile(archive) as zf:
            data = zf.read(fa.MASTER)
        self.assertIn("REGISTRATION: no MASTER.txt row carries N-NUMBER 00000.", text)
        self.assertIn("MASTER.txt as read: %d bytes, %d lines including the header, SHA-256 %s."
                      % (len(data), data.count(b"\n"), hashlib.sha256(data).hexdigest()), text)
        self.assertNotIn("Make (", text)

    def test_missing_member_or_column_is_a_failure(self):
        archive = assemble(self.folder, members=(fa.MASTER,))
        with self.assertRaisesRegex(fa.SourceFailed, "the archive has no ACFTREF.txt"):
            fa.lookup(archive, "100ZT")
        bad = self.folder / "bad.zip"
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr(fa.MASTER, BOM + b"N-NUMBER,SERIAL NUMBER" + CRLF)  # test body, not a recording
        with self.assertRaisesRegex(fa.SourceFailed, "no column"):
            fa.lookup(bad, "100ZT")

    def test_a_non_zip_is_a_failure(self):
        notzip = self.folder / "ReleasableAircraft.zip"
        notzip.write_bytes(fixture("bad-url-302.http"))
        with self.assertRaisesRegex(fa.SourceFailed, "not a readable ZIP"):
            fa.lookup(notzip, "100ZT")


class Cache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.calls = []
        self.source = assemble(tempfile.mkdtemp(dir=self.tmp.name))

    def fetch(self, url, dest):
        self.calls.append(url)
        dest.write_bytes(self.source.read_bytes())
        return captured_meta(dest)

    def test_downloads_once_per_day_and_again_when_stale_or_altered(self):
        fa.ensure_archive(self.folder, fetch=self.fetch, today="2026-10-24")
        fa.ensure_archive(self.folder, fetch=self.fetch, today="2026-10-24")
        self.assertEqual(len(self.calls), 1)
        fa.ensure_archive(self.folder, fetch=self.fetch, today="2026-10-25")
        self.assertEqual(len(self.calls), 2)
        archive = self.folder / "ReleasableAircraft.zip"
        archive.write_bytes(archive.read_bytes() + b"x")
        _, meta = fa.ensure_archive(self.folder, fetch=self.fetch, today="2026-10-24")
        self.assertEqual(len(self.calls), 3)
        self.assertFalse(meta["from_cache"])

    def test_refresh_always_downloads(self):
        fa.ensure_archive(self.folder, fetch=self.fetch, today="2026-10-24")
        fa.ensure_archive(self.folder, refresh=True, fetch=self.fetch, today="2026-10-24")
        self.assertEqual(len(self.calls), 2)

    def test_cache_folder_follows_the_environment(self):
        with patch.dict("os.environ", {fa.CACHE_ENV: str(self.folder)}):
            self.assertEqual(fa.cache_dir(), self.folder / "faa")


class Download(unittest.TestCase):
    """download() against a local server: a 200 streamed, a 302 not followed, a 403."""

    def serve(self, status, body, headers):
        class Handler(http.server.BaseHTTPRequestHandler):
            seen = []

            def do_GET(self):
                Handler.seen.append((self.path, self.headers.get("User-Agent")))
                self.send_response(status)
                for k, v in headers:
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass
        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return "http://127.0.0.1:%d/database/ReleasableAircraft.zip" % server.server_port, Handler.seen

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / "ReleasableAircraft.zip"

    def test_200_is_streamed_hashed_and_recorded(self):
        archive = assemble(Path(self.tmp.name))
        body = archive.read_bytes()
        url, seen = self.serve(200, body, [("Last-Modified", "Sat, 24 Oct 2026 04:58:32 GMT")])
        archive.unlink()
        meta = fa.download(url, self.dest)
        self.assertEqual(self.dest.read_bytes(), body)
        self.assertEqual((meta["bytes"], meta["sha256"]), (len(body), hashlib.sha256(body).hexdigest()))
        self.assertEqual(meta["last_modified"], "Sat, 24 Oct 2026 04:58:32 GMT")
        self.assertEqual(seen[0][1], fa.USER_AGENT)

    def test_302_is_not_followed_and_is_a_failure(self):
        text = fixture("bad-url-302.http").decode().rstrip("\n")
        head, body = text.split("\n\n", 1)
        location = [h.split(": ", 1)[1] for h in head.split("\n") if h.startswith("Location: ")][0]
        url, seen = self.serve(302, body.encode(), [("Location", location)])
        with self.assertRaisesRegex(fa.SourceFailed, "answered HTTP/1.[01] 302"):
            fa.download(url, self.dest)
        self.assertEqual(len(seen), 1)
        self.assertFalse(self.dest.exists())

    def test_403_is_a_failure(self):
        url, _ = self.serve(403, b"Access Denied (test body)", [])  # test body, not the Akamai page
        with self.assertRaisesRegex(fa.SourceFailed, "403"):
            fa.download(url, self.dest)
        self.assertFalse(self.dest.exists())


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "faa_lookup.md"

    def test_page_states_the_price_and_the_real_archive_values(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)
        self.assertIn(PROVENANCE["archive-200-headers.http"]["archive_sha256"], page)
        self.assertIn(PROVENANCE["master-header.csv"]["master_txt"]["sha256"], page)
        self.assertIn("```text\n%s\n```" % line("master-row-100ZT.csv").decode(), page)


class CommandLine(unittest.TestCase):
    def test_bad_input_and_source_failure(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as ctx:
                fa.main(["N10-0Z"])
        self.assertEqual(ctx.exception.code, 2)

        def failing(*a, **k):
            raise fa.SourceFailed("test failure")
        out, err = io.StringIO(), io.StringIO()
        with patch.object(fa, "run", failing), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(fa.main(["N100ZT"]), 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("source failure, nothing printed: test failure", err.getvalue())


if __name__ == "__main__":
    unittest.main()
