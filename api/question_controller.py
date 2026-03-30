import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_checker import admin_only, any_user
from models import Question
from schemas.question_schema import QuestionDTO
from service.question_service import QuestionService
from schemas.api_response import ApiResponse

from fastapi.responses import Response

router = APIRouter(prefix="/api/questions", tags=["Questions"])

question_service = QuestionService()


@router.post("/{category_id}/list", response_model=ApiResponse)
async def add_questions_to_category(category_id: uuid.UUID, questions: List[QuestionDTO], db: Session = Depends(get_db), _ = Depends(admin_only)):
    return await question_service.add_questions_to_category(db, category_id, questions)


@router.post("/{category_id}/upload-pdf", response_model=ApiResponse)
async def  add_questions_to_category(category_id: uuid.UUID, pdf: UploadFile = File(...), db: Session = Depends(get_db), _ = Depends(admin_only)):
    return await question_service.add_questions_by_file(db, category_id, pdf)

@router.get("/")
def get_all_questions(db: Session = Depends(get_db), _ = Depends(any_user)):
    return question_service.get_all_questions(db)


@router.get("/{question_id}")
def get_question_by_id(question_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
    question = question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.get("/category/{category_id}")
def get_questions_by_category(category_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(admin_only)):
    return question_service.get_questions_by_category(db, category_id)


@router.put("/{question_id}")
def update_question(question_id: uuid.UUID, dto: QuestionDTO, db: Session = Depends(get_db), _ = Depends(admin_only)):
    updated = question_service.update_question(db, question_id, dto)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.delete("/{question_id}")
def delete_question(question_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(admin_only)):
    return question_service.delete_question(db, question_id)





# utility controller to get audio of question
@router.get("/{question_id}/audio")
def get_question_audio(question_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
    question = db.query(Question).filter(Question.id == question_id).first()
    print(question)
    if not question or not question.audio_bytes:
        raise HTTPException(status_code=404)

    # Returns the raw bytes with the correct media type
    return Response(content=question.audio_bytes, media_type="audio/mpeg")