from sqlalchemy.orm import Session

from ml_models.emotion_detection_by_wavlm import predict_emotion_wavlm_model
from models import QuestionResult, Question, TestAttempt
from schemas.api_response import ApiResponse
from utils.audio_utils import clean_audio_librosa, convert_array_to_bytes
from mapper.dto_utils import map_question_result_to_dto


class EmotionPredictionByWavLmService():

    def __init__(self, db: Session):
        self.db = db


    # method to prediction emotion of single question
    def predict_question_emotion(self, attempt_id: int, question_id: int, audio_path: str):

        response = ApiResponse(status_code=200, message="OK")

        try:
            existed_question = self.db.query(Question).filter(Question.id == question_id).first()
            existed_attempt = self.db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()

            if existed_question is None or existed_attempt is None:
                response.status_code = 404
                response.message = "Question or Attempt Not Found"
                return response

            # clean the audio
            cleaned_audio_array = clean_audio_librosa(audio_path)

            probs_dict = predict_emotion_wavlm_model(cleaned_audio_array)

            # extract dominant emotion
            dominant_emotion = max(probs_dict, key=probs_dict.get)
            confidence = probs_dict[dominant_emotion]

            # 3. Check if a record already exists for this question in this attempt
            result = self.db.query(QuestionResult).filter(
                QuestionResult.attempt_id == attempt_id,
                QuestionResult.question_id == question_id
            ).first()

            # 4. Create a new record if it doesn't exist
            if not result:
                result = QuestionResult(
                    attempt_id=attempt_id,
                    question_id=question_id
                )
                self.db.add(result)

            # create bytes of audio
            audio_bytes = convert_array_to_bytes(cleaned_audio_array)
            result.user_answer_audio = audio_bytes
            result.emotion_probabilities = probs_dict

            print(probs_dict)

            self.db.commit()
            self.db.refresh(result)

            # map to dto
            response.status_code = 200
            response.message = "Success"
            response.data = map_question_result_to_dto(result)


        except Exception as e:
            self.db.rollback()
            print(e)
            response.status_code = 500
            response.message = "Exception Occurred while emotion prediction of question"
            raise e

        return response