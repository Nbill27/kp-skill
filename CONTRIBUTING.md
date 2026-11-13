# Contributing

This repository is a skill, not an application. Most changes are edits to
Markdown that an agent will read at runtime, so the bar is different from code:
a wrong sentence changes behaviour on every future request.

## Before you change anything

1. Read `SKILL.md`. It is the entry point and it defines the routing.
2. Read `docs/rule-sources.md` so you know whether you are changing a campus
   requirement or a repository method.
3. If the change touches a rule, find the reference file that owns it. Rules
   have one owner. Do not restate a rule in a second file.

## Ground rules

- **One owner per rule.** `references/humanizer.md` owns the language
  diagnostics; `references/checklist.md` audits against them by name. Do not
  fork a list.
- **No invented campus policy.** If the guide does not say it, do not present it
  as a requirement. Mark repository advice as advice.
- **No fabricated examples.** Sample data in docs must be obviously fictional
  and must not look like a real student, company, or grade.
- **Placeholders are part of the design.** `[ISI: ...]`, `[CEK: ...]`,
  `[BUKTI: ...]`, and `[KONFIRMASI PEMBIMBING: ...]` are the correct output when
  a fact is missing. Do not replace them with plausible text.
- **English for repository docs, Indonesian for student-facing prose.** The
  skill answers in the user's language; the repository explains itself in
  English.

## Editing the skill

- Keep `SKILL.md` a router plus invariants. Detail belongs in `references/`.
- Every `references/*.md` file must be referenced from `SKILL.md`, and every
  pointer must resolve. The validator enforces both directions.
- Bump `Version X.Y.Z` in `SKILL.md` and add a matching `CHANGELOG.md` entry.
  The validator compares the two.
- If you change behaviour, add or update a case in `tests/prompts/`.

## Validating

Standard library only, no install step:

```bash
python scripts/validate_package.py
python scripts/validate_package.py --json
python scripts/validate_package.py --quiet
```

Exit code 0 means no errors. Warnings do not fail the build but should be
explained in the pull request.

Format checking of a real document, when you have one:

```bash
python scripts/check_docx.py laporan.docx
python scripts/check_docx.py laporan.docx --json --fail-on high
```

## Installers

`install.sh` and `install.ps1` must expose the same five targets plus `--all`,
`--uninstall`, and `--dry-run`. The validator checks that both scripts declare
every target. If you add a target, change both scripts, the README install
table, and the validator's `AGENTS` map in the same commit.

The install is a plain recursive copy. Do not add a flag the scripts do not
implement, and do not document one the README does not mention.

## Pull requests

- One concern per pull request.
- State what behaviour changes, and which reference file owns the rule.
- Paste the validator output.
- If you cannot verify a claim against the guide, say so in the description
  rather than asserting it in the docs.

## Reporting a problem

Open an issue with the prompt you sent, the answer you got, and the answer you
expected. A behaviour bug without a reproducible prompt is hard to fix.
