from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.login_request import LoginRequestDTO
from schemas.user_schema import UserDTO
from service.auth_service import auth_service
from pydantic import BaseModel, EmailStr, field_validator
import re


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(user_dto: UserDTO, db: Session = Depends(get_db)):
    # print("Password received in controller:", request.registration.password)
    # print("Type in controller:", type(request.registration.password))
    # print("Length in controller:", len(request.registration.password))

    return await auth_service.register_user(db, user_dto)

@router.post("/login")
async def login(login_data: LoginRequestDTO, db: Session = Depends(get_db)):

    return await auth_service.authenticate_user(db, login_data)

