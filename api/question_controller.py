from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from service.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

question_service = QuestionService()


@router.post("/")
async def create_question(
    category_id: int = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = {
            "text": text,
            "category_id": category_id,
        }

        return question_service.create_question(db, data)
    except Exception as e:
        print(e)

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
def update_question(question_id: int, data: dict, db: Session = Depends(get_db)):
    updated = question_service.update_question(db, question_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    deleted = question_service.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}
