
# schemas/test_category_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


from models import TestAttempt
from .assessment_class_range_schema import AssessmentClassRangeDTO
from .question_schema import QuestionDTO
from .survey_option_schema import SurveyOptionDTO


class TestCategoryDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_type: Optional[str]  = None
    class_ranges: Optional[List[AssessmentClassRangeDTO]] = []
    questions: Optional[List[QuestionDTO]] = []
    options: Optional[List[SurveyOptionDTO]] = []

    model_config = ConfigDict(
        from_attributes=True,
        check_fields=False  # This helps if some fields are missing from the ORM object
    )




