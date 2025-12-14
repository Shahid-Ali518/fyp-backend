from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionDTO(BaseModel):
    id: Optional[int] = None
    category_id: int
    text: str
    audio_bytes: Optional[bytes] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
