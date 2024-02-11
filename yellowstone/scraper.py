"""
Utilities to assist with scraping.
"""

import logging
import re
from datetime import datetime
from typing import Union

import requests
from bs4 import BeautifulSoup, Tag

from .exception import ScrapingError
from .request.common import USER_ID_REGEX, USER_SLUG_REGEX, UserModuleData

TIMESTAMP_REGEX = re.compile(r"time_(\d+)")

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


def find_element(source: str, soup: Union[BeautifulSoup, Tag], selector: str) -> Tag:
    logging.debug("Selecting %s from %s", selector, source)
    element = soup.select_one(selector)
    if element is None:
        raise ScrapingError(f"No '{selector}' found for {source}")

    return element


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


def get_entity_user(source: str, tag: Tag) -> UserModuleData:
    """
    Parses out a user module entity.

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
    user_name = find_element(source, tag, "img.small").attrs["alt"]
    return UserModuleData(
        id=user_id,
        slug=user_slug,
        name=user_name,
    )
