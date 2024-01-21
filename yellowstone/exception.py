"""
Defines exceptions used by the service.
"""


class JobFailed(RuntimeError):
    pass


class ScrapingError(RuntimeError):
    pass


class UnknownJobError(RuntimeError):
    pass


class WikidotError(RuntimeError):
    pass


class WikidotTokenError(WikidotError):
    pass
