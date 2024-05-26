import unittest
from typing import Generator

from ovos_skill_pyradios import PyradiosSkill

MEDIA_KEYS = ["match_confidence", "media_type", "uri", "playback", "image",
              "bg_image", "skill_icon", "title", "artist", "author", "length"]


class TestSkill(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.skill = PyradiosSkill()
    
    def test_search(self):
        stations = self.skill.search_pyradios("radio NPR", None)
        self.assertTrue(isinstance(stations, Generator))
        station = next(stations)
        self.assertTrue(all([k in station for k in MEDIA_KEYS]))
        self.assertTrue(station["media_type"].name == "RADIO")
        self.assertTrue(station["playback"].name == "AUDIO")


if __name__ == "__main__":
    unittest.main()
