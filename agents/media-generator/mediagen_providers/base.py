"""The provider interface shared by image.py, video.py and voice.py."""


class ProviderError(Exception):
    """A provider failed to produce output. Nothing is delivered from it."""


class NotConfigured(ProviderError):
    """A provider slot has no live backend in this build, or lacks its key."""


class Capabilities(object):
    """What a provider can do, as the router's rules read it.

    formats            output formats, e.g. ("png",)
    aspects            supported aspect ratios, e.g. ("1:1", "16:9", "9:16")
    max_seconds        longest video or voice length; None for images
    max_count          most outputs per call
    follows_references whether reference material can steer the output
    voices             voice ids offered (voice providers only)
    offline            True when it runs locally with no network and no key
    model              the model id the provider reports for its output
    commercial_use     True when the provider's terms, as recorded by the
                       operator, allow commercial use and resale of the output;
                       False excludes the provider; None means not recorded
    max_side           largest width or height in pixels (image and video)
    """

    def __init__(self, formats, aspects=(), max_seconds=None, max_count=4,
                 follows_references=False, voices=(), offline=False, model="", commercial_use=None,
                 max_side=None):
        self.formats = tuple(formats)
        self.aspects = tuple(aspects)
        self.max_seconds = max_seconds
        self.max_count = max_count
        self.follows_references = follows_references
        self.voices = tuple(voices)
        self.offline = offline
        self.model = model
        self.commercial_use = commercial_use
        self.max_side = max_side


class Output(object):
    """One file a provider produced, with what it says it made."""

    def __init__(self, path, media_format, prompt, provider, placeholder, model=""):
        self.path = path
        self.format = media_format
        self.prompt = prompt
        self.provider = provider
        self.placeholder = placeholder
        self.model = model


class Provider(object):
    name = "base"
    media_type = None
    capabilities = Capabilities(formats=())
    key_env = None  # environment variable a live provider would read its key from

    def configured(self, env):
        return True, ""

    def generate(self, job, out_dir, attempt):
        raise NotImplementedError


class LiveSlot(Provider):
    """A slot for a live provider, chosen and wired by the operator at award.

    In this build it is never configured: no vendor is chosen, no request
    shape is written, and no key is read. It exists so the router's rules and
    the delivery note already account for a live provider, and so wiring one
    in is a new class here rather than a change to the pipeline.
    """

    def configured(self, env):
        return False, ("live %s provider slot: no vendor is wired in this build; wiring one and its key is an "
                       "operator decision at award" % self.media_type)

    def generate(self, job, out_dir, attempt):
        raise NotConfigured(self.configured({})[1])
