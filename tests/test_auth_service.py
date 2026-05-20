import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from service.auth_service import AuthService
from schemas.login_request import LoginRequestDTO


@pytest.mark.asyncio
async def test_authenticate_user_success(mock_db, sample_user_model):
    login_dto = LoginRequestDTO(email="shahid@pucit.edu.pk", password="password123")
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_model

    with patch("service.auth_service.verify_password", return_value=True), \
            patch("service.auth_service.create_access_token", return_value="mocked_jwt_token"):
        response = await AuthService.authenticate_user(mock_db, login_dto)

        assert response.status_code == 200
        assert response.data.access_token == "mocked_jwt_token"
        assert response.data.username == sample_user_model.name


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password_throws_401(mock_db, sample_user_model):
    login_dto = LoginRequestDTO(email="shahid@pucit.edu.pk", password="wrong_password")
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_model

    with patch("service.auth_service.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.authenticate_user(mock_db, login_dto)

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in exc_info.value.detail