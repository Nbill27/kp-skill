#!/usr/bin/env python3
"""Update a kp-skill installation from GitHub Releases.

This is the updater for the ``kerja-praktek-bina-insani`` Agent Skill.
It lives inside the skill folder (``skills/kerja-praktek-bina-insani/scripts/``)
so it is copied into every installation by the normal installers, and it
updates the installation it runs from. Standard library only, no ``pip
install`` step, no Git, no package manager.

Commands::

    python kp-skill.py version
    python kp-skill.py check-update [--json]
    python kp-skill.py update [--to 2.3.0] [--yes]
    python kp-skill.py rollback [--yes]

Version source: GitHub Releases (``https://github.com/Nbill27/kp-skill``).
The installed version is read from ``SKILL.md`` in the same installation.
``check-update`` never writes a file. ``update`` downloads the release
zipball, extracts it to a temporary directory, runs the package validator
from the extracted release, backs the current installation up outside the
skill folder, and only then replaces it. If the replacement fails, the
backup is restored. There is no automatic update.

Integrity note: GitHub generates release zipballs on demand and publishes
no checksum for them. When a release carries a ``SHA256SUMS.txt`` asset,
this updater downloads it and verifies the downloaded archive against the
entry for it before installing; only then is the update checksum-verified.
When there is no such asset, or it has no entry for the archive, integrity
is established by safe extraction plus ``scripts/validate_package.py`` from
the extracted release, and the updater says so instead of claiming a
checksum check.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

REPO_OWNER = "Nbill27"
REPO_NAME = "kp-skill"
SKILL_NAME = "kerja-praktek-bina-insani"
API_LATEST_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
API_RELEASE_BY_TAG_URL = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{{tag}}"
)
ZIPBALL_URL = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/zipball/{{tag}}"
)
REEXEC_ENV = "KP_SKILL_UPDATER_REEXEC"
SKILL_DIR_ENV = "KP_SKILL_UPDATER_SKILL_DIR"
VERSION_RE = re.compile(r"^Version\s+([0-9]+\.[0-9]+\.[0-9]+)\b", re.MULTILINE)
TAG_RE = re.compile(r"^v?([0-9]+\.[0-9]+\.[0-9]+)$")
SHA256_RE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(\S+)\s*$")
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
NETWORK_TIMEOUT_SECONDS = 30


class UpdaterError(Exception):
    """Expected user-facing failure: input, network, validation, or install."""


def parse_version(text: str) -> tuple[int, int, int]:
    """Parse ``2.3.0`` or ``v2.3.0`` into a comparable tuple."""
    match = TAG_RE.match(text.strip())
    if not match:
        raise UpdaterError(f"Not a version like 2.3.0: {text!r}")
    return tuple(int(part) for part in match.group(1).split("."))  # type: ignore[return-value]


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def compare_versions(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def skill_dir() -> Path:
    """The skill folder this script runs from, from ``__file__``, not cwd.

    When the updater re-executes itself from a temp copy (so it can replace
    its own folder), the original skill folder is passed in through
    ``KP_SKILL_UPDATER_SKILL_DIR``.
    """
    override = os.environ.get(SKILL_DIR_ENV)
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent


def read_installed_version(directory: Path | None = None) -> tuple[int, int, int]:
    """Read the ``Version X.Y.Z`` line from an installed ``SKILL.md``."""
    target = (directory or skill_dir()) / "SKILL.md"
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise UpdaterError(f"Cannot read installed SKILL.md at {target}: {exc}") from exc
    match = VERSION_RE.search(text)
    if not match:
        raise UpdaterError(f"Installed SKILL.md at {target} has no 'Version X.Y.Z' line")
    return parse_version(match.group(1))


def backup_root() -> Path:
    """Backups live outside the skill folder, so an update cannot delete them.

    Per-installation backups would be picked up as skills if they sat inside
    an agent skills directory, so they go to the user cache directory
    instead: ``~/.cache/kp-skill/backups`` on Linux/macOS and
    ``%LOCALAPPDATA%\\kp-skill\\backups`` on Windows.
    """
    if os.name == "nt":
        base = Path(
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or Path.home() / "AppData" / "Local"
        )
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "kp-skill" / "backups"


def _http_get_json(url: str) -> dict[str, Any]:
    try:
        installed_label = format_version(read_installed_version())
    except UpdaterError:
        installed_label = "unknown"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"kp-skill-updater/{installed_label}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise UpdaterError(
                "GitHub returned 404 for the release lookup. Check that the "
                "repository has a release for the requested version."
            ) from exc
        raise UpdaterError(f"GitHub request failed ({exc.code}): {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise UpdaterError(
            f"Cannot reach GitHub: {exc.reason}. Check the network connection "
            "and try again; nothing was changed."
        ) from exc
    except (OSError, ValueError) as exc:
        raise UpdaterError(f"GitHub request failed: {exc}") from exc


def fetch_latest_release() -> dict[str, Any]:
    """Return the latest GitHub Release: tag, version, zipball and page URL."""
    data = _http_get_json(API_LATEST_URL)
    tag = str(data.get("tag_name") or "")
    if not TAG_RE.match(tag):
        raise UpdaterError(f"Latest GitHub Release has an unexpected tag: {tag!r}")
    version = parse_version(tag)
    return {
        "tag": tag,
        "version": format_version(version),
        "version_tuple": version,
        "name": str(data.get("name") or tag),
        "html_url": str(data.get("html_url") or ""),
        "zipball_url": ZIPBALL_URL.format(tag=tag),
        "assets": [
            {
                "name": str(asset.get("name") or ""),
                "browser_download_url": str(asset.get("browser_download_url") or ""),
            }
            for asset in (data.get("assets") or [])
            if isinstance(asset, dict)
        ],
    }


def fetch_release_by_tag(tag: str) -> dict[str, Any]:
    """Return one GitHub Release by tag, for ``update --to``."""
    version = parse_version(tag)
    tag_name = f"v{format_version(version)}"
    data = _http_get_json(API_RELEASE_BY_TAG_URL.format(tag=tag_name))
    found = str(data.get("tag_name") or "")
    if found != tag_name:
        raise UpdaterError(
            f"GitHub returned tag {found!r} for requested release {tag_name!r}"
        )
    return {
        "tag": tag_name,
        "version": format_version(version),
        "version_tuple": version,
        "name": str(data.get("name") or tag_name),
        "html_url": str(data.get("html_url") or ""),
        "zipball_url": ZIPBALL_URL.format(tag=tag_name),
        "assets": [
            {
                "name": str(asset.get("name") or ""),
                "browser_download_url": str(asset.get("browser_download_url") or ""),
            }
            for asset in (data.get("assets") or [])
            if isinstance(asset, dict)
        ],
    }


def download_file(url: str, destination: Path) -> Path:
    """Download a URL to a new file, with a size cap. No partial file on error."""
    request = urllib.request.Request(url, headers={"User-Agent": "kp-skill-updater"})
    try:
        with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
            total = 0
            with destination.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise UpdaterError(
                            f"Download exceeds the {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MiB limit"
                        )
                    handle.write(chunk)
    except urllib.error.HTTPError as exc:
        raise UpdaterError(f"Download failed ({exc.code}): {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise UpdaterError(
            f"Cannot download the release: {exc.reason}. Nothing was changed."
        ) from exc
    except OSError as exc:
        raise UpdaterError(f"Cannot write the downloaded release: {exc}") from exc
    return destination


def verify_sha256_if_available(release: dict[str, Any], archive: Path) -> bool:
    """Verify the archive against a release ``SHA256SUMS.txt`` asset, if any.

    Returns True only when the asset exists, has an entry for this archive,
    and the hash matches. Returns False (with a printed note) when there is
    no asset or no matching entry; the caller then relies on safe extraction
    plus the package validator and must not claim a checksum check. Raises
    UpdaterError on a hash mismatch.
    """
    assets = release.get("assets") or []
    sums_asset = next(
        (asset for asset in assets if asset.get("name") == "SHA256SUMS.txt"), None
    )
    if sums_asset is None or not sums_asset.get("browser_download_url"):
        print(
            "No SHA256SUMS.txt asset on this release; integrity is established "
            "by safe extraction plus the package validator, not by a checksum."
        )
        return False
    sums_path = archive.parent / "SHA256SUMS.txt"
    download_file(str(sums_asset["browser_download_url"]), sums_path)
    try:
        entries: dict[str, str] = {}
        for line in sums_path.read_text(encoding="utf-8").splitlines():
            match = SHA256_RE.match(line.strip())
            if match:
                entries[Path(match.group(2)).name] = match.group(1).lower()
    except OSError as exc:
        raise UpdaterError(f"Cannot read the downloaded SHA256SUMS.txt: {exc}") from exc
    candidates = [
        archive.name,
        f"kp-skill-{release['version']}.zip",
        f"{REPO_NAME}-{release['version']}.zip",
    ]
    expected: str | None = None
    for name in candidates:
        if name in entries:
            expected = entries[name]
            break
    if expected is None:
        print(
            f"SHA256SUMS.txt has no entry for {archive.name}; "
            "not checksum-verified."
        )
        return False
    digest = hashlib.sha256()
    with archive.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise UpdaterError(
            f"SHA-256 mismatch for the downloaded release: expected {expected}, "
            f"got {digest.hexdigest()}. Refusing to install."
        )
    print("SHA-256 verified against SHA256SUMS.txt.")
    return True


def _is_within(directory: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(directory.resolve())
    except (ValueError, RuntimeError):
        return False
    return True


def safe_extract_zip(archive: Path, destination: Path) -> None:
    """Extract a zipball, rejecting absolute paths, ``..`` and symlinks."""
    try:
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                name = info.filename
                if not name or name.startswith("/") or ":" in name.split("/")[0]:
                    raise UpdaterError(f"Unsafe path in release archive: {name!r}")
                parts = Path(name).parts
                if any(part in ("", ".", "..") for part in parts):
                    raise UpdaterError(f"Unsafe path in release archive: {name!r}")
                is_symlink = (info.external_attr >> 16) & 0o120000 == 0o120000
                if is_symlink:
                    raise UpdaterError(f"Symlink in release archive refused: {name!r}")
                target = destination / name
                if not _is_within(destination, target):
                    raise UpdaterError(f"Unsafe path in release archive: {name!r}")
            zf.extractall(destination)
    except zipfile.BadZipFile as exc:
        raise UpdaterError(f"Downloaded release is not a valid zip archive: {exc}") from exc
    except OSError as exc:
        raise UpdaterError(f"Cannot extract the release archive: {exc}") from exc


def find_repo_root(extracted: Path) -> Path:
    """A zipball extracts to one top directory; return the one with ``skills/``."""
    if (extracted / "skills" / SKILL_NAME / "SKILL.md").is_file():
        return extracted
    candidates = [
        child
        for child in extracted.iterdir()
        if child.is_dir() and (child / "skills" / SKILL_NAME / "SKILL.md").is_file()
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise UpdaterError(
        "Downloaded release does not contain skills/kerja-praktek-bina-insani/SKILL.md"
    )


def validate_release(repo_root: Path, expected_version: tuple[int, int, int]) -> None:
    """Validate an extracted release before anything installed is touched."""
    validator = repo_root / "scripts" / "validate_package.py"
    if not validator.is_file():
        raise UpdaterError(
            f"Release is missing scripts/validate_package.py at {repo_root}"
        )
    updater = repo_root / "skills" / SKILL_NAME / "scripts" / "kp-skill.py"
    if not updater.is_file():
        raise UpdaterError(
            "Release does not contain skills/kerja-praktek-bina-insani/scripts/kp-skill.py. "
            "Updating to it would remove the updater itself; use the installer instead."
        )
    try:
        result = subprocess.run(
            [sys.executable, str(validator), "--root", str(repo_root)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UpdaterError(f"Cannot run the release validator: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise UpdaterError(
            "Release failed validation, refusing to install:\n" + detail[-2000:]
        )
    actual = read_installed_version(repo_root / "skills" / SKILL_NAME)
    if actual != expected_version:
        raise UpdaterError(
            f"Release SKILL.md says {format_version(actual)} but the release tag "
            f"is {format_version(expected_version)}; refusing to install."
        )

def _timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_backup(
    directory: Path, from_version: tuple[int, int, int], to_version: tuple[int, int, int]
) -> Path:
    """Copy the current installation outside the skill folder, with metadata."""
    root = backup_root()
    name = (
        f"{SKILL_NAME}-{format_version(from_version)}-to-"
        f"{format_version(to_version)}-{_timestamp()}"
    )
    backup_dir = root / name
    try:
        root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(directory, backup_dir / "skill")
        metadata = {
            "skill": SKILL_NAME,
            "from_version": format_version(from_version),
            "to_version": format_version(to_version),
            "installed_path": str(directory),
            "backup_path": str(backup_dir),
            "created_utc": _timestamp(),
        }
        (backup_dir / "backup.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        raise UpdaterError(f"Cannot create a backup before updating: {exc}") from exc
    return backup_dir


def list_backups() -> list[dict[str, Any]]:
    """Backups newest first, each with its metadata and skill copy."""
    root = backup_root()
    found: list[dict[str, Any]] = []
    if not root.is_dir():
        return found
    for candidate in root.iterdir():
        metadata_path = candidate / "backup.json"
        skill_copy = candidate / "skill" / "SKILL.md"
        if not candidate.is_dir() or not metadata_path.is_file() or not skill_copy.is_file():
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        metadata["backup_path"] = str(candidate)
        found.append(metadata)
    found.sort(key=lambda item: str(item.get("created_utc", "")), reverse=True)
    return found


def restore_backup(backup_dir: Path, directory: Path) -> tuple[int, int, int]:
    """Replace the installation with a backup copy. Raises on failure."""
    skill_copy = backup_dir / "skill"
    if not (skill_copy / "SKILL.md").is_file():
        raise UpdaterError(f"Backup at {backup_dir} has no skill copy to restore")
    if directory.is_dir():
        shutil.rmtree(directory)
    elif directory.exists():
        directory.unlink()
    shutil.copytree(skill_copy, directory)
    return read_installed_version(directory)


def _reexec_from_temp(argv: list[str]) -> int | None:
    """Re-run this script from a temp copy, so it can replace its own folder.

    Returns the re-executed exit code, or None when no re-exec is needed.
    Only update and rollback need it; version and check-update are read-only.
    """
    if os.environ.get(REEXEC_ENV) == "1":
        return None
    script = Path(__file__).resolve()
    try:
        script.relative_to(skill_dir())
    except ValueError:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="kp-skill-updater-"))
    try:
        copy = tmp / "kp-skill.py"
        shutil.copy2(script, copy)
        env = dict(
            os.environ,
            **{REEXEC_ENV: "1", SKILL_DIR_ENV: str(skill_dir())},
        )
        result = subprocess.run([sys.executable, str(copy), *argv], env=env)
        return result.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        raise UpdaterError("Refusing to proceed without --yes in non-interactive use")
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in ("y", "yes")


def _print_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def cmd_version(args: argparse.Namespace) -> int:
    directory = skill_dir()
    version = read_installed_version(directory)
    payload = {
        "installed": format_version(version),
        "skill": SKILL_NAME,
        "skill_dir": str(directory),
        "python": sys.version.split()[0],
        "backup_root": str(backup_root()),
    }
    _print_payload(payload, args.json)
    return 0


def cmd_check_update(args: argparse.Namespace) -> int:
    installed = read_installed_version()
    release = fetch_latest_release()
    latest = release["version_tuple"]
    comparison = compare_versions(installed, latest)
    payload = {
        "installed": format_version(installed),
        "latest": format_version(latest),
        "tag": release["tag"],
        "update_available": comparison < 0,
        "release_url": release["html_url"],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    elif comparison < 0:
        print(
            f"Update available: {format_version(installed)} -> "
            f"{format_version(latest)} ({release['tag']}). "
            f"Run: python kp-skill.py update"
        )
    elif comparison == 0:
        print(f"Up to date: {format_version(installed)} is the latest release.")
    else:
        print(
            f"Installed {format_version(installed)} is newer than the latest "
            f"release {format_version(latest)}."
        )
    return 2 if comparison < 0 else 0


def _prepare_release(
    args: argparse.Namespace, installed: tuple[int, int, int]
) -> tuple[Path, tuple[int, int, int], str, tempfile.TemporaryDirectory]:
    """Download or read a release zip, extract it safely, validate it.

    Returns (repo_root, target_version, tag, temp_dir). The caller owns
    the temp directory and must clean it up.
    """
    tmp = tempfile.TemporaryDirectory(prefix="kp-skill-release-")
    tmp_path = Path(tmp.name)
    try:
        if args.zip:
            archive = Path(args.zip).expanduser().resolve()
            if not archive.is_file():
                raise UpdaterError(f"Release zip not found: {archive}")
            target: tuple[int, int, int] | None = None
            if args.to:
                target = parse_version(args.to)
        else:
            if args.to:
                release = fetch_release_by_tag(args.to)
            else:
                release = fetch_latest_release()
            target = release["version_tuple"]
            archive = tmp_path / "release.zip"
            print(f"Downloading {release['tag']} ...")
            download_file(release["zipball_url"], archive)
            verify_sha256_if_available(release, archive)
        extracted = tmp_path / "extracted"
        extracted.mkdir(parents=True, exist_ok=True)
        safe_extract_zip(archive, extracted)
        repo_root = find_repo_root(extracted)
        if target is None:
            target = read_installed_version(repo_root / "skills" / SKILL_NAME)
        validate_release(repo_root, target)
    except Exception:
        tmp.cleanup()
        raise
    return repo_root, target, f"v{format_version(target)}", tmp


def cmd_update(args: argparse.Namespace) -> int:
    reexec_code = _reexec_from_temp(list(getattr(args, "_raw_argv", [])))
    if reexec_code is not None:
        return reexec_code
    directory = skill_dir()
    installed = read_installed_version(directory)
    tmp: tempfile.TemporaryDirectory | None = None
    try:
        repo_root, target, tag, tmp = _prepare_release(args, installed)
        comparison = compare_versions(installed, target)
        if comparison == 0:
            print(f"Already up to date: {format_version(installed)}.")
            return 0
        if comparison > 0 and not args.allow_downgrade:
            raise UpdaterError(
                f"Target {format_version(target)} is older than installed "
                f"{format_version(installed)}. Use rollback to go back, or "
                "pass --allow-downgrade to force it."
            )
        if not _confirm(
            f"Update {SKILL_NAME} {format_version(installed)} -> "
            f"{format_version(target)} ({tag})?",
            args.yes,
        ):
            print("Update cancelled; nothing was changed.")
            return 0
        new_skill = repo_root / "skills" / SKILL_NAME
        backup_dir = create_backup(directory, installed, target)
        try:
            shutil.rmtree(directory)
            shutil.copytree(new_skill, directory)
            actual = read_installed_version(directory)
        except (OSError, UpdaterError) as exc:
            print(f"Replacement failed ({exc}); restoring the backup ...", file=sys.stderr)
            try:
                restore_backup(backup_dir, directory)
            except OSError as restore_exc:
                raise UpdaterError(
                    f"Replacement failed and the backup could not be restored: "
                    f"{restore_exc}. Backup kept at {backup_dir}"
                ) from restore_exc
            raise UpdaterError(f"Update failed; previous version restored: {exc}") from exc
        if actual != target:
            raise UpdaterError(
                f"Installed version after update is {format_version(actual)}, "
                f"expected {format_version(target)}"
            )
        print(f"Updated {SKILL_NAME} to {format_version(target)}.")
        print(f"Backup kept at {backup_dir}")
        print("Start a new agent session to use the updated skill.")
        return 0
    finally:
        if tmp is not None:
            tmp.cleanup()


def cmd_rollback(args: argparse.Namespace) -> int:
    reexec_code = _reexec_from_temp(list(getattr(args, "_raw_argv", [])))
    if reexec_code is not None:
        return reexec_code
    directory = skill_dir()
    installed = read_installed_version(directory)
    backups = list_backups()
    if not backups:
        raise UpdaterError(f"No backups found under {backup_root()}")
    chosen: dict[str, Any] | None = None
    if args.backup:
        for candidate in backups:
            if candidate["backup_path"] == args.backup or Path(candidate["backup_path"]).name == args.backup:
                chosen = candidate
                break
        if chosen is None:
            raise UpdaterError(f"No backup named {args.backup!r}")
    else:
        chosen = backups[0]
    backup_dir = Path(str(chosen["backup_path"]))
    from_version = parse_version(str(chosen["from_version"]))
    if not _confirm(
        f"Roll back {SKILL_NAME} {format_version(installed)} -> "
        f"{format_version(from_version)} (backup {backup_dir.name})?",
        args.yes,
    ):
        print("Rollback cancelled; nothing was changed.")
        return 0
    restored = restore_backup(backup_dir, directory)
    print(f"Rolled back {SKILL_NAME} to {format_version(restored)}.")
    print(f"Backup kept at {backup_dir}")
    print("Start a new agent session to use the restored skill.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update an installed kp-skill from GitHub Releases."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    version_parser = sub.add_parser("version", help="Show the installed version")
    version_parser.add_argument("--json", action="store_true")
    version_parser.set_defaults(func=cmd_version)

    check_parser = sub.add_parser(
        "check-update", help="Check the latest release without changing files"
    )
    check_parser.add_argument("--json", action="store_true")
    check_parser.set_defaults(func=cmd_check_update)

    update_parser = sub.add_parser("update", help="Update to the latest release")
    update_parser.add_argument("--to", help="Update to a specific version, e.g. 2.3.0")
    update_parser.add_argument(
        "--zip",
        help="Update from a local release zip instead of downloading (testing)",
    )
    update_parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    update_parser.add_argument(
        "--allow-downgrade", action="store_true", help="Allow updating to an older version"
    )
    update_parser.set_defaults(func=cmd_update)

    rollback_parser = sub.add_parser("rollback", help="Restore the latest backup")
    rollback_parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    rollback_parser.add_argument("--backup", help="Backup directory name or path to restore")
    rollback_parser.set_defaults(func=cmd_rollback)

    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        print("kp-skill.py needs Python 3.10 or newer.", file=sys.stderr)
        return 1
    parser = build_parser()
    parsed_argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    args._raw_argv = parsed_argv
    try:
        return args.func(args)
    except UpdaterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled; nothing was changed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
