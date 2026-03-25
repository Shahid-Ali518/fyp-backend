from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

# enum to store user role
class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

# user class
class User(Base):
    __tablename__ = "users"

    # id
    id = Column(Integer, primary_key=True, index=True)
    # username
    name = Column(String(50), nullable=False, server_default='unknown')
    # phone number
    phone_number = Column(String(20), unique=True, nullable=False)
    # email
    email = Column(String(120), unique=True, nullable=False)
    # password
    password = Column(String(255), nullable=False)
    # user role
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    # time at which comes to the application and login in
    created_at = Column(DateTime, default=datetime.utcnow)

    # store its all records of tests he/she attempted
    attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete")
