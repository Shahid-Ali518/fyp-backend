from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from service.auth_service import auth_service
from utils.api_response import ApiResponse
from pydantic import BaseModel, EmailStr, field_validator
import re


router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')
        return v

class RegistrationRequest(BaseModel):
    registration: UserRegister

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegistrationRequest, db: Session = Depends(get_db)):
    print("Password received in controller:", request.registration.password)
    print("Type in controller:", type(request.registration.password))
    print("Length in controller:", len(request.registration.password))
    user = await auth_service.register_user(db, request.registration.dict())
    return {
        "message": "User registered successfully",
        "statusCode": 200,
        "data": {"id": str(user.id), "name": user.name, "email": user.email}
    }

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    result = await auth_service.authenticate_user(db, login_data.dict())
    return {
        "message": result["message"],
        "statusCode": result["status_code"],
        "token": result["token"],
        "role": result["role"],
        "user": result["user"]
    }
