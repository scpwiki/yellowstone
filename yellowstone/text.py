"""
Utility to manage text fields in the database.
"""

from Crypto.Hash import KangarooTwelve


def hash_text(contents: str) -> bytes:
    hash = KangarooTwelve.new()
    hash.update(contents.encode("utf-8"))
    return hash.read(16)


def add_text(contents: str, *, database) -> None:
    hash = hash_text(contents)
    database.add_text(hash=hash, contents=contents)
