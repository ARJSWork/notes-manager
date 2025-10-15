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
    Colors,
    TextField,
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


def show(page: Page, callback: callable, state: str = None):
    """Show a dialog to add a new meeting note."""
    print("meeting_notes.show called, callback=", bool(callback))

    # Visible date text and datepicker
    selected_date = Text(datetime.now().strftime('%Y-%m-%d'))

    def on_date_selected(e):
        val = getattr(e.control, "value", None)
        if val:
            try:
                selected_date.value = val.strftime('%Y-%m-%d')
            except Exception:
                selected_date.value = str(val)
        page.update()

    date_picker = DatePicker(
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2030, 12, 31),
        date_picker_entry_mode="CALENDAR_ONLY",
        date_picker_mode="DAY",
        help_text="Select a date",
        on_change=on_date_selected,
    )

    # Template and module selectors
    template_title = Text("Templates", visible=True)

    template_options = ListView(
        controls=[
            RadioGroup(
                content=Column([
                    Radio(value=t, label=t) for t in DEFAULT_TEMPLATES.keys()
                ]),
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

    # Inline fields to capture module values (Topic, Time, Location, Participants, Notes)
    topic_field = TextField(label="Topic", value="", width=380, visible=False)
    time_field = TextField(label="Time", value="", width=120, visible=False)
    location_field = TextField(label="Location", value="", width=200, visible=False)
    participants_field = TextField(label="Participants", value="", multiline=True, min_lines=2, max_lines=4, width=380, visible=False)
    notes_field = TextField(label="Notes", value="", multiline=True, min_lines=3, max_lines=10, width=380, visible=False)

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

        date_str = selected_date.value if selected_date else datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H:%M') if not time_field.value else time_field.value
        location_str = "Online" if not location_field.value else location_field.value
        #participants_str = participants_field.value if participants_field.value else None
        notes = []
        todos = []
        participants = []
        title = f"{tmpl}" if tmpl else f"Note"
        title += f" {date_str} {time_str}"

        # Visible feedback to main area so we can confirm the handler executed
        try:
            registry.subjects["contentView"].notify(page, [Text(f"meeting_notes OK: {title}")])
        except Exception:
            pass

        if callback:
            try:
                # Build a body string that mirrors the template/modules structure
                body_lines = []
                # Use DEFAULT_MODULES ordering if available
                try:
                    from models.notes import DEFAULT_MODULES
                    modules_order = DEFAULT_MODULES
                except Exception:
                    modules_order = ["Topic", "Date", "Time", "Participants", "Location", "Notes"]

                for m in modules_order:
                    body_lines.append(f"## {m}")
                    if m == "Topic":
                        v = topic_field.value or "Meeting Notes"
                        if v:
                            body_lines.append(v)
                        continue
                    if m == "Date":
                        v = date_str or selected_date.value or ""
                        if v:
                            body_lines.append(v)
                        continue
                    if m == "Time":
                        v = time_str or time_field.value or ""
                        if v:
                            body_lines.append(v)
                        continue
                    if m == "Participants":
                        v = participants_field.value or ""
                        if v:
                            # preserve lines
                            for ln in str(v).splitlines():
                                body_lines.append(ln)
                                participants.append(ln)
                        else:
                            # keep template default if no user notes
                            try:
                                t = DEFAULT_TEMPLATES.get(tmpl, {})
                                default_notes = t.get("Participants", []) if isinstance(t.get("Participants", []), list) else []
                                for ln in default_notes:
                                    body_lines.append(ln)
                                    participants.append(ln)
                            except Exception:
                                pass
                        continue
                    if m == "Location":
                        v = location_str or location_field.value or ""
                        if v:
                            body_lines.append(v)
                        continue
                    if m == "Notes":
                        v = notes_field.value or ""
                        if v:
                            for ln in str(v).splitlines():
                                body_lines.append(ln)
                        else:
                            # keep template default if no user notes
                            try:
                                t = DEFAULT_TEMPLATES.get(tmpl, {})
                                default_notes = t.get("Notes", []) if isinstance(t.get("Notes", []), list) else []
                                for ln in default_notes:
                                    if ln.strip().startswith("#") or ln.strip().startswith("##"):
                                        body_lines.append("")  # add spacing before headings
                                        notes.append("")

                                    body_lines.append(ln)
                                    notes.append(ln)
                            except Exception:
                                pass
                        continue
                    if m == "ToDos":
                        v = notes_field.value or ""
                        if v:
                            for ln in str(v).splitlines():
                                body_lines.append(ln)
                                todos.append(ln)
                        else:
                            # keep template default if no user notes
                            try:
                                t = DEFAULT_TEMPLATES.get(tmpl, {})
                                default_notes = t.get("ToDos", []) if isinstance(t.get("ToDos", []), list) else []
                                for ln in default_notes:
                                    body_lines.append(ln)
                                    todos.append(ln)
                            except Exception:
                                pass
                        continue

                #body_str = "\n".join(body_lines)

                payload = {
                    "title": title,
                    "template": tmpl,
                    "date": date_str,
                    # Module-specific fields
                    "topic": topic_field.value or "Meeting Note",
                    "time": time_field.value or time_str or None,
                    "location": location_field.value or location_str or None,
                    "participants": participants_field.value or "\n".join(participants) or None,
                    "todos": notes_field.value or "\n".join(todos) or None,
                    "notes": notes_field.value or "\n".join(notes[1:]) or None,
                }
                print("meeting_notes: calling callback with", payload)
                callback(page, payload)
            except Exception as ex:
                print("meeting_notes callback error:", ex)

    def on_cancel_click(e):
        """Callback for the Cancel button."""
        page.close(dialog)
        page.update()

    dialog = AlertDialog(
        title=Text("Add Meeting Note"),
        modal=True,
        content=Column(
            [
                Row([
                    selected_date,
                    ElevatedButton("Select Date", on_click=lambda _: page.open(date_picker)),
                ]),
                RadioGroup(
                    content=Row([
                        Radio(value="template", label="Use Template"),
                        Radio(value="modules", label="Select Modules"),
                    ]),
                    on_change=on_option_change,
                    value="template",
                ),
                template_title,
                template_options,
                modules_title,
                module_list,
                # Inline editable fields for note content
                topic_field,
                Row(controls=[date_picker, time_field]),
                location_field,
                participants_field,
                notes_field,
            ],
            spacing=10,
            height=210,
        ),
        actions=[
            ElevatedButton("Cancel", on_click=on_cancel_click),
            ElevatedButton("OK", on_click=on_ok_click, bgcolor=Colors.GREEN, color=Colors.WHITE),
        ],
    )

    page.open(dialog)
