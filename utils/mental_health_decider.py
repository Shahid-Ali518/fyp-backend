def calculate_mental_health_state(all_emotions: list, category_name: str):
    """
    Handles Depression, Anxiety, Stress, and Normal states
    using weighted affective biomarkers.
    """
    if not all_emotions:
        return {"condition": "None", "mental_health_state": "No Data", "mental_health_score": 0.0}

    # 1. Aggregate probabilities across the session
    emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    avg_probs = {emo: 0.0 for emo in emotions}
    for dist in all_emotions:
        for emo in emotions:
            avg_probs[emo] += dist.get(emo, 0) / len(all_emotions)

    score = 0.0

    # 2. THE MULTI-PATH LOGIC ENGINE
    # ---------------------------------------------------------
    # DEPRESSION PATH: Focus on Sadness and lack of positive affect
    if "depression" in category_name.lower():
        # (Sadness dominates) + (Neutrality/Flatness) - (Happiness Buffer)
        score = (avg_probs['sad'] * 0.65) + (avg_probs['neutral'] * 0.35)
        score -= (avg_probs['happy'] * 0.2)

    # ANXIETY PATH: Focus on Fear, Surprise (startle), and Tension
    elif "anxiety" in category_name.lower():
        # (Fear is core) + (Surprise/Startle) + (Anger/Irritability)
        score = (avg_probs['fear'] * 0.6) + (avg_probs['surprise'] * 0.25) + (avg_probs['angry'] * 0.15)

    # STRESS PATH: Focus on Frustration and Aversion
    elif "stress" in category_name.lower():
        # (Anger/Frustration) + (Disgust/Aversion) + (Fear)
        score = (avg_probs['angry'] * 0.5) + (avg_probs['disgust'] * 0.2) + (avg_probs['fear'] * 0.3)

    # WELLNESS/NORMAL PATH: Focus on Stability
    else:
        # High Neutral and Happy levels indicate stability
        score = (avg_probs['neutral'] * 0.5) + (avg_probs['happy'] * 0.5)
        category_name = "Emotional Stability"
    # ---------------------------------------------------------

    # 3. Final Calibration
    final_score = round(max(0, min(1, score)), 4)

    # 4. Map Score to Professional Severity Classes
    if final_score <= 0.25:
        state = "Stable / Minimal Risk"
    elif 0.25 < final_score <= 0.55:
        state = "Mild / Emerging Symptoms"
    elif 0.55 < final_score <= 0.80:
        state = "Moderate / Apparent Distress"
    else:
        state = "High / Significant Concern"

    return {
        "condition": category_name,
        "mental_health_state": state,
        "mental_health_score": final_score
    }