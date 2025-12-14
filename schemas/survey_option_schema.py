# schemas/survey_option_schema.py
from pydantic import BaseModel
from typing import Optional

class SurveyOptionDTO(BaseModel):
    id: Optional[int] = None
    category_id: int
    option_text: str
    weightage: float

    class Config:
        from_attributes = True
