
from sqlalchemy import Column, Integer, ForeignKey, Float,Text
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base



class SurveyOption(Base):
    __tablename__ = "survey_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # test category may contain number of options to select
    category_id = Column(UUID,ForeignKey("test_categories.id", ondelete="CASCADE"),nullable=False)

    # option text like, mild, moderate, ...
    option_text = Column(Text, nullable=False)  # e.g. "Neutral", "Low", "High"

    # weightage of option
    weightage = Column(Float, nullable=False)

    # relationships
    category = relationship("TestCategory", back_populates="options")
