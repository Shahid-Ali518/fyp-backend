# schemas/assessment_class_range_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class AssessmentClassRangeDTO(BaseModel):
    id: Optional[int] = None
    category_id: Optional[int] = None
    label: str
    min_score: int
    max_score: int
    recommendation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
