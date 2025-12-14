from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    message: str
    status_code: int
    data: Optional[T] = None
