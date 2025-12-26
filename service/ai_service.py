import os
import tempfile
from typing import List, Dict, Any
# from dotenv import load_dotenv
#
# import ffmpeg
# import whisper
# from transformers import pipeline
#
# import numpy as np
# import librosa
# import onnxruntime as ort
# from  utils.stt_converter import DEPRESSION_WEIGHTS, ANXIETY_WEIGHTS, map_score_to_severity
#

# ---------------------------------------------------------
# Set ffmpeg path
# ---------------------------------------------------------
# load_dotenv()
# FFMPEG_PATH = os.getenv("FFMPEG_PATH")
# if FFMPEG_PATH:
#     os.environ["PATH"] = str(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")
#

# ---------------------------------------------------------
# Load Models Once
# ---------------------------------------------------------
# print("Loading Whisper model...")
# whisper_model = whisper.load_model("small")
#
# print("Loading text emotion model...")
#
# emotion_model = pipeline(
#     "text-classification",
#     model="j-hartmann/emotion-english-distilroberta-base",
#     return_all_scores=True
# )

# print("Loading ONNX Voice Emotion Recognition model...")
# VOICE_EMOTION_ONNX_PATH = "pretrained_models/voice_emotion.onnx"
# voice_ort_session = ort.InferenceSession(VOICE_EMOTION_ONNX_PATH)

VOICE_LABEL_MAP = {
    "Anger": "angry",
    "Disgust": "disgust",
    "Fear": "fear",
    "Sad": "sad",
    "Surprised": "surprise",
    "Happy": "happy",
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
# def convert_to_wav(src_path: str, out_path: str):
#     """Convert audio/video to mono 16k WAV."""
#     stream = ffmpeg.input(src_path)
#     stream = ffmpeg.output(
#         stream, out_path,
#         format="wav", acodec="pcm_s16le",
#         ac=1, ar="16000"
#     )
#     ffmpeg.run(stream, overwrite_output=True)
#

# ---------------------------------------------------------
# SPEECH-TO-TEXT (Whisper)
# ---------------------------------------------------------
# def transcribe_file(path: str) -> str:
#     result = whisper_model.transcribe(path, language="en")
#     return result.get("text", "").strip()
#

# ---------------------------------------------------------
# TEXT EMOTION + KEYWORD MATCHING
# ---------------------------------------------------------

# def analyze_text(text: str, category_name: str):
#     """
#     Analyze text emotions and compute severity based on test category.
#     Returns weighted score, severity, and model confidence.
#     """
#     if not text.strip():
#         raise ValueError("Empty transcript detected from audio")
#     # 1. Run emotion model (multi-label)
#     emotion_results = emotion_model(text[:512])[0]
#
#     # Convert to percentage map
#     emotion_percentages = {
#         e["label"]: float(e["score"]) * 100
#         for e in emotion_results
#     }

    # commented by saqib
    # Convert scores to a confidence map
    # emotion_confidence = {
    #     e["label"]: float(e["score"])
    #     for e in emotion_results
    # }

    # 2. Select emotion weights by category
    # category_name = category_name.lower()
    # if category_name == "depression":
    #     emotion_weights = DEPRESSION_WEIGHTS
    # elif category_name == "anxiety":
    #     emotion_weights = ANXIETY_WEIGHTS
    # else:
    #     raise ValueError("Unsupported test category")

    # 3. Weighted emotion score
    # weighted_score = 0.0
    # used_emotions = {}
    # for emotion, weight in emotion_weights.items():
    #     percent = emotion_percentages.get(emotion, 0.0)
    #     weighted_score += percent * weight
    #     used_emotions[emotion] = percent

    # commented by saqib
    # # 4. Determine severity level
    # severity_level = map_score_to_severity(weighted_score)

    # # 5. Fetch severity weightage from SurveyOption
    # option_weight_map = {
    #     opt["option_text"].lower(): opt["weightage"]
    #     for opt in options_data
    # }

    # severity_weightage = option_weight_map.get(
    #     severity_level,
    #     min(option_weight_map.values())
    # )

    # # 6. Compute overall confidence (average of selected emotions)
    # # You can also compute max or any other metric if preferred


    # selected_emotions = emotion_weights.keys()
    # confidences = [emotion_confidence.get(e, 0.0) for e in selected_emotions]
    # overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # return {
    #     "category": category_name,
    #     "emotion_breakdown": used_emotions,
    #     "weightage": round(weighted_score, 2),
    #     # "severity_level": severity_level,
    #     # "severity_weightage": severity_weightage,
    #     # "model_confidence": round(overall_confidence, 2)  # confidence between 0 and 1
    # }




# ---------------------------------------------------------
# PURE PYTHON SILENCE REMOVAL (NO webrtcvad)
# ---------------------------------------------------------
# def remove_silence_librosa(y: np.ndarray):
#     """Remove leading and trailing silence using librosa only."""
#     y_trimmed, _ = librosa.effects.trim(y, top_db=30)
#     return y_trimmed
#

# ---------------------------------------------------------
# AUDIO CLEANING + NORMALIZATION
# ---------------------------------------------------------
# def preprocess_audio(wav_path: str):
#     y, sr = librosa.load(wav_path, sr=16000, mono=True)
#
#     # Remove start/end silence using librosa
#     y = remove_silence_librosa(y)
#
#     # Normalize audio loudness
#     if np.max(np.abs(y)) > 0:
#         y = y / np.max(np.abs(y))
#
#     # Safety clipping
#     y = np.clip(y, -1.0, 1.0)
#
#     return y, sr


# ---------------------------------------------------------
# SOFTMAX
# ---------------------------------------------------------
# def softmax(x: np.ndarray):
#     exp = np.exp(x - np.max(x))
#     return exp / exp.sum()


# ---------------------------------------------------------
# FINAL — VOICE EMOTION DETECTION (UPDATED)
# # ---------------------------------------------------------
# def analyze_voice_emotion(
#     wav_path: str,
#     category_name: str,
# ) -> dict:


    # 1. Preprocess audio
    # y, sr = preprocess_audio(wav_path)
    #
    # audio_input = y.astype(np.float32)[None, :]
    # input_name = voice_ort_session.get_inputs()[0].name
    #
    # # 2. ONNX inference
    # outputs = voice_ort_session.run(None, {input_name: audio_input})
    # logits = outputs[0][0]
    #
    # # 3. Softmax → probabilities
    # probs = softmax(logits)
    #
    # # 4. Build emotion percentage map
    # emotion_percentages = {}
    #
    # for idx, prob in enumerate(probs):
    #     raw_label = EMOTION_LABELS[idx]
    #     normalized_label = VOICE_LABEL_MAP.get(raw_label)
    #
    #     if normalized_label:
    #         emotion_percentages[normalized_label] = float(prob) * 100
    #
    # # 5. Select emotion weights by category
    # category_name = category_name.lower()
    #
    # if category_name == "depression":
    #     emotion_weights = DEPRESSION_WEIGHTS
    # elif category_name == "anxiety":
    #     emotion_weights = ANXIETY_WEIGHTS
    # else:
    #     raise ValueError("Unsupported test category")
    #
    # # 6. Weighted emotion score
    # weighted_score = 0.0
    # used_emotions = {}
    #
    # for emotion, weight in emotion_weights.items():
    #     percent = emotion_percentages.get(emotion, 0.0)
    #     weighted_score += percent * weight
    #     used_emotions[emotion] = percent

    # commented by saqib
    # 7. Severity level
    # severity_level = map_score_to_severity(weighted_score)

    # # 8. Fetch severity weightage from SurveyOption
    # option_weight_map = {
    #     opt["option_text"].lower(): opt["weightage"]
    #     for opt in options_data
    # }

    # severity_weightage = option_weight_map.get(
    #     severity_level,
    #     min(option_weight_map.values())
    # )

    # return {
    #     "category": category_name,
    #     "emotion_breakdown": used_emotions,
    #     "weightage": round(weighted_score, 2),
    #     # "severity_level": severity_level,
    #     # "severity_weightage": severity_weightage
    # }

