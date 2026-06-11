import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_books(api_client):
    url = "/api/books/"
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_book(api_client):
    url = "/api/books/"
    data = {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
    }
    response = api_client.post(url, data)
    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_user_can_list_books(authenticated_client):
    client, user = authenticated_client
    response = client.get('/api/books/')
    assert response.status_code == 200