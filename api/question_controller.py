from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session

import models
from core.database import get_db
from models import Question
from schemas.question_schema import QuestionDTO
from service.question_service import QuestionService
from utils.api_response import ApiResponse

from fastapi.responses import Response

router = APIRouter(prefix="/questions", tags=["Questions"])

question_service = QuestionService()


@router.post("/{category_id}/list", response_model=ApiResponse)
def add_questions_to_category(category_id: int, questions: List[QuestionDTO], db: Session = Depends(get_db)):
    return question_service.add_questions_to_category(db, category_id, questions)


@router.post("/{category_id}/upload-pdf", response_model=ApiResponse)
async def  add_questions_to_category(category_id: int, pdf: UploadFile = File(...), db: Session = Depends(get_db)):
    return await question_service.add_questions_by_file(db, category_id, pdf)

@router.get("/")
def get_all_questions(db: Session = Depends(get_db)):
    return question_service.get_all_questions(db)


@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = question_service.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.get("/category/{category_id}")
def get_questions_by_category(category_id: int, db: Session = Depends(get_db)):
    return question_service.get_questions_by_category(db, category_id)


@router.put("/{question_id}")
def update_question(question_id: int, dto: QuestionDTO, db: Session = Depends(get_db)):
    updated = question_service.update_question(db, question_id, dto)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    deleted = question_service.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}




# utility controller to get audio of question
@router.get("/{question_id}/audio")
def get_question_audio(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    print(question)
    if not question or not question.audio_bytes:
        raise HTTPException(status_code=404)

    # Returns the raw bytes with the correct media type
    return Response(content=question.audio_bytes, media_type="audio/mpeg")