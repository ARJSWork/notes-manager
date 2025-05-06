###
# File:   src\logic\ui\project\handlers\module.py
# Date:   2025-05-06 / 06:52
# Author: alexrjs
###


# imports
from flet import(
    ControlEvent, Colors, Container, Column, CrossAxisAlignment, Page, IconButton, TextField, MainAxisAlignment, TextButton, ElevatedButton, Row,
    ListView, ListTile, Text, Icons, AlertDialog, VerticalDivider, border, Stack, Badge, alignment
)
from db import registry
from db.messages import getError
from logic.ui import ContentAction, ITEM_TYPE_MODULES


# constants


# variables


# functions/classes


# imports (flet, registry, db, messages, window, etc.)
from flet import (
    ControlEvent, Colors, Column, TextField, MainAxisAlignment, CrossAxisAlignment,
    TextButton, Row
)
from db import registry
from db.messages import getError
from logic.ui import ContentAction
from logic.ui.window import updateWindowTitle, updateWindowState

# Function to create the module view (moved from __init__.py)
def create_view(e: ControlEvent, _key: str, _id: str) -> None:
    """Creates the view for a module."""

    _projectData = registry.project.data
    assert _projectData, getError("A000")
    assert _key, getError("A000")
    assert _id, getError("A000")
    _element = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _element, getError("A000")
    _element = _element[0]
    assert _element, getError("A000")
    _headline = _element["headline"]
    _content = _element["content"]
    _textHeader = TextField(
        value=_headline,
        color=Colors.WHITE,
        read_only=True,
        max_lines=1,
        max_length=50,
        border_radius=5,
        border_width=1,
        border_color=Colors.GREY_500,
        hint_text="Headline",
        label="Headline",
    )
    _textContent = TextField(
        value=_content,
        expand=True,
        multiline=True,
        color=Colors.WHITE,
        read_only=True,
        max_lines=50,
        min_lines=1,
        max_length=1500,
        border_radius=5,
        border_width=1,
        border_color=Colors.GREY_500,
        hint_text="Content",
        label="Content",
    )
    _column = Column(
        controls=[_textHeader, _textContent],
        data=f"{_key}:{_id}",
        alignment=MainAxisAlignment.START,
        horizontal_alignment=CrossAxisAlignment.STRETCH,
    )
    registry.ui.detailPanel = _column
    _edit = TextButton(
        text="Edit",
        autofocus=True,
        data=_column,
        key=ITEM_TYPE_MODULES,
        on_click=lambda e: registry.subjects["contentActions"].notify(
            e, ContentAction.Edit
        ),
    )
    _cancel = TextButton(
        text="Cancel",
        data=_column,
        key="modules",
        visible=False, # Managed by handleContentActions
        on_click=lambda e: registry.subjects["contentActions"].notify(
            e, ContentAction.Cancel
        ),
    )
    _ok = TextButton(
        text="Ok",
        data=_column,
        key="modules",
        visible=False, # Managed by handleContentActions
        on_click=lambda e: registry.subjects["contentActions"].notify(
            e, ContentAction.Ok
        ),
    )
    _row = Row(
        controls=[_edit, _cancel, _ok],
        alignment=MainAxisAlignment.END,
        vertical_alignment=CrossAxisAlignment.END,
        bottom=10,
        right=10,
        expand=True,
    )
    registry.subjects["contentView"].notify(e.page, [_column, _row])

# Function to switch module view to edit mode (moved from __init__.py)
def switch_to_edit_mode(_control, _data) -> None:
    """Switch to edit mode for a module."""

    assert _data, getError("A000")
    _parent = _control.parent
    assert _parent, getError("A000")
    _headline = _data.controls[0]
    _content = _data.controls[1]

    _headline.read_only = False
    _headline.border_color = Colors.AMBER
    _headline.autofocus = True
    _headline.focus()
    _content.read_only = False
    _content.border_color = Colors.AMBER
    _data.update()
    for _child in _parent.controls:
        _child.visible = True

    _control.visible = False
    _parent.update()

# Function to handle 'Ok' action for module edit (moved from handleContentActions)
def handle_ok(page, control, data) -> None:
    """Handles the OK action after editing a module."""
    # ... implementation of module-specific OK logic from handleContentActions ...
    # Remember to update registry.changed, window title/state
    pass # Replace with actual code

# Function to handle 'Cancel' action for module edit (moved from handleContentActions)
def handle_cancel(page, control, data) -> None:
    """Handles the Cancel action while editing a module."""
    # ... implementation of module-specific Cancel logic from handleContentActions ...
    pass # Replace with actual code

# Potentially add functions for module-specific delete/copy logic if needed