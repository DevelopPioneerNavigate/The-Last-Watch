"""Cinematic artwork regression tests for the DPN Novels illustrated book."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cinematic_art import ART, ARCHIVE, MANIFEST, activate_cinematic_art, scene_plate
from build_book import read_manuscript


class CinematicArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.manuscript = read_manuscript()[0]

    def test_scene_anchors_exist(self):
        entries = self.manifest["assets"]
        self.assertGreaterEqual(len(entries), 10)
        self.assertEqual(len(entries), len({p["file"] for p in entries}))
        self.assertEqual(sum(e["anchor"] == "cover" for e in entries), 1)
        for item in entries:
            with self.subTest(art=item["file"]):
                self.assertEqual(len(item["sha256"]), 64)
                if item["anchor"] == "cover":
                    continue
                self.assertIn(item["anchor"].upper().replace("'", " "), self.manuscript.upper().replace("'", " "))

    def test_trigger_mapping(self):
        entries = self.manifest["assets"]
        for item in entries:
            if item["anchor"] == "cover":
                continue
            found = scene_plate(entries, "**" + item["anchor"] + " — TEST TIME**")
            self.assertEqual(found["file"], item["file"])

    def test_full_bleed_pages_render_in_both_aspects(self):
        """Exercise the actual page flowable before original ZIP upload."""
        import tempfile
        from PIL import Image as PILImage
        from pypdf import PdfReader
        from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
        from cinematic_art import CinematicPage

        with tempfile.TemporaryDirectory() as scratch:
            for width, height in ((480, 720), (720, 480)):
                image_path = Path(scratch) / f"sample-{width}.jpg"
                PILImage.new("RGB", (width, height), (25, 65, 90)).save(image_path, "JPEG")
                pdf_path = Path(scratch) / f"proof-{width}.pdf"
                doc = BaseDocTemplate(str(pdf_path), pagesize=(432, 648))
                frame = Frame(0, 0, 432, 648, leftPadding=0, rightPadding=0,
                              topPadding=0, bottomPadding=0)
                doc.addPageTemplates([PageTemplate(id="Photo", frames=[frame])])
                entry = {"path": image_path, "title": "The Atlantic Watch",
                         "caption": "Photo composition test, no layout cropping or overflow"}
                doc.build([CinematicPage(entry, "Helvetica-Bold", "Helvetica")])
                pdf = PdfReader(str(pdf_path))
                self.assertEqual(len(pdf.pages), 1)
                self.assertGreaterEqual(len(pdf.pages[0].images), 1)

    def test_committed_cinematic_book_edition(self):
        # Shipping assets are individually committed; the optional ZIP
        # manifest is an alternate distribution format, not the source.
        direct = ART / "committed_manifest.json"
        edition = json.loads(direct.read_text(encoding="utf-8"))
        items = edition["assets"]
        self.assertEqual(len(items), 15)
        self.assertEqual(sum(e["anchor"] == "cover" for e in items), 1)
        self.assertEqual(len(items), len({e["anchor"] for e in items}))
        expected = {
            "THE LIEUTENANT'S BRIDGE", "BENEATH AURORA",
            "LETTERS NEVER SENT", "THE WATCHKEEPERS",
            "RAVEN ONE'S EMPTY SEAT", "THE GREEN ROOF"
        }
        self.assertTrue(expected.issubset({e["anchor"] for e in items}))
        import hashlib
        from PIL import Image as PILImage
        for item in items:
            with self.subTest(anchor=item["anchor"]):
                filename = item["file"]
                target = ROOT / item.get("source_path", "artwork/cinematic/" + filename)
                self.assertTrue(target.is_file())
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), item["sha256"])
                if item["anchor"] != "cover":
                    self.assertIn(item["anchor"].upper().replace("'", " "), self.manuscript.upper().replace("'", " "))
                    self.assertEqual(scene_plate(items, "**" + item["anchor"] + " — SCENE**")["file"], filename)
                if filename.startswith(("16_", "17_", "18_", "19_", "20_")):
                    with PILImage.open(target) as im:
                        self.assertGreaterEqual(im.width, 1024)
                        self.assertGreaterEqual(im.height, 1536)

    def test_no_partial_archive(self):
        # Prefer the original ZIP when available; verified individual JPEGs
        # are a complete and reproducible alternative, never a silent fallback
        # to unillustrated pages after cinematic assets have been committed.
        direct = ART / "committed_manifest.json"
        verified = activate_cinematic_art()
        if ARCHIVE.is_file():
            self.assertEqual(len(verified), len(self.manifest["assets"]))
        elif direct.is_file():
            self.assertGreaterEqual(len(verified), 9)
            self.assertEqual(sum(item["anchor"] == "cover" for item in verified), 1)
            self.assertEqual(len(verified), len({item["anchor"] for item in verified}))
        else:
            self.assertEqual(verified, [])
        for item in verified:
            self.assertTrue(item["path"].is_file())


if __name__ == "__main__":
    unittest.main()
