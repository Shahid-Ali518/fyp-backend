from sqlalchemy.orm import Session
from models.test_category import TestCategory
from schemas.test_category import TestCategoryCreate, TestCategoryUpdate


class TestCategoryService:

    def create_category(self, data: dict, db: Session):
        category = TestCategory(**data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_all_categories(self, db: Session):
        return db.query(TestCategory).all()

    def get_category(self, db: Session, category_id: int):
        return db.query(TestCategory).filter(TestCategory.id == category_id).first()

    def update_category(self, db: Session, category_id: int, data: TestCategoryUpdate):
        category = self.get_category(db, category_id)
        if not category:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    def delete_category(self, db: Session, category_id: int):
        category = self.get_category(db, category_id)
        if not category:
            return None

        db.delete(category)
        db.commit()
        return True
