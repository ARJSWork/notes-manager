###
# File:   src\ui\panels\note_view.py
# Date:   2025-09-23
# Author: automated-refactor
###

import re
import os
from flet import (
    Checkbox, Column, Text, Row, Colors, Divider, Container, TextField, 
    ScrollMode, ElevatedButton, IconButton, Icons, VerticalAlignment, MainAxisAlignment
    )
from db import registry
from logic.persistence import save_notes
from logic.log import info
#from models.notes import DEFAULT_MODULES
from ui.controls.custom_menu import CustomMenu
from datetime import datetime
import logging


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
    content = _build_content(page, note_data, editing)

    return Column(
        controls=[header, Divider(), content], expand=True,
        scroll=ScrollMode.AUTO,auto_scroll=True, 
        #alignment=MainAxisAlignment.START, horizontal_alignment=VerticalAlignment.START
        )

def _build_header(page, note_data: dict, title_fallback: str, editing: bool) -> Row:
    """Builds the header section of the note view."""
    title = note_data.get("title") or title_fallback or "Untitled"
    date = note_data.get("date")
    time = note_data.get("time")
    tmpl_name = note_data.get("template")

    meta_parts = []
    if date:
        meta_parts.append(f"Created: {date} / {time}")

    if tmpl_name:
        meta_parts.append(f"Template: {tmpl_name}")

    meta = "  •  ".join(meta_parts)

    header_content = [Column(controls=[Text(title, size=20), Text(meta, size=12, color=Colors.WHITE70)])]

    if editing:
        header_content.append(Row(controls=[
            ElevatedButton("Cancel", on_click=lambda ev: _on_cancel(ev, page, note_data, title_fallback)),
            ElevatedButton("Save", bgcolor=Colors.GREEN, color=Colors.WHITE, on_click=lambda ev: _on_save(ev, page, note_data, title_fallback))
        ]))
    else:
        header_content.append(
            IconButton(Icons.EDIT, on_click=lambda ev: _enter_edit(ev, page, note_data, title_fallback),
                       icon_color=Colors.WHITE))

    return Row(controls=header_content, alignment="spaceBetween")

def _build_content(page, note_data: dict, editing: bool) -> Column:
    """Builds the content section of the note view."""
    if editing:
        return _build_edit_view(page, note_data)
    else:
        return _build_display_view(note_data)

def _build_display_view(note_data: dict) -> Column:
    """Builds the display view for the note content."""
    controls = []

    # Row for Date, Time, Location
    date_val = note_data.get("date", "")
    time_val = note_data.get("time", "")
    location_val = note_data.get("location", "")

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
    topic_val = note_data.get("topic", "")
    if topic_val:
        controls.append(Text(f"Topic: {topic_val}", size=20, weight="bold"))
        #controls.append(Text(topic_val, size=20, weight="bold"))

    # Participants
    participants_val = note_data.get("participants", "")
    if participants_val:
        controls.append(Divider())
        controls.append(Text("Participants", size=16, weight="bold"))

        # Allow participants to be stored as a string or a list/tuple.
        if isinstance(participants_val, (list, tuple)):
            participants_text = ", ".join(str(p) for p in participants_val)
        elif isinstance(participants_val, dict):
            participants_text = ", ".join(f"{k}: {v}" for k, v in participants_val.items())
        else:
            participants_text = str(participants_val)

        controls.append(Text(participants_text))

    # Notes
    notes_val = note_data.get("notes", "")
    if notes_val:
        controls.append(Divider())
        controls.append(Text("Notes", size=16, weight="bold"))
        controls.append(Container(content=Text(notes_val), expand=False))

    # ToDos
    todos_val = note_data.get("todos", "")
    if todos_val:
        controls.append(Divider())
        controls.append(Text("To Do's", size=16, weight="bold"))
        
        todo_items = []
        if isinstance(todos_val, list):
            todo_items = todos_val
        elif isinstance(todos_val, str):
            todo_items = todos_val.splitlines()

        for todo in todo_items:
            if todo.strip():
                checked = '[x]' in todo.lower()
                # Use regex to strip checkbox markers like '- [ ]' or '- [x]'
                text = re.sub(r'^\s*-\s*\[[xX\s]?\]\s*', '', todo).strip()
                controls.append(Checkbox(label=text, value=checked, disabled=True))

    return Column(
        controls=controls, expand=True, spacing=10, auto_scroll=True, scroll=ScrollMode.AUTO,
        alignment=MainAxisAlignment.START, horizontal_alignment=VerticalAlignment.START
        )

def _build_edit_view(page, note_data: dict) -> Column:
    """Builds the edit view for the note content."""
    
    # Create TextFields for each module
    topic_tf = TextField(label="Topic", value=note_data.get("topic", ""), max_length=50, expand=True)
    date_tf = TextField(label="Date", value=note_data.get("date", ""), max_length=10, width=120)
    time_tf = TextField(label="Time", value=note_data.get("time", ""), max_length=5, width=80)
    
    locations = registry.notes_collection.locations if hasattr(registry, "notes_collection") and registry.notes_collection else ["Online", "Office", "Conference Room"]
    location_menu = CustomMenu(
        page,
        items=locations,
        selected_item=note_data.get("location") or "Online",
    )

    # Normalize participants into a comma-separated string for the TextField.
    _participants_raw = note_data.get("participants", "")
    if isinstance(_participants_raw, (list, tuple)):
        participants_value = ", ".join(str(p) for p in _participants_raw)
    elif isinstance(_participants_raw, dict):
        participants_value = ", ".join(f"{k}: {v}" for k, v in _participants_raw.items())
    else:
        participants_value = str(_participants_raw or "")

    participants_tf = TextField(label="Participants", value=participants_value, multiline=True, min_lines=3, max_lines=10)
    notes_tf = TextField(label="Notes", value=note_data.get("notes", ""), multiline=True, expand=True)
    todos_val = note_data.get("todos", "")
    if isinstance(todos_val, list):
        todos_val = "\n".join(todos_val)
    todos_tf = TextField(label="To Do's", value=todos_val, multiline=True, expand=True)

    # Store references for saving
    note_data["_controls"] = {
        "Topic": topic_tf,
        "Date": date_tf,
        "Time": time_tf,
        "Location": location_menu,
        "Participants": participants_tf,
        "Notes": notes_tf,
        "ToDos": todos_tf,
    }

    # Layout the fields
    return Column(
        controls=[
            Row(controls=[topic_tf]),
            Row(
                controls=[
                    date_tf,
                    time_tf,
                    location_menu,
                ]
            ),
            participants_tf,
            Container(content=notes_tf, expand=False), # Ensure Notes field expands
            Container(content=todos_tf, expand=False), # Ensure Notes field expands
        ],
        expand=True
    )

def _enter_edit(ev, page, note_data, title_fallback):
    info("Entering edit mode")
    # Debug: show current payload and attached model before entering edit mode
    try:
        logging.debug("[DEBUG] _enter_edit note_data: title=%r, date=%r, template=%r, body_present=%s", note_data.get('title'), note_data.get('date'), note_data.get('template'), bool(note_data.get('body')))
        if note_data.get('_note_obj') is not None:
            no = note_data.get('_note_obj')
            logging.debug("[DEBUG] _enter_edit _note_obj: title=%r, topic=%r, date=%r, time=%r, location=%r, participants=%r, notes=%r", getattr(no,'title',None), getattr(no,'topic',None), getattr(no,'date',None), getattr(no,'time',None), getattr(no,'location',None), getattr(no,'participants',None), getattr(no,'notes',None))
        else:
            logging.debug("[DEBUG] _enter_edit: no attached _note_obj")
    except Exception as _e:
        logging.exception("[DEBUG] _enter_edit introspect error")

    note_data["_editing"] = True
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])

def _on_save(ev, page, note_data, title_fallback):
    info("Saving note")
    assert note_data is not None, "note_data is None"

    note_data["_editing"] = False
    _controls = note_data.get("_controls")
    if _controls:
        # Simple text fields
        topic_tf = _controls.get("Topic")
        note_data["topic"] = (getattr(topic_tf, "value", "") or "").strip()

        date_tf = _controls.get("Date")
        note_data["date"] = (getattr(date_tf, "value", "") or "").strip()

        time_tf = _controls.get("Time")
        note_data["time"] = (getattr(time_tf, "value", "") or "").strip()

        # Location: preserve selected custom value and update collection if changed
        location_menu = _controls.get("Location")
        try:
            items, selected = location_menu.get_values()
        except Exception:
            # Fallback if API differs: try to read properties directly
            items = getattr(location_menu, "items", [])
            selected = getattr(location_menu, "selected_item", None)

        if hasattr(registry, "notes_collection") and registry.notes_collection:
            if items != registry.notes_collection.locations:
                registry.notes_collection.locations = items
                registry.notes_collection.locations.sort()
                if hasattr(registry, "notesFile") and registry.notesFile:
                    save_notes(registry.notes_collection, registry.notesFile)

        note_data["location"] = selected or ""

        # Participants: split by comma, semicolon or newline into a list
        participants_tf = _controls.get("Participants")
        participants_text = (getattr(participants_tf, "value", "") or "")
        parts = [p.strip() for p in re.split(r"[,\n;]+", participants_text) if p.strip()]
        note_data["participants"] = parts

        # Notes and Todos
        notes_tf = _controls.get("Notes")
        note_data["notes"] = (getattr(notes_tf, "value", "") or "")

        todos_tf = _controls.get("ToDos")
        todos_text = (getattr(todos_tf, "value", "") or "")
        note_data["todos"] = [line for line in todos_text.splitlines() if line.strip()]

        # update timestamp
        note_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        _no = note_data.get("_note_obj")
        if _no:
            logging.debug("[DEBUG] _on_save: updating attached _note_obj %r", getattr(_no,'title',None))
            # Update the attached MeetingNote object with edited values
            _no.title = note_data.get("title", title_fallback)
            _no.topic = note_data.get("topic", "")
            _no.date = note_data.get("date", "")
            _no.time = note_data.get("time", "")
            _no.location = note_data.get("location", "")
            _no.participants = note_data.get("participants", [])
            _no.notes = note_data.get("notes", "")
            _no.todos = note_data.get("todos", [])
            _no.updated_at = note_data["updated_at"]

            # Mark note dirty and persist changed notes
            _no.mark_dirty()
            logging.debug("[DEBUG] _on_save: updated _note_obj to title=%r, topic=%r, date=%r, time=%r, location=%r, participants=%r, notes=%r, todos=%r, updated_at=%r", getattr(_no,'title',None), getattr(_no,'topic',None), getattr(_no,'date',None), getattr(_no,'time',None), getattr(_no,'location',None), getattr(_no,'participants',None), getattr(_no,'notes',None), getattr(_no,'todos',None), getattr(_no,'updated_at',None))
    else:
        info("No _controls found in note_data; skipping save of edits")
        # If no _controls, just exit edit mode without changes
        return


    # Persist changes back to the attached MeetingNote object if available
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])

def _on_cancel(ev, page, note_data, title_fallback):
    info("Canceling edit")
    note_data["_editing"] = False
    note_data.pop("_controls", None)  # Remove references to controls
    note_data.pop("_editing", None)  # Remove editing flag
    registry.subjects["contentView"].notify(page, [build_note_view(page, note_data, title_fallback)])