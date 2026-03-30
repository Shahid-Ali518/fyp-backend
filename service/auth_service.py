from sqlalchemy.orm import Session
from models.user import User, UserRole
from core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from typing import Dict, Any

from schemas.api_response import ApiResponse
from schemas.auth_response import AuthResponseDTO
from schemas.login_request import LoginRequestDTO
from schemas.user_schema import UserDTO
from service.user_service import user_service


class AuthService:
    
    @staticmethod
    async def register_user(db: Session, registration_data: UserDTO) -> ApiResponse:
        #
        return user_service.create_user(db, registration_data)

    @staticmethod
    async def authenticate_user(db: Session, login_data: LoginRequestDTO) -> ApiResponse:

        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )

        auth_response = AuthResponseDTO(
            access_token=access_token,
            username=user.name,
            email=user.email,
            role=user.role.value
        )

        return ApiResponse(
            status_code=status.HTTP_200_OK,
            message="User Login Successful",
            data=auth_response
        )

auth_service = AuthService()
