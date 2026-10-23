"""Provider modules for the media generator (issue #78).

One interface for every provider:

    provider.name            short id, e.g. "stub-image"
    provider.media_type      "image", "video" or "voice"
    provider.capabilities    dict the router's rules read (see base.Capabilities)
    provider.configured(env) (True, "") or (False, reason); a provider that is
                             not configured is never routed to
    provider.generate(job, out_dir, attempt) -> list of Output

image.py, video.py and voice.py each hold the offline stub provider for that
media type and a slot for a live provider. The live slots are interfaces
only in this build: they report not configured, and generate() refuses.
No live provider is called anywhere in this folder.
"""

from mediagen_providers.base import (  # noqa: F401
    Capabilities, NotConfigured, Output, Provider, ProviderError,
)
from mediagen_providers import image, video, voice  # noqa: F401


def all_providers():
    """Every provider known to this build, in a fixed order."""
    return [image.StubImage(), image.StubImageRefs(), image.LiveImageSlot(),
            video.StubVideo(), video.LiveVideoSlot(),
            voice.StubVoice(), voice.LiveVoiceSlot()]
