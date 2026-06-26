# Bookshelf API

A personal reading tracker REST API built with Django REST Framework and PostgreSQL. Rate books, write reviews, track reading progress, set yearly goals, and view your reading stats.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![DRF](https://img.shields.io/badge/Django_REST_Framework-API-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

**Live API:** https://bookshelf-api-production-d927.up.railway.app

---

## About

Bookshelf API is a pure REST API backend with no frontend. It handles user authentication, personal book collection management, reading goal tracking, and reading statistics. Built as a portfolio project to demonstrate Django REST Framework, token-based authentication, ownership-protected data, ORM aggregations, and professional API design patterns.

## Features

- **Token Authentication** — Register and login to receive an API token, used for all subsequent requests
- **Book CRUD** — Create, read, update, and delete books in your personal shelf
- **Ownership protection** — Users can only access and modify their own books, enforced at the database query level
- **Reading status tracking** — Mark books as want to read, reading, completed, or abandoned
- **Rating and reviews** — Rate completed books 1–5 and write personal reviews
- **Reading progress** — Track current page and total pages with a calculated progress percentage
- **Reading goals** — Set a yearly target book count and track progress toward it
- **Reading stats** — Total books, completed this year, currently reading, average rating, favourite genre, and goal progress — all calculated via ORM aggregations
- **Filtering** — Filter books by status or genre
- **Search** — Search books by title or author
- **Ordering** — Order books by rating, creation date, or finish date
- **Pagination** — All list endpoints paginated at 10 results per page
- **Automated tests** — pytest suite covering auth, ownership protection, and business logic with 96% coverage

## Tech Stack

- **Backend** — Python 3.13, Django 6.0, Django REST Framework
- **Auth** — dj-rest-auth, django-allauth
- **Database** — PostgreSQL
- **Testing** — pytest, pytest-django, pytest-cov
- **Static files** — WhiteNoise
- **Server** — Gunicorn
- **Deployment** — Railway
- **Config** — python-decouple

## Project Structure

```
config/               # Project settings, root URLs, wsgi, api root view
accounts/             # CustomUser model (bio, favourite_genre)
bookshelf/            # Book and ReadingGoal models, serializers, views, tests
```

---

## API Endpoints

**Base URL (local):** `http://127.0.0.1:8000`  
**Base URL (live):** `https://bookshelf-api-production-d927.up.railway.app`

All `/api/` endpoints require the following header:
```
Authorization: Token <your_token_here>
```

---

### Authentication

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| POST | `/auth/registration/` | Register new user, returns token | No |
| POST | `/auth/login/` | Login, returns token | No |
| POST | `/auth/logout/` | Logout, destroys token | Yes |
| GET | `/auth/user/` | Get current user details | Yes |

**Register example:**
```json
POST /auth/registration/
{
    "username": "john",
    "email": "john@example.com",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!"
}

Response 201:
{
    "key": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Login example:**
```json
POST /auth/login/
{
    "username": "john",
    "password": "SecurePass123!"
}

Response 200:
{
    "key": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List all books in your shelf |
| POST | `/api/books/` | Add a book to your shelf |
| GET | `/api/books/{id}/` | Retrieve a book |
| PUT | `/api/books/{id}/` | Full update |
| PATCH | `/api/books/{id}/` | Partial update (e.g. just status) |
| DELETE | `/api/books/{id}/` | Remove from shelf |

**Add book example:**
```json
POST /api/books/
{
    "title": "Dune",
    "author": "Frank Herbert",
    "genre": "Science Fiction",
    "status": "reading",
    "current_page": 120,
    "total_pages": 412
}

Response 201:
{
    "id": 1,
    "title": "Dune",
    "author": "Frank Herbert",
    "genre": "Science Fiction",
    "description": "",
    "status": "reading",
    "rating": null,
    "review": "",
    "current_page": 120,
    "total_pages": 412,
    "reading_progress": 29.1,
    "start_date": null,
    "finish_date": null,
    "created_at": "2026-06-01T10:00:00Z",
    "updated_at": "2026-06-01T10:00:00Z"
}
```

**Mark as completed with rating example:**
```json
PATCH /api/books/1/
{
    "status": "completed",
    "rating": 5,
    "finish_date": "2026-06-15"
}
```

**Status values:** `want_to_read` · `reading` · `completed` · `abandoned`

**Rating:** Integer 1–5, only valid when status is `completed`

**Query parameters:**
```
?status=reading                 → filter by status
?genre=Science Fiction          → filter by genre
?search=tolkien                 → search by title or author
?ordering=-rating               → order by rating descending
?ordering=created_at            → order by date added ascending
Combinable:
?status=completed&ordering=-rating
```

**Paginated response format:**
```json
{
    "count": 24,
    "next": "http://127.0.0.1:8000/api/books/?page=2",
    "previous": null,
    "results": [...]
}
```

---

### Reading Goal

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/goal/` | Get your reading goal (current year by default) |
| GET | `/api/goal/?year=2025` | Get goal for a specific year |
| POST | `/api/goal/` | Set a reading goal |
| PUT | `/api/goal/` | Update your reading goal |

**Set goal example:**
```json
POST /api/goal/
{
    "year": 2026,
    "target_books": 20
}

Response 201:
{
    "id": 1,
    "year": 2026,
    "target_books": 20,
    "books_completed_this_year": 4,
    "progress_percentage": 20.0
}
```

---

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/` | Full reading stats for your shelf |

**Stats response:**
```json
GET /api/stats/

{
    "total_books": 24,
    "completed_this_year": 8,
    "currently_reading": 2,
    "want_to_read": 12,
    "abandoned": 2,
    "average_rating": 4.25,
    "favourite_genre": "Science Fiction",
    "goal_progress": 40.0
}
```

`goal_progress` is `null` if no reading goal has been set for the current year.  
`average_rating` is `null` if no completed books have been rated yet.

---

## Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/Gongzuo-Dk/bookshelf-api.git
cd bookshelf-api
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**

Use `.env.example` as a reference:
```
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=bookshelf_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

**5. Set up the database**

Make sure PostgreSQL is running and the database exists:
```bash
python manage.py migrate
```

**6. Create a superuser**
```bash
python manage.py createsuperuser
```

**7. Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to see the API root, or use Postman.

---

## Running Tests

```bash
pytest
```

With coverage report:
```bash
pytest --cov=bookshelf
```

The test suite covers:
- Unauthenticated requests return 401
- Users can only access their own books
- Cross-user access returns 404 (not 403 — no data leakage)
- Book creation automatically assigns the authenticated user
- Rating validation — only allowed on completed books
- Reading goal creation, retrieval, and update
- Stats endpoint returns correct counts, averages, and goal progress
- Aggregation math verified against known data

---

## Key Implementation Details

- **Custom User Model** — Extends `AbstractUser` with `bio` and `favourite_genre` fields, set up before the first migration so the auth system is owned from day one
- **Token Authentication** — DRF's built-in token auth via dj-rest-auth. Clients receive a token on login and include it as `Authorization: Token <key>` on every request
- **Ownership at queryset level** — `get_queryset()` filters by `request.user` on every ViewSet. Users never see other users' books — because they're never fetched from the database
- **Row-level security** — `perform_create` injects `user=request.user` server-side. The user field is never accepted from the request body
- **Serializer validation** — `validate_rating` ensures ratings are between 1 and 5. Cross-field `validate()` ensures ratings are only accepted on completed books, handling PATCH partial updates correctly via `getattr(self.instance, ...)`
- **Calculated fields** — `reading_progress` (percentage) and `books_completed_this_year` are computed via `SerializerMethodField` — returned in responses without being stored in the database
- **ORM aggregations** — Stats endpoint uses `Avg`, `Count`, and `annotate` to calculate at the database level, never in Python loops. `values('genre').annotate(count=Count('genre')).order_by('-count')` determines the favourite genre via a single GROUP BY query
- **Environment variables** — All secrets managed via python-decouple. `.env.example` provided for reference

---

## Author

Daniel K  
GitHub: https://github.com/Gongzuo-Dk  
LinkedIn: https://www.linkedin.com/in/danylo-kulynych/