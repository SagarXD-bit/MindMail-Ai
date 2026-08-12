"""Test the health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client):
    """Health endpoint should return status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
