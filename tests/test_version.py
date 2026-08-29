import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import version


class VersionTests(unittest.TestCase):
    def test_release_build_version_takes_priority(self):
        build_info = SimpleNamespace(APP_VERSION="9.8.7")

        with patch.dict("sys.modules", {"src.build_info": build_info}):
            self.assertEqual(version.get_app_version(), "9.8.7")

    def test_project_version_is_read_from_pyproject(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            pyproject = Path(temp_dir) / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "todo-program"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )

            self.assertEqual(version.read_project_version(pyproject), "1.2.3")

    def test_missing_project_version_returns_development_label(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "pyproject.toml"

            self.assertEqual(version.read_project_version(missing), "dev")


if __name__ == "__main__":
    unittest.main()
