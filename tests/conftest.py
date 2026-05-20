import pytest
from unittest.mock import MagicMock
import uuid
from datetime import datetime, timezone
from models.user import User, UserRole

@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mocking standard method chaining architectures
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.first.return_value = None
    return db

@pytest.fixture
def sample_user_id():
    return uuid.uuid4()

@pytest.fixture
def sample_user_model(sample_user_id):
    user = User(
        id=sample_user_id,
        name="Shahid Ali",
        email="shahid@pucit.edu.pk",
        password="hashed_secure_password_123",
        role=UserRole.USER,
        created_at=datetime.now(timezone.utc)
    )
    user.attempts = []
    return user