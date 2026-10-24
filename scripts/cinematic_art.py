#!/usr/bin/env python3
"""Verified cinematic artwork for the Diesel / DPN Novels print PDF.

The single source archive lives at artwork/cinematic/The_Last_Watch_Cinematic_Plates.zip.
Images are never downloaded dynamically or generated in CI. Every entry is
SHA-256 checked against the committed manifest before it can enter the book.
If the archive is absent, use the older all-vector edition without claiming
the cinematic pictures are present.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable
from PIL import Image as PILImage, ImageFilter, ImageOps

PAGE_W, PAGE_H = 432, 648
ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artwork" / "cinematic"
ARCHIVE = ART / "The_Last_Watch_Cinematic_Plates.zip"
MANIFEST = ART / "manifest.json"
PLATES = ART / "plates"


def _clean(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def activate_cinematic_art():
    """Return manifest entries only when *every* source image verifies.

    Keep the archive (not unpacked copies) as the committed, reproducible source.
    No partial illustrated editions are produced.
    """
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = data.get("assets", [])
    if len(entries) < 10 or len({x["anchor"] for x in entries}) != len(entries):
        raise ValueError("Cinematic manifest must have at least ten unique placements")
    if not ARCHIVE.is_file():
        # Production fallback: source-controlled individual cinematic JPEGs.
        # These files are already committed, so no external image host or ZIP
        # is needed to reproduce the PDF in GitHub Actions.
        direct_path = ART / "committed_manifest.json"
        if direct_path.is_file():
            direct = json.loads(direct_path.read_text(encoding="utf-8"))
            direct_entries = direct.get("assets", [])
            if len(direct_entries) < 9:
                raise ValueError("Committed cinematic manifest must list cover and eight scenes")
            if len({e["anchor"] for e in direct_entries}) != len(direct_entries):
                raise ValueError("Duplicate committed cinematic scene anchors")
            if sum(e["anchor"] == "cover" for e in direct_entries) != 1:
                raise ValueError("Exactly one committed cinematic cover required")
            for e in direct_entries:
                filename = e["file"]
                if Path(filename).name != filename or not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    raise ValueError(f"Unsafe committed cinematic filename: {filename}")
                # Image assets may reside in the original artwork folder or in
                # the separately committed cinematic asset collection.
                asset_path = e.get("source_path")
                if asset_path:
                    parts = Path(asset_path).parts
                    if len(parts) != 3 or parts[:2] != ("assets", "cinematic") or parts[2] != filename:
                        raise ValueError(f"Unsafe cinematic asset path: {asset_path}")
                    target = ROOT / asset_path
                else:
                    target = ART / filename
                if not target.is_file():
                    raise FileNotFoundError(f"Missing committed cinematic image: {target}")
                raw = target.read_bytes()
                if not 25_000 <= len(raw) <= 14_000_000:
                    raise ValueError(f"Invalid size for cinematic image: {target}")
                if hashlib.sha256(raw).hexdigest() != e["sha256"]:
                    raise ValueError(f"Committed cinematic image hash mismatch: {target}")
                e["path"] = target
            print(f"CINEMATIC ART ACTIVE: verified {len(direct_entries)} committed cover/scene placements")
            return direct_entries
        if os.environ.get("DPN_REQUIRE_CINEMATIC") == "1":
            raise FileNotFoundError("No verified cinematic image pack or committed images")
        return []

    PLATES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        for item in entries:
            filename = item["file"]
            if Path(filename).name != filename or not filename.lower().endswith((".jpeg", ".jpg", ".png")):
                raise ValueError(f"Unsafe cinematic file name: {filename}")
            name = "plates/" + filename
            try:
                raw = z.read(name)
            except KeyError as exc:
                raise ValueError(f"Missing plate from cinematic archive: {name}") from exc
            sha = hashlib.sha256(raw).hexdigest()
            if sha != item["sha256"]:
                raise ValueError(f"Image integrity mismatch: {name}")
            if len(raw) < 25_000 or len(raw) > 14_000_000:
                raise ValueError(f"Unexpected image size: {name}")
            # Avoid decoding and rewriting JPEG bytes, which would change the
            # color quality and the hash; leave print artwork unmodified.
            target = PLATES / filename
            if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                target.write_bytes(raw)
            item["path"] = target

    if sum(a["anchor"] == "cover" for a in entries) != 1:
        raise ValueError("Exactly one cinematic cover is required")
    print(f"CINEMATIC ART ACTIVE: verified {len(entries)} original illustrated assets")
    return entries


def scene_plate(entries, scene_heading: str):
    """Match a scene heading (including its '— time' suffix) to exactly one photo."""
    heading = _clean(scene_heading.replace("*", ""))
    matches = [e for e in entries if e["anchor"] != "cover" and _clean(e["anchor"]) in heading]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous cinematic heading: {scene_heading}")
    return matches[0] if matches else None


def cover_plate(entries):
    return next((entry for entry in entries if entry["anchor"] == "cover"), None)


def draw_cinematic_cover(canvas, entry, serif_bold, sans_bold):
    """Photo cover with restrained print-legible type, replacing basic silhouette."""
    if not entry:
        return False
    canvas.saveState()
    _cover_photo(canvas, entry["path"])
    if entry.get("prelettered"):
        # Artwork already bears the title, author and imprint: do not conceal it
        # beneath an additional typography overlay.
        canvas.restoreState()
        return True
    canvas.setFillColor(colors.Color(0.005, .018, .04, alpha=.75))
    canvas.rect(0, PAGE_H - 270, PAGE_W, 270, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#d6bb80"))
    canvas.setFont(sans_bold, 10)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 76, "DPN NOVELS  /  AN ORIGINAL NAVAL WAR NOVEL")
    canvas.setStrokeColor(colors.HexColor("#d6bb80"))
    canvas.setLineWidth(.9)
    canvas.line(55, PAGE_H - 96, PAGE_W - 55, PAGE_H - 96)
    canvas.setFillColor(colors.white)
    canvas.setFont(serif_bold, 36)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 165, "THE LAST")
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 213, "WATCH")
    canvas.setFillColor(colors.Color(0.005, .018, .04, alpha=.78))
    canvas.rect(0, 22, PAGE_W, 64, fill=1, stroke=0)
    canvas.setFont(sans_bold, 12)
    canvas.setFillColor(colors.HexColor("#f1d4a0"))
    canvas.drawCentredString(PAGE_W/2, 56, "WRITTEN BY DIESEL  /  DPN NOVELS")
    canvas.restoreState()
    return True


def _cover_photo(canvas, path):
    im = ImageReader(str(path))
    w, h = im.getSize()
    scale = max(PAGE_W / w, PAGE_H / h)
    nw, nh = w*scale, h*scale
    canvas.drawImage(im, (PAGE_W-nw)/2, (PAGE_H-nh)/2,
                     width=nw, height=nh, mask="auto")


class CinematicPage(Flowable):
    """One full-page, bleed-to-trim dramatic scene image with caption panel."""

    def __init__(self, entry, sans_bold, sans_regular):
        super().__init__()
        self.entry = entry
        self.title_font = sans_bold
        self.caption_font = sans_regular
        self.width = PAGE_W
        self.height = PAGE_H - 1

    def draw(self):
        c = self.canv
        c.saveState()
        # A photo-page flowable is located at the exact 0,0 plate frame.
        im = ImageReader(str(self.entry["path"]))
        iw, ih = im.getSize()
        if iw / ih > .90:
            # Letterbox the *entire* wide scene over a soft full-bleed
            # photographic backdrop, rather than empty black bands.
            original = PILImage.open(self.entry["path"]).convert("RGB")
            backdrop = ImageOps.fit(
                original, (720, 1080), method=PILImage.Resampling.LANCZOS
            ).filter(ImageFilter.GaussianBlur(30))
            c.drawImage(ImageReader(backdrop), 0, 0,
                        width=PAGE_W, height=PAGE_H, mask="auto")
            c.setFillColor(colors.Color(.004, .013, .027, alpha=.52))
            c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
            scale = min(PAGE_W / iw, (PAGE_H - 112) / ih)
            dw, dh = iw * scale, ih * scale
            dx, dy = (PAGE_W - dw)/2, 105 + (PAGE_H - 112 - dh)/2
            c.drawImage(im, dx, dy, width=dw, height=dh, mask="auto")
            c.setStrokeColor(colors.HexColor("#af966f"))
            c.setLineWidth(.9)
            c.rect(dx+1, dy+1, dw-2, dh-2, fill=0, stroke=1)
        else:
            _cover_photo(c, self.entry["path"])
        c.setFillColor(colors.Color(.009, .02, .04, alpha=.78))
        c.rect(0, 0, PAGE_W, 105, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#b69970"))
        c.setLineWidth(1.2)
        c.line(40, 99, PAGE_W-40, 99)
        c.setFillColor(colors.HexColor("#f0e7dc"))
        c.setFont(self.title_font, 16)
        c.drawString(41, 72, self.entry["title"].upper())
        caption = self.entry["caption"]
        # Split long figure captions without leaking past the book's trim.
        words = caption.split()
        lines, line = [], ""
        for word in words:
            t = (line + " " + word).strip()
            if len(t) > 61:
                lines.append(line)
                line = word
            else:
                line = t
        if line: lines.append(line)
        c.setFont(self.caption_font, 8.3)
        c.setFillColor(colors.HexColor("#cedbe6"))
        for i, line in enumerate(lines[:2]):
            c.drawString(41, 51 - i*13, line)
        c.setFillColor(colors.HexColor("#c8a66b"))
        c.setFont(self.caption_font, 7.3)
        c.drawRightString(PAGE_W-40, 18, "THE LAST WATCH  •  DIESEL / DPN NOVELS")
        c.restoreState()
