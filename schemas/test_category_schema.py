from pydantic import BaseModel
from typing import Optional

# schemas/test_category_schema.py
from pydantic import BaseModel
from typing import Optional, List

from models import TestAttempt
from .assessment_class_range_schema import AssessmentClassRangeDTO
from .question_schema import QuestionDTO
from .survey_option_schema import SurveyOptionDTO
from .test_attempt_schema import TestAttemptDTO


class TestCategoryDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    class_ranges: Optional[List[AssessmentClassRangeDTO]] = []
    questions: Optional[List[QuestionDTO]] = []
    options: Optional[List[SurveyOptionDTO]] = []
    attempts: Optional[List[TestAttemptDTO]] = []


    class Config:
        from_attributes = True

