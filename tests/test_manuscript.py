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
        self.assertEqual(self.scenes, 19)
        self.assertGreater(self.words, 25000)
        self.assertNotIn("{{scene:", self.raw)
        self.assertIn("THE END", self.raw)

    def test_structure(self):
        self.assertEqual(len(re.findall(r"(?m)^# PROLOGUE", self.raw)), 1)
        self.assertEqual(len(re.findall(r"(?m)^# EPILOGUE", self.raw)), 1)
        self.assertEqual(len(re.findall(r"(?m)^# CHAPTER", self.raw)), 13)

    def test_scene_placement(self):
        placements = [
            ("THE PEOPLE WE HAD PROMISED", "THE SHIP THAT BREATHES"),
            ("THE SHIP THAT BREATHES", "# CHAPTER TWO"),
            ("A FAINT LINE IN THE NOISE", "THE AIRCRAFT IN THE DARK"),
            ("THE AIRCRAFT IN THE DARK", "# CHAPTER THREE"),
            ("THE DISTANCE BETWEEN SHIPS", "THE LAST MANIFEST"),
            ("THE LAST MANIFEST", "# CHAPTER FOUR"),
            ("THE PICTURE IS NOT THE SEA", "# CHAPTER FIVE"),
            ("THE COST OF KEEPING COURSE", "# CHAPTER SIX"),
            ("THE INVISIBLE FRONT", "# CHAPTER SEVEN"),
            ("WHEN CUTLASS WENT DARK", "# CHAPTER EIGHT"),
            ("THE SPACE BEFORE FIRE", "# CHAPTER NINE"),
            ("THE BOUNDARIES HOLD", "# CHAPTER TEN"),
            ("THE PEOPLE WHO WERE NOT ON THE SCREEN", "# CHAPTER ELEVEN"),
            ("THE WEATHER HAS NO ALLIES", "THE DARK BETWEEN THE ALARMS"),
            ("THE DARK BETWEEN THE ALARMS", "# CHAPTER TWELVE"),
            ("VOICES FROM THE WEST", "# CHAPTER THIRTEEN"),
            ("LETTERS NEVER SENT", "# EPILOGUE"),
            ("THE HEARING ROOM", "THE VOICES AT HOME"),
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
