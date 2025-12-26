from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.assessment_class_range_schema import AssessmentClassRangeDTO
from service.assessment_class_range_service import AssessmentClassRangeService


router = APIRouter(prefix="/assessment-class-ranges", tags=["Assessment Class Range"])


class AssessmentClassRangeController():


    def __init__(self, db: Session, service: AssessmentClassRangeService):
        self.db = db
        self.service = service


    @router.post('/{category_id}')
    def add_class_ranges_to_category(
            category_id: int,
            dto: List[AssessmentClassRangeDTO],
            db : Session = Depends(get_db)
    ):
        service = AssessmentClassRangeService(db)
        return service.add_all_ranges_to_category(category_id, dto)

    @router.get('/{category_id}')
    def get_class_ranges_by_category(category_id: int, db : Session = Depends(get_db)):
        service = AssessmentClassRangeService(db)
        return service.get_options_by_category(category_id)

    @router.get('/{assessment_class_id}')
    def get_assessment_class_range_by_id(assessment_class_id: int,  db: Session = Depends(get_db)):
        service = AssessmentClassRangeService(db)
        return service.get_assessment_class_by_id(assessment_class_id)

    @router.put('/{assessment_class_id}')
    def update_assessment_class_range_by_id(assessment_class_id: int, dto: AssessmentClassRangeDTO, db: Session = Depends(get_db)):
        service = AssessmentClassRangeService(db)
        return service.update_assessment_class_range(assessment_class_id, dto)

    @router.delete('/{assessment_class_id}')
    def delete_assessment_class_range(assessment_class_id: int, db: Session = Depends(get_db)):
        service = AssessmentClassRangeService(db)
        return service.delete_assessment_class_range(assessment_class_id)


