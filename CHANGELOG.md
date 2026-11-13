# Changelog

All notable changes to this repository. Versions refer to the `kerja-praktek-bina-insani` skill.

## 2.2.0 — 2026-11-13

Turns the repository from "a folder you copy" into a package that checks itself. No campus rule changed: every edit below is infrastructure, documentation, or a defect fix.

### Added

- `scripts/validate_package.py` — structural validator, seventeen checks (R01–R17). Verifies the `skills/<name>/SKILL.md` layout, that the frontmatter `name` matches the directory and is kebab-case, that every `references/*.md` pointer in `SKILL.md` resolves and that no reference file is orphaned, that `Version X.Y.Z` in `SKILL.md` matches the newest `CHANGELOG.md` entry, that the README mentions every shipped file, that the README documents no `install.sh` flag the script does not implement, that both installers expose the same five targets, and that no placeholder or invisible character ships inside the skill. Standard library only.
- `scripts/check_docx.py` - deterministic `.docx` format checker for the rules in `references/format.md`: A4 paper, 4/3/4/3 cm margins, Times New Roman 12, double spacing, 14 pt bold uppercase chapter titles, and caption placement. Also reports unresolved comments, tracked changes, and leftover editorial notes such as `[Isi tabel ini ...]`. The cover page and front-matter headings are exempt because the guide gives them their own sizes. Reads the OOXML directly with `zipfile` and `xml.etree`, so it needs no `python-docx` and no network. Flags `--json` and `--fail-on high|medium|low|none`.
- `install.ps1` — Windows installer with the same five targets as `install.sh`, plus `-All`, `-Uninstall`, `-DryRun`, and `-Help`. Rejects two targets in one invocation.
- `.github/workflows/validate.yml` — runs the validator and both installers on Linux, macOS, and Windows across Python 3.10, 3.12, and 3.13, including a real install, a reinstall, and an uninstall against a throwaway home directory.
- `.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md` — a bug report that demands the prompt and the answer, and a PR checklist that asks for the validator output.
- `tests/prompts/` — ten behaviour cases (topic eligibility, SI outline, PIECES, format, ghostwriting boundary, missing data, humanizer, document inspection, forms, Bab V) with `loads`/`expects`/`rejects` fields. Run by hand, not by CI, because the pass condition is a judgement about an answer.
- `examples/sample-audit.md` — a fictional Bab I–III audit showing the output shape: severity, location, owning requirement, observed condition, impact, remediation, status, and an explicit "what was not checked" section.
- `docs/rule-sources.md` — provenance boundary and authority tiers: campus requirement, repository method, third-party tool.
- `CONTRIBUTING.md` and `AGENTS.md` — one owner per rule, no invented campus policy, validator and installer instructions, and the do-nots.
- `README.id.md` — Indonesian README for students.

### Fixed

- **`gh skill install` example installed the wrong thing.** The 2.1.0 README showed `gh skill install Nbill27/kp-skill --all`, which reads as "every agent" but resolves to the tool's defaults: project scope and the `github-copilot` agent. The README now names the skill explicitly and passes `--agent` and `--scope`, and states what the defaults are.
- **The repository could not be pinned.** With no tags, `--pin` had nothing to resolve. `v2.2.0` is the first tag.
- **`cp -r` could leave stale files.** Reinstalling merged into the existing folder, so a file removed in a newer version survived. Both installers now remove the destination before copying.
- **The README documented an install path Windows users cannot take.** It only showed POSIX shell. There is now a PowerShell section and a Windows column in the scope table.

### Changed

- `install.sh` rewritten: `--all`, `--uninstall`, and `--dry-run` added; `-h` and `--help` both work; an unknown flag exits 1 with the usage text instead of being ignored.
- `README.md` install docs rebuilt around the installer scripts and the five agents, with a per-agent verification line and manual-copy fallback. It also documents both scripts under "Check your report".
- `SKILL.md` version is 2.2.0, `compatibility` names Claude Code, OpenCode, Codex, Hermes, and CodeBuddy, and section 16 points at `scripts/check_docx.py` as the deterministic format check.
- `.gitignore` ignores `__pycache__/` and `*.pyc`.

### Preserved

- All nine reference files are unchanged. The campus rules, the placeholder contract, the ghostwriting boundary, and the inspect-first policy are the same as 2.1.0.

## 2.1.0 — 2026-11-13

Adds the academic humanizer and the optional `watermarks-remover` integration, and repairs six defects found when reviewing the 2.0 draft before it reached this repository.

### Added

- `references/humanizer.md` — academic Indonesian humanizer: ten diagnostic categories, editing procedure, guardrails, output template. Declared the single authority for language-pattern auditing.
- `references/document-inspection.md` — five-layer inspection policy (Unicode, file metadata, provenance credentials, statistical text watermark, visible graphic watermark), inspect-first workflow, preservation rules.
- `references/watermarks-remover.md` — optional integration with [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover). Documents both the local CLI path (`skills/clean-user-facing-text`, no server) and the HTTP service path, with endpoints, environment variables, request sequence, and limits.
- `SKILL.md` section 3 "Core facts", section 16 "Tools", and a version line.
- `CHANGELOG.md`.

### Fixed

- **Broken integration path after install.** The 2.0 draft pointed at `integrations/watermarks-remover/README.md` at the repository root, but `install.sh` and the documented `cp -r skills/*` only copy the skill folder, so the pointer dangled in every installed copy. The integration documentation now lives at `references/watermarks-remover.md` inside the skill.
- **Trigger keywords dropped from the frontmatter.** Restored `bimbingan KP`, `surat keterangan KP`, `nilai KP`, the full study-program names, and `BAA`, which the 2.0 description had lost, so the skill still loads on those requests.
- **Campus facts missing from `SKILL.md`.** 4 SKS, 1–6 month duration, legal-entity host, minimum 5 supervision meetings, PDF submission to BAA, and the grade-E consequence of forging a letter or grade were only implied by references. They are now stated in section 3.
- **Duplicated authority.** `references/checklist.md` and `references/format.md` each said "the five machine patterns" while `humanizer.md` lists ten categories. Both now audit against `humanizer.md` by reference instead of carrying a competing count.
- **Unaudited markers.** `[BUKTI: ...]` and `[KONFIRMASI PEMBIMBING: ...]` were introduced but never checked. The Layer 1 marker audit in `checklist.md` now covers all four markers.
- **Outdated integration description.** The 2.0 draft described the upstream project as service-only. Upstream now also ships a self-contained local skill, `skills/clean-user-facing-text`, with `scripts/inspect_text.py --audit` and `scripts/clean_text.py`. The integration reference documents that path first and the server second.

### Changed

- `allowed-tools` gains `WebFetch` for reading public upstream documentation; `SKILL.md` states that fetched web content is not campus policy.
- `README.md` lists every file inside the skill and states that the folder is a complete install.
- `README.md` install instructions now cover Claude Code (`~/.claude/skills`), OpenCode (`~/.config/opencode/skills`), Codex (`~/.agents/skills`), Hermes, and CodeBuddy, with user and project scope for each. `install.sh` gained `--claude`, `--opencode`, `--codex`, and `--help`, so no documented flag is missing from the script.

### Preserved

- All six campus reference files (`procedure.md`, `outlines.md`, `content-guide.md`, `format.md`, `forms.md`, `checklist.md`) keep their existing content, apart from three language-audit bullets named above: two in `checklist.md` and one in `format.md`.

## 1.0.0 — 2025

- Initial skill: planning, placement, chapters, methods, forms, and final check per the 2025 FID guide.
