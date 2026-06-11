import datetime
import pytest
from bookshelf.models import ReadingGoal

@pytest.mark.django_db
def test_create_reading_goal(api_client, create_user):
    user = create_user(username="alice")
    api_client.force_authenticate(user=user)

    data = {"year": 2026, "target_books": 20}
    response = api_client.post("/api/goal/", data)

    assert response.status_code == 201
    assert response.data["year"] == 2026
    assert response.data["target_books"] == 20
    assert ReadingGoal.objects.filter(user=user, year=2026).exists()


@pytest.mark.django_db
def test_get_reading_goal_not_found(api_client, create_user):
    user = create_user(username="alice")
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/goal/?year=2026")

    assert response.status_code == 404


@pytest.mark.django_db
def test_update_reading_goal(api_client, create_user):
    user = create_user(username="alice")
    ReadingGoal.objects.create(user=user, year=2026, target_books=20)

    api_client.force_authenticate(user=user)
    response = api_client.put("/api/goal/", {"year": 2026, "target_books": 30})

    assert response.status_code == 200
    assert response.data["target_books"] == 30


@pytest.mark.django_db
def test_stats_basic_counts(api_client, create_user, create_book):
    user = create_user(username="alice")

    create_book(user, status="reading")
    create_book(user, status="reading")
    create_book(user, status="want_to_read")
    create_book(user, status="abandoned")
    create_book(user, status="completed", rating=4, finish_date=datetime.date.today())

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/stats/")

    assert response.status_code == 200
    assert response.data["total_books"] == 5
    assert response.data["currently_reading"] == 2
    assert response.data["want_to_read"] == 1
    assert response.data["abandoned"] == 1
    assert response.data["completed_this_year"] == 1


@pytest.mark.django_db
def test_stats_average_rating_and_favourite_genre(api_client, create_user, create_book):
    user = create_user(username="alice")
    today = datetime.date.today()

    create_book(user, status="completed", rating=5, genre="Fantasy", finish_date=today)
    create_book(user, status="completed", rating=3, genre="Fantasy", finish_date=today)
    create_book(user, status="completed", rating=4, genre="Sci-Fi", finish_date=today)

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/stats/")

    assert response.status_code == 200
    assert response.data["average_rating"] == 4.0
    assert response.data["favourite_genre"] == "Fantasy"


@pytest.mark.django_db
def test_stats_goal_progress(api_client, create_user, create_book):
    user = create_user(username="alice")
    current_year = datetime.date.today().year
    today = datetime.date.today()

    ReadingGoal.objects.create(user=user, year=current_year, target_books=10)

    create_book(user, status="completed", finish_date=today)
    create_book(user, status="completed", finish_date=today)

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/stats/")

    assert response.status_code == 200
    assert response.data["goal_progress"] == 20.0