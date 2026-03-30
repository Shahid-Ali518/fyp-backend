from sqlalchemy import Column, Integer, String, Text
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from core.database import Base

class TestCategory(Base):
    __tablename__ = "test_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category_type = Column(String(100))

    # relationships
    questions = relationship("Question", back_populates="category", cascade="all, delete")
    attempts = relationship("TestAttempt", back_populates="category")
    class_ranges = relationship("AssessmentClassRange",back_populates="category",cascade="all, delete")
    # options belong to particular category
    options = relationship("SurveyOption", back_populates="category", cascade="all, delete")