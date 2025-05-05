###
# File:   src\ui\dialogs\project.py
# Date:   2025-02-06 / 10:26
# Author: alexrjs
###


# imports
from os import path
from flet import Page, Text, ElevatedButton, AlertDialog, TextField, Row
from db import register, registry


# constants


# variables


# functions/classes
def show(page: Page, id:str, field:str, title:str, callback:callable, state:str=None) -> str:
    """Show a project dialog."""

    def on_ok_click(e):
        """Callback for the Ok button."""

        page.close(_dialog)
        page.update()
        if not _name_field.value.strip():
            return
            
        if callback:
            callback(page, state, {"id": id, "field": field, "value": _name_field.value.strip()})

    def on_cancel_click(e):
        """Callback for the Cancel button."""

        page.close(_dialog)
        page.update()

    def on_text_change(e):
        ok_button.disabled = not _name_field.value.strip()
        page.update()

    _name = title.capitalize()
    _name_field = TextField(value=field, label=f"Current {_name} value", width=260, on_change=on_text_change)
    cancel_button = ElevatedButton("Cancel", on_click=on_cancel_click)
    ok_button = ElevatedButton("Ok", on_click=on_ok_click, disabled=True)

    _dialog = AlertDialog(
        title=Text(f"Enter new {_name} value:"),
        modal=True,
        content=Row([_name_field]),
        content_padding=10,
        actions=[ok_button, cancel_button],
    )

    page.open(_dialog)
