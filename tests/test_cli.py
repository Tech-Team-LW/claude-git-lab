import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from devops_portal import cli


class CliTests(unittest.TestCase):
    """Runs real commands against a throwaway data file."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        data_file = str(Path(self.tmp.name) / "portal.json")
        self.env = mock.patch.dict(os.environ, {"PORTAL_DATA": data_file})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def run_cli(self, *argv):
        """Run the CLI and return (exit_code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_team_add_then_list(self):
        self.assertEqual(self.run_cli("team", "add", "Asha", "SRE")[0], 0)
        code, out, _ = self.run_cli("team", "list")
        self.assertEqual(code, 0)
        self.assertIn("Asha", out)
        self.assertIn("SRE", out)

    def test_empty_team_list_gives_hint(self):
        code, out, _ = self.run_cli("team", "list")
        self.assertEqual(code, 0)
        self.assertIn("No team members yet", out)

    def test_error_goes_to_stderr_with_exit_code_1(self):
        code, out, err = self.run_cli("team", "remove", "Nobody")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("No member named 'Nobody'", err)

    def test_service_check_returns_1_when_down(self):
        self.run_cli("service", "add", "web", "http://localhost:5000/health")
        with mock.patch("devops_portal.services.check_url", return_value=(False, "refused")):
            code, out, _ = self.run_cli("service", "check")
        self.assertEqual(code, 1)
        self.assertIn("DOWN", out)

    def test_service_check_returns_0_when_up(self):
        self.run_cli("service", "add", "web", "http://localhost:5000/health")
        with mock.patch("devops_portal.services.check_url", return_value=(True, "HTTP 200")):
            code, out, _ = self.run_cli("service", "check", "web")
        self.assertEqual(code, 0)
        self.assertIn("UP", out)

    def test_sysinfo(self):
        code, out, _ = self.run_cli("sysinfo")
        self.assertEqual(code, 0)
        self.assertIn("Hostname:", out)


if __name__ == "__main__":
    unittest.main()
