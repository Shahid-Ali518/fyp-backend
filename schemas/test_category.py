from pydantic import BaseModel
from typing import Optional

class TestCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class TestCategoryCreate(TestCategoryBase):
    pass


class TestCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TestCategoryResponse(TestCategoryBase):
    id: int

    class Config:
        orm_mode = True
