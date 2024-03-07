import re
import unittest

from yellowstone.scraper import regex_extract


class TestScraper(unittest.TestCase):
    def test_regex_extract(self):
        regex = re.compile(r"SCP-(\d+)(?:-(\w+))?")

        match = regex_extract("test", "SCP-1000", regex)
        self.assertEqual(match[1], "1000")
        self.assertEqual(match[2], None)

        match = regex_extract("test", "SCP-371-J", regex)
        self.assertEqual(match[1], "371")
        self.assertEqual(match[2], "J")


if __name__ == "__main__":
    unittest.main()
