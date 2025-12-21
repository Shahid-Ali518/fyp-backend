import io
import re
from typing import List

import PyPDF2
from PyPDF2 import PdfReader
from fastapi import UploadFile, File, HTTPException

from sqlalchemy.orm import Session
from starlette import status

from models import TestCategory
from models.question import Question
from schemas.question_schema import QuestionDTO
from utils.api_response import ApiResponse
from utils.tts_converter import text_to_audio_bytes


class QuestionService:

    # add only one question ==================================
    def add_question_to_category(self, db: Session, category_id : int , dtos : List[QuestionDTO]):
        response = ApiResponse(message="Success", status_code=201)

        try:

            if category_id is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "category does not exist"
                return response

            category_exist = db.query().filter(TestCategory.id == category_id).first()
            if category_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "category does not exist"
                return response


            all_questions = []
            for dto in dtos:
                text = dto.text

                # Convert text to audio (bytes)
                audio_bytes = text_to_audio_bytes(text)
                # print(audio_bytes)
                print("here audio bytes are generated")

                question = Question(text=dto.text, category_id=dto.category_id, audio_bytes=audio_bytes)
                all_questions.append(question)

            db.add(all_questions)
            db.commit()
            db.refresh(all_questions)
            response.message = "Question created"
            response.status_code = 201

        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while creating question"
            response.status_code = 500

        return response

    # method to add list of questions to a category =================================
    async def add_questions_to_category(self, db: Session, category_id : int, dtos : List[QuestionDTO]):
        response = ApiResponse(message="Success", status_code=201)
        try:
            if category_id is None:
                raise HTTPException(status_code=404, detail="category does not exist")
            # check weather category exists or not
            is_category_exist = db.query().filter(TestCategory.id == category_id).first()

            if is_category_exist is None:
                raise HTTPException(status_code=404, detail="category does not exist")

            all_questions = []
            for dto in dtos:
                text = dto.text
                audio_bytes = text_to_audio_bytes(text)

                question = Question(category_id, text, audio_bytes)
                all_questions.append(question)

            db.add(all_questions)
            db.commit()
            db.refresh(all_questions)
            response.message = "Question added"
            response.status_code = 201


        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while adding  questions"
            response.status_code = 500

        return response

    # add number of questions with pdf, docs file  ===================================================================
    async def add_questions_by_file(
            self,
            db: Session,
            category_id: int,
            file: UploadFile = File(...)
    ):

        pdf_bytes = await file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))

        # Validate file type
        if not file.filename.lower().endswith((".pdf", ".docx")):
            return ApiResponse(
                status_code=400,
                message="Please upload a PDF or DOCX file",
                data=None
            )

        # Read file
        try:
            QUESTION_START = r"^\s*\d+[\.\)\-]\s*"  # 1. 2) 3-
            questions_text = []
            current_question = ""

            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = [line.strip() for line in text.split("\n") if line.strip()]

                for line in lines:

                    # Ignore headers / footers
                    if len(line) < 4:
                        continue
                    if re.match(r"^(page|phq|gad|instructions)", line.lower()):
                        continue

                    # New question detected
                    if re.match(QUESTION_START, line):
                        if current_question:
                            questions_text.append(current_question.strip())

                        current_question = line
                    else:
                        # Continuation of the same question
                        if current_question:
                            current_question += " " + line

            # Save last question
            if current_question:
                questions_text.append(current_question.strip())

            # Clean questions
            def clean_question(text: str) -> str:
                text = re.sub(QUESTION_START, "", text)
                text = re.sub(r"\s+", " ", text)
                return text.strip()

            questions_text = [clean_question(q) for q in questions_text]

            if not questions_text:
                return ApiResponse(
                    status_code=400,
                    message="No valid questions found in file",
                    data=None
                )

            # Convert to DB objects
            questions = []
            for q_text in questions_text:
                audio_bytes = text_to_audio_bytes(q_text)
                question = Question(
                    category_id=category_id,
                    text=q_text,
                    audio_bytes=audio_bytes
                )
                questions.append(question)

            db.add_all(questions)
            db.commit()

            return ApiResponse(
                status_code=201,
                message="Questions added successfully",
                data={"count": len(questions)}
            )
        except Exception as e:
            db.rollback()
            print("DB error:", e)
            return ApiResponse(status_code=500, message="Failed to save questions", data=None)

    # method to fetch all questions in db ========================================
    def get_all_questions(self, db: Session):
        response = ApiResponse(message="Success", status_code=201)
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
        response = ApiResponse(message="Success", status_code=201)
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
        response = ApiResponse(message="Success", status_code=201)
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
        response = ApiResponse(message="Success", status_code=201)
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
        response = ApiResponse(message="Success", status_code=201)
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


