from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models import TestAttempt
from service.test_attempt_service import TestAttemptService
from utils.api_response import ApiResponse

router = APIRouter(prefix="/test-attempts")

service = TestAttemptService()

@router.post("/create/{user_id}/{category_id}", response_model=ApiResponse)
def take_option_based_attempt(user_id: int, category_id: int,  db: Session = Depends(get_db)):
    return service.create_attempt(user_id, category_id,  db)




@router.post("/", response_model=ApiResponse)
def take_option_based_attempt( payload: dict = Body(...), db: Session = Depends(get_db)):
    return service.take_option_based_attempt(payload, db)


@router.post("/take-voice-based-attempt/{user_id}/{attempt_id}", response_model=ApiResponse)
def take_voice_based_attempt(user_id: int, attempt_id: int, db: Session = Depends(get_db)):
    return service.take_voice_based_attempt(user_id, attempt_id, db)

@router.delete("/cancel/{user_id}/{attempt_id}", response_model=ApiResponse)
def cancel_attempt(user_id: int, attempt_id: int, db: Session = Depends(get_db)):
    return service.cancel_attempt(user_id, attempt_id, db)