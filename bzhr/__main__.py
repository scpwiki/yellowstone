"""
Entrypoint for the BZHR Wikidot backup service.
"""

import asyncio

from dotenv import load_dotenv

from .config import Config
from .core import BackupDispatcher

if __name__ == "__main__":
    load_dotenv()
    config = Config.parse_args()
    dispatch = BackupDispatcher(config)
    asyncio.run(dispatch.main_loop())
