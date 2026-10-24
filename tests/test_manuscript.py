"""Tests for narrative structure and scene inclusion."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_book import read_manuscript


class NovelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.words, cls.chapters, cls.scenes = read_manuscript()

    def test_full_manuscript_present(self):
        self.assertEqual(self.chapters, 13)
        self.assertEqual(self.scenes, 52)
        self.assertGreater(self.words, 68000)
        self.assertNotIn("{{scene:", self.raw)
        self.assertIn("THE END", self.raw)

    def test_structure(self):
        self.assertEqual(len(re.findall(r"(?m)^# PROLOGUE", self.raw)), 1)
        self.assertEqual(len(re.findall(r"(?m)^# EPILOGUE", self.raw)), 1)
        self.assertEqual(len(re.findall(r"(?m)^# CHAPTER", self.raw)), 13)

    def test_scene_placement(self):
        placements = [
            ("THE PEOPLE WE HAD PROMISED", "THE FIRST CROSSING"),
            ("THE FIRST CROSSING", "THE TANKER\u0027S CAPTAIN"),
            ("THE TANKER\u0027S CAPTAIN", "WHAT THE ORDERS DID NOT SAY"),
            ("WHAT THE ORDERS DID NOT SAY", "THE SHIP THAT BREATHES"),
            ("THE SHIP THAT BREATHES", "THE SILENT QUARTER"),
            ("THE SILENT QUARTER", "# CHAPTER TWO"),
            ("A FAINT LINE IN THE NOISE", "THE DARK WATER BETWEEN"),
            ("THE DARK WATER BETWEEN", "THE AIRCRAFT IN THE DARK"),
            ("THE AIRCRAFT IN THE DARK", "# CHAPTER THREE"),
            ("THE DISTANCE BETWEEN SHIPS", "THE LAST MANIFEST"),
            ("THE LAST MANIFEST", "THE HOUR BEFORE SUNRISE"),
            ("THE HOUR BEFORE SUNRISE", "# CHAPTER FOUR"),
            ("THE PICTURE IS NOT THE SEA", "BENEATH AURORA"),
            ("BENEATH AURORA", "# CHAPTER FIVE"),
            ("THE COST OF KEEPING COURSE", "THE FISHERMAN\u0027S CHOICE"),
            ("THE FISHERMAN\u0027S CHOICE", "# CHAPTER SIX"),
            ("THE VOICE FROM HAWTHORNE", "THE FISHERMAN\u0027S CHOICE"),
            ("THE NAME ON THE METAL", "THE INVISIBLE FRONT"),
            ("THE UNWRITTEN MAP", "BEFORE THE SECOND SALVO"),
            ("THE INVISIBLE FRONT", "BEFORE THE SECOND SALVO"),
            ("BEFORE THE SECOND SALVO", "# CHAPTER SEVEN"),
            ("THE TWELVE TRACKS", "WHEN CUTLASS WENT DARK"),
            ("WHEN CUTLASS WENT DARK", "THE LIEUTENANT\u0027S BRIDGE"),
            ("THE LIEUTENANT\u0027S BRIDGE", "THE SHIPS THAT ANSWERED"),
            ("THE SHIPS THAT ANSWERED", "# CHAPTER EIGHT"),
            ("THE SPACE BEFORE FIRE", "THE SHIP WE COULD NOT SEE"),
            ("THE SHIP WE COULD NOT SEE", "# CHAPTER NINE"),
            ("THE BOUNDARIES HOLD", "# CHAPTER TEN"),
            ("THE PEOPLE WHO WERE NOT ON THE SCREEN", "A SPACE FOR THE LIVING"),
            ("A SPACE FOR THE LIVING", "THE WEIGHT OF WATER"),
            ("THE WEIGHT OF WATER", "# CHAPTER ELEVEN"),
            ("THE WEATHER HAS NO ALLIES", "THE COLD HOURS"),
            ("THE COLD HOURS", "THE DARK BETWEEN THE ALARMS"),
            ("THE DARK BETWEEN THE ALARMS", "# CHAPTER TWELVE"),
            ("THE FREIGHTER AT THE EDGE", "THE MORNING WITHOUT SIGNALS"),
            ("THE MORNING WITHOUT SIGNALS", "RAVEN ONE\u0027S EMPTY SEAT"),
            ("RAVEN ONE\u0027S EMPTY SEAT", "VOICES FROM THE WEST"),
            ("THE MORNING WITHOUT SIGNALS", "VOICES FROM THE WEST"),
            ("VOICES FROM THE WEST", "THE CORRIDOR OF LIGHTS"),
            ("THE CORRIDOR OF LIGHTS", "# CHAPTER THIRTEEN"),
            ("THE PIER AT REYKJAVÍK", "THE CAPTAINS WITHOUT SHIPS"),
            ("THE CAPTAINS WITHOUT SHIPS", "LETTERS NEVER SENT"),
            ("LETTERS NEVER SENT", "WHERE THE CARGO WENT"),
            ("WHERE THE CARGO WENT", "THE CONVOY AFTER OURS"),
            ("THE CONVOY AFTER OURS", "THE DISTANCE HOME"),
            ("THE DISTANCE HOME", "THE FIRST LEDGER"),
            ("THE CONVOY AFTER OURS", "THE FIRST LEDGER"),
            ("LETTERS NEVER SENT", "THE FIRST LEDGER"),
            ("THE FIRST LEDGER", "# EPILOGUE"),
            ("LETTERS NEVER SENT", "# EPILOGUE"),
            ("THE HEARING ROOM", "THE ELEVENTH SURVIVOR"),
            ("THE ELEVENTH SURVIVOR", "THE VISITOR FROM CUTLASS"),
            ("THE VISITOR FROM CUTLASS", "THE BOOK OF NAMES"),
            ("THE BOOK OF NAMES", "THE VOICES AT HOME"),
            ("THE VOICES AT HOME", "WHAT ETHAN CHOSE"),
        ]
        for earlier, later in placements:
            with self.subTest(earlier=earlier):
                self.assertIn(earlier, self.raw)
                self.assertIn(later, self.raw)
                self.assertLess(self.raw.index(earlier), self.raw.index(later))

    def test_character_continuity(self):
        self.assertNotIn("daughter became an engineer", self.raw)
        self.assertNotIn("Rios went on to make chief", self.raw)
        for key in ("Chief Ramirez", "Caledonia", "Raven One", "Captain Lindholm", "Commander Mara Chen"):
            self.assertIn(key, self.raw)


if __name__ == "__main__":
    unittest.main()
