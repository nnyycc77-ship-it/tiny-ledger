"""Regression tests using unmodified public responses captured with provenance.

Fault-injection cases deliberately corrupt captured responses; they are not data
examples or evidence. Integration tests opt in with USASPENDING_LIVE=1.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta
from email.message import Message
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import usaspending_awards as u


FIXTURES = Path(__file__).parent / "fixtures" / "usaspending"


def captured(name="recipient"):
    meta = json.loads((FIXTURES / f"{name}.meta.json").read_bytes())
    return u.Capture(meta["request_body"], meta["retrieved_utc"],
                     (FIXTURES / f"{name}.json").read_bytes().decode("utf-8"))


class QueryTests(unittest.TestCase):
    def test_queries_reproduce_captured_requests(self):
        for name, argv in [
            ("recipient", ["--recipient", "Boeing", "--limit", "2"]),
            ("empty", ["--recipient", "Instant Pot Smart WiFi", "--limit", "2"]),
            ("naics", ["--recipient", "Boeing", "--naics", "336411", "--limit", "2"]),
        ]:
            with self.subTest(name=name):
                self.assertEqual(u.build_query(u.parser().parse_args(argv)), captured(name).query)

    def test_page_and_date_filters(self):
        dates = [record["Start Date"] for record in json.loads(captured().raw)["results"]]
        args = u.parser().parse_args([
            "--naics", "336411", "--start", min(dates), "--end", max(dates), "--page", "2",
        ])
        query = json.loads(u.build_query(args))
        self.assertEqual(query["page"], 2)
        self.assertEqual(query["filters"]["time_period"], [{"start_date": min(dates), "end_date": max(dates)}])
        self.assertFalse(query["subawards"])

    def test_invalid_inputs_before_fetch(self):
        for extra in [[], ["--recipient", " "], ["--naics", "x"],
                      ["--naics", "336411", "--page", "0"],
                      ["--naics", "336411", "--limit", "101"],
                      ["--naics", "336411", "--limit", "0"],
                      ["--recipient", "Boeing", "--start", "2011-02-24"],
                      ["--recipient", "Boeing", "--start", "2011-02-30", "--end", "2011-03-01"],
                      ["--recipient", "Boeing", "--start", "2011-03-01", "--end", "2011-02-24"],
                      ["--recipient", "Boeing", "--start", "20110224", "--end", "20110301"]]:
            with self.subTest(extra=extra), patch.object(u, "fetch") as fetch:
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    self.assertEqual(u.main(extra), 2)
                self.assertEqual(out.getvalue(), "")
                fetch.assert_not_called()

    def test_exclusions_require_reason_and_unique_id(self):
        identifier = json.loads(captured().raw)["results"][0]["generated_internal_id"]
        for values in [[identifier], [identifier + "= "], ["=reason"],
                       [identifier + "=reason", identifier + "=reason"]]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                u.exclusions(values)
        self.assertEqual(u.exclusions([identifier + "=a=b"]), {identifier: "a=b"})


class ReportTests(unittest.TestCase):
    def test_full_raw_response_immediately_under_link(self):
        for name in ["recipient", "empty", "naics"]:
            capture = captured(name)
            report = u.render(capture, {})
            self.assertIn(f"Source: <{u.ENDPOINT}>\n" + u.fenced(capture.raw), report)
            self.assertEqual(report.count("Source: <"), 1)
            self.assertIn(u.fenced(capture.query), report)
            self.assertIn(capture.retrieved, report)

    def test_empty_keeps_entire_response_and_limits_claim(self):
        capture = captured("empty")
        self.assertEqual(json.loads(capture.raw)["results"], [])
        report = u.render(capture, {})
        self.assertIn("returned 0 record(s)", report)
        self.assertIn("does not establish that the recipient has no awards", report)
        self.assertIn(capture.raw, report)

    def test_source_fields_and_record_order(self):
        capture = captured()
        report = u.render(capture, {})
        records = json.loads(capture.raw, parse_float=u.Decimal)["results"]
        for record in records:
            for field in u.FIELDS:
                self.assertIn(f"- {field} as shown: {u.display(record.get(field))}", report)
        self.assertLess(report.index(u.display(records[0]["generated_internal_id"])),
                        report.index(u.display(records[1]["generated_internal_id"])))

    def test_near_match_exclusion_preserves_record_and_reason(self):
        capture = captured()
        record = json.loads(capture.raw)["results"][1]
        reason = "Outside this brief's Department of Defense scope; source Awarding Agency is " + record["Awarding Agency"] + "."
        report = u.render(capture, {record["generated_internal_id"]: reason})
        self.assertIn("### Checked and excluded near match", report)
        self.assertIn("Reviewer-supplied exclusion reason: " + u.display(reason), report)
        self.assertIn(u.display(record["Award ID"]), report)
        self.assertIn(capture.raw, report)

    def test_unknown_exclusion_rejected(self):
        with self.assertRaisesRegex(ValueError, "not returned"):
            u.render(captured("empty"), {json.loads(captured().raw)["results"][0]["generated_internal_id"]: "reason"})

    def test_pagination_is_not_exhaustive_claim(self):
        self.assertIn("More pages are reported", u.render(captured(), {}))
        capture = captured("empty")
        data = json.loads(capture.raw)
        data["page_metadata"]["page"] = 2
        query = json.loads(capture.query)
        query["page"] = 2
        report = u.render(replace(capture, raw=json.dumps(data), query=json.dumps(query)), {})
        self.assertIn("requested page 2", report)
        self.assertIn("one requested page", report)
        self.assertNotIn("More pages are reported", report)

    def test_corrupt_schema_rejected(self):
        capture = captured()
        data = json.loads(capture.raw)
        cases = [[], {}, {**data, "results": None}, {**data, "results": [None]},
                 {**data, "page_metadata": {}},
                 {**data, "page_metadata": {"page": 1, "hasNext": "false"}},
                 {**data, "page_metadata": {"page": 2, "hasNext": False}},
                 {**data, "results": [data["results"][0]] * 2}]
        missing_id = deepcopy(data)
        missing_id["results"][0].pop("generated_internal_id")
        cases.append(missing_id)
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                u.render(replace(capture, raw=json.dumps(value)), {})
        with self.assertRaises(ValueError):
            u.render(replace(capture, raw="<html>upstream failure</html>"), {})

    def test_missing_field_never_filled_in(self):
        capture = captured()
        data = json.loads(capture.raw)
        data["results"][0].pop("Award Amount")
        report = u.render(replace(capture, raw=json.dumps(data)), {})
        self.assertIn("Award Amount as shown: not supplied by source", report)

    def test_fence_and_summary_injection(self):
        raw = "before\n```\n# after\n````"
        self.assertEqual(u.fenced(raw), "`````\n" + raw + "\n`````")
        self.assertNotIn("\n", u.display("\n# injected <html>"))
        self.assertIn(r"\<html\>", u.display("<html>"))


class FetchTests(unittest.TestCase):
    def test_post_bytes_and_response_preserved(self):
        capture = captured()
        response = io.BytesIO(capture.raw.encode("utf-8"))
        response.status = 200
        response.headers = Message()
        response.headers["Content-Type"] = "application/json"
        with patch.object(u, "urlopen", return_value=response) as open_url:
            result = u.fetch(capture.query)
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, u.ENDPOINT)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.data, capture.query.encode("utf-8"))
        self.assertEqual(open_url.call_args.kwargs["timeout"], 30)
        self.assertEqual(result.raw, capture.raw)
        self.assertEqual(datetime.fromisoformat(result.retrieved).utcoffset(), timedelta(0))

    def test_http_network_and_invalid_response_fail_without_stdout(self):
        failures = [HTTPError(u.ENDPOINT, 429, "rate limited", {}, None),
                    URLError("unavailable"), TimeoutError("timed out"),
                    ValueError("invalid response")]
        for failure in failures:
            with self.subTest(failure=failure), patch.object(u, "fetch", side_effect=failure):
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    self.assertEqual(u.main(["--recipient", "Boeing"]), 2)
                self.assertEqual(out.getvalue(), "")
                self.assertIn("no report emitted", err.getvalue())

    def test_non_json_content_type_rejected(self):
        response = io.BytesIO(captured().raw.encode())
        response.status = 200
        response.headers = Message()
        response.headers["Content-Type"] = "text/html"
        with patch.object(u, "urlopen", return_value=response), self.assertRaises(ValueError):
            u.fetch(captured().query)

    def test_cli_matches_rendered_capture(self):
        capture = captured()
        out = io.StringIO()
        with patch.object(u, "fetch", return_value=capture), redirect_stdout(out):
            self.assertEqual(u.main(["--recipient", "Boeing", "--limit", "2"]), 0)
        self.assertEqual(out.getvalue(), u.render(capture, {}))


@unittest.skipUnless(os.environ.get("USASPENDING_LIVE") == "1", "opt-in live public API check")
class LiveTests(unittest.TestCase):
    def test_live_queries_return_valid_evidence(self):
        # These checks contact the source; captured fixtures are never replayed here.
        for name in ["recipient", "empty", "naics"]:
            with self.subTest(name=name):
                capture = u.fetch(captured(name).query)
                report = u.render(capture, {})
                self.assertIn(capture.raw, report)
                self.assertIn(capture.retrieved, report)
                self.assertIn("Source: <" + u.ENDPOINT + ">\n", report)


if __name__ == "__main__":
    unittest.main()
