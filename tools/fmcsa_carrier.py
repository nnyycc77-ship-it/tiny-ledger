#!/usr/bin/env python3
"""FMCSA carrier data fetcher.

Queries three public FMCSA sources live for one motor carrier and prints
one Markdown section in the delivery format from AGENT-BRIEF.md: for
each source, the claim lines, then the source link, then the complete
raw HTTP response transcript printed verbatim directly beneath it.

Sources, in the order printed:

1. FMCSA Company Census File on the DOT open data portal (dataset
   az4n-8mr2, JSON), by USDOT number, with the same $select field list
   the published carrier vetting delivery used. Also used for the
   carrier name search (--name).
2. FMCSA SAFER Company Snapshot (HTML), by USDOT number.
3. FMCSA Licensing and Insurance carrier search (HTML), by USDOT
   number. The published delivery records that this site presents a
   verification challenge to automated reads and was read in a live
   browser session; this tool prints whatever the site returns and
   says so when no record fields are found in it.

No key is needed for any of these sources and none is read. Standard
library only. The only network calls are the GETs to the three hosts
above.

Usage examples:

    python3 tools/fmcsa_carrier.py --usdot 2046
    python3 tools/fmcsa_carrier.py --subject "GARDA CL CENTRAL INC" --usdot 2046
    python3 tools/fmcsa_carrier.py --usdot 2046 --source census --source safer
    python3 tools/fmcsa_carrier.py --name "CHENEY BROTHERS" \
        --exclude 123456="different state; not the subject carrier"

Claim lines never go beyond the response. For the Census record every
selected field is printed as shown, or marked not present in the
record. For the SAFER page the claim lines are the text lines that
follow each labelled field in the page text (the way the published
delivery quotes them); a label not found is said to be not found, and
the inspection, out of service and crash tables are left to the raw
excerpt rather than parsed. A transport failure (no connection, blocked
host, timeout) prints nothing on stdout and exits 2: a failed fetch is
never shown as an empty result. An HTTP error status is not a failed
fetch: its complete transcript is printed and the claim lines say the
fields are not determinable from that response.

The tool never judges which name search candidate is the subject
carrier. --exclude lists a candidate as checked and excluded with the
operator's reason, and refuses a USDOT number that is not in the
response.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

CENSUS_URL = "https://data.transportation.gov/resource/az4n-8mr2.json"
CENSUS_SELECT = (
    "dot_number,legal_name,dba_name,phy_city,phy_state,power_units,"
    "total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,"
    "safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,"
    "business_org_desc,carship,carrier_operation,status_code,classdef"
)
CENSUS_FIELDS = CENSUS_SELECT.split(",")
SAFER_URL = "https://safer.fmcsa.dot.gov/query.asp"
LI_URL = "https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist"
TIMEOUT_SECONDS = 60
ALL_SOURCES = ("census", "safer", "li")

# Labels quoted from the SAFER Company Snapshot text as recorded in the
# published carrier vetting delivery (deliveries/carrier-vetting-...md,
# sources S2, S3 and S8). The value of a label is the text line (or
# lines) that follow it, up to the next label or a line ending in ":".
SAFER_LABELS = [
    "Entity Type:",
    "USDOT Status:",
    "Out of Service Date:",
    "USDOT Number:",
    "MCS-150 Form Date:",
    "MCS-150 Mileage (Year):",
    "Operating Authority Status:",
    "MC/MX/FF Number(s):",
    "Legal Name:",
    "DBA Name:",
    "Physical Address:",
    "Phone:",
    "Power Units:",
    "Non-CMV Units:",
    "Drivers:",
    "Total Inspections:",
    "Rating Date:",
    "Review Date:",
    "Rating:",
]
SAFER_MULTILINE = {"Operating Authority Status:", "Physical Address:"}
SAFER_STOP_PREFIXES = ("For Licensing and Insurance details",)

# Line prefixes quoted from the Licensing and Insurance record text as
# recorded in the published delivery (source S9).
LI_PREFIXES = ("US DOT:", "Docket Number:", "Legal Name:")


# ----------------------------------------------------------------------
# Query building
# ----------------------------------------------------------------------

def check_usdot(value):
    value = str(value).strip()
    if not value.isdigit():
        raise ValueError("a USDOT number is digits only, got %r" % value)
    return value


def census_record_url(usdot):
    """The exact URL shape recorded in the published delivery: dot_number
    first, then $select with the field list, commas and $ unencoded."""
    return "%s?dot_number=%s&$select=%s" % (CENSUS_URL, check_usdot(usdot), CENSUS_SELECT)


def census_name_url(name, limit):
    """Full text search ($q) over the Census File, same $select list.
    Spaces are encoded as %20; $ and commas are left as they are. This
    query shape has not been checked against a recorded live response."""
    return CENSUS_URL + "?" + urllib.parse.urlencode(
        [("$q", name), ("$select", CENSUS_SELECT), ("$limit", str(int(limit)))],
        quote_via=lambda s, safe="", encoding=None, errors=None:
            urllib.parse.quote(s, safe="$,", encoding=encoding, errors=errors),
    )


def safer_url(usdot):
    """The exact URL shape recorded in the published delivery."""
    return (
        "%s?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT"
        "&query_string=%s" % (SAFER_URL, check_usdot(usdot))
    )


def li_url(usdot):
    """The carrier search form fields recorded in the published delivery
    (n_dotno, s_prefix=MC, pv_vpath=LIVIEW), sent as a GET query. The
    delivery read this record in a browser; the GET form of the request
    has not been checked against a recorded live response."""
    return "%s?n_dotno=%s&s_prefix=MC&pv_vpath=LIVIEW" % (LI_URL, check_usdot(usdot))


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Capture(object):
    """One HTTP exchange: the exact URL, the UTC retrieval time, the
    complete raw transcript (status line, headers in the order returned,
    a blank line, the body), the body text, the status line, and how the
    body bytes were decoded."""

    def __init__(self, url, retrieved, status_line, headers, body, decoding):
        self.url = url
        self.retrieved = retrieved
        self.status_line = status_line
        self.headers = headers
        self.body = body
        self.decoding = decoding

    @property
    def transcript(self):
        return "\n".join([self.status_line] + self.headers + ["", self.body])

    @property
    def status_ok(self):
        return self.status_line.split(" ", 2)[1:2] == ["200"]


def decode_body(raw):
    """UTF-8 when the bytes are valid UTF-8, else Latin-1, which maps every
    byte to one character so nothing is dropped or replaced."""
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("latin-1"), "latin-1 (the body is not valid UTF-8)"


def fetch(url):
    """GET the URL and return a Capture. HTTP error statuses are captured
    rather than raised, so a failed query is still shown verbatim.
    Transport errors (urllib.error.URLError, OSError) propagate."""
    retrieved = utc_now_iso()
    request = urllib.request.Request(
        url, headers={"Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                      "User-Agent": "tiny-ledger-fmcsa-fetcher"}
    )
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(
            getattr(response, "version", 11), "HTTP/1.1"
        )
        status_line = "%s %s %s" % (version, response.status, response.reason)
        headers = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        body, decoding = decode_body(response.read())
    return Capture(url, retrieved, status_line, headers, body, decoding)


# ----------------------------------------------------------------------
# Response reading
# ----------------------------------------------------------------------

def parse_census(body):
    """Census responses are a JSON array of objects. Returns the list, or
    raises ValueError when the body is anything else."""
    data = json.loads(body)
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError("response body is not a JSON array of objects")
    return data


class _TextLines(HTMLParser):
    """Collects the visible text of an HTML page as lines. Block level
    tags start a new line; inline tags do not, so a label split across
    inline markup stays on one line. Script and style content is
    skipped. Inner spacing of a line is kept as in the source, including
    non-breaking spaces; only leading and trailing whitespace is removed."""

    BLOCK = {
        "address", "article", "aside", "blockquote", "body", "br", "caption",
        "center", "dd", "div", "dl", "dt", "fieldset", "footer", "form", "h1",
        "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html", "legend",
        "li", "main", "nav", "ol", "option", "p", "pre", "section", "select",
        "table", "tbody", "td", "tfoot", "th", "thead", "title", "tr", "ul",
    }
    SKIP = {"script", "style"}

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.lines = []
        self._buf = []
        self._skip = 0

    def _flush(self):
        text = "".join(self._buf)  # characters kept as in the source, non-breaking spaces included
        self._buf = []
        for piece in text.replace("\r", "").split("\n"):
            piece = piece.strip()
            if piece:
                self.lines.append(piece)

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        if tag in self.BLOCK:
            self._flush()

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        if tag in self.BLOCK:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)

    def close(self):
        HTMLParser.close(self)
        self._flush()
        return self.lines


def text_lines(html):
    parser = _TextLines()
    parser.feed(html)
    return parser.close()


def labelled_values(lines, labels, multiline=frozenset(), stop_prefixes=()):
    """For each label, the text lines that follow its first occurrence,
    stopping at the next known label, at a line ending in ':' (except
    the first line after a multiline label), or at a stop prefix. Returns
    {label: None} when the label is not in the text and {label: []} when
    the label is directly followed by another label (a blank field)."""
    label_set = set(labels)
    found = {}
    for label in labels:
        try:
            start = lines.index(label)
        except ValueError:
            found[label] = None
            continue
        values = []
        for line in lines[start + 1:start + 1 + (4 if label in multiline else 1)]:
            if line in label_set or line.startswith(stop_prefixes):
                break
            if line.endswith(":") and not (label in multiline and not values):
                break
            values.append(line)
        found[label] = values
    return found


def value_text(values):
    if values is None:
        return "label not found in the response text"
    if not values:
        return "none shown (blank in the source)"
    return " ".join(values)


# ----------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------

def source_block(heading, capture, note=None):
    lines = ["Source. %s" % heading, "- Query URL: %s" % capture.url,
             "- Retrieved (UTC): %s" % capture.retrieved]
    if capture.decoding != "utf-8":
        lines.append("- Body decoding: %s" % capture.decoding)
    if note:
        lines.append("- Note: %s" % note)
    lines.append(
        "Excerpt (complete raw HTTP response transcript for the query above: "
        "status line, headers in the order returned, a blank line, then the "
        "complete body exactly as returned):"
    )
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", capture.transcript)), default=0))
    lines.append(fence)
    lines.extend(capture.transcript.split("\n"))
    lines.append(fence)
    return lines


def not_ok_lines(capture, what):
    return [
        "QUERY: %s (retrieved %s) returned HTTP status %s, not 200. The %s "
        "fields are not determinable from this response; the complete raw "
        "transcript is beneath the source link." % (
            what, capture.retrieved, capture.status_line.split(" ", 1)[1], what.split(" (")[0])
    ]


def render_census_record(record):
    lines = []
    for field in CENSUS_FIELDS:
        if field in record and record[field] is not None and str(record[field]) != "":
            lines.append("- %s as shown: %s" % (field, record[field]))
        else:
            lines.append("- %s: not present in the record" % field)
    extra = [k for k in record if k not in CENSUS_FIELDS]
    for k in extra:
        lines.append("- %s as shown (not in the $select list): %s" % (k, json.dumps(record[k], ensure_ascii=False)))
    return lines


def census_section(usdot, capture):
    lines = ["### Census record (FMCSA Company Census File, DOT open data dataset az4n-8mr2)", ""]
    what = "dot_number = %s" % usdot
    if not capture.status_ok:
        lines.extend(not_ok_lines(capture, what))
    else:
        try:
            records = parse_census(capture.body)
        except ValueError as err:
            lines.append(
                "QUERY: %s (retrieved %s) did not return a JSON array of objects "
                "(%s). The complete raw transcript is beneath the source link." % (what, capture.retrieved, err)
            )
            records = None
        if records is not None:
            n = len(records)
            lines.append("QUERY: %s returned %d %s (retrieved %s)." % (
                what, n, "record" if n == 1 else "records", capture.retrieved))
            if n == 0:
                lines[-1] += (" The response body was an empty array; the complete raw "
                              "HTTP response transcript is beneath the source link.")
            for i, record in enumerate(records):
                lines.append("")
                if n > 1:
                    lines.append("Record %d of %d:" % (i + 1, n))
                lines.extend(render_census_record(record))
    lines.append("")
    lines.extend(source_block("FMCSA Company Census File record, USDOT %s" % usdot, capture))
    return lines


def safer_section(usdot, capture):
    lines = ["### SAFER Company Snapshot", ""]
    what = "query_param = USDOT, query_string = %s" % usdot
    if not capture.status_ok:
        lines.extend(not_ok_lines(capture, what))
    else:
        found = labelled_values(text_lines(capture.body), SAFER_LABELS,
                                SAFER_MULTILINE, SAFER_STOP_PREFIXES)
        hits = sum(1 for v in found.values() if v is not None)
        lines.append(
            "QUERY: %s (retrieved %s). %d of %d labelled fields were found in the "
            "page text. Each value below is the text that follows its label in "
            "the page; the inspection, out of service and crash tables are not "
            "parsed and are read from the complete page beneath the source link."
            % (what, capture.retrieved, hits, len(SAFER_LABELS))
        )
        if hits == 0:
            lines.append(
                "None of the labelled fields appear in the response text, so no "
                "carrier field is claimed from it; read the complete response "
                "beneath the source link."
            )
        lines.append("")
        for label in SAFER_LABELS:
            lines.append("- %s %s" % (label, value_text(found[label])))
    lines.append("")
    lines.extend(source_block("FMCSA SAFER Company Snapshot, USDOT %s" % usdot, capture))
    return lines


def li_section(usdot, capture):
    lines = ["### Licensing and Insurance", ""]
    what = "n_dotno = %s, s_prefix = MC, pv_vpath = LIVIEW" % usdot
    if not capture.status_ok:
        lines.extend(not_ok_lines(capture, what))
    else:
        matches = [line for line in text_lines(capture.body) if line.startswith(LI_PREFIXES)]
        lines.append("QUERY: %s (retrieved %s). %d record text %s found." % (
            what, capture.retrieved, len(matches), "line" if len(matches) == 1 else "lines"))
        if matches:
            lines.append("")
            for line in matches:
                lines.append("- As shown: %s" % line)
        else:
            lines.append(
                "No Licensing and Insurance record fields were found in the "
                "response text. If the response beneath the source link is a "
                "verification challenge page rather than the carrier record, "
                "the record was not retrievable by automated read; the published "
                "carrier vetting delivery read this site in a live browser "
                "session for that reason. Nothing is claimed from this response."
            )
    lines.append("")
    lines.extend(source_block("FMCSA Licensing and Insurance carrier search, USDOT %s" % usdot, capture))
    return lines


def parse_exclusions(values):
    """--exclude 123456="reason" -> {'123456': 'reason'}."""
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError("--exclude needs the form USDOT=reason, got %r" % value)
        number, reason = value.split("=", 1)
        number = number.strip()
        reason = reason.strip().strip('"').strip("'")
        if not number.isdigit() or not reason:
            raise ValueError("--exclude needs a USDOT number and a reason, got %r" % value)
        exclusions[number] = reason
    return exclusions


def name_search_section(name, capture, exclusions=None):
    exclusions = dict(exclusions or {})
    lines = ["### Census name search (FMCSA Company Census File, DOT open data dataset az4n-8mr2)", ""]
    what = '$q = "%s"' % name
    if not capture.status_ok:
        lines.extend(not_ok_lines(capture, what))
        if exclusions:
            raise ValueError("exclusions given but the response is not HTTP 200")
    else:
        try:
            records = parse_census(capture.body)
        except ValueError as err:
            lines.append(
                "QUERY: %s (retrieved %s) did not return a JSON array of objects "
                "(%s). The complete raw transcript is beneath the source link." % (what, capture.retrieved, err)
            )
            records = None
            if exclusions:
                raise ValueError("exclusions given but the response is not a JSON array")
        if records is not None:
            n = len(records)
            lines.append("QUERY: %s returned %d %s (retrieved %s)." % (
                what, n, "record" if n == 1 else "records", capture.retrieved))
            if n == 0:
                lines[-1] += (" The response body was an empty array; the complete raw "
                              "HTTP response transcript is beneath the source link.")
            kept, excluded = [], []
            for record in records:
                key = str(record.get("dot_number", ""))
                if key in exclusions:
                    excluded.append((record, exclusions.pop(key)))
                else:
                    kept.append(record)
            if exclusions:
                raise ValueError("excluded USDOT number(s) not in the response: %s"
                                 % ", ".join(sorted(exclusions)))
            if kept:
                lines.append("")
                lines.append("CANDIDATES: %d %s. Which candidate is the subject carrier "
                             "is the operator's call; nothing here decides it." % (
                                 len(kept), "record" if len(kept) == 1 else "records"))
                for i, record in enumerate(kept):
                    lines.append("")
                    lines.append("Candidate %d of %d:" % (i + 1, len(kept)))
                    lines.extend(render_census_record(record))
            elif n:
                lines.append("")
                lines.append("CANDIDATES: none kept; every record returned is listed below as checked and excluded.")
            if excluded:
                lines.append("")
                lines.append("Checked and excluded: %d %s in the same response %s listed below with the reason each was excluded." % (
                    len(excluded), "record" if len(excluded) == 1 else "records",
                    "is" if len(excluded) == 1 else "are"))
                for record, reason in excluded:
                    lines.append("")
                    lines.extend(render_census_record(record))
                    lines.append("- Checked and excluded because: %s" % reason)
    lines.append("")
    lines.extend(source_block('FMCSA Company Census File name search, $q = "%s"' % name, capture))
    return lines


def render_carrier(subject, usdot, captures, sources):
    lines = ["## Carrier: %s" % subject, ""]
    lines.append(
        "Databases: " + ", ".join({
            "census": "FMCSA Company Census File (DOT open data portal, dataset az4n-8mr2)",
            "safer": "FMCSA SAFER Company Snapshot",
            "li": "FMCSA Licensing and Insurance",
        }[s] for s in sources) + ", queried by USDOT number %s." % usdot
    )
    lines.append("")
    for s in sources:
        if s == "census":
            lines.extend(census_section(usdot, captures["census"]))
        elif s == "safer":
            lines.extend(safer_section(usdot, captures["safer"]))
        elif s == "li":
            lines.extend(li_section(usdot, captures["li"]))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


# ----------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Query FMCSA carrier sources and print one Markdown section "
        "in the delivery format."
    )
    parser.add_argument("--subject", help="carrier name for the heading; defaults to the USDOT number or the search text")
    parser.add_argument("--usdot", help="USDOT number of the carrier")
    parser.add_argument("--name", help="carrier name search text for the Census File ($q)")
    parser.add_argument("--limit", type=int, default=50, help="name search $limit (default 50)")
    parser.add_argument("--source", action="append", choices=ALL_SOURCES,
                        help="with --usdot, which sources to query; repeatable; default all three in order")
    parser.add_argument("--exclude", action="append", metavar='USDOT="reason"',
                        help="with --name, list this USDOT number from the response as checked and excluded, with the reason; repeatable")
    args = parser.parse_args(argv)

    if bool(args.usdot) == bool(args.name):
        parser.error("give exactly one of --usdot or --name")
    if args.exclude and not args.name:
        parser.error("--exclude applies to a --name search")
    if args.source and not args.usdot:
        parser.error("--source applies to a --usdot run")
    try:
        exclusions = parse_exclusions(args.exclude)
        if args.usdot:
            usdot = check_usdot(args.usdot)
        if args.limit < 1:
            raise ValueError("--limit must be at least 1")
    except ValueError as err:
        parser.error(str(err))

    try:
        if args.name:
            url = census_name_url(args.name, args.limit)
            capture = fetch(url)
            lines = ["## Carrier search: %s" % (args.subject or args.name), ""]
            lines.extend(name_search_section(args.name, capture, exclusions))
        else:
            sources = []
            for s in args.source or ALL_SOURCES:
                if s not in sources:
                    sources.append(s)
            urls = {"census": census_record_url, "safer": safer_url, "li": li_url}
            captures = {}
            for s in sources:
                captures[s] = fetch(urls[s](usdot))
            lines = render_carrier(args.subject or "USDOT %s" % usdot, usdot, captures, sources)
    except (urllib.error.URLError, OSError) as err:
        sys.stderr.write("fetch failed, nothing printed: %s\n" % err)
        return 2
    except ValueError as err:
        sys.stderr.write("error: %s\n" % err)
        return 2
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
