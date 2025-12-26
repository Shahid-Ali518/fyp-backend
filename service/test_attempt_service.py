from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import TestCategory, QuestionResult, TestAttempt, User
from models.assessment_class_range import AssessmentClassRange
from models.survey_option import SurveyOption
from schemas.test_attempt_schema import TestAttemptDTO
from schemas.user_schema import UserDTO
from utils.api_response import ApiResponse
from utils.dto_utils import map_user_user_dto, map_TestCategoryEntity_to_dto, map_test_attempt_to_dto


class TestAttemptService:

    def create_attempt(self, payload: dict, db: Session):

        response = ApiResponse(status_code=200, message="success")
        print(payload)
        try:
            category_id = payload.get("category_id")
            user_id = payload.get("user_id")
            answers = payload.get("answers", [])

            # 1. Basic validation
            if not category_id or not user_id or not answers:
                raise HTTPException(status_code=400, detail="Invalid payload")

            # 2. Validate category
            category = db.query(TestCategory).filter(
                TestCategory.id == category_id
            ).first()

            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

            total_score = 0
            question_results = []

            # 3. Calculate total score
            for ans in answers:
                q_id = ans["question_id"]
                o_id = ans["option_id"]
                print(q_id, o_id)

                option = db.query(SurveyOption).filter(
                    SurveyOption.id == o_id
                ).first()

                if not option:
                    raise HTTPException(status_code=404, detail=f"Option {o_id} not found")

                total_score += option.weightage

                question_results.append(
                    QuestionResult(
                        question_id=q_id,
                        selected_option_id=o_id
                    )
                )

            # 4. Match score with class range
            class_range = db.query(AssessmentClassRange).filter(
                AssessmentClassRange.category_id == category_id,
                AssessmentClassRange.min_score <= total_score,
                AssessmentClassRange.max_score >= total_score
            ).first()

            if not class_range:
                raise HTTPException(
                    status_code=404,
                    detail="No class range found for calculated score"
                )

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(username="Shahid", email="shahid@gmail.com", password="123")
                db.add(user)
                db.commit()
                db.refresh(user)



            # 5. Create attempt (AFTER calculations)
            attempt = TestAttempt(
                user_id=user.id,
                category_id=category_id,
                test_score=total_score
                # overall_emotion = class_range.label
            )

            db.add(attempt)
            # db.flush()  # Generates attempt.id without committing

            # 6. Attach attempt_id to question results
            for qr in question_results:
                qr.attempt_id = attempt.id
                db.add(qr)


            # 7. Final commit (ONE COMMIT ONLY)
            db.add_all(question_results)
            db.commit()

            attempt.user = user
            attempt.category = category
            attempt.question_results = question_results


            attempt_dto = map_test_attempt_to_dto(attempt)

            response.status_code = 201
            response.message = "Attempt created"
            response.data = attempt_dto
            print("Test attempt dto: ", attempt_dto)



        except Exception as e:
            print(e)
            db.rollback()
            response.status_code = 500
            response.message = "exception occurred while creating attempt"

        return response
