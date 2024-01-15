"""
Retrieve groups of site members by page.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime

from bs4 import Tag

from ..scraper import find_element, get_entity_date, make_soup, regex_extract
from ..wikidot import Wikidot
from .user import get_user_slug

USER_ID_REGEX = re.compile(r"WIKIDOT\.page\.listeners\.userInfo\((\d+)\).*")

logger = logging.getLogger(__name__)


@dataclass
class SiteMemberData:
    name: str
    slug: str
    id: int
    joined_at: datetime


def get(site_slug: str, offset: int, *, wikidot: Wikidot) -> list[SiteMemberData]:
    logger.info("Retrieving site member data for %s (offset %d)", site_slug, offset)

    assert offset > 0, "Offset cannot be zero or negative"
    html = wikidot.ajax_module_connector(
        site_slug,
        "membership/MembersListModule",
        {
            "page": offset,
            "group": "",
            "order": "",
        },
    )
    soup = make_soup(html)
    rows = soup.find_all("tr")
    return list(map(process_row, rows))


def process_row(row: Tag) -> SiteMemberData:
    source = str(row)

    # Extract user information
    element = row.find_all("a")[1]
    name = element.text
    slug = get_user_slug(source, element)
    id = int(regex_extract(source, element["onclick"], USER_ID_REGEX)[1])

    # Extract membership join date
    element = find_element(source, row, "span.odate")
    joined_at = get_entity_date(source, element.attrs["class"])

    return SiteMemberData(
        name=name,
        slug=slug,
        id=id,
        joined_at=joined_at,
    )
