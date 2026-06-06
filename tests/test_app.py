import importlib
import urllib.parse

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client():
    module = importlib.reload(app_module)
    return TestClient(module.app)


def test_get_activities_returns_available_activities(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert activity_name in payload
    assert isinstance(payload[activity_name]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "jane.doe@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/signup",
        params={"email": email},
    )
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_returns_bad_request(client):
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@example.com"

    # Act
    first_response = client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/signup",
        params={"email": email},
    )
    second_response = client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant(client):
    # Arrange
    activity_name = "Math Club"
    email = "remove.me@mergington.edu"
    client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/signup",
        params={"email": email},
    )

    # Act
    response = client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/remove",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_not_found(client):
    # Arrange
    activity_name = "Gym Class"
    email = "notfound@example.com"

    # Act
    response = client.post(
        f"/activities/{urllib.parse.quote(activity_name)}/remove",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
