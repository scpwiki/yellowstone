import re
import unittest
from datetime import datetime

from bs4 import Tag

from yellowstone.scraper import (
    find_element,
    get_entity_date,
    get_entity_user,
    get_entity_user_exists,
    make_soup,
    regex_extract,
    regex_extract_int,
    regex_extract_str,
    select_element,
)
from yellowstone.types import (
    AnonymousUserData,
    CustomUserData,
    DeletedUserData,
    UserModuleData,
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
        entity = self.get_entity(
            '<span class="printuser avatarhover">'
            '<a href="http://www.wikidot.com/user:info/aismallard" '
            'onclick="WIKIDOT.page.listeners.userInfo(4598089); return false;">'
            '<img alt="aismallard" class="small" '
            'src="https://www.wikidot.com/avatar.php?userid=4598089&amp;amp;size=small&amp;amp;timestamp=1707451824" '
            'style="background-image:url(https://www.wikidot.com/userkarma.php?u=4598089)"/>'
            "</a>"
            "</span>"
        )

        user = get_entity_user(TEST_SOURCE, entity)
        self.assertIsInstance(user, UserModuleData)
        self.assertEqual(user.id, 4598089)
        self.assertEqual(user.slug, "aismallard")
        self.assertEqual(user.name, "aismallard")

        # Also test that get_entity_user_exists() returns the same thing
        # (though this function is not normally used directly)
        entity2 = entity.find("a")
        user2 = get_entity_user_exists(TEST_SOURCE, entity2)
        self.assertEqual(user, user2)

    def test_deleted_user(self):
        entity = self.get_entity(
            '<span class="printuser deleted" data-id="2826145">'
            '<img class="small" src="https://www.wikidot.com/common--images/avatars/default/a16.png" alt="">'
            "(account deleted)"
            "</span>"
        )

        user = get_entity_user(TEST_SOURCE, entity)
        self.assertIsInstance(user, DeletedUserData)
        self.assertEqual(user.id, 2826145)

    def test_anonymous_user(self):
        entity = self.get_entity(
            '<span class="printuser anonymous">'
            """<a href="javascript:;" onclick="WIKIDOT.page.listeners.anonymousUserInfo('185.220.101.20'); return false;">"""
            '<img class="small" src="http://www.wikidot.com/common--images/avatars/default/a16.png" alt="">'
            "</a>"
            """<a href="javascript:;" onclick="WIKIDOT.page.listeners.anonymousUserInfo('185.220.101.20'); return false;">"""
            "Anonymous "
            '<span class="ip">(185.220.101.x)</span>'
            "</a>"
            "</span>"
        )

        user = get_entity_user(TEST_SOURCE, entity)
        self.assertIsInstance(user, AnonymousUserData)
        self.assertEqual(user.ip, "185.220.101.20")

    def test_wikidot_user(self):
        entity = self.get_entity('<span class="printuser">Wikidot</span>')
        user = get_entity_user(TEST_SOURCE, entity)
        self.assertIsInstance(user, CustomUserData)
        self.assertTrue(user.is_system)

    def get_entity(self, html) -> Tag:
        soup = make_soup(html)
        entity = soup.find("span", class_="printuser")
        self.assertIsInstance(entity, Tag)
        return entity
