import tempfile
import unittest
from pathlib import Path

from devops_portal import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "sub" / "portal.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_gives_empty_data(self):
        self.assertEqual(storage.load(self.path), storage.empty_data())

    def test_save_then_load(self):
        data = {"members": [{"name": "Asha", "role": "SRE"}], "services": []}
        storage.save(data, self.path)  # also creates the "sub" folder
        self.assertEqual(storage.load(self.path), data)

    def test_missing_keys_are_filled_in(self):
        self.path.parent.mkdir()
        self.path.write_text('{"members": []}')
        self.assertEqual(storage.load(self.path)["services"], [])

    def test_invalid_json_raises_value_error(self):
        self.path.parent.mkdir()
        self.path.write_text("not json")
        with self.assertRaises(ValueError):
            storage.load(self.path)


if __name__ == "__main__":
    unittest.main()
