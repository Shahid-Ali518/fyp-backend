from datetime import datetime, timezone

from proto.marshal.compat import message
from sqlalchemy.orm import Session, joinedload, contains_eager
from transformers.models.xlstm.configuration_xlstm import external_xlstm

from mapper.user_mapper import map_user_to_user_dto, map_user_with_history_to_dto
from models import User
from models.user import User, UserRole
from models.test_attempt import TestAttempt
from core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
from typing import Dict, Any, List
import uuid

from schemas.api_response import ApiResponse
from schemas.user_schema import UserDTO


class UserService:


    # write operations ==============================================
    @staticmethod
    def create_user(db: Session, user_dto: UserDTO) -> ApiResponse:
        # validate inputs
        if not user_dto.name or not user_dto.email or not user_dto.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name, email, and password are required and cannot be empty"
            )

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_dto.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        try:
            #
            new_user = User(
                name=user_dto.name,
                email=user_dto.email,
                password=get_password_hash(user_dto.password),
                role=UserRole.USER,
                created_at=datetime.now(timezone.utc)
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)


            return ApiResponse(
                message="User registered successfully",
                status_code=201
            )

        except Exception as e:
            db.rollback()
            print(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the account"
            )


    # method to update profile ===============================================
    @staticmethod
    def update_user_profile(self, db: Session, user_id: uuid.UUID, name_to_update: str) -> ApiResponse[UserDTO]:

        # find user by iid
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user.name = name_to_update
            db.add(user)
            db.commit()
            db.refresh(user)

            dto = map_user_to_user_dto(user)
            return ApiResponse[UserDTO](
                message="User Updated successfully",
                status_code=status.HTTP_200_OK,
                data=dto
            )
        except Exception as e:
            db.rollback()
            print(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating account"
            )

    # method to get user by id =====================================
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> ApiResponse[UserDTO]:

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user_dto = map_user_to_user_dto(user)

            return ApiResponse[UserDTO](
                message="User Fetched successfully",
                status_code=status.HTTP_200_OK,
                data=user_dto
            )

        except Exception as e:
            db.rollback()
            print(f"Error getting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting user"
            )

    # method to get user's profile history
    @staticmethod
    def get_user_profile_history(db: Session, user_id: uuid.UUID) -> ApiResponse:

       try:
           # fetch user's details by using join and afterward sort them by date
           user = db.query(User) \
               .join(User.test_attempts) \
               .options(contains_eager(User.test_attempts)) \
               .filter(User.id == user_id) \
               .order_by(TestAttempt.attempt_date.desc()) \
               .first()

           if not user:
               # If .join() fail to find then simply return user info
               user = db.query(User).filter(User.id == user_id).first()
               if not user:
                   raise HTTPException(status_code=404, detail="User not found")

           # map to dtos
           data = map_user_with_history_to_dto(user, user.test_attempts)

           return ApiResponse(
               message="User profile fetched with most recent attempts first",
               status_code=200,
               data=data
           )

       except Exception as e:
            db.rollback()
            print(f"Error getting user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting user profile"
            )


    @staticmethod
    def get_all_users_for_admin(db: Session) -> ApiResponse[List[UserDTO]]:

        try:
            # custom query to fetch all non-admin users
            users = db.query(
                User.id,
                User.name,
                User.email,
                User.role,
                User.created_at
            ).filter(User.role != 'ADMIN').all()


            if len(users) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user_dtos = [map_user_to_user_dto(user) for user in users]

            return ApiResponse[List[UserDTO]](
                message="Users Fetched successfully",
                status_code=status.HTTP_200_OK,
                data=user_dtos
            )
        except Exception as e:
            db.rollback()
            print(f"Error getting users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting users"
            )

    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> ApiResponse:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            db.delete(user)
            db.commit()
            return ApiResponse(
                message="User Deleted successfully",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            db.rollback()
            print(f"Error deleting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting user"
            )


    @staticmethod
    def change_password(db: Session, user_id: uuid.UUID, password_to_change: str) -> ApiResponse[UserDTO]:

        try:
            # find user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if not verify_password(password_to_change, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect old password"
                )

            user.password = get_password_hash(password_to_change)
            db.add(user)
            db.commit()
            db.refresh(user)

            return ApiResponse[UserDTO](
                message="Password Updated successfully",
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            db.rollback()
            print(f"Error changing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing password"
            )

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
