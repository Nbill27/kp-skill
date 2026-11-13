# Academic Humanizer — Authentic Writing Quality

## Objective

Improve clarity, precision, cohesion, and readability of student-authored academic Indonesian. The aim is better communication and faithful representation of the student's actual understanding, not evasion of AI-detection systems.

## Input contract

Before editing, determine the requested scope: Koreksi, Sunting, Tulis ulang, or Tulis (see `SKILL.md` section 12). Preserve exact facts, numerical values, citations, quotations, technical terms, uncertainty, and research scope. Ask for source/context only when changing the passage safely depends on it.

## Diagnostic categories

This list is the single authority for language-pattern auditing. `references/checklist.md` (Layer 2) audits against it by reference; do not create a second, differently numbered list elsewhere.

Inspect for:
1. **Empty openings:** broad claims such as "Di era digital ini" or "Seiring perkembangan teknologi" that do not establish a case-specific reason.
2. **Vague actors:** unclear subjects such as "dilakukan proses" without identifying the responsible actor or system where relevant.
3. **Generic claims:** claims such as "meningkatkan efektivitas dan efisiensi" without identifying which activity, measure, or evidence supports them.
4. **Repetitive transitions:** repeated use of "Selain itu", "Oleh karena itu", "Dengan demikian", or "Hal ini" at every paragraph opening.
5. **Redundancy:** repeated explanations, duplicated summaries, and sentences that restate the heading without adding information.
6. **Inflated language:** "sangat optimal", "revolusioner", "signifikan" or "komprehensif" without evidence or a defined comparison.
7. **Literal translation:** unnatural connectors and English-style clause structures translated word-for-word.
8. **Sentence monotony:** many sentences with the same length and structure; improve rhythm only where it helps comprehension, not to manipulate detector scores.
9. **Term inconsistency:** multiple names for the same application, role, process, metric, or method.
10. **Unsupported personalization:** invented "pengalaman penulis", observations, opinions, or workplace details.

## Editing procedure

1. Read at least the surrounding paragraph and heading; do not humanize isolated sentences when context is available.
2. Identify the main claim and its evidence. If evidence is absent, retain an explicit `[BUKTI: ...]` or `[CEK: ...]` marker.
3. Remove filler and generic openings only when they add no meaning.
4. Replace vague wording with precise wording only when the underlying facts identify the actor, process, object, or impact.
5. Vary sentence structure naturally; do not insert deliberate mistakes or colloquialisms into a formal report.
6. Keep appropriate passive voice in methods and procedural descriptions.
7. Preserve citation syntax and source attribution exactly unless the user asks for citation-format correction and the authoritative reference is available.
8. Follow the campus guide's language and formatting requirements in `format.md`.
9. Return the edited passage and a concise change log grouped by clarity, cohesion, terminology, and evidence flags.
10. State that no AI-detector outcome is guaranteed and no detector bypass was attempted.

## Guardrails

- Never target a detector score or write instructions such as "make it undetectable".
- Never fabricate personal voice, anecdotes, interviews, field observations, or student effort.
- Never change factual meaning, causal strength, certainty, sample size, date, value, or conclusion.
- Never delete citations to make text appear original.
- Do not turn a limited prototype into a production system, a suggestion into an implemented result, or correlation into causation.
- When a sentence is vague because the student has not supplied the relevant information, ask for the fact or leave a marker; do not invent a detail.

## Relationship to text-hygiene tooling

Mechanical cleanup of invisible Unicode and private metadata is a separate task with a separate policy; see `document-inspection.md` and `watermarks-remover.md`. Humanizing prose and cleaning file artifacts are different operations with different risks. Running one does not satisfy the other, and neither one establishes authorship.

## Output template

### Hasil suntingan
[Revised text]

### Catatan perubahan
- [Specific wording issue] → [What changed and why]

### Hal yang masih perlu dikonfirmasi
- [Only facts/claims that need the student's evidence]

### Scope
[ Koreksi / Sunting / Tulis ulang / Tulis ]
