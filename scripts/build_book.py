#!/usr/bin/env python3
"""Build a print-style, searchable PDF novel from the Markdown manuscript.

Run from the repository root:
    python scripts/build_book.py

Dependency: reportlab (pip install reportlab)
"""
from __future__ import annotations

import html
import math
import os
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "books" / "The_Last_Watch_Extended_Edition.pdf"
PAGE_W, PAGE_H = 6.0 * inch, 9.0 * inch
NAVY = colors.HexColor("#10263e")
MIDNIGHT = colors.HexColor("#071523")
FOAM = colors.HexColor("#c5dceb")
GOLD = colors.HexColor("#c8a66b")
INK = colors.HexColor("#273442")
MUTED = colors.HexColor("#526578")

def font(name: str, candidates: list[str], fallback: str) -> str:
    for c in candidates:
        if Path(c).exists():
            pdfmetrics.registerFont(TTFont(name, c))
            return name
    return fallback

SANS = font("DPN-Sans", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
], "Helvetica")
SANS_BOLD = font("DPN-Sans-Bold", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
], "Helvetica-Bold")
SERIF = font("DPN-Serif", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
], "Times-Roman")
SERIF_BOLD = font("DPN-Serif-Bold", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
], "Times-Bold")
SERIF_ITALIC = font("DPN-Serif-Italic", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
], "Times-Italic")
pdfmetrics.registerFontFamily(SERIF, normal=SERIF, bold=SERIF_BOLD, italic=SERIF_ITALIC,
                              boldItalic=SERIF_BOLD)
pdfmetrics.registerFontFamily(SANS, normal=SANS, bold=SANS_BOLD,
                              italic=SANS, boldItalic=SANS_BOLD)

ST = {
    "title": ParagraphStyle("title", fontName=SERIF_BOLD, fontSize=23, leading=31,
                            textColor=NAVY, spaceAfter=18, alignment=TA_CENTER),
    "sub": ParagraphStyle("sub", fontName=SANS, fontSize=9, leading=16,
                          textColor=MUTED, spaceAfter=16, alignment=TA_CENTER),
    "copyright": ParagraphStyle("copyright", fontName=SERIF, fontSize=9,
                               leading=16, textColor=INK, spaceAfter=12),
    "heading": ParagraphStyle("chapter", fontName=SERIF_BOLD, fontSize=17,
                             leading=24, textColor=NAVY, spaceAfter=23, spaceBefore=7,
                             keepWithNext=True),
    "intro": ParagraphStyle("intro", fontName=SANS_BOLD, fontSize=8.0, leading=14,
                           textColor=MUTED, spaceAfter=15, spaceBefore=2),
    "body": ParagraphStyle("body", fontName=SERIF, fontSize=9.7, leading=16.1,
                          textColor=INK, alignment=TA_LEFT, spaceAfter=11,
                          allowWidows=0, allowOrphans=0),
    "quote": ParagraphStyle("quote", fontName=SERIF_ITALIC, fontSize=10.3,
                           leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=14,
                           leftIndent=17, rightIndent=16),
    "center": ParagraphStyle("center", fontName=SERIF_ITALIC, fontSize=10,
                            leading=17, textColor=INK, spaceBefore=10, spaceAfter=14,
                            alignment=TA_CENTER),
    "tochead": ParagraphStyle("tochead", fontName=SERIF_BOLD, fontSize=20,
                             leading=28, textColor=NAVY, spaceAfter=24),
    "toc": ParagraphStyle("toc", fontName=SERIF, fontSize=9.8,
                         leading=17, textColor=INK, leftIndent=7, firstLineIndent=0),
}

def inline_md(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text

class NovelDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=(PAGE_W, PAGE_H), leftMargin=52,
                         rightMargin=48, topMargin=57, bottomMargin=53,
                         title="The Last Watch — Extended Edition",
                         author="DPN Technology",
                         subject="An original fictional naval war novel",
                         pageCompression=1)
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0,
                            bottomPadding=0, topPadding=0, id="coverframe")
        body_frame = Frame(self.leftMargin, self.bottomMargin,
                           self.width, self.height,
                           leftPadding=0, rightPadding=0, topPadding=0,
                           bottomPadding=0, id="bodyframe")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="Body", frames=[body_frame], onPage=draw_body),
        ])
        self.chapter_num = 0

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "chapter":
            title = flowable.getPlainText()
            self.chapter_num += 1
            key = f"chapter_{self.chapter_num}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (0, title, self.page, key))

class CoverSpacer(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 1
        self.height = PAGE_H - 1
    def draw(self):
        pass

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MIDNIGHT)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # A subtle horizon and sea, composed of vector shapes rather than a raster image.
    for i in range(9):
        y = 85 + 22 * i
        canvas.setFillColor(colors.Color(0.07 + i*.009, .17 + i*.007,
                                        .28 + i*.006, alpha=1))
        canvas.rect(0, y, PAGE_W, 23, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#214660"))
    canvas.setLineWidth(.65)
    for i in range(28):
        y = 75 + i * 13
        wave = canvas.beginPath()
        wave.moveTo(-30, y)
        for j in range(9):
            x = j * 66 - 30
            wave.curveTo(x + 15, y + (i%3)*2.2, x + 38, y - 6.0, x + 66, y)
        canvas.drawPath(wave, stroke=1, fill=0)

    # Minimal warship profile in silhouette near the horizon.
    canvas.setFillColor(colors.HexColor("#020b13"))
    ship = canvas.beginPath()
    ship.moveTo(26, 258)
    ship.lineTo(392, 258)
    ship.lineTo(365, 236)
    ship.lineTo(68, 236)
    ship.close()
    canvas.drawPath(ship, fill=1, stroke=0)
    canvas.rect(120, 258, 176, 12, fill=1, stroke=0)
    canvas.rect(150, 270, 107, 22, fill=1, stroke=0)
    canvas.rect(182, 292, 47, 27, fill=1, stroke=0)
    canvas.rect(202, 319, 4, 55, fill=1, stroke=0)
    canvas.rect(173, 330, 73, 2, fill=1, stroke=0)
    canvas.rect(292, 270, 25, 6, fill=1, stroke=0)

    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.2)
    canvas.line(61, PAGE_H - 111, PAGE_W - 61, PAGE_H - 111)
    canvas.setFillColor(FOAM)
    canvas.setFont(SANS_BOLD, 10)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 82, "DPN TECHNOLOGY  /  ORIGINAL FICTION")
    canvas.setFillColor(colors.white)
    canvas.setFont(SERIF_BOLD, 37)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 172, "THE LAST")
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 219, "WATCH")
    canvas.setFillColor(GOLD)
    canvas.setFont(SANS_BOLD, 10)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 260, "A NORTH ATLANTIC WAR NOVEL")
    canvas.setFillColor(FOAM)
    canvas.setFont(SERIF_ITALIC, 11)
    canvas.drawCentredString(PAGE_W / 2, 155, "The ocean does not decide who we are.")
    canvas.drawCentredString(PAGE_W / 2, 137, "Our actions do.")
    canvas.setFillColor(GOLD)
    canvas.setFont(SANS, 8.5)
    canvas.drawCentredString(PAGE_W / 2, 44, "EXTENDED MANUSCRIPT EDITION  •  2026")
    canvas.restoreState()

def draw_body(canvas, doc):
    canvas.saveState()
    page = doc.page
    canvas.setStrokeColor(colors.HexColor("#d6dfe5"))
    canvas.setLineWidth(.45)
    canvas.line(52, PAGE_H - 39, PAGE_W - 48, PAGE_H - 39)
    canvas.setFillColor(MUTED)
    canvas.setFont(SANS, 7.0)
    canvas.drawString(52, PAGE_H - 30, "THE LAST WATCH")
    canvas.drawRightString(PAGE_W - 48, PAGE_H - 30, "DPN TECHNOLOGY")
    canvas.line(52, 39, PAGE_W - 48, 39)
    canvas.setFont(SANS, 7.7)
    canvas.drawCentredString(PAGE_W / 2, 24, str(max(1, page - 1)))
    canvas.restoreState()

def read_manuscript():
    parts = sorted((ROOT / "manuscript").glob("part-*.md"))
    if not parts:
        raise SystemExit("No manuscript parts were found.")
    raw = "\n\n".join(p.read_text(encoding="utf-8") for p in parts)
    chapter_count = len(re.findall(r"(?m)^# CHAPTER \w+", raw))
    words = len(re.findall(r"\b[\w’'-]+\b", raw))
    if chapter_count != 13 or "# EPILOGUE" not in raw or words < 9000:
        raise SystemExit(f"Manuscript incomplete: {chapter_count} chapters, {words} words")
    return raw, words, chapter_count

def paragraphs_of(raw):
    blocks = []
    acc = []
    for line in raw.splitlines():
        if not line.strip():
            if acc:
                blocks.append("\n".join(acc).strip())
                acc = []
        else:
            acc.append(line.strip())
    if acc:
        blocks.append("\n".join(acc).strip())
    return blocks

def make_book(raw, word_count):
    story = []
    story.append(CoverSpacer())
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    story.append(Spacer(1, 80))
    story.append(Paragraph("THE LAST WATCH", ST["title"]))
    story.append(Paragraph("A North Atlantic War Novel · Extended Manuscript Edition", ST["sub"]))
    story.append(Spacer(1, 25))
    story.append(Paragraph("An original work of naval military fiction told through the eyes of Commander Daniel Vale, Commanding Officer, USS Northstar.", ST["copyright"]))
    story.append(Paragraph(f"Approximately {word_count:,} words. Designed for long-form reading or narration.", ST["copyright"]))
    story.append(Paragraph("© 2026 DPN Technology. All rights reserved. This fictional story may not be reproduced, redistributed, or adapted without the rights holder's permission, except where applicable law permits.", ST["copyright"]))
    story.append(Paragraph("The characters, naval vessels, units, nations' actions, and events portrayed in this book are invented. Any resemblance to actual people or operations is coincidental.", ST["copyright"]))
    story.append(PageBreak())

    story.append(Paragraph("CONTENTS", ST["tochead"]))
    toc = TableOfContents()
    toc.levelStyles = [ST["toc"]]
    story.append(toc)
    story.append(PageBreak())

    started = False
    for block in paragraphs_of(raw):
        if block.startswith("# PROLOGUE") or block.startswith("# CHAPTER ") or block.startswith("# EPILOGUE"):
            started = True
            story.append(PageBreak())
            story.append(Paragraph(inline_md(block[2:]), ST["heading"]))
            continue
        if not started:
            continue
        if block in ("---", "***"):
            story.append(Spacer(1, 13))
            continue
        if block.startswith("**") and block.endswith("**") and "\n" not in block:
            story.append(Paragraph(inline_md(block), ST["intro"]))
            continue
        if block.startswith("> "):
            story.append(Paragraph(inline_md(block[2:]), ST["quote"]))
            continue
        if block.startswith("*") and block.endswith("*") and "\n" not in block:
            story.append(Paragraph(inline_md(block), ST["center"]))
            continue
        s = " ".join(block.splitlines())
        story.append(Paragraph(inline_md(s), ST["body"]))

    doc = NovelDoc(OUT)
    doc.multiBuild(story, maxPasses=5)

def main():
    raw, words, chapters = read_manuscript()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    make_book(raw, words)
    print(f"Built {OUT.relative_to(ROOT)}: {chapters} chapters, {words:,} words, {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
