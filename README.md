# kp-skill

Agent skill for writing Kerja Praktek reports at Universitas Bina Insani, built from the official campus guide. Plain Agent Skills format: the skill is a folder with a `SKILL.md` at its root, so any agent that reads that format can use it.

## Skills

| Skill | What it does |
| --- | --- |
| `kerja-praktek-bina-insani` | Plans, runs, and writes a Kerja Praktek magang internship and laporan KP under the FID guide, per study program (SI, TI, RPL, MI), with its procedures, outlines, analysis methods (PIECES, SWOT, Information Characteristics), forms, and final checks. |

The rules in this skill come from the official guide: *Buku Panduan Kerja Praktek FID Universitas Bina Insani, 2025*. The guide itself is a campus document and is not bundled in this repo.

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

Ask the agent to write or check a laporan KP. The skill loads when the request matches: kerja praktek, magang, laporan KP, Bina Insani, or a chapter name such as Bab I through Bab V.

## Notes

- The skill never invents data, respondents, sources, numbers, or results. Missing material is marked `[ISI: ...]` and unverified material is marked `[CEK: ...]`.
- The skills refuse ghostwriting and requests to disguise AI output as the student own writing.

## License

MIT. See [LICENSE](LICENSE).
