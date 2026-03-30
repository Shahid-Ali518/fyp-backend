import io
import re
import uuid
from datetime import datetime, timezone
from typing import List

from PyPDF2 import PdfReader
from fastapi import UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import TestCategory
from models.question import Question
from schemas.question_schema import QuestionDTO
from schemas.api_response import ApiResponse
from utils.tts_converter import text_to_audio_bytes

class QuestionService:



    # add only one question ==================================
    # def add_question_to_category(self, db: Session, category_id : int , dtos : List[QuestionDTO]):
    #     response = ApiResponse(message="Success", status_code=201)
    #
    #     try:
    #
    #         if category_id is None:
    #             response.status_code = status.HTTP_404_NOT_FOUND
    #             response.message = "category does not exist"
    #             return response
    #
    #         category_exist = db.query().filter(TestCategory.id == category_id).first()
    #         if category_exist is None:
    #             response.status_code = status.HTTP_404_NOT_FOUND
    #             response.message = "category does not exist"
    #             return response
    #
    #
    #         all_questions = []
    #         for dto in dtos:
    #             text = dto.text
    #
    #             # Convert text to audio (bytes)
    #             audio_bytes = text_to_audio_bytes(text)
    #             # print(audio_bytes)
    #             print("here audio bytes are generated")
    #
    #             question = Question(text=dto.text, category_id=dto.category_id, audio_bytes=audio_bytes)
    #             all_questions.append(question)
    #
    #         db.add(all_questions)
    #         db.commit()
    #         response.message = "Question created"
    #         response.status_code = 201
    #
    #     except Exception as e:
    #         print(e)
    #         db.rollback()
    #         response.message = "Exception occurred while creating question"
    #         response.status_code = 500
    #
    #     return response

    # method to add list of questions to a category =================================
    async def add_questions_to_category(self, db: Session, category_id : uuid.UUID, dtos : List[QuestionDTO]):
        response = ApiResponse(message="Success", status_code=201)
        try:
            if category_id is None:
                raise HTTPException(status_code=404, detail="category does not exist")
            # check weather category exists or not
            is_category_exist = db.query(TestCategory).filter(TestCategory.id == category_id).first()

            if is_category_exist is None:
                raise HTTPException(status_code=404, detail="category does not exist")

            all_questions = []
            for dto in dtos:
                text = dto.text
                audio_bytes = text_to_audio_bytes(text)

                question = Question(category_id=category_id, text=text, audio_bytes=audio_bytes, created_at=datetime.now(timezone.utc))
                all_questions.append(question)

            db.add_all(all_questions)
            db.commit()

            response.message = "Question added"
            response.status_code = 201


        except HTTPException as he:
            db.rollback()
            raise he

        except Exception as e:
            print(e)
            db.rollback()
            response.message = "Exception occurred while adding  questions"
            response.status_code = 500

        return response

    # add number of questions with pdf, docs file  ===================================================================
    async def add_questions_by_file(self, db: Session, category_id: uuid.UUID, file: UploadFile = File(...)):
        # 1. Read PDF
        pdf_bytes = await file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))

        if not file.filename.lower().endswith(".pdf"):
            return ApiResponse(status_code=400, message="Please upload a PDF file")

        try:
            all_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"

            raw_lines = [line.strip() for line in all_text.split("\n") if len(line.strip()) > 5]
            questions_text = []
            current_question = ""
            blacklist = ["instructions", "page", "assessment", "clinical", "score", "patient"]

            for line in raw_lines:
                if any(word in line.lower() for word in blacklist) and len(line) < 35:
                    continue

                # Heuristic for a new question start
                is_new_start = re.match(r"^\d+[\.\)\-]\s*", line) or \
                               (line[0].isupper() and (line.endswith('?') or len(line) > 45))

                if is_new_start:
                    if current_question:
                        questions_text.append(current_question.strip())
                    current_question = line
                else:
                    if current_question:
                        current_question += " " + line
                    else:
                        current_question = line

            if current_question:
                questions_text.append(current_question.strip())

            # Clean and Filter
            final_questions = []
            for q in questions_text:
                cleaned = re.sub(r"^\d+[\.\)\-]\s*", "", q).strip()
                if len(cleaned) > 12:
                    final_questions.append(cleaned)

            if not final_questions:
                return ApiResponse(status_code=400, message="No valid questions found in file")

            # Create DB Objects
            db_objects = []
            for q_text in final_questions:
                # Note: This is synchronous, it will block until done
                audio = text_to_audio_bytes(q_text)
                db_objects.append(Question(category_id=category_id, text=q_text, audio_bytes=audio))

            db.add_all(db_objects)
            db.commit()

            return ApiResponse(
                status_code=201,
                message=f"Added {len(db_objects)} questions successfully"
            )

        except Exception as e:
            db.rollback()
            return ApiResponse(status_code=500, message=f"Internal Server Error: {str(e)}")

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

    def get_question_by_id(self, db: Session, question_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=201)
        try:
            print(question_id)
            question = db.query(Question).filter(Question.id == question_id).first()
            if question is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "Question not found"
                return response

            question_dto = QuestionDTO(
                id=question.id,
                text=question.text,
                category_id=question.category_id
            )

            response.data = question_dto
            response.message = "Question retrieved successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            response.message = "Exception occurred while retrieving question"
            response.status_code = 500
        return response


    # method to get all questions owned by one category ============================
    def get_questions_by_category(self, db: Session, category_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=201)
        try:
            questions = db.query(Question).filter_by(category_id=category_id).all()
            response.data = questions
            response.message = "Questions retrieved successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            response.message = "Exception occurred while retrieving questions"
            response.status_code = 500

        return response

    # method to update question =======================================================
    def update_question(self, db: Session, question_id: uuid.UUID, dto: QuestionDTO):
        response = ApiResponse(message="Success", status_code=201)
        try:
            question = db.query(Question).filter(Question.id == question_id).first()

            if question is None:
                response.status_code = 404
                response.message = "Question not found"
                return response

            print("Quesstion: " , question.category_id)

            question.text = dto.text
            question.audio_bytes = text_to_audio_bytes(dto.text)
            question.category_id = dto.category_id

            db.add(question)
            db.commit()
            db.refresh(question)

            question_dto = QuestionDTO(
                id=question.id,
                category_id=question.category_id,
                text=question.text
            )

            response.data = question_dto
            response.message = "Question updated"
            response.status_code = 200

        except Exception as e:
            db.rollback()
            response.message = str(e)
            response.status_code = 500

        return response

    # method to delete question =================================
    def delete_question(self, db: Session, question_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=201)
        try:
            question= db.query(Question).filter(Question.id == question_id).first()

            if question is None:
                response.status_code = 404
                response.message = "Question not found"
                return response

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


