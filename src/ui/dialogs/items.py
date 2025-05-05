###
# File:   src\ui\dialogs\project.py
# Date:   2025-02-06 / 10:26
# Author: alexrjs
###


# imports
from os import path
from flet import AlertDialog, Column, Colors, Page, Text, ElevatedButton, TextField, SnackBar
from db import register, registry


# constants


# variables


# functions/classes
def show(page: Page, data_:dict=None) -> None:
    """ Create Template Dialog """

    def on_text_change(e):
        createButton.disabled = not name_field.value.strip()
        if createButton.disabled:
            createButton.bgcolor=None
            createButton.color=None

        else:
            createButton.bgcolor=Colors.GREEN
            createButton.color=Colors.WHITE

        page.update()

    def on_ok(e):
        """Callback for the Ok button."""

        # Validate name is not empty
        if not name_field.value.strip():
            name_field.error_text = "Name is required"
            page.update()
            return

        page.close(_dialog)
        page.update()

        # Create new template if a callback is here to handle it
        if "callback" in data_ and data_["callback"]:
            new_template = {
                "id": data_["id"],
                "type": data_["type"],
                "name": name_field.value,
                "description": description_field.value
            }
            data_["callback"](page, data_["state"], new_template)

        # Show success message
        _name = data_["type"].capitalize()
        _name = _name[:-1] if _name.endswith("s") else _name
        page.open(SnackBar(content=Text(f"Action for '{_name}' successfully completed."), bgcolor=Colors.GREEN))
        page.update()

    def on_cancel(e):
        page.close(_dialog)
        page.update()

    if not data_:
        return 
    
    _name = "Name here..." if "name" not in data_ else data_['name']
    _label = "Name here..." if "name" not in data_ else ""
    _value = "" if "name" not in data_ else _name
    name_field = TextField(hint_text=_name, label=_label, value=_value, width=260, autofocus=True, on_change=on_text_change)

    _description = "Description here..." if "description" not in data_ else data_['description']
    _label = "Description here..." if "description" not in data_ else ""
    _value = "" if "description" not in data_ else _description
    description_field = TextField(hint_text=_description, label=_label, value=_value, multiline=True)

    _dialog = AlertDialog(
        title=Text("Enter the Item values" if "title" not in data_ else data_["title"]),
        content=Column([name_field, description_field], tight=True),
        actions=[
            ElevatedButton("Cancel" if "no" not in data_ else data_["no"], on_click=on_cancel),
            createButton := ElevatedButton("Ok" if "yes" not in data_ else data_["yes"], disabled=True, on_click=on_ok),
        ],
        actions_alignment="end",
    )

    page.open(_dialog)