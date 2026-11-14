from copy import deepcopy

import pytest


def test_signup_adds_participant_to_selected_activity(client, activity_data):
    # Arrange
    email = "new+chess@mergington.edu"
    expected_activities = deepcopy(activity_data)
    expected_activities["Chess Club"]["participants"].append(email)

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert updated_activities == expected_activities


@pytest.mark.parametrize(
    "activity,email,status,detail",
    [
        ("Chess%20Club", "registered@mergington.edu", 400,
         "Student already signed up for this activity"),
        ("Unknown", "new@mergington.edu", 404, "Activity not found"),
    ],
)
def test_invalid_signup_leaves_activities_unchanged(
    client, activity_data, activity, email, status, detail
):
    # Arrange
    original_activities = deepcopy(activity_data)
    url = f"/activities/{activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert activity_data == original_activities


def test_signup_requires_email(client, activity_data):
    # Arrange
    original_activities = deepcopy(activity_data)

    # Act
    response = client.post("/activities/Chess%20Club/signup")

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"] and error["type"] == "missing"
        for error in response.json()["detail"]
    )
    assert activity_data == original_activities
