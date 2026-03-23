
import pytest



#  REGISTER USER


class TestRegisterUser:

    def test_register_user_success(self, client):
        """A new user with valid details should be registered successfully."""
        response = client.post("/auth/register/user", json={
            "user_id":  "newuser01",
            "password": "StrongPass@1",
            "name":     "New User",
            "contact":  "9876543210",
            "email":    "newuser@example.com",
        })

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert "Registeration Successfully" in body["message"]

    def test_register_user_duplicate(self, client, registered_user):
        """Registering the same user_id twice should return 4xx (already exists)."""
        response = client.post("/auth/register/user", json={
            "user_id":  registered_user["user_id"],   # same id as fixture
            "password": "AnotherPass@1",
            "name":     "Duplicate User",
            "contact":  "1111111111",
            "email":    "dup@example.com",
        })

        assert response.status_code in (401,400, 409)   # Credential_Exception

    def test_register_user_missing_fields(self, client):
        """Missing required fields should return 422 Unprocessable Entity."""
        response = client.post("/auth/register/user", json={
            "user_id": "incomplete_user",
            # password, name, contact, email are missing
        })

        assert response.status_code == 422



#  REGISTER ADMIN


class TestRegisterAdmin:

    def test_register_admin_success(self, client, monkeypatch):
        """Admin registration with the correct admin_key should succeed."""
        monkeypatch.setenv("ADMIN_CODE", "SECRET_ADMIN_KEY")

        response = client.post("/auth/register/admin", json={
            "user_id":   "admintest01",
            "password":  "AdminPass@123",
            "admin_key": "SECRET_ADMIN_KEY",
        })

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_register_admin_wrong_key(self, client, monkeypatch):
        """Wrong admin_key should be rejected."""
        monkeypatch.setenv("ADMIN_CODE", "REAL_SECRET")

        response = client.post("/auth/register/admin", json={
            "user_id":   "badadmin01",
            "password":  "AdminPass@123",
            "admin_key": "WRONG_KEY",
        })

        assert response.status_code in (400, 401,403)

    def test_register_admin_duplicate(self, client, registered_admin):
        """Registering an admin that already exists should fail."""
        response = client.post("/auth/register/admin", json={
            "user_id":   registered_admin["user_id"],
            "password":  "AnotherPass@1",
            "admin_key": registered_admin["admin_key"],
        })

        assert response.status_code in (400, 409)



#  LOGIN


class TestLogin:

    def test_login_success(self, client, registered_user):
        """Valid credentials should return a token and user details."""
        response = client.post("/auth/login/", json={
            "user_id": registered_user["user_id"],
            "password": registered_user["password"],
        })

        assert response.status_code == 202
        body = response.json()
        assert body["success"] is True
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["role"] == "USER"
        assert body["user_id"] == registered_user["user_id"]

    def test_login_wrong_password(self, client, registered_user):
        """Wrong password should be rejected with 4xx."""
        response = client.post("/auth/login/", json={
            "user_id": registered_user["user_id"],
            "password": "WrongPassword!",
        })

        assert response.status_code in (400,404)

    def test_login_nonexistent_user(self, client):
        """Logging in with a user_id that doesn't exist should return 4xx."""
        response = client.post("/login/", json={
            "user_id": "ghost_user",
            "password": "DoesNotMatter",
        })

        assert response.status_code in (400, 404)

    def test_admin_login_returns_admin_role(self, client, registered_admin):
        """Admin login should return role = ADMIN."""
        response = client.post("/auth/login/", json={
            "user_id": registered_admin["user_id"],
            "password": registered_admin["password"],
        })

        assert response.status_code == 202
        assert response.json()["role"] == "ADMIN"


class TestVerifyToken:

    def test_verify_valid_token(self, client, registered_user, db_session):
        """A token_id that exists in the DB should verify successfully."""
        from app import models

        # Grab the token_id that was created during user registration
        token = db_session.query(models.Token).filter(
            models.Token.user_id == registered_user["user_id"]
        ).first()

        assert token is not None, "Token should have been created on registration"

        response = client.get("/verify/", params={"token_id": token.token_id})

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "Verifyed" in body["message"]  # matches the typo in your code

    def test_verify_invalid_token(self, client):
        """A random token_id that doesn't exist should return 4xx."""
        response = client.get("/verify/", params={"token_id": "nonexistent-token-id"})

        assert response.status_code in (400, 404)
