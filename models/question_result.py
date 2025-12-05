from xml.dom.expatbuilder import TEXT_NODE

from sqlalchemy import Column, Integer, Enum, Float, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from core.database import Base
from models.question import EmotionType

class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    user_answer_audio = Column(LargeBinary)
    user_answer_text = Column(Text, nullable=False)
    recognized_emotion = Column(Enum(EmotionType))
    confidence = Column(Float, default=0.0)

    attempt = relationship("TestAttempt", back_populates="question_results")
    question = relationship("Question", back_populates="results")
