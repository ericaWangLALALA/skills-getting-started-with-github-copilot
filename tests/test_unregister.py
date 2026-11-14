from copy import deepcopy

import pytest


def test_unregister_removes_only_selected_participant(client, activity_data):
    # Arrange
    email = activity_data["Chess Club"]["participants"][0]
    expected_activities = deepcopy(activity_data)
    expected_activities["Chess Club"]["participants"].remove(email)

    # Act
    response = client.delete(
        "/activities/Chess%20Club/unregister", params={"email": email}
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert updated_activities == expected_activities


def test_unregister_last_participant_leaves_empty_list(client, activity_data):
    # Arrange
    email = "student+club@mergington.edu"
    activity_data["Chess Club"]["participants"] = [email]
    expected_activities = deepcopy(activity_data)
    expected_activities["Chess Club"]["participants"] = []

    # Act
    response = client.delete(
        "/activities/Chess%20Club/unregister", params={"email": email}
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert updated_activities == expected_activities


def test_participant_can_signup_again_after_unregistering(client, activity_data):
    # Arrange
    email = activity_data["Chess Club"]["participants"][-1]
    expected_activities = deepcopy(activity_data)

    # Act
    unregister_response = client.delete(
        "/activities/Chess%20Club/unregister", params={"email": email}
    )
    signup_response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert unregister_response.status_code == 200
    assert signup_response.status_code == 200
    assert updated_activities == expected_activities


@pytest.mark.parametrize(
    "activity,email,detail",
    [
        ("Unknown", "student@mergington.edu", "Activity not found"),
        ("Chess%20Club", "unknown@mergington.edu",
         "Student is not signed up for this activity"),
    ],
)
def test_invalid_unregister_leaves_activities_unchanged(
    client, activity_data, activity, email, detail
):
    # Arrange
    original_activities = deepcopy(activity_data)
    url = f"/activities/{activity}/unregister"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": detail}
    assert activity_data == original_activities


def test_unregister_requires_email(client, activity_data):
    # Arrange
    original_activities = deepcopy(activity_data)

    # Act
    response = client.delete("/activities/Chess%20Club/unregister")

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"] and error["type"] == "missing"
        for error in response.json()["detail"]
    )
    assert activity_data == original_activities


def test_repeated_unregister_does_not_change_activities(client, activity_data):
    # Arrange
    email = activity_data["Chess Club"]["participants"][0]
    url = "/activities/Chess%20Club/unregister"
    first_response = client.delete(url, params={"email": email})
    expected_activities = deepcopy(activity_data)

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_data == expected_activities
