"""
Set up logging for the service.
"""

import logging
import sys

LOG_FILE = f"{__package__}.log"
LOG_FILE_MODE = "w"
LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"


def set_up_logging():
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(LOG_FILE, mode=LOG_FILE_MODE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(__package__)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)
    logger.info("Starting the Yellowstone Wikidot backup service...")
