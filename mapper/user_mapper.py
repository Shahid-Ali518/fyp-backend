from typing import List
from models.user import User
from models.test_attempt import TestAttempt
from schemas.test_attempt_schema import TestAttemptDTO
from schemas.user_schema import UserDTO


def map_user_to_user_dto(user: User) -> UserDTO:

    return UserDTO(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value if user.role else None,
        created_at=user.created_at
    )

def map_dto_to_user(dto: UserDTO) -> User:
    return User(
        id=dto.id,
        name=dto.name,
        email=dto.email
    )

# method to map user details along with its history
def map_user_with_history_to_dto(user: User, attempts: List[TestAttempt]) -> UserDTO:
    dto = map_user_to_user_dto(user)

    # Map the list of attempts to their DTOs
    dto.history = [
        TestAttemptDTO(
            id=a.id,
            test_score=a.test_score,
            test_level=a.test_level.value if a.test_level else None,
            attempt_date=a.attempt_date
        ) for a in attempts
    ]
    return dto