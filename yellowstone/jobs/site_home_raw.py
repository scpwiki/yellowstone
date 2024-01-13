"""
Scrape site and page data from the home page of a site.
"""

import re
from dataclasses import dataclass

from ..utils import download_html, regex_extract

DOMAIN_REGEX = re.compile(r'WIKIREQUEST\.info\.domain = "([^"]+)";')
LANGUAGE_REGEX = re.compile(r"WIKIREQUEST\.info\.lang = '([^']+)';")
SITE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.siteId = (\d+);")
SITE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.siteUnixName = "([^"]+)";')
PAGE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.pageId = (\d+);")
PAGE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.pageUnixName = "([^"]+)";')


@dataclass
class SiteHomeRaw:
    domain: str
    language: str
    site_slug: str
    site_id: int
    home_page_slug: str
    home_page_id: int


def fetch(*, site_slug: str) -> SiteHomeRaw:
    url = f"https://{site_slug}.wikidot.com/"
    html = download_html(url)
    domain = regex_extract(url, html, DOMAIN_REGEX)[1]
    language = regex_extract(url, html, LANGUAGE_REGEX)[1]
    site_id = int(regex_extract(url, html, SITE_ID_REGEX)[1])
    site_slug_ex = regex_extract(url, html, SITE_SLUG_REGEX)[1]
    page_id = int(regex_extract(url, html, PAGE_ID_REGEX)[1])
    page_slug = regex_extract(url, html, PAGE_SLUG_REGEX)[1]
    assert site_slug == site_slug_ex, "site slug in scraped page doesn't match"
    return SiteHomeRaw(
        domain=domain,
        language=language,
        site_id=site_id,
        site_slug=site_slug,
        home_page_id=page_id,
        home_page_slug=page_slug,
    )
