"""Test email API endpoints."""

from fastapi.testclient import TestClient


class TestEmailList:
    """Tests for email listing and filtering."""

    def test_list_emails(self, client, seeded_db):
        """Should return a paginated list of emails."""
        response = client.get("/api/emails?page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert "emails" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["emails"]) <= 5

    def test_search_emails(self, client, seeded_db):
        """Search should filter by subject/content/sender."""
        response = client.get("/api/emails?search=invoice")
        assert response.status_code == 200
        data = response.json()
        # At least one email contains "invoice"
        assert data["total"] >= 1

    def test_filter_by_category(self, client, seeded_db):
        """Filter by category should return only matching emails."""
        response = client.get("/api/emails?category=Spam")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for email in data["emails"]:
            assert email["classification"]["category"] == "Spam"

    def test_filter_by_urgency(self, client, seeded_db):
        """Filter by urgency should return only matching emails."""
        response = client.get("/api/emails?urgency=critical")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for email in data["emails"]:
            assert email["classification"]["urgency"] == "critical"

    def test_sort_newest(self, client, seeded_db):
        """Sort by newest should return most recent first."""
        response = client.get("/api/emails?sort=newest&page_size=5")
        assert response.status_code == 200
        emails = response.json()["emails"]
        if len(emails) >= 2:
            dates = [e["received_at"] for e in emails]
            assert dates[0] >= dates[1]

    def test_sort_urgency(self, client, seeded_db):
        """Sort by urgency should prioritize critical first."""
        response = client.get("/api/emails?sort=urgency&page_size=10")
        assert response.status_code == 200
        emails = response.json()["emails"]
        if len(emails) >= 2 and emails[0]["classification"] and emails[1]["classification"]:
            urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            first = urgency_order.get(emails[0]["classification"]["urgency"], 4)
            second = urgency_order.get(emails[1]["classification"]["urgency"], 4)
            assert first <= second


class TestEmailDetail:
    """Tests for single email retrieval."""

    def test_get_email_detail(self, client, seeded_db):
        """Should return full email with classification and replies."""
        # First get an email ID
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.get(f"/api/emails/{email_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == email_id
        assert "subject" in data
        assert "body_text" in data
        assert "classification" in data
        assert "replies" in data
        assert "follow_ups" in data

    def test_get_nonexistent_email(self, client, seeded_db):
        """Should return 404 for non-existent email."""
        response = client.get("/api/emails/99999")
        assert response.status_code == 404


class TestClassificationUpdate:
    """Tests for manual classification override."""

    def test_update_category(self, client, seeded_db):
        """Should allow manual category change."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.patch(
            f"/api/emails/{email_id}/classification",
            json={"category": "Personal"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Personal"
        assert data["is_manual_override"] is True

    def test_update_urgency(self, client, seeded_db):
        """Should allow manual urgency change."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.patch(
            f"/api/emails/{email_id}/classification",
            json={"urgency": "high"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["urgency"] == "high"
        assert data["is_manual_override"] is True


class TestStatusUpdate:
    """Tests for email status changes."""

    def test_mark_responded(self, client, seeded_db):
        """Should mark email as responded."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.patch(
            f"/api/emails/{email_id}/status",
            json={"status": "responded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "responded"

    def test_invalid_status(self, client, seeded_db):
        """Should reject invalid status."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.patch(
            f"/api/emails/{email_id}/status",
            json={"status": "invalid"},
        )
        assert response.status_code == 400
