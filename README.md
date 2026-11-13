# kp-skill

Agent skill for writing Kerja Praktek reports at Universitas Bina Insani, built from the official campus guide. Plain Agent Skills format: the skill is a folder with a `SKILL.md` at its root, so any agent that reads that format can use it.

## Skills

| Skill | What it does |
| --- | --- |
| `kerja-praktek-bina-insani` | Plans, runs, and writes a Kerja Praktek magang internship and laporan KP under the FID guide, per study program (SI, TI, RPL, MI), with its procedures, outlines, analysis methods (PIECES, SWOT, Information Characteristics), forms, final checks, academic humanizer, and document inspection policy. |

The rules in this skill come from the official guide: *Buku Panduan Kerja Praktek FID Universitas Bina Insani, 2025*. The guide itself is a campus document and is not bundled in this repo.

## Inside the skill

| File | Purpose |
| --- | --- |
| `SKILL.md` | Authority, core facts, workflow, evidence hierarchy, revision scope, integrity rules |
| `references/procedure.md` | Placement, administration, ethics, duration, supervision |
| `references/outlines.md` | Report outline per study program |
| `references/content-guide.md` | What each section must contain, analysis methods |
| `references/format.md` | Typing, cover, numbering, citations, language, references |
| `references/forms.md` | Letters, assessment form, daily log, consultation card |
| `references/checklist.md` | Four-layer final check |
| `references/humanizer.md` | Academic Indonesian humanizer: diagnostic categories, editing procedure, guardrails |
| `references/document-inspection.md` | Hidden Unicode, metadata, and provenance inspection policy |
| `references/watermarks-remover.md` | Optional [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) integration |

Everything the skill needs lives inside the skill folder, so a plain copy of the folder is a complete install. The `watermarks-remover` integration is optional and requires installing that tool separately; see `references/watermarks-remover.md`.

## Install

### Hermes

```bash
git clone https://github.com/Nbill27/kp-skill.git
cp -r kp-skill/skills/* ~/.hermes/skills/
hermes skills list
```

Or run the installer from the repo root:

```bash
./install.sh
```

### CodeBuddy

```bash
git clone https://github.com/Nbill27/kp-skill.git
cp -r kp-skill/skills/* ~/.codebuddy/skills/
```

Project scope instead of user scope: copy into `.codebuddy/skills/` inside the project.

### Other agents

Copy a skill folder into the agent skills directory, keeping the folder name. The `name` in the frontmatter matches the directory name, as the spec requires. `gh skill install` also works:

```bash
gh skill install Nbill27/kp-skill --all
```

## Use

Ask the agent to write or check a laporan KP. The skill loads when the request matches: kerja praktek, KP, magang, laporan KP, bimbingan KP, surat keterangan KP, nilai KP, Bina Insani, FID, BAA, a study program name, or a chapter name such as Bab I through Bab V.

## Notes

- The skill never invents data, respondents, sources, numbers, or results. Missing material is marked `[ISI: ...]`, unverified material `[CEK: ...]`, unattached evidence `[BUKTI: ...]`, and undecided items `[KONFIRMASI PEMBIMBING: ...]`.
- The skill refuses ghostwriting and requests to disguise AI output as the student's own writing. The humanizer targets writing quality; it does not target detector scores.
- Document inspection defaults to inspect-and-report. Cleaning hidden characters or private metadata requires an authorized purpose and writes a separate output file.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
