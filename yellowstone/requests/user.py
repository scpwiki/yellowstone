"""
Retrieve information corresponding to one user account.
"""

import logging
import re
from dataclasses import dataclass

from bs4 import Tag

from ..scraper import ScrapingError, make_soup, regex_extract, find_element, get_entity_date
from ..wikidot import Wikidot

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    pass


def get(user_id: int, *, wikidot: Wikidot) -> UserData:
    logger.info("Retrieving user data for %d", user_id)

    # Fetch from standard 'www' site to avoid dealing with localization issues
    source = f"users/UserInfoWinModule ({user_id})"
    html = wikidot.ajax_module_connector("www",
                                  "users/UserInfoWinModule",
                                  { "user_id": user_id })
    soup = make_soup(html)

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

    rows = soup.find_all("tr")
    for row in rows:
        field, value, element = split_user_detail(row)
        match field:
            case "Real name":
                real_name = element.text
            case "Gender":
                gender = element.text
            case "Birthday":
                birthday = get_entity_date(source, element)
            case "From":
                location = element.text
            case "Website":
                website = element.text
            case "Wikidot.com User since:":
                created_at = get_entity_date(source, element)
            case "About":
                bio = element.text
            case "Account type":
                wikidot_pro = account_type(element.text)
            case "Karma level":
                karma = karma_level(element.text)
            # These are member fields, not user fields, ignore
            case "Member of this Site: since":  # sic
                pass
            case "Role in this Site":
                pass
            # Error case
            case _:
                raise ScrapingError(f"Unknown field in user details: {field!r}")


def split_user_detail(row: Tag) -> tuple[str, str, Tag]:
    field, element = row.find_all("td")
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
