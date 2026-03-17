from sqlalchemy import Column, Integer, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
from models.test_level import TestLevel
from sqlalchemy.dialects.postgresql import UUID

class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("test_categories.id"))
    test_score = Column(Float, default=0.0)
    test_level = Column(Enum(TestLevel, name="testlevel"), nullable=True)
    attempt_date = Column(DateTime, default=datetime.utcnow)

    # relationships
    user = relationship("User", back_populates="attempts")
    category = relationship("TestCategory", back_populates="attempts")
    question_results = relationship("QuestionResult", back_populates="attempt", cascade="all, delete")
