#!/usr/bin/env python3
"""SEC EDGAR Form D fetcher.

Given an issuer name or a CIK, queries the public EDGAR APIs live and
prints one Markdown section in the delivery format from AGENT-BRIEF.md:
claim lines, the exact query, the UTC retrieval time, the source link,
and the complete raw HTTP response transcript printed verbatim directly
beneath the link, for every request made.

Standard library only. No key is needed. EDGAR fair access is enforced:

* Every request carries a descriptive User-Agent that names this tool
  and an operator supplied contact, given with --contact or the
  EDGAR_CONTACT environment variable. The tool refuses to run without
  one. The SEC asks for a declared user agent of the form
  "Sample Company Name AdminContact@<sample company domain>.com"
  (https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data,
  read 2026-10-23).
* Requests are paced to at most one every MIN_INTERVAL_SECONDS, inside
  the SEC's published "Current max request rate: 10 requests/second"
  (same page).
* The contact (placeholder shown: "Name you@example.com") must be that plain
  "Name address" form, with your own address. During
  development EDGAR answered 403 ("Your Request Originates from an
  Undeclared Automated Tool") to a contact carrying a URL in
  parentheses, so the tool refuses URLs, parentheses and brackets.

Usage examples:

    python3 tools/edgar_formd.py --contact "Your Name you@example.com" --cik 2156237
    python3 tools/edgar_formd.py --contact "Your Name you@example.com" --issuer "8VC DSS III"
    EDGAR_CONTACT="Your Name you@example.com" python3 tools/edgar_formd.py --cik 320193
    python3 tools/edgar_formd.py --cik 1801756 --max-filings 2 \\
        --exclude 0000929638-26-003990="amendment of a filing already listed"

Requests, in order:

1. With --issuer, the EDGAR company search (browse-edgar, type D) by
   name. Exactly one match proceeds; several matches are listed with
   their CIKs for the operator to choose one with --cik; none is
   proven by the raw response. The tool never picks an issuer itself.
2. The submissions index for the CIK (data.sec.gov/submissions). Form D
   filings are the entries whose form is D or D/A. Zero is proven by
   the full raw response. If the index names older index files beyond
   its recent window, the section says so; they are not fetched.
3. For each Form D filing, up to --max-filings, the filing's primary
   document XML from the EDGAR archive, parsed with the standard
   library and rendered as one claim block: issuer name and CIK, form
   type, filing date, date of first sale, total offering amount, total
   amount sold, total remaining, investors, industry group, exemptions,
   and the filing index page link, each value as shown. A field the
   XML does not carry is printed as not present, never filled in. A
   filing whose primary document is not XML is listed with its index
   link and no extracted values.

Any failed or unexpected response stops the run with a diagnostic on
stderr and no report on stdout: a failed fetch is never shown as an
empty result. Exclusions are operator supplied (--exclude
ACCESSION=reason); an accession that is not in the submissions
response is refused.
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
COMPANY_SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/"
TOOL_NAME = "tiny-ledger edgar_formd.py"
CONTACT_ENV = "EDGAR_CONTACT"
MIN_INTERVAL_SECONDS = 0.2  # 5 requests/second, inside the published 10/second
TIMEOUT_SECONDS = 60
FORM_D_TYPES = ("D", "D/A")
NOT_PRESENT = "not present in the filing XML"


class FetchError(ValueError):
    """A failed or uninterpretable response must never become an empty result."""


class Capture:
    """One request: the exact URL, the UTC retrieval time, the raw transcript."""

    def __init__(self, url, retrieved, transcript, body):
        self.url = url
        self.retrieved = retrieved
        self.transcript = transcript
        self.body = body


# ----------------------------------------------------------------------
# Fair access: contact, user agent, pacing
# ----------------------------------------------------------------------

def contact_from(value, env=None):
    """The operator contact for the User-Agent. Refuses blank or
    address-less values; never falls back to a default."""
    env = os.environ if env is None else env
    text = (value or env.get(CONTACT_ENV, "") or "").strip()
    if not text or "@" not in text or text.startswith("@") or text.endswith("@"):
        raise ValueError(
            "an operator contact with an email address is required for EDGAR "
            "fair access: for example --contact \"Name you@example.com\" (a placeholder; "
            "use your own address), or set %s" % CONTACT_ENV
        )
    if re.search(r"[()<>/:\\\[\]{}]", text):
        # Observed 2026-10-23: EDGAR answered 403 "Your Request Originates from an
        # Undeclared Automated Tool" to a contact that carried a URL in parentheses,
        # and 200 to the plain "Name email" form the SEC documents.
        raise ValueError(
            "the contact must be the plain form the SEC documents, for example "
            "\"Name you@example.com\" (a placeholder): "
            "no URLs, parentheses or brackets"
        )
    return text


def user_agent(contact):
    return "%s %s" % (TOOL_NAME, contact)


_last_request_at = [0.0]


def pace(now=time.monotonic, sleep=time.sleep):
    """Wait so that consecutive requests are at least MIN_INTERVAL_SECONDS apart."""
    wait = _last_request_at[0] + MIN_INTERVAL_SECONDS - now()
    if wait > 0:
        sleep(wait)
    _last_request_at[0] = now()


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url, contact):
    """GET the URL with the declared user agent, paced. Returns a Capture.

    The transcript is the complete raw HTTP response: status line, the
    headers in the order returned, a blank line, then the body decoded
    as UTF-8 exactly as returned. HTTP error statuses are captured the
    same way; the caller decides whether a non-200 is fatal.
    """
    pace()
    retrieved = utc_now_iso()
    request = urllib.request.Request(url, headers={
        "User-Agent": user_agent(contact),
        "Accept-Encoding": "identity",
    })
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        response = err
    except (urllib.error.URLError, OSError) as err:
        raise FetchError("request failed: %s; no report" % err) from err
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        header_lines = ["%s: %s" % (k, v) for k, v in response.headers.items()]
        raw = response.read()
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError:
        body = raw.decode("latin-1")
    transcript = "\n".join([status_line] + header_lines + ["", body])
    return Capture(url, retrieved, transcript, body)


def require_200(capture, what):
    if not capture.transcript.startswith("HTTP/1.1 200 ") and not capture.transcript.startswith("HTTP/1.0 200 "):
        status = capture.transcript.split("\n", 1)[0]
        raise FetchError("%s answered %r, not 200; no report (query %s)" % (what, status, capture.url))


# ----------------------------------------------------------------------
# URLs and identifiers
# ----------------------------------------------------------------------

def cik10(cik):
    text = str(cik).strip()
    if not text.isdigit() or len(text) > 10 or int(text) == 0:
        raise ValueError("a CIK is 1 to 10 digits, got %r" % cik)
    return text.zfill(10)


def submissions_url(cik):
    return SUBMISSIONS_URL.format(cik10=cik10(cik))


def company_search_url(name):
    if not name.strip():
        raise ValueError("issuer name must not be blank")
    return COMPANY_SEARCH_URL + "?" + urllib.parse.urlencode(
        [("action", "getcompany"), ("company", name.strip()), ("type", "D"), ("output", "")]
    )


def accession_nodash(accession):
    text = accession.strip()
    if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", text):
        raise ValueError("an accession number looks like 0001234567-26-000001, got %r" % accession)
    return text.replace("-", "")


def archive_folder(cik, accession):
    return ARCHIVE_URL.format(cik=int(cik10(cik)), acc_nodash=accession_nodash(accession))


def primary_doc_url(cik, accession, primary_document):
    """The raw primary document. The submissions index gives the rendered
    path (xslFormDX01/primary_doc.xml); the raw file is its last segment."""
    name = (primary_document or "").split("/")[-1]
    if not name:
        return None
    return archive_folder(cik, accession) + name


def filing_index_url(cik, accession):
    return archive_folder(cik, accession) + accession.strip() + "-index.htm"


# ----------------------------------------------------------------------
# Parsing: company search, submissions, Form D XML
# ----------------------------------------------------------------------

def _strip_tags(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def parse_company_search(body):
    """Returns ("many", [(cik, name, state), ...]), ("one", (cik, name)),
    or ("none", []) from the browse-edgar company search HTML."""
    if 'id="companyMatch"' in body or "companyMatch" in body:
        matches = []
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
            cells = [_strip_tags(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(cells) >= 2 and re.fullmatch(r"\d{10}", cells[0]):
                matches.append((cells[0], cells[1], cells[2] if len(cells) > 2 else ""))
        if not matches:
            raise FetchError("company search returned a match table with no rows the tool "
                             "could read; no report")
        return "many", matches
    one = re.search(r'<span class="companyName">(.*?)</span>', body, re.S)
    if one:
        text = _strip_tags(one.group(1))
        cik = re.search(r"CIK#:\s*(\d{10})", text)
        if not cik:
            raise FetchError("company page names a company but no CIK the tool could read; no report")
        name = text.split("CIK#:")[0].strip()
        return "one", (cik.group(1), name)
    if "No matching companies" in body:
        return "none", []
    raise FetchError("company search page has none of the three known shapes; no report")


def parse_submissions(body):
    """Returns (name, cik, filings, older_files) from the submissions JSON.
    filings is a list of dicts with form, filingDate, accessionNumber,
    primaryDocument, primaryDocDescription, in index order."""
    try:
        data = json.loads(body)
    except ValueError as err:
        raise FetchError("submissions body is not JSON; no report") from err
    if not isinstance(data, dict) or not isinstance(data.get("filings"), dict):
        raise FetchError("submissions JSON has no filings object; no report")
    recent = data["filings"].get("recent")
    if not isinstance(recent, dict) or not isinstance(recent.get("form"), list):
        raise FetchError("submissions JSON has no recent filings arrays; no report")
    keys = ("form", "filingDate", "accessionNumber", "primaryDocument", "primaryDocDescription")
    columns = {k: recent.get(k) if isinstance(recent.get(k), list) else [] for k in keys}
    count = len(columns["form"])
    for k in ("filingDate", "accessionNumber"):
        if len(columns[k]) != count:
            raise FetchError("submissions JSON arrays differ in length; no report")
    filings = []
    for i in range(count):
        filings.append({
            "form": columns["form"][i],
            "filingDate": columns["filingDate"][i],
            "accessionNumber": columns["accessionNumber"][i],
            "primaryDocument": columns["primaryDocument"][i] if i < len(columns["primaryDocument"]) else "",
            "primaryDocDescription": columns["primaryDocDescription"][i] if i < len(columns["primaryDocDescription"]) else "",
        })
    older = [f.get("name") for f in data["filings"].get("files") or [] if isinstance(f, dict)]
    return data.get("name"), data.get("cik"), filings, older


def form_d_filings(filings):
    return [f for f in filings if f["form"] in FORM_D_TYPES]


def parse_form_d(body):
    """Parse a Form D primary_doc.xml into shown values. Returns a dict of
    lists of strings; missing elements give empty lists."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as err:
        raise FetchError("primary document is not well formed XML; no report") from err
    if root.tag != "edgarSubmission":
        raise FetchError("primary document root is %r, not edgarSubmission; no report" % root.tag)

    def texts(path):
        return [(e.text or "").strip() for e in root.findall(path) if (e.text or "").strip()]

    first_sale = texts("./offeringData/typeOfFiling/dateOfFirstSale/value")
    if not first_sale and texts("./offeringData/typeOfFiling/dateOfFirstSale/yetToOccur") == ["true"]:
        first_sale = ["yetToOccur: true"]
    return {
        "submissionType": texts("./submissionType"),
        "issuerName": texts("./primaryIssuer/entityName"),
        "issuerCik": texts("./primaryIssuer/cik"),
        "isAmendment": texts("./offeringData/typeOfFiling/newOrAmendment/isAmendment"),
        "dateOfFirstSale": first_sale,
        "totalOfferingAmount": texts("./offeringData/offeringSalesAmounts/totalOfferingAmount"),
        "totalAmountSold": texts("./offeringData/offeringSalesAmounts/totalAmountSold"),
        "totalRemaining": texts("./offeringData/offeringSalesAmounts/totalRemaining"),
        "amountsClarification": texts("./offeringData/offeringSalesAmounts/clarificationOfResponse"),
        "investorsAlreadyInvested": texts("./offeringData/investors/totalNumberAlreadyInvested"),
        "industryGroup": texts("./offeringData/industryGroup/industryGroupType"),
        "exemptions": texts("./offeringData/federalExemptionsExclusions/item"),
    }


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def inline(value):
    """JSON quote and Markdown escape a shown value, as the other fetchers do."""
    text = json.dumps(value, ensure_ascii=False)
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", text)


def _shown(label, values):
    if not values:
        return ["- %s: %s" % (label, NOT_PRESENT)]
    if len(values) == 1:
        return ["- %s as shown: %s" % (label, inline(values[0]))]
    return ["- %s as shown: %s" % (label, "; ".join(inline(v) for v in values))]


def fence_for(text):
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def source_block(capture, note=None):
    fence = fence_for(capture.transcript)
    lines = ["", "Source: <%s>" % capture.url]
    if note:
        lines.append(note)
    lines.append(fence)
    lines.extend(capture.transcript.split("\n"))
    lines.append(fence)
    return lines


def render_filing_block(cik, filing, parsed, label):
    acc = filing["accessionNumber"]
    lines = ["#### Form D %s" % acc]
    lines.append("- Accession number as shown: %s" % inline(acc))
    lines.append("- Form type as shown (submissions index): %s" % inline(filing["form"]))
    lines.append("- Filing date as shown (submissions index): %s" % inline(filing["filingDate"]))
    if parsed is None:
        lines.append("- Primary document as shown: %s; it is not an XML Form D, so no values "
                     "were extracted" % inline(filing["primaryDocument"] or ""))
    else:
        lines.extend(_shown("Issuer name", parsed["issuerName"]))
        lines.extend(_shown("Issuer CIK", parsed["issuerCik"]))
        lines.extend(_shown("Submission type", parsed["submissionType"]))
        lines.extend(_shown("Amendment", parsed["isAmendment"]))
        lines.extend(_shown("Date of first sale", parsed["dateOfFirstSale"]))
        lines.extend(_shown("Total offering amount", parsed["totalOfferingAmount"]))
        lines.extend(_shown("Total amount sold", parsed["totalAmountSold"]))
        lines.extend(_shown("Total remaining", parsed["totalRemaining"]))
        if parsed["amountsClarification"]:
            lines.extend(_shown("Clarification of amounts", parsed["amountsClarification"]))
        lines.extend(_shown("Investors already invested", parsed["investorsAlreadyInvested"]))
        lines.extend(_shown("Industry group", parsed["industryGroup"]))
        lines.extend(_shown("Federal exemptions and exclusions", parsed["exemptions"]))
    lines.append("- Filing index page: %s" % filing_index_url(cik, acc))
    lines.append("- Listed as: %s" % label)
    return lines


def parse_exclusions(values):
    exclusions = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError("--exclude needs ACCESSION=reason, got %r" % value)
        acc, reason = value.split("=", 1)
        acc, reason = acc.strip(), reason.strip().strip('"').strip("'")
        if not acc or not reason:
            raise ValueError("--exclude needs both an accession number and a reason, got %r" % value)
        exclusions[acc] = reason
    return exclusions


# ----------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------

def run(contact, cik=None, issuer=None, max_filings=10, exclusions=None, fetcher=None):
    """Perform the requests and return the Markdown lines. Raises FetchError
    or ValueError; the caller prints nothing on either. `fetcher` defaults to
    the module-level fetch, looked up at call time so tests can replace it."""
    fetcher = fetcher if fetcher is not None else fetch
    exclusions = dict(exclusions or {})
    lines = []

    if issuer is not None:
        url = company_search_url(issuer)
        capture = fetcher(url, contact)
        require_200(capture, "EDGAR company search")
        kind, found = parse_company_search(capture.body)
        lines.append("## SEC EDGAR Form D filings: issuer lookup for %s" % inline(issuer))
        lines.append("")
        lines.append("### Issuer lookup")
        lines.append("")
        lines.append("Exact query: GET %s" % url)
        lines.append("Retrieved (UTC): %s" % capture.retrieved)
        lines.append("")
        if kind == "none":
            lines.append("EDGAR company search returned no matching companies for this name; the "
                         "complete raw response is beneath the source link. No CIK was looked up.")
            lines.extend(source_block(capture))
            return lines
        if kind == "many":
            lines.append("EDGAR company search returned %d matching companies. The tool does not "
                         "choose between them; rerun with --cik for the intended issuer." % len(found))
            lines.append("")
            for c, name, state in found:
                lines.append("- Candidate as shown: CIK %s, %s, state %s" % (inline(c), inline(name), inline(state)))
            lines.extend(source_block(capture))
            return lines
        cik, name = found
        lines.append("EDGAR company search matched exactly one company: %s, CIK %s. Its "
                     "submissions index is queried next." % (inline(name), inline(cik)))
        lines.extend(source_block(capture))
        lines.append("")

    sub_url = submissions_url(cik)
    sub = fetcher(sub_url, contact)
    require_200(sub, "EDGAR submissions index")
    name, cik_shown, filings, older = parse_submissions(sub.body)
    formd = form_d_filings(filings)
    subject = "%s (CIK %s)" % (name, cik_shown)
    if issuer is None:
        lines.append("## SEC EDGAR Form D filings: %s" % subject)
        lines.append("")
    lines.append("### Submissions index")
    lines.append("")
    lines.append("Exact query: GET %s" % sub_url)
    lines.append("Retrieved (UTC): %s" % sub.retrieved)
    lines.append("")
    lines.append("Issuer as shown: %s, CIK %s." % (inline(name), inline(cik_shown)))
    lines.append("EDGAR lists %d Form D filings (form D or D/A) among the %d filings in the index's "
                 "recent window." % (len(formd), len(filings)))
    if older:
        lines.append("The index also names %d older index file(s) outside the recent window, not "
                     "queried by this tool: %s. Filings in them are not covered by this report."
                     % (len(older), ", ".join(inline(o) for o in older)))
    if not formd:
        lines.append("No Form D filing is listed in the recent window; the complete raw response "
                     "is beneath the source link. This is not a statement that no offering exists.")
    else:
        lines.append("")
        for f in formd:
            lines.append("- Form %s filed %s, accession %s, primary document %s"
                         % (inline(f["form"]), inline(f["filingDate"]), inline(f["accessionNumber"]),
                            inline(f["primaryDocument"] or "")))
    lines.extend(source_block(sub))

    present = {f["accessionNumber"] for f in formd}
    missing = sorted(set(exclusions) - present)
    if missing:
        raise ValueError("excluded accession(s) not in the submissions response: %s" % ", ".join(missing))

    for f in formd[:max_filings]:
        label = "Checked and excluded: %s" % exclusions[f["accessionNumber"]] \
            if f["accessionNumber"] in exclusions else "Form D filing"
        lines.append("")
        lines.append("### Form D filing %s" % f["accessionNumber"])
        lines.append("")
        doc_url = primary_doc_url(cik, f["accessionNumber"], f["primaryDocument"])
        if not doc_url or not doc_url.lower().endswith(".xml"):
            lines.append("No XML primary document is listed for this filing; nothing was fetched for it.")
            lines.append("")
            lines.extend(render_filing_block(cik, f, None, label))
            continue
        doc = fetcher(doc_url, contact)
        require_200(doc, "EDGAR filing document")
        parsed = parse_form_d(doc.body)
        lines.append("Exact query: GET %s" % doc_url)
        lines.append("Retrieved (UTC): %s" % doc.retrieved)
        lines.append("")
        lines.extend(render_filing_block(cik, f, parsed, label))
        lines.extend(source_block(doc))

    skipped = len(formd) - min(len(formd), max_filings)
    if skipped > 0:
        lines.append("")
        lines.append("%d further Form D filing(s) listed above were not fetched because "
                     "--max-filings is %d." % (skipped, max_filings))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--contact", help="operator contact for the User-Agent, e.g. "
                        "\"Name you@example.com\"; or set %s" % CONTACT_ENV)
    parser.add_argument("--cik", help="issuer CIK, 1 to 10 digits")
    parser.add_argument("--issuer", help="issuer name for the EDGAR company search")
    parser.add_argument("--max-filings", type=int, default=10,
                        help="Form D filings to fetch and render, newest first; default 10")
    parser.add_argument("--exclude", action="append", metavar='ACCESSION="reason"',
                        help="list this Form D filing as checked and excluded, with the reason; repeatable")
    args = parser.parse_args(argv)
    try:
        contact = contact_from(args.contact)
        if (args.cik is None) == (args.issuer is None):
            raise ValueError("give exactly one of --cik or --issuer")
        if args.max_filings < 0:
            raise ValueError("--max-filings must be 0 or more")
        exclusions = parse_exclusions(args.exclude)
        if args.cik is not None:
            cik10(args.cik)
    except ValueError as err:
        parser.error(str(err))
    try:
        lines = run(contact, cik=args.cik, issuer=args.issuer, max_filings=args.max_filings,
                    exclusions=exclusions)
    except (FetchError, ValueError) as err:
        sys.stderr.write("EDGAR fetch failed: %s. No report emitted.\n" % err)
        return 1
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
