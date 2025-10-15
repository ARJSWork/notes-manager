###
# File:   src\ui\dialogs\confirm.py
# Date:   2025-01-29 / 11:47
# Author: alexrjs
###


# imports
from flet import Colors, Page, Text, ElevatedButton, AlertDialog, MainAxisAlignment


# constants


# variables


# functions/classes
def show(page: Page, callback:callable) -> None:
    """Show a confirm dialog."""
    _button = None

    def on_yes_click(e):
        """Callback for the Yes button."""

        page.close(confirm_dialog)
        page.update()
        if callback:
            callback()

    def on_no_click(e):
        """Callback for the No button."""

        page.close(confirm_dialog)
        page.update()

    def on_focus(e):
        nonlocal _button
        e.control.bgcolor=Colors.RED
        e.control.color=Colors.WHITE
        if _button and _button != e.control:
            _button.bgcolor=None
            _button.color=None
        
        page.update()
        _button = e.control

    confirm_dialog = AlertDialog(
        title=Text("Confirm"),
        modal=True,
        content=Text("Are you sure?"),
        actions=[
            ElevatedButton("Yes", on_click=on_yes_click, on_focus=on_focus, autofocus=True, bgcolor=Colors.RED, color=Colors.WHITE),
            ElevatedButton("No", autofocus=True, on_click=on_no_click, on_focus=on_focus),
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    page.open(confirm_dialog)
    #page.update()
