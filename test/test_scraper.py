from datetime import datetime
import re
import unittest

from yellowstone.scraper import (
    find_element,
    make_soup,
    regex_extract,
    regex_extract_int,
    regex_extract_str,
    select_element,
    get_entity_date,
    get_entity_user,
)

from .helpers import TEST_SOURCE

# This test file has a lot of HTML string constants.
# I split them for readability but some are still too long for the linter.
# flake8: noqa: E501


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


class TestEntity(unittest.TestCase):
    def test_date(self):
        soup = make_soup(
            '<span class="odate time_1707320977 format_%25e%20%25b%20%25Y%2C%20%25H%3A%25M%7Cagohover">'
            "07 Feb 2024 15:49</span>"
        )

        entity = soup.find("span", class_="odate")
        timestamp = get_entity_date(TEST_SOURCE, entity)
        self.assertEqual(timestamp, datetime(2024, 2, 7, 10, 49, 37))


    def test_regular_user(self):
        soup = make_soup(
            '<span class="printuser avatarhover">'
            '<a href="http://www.wikidot.com/user:info/aismallard" '
            'onclick="WIKIDOT.page.listeners.userInfo(4598089); return false;">'
            '<img alt="aismallard" class="small" '
            'src="https://www.wikidot.com/avatar.php?userid=4598089&amp;amp;size=small&amp;amp;timestamp=1707451824" '
            'style="background-image:url(https://www.wikidot.com/userkarma.php?u=4598089)"/>'
            "</a>"
            "</span>"
        )

        entity = soup.find("span", class_="printuser")
        user = get_entity_user(TEST_SOURCE, entity)
        self.assertEqual(user.id, 4598089)
        self.assertEqual(user.slug, "aismallard")
        self.assertEqual(user.name, "aismallard")
