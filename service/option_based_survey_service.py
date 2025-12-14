from sqlalchemy.orm import Session

from models.survey_option import SurveyOption
from utils.constants import Options, OPTION_KEYWORDS, OPTION_WEIGHTAGE
from utils.api_response import Response


class OptionBasedSurveyService():

    def __init__(self):
        pass

    def map_options_to_weights(self, text: str) -> tuple[Options, int]:

        text_lower = text.strip().lower()

        for option, keywords in OPTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return option, OPTION_WEIGHTAGE[option]

        # fallback if no match found
        return Options.neutral, OPTION_WEIGHTAGE[Options.neutral]


    def select_option(self, question_id: int, user_text: str, db: Session):
        response = Response()

        try:
            option_enum, weight = self.map_options_to_weights(user_text)

            survey_option = SurveyOption(question_id=question_id, option_text=option_enum, weightage=weight)

            db.add(survey_option)
            db.commit()
            db.refresh(survey_option)

            response.status_code = 200
            response.message = "Option selected"
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = "Exception occurred while selecting option"

        return response



#
# service = OptionBasedSurveyService()
#
# inputs = [
#     "I feel a little bit low today",
#     "My energy is extremely high",
#     "I am just okay",
#     "Barely any motivation"
# ]
#
# for text in inputs:
#     option, weight = service.map_options_to_weights(text)
#     print(f"Input: {text} -> Option: {option.value}, Weight: {weight}")
