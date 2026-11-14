from copy import deepcopy


def test_root_redirects_to_activity_page(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_includes_details_and_participants(client, activity_data):
    # Arrange
    expected_activities = deepcopy(activity_data)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities
    assert activity_data == expected_activities


def test_static_activity_page_is_served(client):
    # Arrange
    url = "/static/index.html"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'id="activities-list"' in response.text


def test_missing_static_asset_returns_not_found(client):
    # Arrange
    url = "/static/missing-asset.html"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 404
