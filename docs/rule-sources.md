# Rule sources

Where each reference file comes from, and how much authority it carries.

## Provenance boundary

The repository references operationalize *Buku Panduan Kerja Praktek FID
Universitas Bina Insani, 2025*. They are a working restatement of the guide's
rules in a form an agent can apply. They are **not** a verbatim copy of the
guide, and they do not claim to be complete.

Consequences:

- When the guide is available, the guide wins. Report the difference instead of
  silently following the reference.
- When a rule needs an exact page, clause, or example and the guide is absent,
  say so and ask for verification. Never invent a page number.
- When a reference is silent on a case, the honest answer is "not covered here",
  not a plausible generalization from another university's rules.

## Reference map

| File | Covers | Primary authority |
| --- | --- | --- |
| `references/procedure.md` | Placement, host legality, administration, ethics, duration, supervision, submission | Campus requirement |
| `references/outlines.md` | Chapter structure per study program, including the TI Bab IV variant | Campus requirement |
| `references/content-guide.md` | Required content per section; PIECES, SWOT, Information Characteristics | Campus requirement plus method convention |
| `references/format.md` | Paper, margins, fonts, spacing, cover, numbering, figures, tables, citations, language, references | Campus requirement |
| `references/forms.md` | Proposal, request letter, assessment form, daily log, consultation card, Surat Keterangan KP, CV, abstract | Campus requirement |
| `references/checklist.md` | Four-layer final check: substance, language, format, integrity | Campus requirement |
| `references/humanizer.md` | Indonesian academic prose diagnostics, editing procedure, guardrails | Repository method |
| `references/document-inspection.md` | Hidden Unicode, file metadata, provenance credentials, statistical and visible watermarking | Repository policy |
| `references/watermarks-remover.md` | Optional integration with the external `watermarks-remover` tool | Third-party tool documentation |

## Authority tiers

1. **Campus requirement** — the guide states it. Deviating is a compliance
   failure. Cite the reference file, and the guide when available.
2. **Repository method** — the repository chooses a technique for doing the
   work well. Useful and expected, but not a campus rule. Say so when it
   matters.
3. **Third-party tool** — behaviour of an external project. Verify against its
   own documentation and never present it as campus policy.

## Maintenance rule

A change to a rule that comes from the guide must be traceable to the guide
text the contributor read. A change to a repository method needs a reason and a
regression case in `tests/prompts/`. See `CONTRIBUTING.md`.

## Known gaps

- The guide's exact pagination is not recorded, so page-level citation is not
  possible from the references alone.
- Form layouts are described in prose, not reproduced as templates. Students
  still need the official files from BAA or FID.
- Study-program focus is summarized. A program-specific edge case may need the
  guide itself.
