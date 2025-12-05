from sqlalchemy import Column, Integer, Text, LargeBinary, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

class EmotionType(enum.Enum):
    happy = "happy"
    sad = "sad"
    angry = "angry"
    fear = "fear"
    neutral = "neutral"
    surprise = "surprise"
    disgust = "disgust"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("test_categories.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    audio_bytes = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("TestCategory", back_populates="questions")
    results = relationship("QuestionResult", back_populates="question", cascade="all, delete")
