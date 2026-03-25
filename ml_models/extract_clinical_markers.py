import librosa
import numpy as np
# import parselmouth # install

def extract_clinical_markers(audio_path):
    # 1. Load for Pitch Analysis
    # snd = parselmouth.Sound(audio_path)
    # pitch = snd.to_pitch()
    # pitch_values = pitch.selected_array['frequency']
    pitch_values = []
    # Filter out zeros (where no pitch is detected/silence)
    valid_pitch = pitch_values[pitch_values > 0]

    # --- Marker 1: Pitch Variability (The Monotone Indicator) ---
    # Low std_dev (< 10-15 Hz) is a strong indicator of "Flat Affect" in Depression
    pitch_std = np.std(valid_pitch) if len(valid_pitch) > 0 else 0

    # 2. Load with Librosa for timing analysis
    y, sr = librosa.load(audio_path, sr=16000)

    # --- Marker 2: Pause Duration ---
    # Detect non-silent intervals
    intervals = librosa.effects.split(y, top_db=30)  # Adjust top_db for sensitivity

    total_duration = len(y) / sr
    speech_duration = sum([(start - end) for end, start in intervals]) / sr
    pause_duration = total_duration - speech_duration

    # Pause Ratio (High ratio > 0.3 often correlates with Depression)
    pause_ratio = pause_duration / total_duration if total_duration > 0 else 0

    return {
        "pitch_std_dev": round(pitch_std, 2),
        "pause_ratio": round(pause_ratio, 2),
        "speech_rate": round(len(intervals) / total_duration, 2)  # Phrases per second
    }