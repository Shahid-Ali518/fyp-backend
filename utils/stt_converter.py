DEPRESSION_WEIGHTS = {
    "sadness": 0.45,
    "disgust": 0.25,
    "fear": 0.15,
    "anger": 0.15
}

ANXIETY_WEIGHTS = {
    "fear": 0.45,
    "surprise": 0.25,
    "anger": 0.20,
    "sadness": 0.10
}

def map_score_to_severity(score: float) -> str:
    if score <= 25:
        return 1
    elif score <= 45:
        return 2
    elif score <= 65:
        return 3
    else:
        return 4
