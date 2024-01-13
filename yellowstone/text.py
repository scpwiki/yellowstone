"""
Utility to manage text fields in the database.
"""

import logging

from Crypto.Hash import KangarooTwelve

logger = logging.getLogger(__name__)


def hash_text(contents: str) -> bytes:
    hash = KangarooTwelve.new()
    hash.update(contents.encode("utf-8"))
    return hash.read(16)


def add_text(contents: str, *, database) -> None:
    logging.debug("Adding text entry (length %d) to database", len(contents))
    hash = hash_text(contents)
    database.add_text(hash=hash, contents=contents)
