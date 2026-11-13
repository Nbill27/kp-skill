#!/usr/bin/env python3
"""Check a Kerja Praktik .docx against the Bina Insani formatting rules.

Only the rules that can be read reliably from the file are checked. The
thresholds come from ``references/format.md``:

* A4 page (21 x 29.7 cm);
* margins top 4 cm, bottom 3 cm, left 4 cm, right 3 cm;
* body in Times New Roman 12 at double spacing;
* chapter titles centred, uppercase, 14 pt bold;
* figure captions below the figure, table captions above the table.

The cover page has its own sizes in ``references/format.md`` (title 14 pt,
KERJA PRAKTIK 18 pt, author and NPM 14 pt, 1.5 spacing), so the body rules
skip it. Front-matter headings such as PERSETUJUAN LAPORAN KERJA PRAKTIK are
centred, bold, uppercase and short, and the guide sets no size for them, so
they are skipped too. Entries in DAFTAR ISI, DAFTAR GAMBAR and DAFTAR TABEL
carry a tab or dot leader to the page number and are not judged as body text.

The script also looks for leftover tracked changes and comments, which is the
usual reason a submitted file still shows edits to a reviewer, and for
editorial notes such as ``[Isi tabel ini ...]`` that were never replaced.

Standard library only: a student should not have to install anything.

Usage:
    python scripts/check_docx.py laporan.docx
    python scripts/check_docx.py laporan.docx --json
    python scripts/check_docx.py laporan.docx --fail-on medium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_NS = f"{{{W}}}"

TWIPS_PER_CM = 1440 / 2.54
A4_WIDTH_TWIPS = 11906
A4_HEIGHT_TWIPS = 16838
SIZE_TOLERANCE_TWIPS = 40

MARGINS_CM = {"top": 4.0, "bottom": 3.0, "left": 4.0, "right": 3.0}
BODY_FONT = "Times New Roman"
BODY_SIZE_HALF_POINTS = 24  # 12 pt
CHAPTER_SIZE_HALF_POINTS = 28  # 14 pt
DOUBLE_LINE = "480"  # 240 twips = single, so 480 is double

CAPTION_RE = re.compile(r"^(Gambar|Tabel)\s+([IVX]+)\.(\d+)\b")
CHAPTER_RE = re.compile(r"^BAB\s+[IVX]+\b")
TOC_LEADER_RE = re.compile(r"\.{2,}$")

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "none": 0}


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    where: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "where": self.where,
        }


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, rule: str, severity: str, message: str, where: str = "") -> None:
        self.findings.append(Finding(rule, severity, message, where))

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    @property
    def worst(self) -> str:
        rank = max((SEVERITY_ORDER[f.severity] for f in self.findings), default=0)
        for name, value in SEVERITY_ORDER.items():
            if value == rank:
                return name
        return "none"


def text_of(element: ET.Element) -> str:
    """Return the visible text of a paragraph."""
    parts: list[str] = []
    for node in element.iter():
        if node.tag == f"{W_NS}t" and node.text:
            parts.append(node.text)
        elif node.tag == f"{W_NS}tab":
            parts.append("\t")
        elif node.tag in (f"{W_NS}br", f"{W_NS}cr"):
            parts.append("\n")
    return "".join(parts)


def attr(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    return element.get(f"{W_NS}{name}")


def child(element: ET.Element | None, name: str) -> ET.Element | None:
    if element is None:
        return None
    return element.find(f"{W_NS}{name}")


def path_attr(element: ET.Element | None, *steps: str) -> str | None:
    node = element
    for step in steps:
        node = child(node, step)
        if node is None:
            return None
    return node


# --------------------------------------------------------------------------
# Style resolution
# --------------------------------------------------------------------------


@dataclass
class StyleInfo:
    based_on: str | None
    font: str | None
    size: int | None
    bold: bool | None


class Styles:
    """Minimal resolver for the properties this checker cares about."""

    def __init__(self, root: ET.Element | None) -> None:
        self.styles: dict[str, StyleInfo] = {}
        self.default_paragraph: str | None = None
        self.doc_font: str | None = None
        self.doc_size: int | None = None
        if root is None:
            return

        defaults = child(root, "docDefaults")
        rpr_default = path_attr(defaults, "rPrDefault", "rPr")
        fonts_default = child(rpr_default, "rFonts")
        self.doc_font = attr(fonts_default, "ascii") or attr(fonts_default, "hAnsi")
        size = child(rpr_default, "sz")
        self.doc_size = int(attr(size, "val")) if attr(size, "val") else None

        for style in root.findall(f"{W_NS}style"):
            style_id = attr(style, "styleId")
            if not style_id:
                continue
            if attr(style, "type") == "paragraph" and attr(style, "default") in ("1", "true"):
                self.default_paragraph = style_id
            based = child(style, "basedOn")
            rpr = child(style, "rPr")
            fonts = child(rpr, "rFonts")
            size_el = child(rpr, "sz")
            bold_el = child(rpr, "b")
            self.styles[style_id] = StyleInfo(
                based_on=attr(based, "val"),
                font=attr(fonts, "ascii") or attr(fonts, "hAnsi"),
                size=int(attr(size_el, "val")) if attr(size_el, "val") else None,
                bold=None if bold_el is None else attr(bold_el, "val") not in ("0", "false"),
            )

    def chain(self, style_id: str | None) -> list[str]:
        seen: list[str] = []
        current = style_id or self.default_paragraph
        while current and current not in seen and current in self.styles:
            seen.append(current)
            current = self.styles[current].based_on
        return seen

    def resolve_font(self, run_rpr: ET.Element | None, style_id: str | None) -> str | None:
        fonts = child(run_rpr, "rFonts")
        direct = attr(fonts, "ascii") or attr(fonts, "hAnsi")
        if direct:
            return direct
        for style_id in self.chain(style_id):
            if self.styles[style_id].font:
                return self.styles[style_id].font
        return self.doc_font

    def resolve_size(self, run_rpr: ET.Element | None, style_id: str | None) -> int | None:
        size_el = child(run_rpr, "sz")
        direct = attr(size_el, "val")
        if direct:
            return int(direct)
        for style_id in self.chain(style_id):
            if self.styles[style_id].size:
                return self.styles[style_id].size
        return self.doc_size

    def resolve_bold(self, run_rpr: ET.Element | None, style_id: str | None) -> bool:
        bold_el = child(run_rpr, "b")
        if bold_el is not None:
            return attr(bold_el, "val") not in ("0", "false")
        for style_id in self.chain(style_id):
            if self.styles[style_id].bold is not None:
                return bool(self.styles[style_id].bold)
        return False


# --------------------------------------------------------------------------
# Document reading
# --------------------------------------------------------------------------


def read_part(archive: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        data = archive.read(name)
    except KeyError:
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:  # a corrupt part is worth reporting on its own
        raise ValueError(f"{name} is not valid XML: {exc}") from exc


def check_section(root: ET.Element, report: Report) -> None:
    sections = root.findall(f".//{W_NS}sectPr")
    if not sections:
        report.add("D01", "high", "document has no section properties, page size is unknown")
        return

    for index, sect in enumerate(sections, start=1):
        where = f"section {index}"
        size = child(sect, "pgSz")
        width = attr(size, "w")
        height = attr(size, "h")
        if width and height:
            w_val, h_val = int(width), int(height)
            short, long = sorted((w_val, h_val))
            if (
                abs(short - A4_WIDTH_TWIPS) > SIZE_TOLERANCE_TWIPS
                or abs(long - A4_HEIGHT_TWIPS) > SIZE_TOLERANCE_TWIPS
            ):
                report.add(
                    "D01",
                    "high",
                    f"page size is {w_val / TWIPS_PER_CM:.1f} x "
                    f"{h_val / TWIPS_PER_CM:.1f} cm, expected A4 21.0 x 29.7 cm",
                    where,
                )
        else:
            report.add("D01", "high", "page size is not set", where)

        margins = child(sect, "pgMar")
        for side, expected in MARGINS_CM.items():
            raw = attr(margins, side)
            if raw is None:
                report.add("D02", "high", f"{side} margin is not set", where)
                continue
            actual = int(raw) / TWIPS_PER_CM
            if abs(actual - expected) > 0.1:
                report.add(
                    "D02",
                    "high",
                    f"{side} margin is {actual:.1f} cm, expected {expected:.1f} cm",
                    where,
                )


def paragraph_style_id(paragraph: ET.Element) -> str | None:
    style = path_attr(paragraph, "pPr", "pStyle")
    return attr(style, "val")


def paragraph_spacing(paragraph: ET.Element) -> tuple[str | None, str | None]:
    spacing = path_attr(paragraph, "pPr", "spacing")
    if spacing is None:
        return None, None
    return attr(spacing, "line"), attr(spacing, "lineRule")


def is_structural(style_id: str | None) -> bool:
    if not style_id:
        return False
    lowered = style_id.lower()
    return any(
        marker in lowered
        for marker in ("heading", "title", "toc", "caption", "tableof", "listparagraph")
    )


def has_graphic(element: ET.Element) -> bool:
    for tag in ("drawing", "pict", "object"):
        if element.find(f".//{W_NS}{tag}") is not None:
            return True
    return False


def is_centered(paragraph: ET.Element) -> bool:
    return attr(path_attr(paragraph, "pPr", "jc"), "val") == "center"


def is_centered_heading(
    paragraph: ET.Element, styles: Styles, style_id: str | None
) -> bool:
    """Front-matter headings such as PERSETUJUAN LAPORAN KERJA PRAKTIK.

    The guide sets no body size for these, so judging them as body text is a
    false positive. They are centred, bold, uppercase and short.
    """
    text = text_of(paragraph).strip()
    if not text or len(text) > 80 or not text.isupper():
        return False
    if not is_centered(paragraph):
        return False
    runs = paragraph.findall(f".//{W_NS}r")
    return any(styles.resolve_bold(child(run, "rPr"), style_id) for run in runs)


def title_page_blocks(body: ET.Element) -> set[int]:
    """Block indices that belong to the cover page.

    The cover ends at the first explicit page break. If the document has none,
    fall back to the leading run of centred blocks.
    """
    blocks = [node for node in body if node.tag in (f"{W_NS}p", f"{W_NS}tbl")]
    for index, block in enumerate(blocks):
        for br in block.iter(f"{W_NS}br"):
            if attr(br, "type") == "page":
                return set(range(index + 1))

    cover: set[int] = set()
    for index, block in enumerate(blocks):
        if block.tag != f"{W_NS}p":
            break
        if not text_of(block).strip() and not has_graphic(block):
            continue
        if not is_centered(block):
            break
        cover.add(index)
    return cover


def is_toc_entry(paragraph: ET.Element, text: str) -> bool:
    """Daftar Isi/Gambar/Tabel lines lead to a page number with a tab or dots."""
    if paragraph.find(f".//{W_NS}tab") is not None:
        return True
    return bool(TOC_LEADER_RE.search(text))


def is_editorial_note(text: str) -> bool:
    """A whole paragraph wrapped in brackets is a note left for the student."""
    stripped = text.strip()
    if len(stripped.split()) < 4:
        return False
    pairs = (("[", "]"), ("(", ")"))
    return any(stripped.startswith(a) and stripped.endswith(b) for a, b in pairs)


def check_body(root: ET.Element, styles: Styles, report: Report) -> None:
    body = child(root, "body")
    if body is None:
        report.add("D09", "high", "document has no body")
        return

    blocks = [node for node in body if node.tag in (f"{W_NS}p", f"{W_NS}tbl")]
    cover = title_page_blocks(body)

    wrong_fonts: dict[str, int] = {}
    wrong_sizes: list[str] = []
    single_spaced: list[str] = []
    chapter_issues: list[str] = []
    notes: list[str] = []
    checked = 0

    for index, paragraph in enumerate(blocks):
        if paragraph.tag != f"{W_NS}p":
            continue
        style_id = paragraph_style_id(paragraph)
        text = text_of(paragraph).strip()
        if not text:
            continue

        runs = paragraph.findall(f".//{W_NS}r")
        if not runs:
            continue
        checked += 1
        sample = text[:60]

        for run in runs:
            rpr = child(run, "rPr")
            font = styles.resolve_font(rpr, style_id)
            if font and font != BODY_FONT:
                wrong_fonts[font] = wrong_fonts.get(font, 0) + 1

        if CHAPTER_RE.match(text):
            for run in runs:
                rpr = child(run, "rPr")
                size = styles.resolve_size(rpr, style_id)
                bold = styles.resolve_bold(rpr, style_id)
                if size and size != CHAPTER_SIZE_HALF_POINTS:
                    chapter_issues.append(f"{sample!r} is {size / 2:g} pt, expected 14 pt")
                    break
                if not bold:
                    chapter_issues.append(f"{sample!r} is not bold")
                    break
            continue

        if is_editorial_note(text):
            notes.append(sample)
            continue

        if index in cover or is_structural(style_id) or CAPTION_RE.match(text):
            continue

        if is_centered_heading(paragraph, styles, style_id):
            continue

        size = styles.resolve_size(child(runs[0], "rPr"), style_id)
        if size and size != BODY_SIZE_HALF_POINTS:
            wrong_sizes.append(f"{sample!r} is {size / 2:g} pt, expected 12 pt")

        if is_toc_entry(paragraph, text):
            continue

        line, rule = paragraph_spacing(paragraph)
        if line is None or (rule not in (None, "auto") or line != DOUBLE_LINE):
            single_spaced.append(f"{sample!r} (line={line or 'default'})")

    for font, count in sorted(wrong_fonts.items()):
        report.add(
            "D04",
            "medium",
            f"{count} run(s) use {font}, expected {BODY_FONT}",
        )
    if wrong_sizes:
        report.add(
            "D05",
            "medium",
            f"{len(wrong_sizes)} body paragraph(s) are not 12 pt, e.g. "
            + "; ".join(wrong_sizes[:3]),
        )
    if single_spaced:
        report.add(
            "D06",
            "low",
            f"{len(single_spaced)} body paragraph(s) are not double spaced, e.g. "
            + "; ".join(single_spaced[:3]),
        )
    for issue in chapter_issues[:5]:
        report.add("D07", "medium", f"chapter title {issue}")
    if notes:
        report.add(
            "D10",
            "low",
            f"{len(notes)} paragraph(s) still hold editorial notes, e.g. "
            + "; ".join(notes[:3]),
        )
    if not checked:
        report.add("D09", "high", "document has no text paragraphs")


def check_captions(body: ET.Element, report: Report) -> None:
    blocks = [node for node in body if node.tag in (f"{W_NS}p", f"{W_NS}tbl")]

    for index, block in enumerate(blocks):
        if block.tag != f"{W_NS}p":
            continue
        text = text_of(block).strip()
        match = CAPTION_RE.match(text)
        if not match:
            continue
        if is_toc_entry(block, text):
            continue
        kind = match.group(1)
        previous = blocks[index - 1] if index else None
        following = blocks[index + 1] if index + 1 < len(blocks) else None
        sample = text[:60]

        if kind == "Tabel":
            if following is not None and following.tag == f"{W_NS}tbl":
                continue
            if previous is not None and previous.tag == f"{W_NS}tbl":
                report.add(
                    "D08", "medium", f"table caption {sample!r} sits below its table"
                )
            else:
                report.add(
                    "D08", "low", f"table caption {sample!r} is not followed by a table"
                )
        else:
            if previous is not None and has_graphic(previous):
                continue
            if following is not None and has_graphic(following):
                report.add(
                    "D08", "medium", f"figure caption {sample!r} sits above its figure"
                )
            else:
                report.add(
                    "D08", "low", f"figure caption {sample!r} is not preceded by a figure"
                )


def check_clean(archive: zipfile.ZipFile, root: ET.Element, report: Report) -> None:
    names = set(archive.namelist())
    if "word/comments.xml" in names:
        comments = read_part(archive, "word/comments.xml")
        count = 0 if comments is None else len(comments.findall(f"{W_NS}comment"))
        if count:
            report.add("D03", "high", f"document still holds {count} unresolved comment(s)")

    tracked = list(root.iter(f"{W_NS}ins")) + list(root.iter(f"{W_NS}del"))
    if tracked:
        report.add(
            "D03",
            "high",
            f"document still holds {len(tracked)} tracked change(s), accept or reject them",
        )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def run(path: Path) -> Report:
    report = Report()
    if not path.is_file():
        report.add("D00", "high", f"{path} does not exist")
        return report
    if path.suffix.lower() != ".docx":
        report.add("D00", "high", f"{path.name} is not a .docx file")
        return report

    try:
        with zipfile.ZipFile(path) as archive:
            document = read_part(archive, "word/document.xml")
            styles_root = read_part(archive, "word/styles.xml")
            if document is None:
                report.add("D00", "high", "word/document.xml is missing, not a Word file")
                return report
            styles = Styles(styles_root)
            check_section(document, report)
            body = child(document, "body")
            if body is not None:
                check_captions(body, report)
            check_body(document, styles, report)
            check_clean(archive, document, report)
    except zipfile.BadZipFile:
        report.add("D00", "high", f"{path.name} is not a valid .docx archive")
    except ValueError as exc:
        report.add("D00", "high", str(exc))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a Kerja Praktik .docx against the Bina Insani format rules."
    )
    parser.add_argument("docx", type=Path, help="path to the .docx file")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--fail-on",
        choices=("high", "medium", "low", "none"),
        default="high",
        help="lowest severity that makes the exit code 1 (default: high)",
    )
    args = parser.parse_args()

    report = run(args.docx)
    threshold = SEVERITY_ORDER[args.fail_on]

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(args.docx),
                    "worst": report.worst,
                    "counts": {
                        level: report.count(level) for level in ("high", "medium", "low")
                    },
                    "findings": [f.as_dict() for f in report.findings],
                },
                indent=2,
            )
        )
    else:
        print(f"File: {args.docx}")
        print(
            "Findings: "
            + ", ".join(
                f"{report.count(level)} {level}" for level in ("high", "medium", "low")
            )
        )
        print()
        for finding in sorted(
            report.findings, key=lambda f: SEVERITY_ORDER[f.severity], reverse=True
        ):
            where = f" [{finding.where}]" if finding.where else ""
            print(f"{finding.severity.upper():6} {finding.rule}{where}  {finding.message}")
        if not report.findings:
            print("OK: no formatting problems found.")
        else:
            print()
            print(f"Worst severity: {report.worst}")

    failed = any(SEVERITY_ORDER[f.severity] >= threshold for f in report.findings)
    return 1 if failed and threshold > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
