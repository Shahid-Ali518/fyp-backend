# schemas/test_attempt_schema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Reuse your EmotionType enum
from models.question import EmotionType
from schemas.question_result_schema import QuestionResultDTO

class TestAttemptDTO(BaseModel):
    id: Optional[int] = None
    user_id: int
    category_id: int
    test_score: Optional[float] = 0.0
    overall_emotion: Optional[EmotionType] = None
    attempt_date: Optional[datetime] = None

    # Optional nested DTOs for response
    question_results: Optional[List[QuestionResultDTO]] = []

    class Config:
        from_attributes = True
