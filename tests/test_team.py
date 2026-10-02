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


if __name__ == "__main__":
    unittest.main()
