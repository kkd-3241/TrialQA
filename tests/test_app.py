"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participants before each test to avoid state leakage."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, data in activities.items():
        data["participants"] = original_participants[name]


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange / Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        # Arrange / Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        # Arrange / Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data


class TestSignupForActivity:
    def test_signup_success(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant(self, client):
        # Arrange
        email = "teststudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email in response.json()[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    def test_unregister_success(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_not_enrolled_returns_404(self, client):
        # Arrange
        email = "notenrolled@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
