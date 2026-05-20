# schemas/user_schema.py
import uuid

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

from schemas.test_attempt_schema import TestAttemptDTO


# Enum for user roles (reuse your UserRole enum)
class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    email: EmailStr
    password: Optional[str] = None
    role: Optional[UserRoleEnum] = UserRoleEnum.USER
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserDTOWithAttemptHistory(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    email: EmailStr
    attempts: List[TestAttemptDTO]