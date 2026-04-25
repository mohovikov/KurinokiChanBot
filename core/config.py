import logging
import os
import sys
from dotenv import load_dotenv, find_dotenv

from core.constants import ColoredFormatter, ANSIColors

load_dotenv(find_dotenv())

DEBUG = os.getenv("DEBUG", False) in (True, "True")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")


def setup_logging():
    base_level = logging.DEBUG if DEBUG else logging.INFO
    FORMAT = f"{ANSIColors.GREEN}%(asctime)s{ANSIColors.ENDC} | %(levelname)s | %(name)s | %(message)s"
    DATE_FORMAT = "%Y/%m/%d – %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(FORMAT, datefmt=DATE_FORMAT))

    logging.basicConfig(level=base_level, handlers=[handler])

    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.getLogger("aiogram.dispatcher").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    if DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
