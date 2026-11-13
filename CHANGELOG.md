# Changelog

All notable changes to this repository. Versions refer to the `kerja-praktek-bina-insani` skill.

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

### Preserved

- All six campus reference files (`procedure.md`, `outlines.md`, `content-guide.md`, `format.md`, `forms.md`, `checklist.md`) keep their existing content, apart from three language-audit bullets named above: two in `checklist.md` and one in `format.md`.

## 1.0.0 — 2025

- Initial skill: planning, placement, chapters, methods, forms, and final check per the 2025 FID guide.
