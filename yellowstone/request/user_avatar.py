"""
Download a user's avatar.
"""

import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


def get(user_id: int) -> bytes:
    # We include the timestamp to blend in with regular requests
    r = requests.get(
        "https://www.wikidot.com/avatar.php",
        params={
            "userid": user_id,
            "timestamp": int(datetime.now().timestamp()),
        },
    )
    r.raise_for_status()
    return r.content
