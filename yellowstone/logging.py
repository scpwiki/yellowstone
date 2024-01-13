"""
Set up logging for the service.
"""

import logging
import sys

LOG_FILE = f"{__package__}.log"
LOG_FILE_MODE = "w"
LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
LOG_FILE_FORMAT = f"%(asctime)s {LOG_FORMAT}"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"


def set_up_logging():
    file_handler = logging.FileHandler(LOG_FILE, mode=LOG_FILE_MODE, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter(LOG_FILE_FORMAT, datefmt=LOG_DATE_FORMAT),
    )

    logger = logging.getLogger(__package__)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    logger.info("Starting the Yellowstone Wikidot backup service...")
