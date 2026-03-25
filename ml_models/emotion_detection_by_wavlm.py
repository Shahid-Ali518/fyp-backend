import torch
import numpy as np
import librosa
from ml_models.wavml_model_loader import wavml_model, DEVICE, feature_extractor, CREMAD_LABELS
import warnings
warnings.filterwarnings("ignore")


def post_process(logits):
    # Get the index of the highest score
    predicted_id = torch.argmax(logits, dim=-1).item()
    return CREMAD_LABELS[predicted_id]

def predict_emotion_wavlm_model(audio_array):

    # Load audio using librosa
    # speech, sr = librosa.load(file_path, sr=16000)
    speech = audio_array

    # 2.
    # This ensures your voice isn't "too quiet" compared to the training data
    if np.max(np.abs(speech)) > 0:
        speech = speech / np.max(np.abs(speech))

    # truncate to 3 seconds
    max_length = 16000 * 3
    if len(speech) > max_length:
        speech = speech[:max_length]
    else:
        speech = np.pad(speech, (0, max_length - len(speech)))

    # 4. Feature Extraction
    inputs = feature_extractor(speech, sampling_rate=16000, return_tensors="pt")
    inputs = {k: v.to(wavml_model.device) for k, v in inputs.items()}

    # 5. Get Prediction
    with torch.no_grad():
        logits = wavml_model(**inputs).logits

    print(post_process(logits))
    scores = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]

    probs_dict = {
        CREMAD_LABELS[i]: round(float(scores[i]), 4)
        for i in range(len(CREMAD_LABELS))
    }

    return probs_dict

# predict_emotion_wavlm_model()

#
# path = r"K:\FYP\fyp-backend\happy.wav"
# print("Happy")
# result = predict_emotion_wavlm_model(path)
# print(result)


# path = r"K:\FYP\fyp-backend\disgustorsad.wav"
# print("Sad")
# print(predict_emotion_wavlm_model(path))

# path = r"K:\FYP\fyp-backend\angry.wav"
# print("Angry")
# print(predict_emotion_wavlm_model(path))
#
# path = r"K:\FYP\fyp-backend\neutral.wav"
# print("Neutral")
# print(predict_emotion_wavlm_model(path))