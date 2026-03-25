from xml.dom.expatbuilder import TEXT_NODE

from sqlalchemy import Column, Integer, Enum, Float, ForeignKey, LargeBinary, Text, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from models.question import EmotionType


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(Integer, primary_key=True)

    # Foreign keys
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    # Store the selected option
    selected_option_id = Column(Integer, ForeignKey("survey_options.id", ondelete="SET NULL"), nullable=True)

    # Optional user input fields
    user_answer_audio = Column(LargeBinary, nullable=True)
    # text from user voice
    user_answer_text = Column(Text, nullable=True)

    # all emotion probabilities in json format
    emotion_probabilities = Column(JSON, nullable=True)

    # Relationships
    attempt = relationship("TestAttempt", back_populates="question_results")
    question = relationship("Question", back_populates="results")
    selected_option = relationship("SurveyOption")  # Link to the chosen option
