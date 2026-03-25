from typing import List

from sqlalchemy.orm import Session
from starlette import status

from models import TestCategory
from models.survey_option import SurveyOption
from schemas.survey_option_schema import SurveyOptionDTO
from service.category_service import TestCategoryService
from utils.api_response import ApiResponse
from utils.dto_utils import map_survey_option_to_dto


class SurveyOptionService:

    def __init__(self, db: Session):
        self.db = db



    # method to add list of options to a particular test category =======================
    def add_options_to_category(self, category_id, options: List[SurveyOptionDTO]):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if category_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No category id"
                return response
            if options is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No options"
                return response
            if self.db.query(TestCategory).filter(TestCategory.id == category_id).count() == 0:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such category"
                return response

            all_options = []

            for dto in options:
                option = SurveyOption(
                    category_id=category_id,
                    option_text=dto.option_text,
                    weightage=dto.weightage
                )
                all_options.append(option)

            self.db.add_all(all_options)
            self.db.commit()

            response.message = "All options added"
            response.status_code = status.HTTP_201_CREATED


        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            print(e)
            self.db.rollback()
            response.message = "Exception occurred while add options"

        return response

    # method to find all options owned by particular test category ====================
    def get_options_by_category(self, category_id):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if category_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No category id"
                return response

            if self.db.query(TestCategory).filter(TestCategory.id == category_id).count() == 0:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such category"
                return response
            options = self.db.query(SurveyOption).filter(TestCategory.category_id == category_id).all()
            response.data = options
            response.message = "All options fetched"
            response.status_code = status.HTTP_200_OK


        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            print(e)
            self.db.rollback()
            response.message = "Exception occurred while fetching options"

        return response


    # method to get a single option ====================================
    def get_option_by_id(self, option_id):
        response = ApiResponse(message="Success", status_code=201)
        try:
            if option_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No option id"
                return response

            option_exist  = self.db.query(SurveyOption).filter(SurveyOption.id == option_id).first()

            if option_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such option"
                return response

            option_dto = map_survey_option_to_dto(option_exist)

            response.data = option_dto
            response.message = "option fetched successfully"
            response.status_code = status.HTTP_200_OK

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while fetching option"

        return response


    # method to update option ========================================
    def update_option(self, option_id, dto: SurveyOptionDTO):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if option_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No option id"
                return response

            option_exist = self.db.query(SurveyOption).filter(SurveyOption.id == option_id).first()
            if option_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such option"
                return response

            option_exist.option_text = dto.option_text
            option_exist.weightage = dto.weightage

            self.db.add(option_exist)
            self.db.commit()
            self.db.refresh(option_exist)

            option_dto = map_survey_option_to_dto(option_exist)

            response.data = option_dto
            response.message = "option updated successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while updating option"

        return response

    # method to delete option ==========================================
    def delete_option(self, option_id):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if option_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No option id"
                return response

            option_exist = self.db.query(SurveyOption).filter(SurveyOption.id == option_id).first()
            if option_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such option"
                return response

            self.db.delete(option_exist)
            self.db.commit()


            response.message = "option deleted successfully"
            response.status_code = status.HTTP_200_OK

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while updating option"

        return response


