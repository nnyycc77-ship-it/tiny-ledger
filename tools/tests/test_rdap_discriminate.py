"""Tests for tools/rdap_discriminate.py (issue #201). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_rdap_discriminate.py' -v

Every client answer here is SYNTHETIC: scripted (status, error) pairs that
stand in for the clients, labelled where they are built. The error text
"Remote end closed connection without response" is the text the
coordinator's live run recorded on issue #53 (comment 6358252220), used here
as the shape of a no-response answer. urlopen and subprocess.run are
replaced by functions that fail the test.
"""

import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rdap_discriminate as rd  # noqa: E402

DISCONNECT = "Remote end closed connection without response"
URL = "https://rdap.org/domain/zqxflorp.com"


def scripted(*answers):
    """A SYNTHETIC client answering the given (status, error) pairs in turn."""
    queue = list(answers)

    def client(url):
        return queue.pop(0)
    return client


def no_network(*args, **kwargs):
    raise AssertionError("rdap_discriminate tried to reach the network")


def attempts(script):
    """{client: [(status, error), ...]} -> the Attempts one pass would record."""
    rounds = len(next(iter(script.values())))
    clients = {name: scripted(*answers) for name, answers in script.items()}
    tick = iter(range(1000))
    with mock.patch("urllib.request.urlopen", no_network), mock.patch("subprocess.run", no_network):
        return rd.run_pass([URL], clients, rounds, now=lambda: "2026-10-24T08:00:00Z",
                           clock=lambda: next(tick) / 10)[URL]


class ClassifyTests(unittest.TestCase):
    def test_request_shape(self):
        a = attempts({"tool": [(None, DISCONNECT)] * 3, "urllib": [(404, None)] * 3})
        self.assertEqual(rd.classify(a), "request shape")

    def test_intermittent(self):
        a = attempts({"tool": [(404, None), (None, DISCONNECT), (404, None)], "urllib": [(404, None)] * 3})
        self.assertEqual(rd.classify(a), "intermittent")

    def test_intermittent_in_a_plain_client_counts_too(self):
        a = attempts({"tool": [(404, None)] * 2, "urllib": [(None, DISCONNECT), (404, None)]})
        self.assertEqual(rd.classify(a), "intermittent")

    def test_agree_and_all_fail_and_differ(self):
        self.assertEqual(rd.classify(attempts({"tool": [(404, None)] * 2, "urllib": [(404, None)] * 2})), "agree")
        self.assertEqual(rd.classify(attempts({"tool": [(None, DISCONNECT)] * 2,
                                               "urllib": [(None, "timed out")] * 2})), "all fail")
        self.assertEqual(rd.classify(attempts({"tool": [(200, None)] * 2, "urllib": [(404, None)] * 2})), "differ")
        # A plain client failing every time while the tool succeeds is not the tool's request shape.
        self.assertEqual(rd.classify(attempts({"tool": [(404, None)] * 2,
                                               "urllib": [(None, DISCONNECT)] * 2})), "differ")


class PassTests(unittest.TestCase):
    def test_clients_are_interleaved_round_by_round_and_timed(self):
        a = attempts({"tool": [(404, None), (404, None)], "urllib": [(404, None), (404, None)]})
        self.assertEqual([(x.client, x.round) for x in a], [("tool", 1), ("urllib", 1), ("tool", 2), ("urllib", 2)])
        self.assertTrue(all(x.elapsed_ms == 100 for x in a))
        self.assertTrue(all(x.started == "2026-10-24T08:00:00Z" for x in a))


class RenderTests(unittest.TestCase):
    def run_main(self, argv, script):
        clients = {name: scripted(*answers) for name, answers in script.items()}
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("urllib.request.urlopen", no_network), mock.patch("subprocess.run", no_network):
            code = rd.main(argv, clients=clients, stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_every_attempt_is_printed_with_the_error_exactly_as_raised(self):
        code, out, _ = self.run_main(["zqxflorp", "--rounds", "2"],
                                     {"tool": [(404, None), (None, DISCONNECT)], "urllib": [(404, None)] * 2})
        self.assertEqual(code, 0)
        self.assertIn("## %s" % URL, out)
        self.assertIn("Classification: **intermittent**", out)
        self.assertIn("| tool | 2 | ", out)
        self.assertIn("no response: %s |" % DISCONNECT, out)
        self.assertIn("| urllib | 1 | ", out)
        self.assertIn("HTTP 404 |", out)
        self.assertIn("Not run: curl, curl-tool-ua (curl is not installed here).", out)

    def test_several_names_and_tlds_each_get_a_section(self):
        # SYNTHETIC: 4 URLs x 3 default rounds = 12 answers per client.
        _, out, _ = self.run_main(["zqxflorp", "Nike", "--tlds", "com,io"],
                                  {"tool": [(404, None)] * 12, "urllib": [(404, None)] * 12})
        for host in ("zqxflorp.com", "zqxflorp.io", "nike.com", "nike.io"):
            self.assertIn("## https://rdap.org/domain/%s" % host, out)

    def test_bad_input_is_refused_before_any_request(self):
        for argv in (["!!!"], ["zqxflorp", "--rounds", "0"], ["zqxflorp", "--rounds", "11"],
                     ["zqxflorp", "--tlds", "c.om"], ["zqxflorp", "--tlds", ","]):
            code, out, _ = self.run_main(argv, {"tool": []})  # an empty script: any request fails the test
            self.assertEqual((code, out), (2, ""), argv)
        with self.assertRaises(SystemExit):  # no name at all: argparse refuses
            self.run_main(["--rounds", "2"], {"tool": []})

    def test_pipes_in_an_error_do_not_break_the_table(self):
        _, out, _ = self.run_main(["zqxflorp", "--rounds", "1"], {"tool": [(None, "a|b")], "urllib": [(404, None)]})
        self.assertIn("no response: a\\|b |", out)


class ClientTests(unittest.TestCase):
    def test_curl_client_reads_the_status_and_reports_failures_with_their_text(self):
        class Done:  # SYNTHETIC completed process
            def __init__(self, rc, out, err):
                self.returncode, self.stdout, self.stderr = rc, out, err
        seen = []

        def fake_run(cmd, **kw):
            seen.append(cmd)
            return Done(0, "404", "") if len(seen) == 1 else Done(52, "000", "curl: (52) Empty reply from server")
        with mock.patch("subprocess.run", fake_run):
            client = rd.curl_client("tiny-ledger-brand-name-checker")
            self.assertEqual(client(URL), (404, None))
            self.assertEqual(client(URL), (None, "curl exit 52: curl: (52) Empty reply from server"))
        self.assertIn("-A", seen[0])
        self.assertIn("tiny-ledger-brand-name-checker", seen[0])
        self.assertEqual(seen[0][-1], URL)

    def test_urllib_client_maps_http_errors_and_transport_failures(self):
        import urllib.error

        def http_404(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, io.BytesIO(b""))

        def disconnect(request, timeout=None):
            import http.client
            raise http.client.RemoteDisconnected(DISCONNECT)
        with mock.patch("urllib.request.urlopen", http_404):
            self.assertEqual(rd.urllib_client(URL), (404, None))
        with mock.patch("urllib.request.urlopen", disconnect):
            self.assertEqual(rd.urllib_client(URL), (None, DISCONNECT))


if __name__ == "__main__":
    unittest.main()
