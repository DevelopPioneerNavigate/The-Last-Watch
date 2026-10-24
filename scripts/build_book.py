#!/usr/bin/env python3
"""Build a print-style, searchable PDF novel from the Markdown manuscript.

Run from the repository root:
    python scripts/build_book.py

Dependency: reportlab (pip install reportlab)
"""
from __future__ import annotations

import html
import hashlib
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
                         title="The Last Watch — Expanded Novel Edition",
                         author="Diesel (DPN Novels)",
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
            key = "chapter_" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:12]
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
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 82, "DPN NOVELS  /  ORIGINAL FICTION")
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
    canvas.drawCentredString(PAGE_W / 2, 44, "WRITTEN BY DIESEL  •  DPN NOVELS")
    canvas.restoreState()


class InkPlate(Flowable):
    """Original print-friendly vector illustration between the chapter heading and text."""
    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode
        self.width = 322
        self.height = 106

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        c.saveState()
        c.setFillColor(colors.HexColor("#10263e"))
        c.roundRect(0, 0, w, h, 5, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#446e8b"))
        c.setLineWidth(.65)
        # Fine, repeating sea lines echo a woodcut printed with blue ink.
        for n in range(11):
            y = 12 + n * 6.8
            p = c.beginPath()
            p.moveTo(7, y)
            for k in range(7):
                x = 7 + k*45
                p.curveTo(x+14, y+2.6, x+30, y-3.4, x+45, y)
            c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(colors.HexColor("#d9e4ee"))
        if self.mode == "watch":
            # Opening frontispiece: an unbroken horizon and the midnight watch.
            c.setFillColor(colors.HexColor("#e2c793"))
            c.circle(257,82,10,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#071523"))
            p=c.beginPath()
            p.moveTo(40,37);p.lineTo(280,37)
            p.lineTo(259,25);p.lineTo(62,25)
            p.close();c.drawPath(p,fill=1,stroke=0)
            c.rect(116,38,92,11,fill=1,stroke=0)
            c.rect(145,49,46,22,fill=1,stroke=0)
            c.rect(166,71,3,24,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#a6c7da"))
            c.setLineWidth(1)
            c.line(167,90,221,68)
            c.line(78,17,244,17)
            for x in (89,109,130,200,231):
                c.circle(x,80 if x%2 else 66,1.5,stroke=1,fill=0)
        elif self.mode == "storm":
            # Dark destroyer silhouette advancing through the moonlit sea.
            c.setFillColor(colors.HexColor("#acc8dd"))
            c.circle(274, 80, 12, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#04111e"))
            p=c.beginPath(); p.moveTo(42,42); p.lineTo(266,42); p.lineTo(236,28)
            p.lineTo(73,28); p.close(); c.drawPath(p, fill=1, stroke=0)
            c.rect(112,43,104,10,stroke=0,fill=1)
            c.rect(146,53,41,19,stroke=0,fill=1)
            c.rect(164,71,3,21,stroke=0,fill=1)
            c.rect(136,77,58,1.5,stroke=0,fill=1)
        elif self.mode == "convoy":
            # Four merchant hulls beneath an escort silhouette: a stylized departure.
            c.setFillColor(colors.HexColor("#d0e4ed"))
            c.circle(265,83,11,stroke=0,fill=1)
            c.setFillColor(colors.HexColor("#071724"))
            for x,y,size in ((35,49,43),(89,43,51),(161,48,43),(231,42,54)):
                p=c.beginPath()
                p.moveTo(x,y);p.lineTo(x+size,y);p.lineTo(x+size-6,y-11)
                p.lineTo(x+8,y-11);p.close();c.drawPath(p,fill=1,stroke=0)
                c.rect(x+12,y+1,size*.35,11,stroke=0,fill=1)
                c.rect(x+21,y+12,2,12,stroke=0,fill=1)
            c.setStrokeColor(colors.HexColor("#e2b875"))
            c.setLineWidth(1)
            c.line(28,28,293,28)
            c.line(37,22,280,22)
        elif self.mode == "radar":
            c.setStrokeColor(colors.HexColor("#b3d2e8"))
            for r in (19,32,47):
                c.circle(161,53,r,stroke=1,fill=0)
            c.line(102,53,220,53)
            c.line(161,5,161,101)
            c.setStrokeColor(colors.HexColor("#e0b878"))
            c.setLineWidth(2)
            for x,y in ((199,80),(128,30),(170,93),(112,64)):
                c.line(x-3,y-3,x+3,y+3)
                c.line(x-3,y+3,x+3,y-3)
        elif self.mode == "rescue":
            # A searchlight reaches across rough water toward a rescue boat.
            c.setFillColor(colors.HexColor("#ebd7ae"))
            p=c.beginPath()
            p.moveTo(94,71);p.lineTo(280,41);p.lineTo(279,20)
            p.close();c.drawPath(p,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#081b29"))
            c.rect(42,45,83,22,stroke=0,fill=1)
            c.rect(66,67,23,19,stroke=0,fill=1)
            c.rect(77,86,2,13,stroke=0,fill=1)
            p=c.beginPath()
            p.moveTo(171,32);p.lineTo(259,32);p.lineTo(244,24)
            p.lineTo(184,24);p.close();c.drawPath(p,fill=1,stroke=0)
            for x in (192,210,227):
                c.circle(x,38,4,stroke=0,fill=1)
                c.rect(x-2,32,4,5,stroke=0,fill=1)
            c.setStrokeColor(colors.HexColor("#9fc5da"))
            c.setLineWidth(2)
            c.arc(251,15,269,30,180,130)
        elif self.mode == "fire":
            c.setFillColor(colors.HexColor("#07131d"))
            c.rect(52,17,214,78,stroke=0,fill=1)
            c.setStrokeColor(colors.HexColor("#bcd1e0"))
            c.setLineWidth(2)
            for x in (65,99,230,256):
                c.line(x,20,x,91)
            for y in (25,46,85):
                c.line(65,y,256,y)
            c.setFillColor(colors.HexColor("#e4a867"))
            p=c.beginPath();p.moveTo(140,19);p.curveTo(122,48,159,52,150,87)
            p.curveTo(185,56,195,36,176,19);p.close();c.drawPath(p,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#fff0c7"))
            p=c.beginPath();p.moveTo(151,20);p.curveTo(141,39,163,45,157,66)
            p.curveTo(172,43,178,31,169,20);p.close();c.drawPath(p,fill=1,stroke=0)
        elif self.mode == "wreckage":
            # An isolated wing fragment and reflected starlight, the unnamed aircrew.
            c.setFillColor(colors.HexColor("#b2cedd"))
            c.circle(260,80,9,stroke=0,fill=1)
            c.setFillColor(colors.HexColor("#0a1b28"))
            p=c.beginPath()
            p.moveTo(81,50);p.lineTo(186,63);p.lineTo(230,51)
            p.lineTo(172,44);p.lineTo(128,34);p.lineTo(94,35)
            p.close();c.drawPath(p,stroke=0,fill=1)
            c.setStrokeColor(colors.HexColor("#e8ba81"))
            c.setLineWidth(2)
            c.line(126,47,142,49)
            c.setStrokeColor(colors.HexColor("#bdd5e5"))
            c.setLineWidth(1)
            for x in (60,108,154,205,249):
                c.line(x,22,x+28,22)
        elif self.mode == "horizon":
            # Two distant surface ships divided by uncertain weather.
            c.setFillColor(colors.HexColor("#9fb9cd"))
            for x,y in ((75,65),(110,77),(168,70),(246,82)):
                c.circle(x,y,1.5,stroke=0,fill=1)
            c.setFillColor(colors.HexColor("#061523"))
            for x,size,y in ((54,117,37),(196,89,30)):
                p=c.beginPath()
                p.moveTo(x,y);p.lineTo(x+size,y)
                p.lineTo(x+size-14,y-10);p.lineTo(x+17,y-10)
                p.close();c.drawPath(p,stroke=0,fill=1)
                c.rect(x+size*.34,y, size*.29,12,fill=1,stroke=0)
                c.rect(x+size*.46,y+12,3,19,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#ecc38c"))
            c.setLineWidth(1)
            c.line(159,18,164,77)
        elif self.mode == "night":
            # A solitary escort riding beneath a starless North Atlantic sky.
            c.setFillColor(colors.HexColor("#071827"))
            c.circle(268,79,11,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#e6c794"))
            for x,y in ((50,82),(92,69),(173,87),(242,88),(282,65)):
                c.circle(x,y,1.1,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#05121f"))
            p=c.beginPath();p.moveTo(68,45);p.lineTo(240,45)
            p.lineTo(220,32);p.lineTo(89,32);p.close();c.drawPath(p,fill=1,stroke=0)
            c.rect(120,45,64,12,fill=1,stroke=0)
            c.rect(146,57,3,24,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#b6d2e3"))
            c.setLineWidth(1.3)
            for i in range(4):
                c.line(41,19+i*5,280,19+i*5)
        elif self.mode == "letter":
            # An envelope, folded flag and fountain pen: Vale's first private account.
            c.setFillColor(colors.HexColor("#d2e3ea"))
            c.roundRect(79,18,159,70,4,stroke=0,fill=1)
            c.setStrokeColor(colors.HexColor("#244962"))
            c.setLineWidth(1.5)
            p=c.beginPath()
            p.moveTo(79,88);p.lineTo(159,47);p.lineTo(238,88)
            c.drawPath(p,stroke=1,fill=0)
            c.line(79,18,130,59)
            c.line(238,18,190,59)
            c.setStrokeColor(colors.HexColor("#bc965f"))
            c.setLineWidth(2)
            c.line(204,76,258,20)
            c.setFillColor(colors.HexColor("#e4c08a"))
            p=c.beginPath();p.moveTo(258,20);p.lineTo(264,16)
            p.lineTo(260,27);p.close();c.drawPath(p,stroke=0,fill=1)
        elif self.mode == "engine":
            # A shipboard turbine silhouette, electrical pathways and repair tools.
            c.setFillColor(colors.HexColor("#0a1b2b"))
            c.roundRect(48,28,222,54,3,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#b5d6e7"))
            c.setLineWidth(2)
            c.circle(121,54,22,fill=0,stroke=1)
            c.circle(121,54,9,fill=0,stroke=1)
            c.circle(219,54,16,fill=0,stroke=1)
            c.line(144,54,203,54)
            c.line(84,54,99,54)
            for x,y in ((120,76),(145,54),(120,32),(97,54)):
                c.line(121,54,x,y)
            c.setStrokeColor(colors.HexColor("#e2ba7a"))
            c.setLineWidth(1.6)
            c.line(78,87,239,87)
            c.line(78,20,239,20)
            c.line(173,20,173,42)
            c.line(173,68,173,87)
        elif self.mode == "fisher":
            # The small rescue trawler approaching a broad sea under a searchlight.
            c.setFillColor(colors.HexColor("#e5cb9c"))
            p=c.beginPath()
            p.moveTo(90,82);p.lineTo(288,48);p.lineTo(288,27)
            p.close();c.drawPath(p,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#061726"))
            p=c.beginPath()
            p.moveTo(65,42);p.lineTo(244,42);p.lineTo(222,27)
            p.lineTo(87,27);p.close();c.drawPath(p,fill=1,stroke=0)
            c.rect(116,43,73,22,fill=1,stroke=0)
            c.rect(141,65,4,25,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#b2d4e7"))
            c.setLineWidth(1.3)
            c.line(143,88,212,55)
            c.line(113,65,189,65)
            for x in (50,104,172,231):
                c.line(x,18,x+41,18)
        elif self.mode == "salvo":
            # A distant defensive missile engagement over a black Atlantic horizon.
            c.setFillColor(colors.HexColor("#f5e3bb"))
            c.circle(253,74,9,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#b5d8e9"))
            c.setLineWidth(1.5)
            for x,y in ((50,26),(119,34),(200,20)):
                c.line(x,y,x+42,y+38)
            c.setStrokeColor(colors.HexColor("#e7b577"))
            c.setLineWidth(3)
            c.line(78,29,144,75)
            c.line(168,27,211,63)
            c.setFillColor(colors.HexColor("#071827"))
            p=c.beginPath();p.moveTo(52,36);p.lineTo(286,36)
            p.lineTo(267,22);p.lineTo(72,22)
            p.close();c.drawPath(p,fill=1,stroke=0)
            c.rect(137,36,67,13,fill=1,stroke=0)
            c.rect(164,49,4,17,fill=1,stroke=0)
        elif self.mode == "memorial":
            # A folded flag and ship's bell, an understated memorial plate.
            c.setFillColor(colors.HexColor("#cedde6"))
            c.setStrokeColor(colors.HexColor("#e7bc7a"))
            c.setLineWidth(2)
            c.line(90,32,231,32)
            p=c.beginPath()
            p.moveTo(139,32);p.lineTo(174,80);p.lineTo(209,32)
            p.close();c.drawPath(p,stroke=1,fill=0)
            c.setFillColor(colors.HexColor("#e9c88d"))
            c.circle(174,33,4,stroke=0,fill=1)
            c.setFillColor(colors.HexColor("#233e60"))
            p=c.beginPath()
            p.moveTo(74,20);p.lineTo(112,65);p.lineTo(151,20)
            p.close();c.drawPath(p,fill=1,stroke=0)
            c.setStrokeColor(colors.HexColor("#e4e9ef"))
            for x in (96,108,120,132):
                c.line(x,23,x+19,44)
        else:
            # Distant harbor lights and coastline in early winter evening.
            c.setFillColor(colors.HexColor("#94b6d1"))
            p=c.beginPath();p.moveTo(0,46);p.lineTo(45,60);p.lineTo(88,53)
            p.lineTo(132,70);p.lineTo(180,58);p.lineTo(230,73);p.lineTo(w,53)
            p.lineTo(w,0);p.lineTo(0,0);p.close();c.drawPath(p,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#0c2237"))
            c.rect(195,47,12,31,stroke=0,fill=1)
            c.rect(198,78,6,9,stroke=0,fill=1)
            c.setFillColor(colors.HexColor("#f0c98a"))
            c.circle(201,86,2.6,stroke=0,fill=1)
            for x,y in ((72,59),(105,58),(246,73),(280,68)):
                c.circle(x,y,1.5,stroke=0,fill=1)
        c.restoreState()

def draw_body(canvas, doc):
    canvas.saveState()
    page = doc.page
    canvas.setStrokeColor(colors.HexColor("#d6dfe5"))
    canvas.setLineWidth(.45)
    canvas.line(52, PAGE_H - 39, PAGE_W - 48, PAGE_H - 39)
    canvas.setFillColor(MUTED)
    canvas.setFont(SANS, 7.0)
    canvas.drawString(52, PAGE_H - 30, "THE LAST WATCH")
    canvas.drawRightString(PAGE_W - 48, PAGE_H - 30, "DIESEL  /  DPN NOVELS")
    canvas.line(52, 39, PAGE_W - 48, 39)
    canvas.setFont(SANS, 7.7)
    canvas.drawCentredString(PAGE_W / 2, 24, str(max(1, page - 1)))
    canvas.restoreState()

SCENE_PATTERN = re.compile(r"(?m)^\{\{scene:([a-z0-9-]+\.md)\}\}$")

def read_manuscript():
    parts = sorted((ROOT / "manuscript").glob("part-*.md"))
    if not parts:
        raise SystemExit("No manuscript parts were found.")

    raw = "\n\n".join(p.read_text(encoding="utf-8") for p in parts)
    included = []

    def insert_scene(match):
        name = match.group(1)
        if name in included:
            raise SystemExit(f"Scene referenced more than once: {name}")
        path = ROOT / "manuscript" / "scenes" / name
        if not path.is_file():
            raise SystemExit(f"Missing scene: {path}")
        scene_text = path.read_text(encoding="utf-8").strip()
        if not scene_text or "# CHAPTER" in scene_text or "{{scene:" in scene_text:
            raise SystemExit(f"Invalid scene source: {name}")
        included.append(name)
        return scene_text

    raw = SCENE_PATTERN.sub(insert_scene, raw)
    if "{{scene:" in raw:
        raise SystemExit("Unresolved scene directive in manuscript.")
    scene_files = list((ROOT / "manuscript" / "scenes").glob("*.md"))
    if sorted(p.name for p in scene_files) != sorted(included):
        raise SystemExit("Every scene file must be referenced exactly once in the core manuscript.")

    chapter_count = len(re.findall(r"(?m)^# CHAPTER \w+", raw))
    words = len(re.findall(r"\b[\w’'-]+\b", raw))
    if chapter_count != 13 or "# EPILOGUE" not in raw or words < 68000 or len(included) < 52:
        raise SystemExit(f"Manuscript incomplete: {chapter_count} chapters, {len(included)} scenes, {words} words")
    return raw, words, chapter_count, len(included)

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
    story.append(Paragraph("A North Atlantic War Novel · Written by Diesel · DPN Novels", ST["sub"]))
    story.append(Spacer(1, 25))
    story.append(Paragraph("Written by Diesel. Published under the DPN Novels imprint. An original work of naval military fiction told through the eyes of Commander Daniel Vale, Commanding Officer, USS Northstar.", ST["copyright"]))
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
    section_seen = False
    chapter_idx = 0
    for block in paragraphs_of(raw):
        if block.startswith("# THE LAST WATCH") or block.startswith("## Extended Manuscript"):
            continue
        if block.startswith("# PROLOGUE") or block.startswith("# CHAPTER ") or block.startswith("# EPILOGUE"):
            started = True
            if section_seen:
                story.append(PageBreak())
            section_seen = True
            story.append(Paragraph(inline_md(block[2:]), ST["heading"]))
            chapter_idx += 1
            art_mode = {1: "watch", 2: "storm", 3: "convoy", 4: "rescue", 5: "radar", 6: "fisher", 7: "wreckage", 8: "salvo", 9: "horizon", 10: "fire", 11: "engine", 12: "night", 13: "harbor", 14: "memorial", 15: "letter"}.get(chapter_idx)
            if art_mode:
                story.append(InkPlate(art_mode))
                story.append(Spacer(1, 12))
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
    raw, words, chapters, scenes = read_manuscript()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    make_book(raw, words)
    print(f"Built {OUT.relative_to(ROOT)}: {chapters} chapters, {scenes} expanded scenes, {words:,} words, {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
