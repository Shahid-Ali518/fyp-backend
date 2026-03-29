# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum for user roles (reuse your UserRole enum)
class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserDTO(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    role: Optional[UserRoleEnum] = UserRoleEnum.user
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
