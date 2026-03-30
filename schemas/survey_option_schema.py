# schemas/survey_option_schema.py
import uuid

from pydantic import BaseModel, ConfigDict
from typing import Optional

class SurveyOptionDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    option_text: str
    weightage: float

    model_config = ConfigDict(from_attributes=True)
