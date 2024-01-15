"""
Retrieve information corresponding to one user account.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

from bs4 import Tag

from ..scraper import (
    ScrapingError,
    make_soup,
    regex_extract,
    find_element,
    get_entity_date,
)
from ..utils import chunks
from ..wikidot import Wikidot

KARMA_LEVEL_STRIP_REGEX = re.compile(r"([\w ]+?) *\t.*?")
USER_SLUG_REGEX = re.compile(r"https?://www\.wikidot\.com/user:info/([^/]+)")

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
    karma: int


def get(user_id: int, *, wikidot: Wikidot) -> UserData:
    logger.info("Retrieving user data for %d", user_id)
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
                birthday = datetime.strptime(value, "%d %b %Y").date()
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

    # Assert unconditional details
    assert created_at is not None, "No user creation date found"
    assert wikidot_pro is not None, "No account type found"
    assert karma is not None, "No karma found"

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


def get_user_slug(source: str, element: Tag) -> str:
    href = element["href"]
    assert isinstance(href, str), "multiple href attributes found"
    match = regex_extract(source, href, USER_SLUG_REGEX)
    assert isinstance(match[1], str), "match group is not a string"
    return match[1]


def split_user_detail(columns: tuple[Tag, Tag]) -> tuple[str, str, Tag]:
    field, element = columns
    assert "active" in field.attrs["class"], "field lacks 'active' class"
    return field.text.strip(), element.text.strip(), element


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
