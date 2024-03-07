import re
import unittest

from yellowstone.scraper import (
    find_element,
    make_soup,
    regex_extract,
    regex_extract_int,
    regex_extract_str,
    select_element,
)

from .helpers import TEST_SOURCE


class TestScraper(unittest.TestCase):
    def test_regex_extract(self):
        regex = re.compile(r"SCP-(\d+)(?:-(\w+))?")

        match = regex_extract(TEST_SOURCE, "SCP-1000", regex)
        self.assertEqual(match[1], "1000")
        self.assertEqual(match[2], None)

        match = regex_extract(TEST_SOURCE, "SCP-371-J", regex)
        self.assertEqual(match[1], "371")
        self.assertEqual(match[2], "J")

    def test_regex_extract_str(self):
        regex = re.compile(r"name_(\w+)")
        result = regex_extract_str(TEST_SOURCE, "name_j12pmu", regex)
        self.assertEqual(result, "j12pmu")

    def test_regex_extract_int(self):
        regex = re.compile(r"id_(\d+)")
        result = regex_extract_int(TEST_SOURCE, "id_9406112", regex)
        self.assertEqual(result, 9406112)

    def test_find_element(self):
        soup = make_soup(
            '<div class="wrap">'
            '<span id="date" style="color: blue">2023-01-07</span>'
            "</div>"
        )

        element = find_element(TEST_SOURCE, soup, "div", class_="wrap")
        self.assertEqual(element.name, "div")
        self.assertEqual(element.attrs, {"class": ["wrap"]})

        element = find_element(TEST_SOURCE, soup, id="date")
        self.assertEqual(element.name, "span")
        self.assertEqual(element.attrs, {"id": "date", "style": "color: blue"})

    def test_select_element(self):
        soup = make_soup(
            '<ol class="list">' "<li>ONE</li> <li>TWO</li> <li>THREE</li>" "</ol>"
        )

        element = select_element(TEST_SOURCE, soup, "ol.list li:nth-child(2)")
        self.assertEqual(element.name, "li")
        self.assertEqual(element.text, "TWO")
