###
# File:   src\ui\dialogs\preview.py
# Date:   2025-05-06 / 09:18
# Author: alexrjs
###


# imports
from flet import(
    TextField, ElevatedButton, Row, Text, AlertDialog
)
from db import registry
from db.messages import getError


# constants


# variables


# functions/classes

def show(text_: str = None, id_: str = None) -> None:
    """Shows a preview dialog."""

    # Check prerequisits
    assert text_, getError("A000")

    def _copy_and_close(e):
        e.page.set_clipboard(text_)
        e.page.close(_dlg)

    _dlg = AlertDialog(
        title=Text(f"Preview Meeting"),
        content=TextField(
            text_,
            multiline=True,
            min_lines=1,
            max_lines=400,
            read_only=True,
            autofocus=False,
            width=800,
            expand=True,
        ),
        actions=[
            ElevatedButton("Copy & Close", key=id_, on_click=_copy_and_close),
            ElevatedButton("Close", key=id_, on_click=lambda e: e.page.close(_dlg)),
        ],
        actions_alignment="end",
    )
    registry.page.open(_dlg)
