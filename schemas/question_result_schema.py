# schemas/question_result_schema.py
import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict


class QuestionResultDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    attempt_id: Optional[uuid.UUID] = None
    question_id: Optional[uuid.UUID] = None
    selected_option_id: Optional[uuid.UUID] = None

    # User responses
    user_answer_audio: Optional[bytes] = None
    user_answer_text: Optional[str] = None

    # Emotion detection
    emotion_probabilities: Optional[Dict[str, float]] = None


    model_config = ConfigDict(from_attributes=True)
