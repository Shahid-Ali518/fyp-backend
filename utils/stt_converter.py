DEPRESSION_WEIGHTS = {
    "sad": 0.45,
    "disgust": 0.25,
    "fear": 0.15,
    "angry": 0.15
}

ANXIETY_WEIGHTS = {
    "fear": 0.45,
    "surprise": 0.25,
    "angry": 0.20,
    "sad": 0.10
}

def map_score_to_severity(score: float) -> str:
    if score <= 25:
        return "low"
    elif score <= 45:
        return "mild"
    elif score <= 65:
        return "moderate"
    else:
        return "high"
