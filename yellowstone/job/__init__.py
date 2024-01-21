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


class JobManager:
    __slots__ = ("database",)

    def __init__(self, database):
        self.database = database

    def add_raw(self, type: JobType, data: Json) -> None:
        self.database.add_job(
            job_type=type.value,
            data=json.dumps(data),
        )

    def index_site_pages(self, data: None) -> None:
        self.add_raw(JobType.INDEX_SITE_PAGES, data)

    def index_site_forums(self, data: None) -> None:
        self.add_raw(JobType.INDEX_SITE_FORUMS, data)

    def index_site_members(self, data: SiteMemberJob) -> None:
        self.add_raw(JobType.INDEX_SITE_MEMBERS, cast(Json, data))

    def fetch_user(self, data: GetUserJob) -> None:
        self.add_raw(JobType.FETCH_USER, cast(Json, data))

    def fetch_user_avatar(self, data: GetUserAvatarJob) -> None:
        self.add_raw(JobType.FETCH_USER_AVATAR, cast(Json, data))

    def process_job(self):
        # TODO
        ...
