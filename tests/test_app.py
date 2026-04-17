"""
Backend tests for the Mergington High School API.

Uses the AAA (Arrange-Act-Assert) pattern to structure tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to a clean state before each test."""
    original_state = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange – no additional setup needed; default activities exist

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert "Chess Club" in data

    def test_activity_has_expected_fields(self, client):
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for activity in data.values():
            assert expected_fields.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignupForActivity:
    def test_successful_signup(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "another@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self, client):
        # Arrange – michael is already in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_full_activity_returns_400(self, client):
        # Arrange – fill Chess Club to its max_participants of 12
        activity_name = "Chess Club"
        for i in range(10):
            activities[activity_name]["participants"].append(f"filler{i}@mergington.edu")

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"},
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregisterFromActivity:
    def test_successful_unregister(self, client):
        # Arrange – michael is already in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_confirmation_message(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            "/activities/NonexistentActivity/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_400(self, client):
        # Arrange – this student was never registered
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
