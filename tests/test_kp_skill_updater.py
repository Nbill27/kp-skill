"""Unit tests for the kp-skill updater; no network and no GitHub needed.

Run from the repository root:

    python -m unittest discover -s tests -p "test_kp_skill_updater.py" -v
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "kerja-praktek-bina-insani"
    / "scripts"
    / "kp-skill.py"
)
SPEC = importlib.util.spec_from_file_location("kp_skill_updater", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _make_skill(directory: Path, version: str) -> Path:
    skill = directory / "kerja-praktek-bina-insani"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: kerja-praktek-bina-insani\n---\n\nVersion {version}.\n",
        encoding="utf-8",
    )
    shutil.copy2(SCRIPT, skill / "scripts" / "kp-skill.py")
    return skill


def _make_release_zip(directory: Path, version: str) -> Path:
    """A minimal release zip: a repo root with a passing stub validator."""
    root = directory / f"release-{version}"
    skill = root / "skills" / "kerja-praktek-bina-insani"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: kerja-praktek-bina-insani\n---\n\nVersion {version}.\n",
        encoding="utf-8",
    )
    shutil.copy2(SCRIPT, skill / "scripts" / "kp-skill.py")
    validator = root / "scripts" / "validate_package.py"
    validator.parent.mkdir(parents=True, exist_ok=True)
    validator.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    archive = directory / f"kp-skill-{version}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(directory))
    return archive


class VersionTests(unittest.TestCase):
    def test_parse_and_compare(self):
        self.assertEqual(MODULE.parse_version("v2.3.0"), (2, 3, 0))
        self.assertEqual(MODULE.parse_version("2.2.1"), (2, 2, 1))
        self.assertLess(MODULE.compare_versions((2, 2, 0), (2, 2, 1)), 0)
        self.assertEqual(MODULE.compare_versions((2, 2, 1), (2, 2, 1)), 0)
        self.assertGreater(MODULE.compare_versions((2, 3, 0), (2, 2, 1)), 0)
        with self.assertRaises(MODULE.UpdaterError):
            MODULE.parse_version("banana")

    def test_read_installed_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _make_skill(Path(tmp), "2.2.0")
            self.assertEqual(MODULE.read_installed_version(skill), (2, 2, 0))


class ExtractionTests(unittest.TestCase):
    def test_rejects_dotdot_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("../evil.txt", "x")
            with self.assertRaises(MODULE.UpdaterError):
                MODULE.safe_extract_zip(archive, root / "out")

    def test_rejects_absolute_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("/tmp/evil.txt", "x")
            with self.assertRaises(MODULE.UpdaterError):
                MODULE.safe_extract_zip(archive, root / "out")

    def test_accepts_normal_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "good.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("pkg/file.txt", "hello")
            out = root / "out"
            MODULE.safe_extract_zip(archive, out)
            self.assertEqual((out / "pkg" / "file.txt").read_text(), "hello")


class Sha256Tests(unittest.TestCase):
    def _release_with_sums(self, archive: Path, digest: str):
        def fake_download(url: str, destination: Path):
            destination.write_text(f"{digest}  release.zip\n", encoding="utf-8")
            return destination

        return {
            "tag": "v2.2.1",
            "version": "2.2.1",
            "version_tuple": (2, 2, 1),
            "assets": [
                {
                    "name": "SHA256SUMS.txt",
                    "browser_download_url": "https://example.invalid/SHA256SUMS.txt",
                }
            ],
        }, fake_download

    def test_verifies_matching_hash(self):
        import hashlib

        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "release.zip"
            archive.write_bytes(b"fake release")
            digest = hashlib.sha256(b"fake release").hexdigest()
            release, fake_download = self._release_with_sums(archive, digest)
            with patch.object(MODULE, "download_file", side_effect=fake_download):
                self.assertTrue(MODULE.verify_sha256_if_available(release, archive))

    def test_refuses_mismatched_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "release.zip"
            archive.write_bytes(b"fake release")
            release, fake_download = self._release_with_sums(archive, "0" * 64)
            with patch.object(MODULE, "download_file", side_effect=fake_download):
                with self.assertRaises(MODULE.UpdaterError):
                    MODULE.verify_sha256_if_available(release, archive)

    def test_no_asset_is_not_a_checksum_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "release.zip"
            archive.write_bytes(b"fake release")
            release = {"tag": "v2.2.1", "version": "2.2.1", "assets": []}
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertFalse(MODULE.verify_sha256_if_available(release, archive))
            self.assertIn("No SHA256SUMS.txt", stdout.getvalue())


class CheckUpdateTests(unittest.TestCase):
    def test_reports_update_available(self):
        fake = {
            "tag": "v2.3.0",
            "version": "2.3.0",
            "version_tuple": (2, 3, 0),
            "name": "v2.3.0",
            "html_url": "https://example.invalid/r",
            "zipball_url": "https://example.invalid/z",
        }
        with patch.object(MODULE, "read_installed_version", return_value=(2, 2, 1)), patch.object(
            MODULE, "fetch_latest_release", return_value=fake
        ):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = MODULE.main(["check-update"])
            self.assertEqual(code, 2)
            self.assertIn("Update available", stdout.getvalue())

    def test_reports_up_to_date(self):
        fake = {
            "tag": "v2.2.1",
            "version": "2.2.1",
            "version_tuple": (2, 2, 1),
            "name": "v2.2.1",
            "html_url": "https://example.invalid/r",
            "zipball_url": "https://example.invalid/z",
        }
        with patch.object(MODULE, "read_installed_version", return_value=(2, 2, 1)), patch.object(
            MODULE, "fetch_latest_release", return_value=fake
        ):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = MODULE.main(["check-update"])
            self.assertEqual(code, 0)
            self.assertIn("Up to date", stdout.getvalue())


class UpdateRollbackTests(unittest.TestCase):
    def test_update_then_rollback_with_local_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / "cache"
            install_root = root / "skills"
            skill = _make_skill(install_root, "2.2.0")
            archive = _make_release_zip(root, "2.2.1")
            env = {
                "XDG_CACHE_HOME": str(cache),
                "KP_SKILL_UPDATER_SKILL_DIR": str(skill),
            }
            with patch.dict(os.environ, env):
                code = MODULE.main(
                    ["update", "--zip", str(archive), "--yes"]
                )
            self.assertEqual(code, 0)
            self.assertEqual(MODULE.read_installed_version(skill), (2, 2, 1))
            with patch.dict(os.environ, env):
                found = MODULE.list_backups()
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["from_version"], "2.2.0")
            self.assertEqual(found[0]["to_version"], "2.2.1")
            with patch.dict(os.environ, env):
                code = MODULE.main(["rollback", "--yes"])
            self.assertEqual(code, 0)
            self.assertEqual(MODULE.read_installed_version(skill), (2, 2, 0))

    def test_update_refuses_older_release_without_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "skills"
            skill = _make_skill(install_root, "2.2.1")
            archive = _make_release_zip(root, "2.2.0")
            env = {
                "XDG_CACHE_HOME": str(root / "cache"),
                "KP_SKILL_UPDATER_SKILL_DIR": str(skill),
            }
            with patch.dict(os.environ, env):
                code = MODULE.main(["update", "--zip", str(archive), "--yes"])
            self.assertEqual(code, 1)
            self.assertEqual(MODULE.read_installed_version(skill), (2, 2, 1))

    def test_update_validates_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "skills"
            skill = _make_skill(install_root, "2.2.0")
            archive = _make_release_zip(root, "2.2.1")
            env = {
                "XDG_CACHE_HOME": str(root / "cache"),
                "KP_SKILL_UPDATER_SKILL_DIR": str(skill),
            }
            with patch.dict(os.environ, env):
                code = MODULE.main(
                    ["update", "--zip", str(archive), "--to", "2.3.0", "--yes"]
                )
            self.assertEqual(code, 1)
            self.assertEqual(MODULE.read_installed_version(skill), (2, 2, 0))


if __name__ == "__main__":
    unittest.main()
