import pytest
from rest_framework.test import APIClient
from accounts.models import CustomUser
from bookshelf.models import Book, ReadingGoal

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(username="testuser", password="StrongPass123!", email="test@test.com"):
        return CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email
        )
    return make_user

@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user

@pytest.fixture
def create_book(db):
    def make_book(user, **kwargs):
        defaults = {
            "title": "Default Title",
            "author": "Default Author",
            "genre": "Fiction",
            "status": "want_to_read",
        }
        defaults.update(kwargs)
        return Book.objects.create(user=user, **defaults)
    return make_book