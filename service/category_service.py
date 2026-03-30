import uuid

from fastapi import HTTPException
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from mapper.category_mapper import CategoryMapper
from models.test_category import TestCategory
from schemas.test_category_schema import TestCategoryDTO
from schemas.api_response import ApiResponse


class TestCategoryService:

    # method to create a new category ================================
    def create_category(self, category: TestCategoryDTO, db: Session):
        response = ApiResponse(message="Success", status_code=201)
        # check weather category name is already exist
        exist = db.query(TestCategory).filter(TestCategory.name == category.name).first()
        if exist:
            raise HTTPException(status_code=400, detail="Test category already exists")

        # perform insertion
        try:
            added_category = TestCategory(
                name=category.name,
                description=category.description,
                category_type = category.category_type,
            )
            db.add(added_category)
            db.commit()
            db.refresh(added_category)

            response_category = TestCategoryDTO(
                id=added_category.id,
                name=added_category.name,
                description=added_category.description,
                category_type=added_category.category_type,
            )

            response.message = "Category created"
            response.status_code = 201
            response.data = response_category

        except IntegrityError as e:
            db.rollback()

            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(
                    status_code=409,
                    detail="A category with this name already exists."
                )

            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while creating category."
            )

        return response


    # method to fetch all categories ===========================
    def get_all_categories(self, db: Session):
        response = ApiResponse(message="Success", status_code=201)
        try:
            categories = db.query(TestCategory).all()
            response.message = "successfully fetched all test categories"
            response.status_code = 200
            
            dtos = [
                TestCategoryDTO(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    category_type=c.category_type
                ) for c in categories
            ]
            response.data = dtos
            print(dtos)
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching all test categories'

        return response

    # method to get a category by id ============================
    def get_category_by_id(self, db: Session, category_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=201)
        try:
            category = db.query(TestCategory).get(category_id)
            if category:
                response.message = "successfully fetched test category"
                response.status_code = 200
                response.data = TestCategoryDTO(
                    id=category.id,
                    name=category.name,
                    description=category.description,
                    category_type=category.category_type
                )
            else:
                response.message = "Test category not found"
                response.status_code = 404
                response.data = None
        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching test category'

        return response

    # method to get detailed category along with its all children
    def get_full_category_details(self, db: Session, category_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=200)
        try:
            # 1. Fetch with Eager Loading (One Query)
            category = db.query(TestCategory).options(
                joinedload(TestCategory.questions),
                joinedload(TestCategory.options),
                joinedload(TestCategory.class_ranges)
            ).filter(TestCategory.id == category_id).first()

            if not category:
                response.message = "Assessment not found"
                response.status_code = 404
                return response

            # 2. Use the Mapper
            response.data = CategoryMapper.to_detailed_dto(category)
            response.message = "Successfully aggregated all assessment layers"
            response.status_code = 200

        except Exception as e:
            print(f"Mapping Error: {e}")
            response.status_code = 500
            response.message = "Internal server error during data mapping"

        return response

    # method to get category by category_type =================================

    def get_category_by_type(self, db: Session, category_type: str):
        response = ApiResponse(message="Success", status_code=201)
        try:
            categories = db.query(TestCategory).filter(TestCategory.category_type == category_type).all()

            if not categories:
                raise HTTPException(status_code=404, detail="Test category not found")

            # Properly map models to the DTOs
            dtos = [
                TestCategoryDTO(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    category_type=c.category_type
                ) for c in categories
            ]
            
            response.message = "successfully fetched test category"
            response.status_code = 200
            response.data = dtos

        except Exception as e:
            print(e)
            response.status_code = 500
            response.message = 'exception occurred while fetching test category'

        return response

    # method to update a category ======================================================
        
    def update_category(self, db: Session, category_id: uuid.UUID, dto: TestCategoryDTO):
        response = ApiResponse(message="Success", status_code=201)
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
    def delete_category(self, db: Session, category_id: uuid.UUID):
        response = ApiResponse(message="Success", status_code=201)

        try:
            category = db.query(TestCategory).filter(TestCategory.id == category_id).first()

            if not category:
                return None

            db.delete(category)
            db.commit()
            response.message = "successfully deleted test category"
            response.status_code = 200

        except Exception as e:
            print(e)
            db.rollback()
            response.status_code = 500
            response.message = 'exception occurred while updating test category'

        return response

