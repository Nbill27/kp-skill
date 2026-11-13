# AGENTS.md

Instructions for an agent working **in this repository**. This file is not part
of the installed skill; it does not ship to users.

## What this repo is

A single Agent Skills package at `skills/kerja-praktek-bina-insani/`. The skill
folder is self-contained: `SKILL.md` plus `references/*.md`. Everything else is
repository infrastructure.

## Layout

| Path | Role |
| --- | --- |
| `skills/kerja-praktek-bina-insani/SKILL.md` | Entry point: authority, invariants, routing to references |
| `skills/kerja-praktek-bina-insani/references/` | One file per topic; each has exactly one owner |
| `scripts/validate_package.py` | Structural validator, standard library only |
| `scripts/check_docx.py` | Deterministic .docx format checker, standard library only |
| `tests/prompts/` | Behaviour regression corpus, run by hand |
| `examples/sample-audit.md` | Reference output shape |
| `docs/rule-sources.md` | Provenance and authority tiers |
| `install.sh` / `install.ps1` | POSIX and PowerShell installers, same targets |

## Rules when editing

1. Read `SKILL.md` before editing a reference. The routing table decides which
   file owns a rule.
2. Do not duplicate a rule across files. If two files disagree, one of them is
   wrong; fix the owner and remove the copy.
3. Do not add campus policy the references do not already support. If a rule is
   a repository recommendation, label it as one.
4. Keep the placeholder contract intact: `[ISI: ...]`, `[CEK: ...]`,
   `[BUKTI: ...]`, `[KONFIRMASI PEMBIMBING: ...]`.
5. Never write a fabricated example that could be mistaken for real student or
   company data.

## Verification before you claim done

```bash
python scripts/validate_package.py
```

Must exit 0. If you touched an installer, also check:

```bash
sh -n install.sh
```

and on Windows:

```powershell
.\install.ps1 -DryRun
```

If you changed behaviour, run the relevant case in `tests/prompts/` against the
new text and record the outcome.

## What not to do

- Do not add a dependency to the validator or the checker. They must run on a
  bare Python install, because students run them.
- Do not document an installer flag that the script does not implement.
- Do not bump the version without a `CHANGELOG.md` entry; the validator fails.
- Do not commit `__pycache__` or `.pyc` files.
