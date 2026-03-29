from sqlalchemy.orm import Session
from models.user import User, UserRole
from core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from typing import Dict, Any

class AuthService:
    
    @staticmethod
    async def register_user(db: Session, registration_data: Dict[str, Any]) -> User:
        # Check if email already exists
        print("Password received:", registration_data["password"])
        print("Type:", type(registration_data["password"]))
        print("Length:", len(registration_data["password"]))
        existing_user = db.query(User).filter(User.email == registration_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            name=registration_data["name"],
            email=registration_data["email"],
            password=get_password_hash(registration_data["password"]),
            role=UserRole.USER  # Default role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate_user(db: Session, login_data: Dict[str, Any]) -> Dict[str, Any]:
        user = db.query(User).filter(User.email == login_data["email"]).first()
        
        if not user or not verify_password(login_data["password"], user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        return {
            "token": access_token,
            "role": user.role.value,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email
            },
            "status_code": 200,
            "message": "Login successful"
        }

auth_service = AuthService()
