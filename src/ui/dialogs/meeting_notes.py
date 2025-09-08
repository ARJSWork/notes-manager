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
    ScrollMode,
)
from models.notes import DEFAULT_TEMPLATES, DEFAULT_MODULES
from db import registry


# functions/classes
def show(page: Page, callback: callable, state: str = None):
    """Show a dialog to add a new meeting note."""
    print("meeting_notes.show called, callback=", bool(callback))

    def on_ok_click(e):
        """Callback for the Ok button."""
        print("meeting_notes: OK clicked")
        page.close(dialog)
        page.update()
        # Collect selected template and date and pass to caller via callback
        try:
            tmpl = None
            if template_options and template_options.controls:
                rg = template_options.controls[0]
                tmpl = getattr(rg, "value", None)
        except Exception:
            tmpl = None

        date_str = selected_date.value if selected_date else None
        title = f"{tmpl} {date_str}" if tmpl or date_str else None
        # Visible feedback to main area so we can confirm the handler executed
        try:
            registry.subjects["contentView"].notify(page, [Text(f"meeting_notes OK: {title}")])
        except Exception:
            pass
        if callback:
            try:
                print("meeting_notes: calling callback with", {"title": title, "template": tmpl, "date": date_str})
                callback(page, {"title": title, "template": tmpl, "date": date_str})
            except Exception as ex:
                print("meeting_notes callback error:", ex)

    def on_cancel_click(e):
        """Callback for the Cancel button."""
        page.close(dialog)
        page.update()

    def on_date_selected(e):
        # Use the value provided by the DatePicker event instead of now()
        val = getattr(e.control, "value", None)
        if val:
            try:
                selected_date.value = val.strftime('%Y-%m-%d')
            except Exception:
                selected_date.value = str(val)
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
    # Note: DatePicker should be opened with page.open(date_picker)
    # (don't append to overlay here; open it when the user clicks the button)

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
                            on_click=lambda _: page.open(date_picker),
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
            height=210,
        ),
        actions=[
            ElevatedButton("Cancel", on_click=on_cancel_click),
            ElevatedButton("OK", on_click=on_ok_click),
        ],
    )

    page.open(dialog)
