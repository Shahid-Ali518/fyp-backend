from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base

class TestCategory(Base):
    __tablename__ = "test_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    questions = relationship("Question", back_populates="category", cascade="all, delete")
    attempts = relationship("TestAttempt", back_populates="category")
