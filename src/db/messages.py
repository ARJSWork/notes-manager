###
# File:   src\db\messages.py
# Date:   2025-02-18 / 07:19
# Author: alexrjs
###


# imports
import logging


# constants
_CODEMAPPING = {
    "A": "Notes",
    "U": "UI",
    "F": "File"
}


# variables


# functions/classes
def getError(code_: str) -> str:
    """Return a error message"""

    _code = f"Error {code_[1:]} ({_CODEMAPPING[code_[0]]}):"
    match code_:
        case "U000":
            return f"{_code} Unknown error!"

        case "U001":
            return f"{_code} Page not found or set!"
        
        case "U002":
            return f"{_code} Control not found or set!"
        
        case "U003":
            return f"{_code} Content not found or set!"
        
        case "A000":
            return f"{_code} Unknown error!"
        
        case "A001":
            return f"{_code} Panel not found!"

        case "A002":
            return f"{_code} Attached data is empty!"

        case _:
            return f"{_code} Unknown error!"
        

def getWarning(code_: str) -> str:
    """Return a warning message"""

    match code_:
        case "001":
            return "Warning 001: File not found"
        
        case _:
            return "Warning: Unknown warning"
        

def getInfo(code_: str) -> str:
    """Return a info message"""

    match code_:
        case "001":
            return "Info 001: File saved"
        
        case _:
            return "Info: Unknown info"

def getDebug(code_: str) -> str:
    """Return a debug message"""

    match code_:
        case "001":
            return "Debug 001: File not found"
        
        case _:
            return "Debug: Unknown debug"

def handleError(code_: str, data_: str) -> bool:
    """Handle a error"""

    try:
        assert data_, getError(code_)
    except Exception as _e:
        logging.error(f"Error not found - {code_}: {data_}")
        return False

    return True