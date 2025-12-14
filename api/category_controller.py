from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.test_category_schema import TestCategoryCreate
from service.category_service import TestCategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

category_service = TestCategoryService()


@router.post("/")
def create_category(data: dict = Body(...), db: Session = Depends(get_db)):
    return category_service.create_category(data, db)


@router.get("/")
def get_all_categories(db: Session = Depends(get_db)):
    return category_service.get_all_categories(db)


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}")
def update_category(category_id: int, data: dict, db: Session = Depends(get_db)):
    updated = category_service.update_category(db, category_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    deleted = category_service.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
