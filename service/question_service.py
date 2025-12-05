from sqlalchemy.orm import Session
from models.question import Question
from schemas.question import QuestionCreate, QuestionUpdate
from utils.tts_converter import text_to_audio_bytes


class QuestionService:

    def create_question(self, db: Session, data: dict):
        text = data.get("text")

        # Convert text -> audio (bytes)
        audio_bytes = text_to_audio_bytes(text)
        # print(audio_bytes)
        print("here audio bytes are generated")
        data["audio_bytes"] = audio_bytes

        question = Question(**data)
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    def get_all_questions(self, db: Session):
        return db.query(Question).all()

    def get_question(self, db: Session, question_id: int):
        try:
            return db.query(Question).filter(Question.id == question_id).first()
        except Exception:
            return None

    def get_questions_by_category(self, db: Session, category_id: int):
        try:
            return db.query(Question).filter(Question.category_id == category_id).all()
        except Exception:
            return None

    def update_question(self, db: Session, question_id: int, data: QuestionUpdate):
        question = self.get_question(db, question_id)
        if not question:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(question, key, value)

        db.commit()
        db.refresh(question)
        return question

    def delete_question(self, db: Session, question_id: int):
        try:
            question = self.get_question(db, question_id)
            if not question:
                return None

            db.delete(question)
            db.commit()
            return True
        except Exception:
            return None

