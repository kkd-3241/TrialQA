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
    """Reset the activities state before each test."""
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_all():
    """GET /activities returns the full activities dictionary."""
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "Chess Club" in data


def test_get_activities_has_expected_fields():
    """Each activity contains the required fields."""
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    for name, details in response.json().items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_signup_adds_participant():
    """POST /activities/{name}/signup appends the email to participants."""
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


def test_signup_returns_success_message():
    """POST /activities/{name}/signup returns a confirmation message."""
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
    assert "message" in response.json()


def test_signup_duplicate_returns_400():
    """Signing up the same student twice returns HTTP 400."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in Chess Club

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404():
    """Signing up for a non-existent activity returns HTTP 404."""
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant():
    """DELETE /activities/{name}/signup removes the email from participants."""
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
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_enrolled_returns_400():
    """Unregistering a student not enrolled returns HTTP 400."""
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400


def test_unregister_unknown_activity_returns_404():
    """Unregistering from a non-existent activity returns HTTP 404."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
