import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.role_checker import admin_only
from schemas.api_response import ApiResponse
from schemas.user_schema import UserDTO
from service.user_service import user_service
from core.security import get_current_user
from models.user import User
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter(prefix="/api/users", tags=["user"])

class UserUpdate(BaseModel):
    name: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str


@router.get("/admin/all", response_model=ApiResponse[List[UserDTO]])
async def get_all_users(db: Session = Depends(get_db), _ = Depends(admin_only)): # Only Admin can list users
    return user_service.get_all_users_for_admin(db)

@router.get("/get-logged-in-profile-info")
async def get_logged_in_profile_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }

@router.get("/{user_id}", response_model=ApiResponse[UserDTO])
async def get_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = Depends(admin_only) # Method level security
):
    return user_service.get_user_by_id(db, user_id)


@router.put("/update-profile")
async def update_profile(
    update_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Pass just the name string as your service expects
    return user_service.update_user_profile(db, current_user.id, update_data.name)

@router.get("/profile-history")
async def get_profile_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_service.get_user_profile_history(db, current_user.id)

@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = Depends(admin_only) # Only Admin can delete accounts
):
    return user_service.delete_user(db, user_id)

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return user_service.get_user_dashboard_stats(db, str(current_user.id))
