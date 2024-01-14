"""
Retrieve site members by page.
"""

import re
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup, Tag

from ..exceptions import ScrapingError
from ..scraper import find_element, regex_extract

USER_SLUG_REGEX = re.compile(r"https?://www\.wikidot\.com/user:info/([^/]+)")
USER_ID_REGEX = re.compile(r"WIKIDOT\.page\.listeners\.userInfo\((\d+)\).*")
TIMESTAMP_REGEX = re.compile(r"time_(\d+)")


@dataclass
class SiteMemberData:
    name: str
    slug: str
    id: int
    joined_at: datetime


def get(site_slug: str, offset: int) -> list[SiteMemberData]:
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


def get_join_date(source: str, classes: list[str]) -> datetime:
    for klass in classes:
        match = TIMESTAMP_REGEX.fullmatch(klass)
        if match is not None:
            return datetime.fromtimestamp(int(match[1]))

    raise ScrapingError(f"Could not find date timestamp from {source}")
