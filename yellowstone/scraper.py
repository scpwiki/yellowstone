"""
Utilities to assist with scraping.
"""

import logging
import re
from typing import Union

import requests
from bs4 import BeautifulSoup, Tag

from .exceptions import ScrapingError

logger = logging.getLogger(__name__)


def download_html(url: str) -> str:
    logging.debug("Downloading HTML from %s", url)
    r = requests.get(url)
    r.raise_for_status()
    return r.text


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
