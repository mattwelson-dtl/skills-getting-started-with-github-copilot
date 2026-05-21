from copy import deepcopy

from src import app as app_module


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()

    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant_to_activity(client):
    response = client.post(
        "/activities/Tennis/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up sam@mergington.edu for Tennis"}
    assert app_module.activities["Tennis"]["participants"] == ["sam@mergington.edu"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Robotics/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_full_activity(client):
    original = deepcopy(app_module.activities["Tennis"])
    app_module.activities["Tennis"]["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(app_module.activities["Tennis"]["max_participants"])
    ]

    try:
        response = client.post(
            "/activities/Tennis/signup",
            params={"email": "sam@mergington.edu"},
        )
    finally:
        app_module.activities["Tennis"] = original

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed michael@mergington.edu from Chess Club"
    }
    assert app_module.activities["Chess Club"]["participants"] == [
        "daniel@mergington.edu"
    ]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Robotics/participants",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_student_not_signed_up(client):
    response = client.delete(
        "/activities/Tennis/participants",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }