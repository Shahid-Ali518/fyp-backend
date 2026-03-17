from sqlalchemy.orm import Session
from models.user import User, UserRole
from models.test_attempt import TestAttempt
from core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
from typing import Dict, Any, List
import uuid

class UserService:
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        return db.query(User).all()

    @staticmethod
    def delete_user(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully", "statusCode": 200}

    @staticmethod
    def update_user_profile(db: Session, user: User, update_data: Dict[str, Any]) -> User:
        user.name = update_data.get("name", user.name)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, password_data: Dict[str, Any]):
        if not verify_password(password_data["old_password"], user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        user.password = get_password_hash(password_data["new_password"])
        db.commit()
        return {"message": "Password changed successfully", "statusCode": 200}

    @staticmethod
    def get_user_dashboard_stats(db: Session, user_id: str) -> Dict[str, Any]:
        attempts = db.query(TestAttempt).filter(TestAttempt.user_id == user_id).order_by(TestAttempt.attempt_date.desc()).all()
        
        tests_taken = len(attempts)
        recent_emotion = "Neutral"
        last_activity = "N/A"
        
        if attempts:
            latest_attempt = attempts[0]
            recent_emotion = latest_attempt.test_level.value if latest_attempt.test_level else "Neutral"
            last_activity = latest_attempt.attempt_date.strftime("%Y-%m-%d %H:%M")
            
        return {
            "testsTaken": tests_taken,
            "recentEmotion": recent_emotion,
            "lastActivity": last_activity
        }

user_service = UserService()
