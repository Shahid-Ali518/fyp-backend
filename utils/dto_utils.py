from typing import List

from models import TestCategory, User, TestAttempt
from schemas.test_attempt_schema import TestAttemptDTO
from schemas.test_category_schema import TestCategoryDTO
from schemas.user_schema import UserDTO


# map testcategory list to dto list
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
        username=user.username,
        email=user.email
    )

# method to map testAttempt to dto
def map_test_attempt_to_dto(attempt : TestAttempt) -> TestAttemptDTO:
    user_dto = map_user_user_dto(attempt.user)
    category_dto = map_TestCategoryEntity_to_dto(attempt.category)

    return TestAttemptDTO(
        id=attempt.id,
        test_score=attempt.test_score,
        overall_emotion=attempt.overall_emotion,
        user=user_dto,
        category=category_dto

    )