from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def activity_data():
    original_activities = deepcopy(activities)
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays after school",
            "max_participants": 12,
            "participants": [
                "registered@mergington.edu",
                "other@mergington.edu",
            ],
        },
        "Programming Class": {
            "description": "Learn programming",
            "schedule": "Tuesdays after school",
            "max_participants": 20,
            "participants": [],
        },
    })
    try:
        yield activities
    finally:
        activities.clear()
        activities.update(original_activities)


@pytest.fixture
def client(activity_data):
    with TestClient(app) as test_client:
        yield test_client
