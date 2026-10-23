"""USPTO trademark leg for the Brand Name Checker (issue #125).

The checker's trademark section comes from section() here. Until a live
keyed run of a documented name search exists, the section is today's
honest wording, byte for byte: "Not covered", the database it would
search, the countries requested.

Key: read from the environment variable USPTO_API_KEY and from nowhere
else. It is never printed, logged or written. No key: the section is
unchanged.

What is on record (coordinator captures and ruling on issue #125, comment
6372123640, quoting the USPTO page "Trademark bulk data"): the keyed USPTO
route is TSDR, which answers case status, documents and images for a known
case number; the key is registered through a USPTO.gov account. No
official keyed endpoint that takes a candidate name and returns exact and
near matches is on record, so no endpoint, header, rate limit or response
schema is written here. The request builder and the response reader are
NOT DOCUMENTED: both refuse to run, and with a key present section() says
so on stderr and keeps the unconfirmed wording. A key alone therefore
never produces a trademark claim; only a documented endpoint plus a live
keyed run can switch the leg on.

Standard library only.
"""

import os
import sys

KEY_ENV = "USPTO_API_KEY"

# Today's wording, moved here unchanged from brand_name_checker.report().
UNCONFIRMED = ("Not covered. No working trademark source has been captured for this tool, so no trademark search "
               "was run and no mark or status is stated. The database it would search: USPTO trademark search "
               "(United States). Countries requested: %s.")

NOT_DOCUMENTED = ("no documented USPTO trademark name search is on record (issue #125: the keyed route on record, "
                  "TSDR, answers status by case number, not by name)")


class NotDocumented(Exception):
    """The USPTO request or response shape is not recorded in this repo. Nothing was sent."""


def read_key(env=None):
    """The key from USPTO_API_KEY, stripped, or None when absent or empty."""
    env = os.environ if env is None else env
    value = env.get(KEY_ENV, "").strip()
    return value or None


def build_search_request(name, key):
    """NOT DOCUMENTED: the keyed name search request. Refuses to run."""
    raise NotDocumented("search request: " + NOT_DOCUMENTED)


def read_search_response(body):
    """NOT DOCUMENTED: the name search response reader. Refuses to run."""
    raise NotDocumented("search response: " + NOT_DOCUMENTED)


def unconfirmed_lines(countries):
    return ["### Trademarks", "", UNCONFIRMED % ", ".join(countries), ""]


def section(name, countries, env=None, stderr=None):
    """The report's trademark section as a list of lines.

    No key: today's wording. A key: the request builder refuses (NOT
    DOCUMENTED), the refusal goes to stderr without the key, and the
    section keeps today's wording.
    """
    key = read_key(env)
    if key is None:
        return unconfirmed_lines(countries)
    stderr = sys.stderr if stderr is None else stderr
    try:
        build_search_request(name, key)
    except NotDocumented as err:
        stderr.write("note: %s is set, but the keyed search did not run: %s. The trademark leg stays not "
                     "covered.\n" % (KEY_ENV, err))
        return unconfirmed_lines(countries)
    raise NotDocumented("search request built without a documented shape; refusing to continue")
