import uuid
from typing import List

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_checker import admin_only, any_user
from schemas.survey_option_schema import SurveyOptionDTO
from service.survey_option_service import SurveyOptionService

router = APIRouter(prefix="/api/survey-options", tags=["survey-options"])

class SurveyOptionsController():


    @router.post('/{category_id}/add-all')
    def add_options_to_category(
            category_id: uuid.UUID ,
            options: List[SurveyOptionDTO] = Body(..., embed=False),

            db: Session = Depends(get_db),
            _= Depends(admin_only)
    ):
        service = SurveyOptionService(db)
        return service.add_options_to_category(category_id, options)

    @router.get('/by-category/{category_id}')
    def get_options_by_category(category_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
        service = SurveyOptionService(db)
        return service.get_options_by_category(category_id)

    @router.get('/{option_id}')
    def get_option_by_id(option_id: uuid.UUID, db: Session = Depends(get_db), _ = Depends(any_user)):
        service = SurveyOptionService(db)
        return service.get_option_by_id(option_id)

    @router.put('/{option_id}')
    def update_option(option_id: uuid.UUID, option: SurveyOptionDTO, db: Session = Depends(get_db), _= Depends(admin_only)):
        service = SurveyOptionService(db)
        return service.update_option(option_id, option)


    @router.delete('/{option_id}')
    def delete_option(option_id: uuid.UUID, db: Session = Depends(get_db), _= Depends(admin_only)):
        service = SurveyOptionService(db)
        return service.delete_option(option_id)




