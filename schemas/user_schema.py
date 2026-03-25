# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum for user roles (reuse your UserRole enum)
class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class UserDTO(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    phone_number : str
    role: Optional[UserRoleEnum] = UserRoleEnum.user
    created_at: Optional[datetime] = None


