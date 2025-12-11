
from sqlalchemy import Column, Integer, ForeignKey, Float, false, Enum
from sqlalchemy.orm import relationship

from core.database import Base

from utils.constants import Options


class SurveyOption(Base):
    __tablename__ = "survey_options"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Enum(Options), default=Options.neutral, nullable=False)  # e.g. "Neutral", "Low", "High"
    weightage = Column(Float, nullable=False)

    question = relationship("Question", back_populates="survey_options")
