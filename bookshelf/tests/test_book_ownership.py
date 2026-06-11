import pytest
from bookshelf.models import Book


@pytest.mark.django_db
def test_user_sees_only_own_books_in_list(api_client, create_user, create_book):
    user_a = create_user(username="alice")
    user_b = create_user(username="bob")

    create_book(user_a, title="Alice Book 1")
    create_book(user_a, title="Alice Book 2")
    create_book(user_b, title="Bob Book 1")

    api_client.force_authenticate(user=user_a)
    response = api_client.get("/api/books/")

    assert response.status_code == 200
    titles = [book["title"] for book in response.data["results"]]
    assert "Bob Book 1" not in titles
    assert len(titles) == 2


@pytest.mark.django_db
def test_user_cannot_retrieve_other_users_book(api_client, create_user, create_book):
    user_a = create_user(username="alice")
    user_b = create_user(username="bob")

    bob_book = create_book(user_b, title="Bob Book 1")

    api_client.force_authenticate(user=user_a)
    response = api_client.get(f"/api/books/{bob_book.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_cannot_update_other_users_book(api_client, create_user, create_book):
    user_a = create_user(username="alice")
    user_b = create_user(username="bob")

    bob_book = create_book(user_b, title="Bob Book 1")

    api_client.force_authenticate(user=user_a)
    response = api_client.patch(f"/api/books/{bob_book.id}/", {"status": "completed"})

    assert response.status_code == 404
    bob_book.refresh_from_db()
    assert bob_book.status == "want_to_read"


@pytest.mark.django_db
def test_user_cannot_delete_other_users_book(api_client, create_user, create_book):
    user_a = create_user(username="alice")
    user_b = create_user(username="bob")

    bob_book = create_book(user_b, title="Bob Book 1")

    api_client.force_authenticate(user=user_a)
    response = api_client.delete(f"/api/books/{bob_book.id}/")

    assert response.status_code == 404
    assert Book.objects.filter(id=bob_book.id).exists()


@pytest.mark.django_db
def test_created_book_is_assigned_to_authenticated_user(api_client, create_user):
    user = create_user(username="alice")
    api_client.force_authenticate(user=user)

    data = {
        "title": "Project Hail Mary",
        "author": "Andy Weir",
        "genre": "Science Fiction",
    }
    response = api_client.post("/api/books/", data)

    assert response.status_code == 201
    created_book = Book.objects.get(id=response.data["id"])
    assert created_book.user == user