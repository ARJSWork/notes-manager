###
# File:   src\logic\ui\__init__.py
# Date:   2025-02-05 / 10:32
# Author: alexrjs
###


# imports
from enum import Enum


# constants
class NoteItems(Enum):
    ITEM_TYPE_MEETINGS : str = "meetings"
    ITEM_TYPE_TEMPLATES : str = "templates"
    ITEM_TYPE_MODULES : str = "modules"
    ITEM_TYPE_TEXT : str = "text"

class NoteActions(Enum):
    ACTION_RENAME : str = "Rename"
    ACTION_ADD_TEMPLATE : str = "AddTemplate"
    ACTION_ADD_MODULE : str = "AddModule"
    ACTION_ADD_MEETING : str = "AddMeeting"


class NoteState(Enum):
    ADDTEMPLATE : str = "addTemplate"
    ADDMODULE : str = "addModule"
    ADDMEETING : str = "addMeeting"
    RENAMED : str = "renamed"
    SELECTED : str = "selected"
    RENDERED : str = "rendered"


class ContentAction(Enum):
    Ok : str = "ok"
    Cancel : str = "cancel"
    Copy : str = "copy"
    Delete : str = "delete"
    DoDelete : str = "doDelete"
    Rename : str = "rename"
    Edit : str = "edit"
    RenderToClipboard : str = "renderToClipboard"
    RenderToPreview : str = "renderToPreview"
    RenderToFile : str = "renderToFile"


# variables


# functions/classes
