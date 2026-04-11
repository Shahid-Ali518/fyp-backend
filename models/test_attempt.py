
from sqlalchemy import Column, Integer, Float, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sympy import false

from core.database import Base
from datetime import datetime
from models.test_level import TestLevel
from sqlalchemy.dialects.postgresql import UUID
import uuid

class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    category_id = Column(UUID, ForeignKey("test_categories.id"))
    test_score = Column(Float, default=0.0)
    test_state = Column(Text, nullable=True)
    attempt_date = Column(DateTime, default=datetime.utcnow)

    # relationships
    user = relationship("User", back_populates="attempts")
    category = relationship("TestCategory", back_populates="attempts")
    question_results = relationship("QuestionResult", back_populates="attempt", cascade="all, delete")
