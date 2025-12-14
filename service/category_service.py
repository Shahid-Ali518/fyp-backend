from http.client import responses

from sqlalchemy.orm import Session
from models.test_category import TestCategory
from schemas.test_category_schema import TestCategoryCreate, TestCategoryUpdate
from utils.api_response import Response


class TestCategoryService:

    # method to create a new category ================================
    def create_category(self, data: dict, db: Session):
        response = Response()
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
        response = Response()
        try:
            categories = db.query(TestCategory).all()
            response.message = "successfully fetched all test categories"
            response.status_code = 200
            response.categories = categories
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching all test categories'

        return response

    # method to get a category by id ============================
    def get_category(self, db: Session, category_id: int):
        response = Response()
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
    def update_category(self, db: Session, category_id: int, data: TestCategoryUpdate):
        response = Response()
        try:
            category = self.get_category(db, category_id)
            if not category:
                return None

            for key, value in data.dict(exclude_unset=True).items():
                setattr(category, key, value)

            db.commit()
            db.refresh(category)
            response.message = "successfully updated test category"
            response.status_code = 200
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while updating test category'

        return response

    # method to delete a category ================================================
    def delete_category(self, db: Session, category_id: int):
        response = Response()

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

