"""
Retrieve information corresponding to one user account.
"""

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from bs4 import Tag

from ..scraper import (
    ScrapingError,
    find_element,
    get_entity_date,
    make_soup,
    regex_extract,
)
from ..utils import chunks
from ..wikidot import Wikidot
from .common import get_user_slug

KARMA_LEVEL_STRIP_REGEX = re.compile(r"([\w ]+?) *\t.*?")
DATE_REGEX = re.compile(r"(\d+) (\w+) (\d+)")

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    id: int
    slug: str
    name: str
    created_at: datetime
    real_name: Optional[str]
    gender: Optional[str]
    birthday: Optional[date]
    location: Optional[str]
    website: Optional[str]
    bio: Optional[str]
    wikidot_pro: bool
    karma: Optional[int]


def get(user_id: int, *, wikidot: Wikidot) -> UserData:
    source = f"users/UserInfoWinModule ({user_id})"

    # Fetch from standard 'www' site to avoid dealing with localization issues
    html = wikidot.ajax_module_connector(
        "www",
        "users/UserInfoWinModule",
        {"user_id": user_id},
    )
    soup = make_soup(html)

    # Get name-like fields
    name = find_element(source, soup, "h1").text
    element = find_element(source, soup, "a.btn-primary")
    slug = get_user_slug(source, element)

    # Process user details
    created_at = None
    real_name = None
    gender = None
    birthday = None
    location = None
    website = None
    bio = None
    wikidot_pro = None
    karma = None

    rows = chunks(soup.find_all("td"), 2)
    for columns in rows:
        field, value, element = split_user_detail(columns)
        match field:
            case "Real name":
                real_name = value
            case "Gender":
                gender = value
            case "Birthday":
                # We can't use get_entity_date(), this is just a string
                #
                # We also can't use datetime.strptime, since year values
                # might be too small (e.g. 101).
                birthday = parse_date(source, value)
            case "From":
                location = value
            case "Website":
                website = value
            case "Wikidot.com User since:":
                element = find_element(source, element, "span.odate")
                created_at = get_entity_date(source, element)
            case "About":
                bio = value
            case "Account type":
                wikidot_pro = is_wikidot_pro(value)
            case "Karma level":
                karma = karma_level(value)

            # These are member fields, not user fields, ignore
            case "Member of this Site: since":  # sic
                pass
            case "Role in this Site":
                pass

            # Error case
            case _:
                raise ScrapingError(f"Unknown field in user details: {field!r}")

    # Field post-processing
    assert created_at is not None, "No user creation date found"

    if wikidot_pro is None:
        # Wikidot Pro provides a feature to hide your pro status.
        # So if there's no account type field, that ironically
        # indicates that the account must be Pro, so we can
        # just set it here ourselves.
        wikidot_pro = True

    # Build and return
    return UserData(
        id=user_id,
        slug=slug,
        name=name,
        created_at=created_at,
        real_name=real_name,
        gender=gender,
        birthday=birthday,
        location=location,
        website=website,
        bio=bio,
        wikidot_pro=wikidot_pro,
        karma=karma,
    )


def split_user_detail(columns: tuple[Tag, Tag]) -> tuple[str, str, Tag]:
    field, element = columns
    assert "active" in field.attrs["class"], "field lacks 'active' class"
    return field.text.strip(), element.text.strip(), element


def parse_month(value: str) -> int:
    match value:
        case "Jan":
            return 1
        case "Feb":
            return 2
        case "Mar":
            return 3
        case "Apr":
            return 4
        case "May":
            return 5
        case "Jun":
            return 6
        case "Jul":
            return 7
        case "Aug":
            return 8
        case "Sep":
            return 9
        case "Oct":
            return 10
        case "Nov":
            return 11
        case "Dec":
            return 12
        case _:
            raise ScrapingError(f"Unknown month value: {value!r}")


def parse_date(source: str, value: str) -> date:
    match = regex_extract(source, value, DATE_REGEX)
    year = int(match[3])
    month = parse_month(match[2])
    day = int(match[1])
    return date(year, month, day)


def is_wikidot_pro(value: str) -> bool:
    match value:
        case "free":
            return False
        case "Pro":
            return True
        case _:
            raise ScrapingError(f"Invalid value for account type: {value!r}")


def karma_level(value: str) -> int:
    # Strip out only the relevant level
    match = KARMA_LEVEL_STRIP_REGEX.match(value)
    assert match is not None, "No match for stripping out karma level data"
    value = match[1]

    # Return the equivalent integer value
    logger.debug("Extracting karma level from description '%s'", value)
    match value:
        case "none":
            return 0
        case "low":
            return 1
        case "medium":
            return 2
        case "high":
            return 3
        case "very high":
            return 4
        case "guru":
            return 5
        case _:
            raise ScrapingError(f"Invalid value for karma level: {value!r}")
