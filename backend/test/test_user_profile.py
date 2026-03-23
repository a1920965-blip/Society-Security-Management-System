

#  PROFILE

class TestUserProfile:

    def test_get_profile_success(self, client, user_headers, registered_user):
        """Authenticated user should be able to fetch their own profile."""
        response = client.get("/user/profile/", headers=user_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["user_id"] == registered_user["user_id"]
        assert "name" in data
        assert "email" in data
        assert "contact" in data

    def test_get_profile_without_token(self, client):
        """Request without a token should be rejected (401)."""
        response = client.get("/user/profile/")

        assert response.status_code == 401


#  WEATHER

class TestUserWeather:

    def test_get_weather_authenticated(self, client, user_headers):
        """Authenticated user should receive weather data (defaults to Delhi)."""
        response = client.get("/user/weather", headers=user_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body

    def test_get_weather_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/user/weather")

        assert response.status_code == 401


#  NOTICE

class TestUserNotice:

    def test_get_notice_authenticated(self, client, user_headers):
        """Authenticated user should be able to fetch notices."""
        response = client.get("/user/notice", headers=user_headers)

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_get_notice_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/user/notice")

        assert response.status_code == 401


#  UPDATE PERSONAL DETAILS

class TestUpdatePersonal:

    def test_update_personal_success(self, client, user_headers):
        """User should be able to update their personal details."""
        response = client.put("/user/personal/", headers=user_headers, json={
            "contact":     "8888888888",
            "email":       "updated@example.com",
            "designation": "Software Engineer",
            "department":  "IT",
        })

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "Updates" in body["message"]

    def test_update_personal_unauthenticated(self, client):
        """Request without token should return 401."""
        response = client.put("/user/personal/", json={
            "contact": "8888888888",
            "email":   "updated@example.com",
        })

        assert response.status_code == 401


#  UPDATE RESIDENT DETAILS

class TestUpdateResident:

    RESIDENT_PAYLOAD = {
        "house_no": "42",
        "block":    "B",
        "city":     "Delhi",
        "state":    "Delhi",
        "pincode":  "110001",
    }

    def test_update_resident_creates_new_record(self, client, user_headers):
        """First update should create a resident record."""
        response = client.put(
            "/user/resident/",
            headers=user_headers,
            json=self.RESIDENT_PAYLOAD,
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_update_resident_modifies_existing(self, client, user_headers):
        """Second update should modify the existing resident record."""
        # First create
        client.put("/user/resident/", headers=user_headers, json=self.RESIDENT_PAYLOAD)

        # Then update with new data
        updated = {**self.RESIDENT_PAYLOAD, "city": "Mumbai", "state": "Maharashtra"}
        response = client.put("/user/resident/", headers=user_headers, json=updated)

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_update_resident_unauthenticated(self, client):
        """Request without token should return 401."""
        response = client.put("/user/resident/", json=self.RESIDENT_PAYLOAD)

        assert response.status_code == 401


#  VEHICLE  (add & remove)

class TestVehicle:

    VEHICLE_NUMBER = "DL01AB1234"

    def test_add_vehicle_success(self, client, user_headers):
        """User should be able to add a vehicle."""
        response = client.post(
            "/user/vehicle/add/",
            headers=user_headers,
            json={"number": self.VEHICLE_NUMBER},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_delete_vehicle_success(self, client, user_headers):
        """User should be able to remove a vehicle they own."""
        # Add first
        client.post(
            "/user/vehicle/add/",
            headers=user_headers,
            json={"number": self.VEHICLE_NUMBER},
        )

        # Now delete
        response = client.delete(
            "/user/vehicle/remove/",
            headers=user_headers,
            json={"number": self.VEHICLE_NUMBER},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_delete_vehicle_not_found(self, client, user_headers):
        """Deleting a vehicle that doesn't exist should return 4xx."""
        response = client.delete(
            "/user/vehicle/remove/",
            headers=user_headers,
            json={"number": "XX00YY0000"},  # never added
        )

        assert response.status_code in (400, 404)

    def test_add_vehicle_unauthenticated(self, client):
        """Request without token should return 401."""
        response = client.post(
            "/user/vehicle/add/",
            json={"number": self.VEHICLE_NUMBER},
        )

        assert response.status_code == 401
