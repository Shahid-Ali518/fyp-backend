import uuid

import librosa
import os

import numpy as np
from fastapi import UploadFile

from ml_models.emotion_detection_by_wavlm_v1 import predict_emotion_wavlm_v1


async def process_audio_emotion(file: UploadFile):
    temp_filename = f"temp_{uuid.uuid4()}.wav"

    try:
        # 2. Write the uploaded bytes to a real file on disk
        with open(temp_filename, "wb") as f:
            content = await file.read()
            f.write(content)

        # 3. Load from the actual file path (much more stable than BytesIO)
        # We force sr=16000 for WavLM compatibility
        audio_data, _ = librosa.load(temp_filename, sr=16000)

        # 4. Convert to mono if necessary
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)

        # 5. Run your ONNX model inference
        result = predict_emotion_wavlm_v1(audio_data)
        return result

    except Exception as e:
        print(f"Error in processing: {e}")
        raise e

    finally:
        # 6. CRITICAL: Always delete the temp file to save disk space
        if os.path.exists(temp_filename):
            os.remove(temp_filename)