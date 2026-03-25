from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import torch
import librosa

# Load model and feature extractor
model_name = r"K:\FYP\ml_models\huggingface_models"
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

# Load and preprocess audio
audio_path = r"K:\FYP\fyp-backend\angry.wav"
audio, sr = librosa.load(audio_path, sr=16000, mono=True)

# Extract features
inputs = feature_extractor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

# Predict emotion
with torch.no_grad():
    logits = model(**inputs).logits
    predicted_id = torch.argmax(logits, dim=-1).item()

# Get emotion label
emotions = ['Anger', 'Disgust', 'Fear', 'Happiness', 'Neutral', 'Sadness', 'Surprise']
predicted_emotion = emotions[predicted_id]
print(f"Predicted emotion: {predicted_emotion}")

# Get confidence scores
probabilities = torch.softmax(logits, dim=-1)
confidence_scores = {emotion: prob.item() for emotion, prob in zip(emotions, probabilities[0])}
print(f"Confidence scores: {confidence_scores}")