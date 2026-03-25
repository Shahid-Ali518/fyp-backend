# schemas/question_result_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from enum import Enum
from datetime import datetime

from sqlalchemy import JSON

from models import TestAttempt
# Reuse your existing EmotionType enum from models
from models.question import EmotionType

class QuestionResultDTO(BaseModel):
    id: Optional[int] = None
    attempt_id: Optional[int] = None
    question_id: Optional[int] = None
    selected_option_id: Optional[int] = None

    # User responses
    user_answer_audio: Optional[bytes] = None
    user_answer_text: Optional[str] = None

    # Emotion detection
    emotion_probabilities: Optional[Dict[str, float]] = None


    model_config = ConfigDict(from_attributes=True)
