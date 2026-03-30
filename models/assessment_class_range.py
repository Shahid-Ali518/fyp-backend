from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class AssessmentClassRange(Base):
    __tablename__ = "assessment_class_ranges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID, ForeignKey("test_categories.id", ondelete="CASCADE"))

    label = Column(String(50), nullable=False)  # e.g. "Moderate Depression"
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)

    recommendation = Column(Text, nullable=True)

    category = relationship("TestCategory", back_populates="class_ranges")
