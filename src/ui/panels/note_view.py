###
# File:   src\ui\panels\note_view.py
# Date:   2025-09-23
# Author: automated-refactor
###

from datetime import datetime
from flet import Column, Text, Row, Colors, Divider, Container, TextField, ElevatedButton, IconButton, Icons, Dropdown, dropdown
from db import registry
from logic.log import info
from models.notes import DEFAULT_TEMPLATES, DEFAULT_MODULES


def build_note_view(page, note_data: dict | None, title_fallback: str = "") -> Column:
    """Build a default view for a note.

    Returns a Column control suitable for publishing via
    registry.subjects["contentView"].notify(page, [Column(...)])

    This function intentionally mirrors the previous inline implementation
    but centralizes it so rendering can be improved later.
    """
    if not note_data:
        return Column(controls=[Text("(No note selected)")])

    editing = bool(note_data.get("_editing", False))

    header = _build_header(page, note_data, title_fallback, editing)
    content = _build_content(note_data, editing)

    return Column(controls=[header, Divider(), content], expand=True)

def _build_header(page, note_data: dict, title_fallback: str, editing: bool) -> Row:
    """Builds the header section of the note view."""
    title = note_data.get("title") or title_fallback or "Untitled"
    date = note_data.get("date")
    tmpl_name = note_data.get("template")

    meta_parts = []
    if date:
        meta_parts.append(str(date))
    if tmpl_name:
        meta_parts.append(str(tmpl_name))
    meta = " • ".join(meta_parts)

    header_content = [Column(controls=[Text(title, size=20), Text(meta, size=12, color=Colors.WHITE70)])]

    if editing:
        header_content.append(Row(controls=[
            ElevatedButton("Save", on_click=lambda ev: _on_save(ev, page, note_data, title_fallback)),
            ElevatedButton("Cancel", on_click=lambda ev: _on_cancel(ev, page, note_data, title_fallback))
        ]))
    else:
        header_content.append(
            IconButton(Icons.EDIT, on_click=lambda ev: _enter_edit(ev, page, note_data, title_fallback),
                       icon_color=Colors.WHITE))

    return Row(controls=header_content, alignment="spaceBetween")

def _build_content(note_data: dict, editing: bool) -> Column:
    """Builds the content section of the note view."""
    if editing:
        return _build_edit_view(note_data)
    return _build_display_view(note_data)


def _build_display_view(note_data: dict) -> Column:
    """Builds the display view for the note content."""
    body = note_data.get("body")
    if not body:
        return Column(controls=[Text("(No content) — click Edit to add details.", color=Colors.WHITE70)])

    parsed_body = _parse_note_body(body)
    controls = []

    # Row for Date, Time, Location
    date_val = parsed_body.get("Date", "")
    time_val = parsed_body.get("Time", "")
    location_val = parsed_body.get("Location", "")

    meta_controls = []
    if date_val:
        meta_controls.append(Text(f"Date: {date_val}"))
    if time_val:
        meta_controls.append(Text(f"Time: {time_val}"))
    if location_val:
        meta_controls.append(Text(f"Location: {location_val}"))
    
    if meta_controls:
        controls.append(Row(controls=meta_controls, spacing=20))

    # Topic
    topic_val = parsed_body.get("Topic", "")
    if topic_val:
        controls.append(Text(topic_val, size=20, weight="bold"))

    # Participants
    participants_val = parsed_body.get("Participants", "")
    if participants_val:
        controls.append(Text("Participants", size=16, weight="bold"))
        controls.append(Text(participants_val))

    # Notes
    notes_val = parsed_body.get("Notes", "")
    if notes_val:
        controls.append(Text("Notes", size=16, weight="bold"))
        controls.append(Container(content=Text(notes_val), expand=True))

    return Column(controls=controls, expand=True, spacing=10)


def _build_edit_view(note_data: dict) -> Column:
    """Builds the edit view for the note content."""
    
    body = note_data.get("body", "") or ""
    parsed_body = _parse_note_body(body)

    # Pre-fill date and time for new notes
    if not parsed_body.get("Date"):
        parsed_body["Date"] = datetime.now().strftime("%d.%m.%Y")
    if not parsed_body.get("Time"):
        parsed_body["Time"] = datetime.now().strftime("%H:%M")

    # Create TextFields for each module
    topic_tf = TextField(label="Topic", value=parsed_body.get("Topic", ""), max_length=50, expand=True)
    date_tf = TextField(label="Date", value=parsed_body.get("Date", ""), max_length=10, width=120)
    time_tf = TextField(label="Time", value=parsed_body.get("Time", ""), max_length=5, width=80)
    location_dd = Dropdown(
        label="Location",
        value=parsed_body.get("Location") or "Online",
        options=[
            dropdown.Option(loc) for loc in (registry.notes_collection.locations if hasattr(registry, "notes_collection") and registry.notes_collection else ["Online", "Office", "Conference Room"])
        ],
        editable=True,
        expand=True,
    )

    participants_tf = TextField(label="Participants", value=parsed_body.get("Participants", ""), multiline=True, min_lines=3, max_lines=10)
    notes_tf = TextField(label="Notes", value=parsed_body.get("Notes", ""), multiline=True, expand=True)

    # Store references for saving
    note_data["_textfields"] = {
        "Topic": topic_tf,
        "Date": date_tf,
        "Time": time_tf,
        "Location": location_dd,
        "Participants": participants_tf,
        "Notes": notes_tf,
    }

    # Layout the fields
    return Column(
        controls=[
            Row(controls=[topic_tf]),
            Row(
                controls=[
                    date_tf,
                    time_tf,
                    location_dd,
                ]
            ),
            participants_tf,
            Container(content=notes_tf, expand=True), # Ensure Notes field expands
        ],
        expand=True
    )

def _parse_note_body(body: str) -> dict:
    """Parses a note body string into a dictionary of modules."""
    modules = {}
    current_module = None
    content = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_module:
                modules[current_module] = "\n".join(content).strip()
            current_module = line[3:].strip()
            content = []
        else:
            content.append(line)
    
    if current_module:
        modules[current_module] = "\n".join(content).strip()

    return modules


def _enter_edit(ev, page, note_data, title_fallback):
    info("Entering edit mode")
    note_data["_editing"] = True
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])

def _on_save(ev, page, note_data, title_fallback):
    info("Saving note")
    textfields = note_data.get("_textfields")
    if textfields:
        new_body = []
        # Iterate in default order to ensure consistency
        for module_name in DEFAULT_MODULES:
            if module_name in textfields:
                control = textfields[module_name]
                value = control.value or ""

                # For Location, update the global list if a new value is added
                if module_name == "Location" and value:
                    if hasattr(registry, "notes_collection") and registry.notes_collection:
                        if value not in registry.notes_collection.locations:
                            registry.notes_collection.locations.append(value)
                
                if value:
                    new_body.append(f"## {module_name}")
                    new_body.append(str(value))
        note_data["body"] = "\n".join(new_body)

    note_data["_editing"] = False
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])

def _on_cancel(ev, page, note_data, title_fallback):
    info("Canceling edit")
    note_data["_editing"] = False
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])
