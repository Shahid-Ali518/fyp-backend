from typing import List

from sqlalchemy.orm import Session
from starlette import status

from models import TestCategory
from models.assessment_class_range import AssessmentClassRange
from schemas.assessment_class_range_schema import AssessmentClassRangeDTO
from utils.api_response import ApiResponse
from utils.dto_utils import map_assessment_class_range_to_dto


class AssessmentClassRangeService():

    def __init__(self, db: Session):
        self.db = db


    # method to add all ranges to a particular category
    def add_all_ranges_to_category(self, category_id: int, dtos: List[AssessmentClassRangeDTO]):

        response = ApiResponse(message="Success", status_code=201)

        try:
            if category_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No category id"
                return response
            if dtos is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No Class Ranges"
                return response

            if self.db.query(TestCategory).filter(TestCategory.id == category_id).count() == 0:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such category"
                return response

            all_ranges = []

            for dto in dtos:
                orm_instance = AssessmentClassRange(
                    category_id=category_id,
                    min_score=dto.min_score,
                    max_score=dto.max_score,
                    label=dto.label
                )

                all_ranges.append(orm_instance)

            self.db.add_all(all_ranges)
            self.db.commit()

            response.message = "All ranges added"
            response.status_code = status.HTTP_201_CREATED


        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            print(e)
            self.db.rollback()
            response.message = "Exception occurred while add ranges"

        return response

    # method to find all assessment class ranges owned by particular test category ====================
    def get_options_by_category(self, category_id: int):
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

            ranges = self.db.query(AssessmentClassRange).filter(TestCategory.category_id == category_id).all()
            response.data = ranges
            response.message = "All Assessment class ranges fetched"
            response.status_code = status.HTTP_200_OK


        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            print(e)
            self.db.rollback()
            response.message = "Exception occurred while fetching Ranges"

        return response


    # method to get a single assessment class range =====================
    def get_assessment_class_by_id(self, assessment_class_id: int):
        response = ApiResponse(message="Success", status_code=201)
        try:
            if assessment_class_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No Assessment class id"
                return response

            assessment_range = self.db.query(AssessmentClassRange).filter(AssessmentClassRange.id == assessment_class_id).first()
            print(assessment_range)
            if assessment_range is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such Assessment class "
                return response

            assessment_range_dto = map_assessment_class_range_to_dto(assessment_range)

            response.data = assessment_range_dto
            response.message = "Assessment class  fetched successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while fetching Assessment Class"

        return response


    # method to update Assessment class
    def update_assessment_class_range(self, assessment_class_id: int, dto: AssessmentClassRangeDTO):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if assessment_class_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No Assessment class id"
                return response

            assess_exist = self.db.query(AssessmentClassRange).filter(AssessmentClassRange.id == assessment_class_id).first()
            if assess_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such Assessment class "
                return response

            assess_exist.min_score = dto.min_score
            assess_exist.max_score = dto.max_score
            assess_exist.label = dto.label

            self.db.add(assess_exist)
            self.db.commit()
            self.db.refresh(assess_exist)

            assessment_range_dto = map_assessment_class_range_to_dto(assess_exist)
            response.message = "option updated successfully"
            response.status_code = 200
            response.data = assessment_range_dto

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while updating Assessment Class"

        return response

    # method to delete option ============================================
    def delete_assessment_class_range(self, assessment_class_id: int):
        response = ApiResponse(message="Success", status_code=201)

        try:
            if assessment_class_id is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.message = "No Assessment class id"
                return response

            class_exist = self.db.query(AssessmentClassRange).filter(AssessmentClassRange.id == assessment_class_id).first()
            if class_exist is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                response.message = "No such option"
                return response

            self.db.delete(class_exist)
            self.db.commit()


            response.message = "Assessment class  deleted successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            self.db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = "Exception occurred while updating option"

        return response
