###
# File:   src\ui\dialogs\project.py
# Date:   2025-02-06 / 10:26
# Author: alexrjs
###


# imports
from os import path
from flet import Colors, Page, Text, ElevatedButton, AlertDialog, TextField, Row
from db import register, registry, DEFAULT_PROJECT_PATH


# constants


# variables


# functions/classes
def show(page: Page, callback:callable, state:str=None) -> str:
    """Show a project dialog."""

    def on_ok_click(e):
        """Callback for the Ok button."""

        page.close(project_dialog)
        page.update()
        if not project_name_field.value.strip():
            return
        
        _path = path.join(DEFAULT_PROJECT_PATH, f"{project_name_field.value.lower()}.json")
        # TODO: Check if the file already exists and display a warning dialog
        # TODO: Save the project file
        register("projectFile", _path)
        register("projectName", project_name_field.value)
        if callback:
            callback(page, state)

    def on_cancel_click(e):
        """Callback for the Cancel button."""

        page.close(project_dialog)
        page.update()

    def on_text_change(e):
        ok_button.disabled = not project_name_field.value.strip()
        if ok_button.disabled:
            ok_button.bgcolor=None
            ok_button.color=None

        else:
            ok_button.bgcolor=Colors.GREEN
            ok_button.color=Colors.WHITE

        page.update()

    project_name_field = TextField(label="Project Name", width=260, autofocus=True, on_change=on_text_change)
    ok_button = ElevatedButton("Ok", on_click=on_ok_click, disabled=True)
    cancel_button = ElevatedButton("Cancel", on_click=on_cancel_click)

    project_dialog = AlertDialog(
        title=Text("Enter Project Name"),
        modal=True,
        content=Row([project_name_field]),
        content_padding=10,
        actions=[cancel_button, ok_button],
    )

    page.open(project_dialog)
