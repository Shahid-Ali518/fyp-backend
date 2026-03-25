from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class QuestionCreateDTO(BaseModel):
    text: str
    audio_url: Optional[str] = None

class QuestionDTO(BaseModel):
    id: Optional[int] = None
    category_id: Optional[int] = None
    text: str
    # 1. Change type to str and rename to audio_url for clarity
    audio_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    # 2. Logic to generate the URL string for audio
    @field_validator("audio_url", mode="before")
    @classmethod
    def generate_audio_url(cls, v, info):
        # SQLAlchemy objects are passed in as 'v' when mode="before"
        # We extract the ID to create the streaming link
        if hasattr(v, 'id'):
            return f"http://localhost:8000/questions/{v.id}/audio"
        return None