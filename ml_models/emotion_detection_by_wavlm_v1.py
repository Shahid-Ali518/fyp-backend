import numpy as np
import librosa
from ml_models.wavlm_model_v1_onnx_loader import session, feature_extractor, EMOTION_LABELS

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=1)

def predict_emotion_wavlm_v1(audio_array: np.ndarray):
    speech = audio_array

    # 1. REMOVE SILENCE
    # Increased top_db to 30 to be more aggressive against background hiss
    speech, _ = librosa.effects.trim(speech, top_db=30)

    # 2. Z-SCORE NORMALIZATION (Standardization)
    # This is the "WavLM Way" - it balances the frequency energy properly
    if np.std(speech) > 0:
        speech = (speech - np.mean(speech)) / (np.std(speech) + 1e-5)
    else:
        # Fallback if audio is empty or flat
        speech = speech - np.mean(speech)

    # 3. FIXED LENGTH (3 Seconds @ 16kHz)
    max_length = 16000 * 3
    if len(speech) > max_length:
        speech = speech[:max_length]
    else:
        speech = np.pad(speech, (0, max_length - len(speech)))

    # 4. INFERENCE
    inputs = feature_extractor(speech, sampling_rate=16000, return_tensors="np")
    onnx_inputs = {session.get_inputs()[0].name: inputs.input_values}
    logits = session.run(None, onnx_inputs)[0]

    # 5. CALIBRATION OFFSETS
    # We penalize Disgust (1) and Sad (5) which are common "false positives"
    # for laptop mics. We boost Neutral (4) and Happy (3) slightly.
    logits[0][1] -= 2.0  # Stronger penalty for Disgust
    logits[0][5] -= 1.8  # Stronger penalty for Sad
    logits[0][4] += 0.8  # Boost Neutral
    logits[0][3] += 0.5  # Boost Happy (helps detect excitement)

    # 6. CALCULATE PROBABILITIES
    probs = softmax(logits)[0]
    predicted_id = np.argmax(probs)

    # 7. LOGICAL OVERRIDE
    # If the model is still leaning toward Sad/Disgust but Neutral is present,
    # we favor the "saner" option for a real-world application.
    if EMOTION_LABELS[predicted_id] in ["sad", "disgust"]:
        neutral_idx = 4
        # If Neutrality is even a small contender (over 15%), we pick it
        if probs[neutral_idx] > 0.15:
            predicted_id = neutral_idx

    # 8. PREPARE RESPONSE
    probs_dict = {
        EMOTION_LABELS[i]: round(float(probs[i]), 4)
        for i in range(len(EMOTION_LABELS))
    }

    return {
        "top_emotion": EMOTION_LABELS[predicted_id],
        "probabilities": probs_dict
    }