#!/usr/bin/env python3
"""Domain trust check: DNS mail and web posture for one domain.

Task: issue #159 (tool factory wave 1, parent #158). Given one domain,
this tool asks two public sources and prints one Markdown section in the
delivery format from AGENT-BRIEF.md: claim lines, then every source link
with the complete raw HTTP response transcript printed verbatim beneath
it.

* DNS, through the Cloudflare DNS over HTTPS JSON API (keyless):
  the A records and MX records of the domain, its TXT records (where an
  SPF record lives), and the TXT records of _dmarc.<domain> (where a
  DMARC record lives). Four GETs to cloudflare-dns.com with the header
  accept: application/dns-json.
* The site itself: a GET of https://<domain>/ with redirects not
  followed, so the status and any Location header are read from the
  response itself; each redirect is then requested in turn, at most
  five hops, every hop its own source.

What the claim lines say, all read from the responses as shown:

* A and MX: each record's data as shown, or that the answer holds none.
* SPF: the TXT record that begins "v=spf1" (a record split into several
  quoted strings is joined, as DNS returns it), and its ending policy:
  the qualifier of the final "all" mechanism ("-all", "~all", "?all",
  "+all"; a bare "all" is shown as "all"). With no "all" but a
  "redirect=" modifier, the ending is that redirect. With neither, or
  with no SPF record, or with more than one, the section says so and
  picks nothing.
* DMARC: the TXT record at _dmarc.<domain> that begins "v=DMARC1" and
  its p= tag as shown; no record, or more than one, is said as such.
* HTTPS: the status of each hop and its Location header when the status
  is a redirect. A connection that fails is reported with the error text
  it raised, since that failure is the observation; no response exists to
  print for it.

Empty results are proven, never asserted: a name that does not exist
(the API's Status field as shown) or an answer with no record of the
asked type is printed with its complete raw response beneath it.

Fail closed: a DNS answer that is not HTTP 200, a body that is not the
API's JSON object, or a transport failure on the DNS leg prints nothing
on stdout and exits 2. No certificate check is made in this version.

Usage, with the reserved example domain as the example input:

    python3 tools/domain_trust_check.py example.com

Standard library only. No key, account, or environment value is needed.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DOH_URL = "https://cloudflare-dns.com/dns-query"
DOH_ACCEPT = "application/dns-json"
USER_AGENT = "tiny-ledger-domain-trust-check"
TIMEOUT_SECONDS = 30
MAX_HOPS = 5
MAX_BODY_BYTES = 2000000
RR_TYPES = {"A": 1, "CNAME": 5, "MX": 15, "TXT": 16}
SCOPE_LINE = ("Observation only: the records and responses below are what the public sources "
              "returned at the stated times. DNS and web configuration change; this is not a "
              "security audit or a mail delivery assessment.")
LABEL_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")


class FetchError(Exception):
    """A DNS answer that cannot be reported. Never rendered as an empty result."""


# ----------------------------------------------------------------------
# Inputs and URLs
# ----------------------------------------------------------------------

def check_domain(value):
    """The domain in lower case without a trailing dot. Refuses a URL, a
    path, a port, or a label the DNS cannot carry."""
    text = str(value or "").strip().lower().rstrip(".")
    if not text or "/" in text or ":" in text or "@" in text or " " in text:
        raise ValueError("give a bare domain, for example example.com, got %r" % value)
    try:
        text = text.encode("idna").decode("ascii")
    except UnicodeError:
        raise ValueError("the domain cannot be encoded for DNS: %r" % value)
    labels = text.split(".")
    if len(labels) < 2 or len(text) > 253 or not all(LABEL_RE.match(label) for label in labels):
        raise ValueError("not a valid domain name: %r" % value)
    return text


def doh_url(name, rr_type):
    return DOH_URL + "?" + urllib.parse.urlencode([("name", name), ("type", rr_type)])


def queries(domain):
    """The four DNS questions, in report order: (label, name, type)."""
    return [("A records", domain, "A"), ("MX records", domain, "MX"),
            ("TXT records (SPF)", domain, "TXT"), ("DMARC record", "_dmarc." + domain, "TXT")]


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
    """One HTTP exchange: URL, UTC retrieval time, status line, headers in
    the order returned, body as returned. `note` records anything this tool
    did to the body (only a size cut, and only on the site leg)."""

    def __init__(self, url, retrieved, status_line, headers, body, note=None):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers
        self.body = body
        self.note = note

    @property
    def transcript(self):
        return "\n".join([self.status_line] + self.headers + ["", self.body])

    @property
    def status(self):
        return int(self.status_line.split(" ", 2)[1])

    def header(self, name):
        for line in self.headers:
            key, sep, value = line.partition(":")
            if sep and key.strip().lower() == name.lower():
                return value.strip()
        return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _decode(raw):
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return raw.decode("latin-1"), "the body is not valid UTF-8 and is shown decoded as Latin-1"


def _exchange(url, headers, limit=None):
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        response = opener.open(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        header_lines = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        raw = response.read() if limit is None else response.read(limit + 1)
    note = None
    if limit is not None and len(raw) > limit:
        raw = raw[:limit]
        note = ("the body is longer than %d bytes and is printed up to that size only; the status "
                "line and headers are complete" % limit)
    body, decoding = _decode(raw)
    if decoding:
        note = decoding if note is None else note + "; " + decoding
    return Capture(url, retrieved, status_line, header_lines, body, note)


def fetch_doh(url):
    """GET one DNS question. Transport errors propagate."""
    return _exchange(url, {"Accept": DOH_ACCEPT, "User-Agent": USER_AGENT})


def fetch_site(url):
    """GET one site URL without following redirects. Transport errors propagate."""
    return _exchange(url, {"User-Agent": USER_AGENT}, limit=MAX_BODY_BYTES)


# ----------------------------------------------------------------------
# Reading DNS answers
# ----------------------------------------------------------------------

def parse_doh(capture):
    """(Status, answers) of a DNS answer. Refuses anything but HTTP 200
    with the API's JSON object: an integer Status, and an Answer array of
    records with name, type and data when Answer is present."""
    if capture.status != 200:
        raise FetchError("%s answered %s, not 200; no report" % (capture.url, capture.status_line))
    try:
        data = json.loads(capture.body)
    except ValueError as err:
        raise FetchError("%s body is not JSON (%s); no report" % (capture.url, err))
    if not isinstance(data, dict) or type(data.get("Status")) is not int:
        raise FetchError("%s body has no integer Status; no report" % capture.url)
    answers = data.get("Answer", [])
    if (not isinstance(answers, list)
            or any(not isinstance(a, dict) or not isinstance(a.get("type"), int)
                   or not isinstance(a.get("data"), str) or not isinstance(a.get("name"), str)
                   for a in answers)):
        raise FetchError("%s Answer is not an array of records with name, type and data; no report" % capture.url)
    return data["Status"], answers


def of_type(answers, rr_type):
    return [a for a in answers if a["type"] == RR_TYPES[rr_type]]


def txt_text(data):
    """The text of a TXT record's data as shown: every quoted string,
    unescaped and joined with nothing between them, as DNS joins a record
    split into strings. Data that is not quoted is taken as it stands."""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', data)
    if not parts:
        return data
    return "".join(re.sub(r"\\(.)", r"\1", p) for p in parts)


def spf_ending(record):
    """The ending policy of one SPF record: (kind, value)."""
    terms = record.split()[1:]
    alls = [t for t in terms if re.match(r"^[+\-~?]?all$", t, re.I)]
    if alls:
        return "all", alls[-1]
    redirects = [t for t in terms if t.lower().startswith("redirect=")]
    if redirects:
        return "redirect", redirects[-1]
    return "none", None


def dmarc_policy(record):
    for tag in record.split(";"):
        key, sep, value = tag.strip().partition("=")
        if sep and key.strip().lower() == "p":
            return value.strip()
    return None


def starts(text, prefix):
    return text.lower() == prefix.lower() or text.lower().startswith(prefix.lower() + " ") \
        or (prefix == "v=DMARC1" and text.lower().startswith("v=dmarc1;"))


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def inline(text):
    ticks = "``" if "`" in text else "`"
    pad = " " if ticks == "``" else ""
    return "%s%s%s%s%s" % (ticks, pad, text, pad, ticks)


def source_block(index, label, capture):
    lines = ["### Source. S%d. %s" % (index, label),
             "- Request URL: %s" % capture.url,
             "- Retrieved (UTC): %s" % capture.retrieved]
    if capture.note:
        lines.append("- Note: %s." % capture.note)
    lines.append("Excerpt (complete raw HTTP response transcript for the request above: status line, "
                 "headers in the order returned, a blank line, then the body as returned):")
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines.append(fence)
    lines.extend(capture.transcript.split("\n"))
    lines.append(fence)
    return lines


def _status_line(index, name, rr_type, capture, status):
    return ("QUERY: %s %s (retrieved %s; source S%d). HTTP status as returned: %s. DNS Status as shown: %d."
            % (name, rr_type, capture.retrieved, index, capture.status_line.split(" ", 1)[1], status))


def _empty(status, name, rr_type, index):
    if status != 0:
        return ("The answer holds no %s record for %s: the DNS Status field is %d, not 0 (the API documentation "
                "says Status is the DNS response code, as defined in the IANA DNS parameters registry). The "
                "complete raw response is in source S%d." % (rr_type, name, status, index))
    return ("The answer holds no %s record for %s (DNS Status 0 with no %s record in the Answer). The "
            "complete raw response is in source S%d." % (rr_type, name, rr_type, index))


def dns_section(label, name, rr_type, index, capture):
    status, answers = parse_doh(capture)
    lines = ["### %s" % label, "", _status_line(index, name, rr_type, capture, status), ""]
    chain = of_type(answers, "CNAME")
    for a in chain:
        lines.append("- CNAME as shown: %s is an alias for %s (TTL %s)." % (inline(a["name"]), inline(a["data"]), a.get("TTL")))
    found = of_type(answers, rr_type)
    if rr_type == "TXT":
        return lines, status, found
    if not found:
        lines.append(_empty(status, name, rr_type, index))
    for a in found:
        lines.append("- %s record as shown: %s (TTL %s)." % (rr_type, inline(a["data"]), a.get("TTL")))
    return lines, status, found


def spf_lines(name, status, found, index):
    lines = []
    records = [(a, txt_text(a["data"])) for a in found]
    spf = [(a, t) for a, t in records if starts(t, "v=spf1")]
    if not records:
        lines.append(_empty(status, name, "TXT", index))
    lines.append("- TXT records in the answer: %d, of which %d begin v=spf1." % (len(records), len(spf)))
    if not spf:
        lines.append("- SPF: no TXT record for %s begins v=spf1 in this answer, so no SPF record and no "
                     "ending policy are shown (source S%d)." % (name, index))
        return lines
    for a, text in spf:
        lines.append("- SPF record as shown (data %s): %s" % (inline(a["data"]), inline(text)))
    if len(spf) > 1:
        lines.append("- SPF: %d records begin v=spf1. The tool does not pick one; no single ending policy is "
                     "claimed (source S%d)." % (len(spf), index))
        return lines
    kind, value = spf_ending(spf[0][1])
    if kind == "all":
        lines.append("- SPF ending policy: %s, the final all mechanism of the record (source S%d)." % (inline(value), index))
    elif kind == "redirect":
        lines.append("- SPF ending policy: the record has no all mechanism and ends with the modifier %s, "
                     "so its policy is the redirected record's, which this tool does not fetch (source S%d)."
                     % (inline(value), index))
    else:
        lines.append("- SPF ending policy: none shown; the record has neither an all mechanism nor a "
                     "redirect modifier (source S%d)." % index)
    return lines


def dmarc_lines(name, status, found, index):
    lines = []
    records = [(a, txt_text(a["data"])) for a in found]
    dmarc = [(a, t) for a, t in records if starts(t, "v=DMARC1")]
    if not records:
        lines.append(_empty(status, name, "TXT", index))
    lines.append("- TXT records in the answer: %d, of which %d begin v=DMARC1." % (len(records), len(dmarc)))
    if not dmarc:
        lines.append("- DMARC: no TXT record for %s begins v=DMARC1 in this answer, so no DMARC policy is "
                     "shown (source S%d)." % (name, index))
        return lines
    for a, text in dmarc:
        lines.append("- DMARC record as shown (data %s): %s" % (inline(a["data"]), inline(text)))
    if len(dmarc) > 1:
        lines.append("- DMARC: %d records begin v=DMARC1. The tool does not pick one; no policy is claimed "
                     "(source S%d)." % (len(dmarc), index))
        return lines
    policy = dmarc_policy(dmarc[0][1])
    if policy is None:
        lines.append("- DMARC policy: the record has no p= tag as shown (source S%d)." % index)
    else:
        lines.append("- DMARC policy (p= tag as shown): %s (source S%d)." % (inline(policy), index))
    return lines


def https_lines(hops, first_index):
    """hops: list of (url, Capture or error text)."""
    lines = []
    for n, (url, result) in enumerate(hops):
        index = first_index + n
        if isinstance(result, str):
            lines.append("- Hop %d: GET %s did not return an HTTP response; the connection attempt raised: %s. "
                         "No response exists to print for it." % (n + 1, url, result))
            continue
        status = result.status_line.split(" ", 1)[1]
        location = result.header("Location")
        text = "- Hop %d: GET %s answered %s (retrieved %s; source S%d)" % (n + 1, url, status, result.retrieved, index)
        if 300 <= result.status < 400:
            text += ", Location header as shown: %s" % (inline(location) if location else "none")
        lines.append(text + ".")
    last_url, last = hops[-1]
    if isinstance(last, str):
        lines.append("- HTTPS: %s gave no HTTP response, so the site's HTTPS answer is not determinable from "
                     "this run." % last_url)
    elif 300 <= last.status < 400 and len(hops) >= MAX_HOPS and last.header("Location"):
        lines.append("- HTTPS: still redirecting after %d hops; this tool stops there." % MAX_HOPS)
    else:
        lines.append("- HTTPS: the final hop answered %s at %s." % (last.status_line.split(" ", 1)[1], last_url))
    return lines


def walk_site(domain, fetch=None):
    """[(url, Capture or error text)] for https://<domain>/ and its redirects."""
    fetch = fetch or fetch_site
    url, hops = "https://%s/" % domain, []
    while len(hops) < MAX_HOPS:
        try:
            capture = fetch(url)
        except (urllib.error.URLError, OSError, ValueError) as err:
            hops.append((url, str(getattr(err, "reason", err))))
            break
        hops.append((url, capture))
        location = capture.header("Location")
        if not (300 <= capture.status < 400 and location):
            break
        url = urllib.parse.urljoin(url, location)
    return hops


def render(domain, dns_captures, hops):
    """dns_captures: [Capture] in the order of queries(domain)."""
    lines = ["## Domain: %s" % domain, "", SCOPE_LINE, ""]
    lines.append("Method: four DNS questions to the Cloudflare DNS over HTTPS JSON API (%s, header "
                 "accept: %s): A, MX and TXT for %s, and TXT for _dmarc.%s. Then a GET of https://%s/ "
                 "with redirects not followed, each redirect requested in turn, at most %d hops. Every "
                 "value below is copied from a response as shown, and every response is printed in full "
                 "in the Sources section under its request URL." % (DOH_URL, DOH_ACCEPT, domain, domain, domain, MAX_HOPS))
    lines.append("")
    for i, ((label, name, rr_type), capture) in enumerate(zip(queries(domain), dns_captures)):
        index = i + 1
        section, status, found = dns_section(label, name, rr_type, index, capture)
        lines += section
        if label.startswith("TXT"):
            lines += spf_lines(name, status, found, index)
        elif label.startswith("DMARC"):
            lines += dmarc_lines(name, status, found, index)
        lines.append("")
    lines += ["### HTTPS", ""] + https_lines(hops, len(dns_captures) + 1) + [""]
    lines += ["## Sources", ""]
    for i, ((label, name, rr_type), capture) in enumerate(zip(queries(domain), dns_captures)):
        lines += source_block(i + 1, "Cloudflare DNS over HTTPS, %s %s" % (name, rr_type), capture) + [""]
    for n, (url, result) in enumerate(hops):
        if not isinstance(result, str):
            lines += source_block(len(dns_captures) + 1 + n, "Site, hop %d, GET %s" % (n + 1, url), result) + [""]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def run(domain, fetch_dns=None, fetch_web=None):
    """The report lines for one domain. Raises ValueError for a bad
    domain, FetchError for a DNS answer that cannot be reported, and lets
    a DNS transport error propagate."""
    domain = check_domain(domain)
    fetch_dns = fetch_dns or fetch_doh
    captures = [fetch_dns(doh_url(name, rr_type)) for _, name, rr_type in queries(domain)]
    for capture in captures:
        parse_doh(capture)  # fail closed before anything is rendered
    return render(domain, captures, walk_site(domain, fetch_web))


def main(argv=None):
    parser = argparse.ArgumentParser(description="DNS mail and web posture for one domain, in the delivery format.")
    parser.add_argument("domain", help="a bare domain, e.g. example.com")
    args = parser.parse_args(argv)
    try:
        lines = run(args.domain)
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    except FetchError as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
