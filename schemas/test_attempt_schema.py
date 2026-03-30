# schemas/test_attempt_schema.py
import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


from schemas.question_result_schema import QuestionResultDTO
from models.test_level import TestLevel


class TestAttemptDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    category_id: uuid.UUID
    test_score: Optional[float] = 0.0
    test_level: Optional[TestLevel] = None
    attempt_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

