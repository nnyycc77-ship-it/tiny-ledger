#!/usr/bin/env python3
"""OFAC sanctions list name check (issue #160, tool factory wave 1).

Given a person or company name, checks it against the US Treasury OFAC
Specially Designated Nationals (SDN) list and prints the result in the
delivery format from AGENT-BRIEF.md: claim lines, the exact source URL,
the UTC retrieval time, and every matching list entry as a verbatim
transcript of the list's own lines.

Matching rule, stated in every report: names are compared after folding
case and replacing every character that is not a letter or digit with a
space. An exact match is the whole normalised query equal to the whole
normalised list name; a contains match is the normalised query appearing
in the normalised list name as whole words. No fuzzy or phonetic score is
computed or claimed.

NOT DOCUMENTED YET: the SDN list's download URL, file format and alias
file are not recorded in this repo and the build environment cannot
reach any OFAC host, so they were asked of the coordinator on issue #160
(comment 6378135614). Until they are captured, fetching and parsing
refuse to run (NotDocumented); nothing about the list is invented here.

Standard library only.
"""

import re
import sys


class NotDocumented(Exception):
    """The SDN source shape is not recorded in this repo. Nothing was fetched."""


def normalise(text):
    """Case folded, every non letter or digit a single space, trimmed."""
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text.casefold()).split())


def match_kind(query, list_name):
    """'exact', 'contains' (whole words) or None."""
    q, n = normalise(query), normalise(list_name)
    if not q:
        return None
    if q == n:
        return "exact"
    if (" %s " % q) in (" %s " % n):
        return "contains"
    return None


def fetch_list():
    raise NotDocumented("the SDN list download URL is not recorded in this repo yet (issue #160)")


def parse_list(body):
    raise NotDocumented("the SDN list file format is not recorded in this repo yet (issue #160)")


def main(argv=None):
    sys.stderr.write("error: not documented yet: the SDN source shape awaits capture on issue #160\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
