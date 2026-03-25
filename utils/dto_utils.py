from typing import List

from api.question_controller import question_service
from models import TestCategory, User, TestAttempt, Question, QuestionResult
from models.assessment_class_range import AssessmentClassRange
from models.survey_option import SurveyOption
from schemas.assessment_class_range_schema import AssessmentClassRangeDTO
from schemas.question_result_schema import QuestionResultDTO
from schemas.question_schema import QuestionDTO
from schemas.survey_option_schema import SurveyOptionDTO
from schemas.test_attempt_schema import TestAttemptDTO
from schemas.test_category_schema import TestCategoryDTO
from schemas.user_schema import UserDTO


# map test category list to dto list
def map_TestCategoryListEntity_to_dtoList(categories : List[TestCategory]) -> List[TestCategoryDTO]:
    list = []
    dto = TestCategoryDTO()
    for category in categories:
        dto.id = category.id
        dto.name = category.name
        dto.description = category.description
        dto.category_type = category.category_type
        list.append(dto)

    return list

# method to map testCategory to dto
def map_TestCategoryEntity_to_dto(category : TestCategory) -> TestCategoryDTO:
    return TestCategoryDTO(
        id=category.id,
        name=category.name,
        description=category.description,
        category_type=category.category_type,
    )

# method to map user to userDTO
def map_user_user_dto(user : User) -> UserDTO:
    return UserDTO(
        id=user.id,
        name=user.name,
        phone_number=user.phone_number,
        email=user.email
    )

# method to map testAttempt to dto
def map_test_attempt_to_dto(attempt : TestAttempt) -> TestAttemptDTO:
    user_dto = map_user_user_dto(attempt.user)
    category_dto = map_TestCategoryEntity_to_dto(attempt.category)

    return TestAttemptDTO(
        id=attempt.id,
        mental_health_score=attempt.mental_health_score,
        mental_health_state=attempt.mental_health_state,
        user=user_dto,
        category=category_dto

    )

def map_assessment_class_range_to_dto(assessment_class_range: AssessmentClassRange) -> AssessmentClassRangeDTO:
    return AssessmentClassRangeDTO(
        id=assessment_class_range.id,
        min_score=assessment_class_range.min_score,
        max_score=assessment_class_range.max_score,
        label=assessment_class_range.label,
        category_id=assessment_class_range.category_id
    )

 # method to map survey option to dto
def map_survey_option_to_dto(option : SurveyOption) -> SurveyOptionDTO:
     return SurveyOptionDTO(
         id=option.id,
         option_text=option.option_text,
         weightage=option.weightage,
         category_id=option.category_id
     )

# method to map question to dto ===================================
def map_question_to_question_dto(question : Question) -> QuestionDTO:
    return QuestionDTO(
        id = question.id,
        text=question.text,
        category_id=question.category_id
    )

# method to map question_result to dto
def map_question_result_to_dto(question_result : QuestionResult) -> QuestionResultDTO:
    return QuestionResultDTO(
        id=question_result.id,
        attempt_id=question_result.attempt_id,
        question_id=question_result.question_id,
        emotion_probabilities =  question_result.emotion_probabilities
    )




