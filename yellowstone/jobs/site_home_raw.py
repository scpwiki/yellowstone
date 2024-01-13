"""
Scrape site and page data from the home page of a site.
"""

import re

from bs4 import BeautifulSoup

from ..scraper import download_html, regex_extract

LANGUAGE_REGEX = re.compile(r"WIKIREQUEST\.info\.lang = '([^']+)';")
SITE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.siteId = (\d+);")
SITE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.siteUnixName = "([^"]+)";')
PAGE_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.pageId = (\d+);")
PAGE_SLUG_REGEX = re.compile(r'WIKIREQUEST\.info\.pageUnixName = "([^"]+)";')
PAGE_CATEGORY_ID_REGEX = re.compile(r"WIKIREQUEST\.info\.categoryId = (\d+);")
FORUM_POST_ID_REGEX = re.compile(r"/forum/t-(\d+)/.*")


def fetch(*, database, site_slug: str) -> None:
    url = f"https://{site_slug}.wikidot.com/"
    html = download_html(url)

    language = regex_extract(url, html, LANGUAGE_REGEX)[1]
    site_id = int(regex_extract(url, html, SITE_ID_REGEX)[1])
    site_slug_ex = regex_extract(url, html, SITE_SLUG_REGEX)[1]
    page_id = int(regex_extract(url, html, PAGE_ID_REGEX)[1])
    page_slug = regex_extract(url, html, PAGE_SLUG_REGEX)[1]
    page_category_id = int(regex_extract(url, html, PAGE_CATEGORY_ID_REGEX)[1])
    assert site_slug == site_slug_ex, "site slug in scraped page doesn't match"

    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one("a#discuss-button")
    match = FORUM_POST_ID_REGEX.fullmatch(element["href"])
    if match is None:
        discussion_thread_id = None
    else:
        discussion_thread_id = int(match[1])

    database.add_site(
        site_slug=site_slug,
        wikidot_id=site_id,
        home_slug=page_slug,
        language=language,
    )
    database.add_page(
        site_slug=site_slug,
        page_slug=page_slug,
        page_id=page_id,
        page_category_id=page_category_id,
        discussion_thread_id=discussion_thread_id,
        discussion_thread_fetched=True,
    )
