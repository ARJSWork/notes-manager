###
# File:   src\ui\dialogs\notes.py
# Date:   2025-02-06 / 10:26
# Author: alexrjs
###


# imports
import os
from os import path
from os import getcwd
import os as _os
from flet import Colors, Page, Text, ElevatedButton, AlertDialog, TextField, Row, Dropdown, dropdown
from db import register, registry, DEFAULT_NOTES_PATH


# constants


# variables


# functions/classes
def show(page: Page, callback:callable, state:str=None) -> str:
    """Show a note dialog."""
    _button = None

    def on_ok_click(e):
        """Callback for the Ok button."""

        page.close(note_dialog)
        page.update()
        if not note_name_field.value.strip():
            return

        # Register the collection folder under top-level notes/<slug>
        slug = note_name_field.value.strip().replace(' ', '_')
        _path = path.join(getcwd(), "notes", slug)
        _os.makedirs(_path, exist_ok=True)
        register("notesFile", _path)
        register("notesName", note_name_field.value.strip())
        if callback:
            callback(page, state)

    def on_cancel_click(e):
        """Callback for the Cancel button."""

        page.close(note_dialog)
        page.update()

    def on_text_change(e):
        ok_button.disabled = not note_name_field.value.strip()
        if ok_button.disabled:
            ok_button.bgcolor=None
            ok_button.color=None

        else:
            ok_button.bgcolor=Colors.GREEN
            ok_button.color=Colors.WHITE

        page.update()

    def on_focus(e):
        nonlocal _button
        if _button:
            _button.bgcolor=None
            _button.color=None
        
        e.control.bgcolor=Colors.GREEN
        e.control.color=Colors.WHITE
        page.update()

        _button = e.control

    def on_submit(e):
        if not ok_button.disabled:
            on_ok_click(e)

    note_name_field = TextField(label="Notes Name", width=260, autofocus=True, on_change=on_text_change, on_submit=on_submit)
    ok_button = ElevatedButton("Ok", on_click=on_ok_click, on_focus=on_focus, disabled=True)
    cancel_button = ElevatedButton("Cancel", on_click=on_cancel_click, on_focus=on_focus)
    _button = ok_button

    note_dialog = AlertDialog(
        title=Text("Enter Notes Name"),
        modal=True,
        content=Row([note_name_field]),
        content_padding=10,
        actions=[cancel_button, ok_button],
    )

    page.open(note_dialog)
