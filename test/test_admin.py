

def _create_epass(client, user_headers):
    """Utility: create an e-pass as a normal user and return the ticket_id."""
    resp = client.post("/user/support/epass", headers=user_headers, json={
        "vehicle_no": "DL01AB1234",
        "contact":    "9876543210",
        "guest_name": "guest visitor",
        "purpose":    "Meeting",
        "arrival":    "2025-12-01T10:00:00",
        "departure":  "2025-12-01T18:00:00",
    })
    print(resp.json())
    return resp.json()["ticket_id"]


def _create_complaint(client, user_headers):
    """Utility: create a complaint as a normal user and return the ticket_id."""
    resp = client.post("/user/support/complaint", headers=user_headers, json={
        "category":       "Electrical",
        "subject":        "Power outage",
        "description":    "No electricity since morning.",
        "has_attachment": False,
        "attachment":     None,
    })
    return resp.json()["ticket_id"]

class TestAdminUserManagement:

    def test_list_users_success(self, client, admin_headers, registered_user):
        """Admin should be able to list all users."""
        response = client.get("/admin/users", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert type(body["data"])==list or type(body["data"])!=None

    def test_list_users_as_normal_user(self, client, user_headers):
        """Normal user should be blocked from admin routes (403)."""
        response = client.get("/admin/users", headers=user_headers)

        assert response.status_code == 403

    def test_list_users_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/admin/users")

        assert response.status_code == 401

    def test_get_single_user_profile(self, client, admin_headers, registered_user):
        """Admin should be able to view any user's full profile."""
        response = client.get(
            "/admin/user/",
            headers=admin_headers,
            params={"user_id": registered_user["user_id"]},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["user_id"] == registered_user["user_id"]

    def test_get_nonexistent_user_profile(self, client, admin_headers):
        """Admin fetching a user_id that doesn't exist should return 4xx."""
        response = client.get(
            "/admin/user/",
            headers=admin_headers,
            params={"user_id": "nobody_here"},
        )

        assert response.status_code in (400, 404)

class TestAdminLogs:

    def test_get_user_logs(self, client, admin_headers, registered_user):
        """Admin should be able to retrieve user action logs."""
        response = client.get("/admin/users/logs", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        if body["data"]:
            log_actions = [l["action"] for l in body["data"]]
            assert "Register" in log_actions

    def test_get_user_logs_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/admin/users/logs")

        assert response.status_code == 401

class TestAdminEpass:

    def test_get_all_epasses(self, client, admin_headers, user_headers):
        """Admin should be able to see all e-pass requests."""
        _create_epass(client, user_headers)       

        response = client.get("/admin/epass", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "epasses" in body["data"]

    def test_approve_epass(self, client, admin_headers, user_headers):
        """Admin should be able to approve an e-pass."""
        ticket_id = _create_epass(client, user_headers)

        response = client.put(
            "/admin/epass/action",
            headers=admin_headers,
            params={"ticket_id": ticket_id},
            json={"status": "APPROVED", "remark": "Looks good"},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reject_epass(self, client, admin_headers, user_headers):
        """Admin should be able to reject an e-pass."""
        ticket_id = _create_epass(client, user_headers)

        response = client.put(
            "/admin/epass/action",
            headers=admin_headers,
            params={"ticket_id": ticket_id},
            json={"status": "REJECTED", "remark": "Invalid vehicle"},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_update_nonexistent_epass(self, client, admin_headers):
        """Updating a ticket_id that doesn't exist should return 4xx."""
        response = client.put(
            "/admin/epass/action",
            headers=admin_headers,
            params={"ticket_id": 999999},
            json={"status": "APPROVED", "remark": "Test"},
        )

        assert response.status_code in (400, 404)

    def test_get_epasses_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/admin/epass")

        assert response.status_code == 401


class TestAdminComplaint:

    def test_get_all_complaints(self, client, admin_headers, user_headers):
        """Admin should be able to see all complaints."""
        _create_complaint(client, user_headers) 

        response = client.get("/admin/complaints", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "complaints" in body["data"]

    def test_update_complaint_to_resolved(self, client, admin_headers, user_headers):
        """Admin should be able to update a complaint's status."""
        ticket_id = _create_complaint(client, user_headers)

        response = client.put(
            "/admin/complaint/action",
            headers=admin_headers,
            params={"ticket_id": ticket_id},
            json={"status": "RESOLVED", "remark": "Fixed by maintenance team"},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_update_nonexistent_complaint(self, client, admin_headers):
        """Updating a complaint that doesn't exist should return 4xx."""
        response = client.put(
            "/admin/complaint/action",
            headers=admin_headers,
            params={"ticket_id": 999999},
            json={"status": "RESOLVED", "remark": "N/A"},
        )

        assert response.status_code in (400, 404)

    def test_get_complaints_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/admin/complaints")

        assert response.status_code == 401


class TestAdminNotice:

    NOTICE_PAYLOAD = {
        "Type": "General",
        "body": "Society meeting scheduled for Sunday at 5 PM.",
        "user": "*",
    }

    def test_post_notice_success(self, client, admin_headers):
        """Admin should be able to post a notice."""
        response = client.post(
            "/admin/notice",
            headers=admin_headers,
            json=self.NOTICE_PAYLOAD,
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_get_notices_success(self, client, admin_headers):
        client.post("/admin/notice", headers=admin_headers, json=self.NOTICE_PAYLOAD)

        response = client.get("/admin/notice", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["status"] is True  
        assert type(body["data"])==list or type(body["data"])!=None
        assert len(body["data"]) >= 1

    def test_post_notice_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.post("/admin/notice", json=self.NOTICE_PAYLOAD)

        assert response.status_code == 401

    def test_post_notice_as_normal_user(self, client, user_headers):
        """Normal user should not be allowed to post notices (403)."""
        response = client.post(
            "/admin/notice",
            headers=user_headers,
            json=self.NOTICE_PAYLOAD,
        )

        assert response.status_code == 403
