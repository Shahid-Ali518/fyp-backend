from pydantic import BaseModel

from models import UserRole


class AuthResponseDTO(BaseModel):
    access_token: str
    username: str
    role: UserRole
    email: str