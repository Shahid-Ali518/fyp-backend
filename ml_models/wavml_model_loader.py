import torch
from transformers import  WavLMForSequenceClassification
from transformers import Wav2Vec2FeatureExtractor


MODEL_PATH = r"K:\FYP\ml_models\wavlm_cremad_model"


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_PATH)
wavml_model = WavLMForSequenceClassification.from_pretrained(MODEL_PATH)
wavml_model.eval()

wavml_model.to(DEVICE)

CREMAD_LABELS = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "neutral",
    5: "sad"
}