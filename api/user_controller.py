from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from service.user_service import user_service
from core.security import get_current_user
from models.user import User
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter(prefix="/user", tags=["user"])

class UserUpdate(BaseModel):
    name: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@router.get("/all")
async def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)

@router.get("/get-logged-in-profile-info")
async def get_logged_in_profile_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }

@router.get("/get-by-id/{user_id}")
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value
    }

@router.delete("/delete/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)

@router.put("/update-profile")
async def update_profile(
    update_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    user = user_service.update_user_profile(db, current_user, update_data.dict(exclude_unset=True))
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    }

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return user_service.change_password(db, current_user, password_data.dict())

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return user_service.get_user_dashboard_stats(db, str(current_user.id))
