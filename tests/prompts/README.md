# Prompt regression corpus

Each file in this directory is one behaviour case for the
`kerja-praktek-bina-insani` skill. The corpus exists so that a change to
`SKILL.md` or a reference file can be checked against the behaviour that was
already agreed, instead of being judged by feel.

These cases are not an automated test suite. They are a fixed set of inputs
with explicit pass/fail expectations, meant to be run by hand (or by an agent)
against the current skill text before a release.

## File format

```markdown
---
id: 01-topic-eligibility
loads: references/procedure.md, references/outlines.md
expects:
  - behaviour that must appear
rejects:
  - behaviour that must not appear
---

## Prompt

The exact text a user would send.

## Why this case exists

One or two sentences tying the case to a rule in the skill.
```

- `id` matches the file name without `.md`.
- `loads` lists the reference files the answer must be grounded in.
- `expects` and `rejects` are observable statements, not style preferences.
- A case fails if any `rejects` item appears, or if a `expects` item is absent.

## Running a case

1. Start a fresh session with the skill installed and no prior context.
2. Send the text under `## Prompt` verbatim.
3. Read the answer against `expects` and `rejects`.
4. Record the outcome and the skill version.

## Coverage

| Case | Area |
| --- | --- |
| `01-topic-eligibility` | Placement legality and study-program fit |
| `02-outline-si` | Program-specific outline selection |
| `03-pieces-analysis` | PIECES grounded in evidence |
| `04-format-check` | Typography and layout rules |
| `05-ghostwriting-refusal` | Integrity boundary |
| `06-missing-data` | Placeholders instead of invention |
| `07-humanizer` | Human editing without fabricating voice |
| `08-document-inspection` | Inspect-first, clean-on-request |
| `09-forms` | Mandatory attachments and their order |
| `10-bab-v` | Conclusion tied to findings, not promises |

Add a case when a defect is found, not when a feature is added. A case that
cannot fail is not a test.
