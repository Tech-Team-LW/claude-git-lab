import unittest

from devops_portal import storage, team


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.data = storage.empty_data()

    def test_add_member(self):
        team.add_member(self.data, "Asha", "SRE")
        self.assertEqual(self.data["members"], [{"name": "Asha", "role": "SRE"}])

    def test_add_duplicate_is_rejected_ignoring_case(self):
        team.add_member(self.data, "Asha", "SRE")
        with self.assertRaises(ValueError):
            team.add_member(self.data, "asha", "Developer")

    def test_add_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            team.add_member(self.data, "   ", "SRE")

    def test_remove_member(self):
        team.add_member(self.data, "Asha", "SRE")
        team.remove_member(self.data, "ASHA")
        self.assertEqual(self.data["members"], [])

    def test_remove_missing_member(self):
        with self.assertRaises(ValueError):
            team.remove_member(self.data, "Nobody")

    # ----- team profile -----

    def test_add_member_with_team(self):
        team.add_member(self.data, "Asha", "SRE", " Platform ")
        self.assertEqual(
            self.data["members"], [{"name": "Asha", "role": "SRE", "team": "Platform"}]
        )

    def test_blank_team_is_not_stored(self):
        team.add_member(self.data, "Asha", "SRE", "   ")
        self.assertNotIn("team", self.data["members"][0])

    def test_get_profile_ignores_case(self):
        team.add_member(self.data, "Asha", "SRE", "Platform")
        self.assertEqual(
            team.get_profile(self.data, "ASHA"),
            {"name": "Asha", "role": "SRE", "team": "Platform"},
        )

    def test_get_profile_without_team(self):
        # Members saved before the team field existed have no "team" key.
        self.data["members"].append({"name": "Ravi", "role": "Developer"})
        self.assertEqual(team.get_profile(self.data, "Ravi")["team"], "")

    def test_get_profile_missing_member(self):
        with self.assertRaises(ValueError):
            team.get_profile(self.data, "Nobody")

    def test_get_profile_does_not_change_data(self):
        team.add_member(self.data, "Asha", "SRE")
        before = [dict(m) for m in self.data["members"]]
        profile = team.get_profile(self.data, "Asha")
        profile["team"] = "changed"
        self.assertEqual(self.data["members"], before)


if __name__ == "__main__":
    unittest.main()
