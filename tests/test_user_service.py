import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from service.user_service import UserService
from schemas.user_schema import UserDTO


def test_create_user_success(mock_db):

    user_dto = UserDTO(name="Shahid Ali", email="shahid@pucit.edu.pk", password="password123")

    # Mock existing user check to return
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with patch("service.user_service.get_password_hash", return_value="hashed_mock"):
        response = UserService.create_user(mock_db, user_dto)

        assert response.status_code == 201
        assert response.message == "User registered successfully"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


def test_create_user_duplicate_email_throws_400(mock_db, sample_user_model):
    user_dto = UserDTO(name="Shahid Ali", email="shahid@pucit.edu.pk", password="password123")

    # Force query to return an existing user model
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_model

    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(mock_db, user_dto)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_update_user_profile_success(mock_db, sample_user_model, sample_user_id):
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_model

    with patch("service.user_service.map_user_to_user_dto") as mock_mapper:
        mock_mapper.return_value = UserDTO(id=sample_user_id, name="Shahid Updated", email=sample_user_model.email)

        response = UserService.update_user_profile(None, mock_db, sample_user_id, "Shahid Updated")

        assert response.status_code == 200
        assert sample_user_model.name == "Shahid Updated"
        mock_db.commit.assert_called_once()


def test_get_user_by_id_not_found_throws_404(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    fake_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        UserService.get_user_by_id(mock_db, fake_id)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail