---
id: 04-format-check
loads: references/format.md
expects:
  - states A4 paper and the 4/3/4/3 cm margin rule
  - states Times New Roman 12 pt and double spacing for body text
  - states chapter titles at 14 pt, bold, uppercase
  - offers a deterministic check instead of eyeballing
rejects:
  - applying another university's margin or font rule
  - claiming the document was checked when no file was inspected
---

## Prompt

Format laporan KP yang benar itu bagaimana? Lalu cek apakah file saya sudah
sesuai.

## Why this case exists

Section 16 says to prefer deterministic local checks and never report a result
that was not obtained. The rule set comes from `references/format.md`, not from
general academic convention, and a claim about a file requires reading the file.
