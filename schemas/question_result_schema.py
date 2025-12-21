# schemas/question_result_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime

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
    recognized_emotion: Optional[EmotionType] = None
    confidence: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)
