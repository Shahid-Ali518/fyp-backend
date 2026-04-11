import uuid

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models import User
from service.test_attempt_service import TestAttemptService
from schemas.api_response import ApiResponse

router = APIRouter(prefix="/api/test-attempts")

service = TestAttemptService()


@router.post("/option-based", response_model=ApiResponse)
def take_option_based_attempt( payload: dict = Body(...),
                               current_user: User = Depends(get_current_user)
                               , db: Session = Depends(get_db)):
    return service.take_option_based_attempt(payload, current_user,  db)


@router.post("/take-voice-based-attempt/{user_id}/{attempt_id}", response_model=ApiResponse)
def take_voice_based_attempt(user_id: int, attempt_id: int, db: Session = Depends(get_db)):
    return service.take_voice_based_attempt(user_id, attempt_id, db)

@router.delete("/cancel/{user_id}/{attempt_id}", response_model=ApiResponse)
def cancel_attempt(user_id: int, attempt_id: int, db: Session = Depends(get_db)):
    return service.cancel_attempt(user_id, attempt_id, db)


@router.get("/{attempt_id}", response_model=ApiResponse)
def get_attempt(attempt_id: uuid.UUID, user = Depends(get_current_user),  db: Session = Depends(get_db)):
    return service.get_test_attempt_by_id(attempt_id, user, db)