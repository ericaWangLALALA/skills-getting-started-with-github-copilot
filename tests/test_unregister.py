import unittest
from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(activities)
        self.client = TestClient(app)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)
        self.client.close()

    def test_unregister_removes_only_selected_participant_and_allows_signup(self):
        email = activities["Chess Club"]["participants"][0]
        other_participants = activities["Chess Club"]["participants"][1:]
        response = self.client.delete(
            "/activities/Chess%20Club/unregister", params={"email": email}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "message": f"Unregistered {email} from Chess Club"
        })
        updated = self.client.get("/activities").json()
        self.assertEqual(updated["Chess Club"]["participants"], other_participants)
        self.assertEqual(
            updated["Programming Class"], self.original_activities["Programming Class"]
        )
        self.assertEqual(
            self.client.post(
                "/activities/Chess%20Club/signup", params={"email": email}
            ).status_code, 200
        )

    def test_unregister_last_participant_leaves_empty_list(self):
        email = "student+club@mergington.edu"
        activities["Chess Club"]["participants"] = [email]

        response = self.client.delete(
            "/activities/Chess%20Club/unregister", params={"email": email}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get("/activities").json()["Chess Club"]["participants"], []
        )

    def test_invalid_unregister_requests_do_not_change_activities(self):
        for activity, email, detail in [
            ("Unknown", "student@mergington.edu", "Activity not found"),
            ("Chess Club", "unknown@mergington.edu",
             "Student is not signed up for this activity"),
        ]:
            with self.subTest(activity=activity):
                response = self.client.delete(
                    f"/activities/{activity}/unregister", params={"email": email}
                )
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {"detail": detail})
                self.assertEqual(activities, self.original_activities)


if __name__ == "__main__":
    unittest.main()
