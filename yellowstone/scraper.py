"""
Utilities to assist with scraping.
"""

import logging
import re
from datetime import datetime
from typing import Optional, Reversible, Union

import requests
from bs4 import BeautifulSoup, PageElement, Tag

from .exception import ScrapingError
from .types import (
    AnonymousUserData,
    CustomUserData,
    DeletedUserData,
    ForumLastPostData,
    ForumPostUser,
    UserModuleData,
    assert_is_tag,
)

LAST_THREAD_AND_POST_ID = re.compile(r"/forum/t-(\d+)(?:/[^/]*)?#post-(\d+)")
TIMESTAMP_REGEX = re.compile(r"time_(\d+)")
USER_ID_REGEX = re.compile(r"WIKIDOT\.page\.listeners\.userInfo\((\d+)\).*")
USER_SLUG_REGEX = re.compile(r"https?://www\.wikidot\.com/user:info/([^/]+)")
USER_GUEST_REGEX = re.compile(r"\s*(.+?) \(.+\)\s*")
USER_IP_REGEX = re.compile(
    r"WIKIDOT\.page\.listeners\.anonymousUserInfo\('([^']+)'\).*",
)

logger = logging.getLogger(__name__)


def download_html(url: str) -> str:
    logging.debug("Downloading HTML from %s", url)
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def regex_extract(source: str, body: str, regex: re.Pattern) -> re.Match:
    logging.debug("Extracting pattern %s from %s", regex.pattern, source)
    match = regex.search(body)
    if match is None:
        raise ScrapingError(f"Pattern {regex.pattern} failed for {source}")

    return match


def regex_extract_str(source: str, body: str, regex: re.Pattern) -> str:
    match = regex_extract(source, body, regex)
    assert (
        len(match.groups()) == 1
    ), "Extracting single value from regex with multiple groups"
    string = match[1]
    assert isinstance(string, str), "Group 1 from regex is not a string"
    return string


def regex_extract_int(source: str, body: str, regex: re.Pattern) -> int:
    return int(regex_extract_str(source, body, regex))


def find_element(source: str, soup: Union[BeautifulSoup, Tag], *args, **kwargs) -> Tag:
    logging.debug("Finding %s %s from %s", args, kwargs, source)
    element = soup.find(*args, **kwargs)
    if element is None:
        raise ScrapingError(f"No '{args} {kwargs}' found for {source}")
    return assert_is_tag(element, "Element")


def select_element(source: str, soup: Union[BeautifulSoup, Tag], selector: str) -> Tag:
    logging.debug("Selecting %s from %s", selector, source)
    element = soup.select_one(selector)
    if element is None:
        raise ScrapingError(f"No '{selector} found for {source}")
    return assert_is_tag(element, "Element")


def get_entity_date(source: str, tag: Tag) -> datetime:
    """
    Parses out a date entity.

    Example:
    ```html
    <span class="odate time_1707320977 format_%25e%20%25b%20%25Y%2C%20%25H%3A%25M%7Cagohover">07 Feb 2024 15:49</span>
    ```
    """  # noqa: E501

    assert tag.name == "span", "HTML date entity is not span"
    for klass in tag.attrs["class"]:
        match = TIMESTAMP_REGEX.fullmatch(klass)
        if match is not None:
            return datetime.fromtimestamp(int(match[1]))

    raise ScrapingError(f"Could not find date timestamp from {source}")


def get_entity_user(source: str, tag: Tag) -> ForumPostUser:
    """
    Parses out a user module entity, including unusual cases.
    Requires being focused on .printuser

    It can output one of:
    * Regular user (current)
    * Deleted user (ID only)
    * Anonymous user (IP)
    * Created by Wikidot (for forum threads)
    """

    assert "printuser" in tag.attrs["class"], "HTML entity is not a .printuser"

    # If this has the "deleted" class, it's a deleted user
    if "deleted" in tag.attrs["class"]:
        return DeletedUserData(int(tag.attrs["data-id"]))

    # If there is a ".printuser a", it's either a regular user or a guest
    entity = tag.find("a")
    if entity is not None:
        assert isinstance(entity, Tag), ".printuser a is not an HTML entity"

        # Anonymous users have an IP address
        if "onclick" in entity.attrs:
            match = USER_IP_REGEX.fullmatch(entity.attrs["onclick"])
            if match is not None:
                ip = match[1]
                return AnonymousUserData(ip)

        # Guests don't have profile links
        if entity.attrs["href"] == "javascript:;":
            guest_name = regex_extract_str(source, tag.text.strip(), USER_GUEST_REGEX)
            return CustomUserData(guest_name)

        # Regular users
        return get_entity_user_regular(source, entity)

    # Created by Wikidot
    if tag.text.strip() == "Wikidot":
        return CustomUserData("wikidot")

    # Cannot figure out what this is, yield an error
    raise ScrapingError(f"Cannot determine user data from {source}")


def get_entity_user_regular(
    source: str,
    tag: Tag,
) -> UserModuleData:
    """
    Parses out a user module entity, when it is known to be "real" (e.g. not anonymous, deleted, etc).
    Requires being focused on the ".printuser a" element.

    Example
    ```html
    <a href="http://www.wikidot.com/user:info/aismallard" onclick="WIKIDOT.page.listeners.userInfo(4598089); return false;"><img alt="aismallard" class="small" src="https://www.wikidot.com/avatar.php?userid=4598089&amp;amp;size=small&amp;amp;timestamp=1707451824" style="background-image:url(https://www.wikidot.com/userkarma.php?u=4598089)"/></a>
    ```
    """  # noqa: E501

    assert tag.name == "a", "HTML user entity is not a"
    user_id = int(
        regex_extract(source, tag.attrs["onclick"], USER_ID_REGEX)[1],
    )
    user_slug = regex_extract(source, tag.attrs["href"], USER_SLUG_REGEX)[1]
    user_name = find_element(source, tag, "img", class_="small").attrs["alt"]
    return UserModuleData(
        id=user_id,
        slug=user_slug,
        name=user_name,
    )


def get_user_slug(source: str, element: Tag) -> str:
    href = element["href"]
    assert isinstance(href, str), "multiple href attributes found"
    match = regex_extract(source, href, USER_SLUG_REGEX)
    assert isinstance(match[1], str), "match group is not a string"
    return match[1]


def extract_last_forum_post(source: str, parent: Tag) -> Optional[ForumLastPostData]:
    source = f"{source} last-info"
    element = find_element(source, parent, class_="last")
    children = tuple(element.children)
    if all(isinstance(c, str) for c in children):
        # If there are no HTML element childrens,
        # there are no posts in this category,
        # which means there is no "last post" data.
        return None

    posted_user = get_entity_user(
        source,
        find_element(source, element, class_="printuser"),
    )
    posted_time = get_entity_date(
        source,
        find_element(source, element, "span", class_="odate"),
    )
    element_link = _get_last_anchor(source, children)

    assert isinstance(element_link, Tag), "Last child in last_info is not an element"
    match = regex_extract(source, element_link.attrs["href"], LAST_THREAD_AND_POST_ID)
    thread_id = int(match[1])
    post_id = int(match[2])

    return ForumLastPostData(
        posted_time=posted_time,
        posted_user=posted_user,
        thread_id=thread_id,
        post_id=post_id,
    )


def _get_last_anchor(source: str, children: Reversible[PageElement]) -> Tag:
    for child in reversed(children):
        if isinstance(child, Tag) and child.name == "a" and "href" in child.attrs:
            return child

    raise ScrapingError(f"No 'a.href' in {source}")
