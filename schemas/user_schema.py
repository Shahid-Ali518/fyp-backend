# schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum for user roles (reuse your UserRole enum)
class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class UserDTO(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    role: Optional[UserRoleEnum] = UserRoleEnum.user
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
