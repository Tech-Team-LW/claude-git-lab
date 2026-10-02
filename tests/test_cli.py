import contextlib
import io
import json
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

    def test_team_profile_shows_name_role_and_team(self):
        self.run_cli("team", "add", "Asha", "SRE", "--team", "Platform")
        code, out, err = self.run_cli("team", "profile", "asha")
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "Name: Asha\nRole: SRE\nTeam: Platform\n")

    def test_team_profile_without_team(self):
        self.run_cli("team", "add", "Ravi", "Developer")
        code, out, _ = self.run_cli("team", "profile", "Ravi")
        self.assertEqual(code, 0)
        self.assertIn("Team: (not set)", out)

    def test_team_profile_reads_old_data_file(self):
        # A file written before members had a team must still work.
        Path(os.environ["PORTAL_DATA"]).write_text(
            '{"members": [{"name": "Asha", "role": "SRE"}], "services": []}'
        )
        code, out, _ = self.run_cli("team", "profile", "Asha")
        self.assertEqual(code, 0)
        self.assertIn("Role: SRE", out)

    def test_team_profile_unknown_member(self):
        code, out, err = self.run_cli("team", "profile", "Nobody")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("No member named 'Nobody'", err)

    def test_team_list_does_not_show_team(self):
        self.run_cli("team", "add", "Asha", "SRE", "--team", "Platform")
        code, out, _ = self.run_cli("team", "list")
        self.assertEqual(code, 0)
        self.assertIn("Asha", out)
        self.assertNotIn("Platform", out)

    def test_blank_team_through_cli_is_not_stored(self):
        self.run_cli("team", "add", "Asha", "SRE", "--team", "  ")
        stored = json.loads(Path(os.environ["PORTAL_DATA"]).read_text())
        self.assertNotIn("team", stored["members"][0])

    def test_team_profile_requires_name(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                self.run_cli("team", "profile")
        self.assertEqual(ctx.exception.code, 2)

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
