import io

from gtts import gTTS


def text_to_audio_bytes(text: str) -> bytes:
    tts = gTTS(text=text, lang="en")

    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()