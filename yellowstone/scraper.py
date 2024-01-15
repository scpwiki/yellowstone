"""
Utilities to assist with scraping.
"""

import logging
import re
from datetime import datetime
from typing import Union

import requests
from bs4 import BeautifulSoup, Tag

from .exceptions import ScrapingError

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
        raise ScrapingError(f"No {selector} found for {source}")

    return element


def get_entity_date(source: str, tag: Tag) -> datetime:
    assert tag.name == "span", "HTML date entity is not span"
    for klass in tag.attrs["class"]:
        match = TIMESTAMP_REGEX.fullmatch(klass)
        if match is not None:
            return datetime.fromtimestamp(int(match[1]))

    raise ScrapingError(f"Could not find date timestamp from {source}")
