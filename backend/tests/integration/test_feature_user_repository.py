import pytest
from unittest.mock import MagicMock
from backend.features.users.repository import UserRepository
from backend.features.users.model import User

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def user_repo(mock_session):
    return UserRepository(session=mock_session)

def test_get_user_by_email(user_repo, mock_session):
    # Setup mock behavior
    mock_user = User(id="123", email="test@example.com", name="Test User")
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user

    user = user_repo.get_user_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"
    assert user.id == "123"
    mock_session.query.assert_called_once_with(User)

def test_create_user_success(user_repo, mock_session):
    # Setup mock behavior (email doesn't exist)
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    
    user = user_repo.create_user(
        user_id="456",
        name="New User",
        email="new@example.com",
        interests=["AI"]
    )
    
    assert user is not None
    assert user.name == "New User"
    assert user.interests == ["AI"]
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_create_user_already_exists(user_repo, mock_session):
    # Setup mock behavior (email already exists)
    mock_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
    
    user = user_repo.create_user(
        user_id="456",
        name="New User",
        email="existing@example.com"
    )
    
    assert user is None
    mock_session.add.assert_not_called()
