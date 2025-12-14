from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class AssessmentClassRange(Base):
    __tablename__ = "assessment_class_ranges"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("test_categories.id", ondelete="CASCADE"))

    label = Column(String(50), nullable=False)  # e.g. "Moderate Depression"
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)

    recommendation = Column(Text, nullable=True)

    category = relationship("TestCategory", back_populates="class_ranges")
