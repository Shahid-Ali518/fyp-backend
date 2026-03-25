# schemas/test_attempt_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Reuse your EmotionType enum
from models.question import EmotionType
from schemas.question_result_schema import QuestionResultDTO
from schemas.test_category_schema import TestCategoryDTO
from schemas.user_schema import UserDTO


class TestAttemptDTO(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    test_score: Optional[float] = 0.0
    mental_health_score: Optional[float]= None
    mental_health_state: Optional[str]= None
    attempt_date: Optional[datetime] = None

    # Optional nested DTOs for response
    question_results: Optional[List[QuestionResultDTO]] = []
    category: Optional[TestCategoryDTO] = None
    user: Optional[UserDTO] = None

    model_config = ConfigDict(from_attributes=True)
