"""Regression: decorative DPN UI must never be spoken in PDF/audiobook text."""
from io import BytesIO
from types import SimpleNamespace
import re
import sys
import unittest
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfgen import canvas as reportlab_canvas

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_book import PAGE_W, PAGE_H, draw_body


class NarrationSafeThemeTests(unittest.TestCase):
    def test_binary_rain_and_running_furniture_are_visual_only(self):
        buffer = BytesIO()
        page = reportlab_canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))
        draw_body(page, SimpleNamespace(page=17))
        page.setFont("Helvetica", 11)
        page.drawString(65, 350, "The convoy crossed the northern sea.")
        page.showPage()
        page.save()

        reader = PdfReader(BytesIO(buffer.getvalue()))
        words = reader.pages[0].extract_text() or ""
        self.assertIn("The convoy crossed the northern sea.", words)
        self.assertNotIn("DIESEL", words)
        self.assertNotIn("THE LAST WATCH", words)
        self.assertNotRegex(words, r"(?:\b[01]\b[\s\r\n]*){8,}")
        self.assertNotIn("\n16\n", words)
        # The DPN design remains present; decorative labels are raster images.
        self.assertGreaterEqual(len(reader.pages[0].images), 1)


if __name__ == "__main__":
    unittest.main()
