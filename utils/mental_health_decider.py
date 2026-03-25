def calculate_mental_health_state(all_emotions: list, category_name: str):
    if not all_emotions:
        # Change 'state' and 'score' to match the keys used at the bottom
        return {
            "condition": "None",
            "mental_health_state": "No Data",
            "mental_health_score": 0.0
        }

    # 1. Aggregate and Average all emotion probabilities
    emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad"]
    avg_probs = {emo: 0.0 for emo in emotions}
    count = len(all_emotions)

    for dist in all_emotions:
        for emo in emotions:
            avg_probs[emo] += dist.get(emo, 0) / count


    score = 0.0
    state = "Stable"

    # 3. Apply Modern Weighting Formulas
    if "depression" in category_name:
        # Weight: Sadness (60%) + Neutral/Flat Affect (40%) - Happy (Penalty)
        score = (avg_probs['sad'] * 0.6) + (avg_probs['neutral'] * 0.4)
        score -= (avg_probs['happy'] * 0.1)  # High happiness reduces depression score

    elif "anxiety" in category_name:
        # Weight: Fear/Tension (70%) + Anger/Agitation (30%)
        score = (avg_probs['fear'] * 0.7) + (avg_probs['angry'] * 0.3)

    elif "stress" in category_name:
        # Weight: Anger/Frustration (50%) + Disgust (20%) + Fear (30%)
        score = (avg_probs['angry'] * 0.5) + (avg_probs['disgust'] * 0.2) + (avg_probs['fear'] * 0.3)
    else:
        score = avg_probs['neutral']
        category_name = "Normal"
    # Final score normalization and rounding
    final_score = round(max(0, min(1, score)), 4)

    # 4. Determine State Label based on Score Thresholds
    if final_score <= 0.35:
        state = f"Low {category_name.split()[0]}"
    elif 0.35 < final_score <= 0.70:
        state = f"Moderate {category_name.split()[0]}"
    else:
        state = f"High {category_name.split()[0]}"

    return {
        "condition": category_name,
        "mental_health_state": state,
        "mental_health_score": final_score
        # "emotion_profile": {k: round(v, 4) for k, v in avg_probs.items()}
    }