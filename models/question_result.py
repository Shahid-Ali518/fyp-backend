
from sqlalchemy import Column, Integer, Enum, Float, ForeignKey, LargeBinary, Text, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    attempt_id = Column(UUID, ForeignKey("test_attempts.id", ondelete="CASCADE"))
    question_id = Column(UUID, ForeignKey("questions.id", ondelete="CASCADE"))

    # Store the selected option
    selected_option_id = Column(UUID, ForeignKey("survey_options.id", ondelete="SET NULL"), nullable=True)

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
