"""Voice providers: the offline stub and the live slot."""

import os

from mediagen_providers import placeholder
from mediagen_providers.base import Capabilities, LiveSlot, Output, Provider


class StubVoice(Provider):
    """Writes labelled placeholder WAV tones offline. Not speech. It records
    the script it was given in the file's metadata, which is what the
    word for word check reads."""

    name = "stub-voice"
    media_type = "voice"
    capabilities = Capabilities(formats=("wav",), max_seconds=60, max_count=4, follows_references=False,
                                voices=("stock-warm-female", "stock-calm-male"), offline=True,
                                model="placeholder-wav-1", commercial_use=True)

    def generate(self, job, out_dir, attempt):
        outputs = []
        for i in range(job.count):
            path = os.path.join(out_dir, "%s-%d-attempt%d.wav" % (job.slug, i + 1, attempt))
            placeholder.wav_voice(path, job.seconds, job.prompt, seed=i + 100 * attempt + job.seed, script=job.script)
            outputs.append(Output(path, "wav", job.prompt, self.name, placeholder=True, model=self.capabilities.model))
        return outputs


class LiveVoiceSlot(LiveSlot):
    name = "live-voice"
    media_type = "voice"
    capabilities = Capabilities(formats=("wav", "mp3"), max_seconds=300, max_count=4, follows_references=True,
                                voices=(), offline=False, model="(chosen at award)", commercial_use=None)
    key_env = "MEDIAGEN_VOICE_KEY"
