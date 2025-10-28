###
# File:   src\ui\bars\status.py
# Date:   2025-02-03 / 09:16
# Author: alexrjs
###


# imports
from flet import Row, Text, Container, Ref, MainAxisAlignment, CrossAxisAlignment, Colors, TextAlign
from db import register, registry
import logging


# constants


# variables


# functions/classes
def build(**kwargs) -> Row:
    """Status bar at the bottom of the page"""

    _page = registry.page
    if not _page:
        logging.error("Error. No page registered")
        return None

    register("ui.status", Ref[Text]())
    _text = Text(
        "Loading...", 
        size=16, 
        text_align=TextAlign.START,
        color=Colors.WHITE,
        ref=registry.ui.status,
    )

    _container = Container(
        expand=True,
        padding=3,
        margin=0,
        bgcolor=Colors.GREY_800, 
        content=_text,
    )

    _row = Row(
        [
            _container,
        ], 
        height=30, 
        alignment=MainAxisAlignment.START,
        vertical_alignment=CrossAxisAlignment.CENTER,
        run_spacing=0,
    )

    return _row

def updateStatus(text: str) -> None:
    """Update the status bar text"""
    
    registry.ui.status.current.value = text
    registry.ui.status.current.update()
