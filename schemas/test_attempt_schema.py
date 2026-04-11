# schemas/test_attempt_schema.py
import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, Text

from schemas.test_category_schema import TestCategoryDTO


class TestAttemptDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    test_score: Optional[float] = 0.0
    test_state: Optional[str] = None
    attempt_date: Optional[datetime] = None
    category: Optional[TestCategoryDTO] = None

    model_config = ConfigDict(from_attributes=True)

