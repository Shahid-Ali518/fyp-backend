import traceback
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import TestCategory, QuestionResult, TestAttempt, User
from models.assessment_class_range import AssessmentClassRange
from models.survey_option import SurveyOption
from schemas.api_response import ApiResponse
from mapper.dto_utils import map_test_attempt_to_dto
from utils.mental_health_decider import calculate_mental_health_state


class TestAttemptService:


    # method to initialize the attempt
    def create_attempt(self, user_id: uuid.UUID, category_id: uuid.UUID, db: Session):
        response = ApiResponse(status_code=200, message="success")

        try:

            existed_user = db.query(User).filter(User.id == user_id).first()
            existed_category = db.query(TestCategory).filter(TestCategory.id == category_id).first()

            if existed_user is None:
                response.message = f"User does not exist with {user_id}"
                response.status_code = 401
                return response

            if existed_category is None:
                response.message = f"Category does not exist with {category_id}"
                response.status_code = 401
                return response

            new_attempt = TestAttempt(
                user_id=user_id,
                category_id=category_id,
                attempt_date=datetime.utcnow(),
                mental_health_score=0.0,
                mental_health_state='',

            )

            db.add(new_attempt)
            db.commit()
            db.refresh(new_attempt)

            response.data = map_test_attempt_to_dto(new_attempt)
            response.message = "Attempt Created Successfully"
            response.status_code = 201

        except Exception as e:
            print(e)
            db.rollback()
            response.status_code = 500
            response.message = "exception occurred while creating attempt"

        return response

    # method to create option based emotion detection attempt
    def take_option_based_attempt(self, payload: dict, db: Session):

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

            # check whether option exists

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
                mental_health_score=total_score,
                mental_health_state = class_range.label
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