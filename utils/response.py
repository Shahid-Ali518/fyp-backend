from typing import List

from models import User, Question, QuestionResult, TestCategory, TestAttempt
from models.survey_option import SurveyOption


class Response:
    message : str
    status_code : int

    user : User
    question : Question
    category : TestCategory
    question_result = QuestionResult
    test_attempt : TestAttempt
    survey_option : SurveyOption

    users : List[type[User]]
    questions : List[type[Question]]
    question_results : List[type[QuestionResult]]
    categories : List[type[TestCategory]]
    test_attempts : List[type[TestAttempt]]
    survey_options : List[type[SurveyOption]]


