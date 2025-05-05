###
# File:   src\ui\dialogs\confirm.py
# Date:   2025-01-29 / 11:47
# Author: alexrjs
###


# imports
from flet import Page, Text, ElevatedButton, AlertDialog, MainAxisAlignment


# constants


# variables


# functions/classes
def show(page: Page, callback:callable) -> None:
    """Show a confirm dialog."""

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

    confirm_dialog = AlertDialog(
        title=Text("Confirm"),
        modal=True,
        content=Text("Are you sure?"),
        actions=[
            ElevatedButton("Yes", on_click=on_yes_click),
            ElevatedButton("No", autofocus=True, on_click=on_no_click),
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    page.open(confirm_dialog)
    #page.update()
