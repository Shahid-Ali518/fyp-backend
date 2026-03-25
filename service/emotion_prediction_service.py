import torch
from typing import Dict
import librosa
# import nr

import numpy as np

from ml_models.emotion_model_loader import model, processor, DEVICE
from utils.audio_utils import load_audio, clean_audio_librosa

# Update labels to match your training
LABELS = {
    0:"angry",
    1:"disgust",
    2:"fear",
    3:"happy",
    4:"neutral",
    5:"sad",
    6:"ps"

}


def predict_emotion_from_file(audio_path: str) -> Dict:
    # 1. Load Audio
    audio, sr = librosa.load(audio_path, sr=16000)

    audio_final = clean_audio_librosa(audio_path)

    # 5. Feature extraction (use audio_final instead of audio)
    inputs = processor(
        audio_final,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    # 3. Move tensors to correct device
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    # 4. Inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        # Calculate Softmax to get probabilities (0.0 to 1.0)
        probabilities = torch.softmax(logits, dim=-1).squeeze()

        # 5. Create a dictionary of all emotion percentages
    emotion_percentages = {}
    for idx, prob in enumerate(probabilities):
        emotion_name = LABELS.get(idx, f"unknown_{idx}")
        # Convert to percentage and round to 2 decimal places
        emotion_percentages[emotion_name] = f"{round(prob.item() * 100, 2)}%"

    # 6. Get the top prediction for the main response
    confidence, predicted_id = torch.max(probabilities, dim=-1)

    print("--- Detailed Analysis ---")
    for emotion, percent in emotion_percentages.items():
        print(f"{emotion}: {percent}")

    # 7. Prepare response
    return {
        "top_prediction": {
            "emotion": LABELS.get(predicted_id.item(), "unknown"),
            "confidence": f"{round(confidence.item() * 100, 2)}%"
        },
        "full_analysis": emotion_percentages
    }


path = r"K:\FYP\fyp-backend\happy.wav"
print("Happy")
result = predict_emotion_from_file(path)


path = r"K:\FYP\fyp-backend\disgustorsad.wav"
print("Sad")
predict_emotion_from_file(path)

path = r"K:\FYP\fyp-backend\angry.wav"
print("Angry")
predict_emotion_from_file(path)