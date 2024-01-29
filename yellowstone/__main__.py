"""
Entrypoint for the Yellowstone Wikidot backup service.
"""

from dotenv import load_dotenv

from .config import Config
from .core import BackupDispatcher
from .logging import set_up_logging

if __name__ == "__main__":
    set_up_logging()
    load_dotenv()
    config = Config.parse_args()
    core = BackupDispatcher(config)
    core.run()
