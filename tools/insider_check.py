#!/usr/bin/env python3
"""SEC EDGAR insider activity check (issue #182, tool factory wave 2).

What insider purchases and sales has this public company reported
recently? Given a CIK or an issuer name, reads the EDGAR submissions index,
takes the most recent Form 3, 4 and 5 filings in it, reads each filing's raw
ownership XML, and prints one Markdown report in the delivery format from
AGENT-BRIEF.md: per filing, the reporting owner and relationship and each
transaction's date, code, shares, price, acquired or disposed code and
shares owned afterwards, all as filed; then the evidence: every query, its
UTC retrieval time, and the raw XML of each transaction row beneath the
filing link. The usage lines below use a placeholder contact; use your own.

    python3 tools/insider_check.py --contact "Your Name you@example.com" --cik 320193
    EDGAR_CONTACT="Your Name you@example.com" python3 tools/insider_check.py --cik 320193 --max-filings 2

EDGAR fair access is enforced exactly as in tools/edgar_formd.py, whose
helpers this tool uses: a declared contact (--contact or EDGAR_CONTACT, in
the plain "Name address" form) in a User-Agent naming this tool, paced
requests, and no contact value anywhere in the repo.

Requests, grounded in the repo's EDGAR fixtures and the coordinator's
captures on issue #182 (comments 6381275960 to 6381276451):
1. With --issuer, the EDGAR company search exactly as tools/edgar_formd.py
   sends it (the captured browse-edgar search, type D). One match
   proceeds; several are listed for the operator to choose with --cik;
   none is a report of no match.
2. The submissions index, https://data.sec.gov/submissions/CIK##########.json.
   The filings whose form is 3, 3/A, 4, 4/A, 5 or 5/A in its recent
   window are the ownership filings; the newest --max-filings of them,
   in index order, are read.
3. Each filing's raw ownership XML: the last segment of the index's
   primaryDocument in the filing's Archives folder. Capture 1 on #182 shows
   form4.xml in the folder for primaryDocument xslF345X06/form4.xml; the
   xslF345X06 path is a rendered view, never read.

Shown as filed, never explained: transactionCode, the acquired or disposed
code and the direct or indirect code. No SEC documentation of the codes was
captured. A price given only as a footnote reference is shown with that
footnote's text, verbatim.

Empty result: an index with no Form 3, 4 or 5 filing in its recent window
is reported with the complete raw submissions response as the proof. It
covers that window only; older index pages, when the index names them,
are listed and not read.

Failures: a failed request, any status but 200 (the captured Archives 404
for a wrong accession folder among them), or a body that is not the
captured shape stops the run with exit 2 and no report, naming the source,
the query and the reason.

Standard library only.
"""

import argparse
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import edgar_formd as ef  # noqa: E402

TOOL_NAME = "tiny-ledger insider_check.py"
CONTACT_ENV = ef.CONTACT_ENV
FetchError = ef.FetchError
Capture = ef.Capture
OWNERSHIP_FORMS = ("3", "3/A", "4", "4/A", "5", "5/A")
DEFAULT_MAX_FILINGS = 5
MAX_FILINGS = 20
TABLES = (("nonDerivativeTransaction", "non-derivative"), ("derivativeTransaction", "derivative"))
RELATIONSHIP_FLAGS = ("isDirector", "isOfficer", "isTenPercentOwner", "isOther")
CODES_NOTE = ("transactionCode, the acquired or disposed code (A or D) and the direct or indirect code are shown "
              "as filed. No SEC documentation of the codes was captured, so they are not explained here.")
OBSERVATION = ("Observation only: this report records what SEC EDGAR returned at the retrieval times stated below. "
               "It lists ownership filings as filed, newest first, from the index's recent window; it is not an "
               "analysis of any trade or of any person.")


def fetch(url, contact):
    """GET with this tool's declared User-Agent, paced, via tools/edgar_formd.py."""
    return ef.fetch(url, contact, TOOL_NAME)


def check_max(value):
    if not isinstance(value, int) or not 1 <= value <= MAX_FILINGS:
        raise ValueError("max filings must be 1 to %d" % MAX_FILINGS)
    return value


# ----------------------------------------------------------------------
# Ownership XML
# ----------------------------------------------------------------------

def _value(element, path):
    """(value text or None, [footnote ids]) for the element at path."""
    found = element.find(path) if element is not None else None
    if found is None:
        return None, []
    value = found.find("value")
    text = value.text.strip() if value is not None and value.text is not None else None
    return text, [f.get("id") for f in found.findall("footnoteId")]


def _text(element, path):
    found = element.find(path)
    return found.text.strip() if found is not None and found.text is not None else None


def parse_ownership(body, url):
    """The filing as filed. Raises FetchError when the body is not an ownership document."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as err:
        raise FetchError("%s answered a body that is not XML (%s); no report" % (url, err))
    if root.tag != "ownershipDocument":
        raise FetchError("%s answered XML whose root is <%s>, not <ownershipDocument>; no report" % (url, root.tag))
    owners = []
    for owner in root.findall("reportingOwner"):
        rel = owner.find("reportingOwnerRelationship")
        flags = [(f, _text(rel, f)) for f in RELATIONSHIP_FLAGS] if rel is not None else []
        owners.append({"name": _text(owner, "reportingOwnerId/rptOwnerName"),
                       "cik": _text(owner, "reportingOwnerId/rptOwnerCik"),
                       "flags": [(f, v) for f, v in flags if v is not None],
                       "officerTitle": _text(rel, "officerTitle") if rel is not None else None})
    if not owners:
        raise FetchError("%s answered an ownership document with no reportingOwner; no report" % url)
    transactions = []
    for tag, label in TABLES:
        raws = re.findall(r"<%s>.*?</%s>" % (tag, tag), body, re.S)
        elements = list(root.iter(tag))
        if len(raws) != len(elements):
            raise FetchError("%s: the %s rows could not be paired with their raw text; no report" % (url, tag))
        for el, raw in zip(elements, raws):
            transactions.append({
                "table": label, "raw": raw,
                "security": _value(el, "securityTitle"),
                "date": _value(el, "transactionDate"),
                "code": (_text(el, "transactionCoding/transactionCode"), []),
                "shares": _value(el, "transactionAmounts/transactionShares"),
                "price": _value(el, "transactionAmounts/transactionPricePerShare"),
                "acquired_disposed": _value(el, "transactionAmounts/transactionAcquiredDisposedCode"),
                "owned_after": _value(el, "postTransactionAmounts/sharesOwnedFollowingTransaction"),
                "direct_indirect": _value(el, "ownershipNature/directOrIndirectOwnership"),
                "exercise_price": _value(el, "conversionOrExercisePrice") if label == "derivative" else None,
            })
    footnotes = {f.get("id"): (f.text or "").strip() for f in root.findall("footnotes/footnote")}
    footnotes_raw = re.search(r"<footnotes>.*?</footnotes>", body, re.S)
    owners_raw = re.findall(r"<reportingOwner>.*?</reportingOwner>", body, re.S)
    return {"documentType": _text(root, "documentType"), "periodOfReport": _text(root, "periodOfReport"),
            "issuerName": _text(root, "issuer/issuerName"), "issuerCik": _text(root, "issuer/issuerCik"),
            "owners": owners, "owners_raw": owners_raw, "transactions": transactions, "footnotes": footnotes,
            "footnotes_raw": footnotes_raw.group(0) if footnotes_raw else None}


def shown(pair, footnotes):
    """A value as filed, with any footnotes it references, verbatim."""
    value, notes = pair
    parts = [ef.inline(value) if value is not None else "no value given"]
    for n in notes:
        parts.append("footnote %s: %s" % (n, ef.inline(footnotes.get(n, "(footnote text not in the document)"))))
    return "; ".join(parts)


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

def filing_lines(filing, capture, doc):
    lines = ["### Form %s, accession %s, filed %s" % (filing["form"], filing["accessionNumber"], filing["filingDate"]),
             "",
             "- Document type as filed: %s; period of report as filed: %s"
             % (ef.inline(doc["documentType"]), ef.inline(doc["periodOfReport"])),
             "- Issuer as filed: %s (issuerCik %s)" % (ef.inline(doc["issuerName"]), ef.inline(doc["issuerCik"]))]
    for owner in doc["owners"]:
        flags = ", ".join("%s %s" % fv for fv in owner["flags"] if fv[1] in ("true", "1")) or "none set to true"
        title = "; officerTitle %s" % ef.inline(owner["officerTitle"]) if owner["officerTitle"] else ""
        lines.append("- Reporting owner as filed: %s (rptOwnerCik %s); relationship flags as filed: %s%s"
                     % (ef.inline(owner["name"]), ef.inline(owner["cik"]), flags, title))
    lines.append("")
    if not doc["transactions"]:
        lines += ["This filing lists no transaction rows. Any holdings it reports are in the raw document at the "
                  "link below.", ""]
    for i, t in enumerate(doc["transactions"], 1):
        fn = doc["footnotes"]
        lines += ["#### Transaction %d (%s table)" % (i, t["table"]),
                  "- Security as filed: %s" % shown(t["security"], fn),
                  "- Transaction date as filed: %s" % shown(t["date"], fn),
                  "- transactionCode as filed: %s" % shown(t["code"], fn),
                  "- Shares as filed: %s" % shown(t["shares"], fn),
                  "- Price per share as filed: %s" % shown(t["price"], fn)]
        if t["exercise_price"] is not None:
            lines.append("- Conversion or exercise price as filed: %s" % shown(t["exercise_price"], fn))
        lines += ["- Acquired or disposed code as filed: %s" % shown(t["acquired_disposed"], fn),
                  "- Shares owned following the transaction as filed: %s" % shown(t["owned_after"], fn),
                  "- Direct or indirect code as filed: %s" % shown(t["direct_indirect"], fn), ""]
    lines += ["Evidence for this filing:", "",
              "Exact query: GET %s" % capture.url,
              "Retrieved (UTC): %s" % capture.retrieved,
              "Response: %s; body %d bytes, SHA-256 %s" % (capture.transcript.split("\n", 1)[0],
                                                          len(capture.body.encode("utf-8")),
                                                          hashlib.sha256(capture.body.encode("utf-8")).hexdigest()),
              "", "Source: <%s>" % capture.url, "The reporting owner, verbatim from the document:"]
    lines += [ef.fence_for(raw) + "\n" + raw + "\n" + ef.fence_for(raw) for raw in doc["owners_raw"]]
    for i, t in enumerate(doc["transactions"], 1):
        fence = ef.fence_for(t["raw"])
        lines += ["Transaction %d, verbatim from the document:" % i, fence, t["raw"], fence]
    if doc["footnotes_raw"]:
        fence = ef.fence_for(doc["footnotes_raw"])
        lines += ["The footnotes, verbatim from the document:", fence, doc["footnotes_raw"], fence]
    return lines + [""]


def run(contact, cik=None, issuer=None, max_filings=DEFAULT_MAX_FILINGS, fetcher=None):
    """Perform the requests and return the report lines. Raises FetchError or ValueError."""
    fetcher = fetcher if fetcher is not None else fetch
    check_max(max_filings)
    lines = ["# SEC EDGAR insider activity: %s" % ("CIK %s" % cik if cik is not None else issuer), "",
             OBSERVATION, ""]
    if issuer is not None:
        url = ef.company_search_url(issuer)
        capture = fetcher(url, contact)
        ef.require_200(capture, "EDGAR company search")
        kind, found = ef.parse_company_search(capture.body)
        lines += ["## Issuer lookup", "",
                  "Exact query: GET %s (the EDGAR company search as tools/edgar_formd.py sends it)" % url,
                  "Retrieved (UTC): %s" % capture.retrieved, ""]
        if kind == "none":
            lines.append("EDGAR company search returned no matching companies for this name; the complete raw "
                         "response is beneath the source link. No submissions index was read; rerun with --cik if "
                         "you know the issuer's CIK.")
            return lines + ef.source_block(capture)
        if kind == "many":
            lines.append("EDGAR company search returned %d matching companies. The tool does not choose between "
                         "them; rerun with --cik for the intended issuer." % len(found))
            lines.append("")
            lines += ["- Candidate as shown: CIK %s, %s, state %s" % (ef.inline(c), ef.inline(n), ef.inline(s))
                      for c, n, s in found]
            return lines + ef.source_block(capture)
        cik, name = found
        lines.append("EDGAR company search matched exactly one company: %s, CIK %s. Its submissions index is "
                     "read next." % (ef.inline(name), ef.inline(cik)))
        lines += ef.source_block(capture) + [""]

    sub_url = ef.submissions_url(cik)
    sub = fetcher(sub_url, contact)
    ef.require_200(sub, "EDGAR submissions index")
    name, cik_shown, filings, older = ef.parse_submissions(sub.body)
    owned = [f for f in filings if f["form"] in OWNERSHIP_FORMS]
    listed = owned[:max_filings]
    lines += ["## Answer", "",
              "Issuer as shown in the index: %s, CIK %s." % (ef.inline(name), ef.inline(cik_shown))]
    if not owned:
        lines += ["EDGAR's submissions index lists no Form 3, 4 or 5 filing (form 3, 3/A, 4, 4/A, 5 or 5/A) among "
                  "the %d filings in its recent window. The complete raw response below is the proof. This covers "
                  "that window only." % len(filings)]
        if older:
            lines.append("The index also names older pages, not read: %s." % ", ".join(ef.inline(o) for o in older))
        lines += ["", "## Evidence", "", "Exact query: GET %s" % sub_url, "Retrieved (UTC): %s" % sub.retrieved]
        return lines + ef.source_block(sub)
    lines += ["EDGAR's submissions index lists %d ownership filings (form 3, 3/A, 4, 4/A, 5 or 5/A) among the %d "
              "filings in its recent window; the newest %d, in index order, are read below."
              % (len(owned), len(filings), len(listed)), "", CODES_NOTE, ""]
    docs = []
    for filing in listed:
        url = ef.primary_doc_url(cik_shown, filing["accessionNumber"], filing["primaryDocument"])
        if url is None:
            raise FetchError("the index gives no primaryDocument for accession %s; no report"
                             % filing["accessionNumber"])
        capture = fetcher(url, contact)
        ef.require_200(capture, "EDGAR Archives ownership document")
        docs.append((filing, capture, parse_ownership(capture.body, url)))
    for filing, capture, doc in docs:
        lines += filing_lines(filing, capture, doc)
    body = sub.body.encode("utf-8")
    lines += ["## Evidence: the submissions index", "",
              "Exact query: GET %s" % sub_url, "Retrieved (UTC): %s" % sub.retrieved,
              "Response: %s; body %d bytes, SHA-256 %s" % (sub.transcript.split("\n", 1)[0], len(body),
                                                          hashlib.sha256(body).hexdigest()),
              "", "The index entries read, as shown (filings.recent arrays, by position):"]
    entries = "\n".join("form %s, filingDate %s, accessionNumber %s, primaryDocument %s"
                        % (f["form"], f["filingDate"], f["accessionNumber"], f["primaryDocument"]) for f in listed)
    lines += [ef.fence_for(entries), entries, ef.fence_for(entries)]
    return lines


def main(argv=None, fetcher=None, stdout=None, stderr=None, env=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = argparse.ArgumentParser(description="SEC EDGAR insider activity (Forms 3, 4 and 5) for one issuer.")
    who = p.add_mutually_exclusive_group(required=True)
    who.add_argument("--cik", help="the issuer's CIK")
    who.add_argument("--issuer", help="the issuer's name, looked up with the EDGAR company search")
    p.add_argument("--contact", help="your EDGAR fair access contact, \"Name address\" (or set %s)" % CONTACT_ENV)
    p.add_argument("--max-filings", type=int, default=DEFAULT_MAX_FILINGS,
                   help="ownership filings to read, 1 to %d (default %d)" % (MAX_FILINGS, DEFAULT_MAX_FILINGS))
    args = p.parse_args(argv)
    try:
        contact = ef.contact_from(args.contact, env)
        if args.cik is not None:
            ef.cik10(args.cik)
        lines = run(contact, cik=args.cik, issuer=args.issuer, max_filings=args.max_filings, fetcher=fetcher)
    except ValueError as err:
        stderr.write("error: %s\n" % err)
        return 2
    stdout.write("\n".join(lines).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
