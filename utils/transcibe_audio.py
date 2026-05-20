import io
import asyncio
from faster_whisper import WhisperModel

# Load model once at startup
# "base" is a good balance. If CPU is slow, use "tiny".
# device="cpu" is standard; compute_type="int8" makes it much faster on CPU.
model = WhisperModel("base", device="cpu", compute_type="int8")


async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribes raw bytes using Faster-Whisper.
    """
    # Use io.BytesIO to treat bytes like a file
    audio_file = io.BytesIO(audio_bytes)

    # We use run_in_executor to prevent blocking the FastAPI event loop
    loop = asyncio.get_event_loop()

    def run_whisper():
        # beam_size=5 is standard for accuracy
        segments, info = model.transcribe(audio_file, beam_size=5)
        # Join all transcribed segments into a single string
        return " ".join([segment.text for segment in segments]).strip()

    result_text = await loop.run_in_executor(None, run_whisper)
    return result_text