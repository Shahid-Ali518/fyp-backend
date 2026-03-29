# schemas/test_attempt_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


from schemas.question_result_schema import QuestionResultDTO
from models.test_level import TestLevel


class TestAttemptDTO(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    category_id: int
    test_score: Optional[float] = 0.0
    test_level: Optional[TestLevel] = None
    attempt_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

