import colorama
import termcolor as tcolor
import logging
import sys
from . import option


log_level = option.log_level
LOG_LEVEL = option.LOG_LEVEL


def check_log_level() -> int | None:
    if log_level == LOG_LEVEL[0]:  # debug
        return logging.DEBUG
    elif log_level == LOG_LEVEL[1]:  # info
        return logging.INFO
    elif log_level == LOG_LEVEL[2]:  # warning
        return logging.WARNING
    elif log_level == LOG_LEVEL[3]:  # error
        return logging.ERROR


colorama.just_fix_windows_console()
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=check_log_level(), format="%(message)s")


def info_log(msg: str):
    level = tcolor.colored("Info:", "blue", attrs=["bold"])
    msg = tcolor.colored(msg, "light_blue", attrs=["bold"])
    logging.info(f"{level} {msg}")


def debug_log(msg: str):
    level = "Debug:"
    logging.debug(f"{level} {msg}")


def warning_log(msg: str):
    level = tcolor.colored("Warning:", "yellow", attrs=["bold"])
    msg = tcolor.colored(msg, "light_yellow", attrs=["bold"])
    logging.warning(f"{level} {msg}")


def error_log(msg: str):
    level = tcolor.colored("Error:", "red", attrs=["bold"])
    msg = tcolor.colored(msg, "light_red", attrs=["bold"])
    logging.error(f"{level} {msg}")
    sys.exit(1)
