from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models import TestAttempt
from service.test_attempt_service import TestAttemptService
from utils.api_response import ApiResponse

router = APIRouter(prefix="/test-attempts")

service = TestAttemptService()


@router.post("/", response_model=ApiResponse)
def create_test_attempt( payload: dict = Body(...), db: Session = Depends(get_db)):
    return service.create_attempt(payload, db)