#!/usr/bin/env python3
"""Email check (issue #338, tool factory wave 3, tool 8).

Given an email address, checks the address's shape locally and reads the
domain's mail records through Cloudflare DNS over HTTPS, keyless, and
prints one Markdown report in the delivery format from AGENT-BRIEF.md:
whether the address is well formed, whether the domain has MX records,
and its SPF and DMARC policies, each as returned, with the complete raw
response of every query beneath its source link.

    python3 tools/email_check.py someone@gmail.com

Source: GET https://cloudflare-dns.com/dns-query with the header
Accept: application/dns-json, one query per record: MX on the domain,
TXT on the domain (the SPF record is the TXT record beginning v=spf1),
and TXT on _dmarc.{domain} (the DMARC record begins v=DMARC1). The wave
3 source check (issue #305 research) confirmed this source keyless for
exactly this use, repeating the wave 1 domain trust finding.

Readings, stated in every report:
- DNS Status 3 is NXDOMAIN: the name does not exist. Status 0 with no
  Answer section is NODATA: the name exists and publishes no record of
  that type. The two are different answers and are never merged.
- A single MX answer of "0 ." is a null MX (RFC 7505): the domain
  formally declares it accepts no email at all. It is one MX record,
  and its reading is the opposite of "has mail servers".
- A TXT record can arrive split into several quoted chunks; the chunks
  are joined with nothing between them before the v=spf1 or v=DMARC1
  selection, as DNS joins them.
- Well formed is a statement about the address's shape only (one @, a
  local part of allowed characters, and a domain of valid labels). It
  says nothing about whether a mailbox exists; this tool never connects
  to a mail server.

Outcomes: any query that fails, times out, answers a non 200 status, or
answers a body that is not the documented DNS JSON shape stops the run
with exit 2 and no report. A timeout in particular is unknown, never a
negative: the source check measured this endpoint taking far longer
than a short client timeout in this environment, so the timeout here is
60 seconds per query. DNS answers that arrive, including NXDOMAIN and
NODATA, are reports, proven by the raw responses.

Standard library only.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

DOH_URL = "https://cloudflare-dns.com/dns-query"
HOST = "cloudflare-dns.com"
DOH_ACCEPT = "application/dns-json"
USER_AGENT = "tiny-ledger-email-check"
TIMEOUT_SECONDS = 60
RR_MX, RR_TXT = 15, 16
LABEL_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")
LOCAL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}$")
OBSERVATION = ("Observation only: this report records what Cloudflare's DNS over HTTPS resolver returned "
               "for this domain's records at the retrieval times stated below, without any key. DNS "
               "records change; this is not a delivery test, and no mail server was contacted.")
READINGS = ("Readings: DNS Status 3 (NXDOMAIN) means the name does not exist; Status 0 with no Answer "
            "section (NODATA) means the name exists and publishes no record of that type. A single MX "
            "answer of \"0 .\" is a null MX (RFC 7505): the domain declares it accepts no email at all.")


class FetchError(ValueError):
    """A failed, refused or unreadable answer. Never a report."""


class Capture:
    def __init__(self, url, final_url, retrieved, status, status_line, headers, body):
        self.url = url
        self.final_url = final_url
        self.retrieved = retrieved
        self.status = status
        self.status_line = status_line
        self.headers = headers  # [(name, value)] in the order returned
        self.body = body

    def transcript(self):
        return "\n".join([self.status_line] + ["%s: %s" % kv for kv in self.headers] + ["", self.body])


def check_address(value):
    """(local, domain) for a well formed address; ValueError naming the defect otherwise."""
    text = (value or "").strip()
    if text.count("@") != 1:
        raise ValueError("an email address has exactly one @ (got %r)" % value)
    local, domain = text.split("@")
    if not LOCAL_RE.match(local) or local.startswith(".") or local.endswith(".") or ".." in local:
        raise ValueError("the local part %r is not well formed: 1 to 64 allowed characters, no leading, "
                         "trailing or doubled dot" % local)
    domain = domain.lower().rstrip(".")
    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        raise ValueError("the domain cannot be encoded for DNS: %r" % value)
    labels = domain.split(".")
    if len(labels) < 2 or len(domain) > 253 or not all(LABEL_RE.match(label) for label in labels):
        raise ValueError("the domain %r is not well formed: at least two valid DNS labels" % domain)
    return local, domain


def doh_url(name, rr_type):
    return DOH_URL + "?" + urllib.parse.urlencode([("name", name), ("type", rr_type)])


def queries(domain):
    """The three DNS questions, in report order: (label, name, type)."""
    return [("MX records", domain, "MX"), ("TXT records (SPF)", domain, "TXT"),
            ("DMARC record", "_dmarc." + domain, "TXT")]


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url):
    """One keyless DoH GET. Returns a Capture for 200; raises FetchError otherwise."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": DOH_ACCEPT})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise FetchError("request to %s failed or timed out: %s; no report, and this is unknown, "
                         "not a negative" % (url, err))
    with response:
        status = response.status if hasattr(response, "status") else response.code
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, status, response.reason)
        headers = list(response.headers.items())
        final_url = response.geturl() or url
        try:
            body = response.read().decode("utf-8")
        except (UnicodeDecodeError, OSError) as err:
            raise FetchError("%s answered a body that could not be read: %s; no report" % (url, err))
    if urllib.parse.urlsplit(final_url).netloc != HOST:
        raise FetchError("%s was redirected off %s; no report" % (url, HOST))
    capture = Capture(url, final_url, retrieved, status, status_line, headers, body)
    if status != 200:
        raise FetchError("%s answered %s; no report" % (url, status_line))
    return capture


def parse_doh(capture):
    """(dns_status, answers) from a 200 body; answers are the Answer entries of the asked type."""
    try:
        doc = json.loads(capture.body)
        status = doc["Status"]
        if not isinstance(status, int):
            raise ValueError("Status is not a number")
        answers = doc.get("Answer") or []
        if not isinstance(answers, list):
            raise ValueError("Answer is not a list")
        for entry in answers:
            if not isinstance(entry.get("data"), str) or not isinstance(entry.get("type"), int):
                raise ValueError("an Answer entry is not the documented shape")
    except (ValueError, KeyError, TypeError, AttributeError) as err:
        raise FetchError("%s answered a body that is not the documented DNS JSON shape (%s); no report"
                         % (capture.url, err))
    return status, answers


def txt_text(data):
    """A TXT record's text: the quoted chunks, unescaped and joined with nothing between them."""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', data)
    if not parts:
        return data
    return "".join(re.sub(r"\\(.)", r"\1", part) for part in parts)


def mx_lines(domain, status, answers):
    if status == 3:
        return ["- MX: the domain %s does not exist (the resolver answered NXDOMAIN), so it has no "
                "mail servers." % domain]
    if status != 0:
        raise FetchError("the MX query answered DNS Status %d, which this tool does not read; no report"
                         % status)
    mx = [a["data"] for a in answers if a["type"] == RR_MX]
    if not mx:
        return ["- MX: the domain exists and publishes no MX record (NODATA), so it names no mail "
                "server to receive its mail."]
    if mx == ["0 ."]:
        return ["- MX: one record as shown, \"0 .\": a null MX (RFC 7505). The domain formally "
                "declares it accepts no email at all."]
    lines = ["- MX: %d record(s) as shown:" % len(mx)]
    for data in mx:
        lines.append("  - %s" % data)
    return lines


def txt_lines(kind, status, answers, prefix, absent_nodata, absent_among):
    if status == 3:
        return ["- %s: the name does not exist (NXDOMAIN), so no %s record is published."
                % (kind, kind)]
    if status != 0:
        raise FetchError("the %s query answered DNS Status %d, which this tool does not read; no report"
                         % (kind, status))
    texts = [txt_text(a["data"]) for a in answers if a["type"] == RR_TXT]
    if not texts:
        return ["- %s: %s" % (kind, absent_nodata)]
    found = [t for t in texts if t.startswith(prefix)]
    if not found:
        return ["- %s: %s (%d TXT record(s) as returned, none begins %s)."
                % (kind, absent_among, len(texts), prefix)]
    lines = ["- %s record as shown:" % kind]
    for t in found:
        lines.append("  - %s" % t)
    return lines


def render(address, domain, captures):
    parsed = [parse_doh(c) for c in captures]
    lines = ["# Email check: %s" % address, "", OBSERVATION, "",
             "Well formed: yes. The address has one @, a well formed local part, and the domain %s is "
             "made of valid DNS labels. This is a statement about shape only; no mailbox was tested."
             % domain, "", READINGS, ""]
    lines += mx_lines(domain, *parsed[0])
    lines += txt_lines("SPF", *parsed[1], prefix="v=spf1",
                       absent_nodata="the domain publishes no TXT records at all (NODATA), so no SPF record",
                       absent_among="no SPF record among the domain's TXT records")
    lines += txt_lines("DMARC", *parsed[2], prefix="v=DMARC1",
                       absent_nodata="no TXT record at _dmarc.%s (NODATA), so no DMARC policy is published" % domain,
                       absent_among="no DMARC record at _dmarc.%s" % domain)
    for (label, _name, _type), capture in zip(queries(domain), captures):
        lines += ["", "## Source: %s" % label, "",
                  "Exact query: GET %s" % capture.url,
                  "Retrieved (UTC): %s" % capture.retrieved,
                  "Source: <%s>" % capture.url,
                  "\n".join(["```", capture.transcript(), "```"])]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="Keyless email check: address shape, MX records, SPF and "
                                            "DMARC policies over DNS over HTTPS.")
    p.add_argument("address", help="an email address, e.g. someone@gmail.com")
    args = p.parse_args(argv)
    try:
        _local, domain = check_address(args.address)
        fetch_one = fetcher or fetch
        captures = [fetch_one(doh_url(name, rr)) for _label, name, rr in queries(domain)]
        lines = render(args.address.strip(), domain, captures)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
