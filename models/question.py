from sqlalchemy import Column, Integer, Text, LargeBinary,  ForeignKey, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID, ForeignKey("test_categories.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)

    audio_bytes = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("TestCategory", back_populates="questions")
    results = relationship("QuestionResult", back_populates="question", cascade="all, delete")
