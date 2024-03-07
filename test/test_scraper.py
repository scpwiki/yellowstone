import re
import unittest

from yellowstone.scraper import regex_extract, regex_extract_str, regex_extract_int


class TestScraper(unittest.TestCase):
    def test_regex_extract(self):
        regex = re.compile(r"SCP-(\d+)(?:-(\w+))?")

        match = regex_extract("test", "SCP-1000", regex)
        self.assertEqual(match[1], "1000")
        self.assertEqual(match[2], None)

        match = regex_extract("test", "SCP-371-J", regex)
        self.assertEqual(match[1], "371")
        self.assertEqual(match[2], "J")

    def test_regex_extract_str(self):
        regex = re.compile(r"name_(\w+)")
        result = regex_extract_str("test", "name_j12pmu", regex)
        self.assertEqual(result, "j12pmu")

    def test_regex_extract_int(self):
        regex = re.compile(r"id_(\d+)")
        result = regex_extract_int("test", "id_9406112", regex)
        self.assertEqual(result, 9406112)
