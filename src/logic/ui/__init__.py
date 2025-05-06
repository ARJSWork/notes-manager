###
# File:   src\logic\ui\__init__.py
# Date:   2025-02-05 / 10:32
# Author: alexrjs
###


# imports
from enum import Enum


# constants
ITEM_TYPE_MEETINGS : str = "meetings"
ITEM_TYPE_TEMPLATES : str = "templates"
ITEM_TYPE_MODULES : str = "modules"
ITEM_TYPE_TEXT : str = "text"


class ProjectState(Enum):
    ADDTEMPLATE = "addTemplate"
    ADDMODULE = "addModule"
    ADDMEETING = "addAgenda"
    RENAMED = "renamed"
    SELECTED = "selected"
    RENDERED = "rendered"


class ContentAction(Enum):
    Ok = "ok"
    Cancel = "cancel"
    Copy = "copy"
    Delete = "delete"
    DoDelete = "doDelete"
    Edit = "edit"
    RenderToClipboard = "renderToClipboard"
    RenderToPreview = "renderToPreview"
    RenderToFile = "renderToFile"


# variables


# functions/classes
