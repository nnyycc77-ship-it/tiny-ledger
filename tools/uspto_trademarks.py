"""USPTO trademark leg for the Brand Name Checker (issue #125).

The checker's trademark section comes from section() here. Until a live
keyed run exists, the section is today's honest wording, byte for byte:
"Not covered", the database it would search, the countries requested.

Key: read from the environment variable USPTO_API_KEY and from nowhere
else. It is never printed, logged or written, and never placed in a URL
this module prints. No key: the section is unchanged.

Not yet grounded: the USPTO developer API's search request (endpoint,
parameters, how the key is sent) and its response shape. This repo does
not record that documentation, and the build environment cannot reach
any USPTO host, so the coordinator was asked for captures on issue #125
(comment 6371843076). Until SEARCH is filled from those captures, a key
alone changes nothing: section() keeps the unconfirmed wording and says
on stderr why the keyed search did not run. The code existing never
upgrades the leg; only a live keyed run does.

Standard library only.
"""

import os
import sys

KEY_ENV = "USPTO_API_KEY"

# Today's wording, moved here unchanged from brand_name_checker.report().
UNCONFIRMED = ("Not covered. No working trademark source has been captured for this tool, so no trademark search "
               "was run and no mark or status is stated. The database it would search: USPTO trademark search "
               "(United States). Countries requested: %s.")

# The documented search request and response reader. None until the USPTO
# developer API documentation is captured and quoted (issue #125).
SEARCH = None


def read_key(env=None):
    """The key from USPTO_API_KEY, stripped, or None when absent or empty."""
    env = os.environ if env is None else env
    value = env.get(KEY_ENV, "").strip()
    return value or None


def unconfirmed_lines(countries):
    return ["### Trademarks", "", UNCONFIRMED % ", ".join(countries), ""]


def section(name, countries, env=None, stderr=None):
    """The report's trademark section as a list of lines."""
    key = read_key(env)
    if key is None:
        return unconfirmed_lines(countries)
    if SEARCH is None:
        stderr = sys.stderr if stderr is None else stderr
        stderr.write("note: %s is set, but the USPTO search request is not documented in this repo yet "
                     "(issue #125); the trademark leg stays not covered.\n" % KEY_ENV)
        return unconfirmed_lines(countries)
    raise NotImplementedError("keyed USPTO search: wired once its documentation is captured (issue #125)")
