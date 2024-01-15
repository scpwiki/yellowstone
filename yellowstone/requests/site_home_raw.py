"""
Scrape site and page data from the home page of a site.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from ..scraper import download_html, find_element, regex_extract, make_soup

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
    site_slug: str
    site_id: int
    site_language: str
    home_page_slug: str
    home_page_id: int
    home_page_discussion_thread_id: Optional[int]
    home_page_category_id: int


def get(site_slug: str) -> SiteHomeData:
    logger.info("Retrieving site home page for %s", site_slug)

    url = f"https://{site_slug}.wikidot.com/"
    html = download_html(url)

    language = regex_extract(url, html, LANGUAGE_REGEX)[1]
    site_id = int(regex_extract(url, html, SITE_ID_REGEX)[1])
    site_slug_ex = regex_extract(url, html, SITE_SLUG_REGEX)[1]
    page_id = int(regex_extract(url, html, PAGE_ID_REGEX)[1])
    page_slug = regex_extract(url, html, PAGE_SLUG_REGEX)[1]
    page_category_id = int(regex_extract(url, html, PAGE_CATEGORY_ID_REGEX)[1])
    assert site_slug == site_slug_ex, "site slug in scraped page doesn't match"

    soup = make_soup(html)
    element = find_element(url, soup, "a#discuss-button")
    assert isinstance(element["href"], str), "element href is not a string"
    match = FORUM_POST_ID_REGEX.fullmatch(element["href"])
    if match is None:
        discussion_thread_id = None
    else:
        discussion_thread_id = int(match[1])

    return SiteHomeData(
        site_slug=site_slug,
        site_id=site_id,
        site_language=language,
        home_page_slug=page_slug,
        home_page_id=page_id,
        home_page_discussion_thread_id=discussion_thread_id,
        home_page_category_id=page_category_id,
    )
