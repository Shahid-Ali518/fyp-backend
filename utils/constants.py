import uuid

# Reusable options for clinical assessment (e.g., Likert scale for symptoms)
# Using common clinical frequency scales
GLOBAL_OPTIONS = [
    {"id": uuid.uuid4(), "option_text": "Not at all / Never", "weightage": 0.0},
    {"id": uuid.uuid4(), "option_text": "Several days / Mildly", "weightage": 0.3},
    {"id": uuid.uuid4(), "option_text": "More than half the days / Moderately", "weightage": 0.6},
    {"id": uuid.uuid4(), "option_text": "Nearly every day / Severely", "weightage": 1.0},
]

# Static Clinical Intake Questions
# These are designed to help a psychiatrist understand the patient's current state.
INTERVIEW_QUESTIONS = [
    {
        "id": uuid.uuid4(),
        "text": "Over the last two weeks, how often have you been bothered by feeling down, depressed, or hopeless?",
        "options": GLOBAL_OPTIONS
    },
    {
        "id": uuid.uuid4(),
        "text": "How often have you had trouble falling or staying asleep, or sleeping too much?",
        "options": GLOBAL_OPTIONS
    },
    {
        "id": uuid.uuid4(),
        "text": "How often have you felt tired or had very little energy to perform daily tasks?",
        "options": GLOBAL_OPTIONS
    },

    {
        "id": uuid.uuid4(),
        "text": "Have you had any trouble concentrating on things, such as reading the newspaper or watching television?",
        "options": GLOBAL_OPTIONS
    }
]