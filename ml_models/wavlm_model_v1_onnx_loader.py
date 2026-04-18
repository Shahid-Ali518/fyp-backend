import onnxruntime as ort
import os
from transformers import Wav2Vec2FeatureExtractor

# Update this path to your folder containing .onnx and .json
MODEL_DIR = r"K:\FYP\ml_models\wavlm_model_v1_app_ready"
ONNX_PATH = os.path.join(MODEL_DIR, "wavlm_model_v1.onnx")

# Load the Processor
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_DIR)

# Load ONNX Session (Automatically handles CPU/GPU)
# Providers will prefer CUDA if available, else CPU
session = ort.InferenceSession(ONNX_PATH, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

# Correct Alphabetical Labels based on your sorted(df.label.unique())
EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]