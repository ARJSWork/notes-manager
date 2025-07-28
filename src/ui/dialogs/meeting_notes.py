###
# File:   src\ui\dialogs\meeting_notes.py
# Date:   2025-07-28
# Author: Gemini
###

# imports
from datetime import datetime
from flet import (
    AlertDialog,
    Checkbox,
    Column,
    DatePicker,
    Dropdown,
    ElevatedButton,
    ListView,
    Page,
    Row,
    Text,
    dropdown,
)
from db import registry
from models.notes import DEFAULT_TEMPLATES, DEFAULT_MODULES


# functions/classes
def show(page: Page, callback: callable, state: str = None):
    """Show a dialog to add a new meeting note."""

    def on_ok_click(e):
        """Callback for the Ok button."""
        page.close(dialog)
        page.update()
        # TODO: Process the selected data

    def on_cancel_click(e):
        """Callback for the Cancel button."""
        page.close(dialog)
        page.update()

    def on_date_selected(e):
        selected_date.value = f"Selected: {date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    selected_date = Text(datetime.now().strftime('%Y-%m-%d'))

    date_picker = DatePicker(
        first_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
        last_date=datetime.strptime("2030-12-31", "%Y-%m-%d"),
        date_picker_entry_mode="CALENDAR_ONLY",
        date_picker_mode="DAY",
        help_text="Select a date",
        on_change=on_date_selected,
    )
    page.overlay.append(date_picker)

    template_dropdown = Dropdown(
        options=[dropdown.Option(t) for t in DEFAULT_TEMPLATES],
        label="Pick a Template",
        width=300,
    )

    module_list = ListView(
        controls=[Checkbox(label=m) for m in DEFAULT_MODULES],
        spacing=5,
        height=150,
    )

    dialog = AlertDialog(
        title=Text("Add Meeting Note"),
        modal=True,
        content=Column(
            [
                Row(
                    [
                        selected_date,
                        ElevatedButton(
                            "Select Date",
                            on_click=lambda _: registry.page.open(date_picker),
                        ),
                    ]
                ),
                template_dropdown,
                Text("Modules"),
                module_list,
            ],
            spacing=10,
            height=300,
        ),
        actions=[
            ElevatedButton("Cancel", on_click=on_cancel_click),
            ElevatedButton("OK", on_click=on_ok_click),
        ],
    )

    page.open(dialog)
