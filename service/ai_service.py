import os
import tempfile
from typing import List, Dict, Any
from dotenv import load_dotenv


import numpy as np
import librosa
import onnxruntime as ort
from  utils.stt_converter import DEPRESSION_WEIGHTS, ANXIETY_WEIGHTS


# ---------------------------------------------------------
# Set ffmpeg path
# ---------------------------------------------------------
load_dotenv()

# to skip all heavy imports, at start up, make true in .env to import
ENABLE_AI = os.getenv("ENABLE_AI_MODELS", "false").lower() == "true"

FFMPEG_PATH = os.getenv("FFMPEG_PATH")
if FFMPEG_PATH:
    os.environ["PATH"] = str(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")



# global variables
whisper_model = None
emotion_model = None
voice_ort_session = None

# ---------------------------------------------------------
# Load Models only when .env becomes true
# ---------------------------------------------------------
if ENABLE_AI:
    import whisper
    import ffmpeg
    import librosa
    import onnxruntime as ort
    from transformers import pipeline
    from utils.stt_converter import DEPRESSION_WEIGHTS, ANXIETY_WEIGHTS

    print("AI Mode Enabled: Loading Models...")
    whisper_model = whisper.load_model("small")

    emotion_model = pipeline(
        task="text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None
    )

    VOICE_EMOTION_ONNX_PATH = "pretrained_models/voice_emotion.onnx"
    voice_ort_session = ort.InferenceSession(VOICE_EMOTION_ONNX_PATH)
else:
    print("AI Mode Disabled: Skipping heavy model loads.")

VOICE_LABEL_MAP = {
    "Anger": "anger",
    "Disgust": "disgust",
    "Fear": "fear",
    "Sad": "sadness",
    "Surprised": "surprise",
    "Happy": "joy",
    "Neutral": "neutral",
    "Calm": "neutral"
}

EMOTION_LABELS = [
    "Anger", "Calm", "Disgust", "Fear",
    "Happy", "Neutral", "Sad", "Surprised"
]




# ---------------------------------------------------------
# AUDIO CONVERSION helper
# ---------------------------------------------------------
def convert_to_wav(src_path: str, out_path: str):
    """Convert audio/video to mono 16k WAV."""
    stream = ffmpeg.input(src_path)
    stream = ffmpeg.output(
        stream, out_path,
        format="wav", acodec="pcm_s16le",
        ac=1, ar="16000"
    )
    ffmpeg.run(stream, overwrite_output=True)


# ---------------------------------------------------------
# SPEECH-TO-TEXT (Whisper)
# ---------------------------------------------------------
def transcribe_file(path: str) -> str:
    try:
        result = whisper_model.transcribe(
            path,
            fp16=False,
            language=None,
            temperature=0.0  # more deterministic
        )
        text = result.get("text", "").strip()

        if not text:
            raise ValueError("Whisper returned empty transcript")

        return text

    except Exception as e:
        raise RuntimeError(f"Speech-to-text failed: {str(e)}")



# ---------------------------------------------------------
# TEXT EMOTION + KEYWORD MATCHING
# ---------------------------------------------------------

def analyze_text(text: str, category_name: str) -> dict:

    if not text.strip():
        raise ValueError("Empty transcript detected from audio")

    try:
        emotion_results = emotion_model(text[:512])
        print("DEBUG RAW:", emotion_results)

        # Normalize HuggingFace output
        if isinstance(emotion_results, list) and len(emotion_results) > 0:
            if isinstance(emotion_results[0], list):
                emotion_results = emotion_results[0]
            elif isinstance(emotion_results[0], dict):
                emotion_results = emotion_results
        elif isinstance(emotion_results, dict):
            emotion_results = [emotion_results]
        else:
            raise ValueError(f"Unexpected model output: {emotion_results}")

    except Exception as e:
        raise RuntimeError(f"Text emotion model failed: {str(e)}")

    emotion_percentages = {}

    print("\n------ Emotion Percentages ------")

    for e in emotion_results:
        if not isinstance(e, dict):
            print("Skipping invalid element:", e)
            continue

        label = e.get("label", "").lower()
        score = float(e.get("score", 0)) * 100

        emotion_percentages[label] = score
        print(f"{label}: {score:.2f}%")

    print("---------------------------------\n")

    category_name = category_name.lower()

    if category_name == "depression":
        emotion_weights = DEPRESSION_WEIGHTS
    elif category_name == "anxiety":
        emotion_weights = ANXIETY_WEIGHTS
    else:
        raise ValueError("Unsupported test category")

    weighted_score = 0.0
    used_emotions = {}

    for emotion, weight in emotion_weights.items():
        percent = emotion_percentages.get(emotion.lower(), 0.0)
        weighted_score += percent * weight
        used_emotions[emotion] = percent

    return {
        "category": category_name,
        "emotion_breakdown": used_emotions,
        "weightage": round(weighted_score, 2),
    }


    # ---------------------------------------------------------
    # SOFTMAX
    # ---------------------------------------------------------
def softmax(x: np.ndarray):
    exp = np.exp(x - np.max(x))
    return exp / exp.sum()


    # ---------------------------------------------------------
    # FINAL — VOICE EMOTION DETECTION (UPDATED)
    # ---------------------------------------------------------
def analyze_voice_emotion(
    wav_path: str,
    category_name: str,
) -> dict:
    """
    Analyze voice emotions and compute severity based on test category.
    """

    # 1. Load audio
    y, sr = librosa.load(wav_path, sr=16000, mono=True)

    # 🔹 Remove leading/trailing silence
    y, _ = librosa.effects.trim(y, top_db=30)

    # 🔹 Normalize (VERY IMPORTANT)
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val

    if y is None or len(y) == 0:
        raise ValueError("Audio contains no speech after silence removal")

    window_size = 16000 * 3
    hop = 16000

    all_probs = []

    # 3. Pad short audio
    if len(y) < window_size:
        y = np.pad(y, (0, window_size - len(y)))

    # 4. Sliding window inference
    for i in range(0, len(y) - window_size + 1, hop):
        chunk = y[i:i + window_size].astype(np.float32)[None, :]

        outputs = voice_ort_session.run(
            None,
            {voice_ort_session.get_inputs()[0].name: chunk}
        )

        probs = softmax(outputs[0][0])
        all_probs.append(probs)

    if len(all_probs) == 0:
        raise ValueError("No valid speech windows found")

    avg_probs = np.mean(np.vstack(all_probs), axis=0)

    # 5. Build emotion percentage map
    emotion_percentages = {}

    for label, prob in zip(EMOTION_LABELS, avg_probs):
        normalized_label = VOICE_LABEL_MAP.get(label)
        if normalized_label:
            emotion_percentages[normalized_label] = float(prob) * 100

    # 6. Select emotion weights
    category_name = category_name.lower()

    if category_name == "depression":
        emotion_weights = DEPRESSION_WEIGHTS
    elif category_name == "anxiety":
        emotion_weights = ANXIETY_WEIGHTS
    else:
        raise ValueError("Unsupported test category")

    # 7. Compute weighted score
    weighted_score = 0.0
    used_emotions = {}

    for emotion, weight in emotion_weights.items():
        percent = emotion_percentages.get(emotion, 0.0)
        weighted_score += percent * weight
        used_emotions[emotion] = percent

    return {
        "category": category_name,
        "emotion_breakdown": used_emotions,
        "weightage": round(weighted_score, 2),
    }

 