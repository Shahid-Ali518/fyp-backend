import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from service.category_service import TestCategoryService
from schemas.test_category_schema import TestCategoryDTO
from models.test_category import TestCategory


@pytest.fixture
def service():
    return TestCategoryService()


def test_create_category_success(service, mock_db):
    dto = TestCategoryDTO(name="Anxiety Test", description="Diagnostic Layer", category_type="MANUAL")
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = service.create_category(dto, mock_db)

    assert response.status_code == 201
    assert response.message == "Category created"
    mock_db.add.assert_called_once()


def test_create_category_duplicate_throws_400(service, mock_db):
    dto = TestCategoryDTO(name="Anxiety Test", description="Diagnostic Layer", category_type="MANUAL")
    mock_db.query.return_value.filter.return_value.first.return_value = TestCategory(id=uuid.uuid4(),
                                                                                     name="Anxiety Test")

    with pytest.raises(HTTPException) as exc_info:
        service.create_category(dto, mock_db)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_get_full_category_details_not_found(service, mock_db):
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
    fake_id = uuid.uuid4()

    response = service.get_full_category_details(mock_db, fake_id)

    assert response.status_code == 404
    assert "Assessment not found" in response.message