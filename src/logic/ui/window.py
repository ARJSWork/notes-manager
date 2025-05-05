###
# File:   src\logic\ui\ui.py
# Date:   2025-01-27 / 13:07
# Author: alexrjs
###


# imports
from flet import Page, Colors
from db import registry


# constants


# variables


# functions/classes
def updateWindowTitle(page:Page, title:str=None) -> None:
    if not page:
        return
    
    # if not title:
    #     return
    
    registry.ui.projectTitle.value = f"Project: {title if title else ''}"
    page.update()


def updateWindowState(page: Page, changed: bool=False) -> None:
    if not page:
        return
    
    if changed:
        registry.ui.projectTitle.color = Colors.AMBER
        registry.ui.menubar.style.bgcolor = Colors.RED_600
        registry.ui.dragBar.bgcolor = Colors.RED_600

    else:
        registry.ui.projectTitle.color = Colors.BLACK
        registry.ui.menubar.style.bgcolor = Colors.GREEN_700
        registry.ui.dragBar.bgcolor = Colors.GREEN_700

    page.update()