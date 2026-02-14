from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from models.test_attempt import TestAttempt
from schemas.test_attempt_schema import TestAttemptDTO

router = APIRouter(prefix="/api/test-attempts", tags=["Test Attempts"])

@router.post("/submit")
def submit_test_attempt(
    payload: TestAttemptDTO,
    db: Session = Depends(get_db)
):
    attempt = TestAttempt(
        category_id=payload.category_id,
        test_score=payload.test_score,
        test_level=payload.test_level
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
    "id": attempt.id,
    "test_score": attempt.test_score,
    "test_level": attempt.test_level,
    "attempt_date": attempt.attempt_date
}

