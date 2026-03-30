# schemas/assessment_class_range_schema.py
import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional

class AssessmentClassRangeDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    label: str
    min_score: int
    max_score: int
    recommendation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
