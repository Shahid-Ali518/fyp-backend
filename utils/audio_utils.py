
import librosa
import io
import soundfile as sf

TARGET_SR = 16000

def load_audio(file_path: str):
    audio, _ = librosa.load(file_path, sr=TARGET_SR, mono=True)
    return audio.astype("float32")



def clean_audio_librosa(audio_path):
    # 1. Load audio (16kHz for Wav2Vec2)
    y, sr = librosa.load(audio_path, sr=16000)

    y_filt = librosa.effects.preemphasis(y)
    y_trimmed, _ = librosa.effects.trim(y_filt, top_db=25)

    if len(y_trimmed) > 0:
        y_final = librosa.util.normalize(y_trimmed)
    else:
        y_final = y_trimmed

    return y_final


import os


# method to convert audio to bytes
def convert_audio_to_bytes(file_path: str) -> bytes:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at: {file_path}")

    with open(file_path, "rb") as audio_file:
        binary_data = audio_file.read()

    return binary_data

# method to convert audio numpy array into bytes
def convert_array_to_bytes(audio_array, sample_rate=16000):
    # Create an in-memory file-like object
    byte_io = io.BytesIO()

    # Write the numpy array to the memory buffer as a WAV file
    sf.write(byte_io, audio_array, sample_rate, format='WAV')

    # Get the actual bytes from the buffer
    return byte_io.getvalue()