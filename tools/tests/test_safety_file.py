"""Tests for tools/safety_file.py (issue #176). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_safety_file.py' -v

Fixtures: fixtures/nhtsa-safety/*.http are real, keyless responses from the
live NHTSA APIs, captured by the coordinator under Option B on issue #176
(this container cannot reach api.nhtsa.gov), all for the 2021 Hyundai
Elantra except the unknown-model and bad-year cases. Each is the posted
headers block (Set-Cookie omitted by the coordinator), a blank line, then
the posted body. Each one's URL, comment, body size and body SHA-256 (as
posted) and the whole file's SHA-256 are in fixtures/nhtsa-safety/
provenance.json; both hashes are checked here.

A fake fetch serves each fixture for the exact URL it was captured from and
fails the test on any other URL. Where a test pairs captures from different
queries (the empty ratings case with the Elantra recalls and complaints),
it says so where it happens.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import safety_file as sf  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "nhtsa-safety"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RETRIEVED = "2026-10-24T03:51:27Z"  # test value; the captures' own times are in provenance.json

VARIANTS = "ratings-2021-hyundai-elantra.http"
VEHICLE = "ratings-vehicle-15697.http"
RECALLS = "recalls-2021-hyundai-elantra.http"
COMPLAINTS = "complaints-2021-hyundai-elantra.http"
RATINGS_EMPTY = "ratings-2021-hyundai-nosuchmodel-empty.http"
RECALLS_400 = "recalls-2021-hyundai-nosuchmodel-400.http"
COMPLAINTS_400 = "complaints-2021-hyundai-nosuchmodel-400.http"
COMPLAINTS_500 = "complaints-hyundai-elantra-abc-500.http"


def capture(name):
    transcript = (FIXTURES / name).read_text(encoding="utf-8")
    return RETRIEVED, transcript, transcript.partition("\n\n")[2]


def served(mapping):
    """A fetch that serves {url: fixture} and fails on anything else."""
    def fetch(url):
        if url not in mapping:
            raise AssertionError("unexpected fetch: %s" % url)
        return capture(mapping[url])
    return fetch


def by_url(*names):
    return {PROVENANCE[n]["url"]: n for n in names}


ELANTRA = by_url(VARIANTS, VEHICLE, RECALLS, COMPLAINTS)


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.glob("*.http")))
        for name, entry in PROVENANCE.items():
            raw = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], name)
            body = raw.split(b"\n\n", 1)[1]
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry["body_sha256"], name)
            self.assertEqual(len(body), entry["body_bytes"], name)

    def test_the_tool_builds_each_captured_url(self):
        urls = {e["url"] for e in PROVENANCE.values()}
        for url in (sf.ratings_url("Hyundai", "Elantra", "2021"), sf.vehicle_url(15697),
                    sf.recalls_url("Hyundai", "Elantra", "2021"), sf.complaints_url("Hyundai", "Elantra", "2021"),
                    sf.ratings_url("Hyundai", "Nosuchmodel", "2021"), sf.recalls_url("Hyundai", "Nosuchmodel", "2021"),
                    sf.complaints_url("Hyundai", "Nosuchmodel", "2021"), sf.complaints_url("Hyundai", "Elantra", "abc")):
            self.assertIn(url, urls)


class Query(unittest.TestCase):
    def test_inputs(self):
        self.assertEqual(sf.check_query(" Hyundai ", "Elantra", "2021"), ("Hyundai", "Elantra", "2021"))
        for bad in (("", "Elantra", "2021"), ("Hyundai", "", "2021"), ("Hyundai", "Elantra", "21"),
                    ("Hyundai", "Elantra", "abc"), ("Hyundai", "Elan/tra", "2021"), ("Hyundai?", "Elantra", "2021")):
            with self.assertRaises(ValueError, msg=bad):
                sf.check_query(*bad)

    def test_spaces_are_percent_encoded(self):
        self.assertEqual(sf.ratings_url("Land Rover", "Range Rover", "2021"),
                         "https://api.nhtsa.gov/SafetyRatings/modelyear/2021/make/Land%20Rover/model/Range%20Rover")
        self.assertIn("make=Land%20Rover&model=Range%20Rover&modelYear=2021",
                      sf.recalls_url("Land Rover", "Range Rover", "2021"))


class Hit(unittest.TestCase):
    def setUp(self):
        with patch.object(sf, "fetch", served(ELANTRA)):
            self.text = "\n".join(sf.run("Hyundai", "Elantra", "2021"))

    def test_one_source_block_per_query(self):
        for url in ELANTRA:
            self.assertEqual(self.text.count("- Query URL: %s\n" % url), 1, url)

    def test_ratings_as_shown(self):
        self.assertIn("RATINGS: the variants query lists 1 rated variant (Count as shown: 1).", self.text)
        self.assertIn("- 2021 Hyundai Elantra 4 DR FWD (VehicleId 15697)", self.text)
        for line in ("- OverallRating as shown: 5", "- OverallFrontCrashRating as shown: 4",
                     "- RolloverRating as shown: 5", "- RolloverPossibility as shown: 0.101",
                     "- NHTSAForwardCollisionWarning as shown: No"):
            self.assertIn(line, self.text)

    def test_recalls_as_shown(self):
        self.assertIn('RECALLS: 6 campaigns in the results array (the response\'s own "Count" field shows 6).',
                      self.text)
        self.assertIn("- 24V879000, ReportReceivedDate as shown 21/11/2024, Component as shown: BACK OVER "
                      "PREVENTION: SENSING SYSTEM: CAMERA", self.text)

    def test_complaints_counts_trace_to_the_records(self):
        records = json.loads(capture(COMPLAINTS)[2])["results"]
        self.assertIn('COMPLAINTS: %d complaint records in the results array (the response\'s own "count" '
                      'field shows 132).' % len(records), self.text)
        self.assertIn("- with crash = true: %d" % sum(1 for r in records if r["crash"] is True), self.text)
        self.assertIn("- with fire = true: %d" % sum(1 for r in records if r["fire"] is True), self.text)
        first = records[0]
        self.assertIn("- %s, %s, %s" % (first["odiNumber"], first["dateComplaintFiled"], first["components"]),
                      self.text)

    def test_cross_check_shows_both_counts(self):
        self.assertIn("- RecallsCount as shown in the ratings record for VehicleId 15697: 6; records in the "
                      "recalls response: 6.", self.text)
        records = json.loads(capture(COMPLAINTS)[2])["results"]
        self.assertIn("- ComplaintsCount as shown in the ratings record for VehicleId 15697: 132; records in the "
                      "complaints response: %d." % len(records), self.text)

    def test_every_transcript_sits_beneath_its_source_link(self):
        for url, name in ELANTRA.items():
            self.assertIn("- Query URL: %s\n- Retrieved (UTC): %s\nExcerpt (complete raw HTTP response transcript"
                          % (url, RETRIEVED), self.text)
            self.assertIn("```\n%s\n```" % capture(name)[1], self.text)


class Empty(unittest.TestCase):
    def test_empty_ratings_are_proven_by_the_transcript(self):
        # Test arrangement: the unknown-model ratings capture (HTTP 200, Count 0)
        # served beside the Elantra recalls and complaints captures, because the
        # unknown-model recalls and complaints queries answered HTTP 400.
        mapping = dict(by_url(RATINGS_EMPTY))
        mapping[sf.recalls_url("Hyundai", "Nosuchmodel", "2021")] = RECALLS
        mapping[sf.complaints_url("Hyundai", "Nosuchmodel", "2021")] = COMPLAINTS
        with patch.object(sf, "fetch", served(mapping)):
            text = "\n".join(sf.run("Hyundai", "Nosuchmodel", "2021"))
        self.assertIn("RATINGS: none found. The variants query returned an empty Results array (Count as shown: "
                      "0)", text)
        self.assertIn("```\n%s\n```" % capture(RATINGS_EMPTY)[1], text)
        self.assertNotIn("Cross check", text)


class SourceFailure(unittest.TestCase):
    def test_400_with_a_success_message_is_a_failure_not_empty(self):
        with patch.object(sf, "fetch", served(by_url(RATINGS_EMPTY, RECALLS_400, COMPLAINTS_400))):
            with self.assertRaises(sf.SourceFailed) as ctx:
                sf.run("Hyundai", "Nosuchmodel", "2021")
        failed = [(f["section"], f["status"]) for f in ctx.exception.failures]
        self.assertEqual(failed, [("Recalls", "HTTP/1.1 400 Bad Request"), ("Complaints", "HTTP/1.1 400 Bad Request")])
        message = str(ctx.exception)
        self.assertIn(PROVENANCE[RECALLS_400]["url"], message)
        self.assertIn('{"Count":0,"Message":"Results returned successfully","results":[]}', message)

    def test_500_is_a_failure(self):
        # gather() is called directly with the captured bad year, which
        # check_query() would refuse before any fetch.
        mapping = {sf.ratings_url("Hyundai", "Elantra", "abc"): RATINGS_EMPTY,
                   sf.recalls_url("Hyundai", "Elantra", "abc"): RECALLS,
                   sf.complaints_url("Hyundai", "Elantra", "abc"): COMPLAINTS_500}
        with patch.object(sf, "fetch", served(mapping)):
            with self.assertRaises(sf.SourceFailed) as ctx:
                sf.gather("Hyundai", "Elantra", "abc")
        self.assertEqual([(f["section"], f["status"]) for f in ctx.exception.failures],
                         [("Complaints", "HTTP/1.1 500 Internal Server Error")])
        self.assertIn('{"message":"Internal server error","error":500}', str(ctx.exception))

    def test_200_without_the_results_array_is_a_failure(self):
        body = '{"message":"something else"}'  # test body, not a recording
        fake = lambda url: (RETRIEVED, "HTTP/1.1 200 OK\n\n" + body, body)  # noqa: E731
        with patch.object(sf, "fetch", fake):
            with self.assertRaises(sf.SourceFailed) as ctx:
                sf.gather("Hyundai", "Elantra", "2021")
        self.assertTrue(all('(no "' in f["status"] for f in ctx.exception.failures))


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "safety_file.md"

    def test_page_quotes_the_tool_and_the_recorded_response(self):
        page = self.PAGE.read_text(encoding="utf-8")
        with patch.object(sf, "fetch", served(ELANTRA)):
            text = "\n".join(sf.run("Hyundai", "Elantra", "2021"))
        claims = page.split("## What a report shows", 1)[1].split("Source: ", 1)[0]
        quoted = [q for line in claims.splitlines() if line.startswith("- `") for q in line[2:].split("`")[1::2]]
        self.assertGreaterEqual(len(quoted), 4)
        for q in quoted:
            self.assertIn(q, text)
        self.assertIn("Source: %s," % PROVENANCE[VEHICLE]["url"], page)
        self.assertIn("```text\n%s\n```" % capture(VEHICLE)[1], page)

    def test_page_states_the_price_and_cites_no_nhtsa_documentation(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)
        self.assertNotIn("nhtsa.gov/nhtsa-datasets-and-apis", page)


class CommandLine(unittest.TestCase):
    def run_main(self, argv, fetch):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sf, "fetch", fetch), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = sf.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_hit(self):
        code, out, _ = self.run_main(["--make", "Hyundai", "--model", "Elantra", "--year", "2021"], served(ELANTRA))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("## Safety file: 2021 Hyundai Elantra\n"))

    def test_source_failure_prints_no_report(self):
        code, out, err = self.run_main(["--make", "Hyundai", "--model", "Nosuchmodel", "--year", "2021"],
                                       served(by_url(RATINGS_EMPTY, RECALLS_400, COMPLAINTS_400)))
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("source failure, nothing printed", err)
        self.assertIn("Recalls: %s answered HTTP/1.1 400 Bad Request" % PROVENANCE[RECALLS_400]["url"], err)

    def test_bad_input_fetches_nothing(self):
        def never(url):
            raise AssertionError("no fetch expected")
        code, out, _ = self.run_main(["--make", "Hyundai", "--model", "Elantra", "--year", "21"], never)
        self.assertEqual((code, out), (2, ""))

    def test_transport_failure_prints_no_report(self):
        def broken(url):
            raise urllib.error.URLError("connection refused (test)")
        code, out, err = self.run_main(["--make", "Hyundai", "--model", "Elantra", "--year", "2021"], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("fetch failed, nothing printed", err)


if __name__ == "__main__":
    unittest.main()
