###
# File:   src\logic\ui\window.py
# Date:   2025-01-27 / 13:07
# Author: alexrjs
###


# imports
from flet import Page, Colors
from db import registry
from enum import Enum, auto


# constants
class WindowState(Enum):
    Initial = auto()
    Changed = auto()
    Saved = auto()


# variables


# functions/classes
def updateWindowTitle(page:Page, title:str=None) -> None:
    if not page:
        return
    
    registry.ui.noteTitle.value = f"Notes: {'*' if registry.dirty else ''}{title if title else ''}"
    page.update()


def updateWindowState(page: Page, changed: WindowState=WindowState.Initial) -> None:
    if not page:
        return
    
    match changed:
        case WindowState.Changed:
            registry.ui.noteTitle.color = Colors.AMBER
            registry.ui.menubar.style.bgcolor = Colors.RED_700
            registry.ui.dragBar.bgcolor = Colors.RED_700
            registry.changed = True
            registry.dirty = True
        case WindowState.Saved:
            registry.ui.noteTitle.color = Colors.BLACK
            registry.ui.menubar.style.bgcolor = Colors.GREEN_700
            registry.ui.dragBar.bgcolor = Colors.GREEN_700
            registry.changed = False
            registry.dirty = False
        case _:
            registry.ui.noteTitle.color = Colors.BLACK
            registry.ui.menubar.style.bgcolor = Colors.BLUE_700
            registry.ui.dragBar.bgcolor = Colors.BLUE_700
            registry.changed = False
            registry.dirty = False
    
    page.update()