# Sample audit

A worked example of the output shape defined in `SKILL.md` section 17. The
report audited here is fictional. Use it as a reference for tone, structure,
and severity, not as a template to copy verbatim.

## Input

> Berikut draf laporan KP saya (Bab I–III). Tolong audit kesiapan submit.

Context supplied with the draft: Sistem Informasi, host is a CV running a
retail store, internship 2 months, daily log present but unsigned, company
assessment form not yet collected, no supervision card.

## Output

**Scope:** Bab I–III, plus the administrative status listed above.
**Not inspected:** Bab IV–V (not supplied), the final PDF, and the original
guide. Findings that depend on those are marked **BELUM ADA BUKTI**.

### Summary

| Layer | Pass | Fail | Needs Evidence |
| --- | --- | --- | --- |
| Substance | 4 | 1 | 2 |
| Language | 3 | 0 | 1 |
| Format | 2 | 1 | 0 |
| Integrity | 1 | 2 | 1 |

### Findings

#### KP-SUB-01 — Rumusan masalah has no matching conclusion path

- **Severity:** Critical
- **Location:** Bab I, Rumusan Masalah, items 1–3; Bab III, Metode
- **Requirement:** `references/checklist.md` Layer 1 — traceability from
  rumusan masalah to tujuan to bab to bukti to simpulan to saran.
- **Observed:** Item 3 asks how the store should evaluate customer satisfaction,
  but no objective, section, method, or evidence addresses it. Items 1 and 2
  map cleanly.
- **Impact:** The examiner can reject the report on coherence alone. Bab V
  cannot answer a question the method never studied.
- **Remediation:** Either drop item 3, or add an objective, a data-collection
  step in Bab III, and a section in Bab IV that answers it. Do not add a
  conclusion for a question that was never investigated.
- **Status:** Fail

#### KP-SUB-02 — PIECES dimension filled without evidence

- **Severity:** High
- **Location:** Bab III, Analisis PIECES, dimensi *Economics*
- **Requirement:** `SKILL.md` section 10 — every dimension needs an observed
  condition, its evidence, and its impact.
- **Observed:** The draft states that the current process wastes "sekitar 30%"
  of operational cost. No cost record, invoice, or interview supports the
  figure.
- **Impact:** A fabricated number is the fastest way to lose credibility in a
  sidang, and it is a direct integrity problem.
- **Remediation:** Replace with `[BUKTI: catatan biaya operasional atau
  wawancara dengan bagian keuangan]` until the student supplies the source, or
  drop the percentage and describe the observed condition qualitatively.
- **Status:** Needs Evidence

#### KP-LANG-01 — Mechanical opener and repeated transition

- **Severity:** Medium
- **Location:** Bab I, Latar Belakang, paragraphs 1 and 3
- **Requirement:** `references/humanizer.md` — empty openers and repeated
  transitions.
- **Observed:** "Dalam era digital yang semakin berkembang pesat" opens the
  chapter, and "Oleh karena itu" opens three consecutive paragraphs.
- **Impact:** The prose reads as generic filler and hides the actual claim.
- **Remediation:** Open with the observed condition at the host, and vary or
  remove the repeated transition. Keep every number and citation intact.
- **Status:** Fail

#### KP-FMT-01 — Table title placed below the table

- **Severity:** Medium
- **Location:** Bab III, Tabel III.2
- **Requirement:** `references/format.md` — table titles above the table,
  centered; figure titles below the figure.
- **Observed:** The caption sits under the table.
- **Impact:** Format compliance is checked mechanically, and this is a visible
  mismatch.
- **Remediation:** Move the caption above the table and center it. Keep the
  chapter-based numbering.
- **Status:** Fail

#### KP-INT-01 — Company assessment not collected

- **Severity:** Critical
- **Location:** Attachments
- **Requirement:** `SKILL.md` section 3 and `references/forms.md` — the company
  assessment and the Surat Keterangan KP must be collected before the
  internship ends.
- **Observed:** The student reports the internship already closed and the
  assessment form was never requested.
- **Impact:** Submission to BAA is incomplete without it. Recovering the form
  after the placement ends depends on the company's goodwill.
- **Remediation:** Contact the company supervisor immediately, explain the
  requirement, and request the signed original on letterhead with the company
  stamp. Do not proceed as if the attachment is optional.
- **Status:** Fail

#### KP-INT-02 — Daily log lacks mentor initials

- **Severity:** High
- **Location:** Lampiran, Log Harian
- **Requirement:** `references/checklist.md` Layer 4 — the daily log needs
  dates, times, activities, mentor initials, and photos.
- **Observed:** Dates and activities are present; mentor initials are missing on
  every row.
- **Impact:** The log does not prove supervision, which is the point of the
  document.
- **Remediation:** Ask the field mentor to initial each row. If the mentor is no
  longer reachable, state that plainly and let the campus supervisor decide.
- **Status:** Fail

### What was not checked

- Bab IV and Bab V were not supplied, so the conclusion-to-finding map is
  unverified.
- The final PDF was not inspected, so page numbering and the attachment order
  are unverified.
- The original 2025 guide was not available, so every rule above is cited to
  this repository's references, not to a page in the guide.
