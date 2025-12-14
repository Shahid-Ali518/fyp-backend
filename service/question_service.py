import io

import PyPDF2
from fastapi import UploadFile, File

from sqlalchemy.orm import Session
from models.question import Question
from schemas.question_schema import QuestionDTO
from utils.api_response import ApiResponse
from utils.tts_converter import text_to_audio_bytes


class QuestionService:

    # add only one question ==================================
    def create_question(self, db: Session, dto : QuestionDTO):
        response = ApiResponse()

        try:
           text = dto.text

           # Convert text to audio (bytes)
           audio_bytes = text_to_audio_bytes(text)
           # print(audio_bytes)
           print("here audio bytes are generated")


           question = Question(text = dto.text, category_id = dto.category_id, audio_bytes = audio_bytes)
           db.add(question)
           db.commit()
           db.refresh(question)
           response.message = "Question created"
           response.status_code = 201

        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while creating question"
            response.status_code = 500

        return response

    # add number of questions with pdf, docs file  ===================================================================
    async def add_questions_by_file(self, db: Session, category_id: int,  file: UploadFile = File(...)):
        response = ApiResponse()
        category_id = category_id

        # check file extension
        if not file.filename.lower().endswith(".pdf") or file.filename.lower().endswith(".docx"):
            response.message = "Please upload a PDF of docx file"
            response.status_code = 204 # bad request
            return response
            # Read PDF
        try:
            pdf_bytes = await file.read()  # async read
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        except Exception as e:
            print(e)
            response.message = "File could not be read"
            response.status_code = 404
            return response

        questions = []

        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue

            # Split PDF page text into lines
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            for line in lines:
                question_text = line.strip()
                if not question_text:
                    continue

                # Convert question text to audio bytes
                audio_bytes = text_to_audio_bytes(question_text)
                question = Question(category_id, question_text, audio_bytes)
                questions.append(question)

        db.add_all(questions)
        db.commit()
        db.refresh(questions)
        response.message = "Questions added successfully"
        response.status_code = 201
        return response


    # method to fetch all questions in db ========================================
    def get_all_questions(self, db: Session):
        response = ApiResponse()
        try:
            questions = db.query(Question).all()
            response.data = questions
            response.message = "Questions retrieved successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while retrieving questions"
            response.status_code = 500

        return response

    def get_question(self, db: Session, question_id: int):
        response = ApiResponse()
        try:
            question = db.query(Question).get(question_id)
            response.question = question
            response.message = "Question retrieved successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            response.message = "Exception occurred while retrieving question"
            response.status_code = 500
        return response


    # method to get all questions owned by one category ============================
    def get_questions_by_category(self, db: Session, category_id: int):
        response = ApiResponse()
        try:
            questions = db.query(Question).filter_by(category_id=category_id).all()
            response.questions = questions
            response.message = "Questions retrieved successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            response.message = "Exception occurred while retrieving questions"
            response.status_code = 500

        return response

    # method to update question =======================================================
    def update_question(self, db: Session, question_id: int, dto: QuestionDTO):
        response = ApiResponse()
        try:
            question = self.get_question(db, question_id)
            if not question:
                response.status_code = 404
                response.message = "Question not found"
                return response

            if dto.text is not None:
                question.text = dto.text
                question.audio_bytes = text_to_audio_bytes(dto.text)

            if dto.category_id is not None:
                question.category_id = dto.category_id

            db.commit()
            db.refresh(question)

            response.data = QuestionDTO.model_validate(question)
            response.message = "Question updated"
            response.status_code = 200

        except Exception as e:
            db.rollback()
            response.message = str(e)
            response.status_code = 500

        return response

    # method to delete question =================================
    def delete_question(self, db: Session, question_id: int):
        response = ApiResponse()
        try:
            question = self.get_question(db, question_id)
            if not question:
                return None

            db.delete(question)
            db.commit()
            response.message = "Question deleted successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while deleting question"
            response.status_code = 500

        return response


