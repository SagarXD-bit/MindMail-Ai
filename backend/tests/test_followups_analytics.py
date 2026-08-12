"""Test follow-up CRUD and analytics endpoints."""

from fastapi.testclient import TestClient


class TestFollowUps:
    """Tests for follow-up management."""

    def test_create_follow_up(self, client, seeded_db):
        """Should create a follow-up reminder."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]

        response = client.post(
            "/api/follow-ups",
            json={
                "email_id": email_id,
                "reminder_at": "2026-12-31T10:00:00",
                "note": "Check for reply",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email_id"] == email_id
        assert data["status"] == "pending"
        assert data["note"] == "Check for reply"

    def test_complete_follow_up(self, client, seeded_db):
        """Should mark a follow-up as completed."""
        # Create one first
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]
        create_resp = client.post(
            "/api/follow-ups",
            json={"email_id": email_id, "reminder_at": "2026-12-31T10:00:00"},
        )
        fu_id = create_resp.json()["id"]

        # Complete it
        response = client.patch(
            f"/api/follow-ups/{fu_id}",
            json={"status": "completed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_snooze_follow_up(self, client, seeded_db):
        """Should snooze a follow-up."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]
        create_resp = client.post(
            "/api/follow-ups",
            json={"email_id": email_id, "reminder_at": "2026-12-31T10:00:00"},
        )
        fu_id = create_resp.json()["id"]

        response = client.patch(
            f"/api/follow-ups/{fu_id}",
            json={"status": "snoozed", "reminder_at": "2027-01-15T09:00:00"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "snoozed"

    def test_delete_follow_up(self, client, seeded_db):
        """Should delete a follow-up."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]
        create_resp = client.post(
            "/api/follow-ups",
            json={"email_id": email_id, "reminder_at": "2026-12-31T10:00:00"},
        )
        fu_id = create_resp.json()["id"]

        response = client.delete(f"/api/follow-ups/{fu_id}")
        assert response.status_code == 200

        # Verify it's gone
        list_resp = client.get("/api/follow-ups?status=pending")
        fu_ids = [fu["id"] for fu in list_resp.json()]
        assert fu_id not in fu_ids

    def test_list_follow_ups_by_status(self, client, seeded_db):
        """Should filter follow-ups by status."""
        list_resp = client.get("/api/emails?page_size=1")
        email_id = list_resp.json()["emails"][0]["id"]
        client.post(
            "/api/follow-ups",
            json={"email_id": email_id, "reminder_at": "2026-12-31T10:00:00"},
        )

        response = client.get("/api/follow-ups?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        for fu in data:
            assert fu["status"] == "pending"


class TestAnalytics:
    """Tests for analytics endpoint."""

    def test_analytics_returns_data(self, client, seeded_db):
        """Analytics should return comprehensive metrics."""
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_emails" in data
        assert data["total_emails"] > 0
        assert "emails_by_category" in data
        assert "emails_by_urgency" in data
        assert "emails_requiring_response" in data
        assert "pending_responses" in data
        assert "follow_ups_completed" in data
        assert "ai_accuracy" in data
        assert "response_rate" in data

    def test_analytics_category_distribution(self, client, seeded_db):
        """Category distribution should sum to total."""
        response = client.get("/api/analytics")
        data = response.json()
        cat_sum = sum(data["emails_by_category"].values())
        assert cat_sum == data["total_emails"]

    def test_analytics_ai_accuracy(self, client, seeded_db):
        """AI accuracy should be a percentage."""
        response = client.get("/api/analytics")
        data = response.json()
        assert 0 <= data["ai_accuracy"] <= 100


class TestSettings:
    """Tests for settings endpoint."""

    def test_get_settings(self, client, seeded_db):
        """Should return current settings."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "default_reply_tone" in data
        assert "auto_categorize" in data

    def test_update_settings(self, client, seeded_db):
        """Should update settings."""
        response = client.put(
            "/api/settings",
            json={"default_reply_tone": "concise"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_reply_tone"] == "concise"
