"""
Date: 2024-01-27
Author: alexrjs
Description: Some default variables and methods for the app
Licence: Unlicense
"""

from os.path import commonprefix
import logging
from types import SimpleNamespace
from traceback import extract_stack
#from utils.client import showStatusMsg


# constants
REPORTLEVEL = SimpleNamespace()
REPORTLEVEL.EXCEPTION = "Exception"
REPORTLEVEL.ERROR = "Error"
REPORTLEVEL.WARNING = "Warning"
REPORTLEVEL.INFO = "Info"
REPORTLEVEL.DEBUG = "Debug"
REPORTLEVELS = [
    REPORTLEVEL.EXCEPTION,
    REPORTLEVEL.ERROR,
    REPORTLEVEL.WARNING,
    REPORTLEVEL.INFO,
    REPORTLEVEL.DEBUG,
]


# variables
reportLevel = REPORTLEVEL.WARNING
reportRegistry = {
    REPORTLEVEL.EXCEPTION: [],
    REPORTLEVEL.ERROR: [],
    REPORTLEVEL.WARNING: [],
    REPORTLEVEL.INFO: [],
    REPORTLEVEL.DEBUG: [],
}


# variables
__prefix__ = __file__


# functions
def setReportLevel(level_: str) -> None:
    """Set the report level."""

    global reportLevel
    reportLevel = level_ if level_ in REPORTLEVELS else REPORTLEVEL.WARNING


def showStatusMsg(message_: str) -> None:
    """Prints a message to the console."""
    logging.info(message_)


def removeCommonPrefix(str1:str=__prefix__, str2:str=None) -> str:
    """Removes the common prefix from a string."""
    _common_prefix = commonprefix([str1, str2])

    # Find the last '/' in the common prefix
    _last_slash_index = _common_prefix.rfind("/")

    if _last_slash_index != -1:
        _common_prefix = _common_prefix[: _last_slash_index + 1]

    result2 = str2[len(_common_prefix) :].lstrip("/")
    return result2.replace("/", ".").replace(".py", "")


def report(message_:str="", type_:str="Info", return_:object=False) -> object:
    """Prints a message to the console and returns a boolean value."""
    _caller = extract_stack()[-2]
    match type_:
        case REPORTLEVEL.EXCEPTION, REPORTLEVEL.ERROR:
            showStatusMsg(f"[{type_}] - {removeCommonPrefix(str2=_caller.filename)}.{_caller.name}.{_caller.lineno}: {message_}")
        case REPORTLEVEL.WARNING:
            showStatusMsg(f"[{type_}] - {_caller.name}: {message_}")
        case _:
            showStatusMsg(f"[{type_}]: {message_}")

    return return_


def error(message_: str = "", report_:object=False) -> object:
    """Prints an error message to the console and returns a boolean value."""
    return report(message_, REPORTLEVEL.ERROR, report_)


def exception(message_: str = "", report_:object=False) -> object:
    """Prints an exception message to the console and returns a boolean value."""
    return report(message_, REPORTLEVEL.EXCEPTION, report_)


def warning(message_: str = "", report_:object=False) -> object:
    """Prints a warning message to the console and returns a boolean value."""
    return report(message_, REPORTLEVEL.WARNING, report_)


def info(message_: str = "", report_:object=False) -> object:
    """Prints an info message to the console and returns a boolean value."""
    return report(message_, REPORTLEVEL.INFO, report_)
