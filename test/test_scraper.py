import re
import unittest
from datetime import datetime

from bs4 import Tag

from yellowstone.scraper import (
    extract_last_forum_post,
    find_element,
    get_entity_date,
    get_entity_user,
    get_entity_user_regular,
    get_user_slug,
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


class TestScraperBasics(unittest.TestCase):
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
    def get_entity(self, html) -> Tag:
        soup = make_soup(html)
        entity = next(soup.children)
        self.assertIsInstance(entity, Tag)
        return entity

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

        # Also test that get_entity_user_regular() returns the same thing
        # (though this function is not normally used directly)
        entity2 = entity.find("a")
        user2 = get_entity_user_regular(TEST_SOURCE, entity2)
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

    def test_guest_user(self):
        entity = self.get_entity(
            '<span class="printuser avatarhover">'
            '<a href="javascript:;">'
            '<img class="small" src="https://secure.gravatar.com/avatar.php?gravatar_id=b804142d40e0801797a7a7616c31d351&amp;default=https://www.wikidot.com/common--images/avatars/default/a16.png&amp;size=16" alt="">'
            "</a>"
            "Dr Thomas (guest)"
            "</span>"
        )

        user = get_entity_user(TEST_SOURCE, entity)
        self.assertIsInstance(user, CustomUserData)
        self.assertEqual(user.name, "Dr Thomas")

    def test_user_slug(self):
        entity = self.get_entity(
            '<a class="btn btn-primary" href="http://www.wikidot.com/user:info/aismallard">Profile page</a>',
        )

        slug = get_user_slug(TEST_SOURCE, entity)
        self.assertEqual(slug, "aismallard")

    def test_last_forum_post(self):
        entity = self.get_entity(
            '<tr><td class="name"><div class="title">'
            '<a href="/forum/c-1113520/sitewide-announcements">Sitewide Announcements</a>'
            "</div>"
            '<div class="description">Announcement of any sitewide changes or events. For usage by both staff and non-staff.</div>'
            "</td>"
            '<td class="threads">190</td>'
            '<td class="posts">6091</td>'
            '<td class="last">by <span class="printuser avatarhover">'
            '<a href="http://www.wikidot.com/user:info/heckker" onclick="WIKIDOT.page.listeners.userInfo(9050655); return false;">'
            '<img alt="Heckker" class="small" src="https://www.wikidot.com/avatar.php?userid=9050655&amp;amp;size=small&amp;amp;timestamp=1709807965" style="background-image:url(https://www.wikidot.com/userkarma.php?u=9050655)"/>'
            "</a>"
            '<a href="http://www.wikidot.com/user:info/heckker" onclick="WIKIDOT.page.listeners.userInfo(9050655); return false;">Heckker</a>'
            "</span><br/>"
            '<span class="odate time_1709691717 format_%28%25O%20ago%29">06 Mar 2024 02:21</span>'
            '<a href="/forum/t-16102888#post-6450010">Jump!</a>'
            "</td></tr>"
        )

        post = extract_last_forum_post(TEST_SOURCE, entity)
        self.assertIsNotNone(post)
        self.assertEqual(post.posted_time, datetime(2024, 3, 5, 21, 21, 57))
        self.assertEqual(post.thread_id, 16102888)
        self.assertEqual(post.post_id, 6450010)

        self.assertIsInstance(post.posted_user, UserModuleData)
        self.assertEqual(post.posted_user.name, "Heckker")
        self.assertEqual(post.posted_user.slug, "heckker")

    def test_last_forum_post_none(self):
        entity = self.get_entity(
            '<tr><td class="name"><div class="title">'
            '<a href="/forum/c-6188516/deleted-threads">Deleted threads</a>'
            "</div>"
            '<div class="description">Deleted forum discussions should go here.</div>'
            "</td>"
            '<td class="threads">0</td><td class="posts">0</td><td class="last">&nbsp;</td>'
            "</tr>"
        )

        post = extract_last_forum_post(TEST_SOURCE, entity)
        self.assertIsNone(post)
