# schemas/survey_option_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class SurveyOptionDTO(BaseModel):
    id: Optional[int] = None
    category_id: Optional[int] = None
    option_text: str
    weightage: float

    model_config = ConfigDict(from_attributes=True)
