from http.client import responses

from sqlalchemy.orm import Session
from models.test_category import TestCategory
from schemas.test_category_schema import TestCategoryDTO
from utils.api_response import ApiResponse


class TestCategoryService:

    # method to create a new category ================================
    def create_category(self, data: dict, db: Session):
        response = ApiResponse()
        try:
            category = TestCategory(**data)
            db.add(category)
            db.commit()
            db.refresh(category)
            response.message = "Category created"
            response.status_code = 201
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while creating test category'

        return response


    # method to fetch all categories ===========================
    def get_all_categories(self, db: Session):
        response = ApiResponse()
        try:
            categories = db.query(TestCategory).all()
            response.message = "successfully fetched all test categories"
            response.status_code = 200
            response.data = categories
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching all test categories'

        return response

    # method to get a category by id ============================
    def get_category(self, db: Session, category_id: int):
        response = ApiResponse()
        try:
            category = db.query(TestCategory).get(category_id)
            response.message = "successfully fetched test category"
            response.status_code = 200
            response.category = category
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching test category'

        return response

    # method to update a category ======================================================
    def update_category(self, db: Session, category_id: int, dto: TestCategoryDTO):
        response = ApiResponse()
        try:
            category = self.get_category(db, category_id)
            if not category:
                response.status_code = 404
                response.message = "Category not found"
                return response

            # Update simple fields
            if dto.name is not None:
                category.name = dto.name
            if dto.description is not None:
                category.description = dto.description

            # Optional: update related lists (class_ranges, questions, options, attempts)
            # You can implement logic to update these relationships as needed.
            # For example, replacing existing class_ranges:
            if dto.class_ranges is not None:
                category.class_ranges = [cr.to_model() for cr in dto.class_ranges]

            if dto.questions is not None:
                category.questions = [q.to_model() for q in dto.questions]

            if dto.options is not None:
                category.options = [o.to_model() for o in dto.options]

            db.commit()
            db.refresh(category)

            response.data = TestCategoryDTO.model_validate(category)
            response.message = "Category updated successfully"
            response.status_code = 200

        except Exception as e:
            print(e)
            db.rollback()  # rollback in case of error
            response.status_code = 500
            response.message = 'Exception occurred while updating test category'

        return response

    # method to delete a category ================================================
    def delete_category(self, db: Session, category_id: int):
        response = ApiResponse()

        try:
            category = self.get_category(db, category_id)
            if not category:
                return None

            db.delete(category)
            db.commit()
            response.message = "successfully deleted test category"
            response.status_code = 200

        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while updating test category'

        return response

