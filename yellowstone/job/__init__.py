"""
Contains all jobs which can be invoked by the service.

This refers to high-level operations which retrieve some
usable chunk of information from various sources within
Wikidot. For instance, a combination of an XMLRPC API call
and scraping.
"""

import json
from enum import Enum, unique
from typing import cast

from ..types import Json
from .get_user import GetUserJob
from .get_user_avatar import GetUserAvatarJob
from .index_site_members import SiteMemberJob


@unique
class JobType(Enum):
    INDEX_SITE_PAGES = "index-site-pages"
    INDEX_SITE_FORUMS = "index-site-forums"
    INDEX_SITE_MEMBERS = "index-site-members"
    FETCH_USER = "fetch-user"
    FETCH_USER_AVATAR = "fetch-user-avatar"


# TODO change to JobManager class?


def add_raw_job(database, type: JobType, data: Json) -> None:
    database.add_job(
        job_type=type.value,
        data=json.dumps(data),
    )


def add_index_site_pages_job(database, data: None) -> None:
    add_raw_job(database, JobType.INDEX_SITE_PAGES, data)


def add_index_site_forums_job(database, data: None) -> None:
    add_raw_job(database, JobType.INDEX_SITE_FORUMS, data)


def add_index_site_members_job(database, data: SiteMemberJob) -> None:
    add_raw_job(database, JobType.INDEX_SITE_MEMBERS, cast(Json, data))


def add_fetch_user_job(database, data: GetUserJob) -> None:
    add_raw_job(database, JobType.FETCH_USER, cast(Json, data))


def add_fetch_user_avatar_job(database, data: GetUserAvatarJob) -> None:
    add_raw_job(database, JobType.FETCH_USER_AVATAR, cast(Json, data))
