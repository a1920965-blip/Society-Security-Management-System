# 🧪 Test Suite — Quick Start

## Folder structure

```
tests/
├── conftest.py           # Shared fixtures (DB, client, tokens)
├── pytest.ini            # pytest config  ← put this in project root
├── test_auth.py          # Login, Register, Verify token
├── test_user_profile.py  # Profile, Weather, Notice, Personal, Resident, Vehicle
├── test_user_support.py  # Complaint, E-pass, Ticket status
└── test_admin.py         # Admin: users, logs, epass, complaints, notices
```

## Setup

```bash
pip install pytest httpx
```

## Run all tests

```bash
pytest
```

## Run a single file

```bash
pytest tests/test_auth.py
```

## Run a single test

```bash
pytest tests/test_auth.py::TestLogin::test_login_success
```

## Run with detailed output (see print statements)

```bash
pytest -s -v
```

---

## How the tests work

| Concept | What it does |
|---|---|
| `conftest.py` | Creates an in-memory SQLite DB — no real DB is ever touched |
| `db_session` fixture | Rolls back after every test → tests are fully isolated |
| `client` fixture | FastAPI `TestClient` wired to the test DB via dependency override |
| `user_headers` | Pre-logs-in a test user, gives you `Authorization: Bearer <token>` |
| `admin_headers` | Same but for an admin account |

---

## Adjusting for your actual import paths

In `conftest.py`, change these two lines to match your project structure:

```python
from app.main import app          # ← your FastAPI instance
from app import database, models  # ← your database.get_db and models.Base
```
