from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    message: str
    status_code: int
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)
