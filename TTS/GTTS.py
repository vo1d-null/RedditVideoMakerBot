import random

from gtts import gTTS

from utils import settings


class GTTS:
    def __init__(self):
        self.max_chars = 5000
        self.voices = ['en-US-Chirp-HD-D', 'en-US-Studio-O', 'en-US-Chirp-HD-O', 'en-US-Chirp-HD-F',]

    def run(self, text, filepath, random_voice=None):
        tts = gTTS(
            text=text,
            lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
            slow=False,
        )
        tts.save(filepath)

    def random_voice(self):
        return random.choice(self.voices)
