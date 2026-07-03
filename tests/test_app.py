from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(deepcopy(original))


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "/static/index.html" in response.url.path


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate():
    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregistered_activity_returns_404():
    response = client.delete("/activities/Unknown/unregister", params={"email": "x@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_activity_removes_participant():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant():
    email = "absentstudent@mergington.edu"
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
