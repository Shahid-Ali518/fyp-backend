
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification



# Absolute path to emotion/model
MODEL_PATH = r"K:\FYP\ml_models\my_emotion_model"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Loading processor from:", MODEL_PATH)
processor = Wav2Vec2Processor.from_pretrained(MODEL_PATH)

print("Loading model from:", MODEL_PATH)
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    MODEL_PATH,
    use_safetensors=True
)

model.to(DEVICE)
model.eval()
