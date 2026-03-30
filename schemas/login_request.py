from pydantic import BaseModel


class LoginRequestDTO(BaseModel):
    email: str
    password: str