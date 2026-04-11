import traceback
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from core.security import get_current_user
from models import TestCategory, QuestionResult, TestAttempt, User
from models.assessment_class_range import AssessmentClassRange
from models.survey_option import SurveyOption
from schemas.api_response import ApiResponse
from mapper.dto_utils import map_test_attempt_to_dto
from schemas.test_attempt_schema import TestAttemptDTO
from schemas.test_category_schema import TestCategoryDTO
from utils.mental_health_decider import calculate_mental_health_state


class TestAttemptService:

    # method to create option based emotion detection attempt
    @staticmethod
    def take_option_based_attempt(payload: dict, user, db: Session):

        response = ApiResponse(status_code=200, message="success")
        # print(payload)
        try:
            category_id = payload.get("category_id")
            answers = payload.get("answers", [])

            # 1. Basic validation
            if not category_id or not answers:
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

                # print(q_id, o_id)

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

            # 5. Create attempt (AFTER calculations)
            attempt = TestAttempt(
                user_id=user.id,
                category_id=category_id,
                test_score=total_score,
                test_state=class_range.label
            )

            db.add(attempt)
            db.flush()  # Generates attempt.id without committing

            # 6. Attach attempt_id to question results
            for qr in question_results:
                qr.attempt_id = attempt.id
                db.add(qr)


            # 7. Final commit (ONE COMMIT ONLY)
            db.add_all(question_results)
            db.commit()

            # attempt.user = user
            # attempt.category = category
            # attempt.question_results = question_results

            # attempt_dto = map_test_attempt_to_dto(attempt)

            # send frontend to id just
            attempt_dto = TestAttemptDTO(
                id=attempt.id,
                test_score=attempt.test_score,
                test_state=attempt.test_state
            )

            response.status_code = 201
            response.message = "Attempt created"
            response.data = attempt_dto
            # print("Test attempt dto: ", attempt_dto)

        except Exception as e:
            print(e)
            db.rollback()
            response.status_code = 500
            response.message = "exception occurred while creating attempt"

        return response


    # method to create voice based emotion detection assessment

    def take_voice_based_attempt(self, user_id: uuid.UUID, attempt_id: uuid.UUID,  db: Session):
        response = ApiResponse(status_code=200, message="success")

        try:

            existed_user = db.query(User).filter(User.id == user_id).first()
            existed_attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()

            if existed_user is None or existed_attempt is None:
                response.message = f"User or Attempt does not exist with {user_id}"
                response.status_code = 404
                return response

            # find test category to check whether it's depression, anxiety, stressed test
            category_name = existed_attempt.category.name.lower()

            question_results = db.query(QuestionResult).filter(QuestionResult.attempt_id == attempt_id).all()

            # calculate all emotions in
            # print(question_results)
            all_emotions  = []
            for qr in question_results:
                emotion = qr.emotion_probabilities
                all_emotions.append(emotion)

            print(all_emotions)

            # calculate final state and score of mental health

            results = calculate_mental_health_state(all_emotions, category_name)

            if results["condition"] == "None":
                Exception("No emotions found")

            elif results["condition"] == "Normal":
                existed_attempt.mental_health_state = results["condition"]
                existed_attempt.mental_health_score = results["mental_health_score"]

            existed_attempt.mental_health_state = results["mental_health_state"]
            existed_attempt.mental_health_score = results["mental_health_score"]

            db.add(existed_attempt)
            db.commit()
            db.refresh(existed_attempt)

            response.status_code = 200
            response.message = "success"
            response.data = map_test_attempt_to_dto(existed_attempt)


        except Exception as e:
            print(e)
            traceback.print_exc()
            db.rollback()
            response.status_code = 500
            response.message = "exception occurred while creating attempt"

        return response


    # method to cancel the attempt
    def cancel_attempt(self, user_id: uuid.UUID, attempt_id: uuid.UUID, db: Session):
        response = ApiResponse(status_code=200, message="success")
        try:

            existed_user = db.query(User).filter(User.id == user_id).first()
            existed_attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()

            if existed_user is None or existed_attempt is None:
                response.message = f"User or Attempt does not exist with {user_id}"
                response.status_code = 404
                return response

            db.delete(existed_attempt)
            db.commit()

            response.status_code = 200
            response.message = "Attempt canceled"

        except Exception as e:
            traceback.print_exc()
            print(e)
            db.rollback()
            response.status_code = 500
            response.message = "exception occurred while cancelling attempt"

        return response


    # method to get attempt with category
    def get_test_attempt_by_id(self, attempt_id: uuid.UUID, user, db: Session):
        response = ApiResponse(status_code=200, message="success")

        try:
            test_attempt = db.query(TestAttempt).options(
                joinedload(TestAttempt.category)
            ).filter(
                TestAttempt.id == attempt_id,
                TestAttempt.user_id == user.id
            ).first()

            if not test_attempt:
                raise HTTPException(status_code=404, detail="Assessment result not found")

            # Since we used joinedload, test_attempt.category is already populated
            # and we don't need a separate query for name and description.
            # attempt_dto = {
            #     "id": test_attempt.id,
            #     "score": test_attempt.mental_health_score,
            #     "state": test_attempt.mental_health_state,
            #     "date": test_attempt.created_at,
            #     "category": {
            #         "name": test_attempt.category.name,
            #         "description": test_attempt.category.description
            #     }
            # }

            attempt_dto = map_test_attempt_to_dto(test_attempt)

            response.data = attempt_dto
            response.status_code = 200
            return response

        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"Error fetching attempt: {e}")
            response.status_code = 500
            response.message = "An internal error occurred while retrieving the results"
            return response


