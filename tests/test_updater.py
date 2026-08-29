import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import updater


class UpdaterTests(unittest.TestCase):
    def test_newer_release_is_detected_by_semantic_version(self):
        self.assertTrue(updater.is_newer_version("0.0.7", "0.0.6"))
        self.assertTrue(updater.is_newer_version("1.0.0", "0.9.9"))
        self.assertFalse(updater.is_newer_version("0.0.6", "0.0.6"))
        self.assertFalse(updater.is_newer_version("0.0.5", "0.0.6"))

    def test_release_payload_selects_the_windows_executable(self):
        payload = {
            "tag_name": "v0.0.7",
            "html_url": "https://example.test/releases/v0.0.7",
            "assets": [
                {
                    "name": "To-do.exe",
                    "browser_download_url": "https://example.test/To-do.exe",
                    "digest": "sha256:abc123",
                    "size": 123,
                }
            ],
        }

        release = updater.release_from_payload(payload)

        self.assertEqual(release.version, "0.0.7")
        self.assertEqual(release.digest, "abc123")
        self.assertEqual(release.size, 123)

    def test_release_payload_rejects_a_missing_executable(self):
        with self.assertRaises(updater.UpdateError):
            updater.release_from_payload({"tag_name": "v0.0.7", "assets": []})

    def test_download_verifies_the_github_digest(self):
        content = b"new executable"
        release = updater.ReleaseInfo(
            version="0.0.7",
            page_url="https://example.test/releases/v0.0.7",
            download_url="https://example.test/To-do.exe",
            digest=hashlib.sha256(content).hexdigest(),
            size=len(content),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "To-do-update.exe"
            with patch("src.updater.urlopen", return_value=io.BytesIO(content)):
                updater.download_release(release, destination)

            self.assertEqual(destination.read_bytes(), content)

    def test_download_removes_a_file_with_the_wrong_digest(self):
        release = updater.ReleaseInfo(
            version="0.0.7",
            page_url="https://example.test/releases/v0.0.7",
            download_url="https://example.test/To-do.exe",
            digest="0" * 64,
            size=3,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "To-do-update.exe"
            with (
                patch("src.updater.urlopen", return_value=io.BytesIO(b"bad")),
                self.assertRaises(updater.UpdateError),
            ):
                updater.download_release(release, destination)

            self.assertFalse(destination.exists())

    def test_replace_executable_launches_the_new_file(self):
        launched = []
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "downloaded.exe"
            target = Path(temp_dir) / "To-do.exe"
            source.write_bytes(b"new")
            target.write_bytes(b"old")

            updater.replace_executable(source, target, launcher=launched.append)

            self.assertEqual(target.read_bytes(), b"new")
            self.assertEqual(launched, [target])
            self.assertFalse(Path(f"{target}.bak").exists())

    def test_replace_executable_restores_the_old_file_if_launch_fails(self):
        def fail_to_launch(path):
            raise OSError("launch failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "downloaded.exe"
            target = Path(temp_dir) / "To-do.exe"
            source.write_bytes(b"new")
            target.write_bytes(b"old")

            with self.assertRaises(OSError):
                updater.replace_executable(source, target, launcher=fail_to_launch)

            self.assertEqual(target.read_bytes(), b"old")


if __name__ == "__main__":
    unittest.main()
