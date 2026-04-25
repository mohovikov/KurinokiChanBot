import logging


class ANSIColors:
    PINK = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


LEVEL_COLORS = {
    logging.DEBUG: ANSIColors.BLUE,
    logging.INFO: ANSIColors.GREEN,
    logging.WARNING: ANSIColors.YELLOW,
    logging.ERROR: ANSIColors.RED,
    logging.CRITICAL: ANSIColors.PINK + ANSIColors.BOLD,
}


class ColoredFormatter(logging.Formatter):
    """Кастомный форматтер с ANSI-цветами."""

    def format(self, record):
        color = LEVEL_COLORS.get(record.levelno, ANSIColors.ENDC)
        record.levelname = f"{color}{record.levelname:8}{ANSIColors.ENDC}"

        record.name = f"{ANSIColors.PINK}{record.name}{ANSIColors.ENDC}"

        if record.levelno >= logging.WARNING:
            record.msg = f"{ANSIColors.BOLD}{record.msg}{ANSIColors.ENDC}"

        return super().format(record)
