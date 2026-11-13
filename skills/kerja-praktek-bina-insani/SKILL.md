---
name: kerja-praktek-bina-insani
description: "Plan, run, and write a Kerja Praktek magang internship and laporan KP under the FID Universitas Bina Insani guide. Use when the user mentions kerja praktek, magang, laporan KP, Bina Insani, FID, Sistem Informasi, Teknik Informatika, Rekayasa Perangkat Lunak, Manajemen Informatika, bimbingan KP, surat keterangan KP, or nilai KP."
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Kerja Praktek Bina Insani

- Use this skill whenever the user plans, runs, writes, revises, or checks a Kerja Praktek internship or report for Fakultas Informatika dan Desain at Universitas Bina Insani.
- Treat the KP guide as the only authority. Read the relevant part of the guide before acting and follow it when it disagrees with anything else.
- The rules below come from the official guide, Buku Panduan Kerja Praktek FID Universitas Bina Insani, 2025. The guide itself is a campus document and is not bundled in this repo. The guide covers Sistem Informasi, Teknik Informatika, Rekayasa Perangkat Lunak, and Manajemen Informatika.
- Work in this order. Plan the placement first, run the internship with its logs and supervisions, build the core map, then the outline for the study program, draft one chapter at a time, apply the writing rules while drafting, assemble the letters and forms, then run the final check.
- Read the reference file that matches the task. Read references/procedure.md for placement, ethics, and supervision. Read references/outlines.md for the report outline of the study program. Read references/content-guide.md for what each section must contain. Read references/format.md for typing, cover, numbering, citations, language, and references. Read references/forms.md for the letters, the assessment form, the daily log, and the consultation card. Read references/checklist.md before declaring the report done.

## Core facts

- Treat Kerja Praktek as a 4 SKS individual course.
- Run the internship for at least 1 month and at most 6 months.
- Place the student at a legal entity such as a PT or CV, in a division that matches the study program.
- Limit the scope to analyzing the problem at the internship site and producing a recommendation or a proposed system improvement.
- Match the proposed system to the study program focus. Sistem Informasi focuses on business solution analysis and IT audit. Teknik Informatika focuses on computer networks, IoT, security, or AI. Rekayasa Perangkat Lunak focuses on mobile application and game programming analysis. Manajemen Informatika focuses on web and desktop system analysis.
- Hold at least 5 supervision meetings with the campus supervisor, online or offline.
- Collect the company assessment and the Surat Keterangan KP before the internship ends. Both documents are mandatory attachments.
- Send the assessment form, the letter, and the full report as a PDF with all attachments to BAA.
- Warn the student that forging the letter or the grade turns the grade into E and bars the student from skripsi guidance.

## Editing scopes

- When the user asks to check or revise existing text, use the narrowest scope that fits the request and say which scope is used.
- Koreksi: fix typos, punctuation, and spelling only. Change no wording, no claim, and no structure.
- Sunting: fix grammar, clarity, and flow. Keep every fact, number, claim, and citation exactly as it is.
- Tulis ulang: restructure a section or rewrite its sentences. Keep every fact and every claim. Flag any claim that cannot be kept.
- Tulis: draft new text from the student material. Mark every missing fact as [ISI: ...] and every unverified fact as [CEK: ...].
- Ask which scope the user wants when the request is unclear. Default to the narrowest scope, Koreksi, when the user only asks to check the text.

## Long document workflow

- Work one chapter at a time. Finish and check a chapter before drafting the next one.
- Before Bab I, build a term list with the exact spelling of every key term and a point of view list with the voice used in the text. Use the same terms and the same voice in every chapter.
- Verify the numbers, citations, and quotes of a chapter while drafting that chapter. Do not leave all verification to the end.
- Report the result per chapter when the chapter is done, including the [ISI: ...] and [CEK: ...] items that chapter still needs.

## Honesty rules

- Never invent data, respondents, sources, numbers, or results.
- Mark anything missing as [ISI: ...] and anything unverified as [CEK: ...].
- Trace every number in the text to a real source such as a daily log entry, a company document, or an interview note.
- Refuse ghostwriting requests and requests to disguise AI output as the student own writing. Offer to draft from the student own material and to revise the student own words instead.

## Tools

- Use the agent document tools to build and revise the actual files.
