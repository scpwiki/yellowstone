"""
Retrieve site members by page.
"""

import re
from dataclasses import dataclass
from datetime import datetime

from bs4 import Tag

from ..exceptions import ScrapingError
from ..scraper import find_element, make_soup, regex_extract
from ..wikidot import Wikidot

USER_SLUG_REGEX = re.compile(r"https?://www\.wikidot\.com/user:info/([^/]+)")
USER_ID_REGEX = re.compile(r"WIKIDOT\.page\.listeners\.userInfo\((\d+)\).*")


@dataclass
class SiteMemberData:
    name: str
    slug: str
    id: int
    joined_at: datetime


def get(site_slug: str, offset: int) -> list[SiteMemberData]:
    logger.info("Retrieving site member data for %s (offset %d)", site_slug, offset)

    assert offset > 0, "Offset cannot be zero or negative"
    html = core.wikidot.ajax_module_connector(
        site_slug,
        "membership/MembersListModule",
        {
            "page": str(offset),
            "group": "",
            "order": "",
        },
    )
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    return list(map(process_row, rows))


def process_row(row: Tag) -> MemberInfo:
    source = str(row)

    # Extract user information
    element = row.find_all("a")[1]
    name = element.text
    slug = regex_extract(source, element["href"], USER_SLUG_REGEX)[1]
    id = int(regex_extract(source, element["onclick"], USER_ID_REGEX)[1])

    # Extract membership join date
    element = find_element(source, row, "span.odate")
    joined_at = get_join_date(source, element.attrs["class"])

    return SiteMemberData(
        name=name,
        slug=slug,
        id=id,
        joined_at=joined_at,
    )
