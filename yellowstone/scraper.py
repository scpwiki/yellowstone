"""
Utilities to assist with scraping.
"""

import re

import requests

from .exceptions import ScrapingError


def download_html(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def regex_extract(source: str, body: str, regex: re.Pattern) -> re.Match:
    match = regex.search(body)
    if match is None:
        raise ScrapingError(f"Pattern {regex.pattern} failed for {source}")

    return match
