DEPRESSION_WEIGHTS = {
    "sadness": 0.50,
    "anger": 0.20,
    "disgust": 0.15,
    "fear": 0.10,
    "neutral": 0.05
}


ANXIETY_WEIGHTS = {
    "fear": 0.50,
    "surprise": 0.20,
    "anger": 0.15,
    "sadness": 0.10,
    "disgust": 0.05
}

def map_score_to_severity(score: float) -> str:
    if score < 30:
        return 1
    elif score <= 50:
        return 2
    elif score <= 70:
        return 3
    else:
        return 4
