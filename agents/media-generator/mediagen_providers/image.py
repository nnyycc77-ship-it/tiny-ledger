"""Image providers: the offline stub and the live slot."""

import os

from mediagen_providers import placeholder
from mediagen_providers.base import Capabilities, LiveSlot, Output, Provider

ASPECT_SIZES = {"1:1": (64, 64), "16:9": (96, 54), "9:16": (54, 96), "4:3": (80, 60), "3:4": (60, 80)}


class StubImage(Provider):
    """Writes labelled placeholder PNGs offline. Not generated media."""

    name = "stub-image"
    media_type = "image"
    capabilities = Capabilities(formats=("png",), aspects=tuple(ASPECT_SIZES), max_count=8,
                                follows_references=False, offline=True)

    def generate(self, job, out_dir, attempt):
        width, height = ASPECT_SIZES[job.aspect]
        outputs = []
        for i in range(job.count):
            path = os.path.join(out_dir, "%s-%d-attempt%d.png" % (job.slug, i + 1, attempt))
            placeholder.png_image(path, width, height, job.prompt, seed=i + 100 * attempt)
            outputs.append(Output(path, "png", job.prompt, self.name, placeholder=True))
        return outputs


class StubImageRefs(StubImage):
    """The same placeholder writer, declared as reference following, so the
    router has an offline image provider for reference based briefs. It does
    not read the reference files; the delivery note says so."""

    name = "stub-image-refs"
    capabilities = Capabilities(formats=("png",), aspects=tuple(ASPECT_SIZES), max_count=4,
                                follows_references=True, offline=True)


class LiveImageSlot(LiveSlot):
    name = "live-image"
    media_type = "image"
    capabilities = Capabilities(formats=("png", "jpg", "webp"), aspects=tuple(ASPECT_SIZES), max_count=4,
                                follows_references=True, offline=False)
    key_env = "MEDIAGEN_IMAGE_KEY"
