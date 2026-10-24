#!/usr/bin/env python3
"""Brand Name Checker: domains, social handles, app store, trademarks.

Given one or more candidate names, prints one Markdown report per name in
the delivery format from AGENT-BRIEF.md: a domains table, a handles table,
app store matches and a trademark section, every row with its check time
in UTC, then the evidence for each row (claim line, source link, raw
excerpt directly beneath it). Each report ends with two fixed lines: the
trademark section is a starting point and not legal advice, and no
searched name was registered or reserved by the agent. The tool only
sends GET requests; it never registers, reserves or signs up for anything.

Key: none needed. Standard library only. Hosts called: rdap.org (and the
registry RDAP server it redirects to), x.com, www.instagram.com,
www.tiktok.com, itunes.apple.com.

    python3 tools/brand_name_checker.py Nike
    python3 tools/brand_name_checker.py zqxflorp --tlds com,io,app \
        --platforms x,instagram,tiktok --variations 3

How each leg is judged (from the live checks recorded on issue #51):

* Domains: GET https://rdap.org/domain/<name>.<tld>, redirects followed.
  200 is registered; 404 is no registration found, and its body is never
  read (a 404 body can hang a chunked reader); any other status, or a
  failed request, is "could not confirm". A 200 row quotes ldhName and the
  registration event from the body. A request that gets no response at
  all is retried once (issue #201, see get()); two failures in a row are
  still "could not confirm".
* X: GET https://x.com/<handle>. 200 is a live account, 404 is no
  account. Any other status or a failed request is "could not confirm".
* Instagram and TikTok answer real and invented names alike with a 200
  login wall, so a 200 is "could not confirm", never available. Only a
  hard 404 is reported as no account found.
* App Store: the iTunes Search API matches loosely (the captured search
  for the invented name zqxflorp returned two unrelated apps), so the tool
  fetches generously and keeps only exact name matches. Exact means: the
  app's trackName, cut at its first subtitle separator (":", " - ",
  " | "), equals the candidate name once both are reduced to lower case
  letters and digits. Google Play has no official public search API; it
  is out of scope and the report says so.
* Trademarks: not covered. No working trademark source has been captured
  for this tool, so the section says so and names the database it would
  search (USPTO trademark search, United States). It never states a mark
  or a status. The section comes from uspto_trademarks.py, which reads an
  optional key from USPTO_API_KEY only; with no key, or before the keyed
  search is documented (issue #125), the wording is unchanged.

Handles are checked in lower case (these platforms treat handles case
insensitively; the recorded X check was x.com/nike). Handle and status
bodies are not read. Evidence for a status-only check is
the status line and response headers as returned, with Set-Cookie values
withheld (session cookies are not evidence and are not printed).

Fail closed: a failed request is never shown as available. Within a
report each failed check is its own "could not confirm" row with the
error. Bad input exits 2 with nothing on stdout.

Variations (--variations N) are only produced when asked. Candidates are
formed by fixed patterns (name + "hq", "get" + name, name + "app",
"try" + name, name + "co", "the" + name) and each is checked live; a
variation is listed only if every requested domain answered 404 and X
answered 404. Unverified candidates are never listed as suggestions.
"""

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from datetime import datetime, timezone

import uspto_trademarks
from propublica_nonprofits import Node, fenced, inline, skip_ws

RDAP_BASE = "https://rdap.org/domain/"
X_BASE = "https://x.com/"
INSTAGRAM_BASE = "https://www.instagram.com/"
TIKTOK_BASE = "https://www.tiktok.com/@"
ITUNES_SEARCH = "https://itunes.apple.com/search"
TIMEOUT_SECONDS = 20
USER_AGENT = "tiny-ledger-brand-name-checker"
PLATFORMS = ("x", "instagram", "tiktok")
VARIATION_PATTERNS = ("{}hq", "get{}", "{}app", "try{}", "{}co", "the{}")

# first_error: set only when the request was retried after getting no response (issue #201).
Result = namedtuple("Result", "url final_url checked status_line status headers body error first_error",
                    defaults=(None,))

REGISTERED = "registered"
NOT_REGISTERED = "no registration found"
LIVE = "taken (live account)"
NO_ACCOUNT = "no account found"
UNCONFIRMED = "could not confirm"


# ----------------------------------------------------------------------
# Fetching
# ----------------------------------------------------------------------

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def header_lines(headers):
    out = []
    for k, v in headers.items():
        out.append("%s: %s" % (k, "[value not printed]" if k.lower() == "set-cookie" else v))
    return out


def get(url, read_body):
    """GET url, following redirects. The body is read only when read_body
    is true and the status is 200. Never raises: a failed request comes
    back with error set and status None.

    A request that gets no response at all (the connection fails or closes
    before any status line) is sent once more, straight away, and only once
    (issue #201: the live discriminating check showed rdap.org answering the
    same URL with a 404 on some attempts and closing the connection on
    others). An HTTP status is never retried, and neither is a failed body
    read after a response. When the second attempt fails too, its failure
    is the result, so the check stays "could not confirm"."""
    result, no_response = _attempt(url, read_body)
    if not no_response:
        return result
    retried, _ = _attempt(url, read_body)
    return retried._replace(first_error=result.error)


def _attempt(url, read_body):
    """(Result, True when no response arrived at all)."""
    checked = utc_now_iso()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as err:
        lines = header_lines(err.headers) if err.headers is not None else []
        final = err.geturl() or url
        err.close()  # the error body is never read
        return Result(url, final, checked, "HTTP %s %s" % (err.code, err.reason), err.code, lines, None, None), False
    except ValueError as err:
        return Result(url, url, checked, None, None, [], None, str(err)), False
    except (urllib.error.URLError, OSError) as err:
        return Result(url, url, checked, None, None, [], None, str(err)), True
    with response:
        version = {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(getattr(response, "version", 11), "HTTP/1.1")
        status_line = "%s %s %s" % (version, response.status, response.reason)
        lines = header_lines(response.headers)
        body = None
        if read_body and response.status == 200:
            try:
                body = response.read().decode("utf-8")
            except (UnicodeDecodeError, OSError) as err:
                return Result(url, response.geturl(), checked, status_line, None, lines, None,
                              "body could not be read: %s" % err), False
        return Result(url, response.geturl(), checked, status_line, response.status, lines, body, None), False


# ----------------------------------------------------------------------
# Verdicts
# ----------------------------------------------------------------------

def domain_verdict(result):
    if result.error:
        return UNCONFIRMED
    if result.status == 200:
        return REGISTERED if result.body is not None else UNCONFIRMED
    if result.status == 404:
        return NOT_REGISTERED
    return UNCONFIRMED


def handle_verdict(platform, result):
    if result.error or result.status is None:
        return UNCONFIRMED
    if result.status == 404:
        return NO_ACCOUNT
    if result.status == 200 and platform == "x":
        return LIVE
    return UNCONFIRMED


def valid_handle(platform, name):
    if platform == "x":
        return re.fullmatch(r"[A-Za-z0-9_]{1,15}", name) is not None
    if platform == "instagram":
        return re.fullmatch(r"[A-Za-z0-9._]{1,30}", name) is not None
    return re.fullmatch(r"[A-Za-z0-9._]{2,24}", name) is not None


def normalize(text):
    return re.sub(r"[^0-9a-z]", "", text.casefold())


def title_part(track_name):
    return re.split(r":| - | – | \| ", track_name, maxsplit=1)[0]


def label(name):
    """The domain label for a name: lower case letters, digits and hyphens."""
    return re.sub(r"[^0-9a-z-]", "", name.lower()).strip("-")


# ----------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------

def status_text(result):
    return result.status_line if result.status_line else "no response (%s)" % result.error


def transcript(result, body_note):
    lines = [result.status_line or "no response"] + result.headers + [""]
    if result.error:
        lines.append("request failed: %s" % result.error)
    elif result.body is not None:
        lines.append(result.body)
    else:
        lines.append(body_note)
    if result.first_error:
        lines.append("[retried once: the first attempt got no response: %s]" % result.first_error)
    return "\n".join(lines)


def evidence(lines, claim, result, body_note, extra=()):
    lines.append("- %s" % claim)
    lines.append("  Source: <%s>%s" % (result.url, "" if result.final_url in (None, result.url)
                                       else " (answered from %s)" % result.final_url))
    lines.append("  Checked (UTC): %s" % result.checked)
    lines.append("")
    for excerpt in extra:
        lines.append(fenced(excerpt))
        lines.append("")
    lines.append(fenced(transcript(result, body_note)))
    lines.append("")


def rdap_excerpts(body):
    """Raw excerpts of ldhName and the registration event, cut from the body."""
    try:
        node = Node(body, skip_ws(body, 0))
    except (ValueError, IndexError):
        return None
    out = []
    if node.has("ldhName"):
        out.append(node.excerpt("ldhName"))
    if node.has("events") and node.literal("events")[:1] == "[":
        for ev in node.children("events"):
            if ev.has("eventAction") and ev.value("eventAction") == "registration":
                out.append(ev.whole())
    return out


def itunes_matches(body, name):
    """(result count as shown, returned count, [exact match nodes]) or None."""
    try:
        node = Node(body, skip_ws(body, 0))
        if not node.has("results") or node.literal("results")[:1] != "[":
            return None
        results = node.children("results")
    except (ValueError, IndexError):
        return None
    want = normalize(name)
    exact = [r for r in results if r.has("trackName") and isinstance(r.value("trackName"), str)
             and normalize(title_part(r.value("trackName"))) == want]
    count = node.literal("resultCount") if node.has("resultCount") else "not shown"
    return count, len(results), exact


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

def check_domain(name, tld, fetch=get):
    result = fetch(RDAP_BASE + "%s.%s" % (label(name), tld), True)
    verdict = domain_verdict(result)
    excerpts = rdap_excerpts(result.body) if verdict == REGISTERED else []
    if verdict == REGISTERED and excerpts is None:
        verdict, excerpts = UNCONFIRMED, []
    return result, verdict, excerpts


def check_handle(platform, name, fetch=get):
    base = {"x": X_BASE, "instagram": INSTAGRAM_BASE, "tiktok": TIKTOK_BASE}[platform]
    suffix = "/" if platform == "instagram" else ""
    result = fetch(base + urllib.parse.quote(name.lower()) + suffix, False)
    return result, handle_verdict(platform, result)


def itunes_url(name, limit):
    return ITUNES_SEARCH + "?" + urllib.parse.urlencode({"term": name, "entity": "software", "limit": limit})


def report(name, tlds, platforms, limit, variations, countries, fetch=get, env=None):
    lines = ['## Brand name check: "%s"' % name, "",
             "Scope: public lookups at the stated check times. A check time is when the source answered, "
             "not a guarantee the name stays free. Nothing was registered or reserved.", ""]

    lines += ["### Domains", "", "| Domain | Result | HTTP status | Checked (UTC) |", "| --- | --- | --- | --- |"]
    domain_rows = [(tld, check_domain(name, tld, fetch)) for tld in tlds]
    for tld, (res, verdict, _) in domain_rows:
        lines.append("| %s.%s | %s | %s | %s |" % (label(name), tld, verdict, status_text(res), res.checked))
    lines += ["", "Evidence:", ""]
    for tld, (res, verdict, excerpts) in domain_rows:
        evidence(lines, "%s.%s: %s." % (label(name), tld, verdict), res,
                 "[body not read: a 404 body is never read]" if res.status == 404 else "[body not read]",
                 excerpts)

    lines += ["### Handles", "", "| Platform | Handle | Result | HTTP status | Checked (UTC) |",
              "| --- | --- | --- | --- | --- |"]
    handle_rows = []
    for platform in platforms:
        if not valid_handle(platform, name):
            lines.append("| %s | %s | not checked: not a valid %s handle | - | - |" % (platform, name, platform))
            continue
        res, verdict = check_handle(platform, name, fetch)
        handle_rows.append((platform, res, verdict))
        lines.append("| %s | %s | %s | %s | %s |" % (platform, name, verdict, status_text(res), res.checked))
    if any(p in ("instagram", "tiktok") for p in platforms):
        lines += ["", "Instagram and TikTok answer real and invented names with the same login wall, so a 200 "
                  "there is reported as could not confirm, never as available."]
    lines += ["", "Evidence:", ""]
    for platform, res, verdict in handle_rows:
        evidence(lines, "%s %s: %s." % (platform, name, verdict), res, "[body not read: the status is the evidence]")

    lines += ["### App stores", ""]
    res = fetch(itunes_url(name, limit), True)
    parsed = itunes_matches(res.body, name) if res.status == 200 and res.body is not None else None
    if parsed is None:
        lines.append("| App Store | could not confirm | %s | %s |" % (status_text(res), res.checked))
        lines.append("")
        evidence(lines, "App Store search: could not confirm (no readable search response).", res, "[no body]")
    else:
        count, returned, exact = parsed
        lines.append("App Store (iTunes Search API), checked %s: %d exact name match(es) among %d result(s) "
                     "returned (resultCount as shown: %s, limit %d)." % (res.checked, len(exact), returned, count, limit))
        lines.append("")
        for r in exact:
            shown = ", ".join("%s %s" % (k, inline(r.literal(k))) for k in ("trackName", "sellerName", "trackViewUrl")
                              if r.has(k))
            lines.append("- Exact match: %s" % shown)
            lines.append("  Source: <%s>" % res.url)
            lines.append("")
            lines.append(fenced("\n".join(r.excerpt(k) for k in ("trackName", "sellerName", "trackViewUrl") if r.has(k))))
            lines.append("")
        claim = ("App Store search returned %d result(s); %d exact name match(es) as listed above."
                 % (returned, len(exact)))
        evidence(lines, claim, res, "")
    lines += ["Google Play: out of scope. Google Play has no official public search API, so it was not checked.", ""]

    lines += uspto_trademarks.section(name, countries, env)

    if variations:
        lines += ["### Variations", ""]
        listed = 0
        for pattern in VARIATION_PATTERNS:
            if listed >= variations:
                break
            cand = pattern.format(label(name).replace("-", ""))
            if not valid_handle("x", cand):
                continue
            domains = [check_domain(cand, tld, fetch) for tld in tlds]
            x_res, x_verdict = check_handle("x", cand, fetch)
            if all(v == NOT_REGISTERED for _, v, _ in domains) and x_verdict == NO_ACCOUNT:
                listed += 1
                lines.append("- %s: free on every checked domain (%s) and on X." % (
                    cand, ", ".join("%s.%s" % (cand, t) for t in tlds)))
                lines.append("")
                for (dres, dverdict, _), tld in zip(domains, tlds):
                    evidence(lines, "%s.%s: %s." % (cand, tld, dverdict), dres, "[body not read: a 404 body is never read]")
                evidence(lines, "x %s: %s." % (cand, x_verdict), x_res, "[body not read: the status is the evidence]")
        if not listed:
            lines += ["No candidate variation verified free on every checked domain and on X, so none is suggested.", ""]

    lines += ["Trademark results are a starting point, not legal advice.",
              "No searched name was registered or reserved by the agent.", ""]
    return "\n".join(lines)


def parser():
    p = argparse.ArgumentParser(description="Brand Name Checker: domains, handles, app store, trademarks.")
    p.add_argument("names", nargs="+", help="candidate names")
    p.add_argument("--tlds", default="com", help="comma separated domain extensions (default com)")
    p.add_argument("--platforms", default=",".join(PLATFORMS), help="comma separated: x,instagram,tiktok")
    p.add_argument("--app-limit", type=int, default=50, help="iTunes Search results to fetch (default 50)")
    p.add_argument("--variations", type=int, default=0, help="suggest up to N verified free variations")
    p.add_argument("--trademark-countries", default="US", help="comma separated country codes (default US)")
    return p


def main(argv=None, fetch=get, env=None):
    args = parser().parse_args(argv)
    try:
        tlds = [t.strip().lower().lstrip(".") for t in args.tlds.split(",") if t.strip()]
        platforms = [p.strip().lower() for p in args.platforms.split(",") if p.strip()]
        countries = [c.strip().upper() for c in args.trademark_countries.split(",") if c.strip()]
        bad = [t for t in tlds if not re.fullmatch(r"[a-z0-9-]{2,63}", t)]
        if bad or not tlds:
            raise ValueError("bad domain extension(s): %s" % (", ".join(bad) or "none given"))
        unknown = [p for p in platforms if p not in PLATFORMS]
        if unknown:
            raise ValueError("unknown platform(s): %s" % ", ".join(unknown))
        if not 1 <= args.app_limit <= 200:
            raise ValueError("--app-limit must be 1 to 200")
        if args.variations < 0:
            raise ValueError("--variations must be 0 or more")
        for n in args.names:
            if not label(n):
                raise ValueError("name has no letters or digits: %r" % n)
    except ValueError as err:
        print("error: %s" % err, file=sys.stderr)
        return 2
    out = [report(n, tlds, platforms, args.app_limit, args.variations, countries, fetch, env) for n in args.names]
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
