import unittest
from unittest.mock import patch

from click.testing import CliRunner

from debate_connector import __version__
from debate_connector.cli import cli


class CliTests(unittest.TestCase):
    def test_short_version_flag_prints_version_only(self):
        result = CliRunner().invoke(cli, ["--v"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{__version__}\n")

    def test_top_level_test_flag_runs_openai_bridge_test(self):
        with patch("debate_connector.cli.run_test", return_value=0) as run_test:
            result = CliRunner().invoke(cli, ["--test"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "")
        run_test.assert_called_once_with()

    def test_top_level_test_flag_propagates_failure(self):
        with patch("debate_connector.cli.run_test", return_value=1):
            result = CliRunner().invoke(cli, ["--test"])

        self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
