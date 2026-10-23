"""The job's content rules as a screen run before any generation (issue #78).

Rules quoted from the job description (issue #78, comment 6366897388):

  - Do not create images, video or voices of real, identifiable people unless
    the buyer confirms they are that person or have their consent.
  - Do not create copyrighted characters, or logos and brands the buyer
    doesn't own.
  - Do not create sexual content, graphic violence, or content meant to
    deceive (for example, fake news footage).
  - When a request breaks a rule, decline that part and explain why in the
    report.

Plus the buyer's rights confirmation for reference material (job
description, Roles: the buyer "confirms they have the rights to any
reference material").

How it screens: the brief's own declarations (depicts_real_person with
person_consent, brand_owned, rights_confirmed) and a stated keyword list
over the subject, style, brand and script. A keyword list cannot recognise
every real person, character or brand by name; it catches the categories
the brief names in words ("celebrity", "logo", "fake news") and a short
list of well known characters and brands. A live build adds the chosen
providers' own moderation and a name recognition step; that is not built
here, and README.md says so.
"""

import re

REAL_PERSON_WORDS = ("celebrity", "celebrities", "famous person", "famous actor", "famous singer", "movie star",
                     "pop star", "politician", "president", "prime minister", "influencer", "real person",
                     "public figure", "royal family", "athlete named", "lookalike", "look-alike")
CHARACTER_NAMES = ("mickey mouse", "minnie mouse", "donald duck", "spider-man", "spiderman", "superman", "batman",
                   "wonder woman", "iron man", "pikachu", "pokemon", "darth vader", "yoda", "harry potter",
                   "mario", "luigi", "sonic the hedgehog", "elsa", "shrek", "homer simpson", "bugs bunny",
                   "hello kitty", "spongebob")
BRAND_WORDS = ("logo", "trademark", "brand mark", "nike", "adidas", "coca-cola", "coca cola", "pepsi", "starbucks",
               "mcdonald*", "apple logo", "google logo", "disney", "louis vuitton", "gucci", "chanel", "rolex")
SEXUAL_WORDS = ("nude", "naked", "nsfw", "explicit", "sexual", "porn", "erotic", "topless", "lingerie model")
VIOLENCE_WORDS = ("gore", "gory", "graphic violence", "dismember*", "decapitat*", "beheading", "mutilat*",
                  "bloody corpse", "torture")
DECEPTIVE_WORDS = ("fake news", "deepfake", "deep fake", "fake footage", "hoax", "fabricated evidence",
                   "pretend to be", "impersonat*", "fake receipt", "fake id", "as if real news")


def _text(job):
    parts = [job.subject, job.style, job.brand, job.script]
    return " " + re.sub(r"\s+", " ", " ".join(p for p in parts if p).lower()) + " "


def _hits(text, words):
    """Whole word or phrase matches; an entry ending in * is a stem that
    matches any ending (decapitat* matches decapitated and decapitation)."""
    found = []
    for w in words:
        if w.endswith("*"):
            pattern = r"(?<![a-z0-9])" + re.escape(w[:-1])
        else:
            pattern = r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.append(w.rstrip("*"))
    return found


def screen(job):
    """A list of (rule, reason) the request breaks; empty when it may go ahead."""
    text = _text(job)
    out = []
    if job.references and not job.rights_confirmed:
        out.append(("reference rights", "the brief includes %d reference item(s) but rights_confirmed is not true; "
                    "reference based work needs the buyer's confirmation that they hold the rights to that "
                    "material" % len(job.references)))
    person_words = _hits(text, REAL_PERSON_WORDS)
    if (job.depicts_real_person or person_words) and not job.person_consent:
        why = ("the brief declares a real, identifiable person" if job.depicts_real_person
               else "the brief names a real, identifiable person (%s)" % ", ".join(person_words))
        out.append(("real person without consent", why + ", and person_consent is not true: the buyer must confirm "
                    "they are that person or have their consent"))
    chars = _hits(text, CHARACTER_NAMES)
    if chars:
        out.append(("copyrighted character", "the brief names a copyrighted character (%s); this agent does not "
                    "create copyrighted characters" % ", ".join(chars)))
    brands = _hits(text, BRAND_WORDS)
    if brands and not job.brand_owned:
        out.append(("brand or logo not owned", "the brief names a logo or brand (%s) and brand_owned is not true; "
                    "logos and brands are created only after the buyer confirms ownership" % ", ".join(brands)))
    for rule, words in (("sexual content", SEXUAL_WORDS), ("graphic violence", VIOLENCE_WORDS),
                        ("deceptive content", DECEPTIVE_WORDS)):
        hits = _hits(text, words)
        if hits:
            out.append((rule, "the brief asks for %s (%s); this agent does not create it" % (rule, ", ".join(hits))))
    return out
