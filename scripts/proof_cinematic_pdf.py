#!/usr/bin/env python3
"""Verify real embedded artwork in the full-length novel and render visual PDF proofs.

Unlike checking source files or counting pages, this compares the JPEG bytes
extracted from the *built PDF* with the checksum-verified committed artwork.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "books" / "The_Last_Watch_Extended_Edition.pdf"
EDITION = ROOT / "books" / "The_Last_Watch_Cinematic_Illustrated_2026-10-24.pdf"
PROOFS = ROOT / "books" / "proofs"
MANIFEST = ROOT / "artwork" / "cinematic" / "committed_manifest.json"
REQUIRED_REPLACEMENTS = {
    "00_northstar_cover.jpg",
    "16_cutlass_crippled_bridge.jpg",
    "17_aurora_child_and_nurse.jpg",
    "18_memorial_watch.jpg",
    "19_ramirez_watchbook.jpg",
    "20_liv_and_vale_remembrance.jpg",
}

def font(size: int, bold: bool = False):
    name = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(name, size)

def main() -> None:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["assets"]
    expected_hashes = {}
    for entry in entries:
        asset = ROOT / entry.get("source_path", "artwork/cinematic/" + entry["file"])
        data = asset.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        assert sha == entry["sha256"], f"Source art checksum failed: {entry['file']}"
        assert sha not in expected_hashes, f"Duplicate image pixels for {entry['file']}"
        expected_hashes[sha] = entry
    assert REQUIRED_REPLACEMENTS.issubset({e["file"] for e in entries})

    PROOFS.mkdir(parents=True, exist_ok=True)
    pdf = fitz.open(SOURCE)
    assert pdf.page_count >= 455
    present = {}
    photographic_pages = []
    for page_index in range(pdf.page_count):
        page = pdf[page_index]
        matched = []
        for img in page.get_images(full=True):
            try:
                payload = pdf.extract_image(img[0])["image"]
            except ValueError:
                continue
            sha = hashlib.sha256(payload).hexdigest()
            if sha in expected_hashes:
                entry = expected_hashes[sha]
                present[entry["file"]] = page_index + 1
                matched.append(entry)
        if matched:
            assert len(matched) == 1, f"Multiple cinematic plates on PDF page {page_index + 1}"
            photographic_pages.append((page_index, matched[0]))
    assert len(present) == len(entries), f"Expected {len(entries)} distinct image files in the PDF, found {len(present)}: {set(e['file'] for e in entries)-set(present)}"
    assert photographic_pages[0][0] == 0, "The cinematic cover is not PDF page 1"
    assert len(photographic_pages) == len(entries), "Scene plate omitted or duplicated"
    assert entries[0].get("prelettered"), "New pre-lettered cover not activated"

    # Proof images come from rendering the actual PDF, not from the source JPEGs.
    cover_pix = pdf[0].get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
    cover_pix.pil_image().convert("RGB").save(PROOFS / "New_Cinematic_Cover_Proof.jpg", quality=93)

    w, h, columns = 320, 488, 3
    rows = (len(photographic_pages) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * (w + 22) + 22, rows * (h + 84) + 72), (15, 22, 34))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 18), "THE LAST WATCH  |  CINEMATIC PDF PAGE PROOF", fill=(237, 230, 216), font=font(24, True))
    for i, (page_index, entry) in enumerate(photographic_pages):
        page = pdf[page_index]
        img = page.get_pixmap(matrix=fitz.Matrix(1.05, 1.05), alpha=False).pil_image().convert("RGB")
        thumb = ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS)
        x = 22 + (i % columns) * (w + 22)
        y = 62 + (i // columns) * (h + 84)
        sheet.paste(thumb, (x, y))
        draw.rectangle((x - 1, y - 1, x + w + 1, y + h + 1), outline=(172, 144, 95), width=2)
        draw.text((x, y + h + 9), f"PDF page {page_index + 1}  |  {entry['title'][:25]}", fill=(246, 241, 230), font=font(13, True))
        draw.text((x, y + h + 33), entry["file"][:36], fill=(178, 194, 207), font=font(11))
    sheet.save(PROOFS / "Cinematic_Art_Contact_Sheet.jpg", quality=89, optimize=True)
    (PROOFS / "Cinematic_Pages.json").write_text(
        json.dumps({"source_pdf": SOURCE.name, "total_pages": pdf.page_count,
                    "verified_image_pages": len(present), "placements":
                    [{"file": entry["file"], "title": entry["title"], "pdf_page": present[entry["file"]]}
                     for entry in entries]}, indent=2) + "\n", encoding="utf-8"
    )
    pdf.close()
    shutil.copyfile(SOURCE, EDITION)
    assert EDITION.stat().st_size > 1_000_000
    print(f"Verified {len(entries)} actual embedded cinematic artworks in {EDITION.name}, including all 6 requested new images.")
    print("Front cover visually rendered to books/proofs/New_Cinematic_Cover_Proof.jpg")
    print("Every image page rendered to books/proofs/Cinematic_Art_Contact_Sheet.jpg")

if __name__ == "__main__":
    main()
