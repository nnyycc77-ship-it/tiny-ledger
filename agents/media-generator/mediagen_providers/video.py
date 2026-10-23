"""Short video providers: the offline stub and the live slot."""

import os

from mediagen_providers import placeholder
from mediagen_providers.base import Capabilities, LiveSlot, Output, Provider
from mediagen_providers.image import stub_size

ASPECT_SIZES = {"1:1": (48, 48), "16:9": (64, 36), "9:16": (36, 64)}
STUB_FPS = 5
STUB_MAX_SIDE = 256


class StubVideo(Provider):
    """Writes labelled placeholder animated GIFs offline. Not generated video."""

    name = "stub-video"
    media_type = "video"
    capabilities = Capabilities(formats=("gif",), aspects=tuple(ASPECT_SIZES), max_seconds=10, max_count=3,
                                follows_references=False, offline=True, model="placeholder-gif-1",
                                commercial_use=True, max_side=STUB_MAX_SIDE)

    def generate(self, job, out_dir, attempt):
        width, height = stub_size(job, ASPECT_SIZES)
        outputs = []
        for i in range(job.count):
            path = os.path.join(out_dir, "%s-%d-attempt%d.gif" % (job.slug, i + 1, attempt))
            placeholder.gif_video(path, width, height, job.seconds, STUB_FPS, job.prompt, seed=i + 100 * attempt + job.seed)
            outputs.append(Output(path, "gif", job.prompt, self.name, placeholder=True, model=self.capabilities.model))
        return outputs


class LiveVideoSlot(LiveSlot):
    name = "live-video"
    media_type = "video"
    capabilities = Capabilities(formats=("mp4", "gif"), aspects=tuple(ASPECT_SIZES), max_seconds=30, max_count=2,
                                follows_references=True, offline=False, model="(chosen at award)",
                                commercial_use=None, max_side=None)
    key_env = "MEDIAGEN_VIDEO_KEY"
