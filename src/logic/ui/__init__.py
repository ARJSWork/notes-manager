###
# File:   src\logic\ui\__init__.py
# Date:   2025-02-05 / 10:32
# Author: alexrjs
###


# imports
from enum import Enum


# constants
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
