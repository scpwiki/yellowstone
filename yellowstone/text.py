# TODO demo of text hashing

from Crypto.Hash import KangarooTwelve


def hash_text(value: str) -> bytes:
    h = KangarooTwelve.new()
    h.update(value.encode("utf-8"))
    return h.read(16)
