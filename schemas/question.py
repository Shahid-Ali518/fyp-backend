from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class EmotionTypeEnum(str, Enum):
    happy = "happy"
    sad = "sad"
    angry = "angry"
    fear = "fear"
    neutral = "neutral"
    surprise = "surprise"
    disgust = "disgust"


class QuestionBase(BaseModel):
    text: str
    audio_bytes: Optional[bytes] = None


class QuestionCreate(QuestionBase):
    category_id: int


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    category_id: Optional[int] = None


class QuestionResponse(QuestionBase):
    id: int
    category_id: int
    created_at: datetime

    class Config:
        orm_mode = True
