#!/usr/bin/env python3
"""Validate the kp-skill package before it is committed or released.

The checks encode the invariants this repository depends on:

* the skill folder follows the Agent Skills layout (`skills/<name>/SKILL.md`);
* the frontmatter `name` matches the directory name;
* every `references/*.md` pointer resolves, and no reference file is orphaned;
* the version in `SKILL.md` matches the newest `CHANGELOG.md` entry;
* the README documents exactly the files that ship, and no `install.sh` flag
  that the script does not implement;
* `install.sh` and `install.ps1` expose the same targets;
* no placeholder text and no invisible characters ship inside the skill.

Standard library only. Exit code 0 when there are no errors, 1 otherwise.

Usage:
    python scripts/validate_package.py [--root PATH] [--json] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILLS_DIR = "skills"
REQUIRED_KEYS = ("name", "description")
RECOMMENDED_KEYS = ("license", "compatibility")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INVISIBLE_RE = re.compile(
    "[\u0000-\u0008\u000b\u000c\u000e-\u001f\u200b-\u200f\u202a-\u202e\u2060\ufeff]"
)
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")
REFERENCE_RE = re.compile(r"references/([A-Za-z0-9._-]+\.md)")
VERSION_RE = re.compile(r"^Version\s+([0-9]+\.[0-9]+\.[0-9]+)\b", re.MULTILINE)
CHANGELOG_VERSION_RE = re.compile(r"^##\s+\[?([0-9]+\.[0-9]+\.[0-9]+)\]?", re.MULTILINE)
SH_FLAG_RE = re.compile(r"install\.sh\s+(--[a-z][a-z-]*)")
# Install targets every installer must expose, and the PowerShell switch that
# exposes it. The names are not derivable by capitalising, OpenCode and
# CodeBuddy carry an inner capital.
AGENTS = {
    "claude": "Claude",
    "opencode": "OpenCode",
    "codex": "Codex",
    "hermes": "Hermes",
    "codebuddy": "CodeBuddy",
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.errors.append(f"{code}: {message}")

    def warn(self, code: str, message: str) -> None:
        self.warnings.append(f"{code}: {message}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str, report: Report, where: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report.error("R03", f"{where}: frontmatter does not open with '---'")
        return {}
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        report.error("R03", f"{where}: frontmatter is never closed with '---'")
        return {}

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            report.error("R03", f"{where}: unparsable frontmatter line {line!r}")
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value
    return data


def check_frontmatter(data: dict[str, str], folder: str, report: Report) -> None:
    for key in REQUIRED_KEYS:
        if not data.get(key):
            report.error("R04", f"frontmatter is missing required key {key!r}")
    for key in RECOMMENDED_KEYS:
        if not data.get(key):
            report.warn("R04", f"frontmatter is missing recommended key {key!r}")

    name = data.get("name", "")
    if name and name != folder:
        report.error("R05", f"frontmatter name {name!r} does not match folder {folder!r}")
    if name and not NAME_RE.match(name):
        report.error("R05", f"frontmatter name {name!r} is not kebab-case")
    if len(name) > 64:
        report.error("R05", f"frontmatter name is {len(name)} characters, limit is 64")

    description = data.get("description", "")
    if description and len(description) > 1024:
        report.error(
            "R06", f"description is {len(description)} characters, limit is 1024"
        )


def check_references(
    skill_dir: Path, body: str, report: Report, label: str
) -> None:
    ref_dir = skill_dir / "references"
    on_disk = {p.name for p in ref_dir.glob("*.md")} if ref_dir.is_dir() else set()
    mentioned = set(REFERENCE_RE.findall(body))

    for name in sorted(mentioned - on_disk):
        report.error("R08", f"{label}: SKILL.md points at missing references/{name}")
    for name in sorted(on_disk - mentioned):
        report.error("R08", f"{label}: references/{name} is never referenced from SKILL.md")


def check_version(skill_text: str, changelog: Path, report: Report, label: str) -> None:
    match = VERSION_RE.search(skill_text)
    if not match:
        report.error("R10", f"{label}: SKILL.md has no 'Version X.Y.Z' line")
        return
    version = match.group(1)
    if not changelog.is_file():
        report.error("R11", "CHANGELOG.md is missing")
        return
    text = read(changelog)
    versions = CHANGELOG_VERSION_RE.findall(text)
    if not versions:
        report.error("R11", "CHANGELOG.md has no '## X.Y.Z' entry")
        return
    if versions[0] != version:
        report.error(
            "R10",
            f"SKILL.md says {version} but the newest CHANGELOG entry is {versions[0]}",
        )


def check_readme(
    readme: Path, skill_dir: Path, install_sh: Path, report: Report
) -> None:
    if not readme.is_file():
        report.error("R12", "README.md is missing")
        return
    text = read(readme)

    shipped = ["SKILL.md"] + [
        f"references/{p.name}" for p in sorted((skill_dir / "references").glob("*.md"))
    ]
    for item in shipped:
        if item not in text:
            report.error("R12", f"README.md never mentions {item}")

    if install_sh.is_file():
        script = read(install_sh)
        for flag in sorted(set(SH_FLAG_RE.findall(text))):
            if flag not in script:
                report.error(
                    "R13", f"README.md documents {flag} but install.sh does not implement it"
                )


def check_installers(root: Path, report: Report) -> None:
    sh = root / "install.sh"
    ps = root / "install.ps1"
    attrs = root / ".gitattributes"

    if not sh.is_file():
        report.error("R14", "install.sh is missing")
    else:
        first = read(sh).splitlines()[0] if read(sh) else ""
        if first.strip() != "#!/bin/sh":
            report.error("R14", "install.sh must start with '#!/bin/sh'")
        if not attrs.is_file() or "*.sh text eol=lf" not in read(attrs):
            report.error("R14", ".gitattributes must pin '*.sh text eol=lf'")

    if not ps.is_file():
        report.error("R16", "install.ps1 is missing")
        return

    sh_text = read(sh)
    ps_text = read(ps)
    missing_sh = [a for a in AGENTS if f"--{a}" not in sh_text]
    missing_ps = [sw for sw in AGENTS.values() if f"[switch]${sw}" not in ps_text]
    if missing_sh:
        report.error(
            "R16", f"install.sh does not expose target(s): {', '.join(missing_sh)}"
        )
    if missing_ps:
        report.error(
            "R16", f"install.ps1 does not expose target(s): {', '.join(missing_ps)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the kp-skill package layout and documentation."
    )
    parser.add_argument(
        "--root", default=".", help="repository root (default: current directory)"
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = Report()

    skills_root = root / SKILLS_DIR
    if not skills_root.is_dir():
        print(f"ERROR R01: {SKILLS_DIR}/ directory is missing", file=sys.stderr)
        return 1

    skill_dirs = sorted(p for p in skills_root.iterdir() if (p / "SKILL.md").is_file())
    if not skill_dirs:
        report.error("R02", f"no {SKILLS_DIR}/<name>/SKILL.md found")

    for skill_dir in skill_dirs:
        label = skill_dir.name
        text = read(skill_dir / "SKILL.md")
        data = parse_frontmatter(text, report, f"{label}/SKILL.md")
        check_frontmatter(data, label, report)
        check_references(skill_dir, text, report, label)
        check_version(text, root / "CHANGELOG.md", report, label)

        for path in [skill_dir / "SKILL.md", *sorted(skill_dir.rglob("*.md"))]:
            content = read(path)
            rel = path.relative_to(root).as_posix()
            if INVISIBLE_RE.search(content):
                report.error("R07", f"{rel} contains invisible or control characters")
            for hit in PLACEHOLDER_RE.findall(content):
                report.error("R15", f"{rel} contains the placeholder {hit}")

        if not (root / "tests" / "prompts").is_dir():
            report.warn("R17", "tests/prompts/ is missing, behaviour has no regression corpus")

        check_readme(root / "README.md", skill_dir, root / "install.sh", report)

    check_installers(root, report)

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "skills": [p.name for p in skill_dirs],
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "ok": not report.errors,
                },
                indent=2,
            )
        )
    else:
        if not args.quiet:
            print(f"Repository: {root}")
            print(f"Skills: {', '.join(p.name for p in skill_dirs) or 'none'}")
            print(f"Errors: {len(report.errors)}  Warnings: {len(report.warnings)}")
            print()
        for warning in report.warnings:
            print(f"WARN  {warning}")
        for error in report.errors:
            print(f"ERROR {error}")
        if report.errors:
            print()
            print(f"FAIL: {len(report.errors)} error(s).")
        elif not args.quiet:
            print("OK: package is valid.")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
