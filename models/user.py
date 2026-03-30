from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

# enum to store user role
class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

import uuid
from sqlalchemy.dialects.postgresql import UUID

# user class
class User(Base):
    __tablename__ = "users"

    # id
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # name
    name = Column(String(100), nullable=False)
    # email
    email = Column(String(120), unique=True, nullable=False)
    # password
    password = Column(String(255), nullable=False)
    # user role
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    # time at which comes to the application and login in
    created_at = Column(DateTime, default=datetime.utcnow)

    # store it's all records of tests he/she attempted
    attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete")
