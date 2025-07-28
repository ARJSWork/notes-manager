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
    Radio,
    RadioGroup,
    Row,
    Text,
    dropdown,
)
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
        selected_date.value = datetime.now().strftime('%Y-%m-%d')
        page.update()

    def on_option_change(e):
        if e.control.value == "template":
            template_title.visible = True
            template_options.visible = True
            modules_title.visible = False
            module_list.visible = False
        else:
            template_title.visible = False
            template_options.visible = False
            modules_title.visible = True
            module_list.visible = True
        page.update()

    selected_date = Text(datetime.now().strftime('%Y-%m-%d'))

    date_picker = DatePicker(
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2030, 12, 31),
        date_picker_entry_mode="CALENDAR_ONLY",
        date_picker_mode="DAY",
        help_text="Select a date",
        on_change=on_date_selected,
    )
    page.overlay.append(date_picker)

    template_title = Text("Templates", visible=True)

    template_options = ListView(
        controls=[
            RadioGroup(
                content=Column(
                    [Radio(value=t, label=t) for t in DEFAULT_TEMPLATES.keys()]
                ),
                value=list(DEFAULT_TEMPLATES.keys())[0] if DEFAULT_TEMPLATES else None,
            )
        ],
        spacing=5,
        height=150,
        visible=True,
    )

    modules_title = Text("Modules", visible=False)

    module_list = ListView(
        controls=[Checkbox(label=m) for m in DEFAULT_MODULES],
        spacing=5,
        height=150,
        visible=False,
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
                            on_click=lambda _: date_picker.pick_date(),
                        ),
                    ]
                ),
                RadioGroup(
                    content=Row(
                        [
                            Radio(value="template", label="Use Template"),
                            Radio(value="modules", label="Select Modules"),
                        ]
                    ),
                    on_change=on_option_change,
                    value="template",
                ),
                template_title,
                template_options,
                modules_title,
                module_list,
            ],
            spacing=10,
            height=300,
        ),
        actions=[
            ElevatedButton("Cancel", on_click=on_cancel_click),
            ElevatedButton("OK", on_ok_click),
        ],
    )

    page.open(dialog)
