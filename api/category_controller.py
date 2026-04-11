import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_checker import admin_only, any_user
from schemas.test_category_schema import TestCategoryDTO
from service.category_service import TestCategoryService
from schemas.api_response import ApiResponse

router = APIRouter(prefix="/api/categories", tags=["Categories"])

category_service = TestCategoryService()


@router.post("/", response_model=ApiResponse)
def create_category(data: TestCategoryDTO, db: Session = Depends(get_db), _ = Depends(admin_only)):
    return category_service.create_category(data, db)

# all categories
@router.get("/", response_model=ApiResponse[List[TestCategoryDTO]])
def get_all_categories(db: Session = Depends(get_db), _ = Depends(any_user)):
    try:
        return category_service.get_all_categories(db)
    except :
        raise HTTPException(status_code=500, detail="Something went wrong")
# category by id
@router.get("/{category_id}", response_model=ApiResponse[TestCategoryDTO])
def get_category(category_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
    category = category_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
# category by id,, along with all children
@router.get("/{category_id}/with-detail", response_model=ApiResponse[TestCategoryDTO])
def get_category(category_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
    return category_service.get_full_category_details(db, category_id)

# category by type
@router.get("/type/{category_type}", response_model=ApiResponse)
def get_categoreis_by_type(category_type: str, db: Session = Depends(get_db), _ = Depends(admin_only)):
    response = category_service.get_category_by_type(db, category_type)
    return response


@router.put("/{category_id}")
def update_category(category_id: uuid.UUID, data: TestCategoryDTO, db: Session = Depends(get_db), _ = Depends(admin_only)):
    response = category_service.update_category(db, category_id, data)
    if not response:
        raise HTTPException(status_code=404, detail="Category not found")
    return response


@router.delete("/{category_id}")
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(admin_only)):
    response = category_service.delete_category(db, category_id)
    if not response:
        raise HTTPException(status_code=404, detail="Category not found")
    return response
