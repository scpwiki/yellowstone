"""
Scrape site and page data from the home page of a site.
"""

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from bs import BeautifulSoup

from ..scraper import download_html, find_element, make_soup, regex_extract
from ..wikidot import Wikidot

if TYPE_CHECKING:
    pass

LANGUAGE_REGEX = re.compile(r"WIKIREQUEST\.info\.lang = '([^']+)';")
SITE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.siteId = (\d+);")
SITE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.siteUnixName = "([^"]+)";')
PAGE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.pageId = (\d+);")
PAGE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.pageUnixName = "([^"]+)";')
PAGE_CATEGORY_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.categoryId = (\d+);")
FORUM_POST_ID_REGEX = re.compile(r"/forum/t-(\d+)/.*")

logger = logging.getLogger(__name__)


@dataclass
class SiteHomeData:
    slug: str
    id: int
    name: str
    tagline: str
    language: str
    home_page_slug: str
    home_page_id: int
    home_page_discussion_thread_id: Optional[int]
    home_page_category_id: int


def get(site_slug: str, *, wikidot: Wikidot) -> SiteHomeData:
    logger.info("Retrieving site home page for %s", site_slug)

    source = url = wikidot.site_url(site_slug)
    html = download_html(url)

    language = regex_extract(url, html, LANGUAGE_REGEX)[1]
    site_id = int(regex_extract(url, html, SITE_ID_REGEX)[1])
    site_slug_ex = regex_extract(url, html, SITE_SLUG_REGEX)[1]
    page_id = int(regex_extract(url, html, PAGE_ID_REGEX)[1])
    page_slug = regex_extract(url, html, PAGE_SLUG_REGEX)[1]
    page_category_id = int(regex_extract(url, html, PAGE_CATEGORY_ID_REGEX)[1])
    assert site_slug == site_slug_ex, "site slug in scraped page doesn't match"

    soup = make_soup(html)
    name, tagline = get_site_titles(source, soup)
    discussion_thread_id = get_discussion_thread_id(source, soup)

    return SiteHomeData(
        slug=site_slug,
        id=site_id,
        name=name,
        tagline=tagline,
        language=language,
        home_page_slug=page_slug,
        home_page_id=page_id,
        home_page_discussion_thread_id=discussion_thread_id,
        home_page_category_id=page_category_id,
    )


def get_site_titles(source: str, soup: BeautifulSoup) -> tuple[str, str]:
    logger.debug("Extracting page title and subtitle from %s", source)
    header = find_element(source, soup, "div#header")
    name = find_element(source, header, "h1 span").text
    tagline = find_element(source, header, "h2 span").text
    return name, tagline


def get_discussion_thread_id(source: str, soup: BeautifulSoup) -> Optional[int]:
    logger.debug("Extracting discussion thread ID (if any) from %s", source)
    element = find_element(source, soup, "a#discuss-button")
    assert isinstance(element["href"], str), "element href is not a string"
    match = FORUM_POST_ID_REGEX.fullmatch(element["href"])
    if match is None:
        return None
    else:
        return int(match[1])
