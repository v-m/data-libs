import logging
from enum import IntEnum, Enum


class ColorCode(IntEnum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


class LevelColor(Enum):
    WARNING = ColorCode.YELLOW
    INFO = ColorCode.WHITE
    DEBUG = ColorCode.GREEN
    CRITICAL = ColorCode.MAGENTA
    ERROR = ColorCode.RED


# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


class LogLevelAbbreviation(Enum):
    DEBUG = "DBG"
    WARNING = "WRN"
    INFO = "INF"
    CRITICAL = "CRT"
    ERROR = "ERR"


class ColoredFormatter(logging.Formatter):
    def __init__(self, format):
        super().__init__(format)

    def format(self, record):
        levelname = record.levelname
        if levelname in LevelColor.__members__:
            levelname_color = (
                # Akhil and Daniele though using enums is a good idea
                COLOR_SEQ % (30 + LevelColor[levelname].value.value)
                + LogLevelAbbreviation[levelname].value
                + RESET_SEQ
            )
            record.colored_levelname = levelname_color
        return super().format(record)
