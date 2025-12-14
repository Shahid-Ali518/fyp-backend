
from sqlalchemy import Column, Integer, ForeignKey, Float,Text
from sqlalchemy.orm import relationship

from core.database import Base



class SurveyOption(Base):
    __tablename__ = "survey_options"

    id = Column(Integer, primary_key=True)

    # test category may contain number of options to select
    category_id = Column( Integer,ForeignKey("test_categories.id", ondelete="CASCADE"),nullable=False)

    # option text like, mild, moderate, ...
    option_text = Column(Text, nullable=False)  # e.g. "Neutral", "Low", "High"

    # weightage of option
    weightage = Column(Float, nullable=False)

    # relationships
    category = relationship("TestCategory", back_populates="options")
