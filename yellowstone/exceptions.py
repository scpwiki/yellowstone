"""
Defines exceptions used by the service.
"""


class ScrapingError(RuntimeError):
    pass


class UnknownJobError(RuntimeError):
    pass


class WikidotError(RuntimeError):
    pass


class WikidotTokenError(WikidotError):
    pass
