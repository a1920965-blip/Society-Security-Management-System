
import pytest



#  TICKET STATUS OVERVIEW


class TestTicketStatus:

    def test_status_authenticated(self, client, user_headers):
        """Authenticated user should get a status summary (even if empty)."""
        response = client.get("/user/status/", headers=user_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "complaints" in body["data"]
        assert "epasses" in body["data"]

    def test_status_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/user/status/")

        assert response.status_code == 401



#  COMPLAINT


class TestComplaint:

    COMPLAINT_PAYLOAD = {
        "category":       "Maintenance",
        "subject":        "Water leakage",
        "description":    "Water is leaking from the ceiling in block B.",
        "has_attachment": False,
        "attachment":     None,
    }

    def test_post_complaint_success(self, client, user_headers):
        """Authenticated user should be able to submit a complaint."""
        response = client.post(
            "/user/complaint",
            headers=user_headers,
            json=self.COMPLAINT_PAYLOAD,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "ticket_id" in body           # must return a ticket_id

    def test_post_complaint_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.post("/user/complaint", json=self.COMPLAINT_PAYLOAD)

        assert response.status_code == 401

    def test_get_complaint_success(self, client, user_headers):
        """User should be able to fetch the complaint they submitted."""
        # Step 1 — create the complaint
        post_resp = client.post(
            "/user/complaint",
            headers=user_headers,
            json=self.COMPLAINT_PAYLOAD,
        )
        ticket_id = post_resp.json()["ticket_id"]

        # Step 2 — fetch by ticket_id
        response = client.get(
            "/user/complaint",
            headers=user_headers,
            params={"ticket_id": ticket_id},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["ticket_id"] == ticket_id
        assert data["subject"] == self.COMPLAINT_PAYLOAD["subject"]
        assert data["category"] == self.COMPLAINT_PAYLOAD["category"]

    def test_get_complaint_not_found(self, client, user_headers):
        """Fetching a ticket that doesn't exist should return 4xx."""
        response = client.get(
            "/user/complaint",
            headers=user_headers,
            params={"ticket_id": 999999},
        )

        assert response.status_code in (400, 404)

    def test_get_complaint_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/user/complaint", params={"ticket_id": 1})

        assert response.status_code == 401



#  E-PASS


class TestEpass:

    EPASS_PAYLOAD = {
        "vehicle_no": "DL01AB1234",
        "contact":    "9876543210",
        "guest_name": "John Doe",
        "purpose":    "Family visit",
        "arrival":    "2025-12-01T10:00:00",
        "departure":  "2025-12-01T18:00:00",
    }

    def test_post_epass_success(self, client, user_headers):
        """Authenticated user should be able to create an e-pass request."""
        response = client.post(
            "/user/epass",
            headers=user_headers,
            json=self.EPASS_PAYLOAD,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "ticket_id" in body          # must return a ticket_id

    def test_post_epass_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.post("/user/epass", json=self.EPASS_PAYLOAD)

        assert response.status_code == 401

    def test_get_epass_success(self, client, user_headers):
        """User should be able to fetch the e-pass they created."""
        # Step 1 — create
        post_resp = client.post(
            "/user/epass",
            headers=user_headers,
            json=self.EPASS_PAYLOAD,
        )
        ticket_id = post_resp.json()["ticket_id"]

        # Step 2 — fetch
        response = client.get(
            "/user/epass",
            headers=user_headers,
            params={"ticket_id": ticket_id},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["ticket_id"] == ticket_id
        assert data["guest_name"] == self.EPASS_PAYLOAD["guest_name"]
        assert data["purpose"] == self.EPASS_PAYLOAD["purpose"]

    def test_get_epass_not_found(self, client, user_headers):
        """Fetching a ticket that doesn't exist should return 4xx."""
        response = client.get(
            "/user/epass",
            headers=user_headers,
            params={"ticket_id": 999999},
        )

        assert response.status_code in (400, 404)

    def test_get_epass_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/user/epass", params={"ticket_id": 1})

        assert response.status_code == 401
