###
# File:   src\ui\dialogs\datetype.py
# Date:   2025-02-20 / 10:26
# Author: alexrjs
###


# imports
from flet import (
    AlertDialog,
    Column,
    Colors,
    Page,
    Text,
    ElevatedButton,
    TextField,
    SnackBar,
    Dropdown,
    dropdown,
    DatePicker,
    Row,
    Icons,
    alignment,
    DatePickerEntryMode,
)
from datetime import date, datetime, timedelta, tzinfo

# constants
MEETING_TYPES = ["BR Sitzung", "Meeting", "Sondersitzung"]


# variables


# functions/classes
def show(page: Page, data_: dict = None) -> None:
    """Create DateType Dialog"""

    def visualize_ok():
        createButton.disabled = not name_field.value.strip()
        if createButton.disabled:
            createButton.bgcolor = None
            createButton.color = None

        else:
            createButton.bgcolor = Colors.GREEN
            createButton.color = Colors.WHITE

    def on_text_change(e):
        visualize_ok()
        page.update()

    def on_date_change(e):
        selected_date = date_picker.value
        name_field.value = selected_date.strftime("%Y-%m-%d")
        name_field.error_text = ""
        description_field.value = f"{meeting_type_dropdown.value} am {selected_date.strftime("%d.%m.%Y")}"
        visualize_ok()
        page.update()

    def on_dropdown_change(e):
        _date = date_picker.value
        _date = "?" if not _date else _date.strftime("%d.%m.%Y") #_date.strftime("%Y-%m-%d")
        description_field.value = f"{meeting_type_dropdown.value} am {_date}"
        description_field.error_text = ""
        visualize_ok()
        page.update()

    def on_ok(e):
        """Callback for the Ok button."""

        # Validate type is not empty
        if not meeting_type_dropdown.value:
            meeting_type_dropdown.error_text = "Type is required"
            page.update()
            return
        else:
            meeting_type_dropdown.error_text = ""
            meeting_type_dropdown.update()
            
        # Validate date is not empty
        if not date_picker.value:
            name_field.error_text = "Date is required"
            page.update()
            return
        else:
            name_field.error_text = ""
            name_field.update()
        
        # Validate name is not empty
        if not name_field.value.strip():
            name_field.error_text = "Name is required"
            error_field.visible = True
            page.update()
            return

        page.close(_dialog)
        page.update()

        # Create new meeting if a callback is here to handle it
        if "callback" in data_ and data_["callback"]:
            new_meeting = {
                "id": data_["id"],
                "type": data_["type"],
                "name": name_field.value,
                "description": description_field.value,
                "date": date_picker.value.strftime("%Y-%m-%d"),
                "kind": meeting_type_dropdown.value,
                "tops": []
            }
            data_["callback"](page, data_["state"], new_meeting)

        # Show success message
        _name = data_["type"].capitalize()
        _name = _name[:-1] if _name.endswith("s") else _name
        page.open(
            SnackBar(
                content=Text(f"Action for '{_name}' successfully completed."),
                bgcolor=Colors.GREEN,
            )
        )
        page.update()

    def on_cancel(e):
        page.close(_dialog)
        page.update()

    if not data_:
        return

    _name = "Name here..." if "name" not in data_ else data_["name"]
    _label = "Name here..." if "name" not in data_ else ""
    _value = "" if "name" not in data_ else _name
    name_field = TextField(
        hint_text=_name,
        label=_label,
        value=_value,
        width=260,
        autofocus=True,
        on_change=on_text_change,
    )

    _description = (
        "Description here..." if "description" not in data_ else data_["description"]
    )
    _label = "Description here..." if "description" not in data_ else ""
    _value = "" if "description" not in data_ else _description
    description_field = TextField(
        hint_text=_description, label=_label, value=_value, multiline=True
    )

    error_field = TextField(
        label="Message",
        value="",
        read_only=True,
        width=200,
        color=Colors.RED,
        icon=Icons.ERROR,
        visible=False,
        #hint_text="Select a date",
    )

    date_picker = DatePicker(
        on_change=on_date_change,
        current_date=datetime.now(),
        date_picker_entry_mode=DatePickerEntryMode.CALENDAR_ONLY,
        first_date=datetime(date.today().year, date.today().month, date.today().day),
        last_date=datetime(date.today().year + 1, date.today().month, date.today().day),
    )

    _kind = "BR Sitzung" if "kind" not in data_ else data_["kind"]
    meeting_type_dropdown = Dropdown(
        value=_kind,
        label="Meeting Type",
        width=200,
        options=[dropdown.Option(type) for type in MEETING_TYPES],
        on_change=on_dropdown_change,
    )

    _dialog = AlertDialog(
        title=Text(
            "Enter the Meeting information" if "title" not in data_ else data_["title"]
        ),
        content=Column(
            [
                Row(
                    [
                        meeting_type_dropdown,
                        ElevatedButton(
                            "Pick Date",
                            on_click=lambda e: page.open(date_picker),
                        ),
                        #date_field,
                    ],
                    alignment=alignment.center,
                ),
                name_field,
                description_field,
                error_field,
            ],
            tight=True,
            width=400,
        ),
        actions=[
            ElevatedButton(
                "Cancel" if "no" not in data_ else data_["no"], on_click=on_cancel
            ),
            createButton := ElevatedButton(
                "Ok" if "yes" not in data_ else data_["yes"],
                disabled=True,
                on_click=on_ok,
            ),
        ],
        actions_alignment="end",
    )

    page.open(_dialog)
