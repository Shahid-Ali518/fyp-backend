from typing import List

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.survey_option_schema import SurveyOptionDTO
from service.survey_option_service import SurveyOptionService

router = APIRouter(prefix="/survey-options", tags=["survey_options"])

class SurveyOptionsController():


    @router.post('/{category_id}')
    def add_options_to_category(
            category_id: int ,
            options: List[SurveyOptionDTO] = Body(..., embed=False),

            db: Session = Depends(get_db)
    ):
        service = SurveyOptionService(db)
        return service.add_options_to_category(category_id, options)

    @router.get('/{category_id}')
    def get_options_by_category(category_id: int, db: Session = Depends(get_db)):
        service = SurveyOptionService(db)
        return service.get_options_by_category(category_id)

    @router.get('/{option_id}')
    def get_option_by_id(option_id: int, db: Session = Depends(get_db)):
        service = SurveyOptionService(db)
        return service.get_option_by_id(option_id)

    @router.put('/{option_id}')
    def update_option(option_id: int, option: SurveyOptionDTO):
        service = SurveyOptionService()
        return service.update_option(option_id, option)


    @router.delete('/{option_id}')
    def delete_option(option_id: int, db: Session = Depends(get_db)):
        service = SurveyOptionService(db)
        return service.delete_option(option_id)




