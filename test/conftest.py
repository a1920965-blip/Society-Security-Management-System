
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker

from app.main import app          
from app import database, models


TEST_DATABASE_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}_test"

engine = create_engine(
    TEST_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the whole test session."""
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    """Fresh database session per test — changes are rolled back automatically."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback() 
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI test client that uses the test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_user(client):
    """Register a test user and return their credentials."""
    payload = {
        "user_id": "testuser01",
        "password": "TestPass@123",
        "name": "Test User",
        "contact": "9999999999",
        "email": "test@example.com",
    }
    response=client.post("/auth/register/user/", json=payload)
    print(response.json())
    assert response.status_code==201
    return payload


@pytest.fixture()
def user_token(client, registered_user):
    """Login as a normal user and return the bearer token."""
    response = client.post(
        "/auth/login/",
        json={
            "user_id": registered_user["user_id"],
            "password": registered_user["password"],
        },
    )
    print(response.json())
    return response.json()["access_token"]


@pytest.fixture()
def user_headers(user_token):
    """Authorization headers for a normal user — plug into any request."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
def registered_admin(client, monkeypatch):
    """Register a test admin (monkeypatches ADMIN_CODE env var)."""
    monkeypatch.setenv("ADMIN_CODE", "SECRET_ADMIN_KEY")
    payload = {
        "user_id": "adminuser01",
        "password": "AdminPass@123",
        "admin_key": "SECRET_ADMIN_KEY",
    }
    client.post("/auth/register/admin/", json=payload)
    return payload


@pytest.fixture()
def admin_token(client, registered_admin):
    """Login as admin and return the bearer token."""
    response = client.post(
        "/auth/login/",
        json={
            "user_id": registered_admin["user_id"],
            "password": registered_admin["password"],
        },
    )
    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    """Authorization headers for an admin — plug into any request."""
    return {"Authorization": f"Bearer {admin_token}"}
