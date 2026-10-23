"""Tests for agents/catering-finder/catering_finder.py. Standard library only, no network.

This module is named test_finder.py, not test_catering_finder.py, because the
CI loader shim in tools/tests carries that name and unittest refuses to import
a second module under a name already loaded from another folder.

Run from the repository root:

    python3 -m unittest discover -s agents/catering-finder/tests -v

The CI job discovers these through tools/tests/test_catering_finder.py.

Which data is which: EVERY FIXTURE under tests/fixtures is SYNTHETIC. The
five vendor pages, the candidate index, the brief and the outreach log were
written by hand for these tests (issue #75) because no vendor host is
reachable from the build container; each page carries that label in its
first line and provenance.json repeats it. No business, price, message or
reply in them is real. The synthetic replies and log entries built inside
this file are labelled where they appear. Nothing here sends anything.
"""

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import catering_finder as cf  # noqa: E402

FIXTURES = HERE / "fixtures"
BRIEF = FIXTURES / "brief.json"
LOG = FIXTURES / "outreach-log.json"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RUN_UTC = "2026-10-23T14:00:00Z"


def run(argv, env=None):
    out, err = io.StringIO(), io.StringIO()
    code = cf.main(argv, env=env or {}, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def store():
    return cf.load_store(FIXTURES)


def page(vendor_id):
    return next(p for p in store()["pages"] if p.vendor_id == vendor_id)


class ProvenanceTests(unittest.TestCase):
    def test_every_fixture_hash_matches_and_is_labelled_synthetic(self):
        self.assertIn("SYNTHETIC", PROVENANCE["_about"])
        for rel, record in PROVENANCE.items():
            if rel.startswith("_"):
                continue
            data = (FIXTURES / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"], rel)
            self.assertEqual(record["label"], "SYNTHETIC", rel)
            if rel.startswith("vendors/"):
                self.assertIn("SYNTHETIC FIXTURE", data.decode("utf-8").splitlines()[0], rel)

    def test_store_refuses_an_edited_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "store"
            shutil.copytree(FIXTURES, copy)
            target = copy / "vendors" / "pecan-grove.html"
            target.write_bytes(target.read_bytes().replace(b"$22", b"$12"))
            with self.assertRaisesRegex(cf.FetchError, "does not match its recorded sha256"):
                cf.load_store(copy)

    def test_store_refuses_a_missing_page_or_bad_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "store"
            shutil.copytree(FIXTURES, copy)
            (copy / "vendors" / "bluebonnet.html").unlink()
            with self.assertRaisesRegex(cf.FetchError, "missing"):
                cf.load_store(copy)
            (copy / "index.json").write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(cf.FetchError, "could not be read as JSON"):
                cf.load_store(copy)


class BriefTests(unittest.TestCase):
    def test_fixture_brief_loads_and_is_normalised(self):
        brief = cf.load_brief(BRIEF)
        self.assertEqual(brief["headcount"], 60)
        self.assertEqual(brief["dietary_needs"], ["vegan", "gluten-free", "nut allergy"])
        self.assertEqual(brief["service_style"], "buffet")
        self.assertEqual(brief["budget_per_head"], 40)
        self.assertIsNone(brief["time"])
        self.assertIsNone(brief["response_deadline_utc"])
        timed = cf.validate_brief(dict(brief, time="12:30", response_deadline_utc="2026-11-10T17:00:00Z"))
        self.assertEqual((timed["time"], timed["response_deadline_utc"]), ("12:30", "2026-11-10T17:00:00Z"))

    def test_invalid_briefs_are_refused(self):
        good = cf.load_brief(BRIEF)
        bad = [
            {k: v for k, v in good.items() if k != "location"},
            dict(good, date="14/11/2026"),
            dict(good, date="2026-02-30"),
            dict(good, headcount=0),
            dict(good, headcount=True),
            dict(good, budget_usd=-5),
            dict(good, dietary_needs="vegan"),
            dict(good, dietary_needs=["vegan", ""]),
            dict(good, service_style="  "),
            dict(good, time="noon"),
            dict(good, response_deadline_utc="next week"),
            ["not", "an", "object"],
        ]
        for data in bad:
            with self.subTest(data=data):
                with self.assertRaises(cf.ConfigError):
                    cf.validate_brief(data)

    def test_needs_and_styles_map_to_the_tables_or_keep_their_wording(self):
        self.assertEqual(cf.canonical_need("Nut allergy"), "nut-free")
        self.assertEqual(cf.canonical_need("gluten free"), "gluten-free")
        self.assertEqual(cf.canonical_need("low sodium"), "low sodium")
        self.assertEqual(cf.need_terms("low sodium"), ("low sodium",))
        self.assertEqual(cf.canonical_style("Family-Style"), "family style")
        self.assertEqual(cf.canonical_style("private dining"), "private dining room")
        self.assertEqual(cf.canonical_style("drop-off catering"), "drop-off")
        self.assertEqual(cf.canonical_style("afternoon tea"), "afternoon tea")
        self.assertEqual(cf.location_tokens("Austin, TX"), ["Austin", "TX"])


class ExtractionTests(unittest.TestCase):
    def test_style_area_capacity_prices_contact_on_the_full_page(self):
        p = page("pecan-grove")
        style = cf.extract_style(p, "buffet")
        self.assertEqual(style.line_no, 10)
        self.assertEqual(style.excerpt, p.lines[9])
        self.assertIsNotNone(cf.extract_area(p, "Austin, TX"))
        self.assertEqual(cf.extract_capacity(p).value, 200)
        prices = cf.extract_prices(p)
        self.assertEqual([(c.value, c.style, c.starting) for c in prices], [(22.0, "buffet", True), (38.0, "plated", False)])
        self.assertEqual([c.value for c in cf.prices_for_style(prices, "buffet")], [22.0])
        self.assertEqual(cf.extract_contact(p).value, "events@pecan-grove-catering.invalid")
        self.assertEqual(len(cf.extract_menu(p)), 5)

    def test_a_denied_mention_is_not_a_style_match(self):
        self.assertTrue(cf.negated("food truck service only. no buffet or table service.", "buffet"))
        self.assertFalse(cf.negated("buffet service with staff", "buffet"))
        self.assertIsNone(cf.extract_style(page("hill-country-taco"), "buffet"))

    def test_silence_yields_none_never_a_value(self):
        verde = page("verde-kitchen")
        self.assertIsNone(cf.extract_capacity(verde))
        self.assertEqual(cf.extract_prices(verde), [])
        self.assertIsNone(cf.extract_dietary(page("bluebonnet"), "vegan"))
        self.assertIsNone(cf.extract_area(page("lone-star-smoke"), "Austin, TX"))

    def test_terms_lines_get_one_label_each(self):
        terms = cf.extract_terms(page("cedar-park"))
        self.assertEqual([(c.field, c.line_no) for c in terms],
                         [("minimum spend or order", 15), ("deposit terms", 16), ("cancellation terms", 17)])
        self.assertEqual(cf.extract_terms(page("verde-kitchen")), [])

    def test_prices_without_a_style_clause_are_kept_only_when_no_clause_names_one(self):
        untagged = cf.prices_for_style(cf.extract_prices(page("hill-country-taco")), "buffet")
        self.assertEqual([c.value for c in untagged], [14.0])
        mixed = cf.extract_prices(page("bluebonnet"))
        self.assertEqual([c.value for c in cf.prices_for_style(mixed, "family style")], [])


class DietaryStateTests(unittest.TestCase):
    def setUp(self):
        self.log = cf.load_log(LOG)
        self.pecan = page("pecan-grove")
        self.blue = page("bluebonnet")

    def test_confirmed_comes_from_the_page_with_the_line_quoted(self):
        state, claim = cf.dietary_state(self.pecan, "vegan", self.log["drafts"]["pecan-grove"], RUN_UTC)
        self.assertEqual(state, "confirmed")
        self.assertIn("vegan", claim.excerpt)

    def test_stated_comes_from_the_recorded_reply_only_when_it_addresses_the_need(self):
        state, reply = cf.dietary_state(self.pecan, "nut allergy", self.log["drafts"]["pecan-grove"], RUN_UTC)
        self.assertEqual(state, "stated")
        self.assertIn("nut-free", reply["text"])
        # SYNTHETIC entry built here: a reply that talks about something else.
        entry = {"drafted_utc": "2026-10-21T13:00:00Z", "sent_utc": "2026-10-21T13:06:00Z",
                 "reply": {"received_utc": "2026-10-22T09:00:00Z", "text": "We are available that day. Buffet is $35."}}
        state, detail = cf.dietary_state(self.blue, "vegan", entry, RUN_UTC)
        self.assertEqual(state, "not confirmed")
        self.assertIn("does not address it", detail)

    def test_unconfirmed_states_name_the_question_status(self):
        self.assertEqual(cf.dietary_state(self.blue, "vegan", None, RUN_UTC), ("not confirmed", "question not yet drafted"))
        state, detail = cf.dietary_state(self.blue, "vegan", self.log["drafts"]["bluebonnet"], RUN_UTC)
        self.assertEqual(state, "not confirmed")
        self.assertEqual(detail, "question asked 2026-10-21T13:06:00Z, no reply as of " + RUN_UTC)
        state, detail = cf.dietary_state(page("verde-kitchen"), "nut allergy", self.log["drafts"]["verde-kitchen"], RUN_UTC)
        self.assertEqual((state, detail), ("not confirmed", "question drafted 2026-10-21T13:00:00Z, not sent"))

    def test_silence_is_never_coverage(self):
        for need in ("vegan", "gluten-free", "nut allergy", "halal"):
            state, _ = cf.dietary_state(self.blue, need, self.log["drafts"]["bluebonnet"], RUN_UTC)
            self.assertEqual(state, "not confirmed", need)

    def test_availability_comes_from_the_answer_only(self):
        self.assertEqual(cf.availability_state(None), "not confirmed")
        self.assertEqual(cf.availability_state(self.log["drafts"]["bluebonnet"]), "not confirmed")
        self.assertEqual(cf.availability_state(self.log["drafts"]["pecan-grove"]), "confirmed")
        self.assertEqual(cf.availability_state(self.log["drafts"]["cedar-park"]), "declined")
        self.assertEqual(cf.reply_availability("We can do that date."), "confirmed")
        self.assertEqual(cf.reply_availability("Unfortunately we cannot take new bookings that week."), "declined")
        self.assertEqual(cf.reply_availability("Please send the menu you have in mind."), "not confirmed")
        self.assertEqual(cf.reply_prices(self.log["drafts"]["pecan-grove"]), [(22.0, "Buffet is $22 per person as on our site")])


class OutreachTests(unittest.TestCase):
    def test_drafts_cover_compared_vendors_only_and_ask_the_unconfirmed_needs_verbatim(self):
        brief, st = cf.load_brief(BRIEF), store()
        log = {"hire_id": None, "drafts": {}}
        drafted = cf.draft_all(brief, st, log)
        self.assertEqual(drafted, ["pecan-grove", "bluebonnet", "verde-kitchen", "cedar-park"])
        message = log["drafts"]["pecan-grove"]["message"]
        self.assertIn("nut allergy?", message)
        self.assertNotIn("vegan", message.split("5.")[1])
        self.assertIn("vegan; gluten-free; nut allergy?", log["drafts"]["bluebonnet"]["message"])
        self.assertIn("2026-11-14", log["drafts"]["bluebonnet"]["message"])
        self.assertIsNone(log["drafts"]["pecan-grove"]["sent_utc"])
        self.assertEqual(cf.draft_all(brief, st, log), [])  # idempotent, nothing overwritten

    def test_drafts_follow_the_job_rules(self):
        brief, st = cf.load_brief(BRIEF), store()
        log = {"hire_id": None, "drafts": {}}
        cf.draft_all(brief, st, log)
        for entry in log["drafts"].values():
            m = entry["message"]
            self.assertIn("on behalf of a customer", m)
            self.assertIn("automated assistant", m)
            self.assertIn("we will stop", m)
            self.assertIn("minimum spend, a deposit, or cancellation terms", m)
            self.assertIn("the customer decides on any booking", m)
            self.assertNotRegex(m, r"@(?!pecan|verde|cedar|bluebonnet|hill|lone)")  # no buyer address: only the vendor's own channel
        timed = cf.validate_brief(dict(json.loads(BRIEF.read_text()), time="12:00"))
        self.assertIn("2026-11-14 at 12:00", cf.draft_message(timed, page("verde-kitchen"), ["nut allergy"], None))

    def test_a_vendor_who_asked_us_to_stop_gets_no_further_draft(self):
        brief, st = cf.load_brief(BRIEF), store()
        log = {"hire_id": None, "drafts": {}}
        cf.draft_all(brief, st, log)
        cf.record_sent(log, "verde-kitchen", "2026-10-21T15:00:00Z")
        cf.record_reply(log, "verde-kitchen", "2026-10-22T09:00:00Z", "Please do not email us again.", stop=True)
        self.assertEqual(log["stopped"], ["verde-kitchen"])
        del log["drafts"]["verde-kitchen"]
        self.assertEqual(cf.draft_all(brief, st, log), [])
        with self.assertRaises(cf.ConfigError):
            cf.record_reply(log, "pecan-grove", "2026-10-22T09:00:00Z", "ok", available="maybe")

    def test_record_sent_and_reply_are_ordered_and_validated(self):
        log = {"hire_id": None, "drafts": {"v": {"drafted_utc": "2026-10-21T13:00:00Z", "sent_utc": None, "reply": None}}}
        with self.assertRaises(cf.ConfigError):
            cf.record_reply(log, "v", "2026-10-22T09:00:00Z", "yes")
        with self.assertRaises(cf.ConfigError):
            cf.record_sent(log, "v", "yesterday")
        with self.assertRaises(cf.ConfigError):
            cf.record_sent(log, "missing", "2026-10-21T15:00:00Z")
        cf.record_sent(log, "v", "2026-10-21T15:00:00Z")
        with self.assertRaises(cf.ConfigError):
            cf.record_reply(log, "v", "2026-10-22T09:00:00Z", "   ")
        cf.record_reply(log, "v", "2026-10-22T09:00:00Z", "We can do it.")
        self.assertEqual(log["drafts"]["v"]["reply"]["text"], "We can do it.")
        self.assertEqual(log["drafts"]["v"]["reply"]["availability"], "confirmed")
        cf.record_reply(log, "v", "2026-10-22T09:30:00Z", "Yes, received. We will check and get back to you.", available="no")
        self.assertEqual(log["drafts"]["v"]["reply"]["availability"], "declined")

    def test_a_log_entry_for_a_vendor_outside_the_run_is_refused(self):
        log = cf.load_log(LOG)
        log["drafts"]["someone-else"] = {}
        with self.assertRaisesRegex(cf.ConfigError, "not in this store: someone-else"):
            cf.check_log_against_store(log, store())


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.result = cf.compare(cf.load_brief(BRIEF), store(), cf.load_log(LOG), run_utc=RUN_UTC)
        self.text = cf.render(self.result)

    def test_shape_and_classification(self):
        self.assertEqual([r["page"].vendor_id for r in self.result["compared"]],
                         ["pecan-grove", "bluebonnet", "verde-kitchen", "cedar-park"])
        self.assertEqual([(p.vendor_id, reason.split(":")[0]) for p, reason in self.result["excluded"]],
                         [("hill-country-taco", "service style"), ("lone-star-smoke", "area")])
        for heading in ("## Summary", "## Availability for 2026-11-14", "## Vendors compared", "## Contacted with no reply",
                        "## Declined", "## Checked and excluded", "## Outreach drafts", "## Sources"):
            self.assertIn(heading, self.text)
        self.assertIn("| Pecan Grove Catering | yes | yes | 200 (fits) | 22 (stated in the vendor's answer) | within budget per head (22 stated vs 40) | confirmed |", self.text)
        self.assertIn("| Cedar Park Kitchen Catering | yes | yes | 120 (fits) | 28 (starting point) (page) |", self.text)
        self.assertIn("Counts: 4 vendor(s) compared; 3 state a capacity of at least 60 on their page; 3 contacted; 2 replied; "
                      "1 confirmed availability for 2026-11-14; 1 declined; 0 asked us to stop.", self.text)
        self.assertIn("- Confirmed by the vendor's answer: Pecan Grove Catering", self.text)
        self.assertIn("- Declined or not available: Cedar Park Kitchen Catering", self.text)
        self.assertIn("- Bluebonnet Table: contacted 2026-10-21T13:06:00Z", self.text)
        self.assertIn("- Cedar Park Kitchen Catering: answer received 2026-10-22T10:15:00Z", self.text)
        self.assertIn("not verified, not inferred", self.text)
        self.assertIn("40 USD per head (the brief's budget divided by its headcount)", self.text)
        self.assertNotIn("Estimate", self.text)
        self.assertIn("Price per person (USD) (starting point as stated)", self.text)
        self.assertIn("Cancellation terms as shown", self.text)

    def test_over_budget_is_marked_from_the_stated_price(self):
        brief = dict(cf.load_brief(BRIEF), budget_usd=1200, budget_per_head=20.0)
        text = cf.render(cf.compare(brief, store(), cf.load_log(LOG), run_utc=RUN_UTC))
        self.assertIn("over budget: 22 stated vs 20 per head in the brief", text)

    def test_all_three_dietary_states_are_exercised(self):
        self.assertIn("CONFIRMED by the vendor's page", self.text)
        self.assertIn("STATED by the vendor's answer received 2026-10-21T16:40:00Z", self.text)
        self.assertIn("NOT CONFIRMED (question asked 2026-10-21T13:06:00Z, no reply as of " + RUN_UTC + ")", self.text)
        self.assertIn("NOT CONFIRMED (question drafted 2026-10-21T13:00:00Z, not sent)", self.text)
        self.assertNotIn("UNCONFIRMED", self.text)

    def test_every_claim_carries_its_source_and_a_verbatim_excerpt(self):
        lines = self.text.splitlines()
        pages = {p.url: p for p in store()["pages"]}
        checked = 0
        for i, line in enumerate(lines):
            if line.startswith("- ") and " as shown: " in line:
                self.assertTrue(lines[i + 1].startswith("  Source: <"), lines[i + 1])
                url = lines[i + 1].split("<")[1].split(">")[0]
                self.assertEqual(lines[i + 2].strip(), "```")
                excerpt = lines[i + 3][2:]
                self.assertIn(excerpt, pages[url].lines, excerpt)
                self.assertEqual(lines[i + 4].strip(), "```")
                checked += 1
        self.assertGreaterEqual(checked, 15)

    def test_empty_comparison_is_rendered_not_hidden(self):
        brief = dict(cf.load_brief(BRIEF), service_style="afternoon tea")
        text = cf.render(cf.compare(brief, store(), {"hire_id": None, "drafts": {}}, run_utc=RUN_UTC))
        self.assertIn("no vendor passed the style and area check", text)
        self.assertEqual(text.count("service style: no line on the page names"), 6)


class CliTests(unittest.TestCase):
    def test_run_prints_the_report_and_fails_closed(self):
        code, out, err = run(["run", "--brief", str(BRIEF), "--store", str(FIXTURES), "--log", str(LOG)])
        self.assertEqual(code, 0, err)
        self.assertIn("# Catering comparison: Austin, TX, 2026-11-14, 60 guests", out)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "brief.json"
            bad.write_text('{"date": "soon"}', encoding="utf-8")
            code, out, err = run(["run", "--brief", str(bad), "--store", str(FIXTURES)])
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertIn("No report emitted", err)

    def test_draft_writes_a_log_and_send_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "log.json"
            code, out, _ = run(["draft", "--brief", str(BRIEF), "--store", str(FIXTURES), "--log", str(log)])
            self.assertEqual(code, 0)
            self.assertIn("nothing sent", out)
            self.assertEqual(sorted(json.loads(log.read_text())["drafts"]), ["bluebonnet", "cedar-park", "pecan-grove", "verde-kitchen"])
            for argv in (["send", "pecan-grove", "--log", str(log)],
                         ["send", "pecan-grove", "--log", str(log), "--execute"],
                         ["send", "pecan-grove", "--log", str(log), "--hire-id", "h1"],
                         ["send", "pecan-grove", "--log", str(log), "--hire-id", "h1", "--execute"]):
                code, out, err = run(argv)
                self.assertEqual(code, 2, argv)
                self.assertIn("send:", err)
            code, out, _ = run(["record-sent", "pecan-grove", "--log", str(log), "--when", "2026-10-21T15:00:00Z"])
            self.assertEqual(code, 0)
            code, out, _ = run(["record-reply", "pecan-grove", "--log", str(log), "--when", "2026-10-22T09:00:00Z",
                                "--text", "Nut-free menu is fine.", "--available", "yes"])
            self.assertEqual(code, 0)
            saved = json.loads(log.read_text())["drafts"]["pecan-grove"]["reply"]
            self.assertEqual((saved["text"], saved["availability"]), ("Nut-free menu is fine.", "confirmed"))
            code, out, _ = run(["record-sent", "bluebonnet", "--log", str(log), "--when", "2026-10-21T15:00:00Z"])
            code, out, _ = run(["record-reply", "bluebonnet", "--log", str(log), "--when", "2026-10-22T09:00:00Z",
                                "--text", "Please stop contacting us.", "--stop"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(log.read_text())["stopped"], ["bluebonnet"])

    def test_capture_stores_a_live_page_with_provenance_and_refuses_non_200(self):
        # The SYNTHETIC transport is wired in by _main_with_fake below: it answers
        # from memory and sends nothing.
        body = b"<!-- SYNTHETIC page body from the fake fetcher -->\n<p>Buffet in Austin</p>\n"
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(["capture", "https://vendor.invalid/ok", "--store", tmp, "--id", "v1", "--name", "Vendor One"])
            self.assertEqual(code, 0)
            prov = json.loads((Path(tmp) / "provenance.json").read_text())
            self.assertEqual(prov["vendors/v1.html"]["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual(json.loads((Path(tmp) / "index.json").read_text())["vendors"][0]["url"], "https://vendor.invalid/ok")
            self.assertEqual(cf.load_store(tmp)["pages"][0].name, "Vendor One")
            code, out, err = run(["capture", "https://vendor.invalid/gone", "--store", tmp, "--id", "v2", "--name", "Two"])
            self.assertEqual(code, 2)
            self.assertIn("HTTP 404", err)
            self.assertFalse((Path(tmp) / "vendors" / "v2.html").exists())


# main() takes the fetcher explicitly so the capture test can avoid the network.
_orig_main = cf.main


def _main_with_fake(argv, env=None, stdout=None, stderr=None, fetcher=None):
    if argv and argv[0] == "capture" and fetcher is None:
        body = b"<!-- SYNTHETIC page body from the fake fetcher -->\n<p>Buffet in Austin</p>\n"

        def fake(url):
            return ("HTTP 200 OK", [("Content-Type", "text/html")], body) if url.endswith("/ok") else ("HTTP 404 Not Found", [], b"")
        fetcher = fake
    return _orig_main(argv, env=env, stdout=stdout, stderr=stderr, fetcher=fetcher)


cf.main = _main_with_fake


if __name__ == "__main__":
    unittest.main()
