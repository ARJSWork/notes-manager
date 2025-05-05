###
# File:   src\ui\views\project.py
# Date:   2025-02-04 / 10:47
# Author: alexrjs
###


# imports
import flet as ft
from flet import (
    Container, Column, Colors, ControlEvent, CrossAxisAlignment, ExpansionTile, ExpansionPanelList, ExpansionPanel, ListTile,
    TextButton, TileAffinity, OutlinedButton, Switch, IconButton, Checkbox, Text, Icons, Icon, Row,
    MainAxisAlignment, VisualDensity,
    alignment, padding
)
from db import register, registry
from db.messages import getError, handleError
from logic.ui import ContentAction, ProjectState
from models.projectmanager import ProjectManager


# constants


# variables


# functions/classes
def handle_change(e: ControlEvent):
    """Handle the change event"""

    print(f"change on panel with index {e.data}")
    e.control.data.controls[1].visible = e.data
    e.control.data.update()


def handle_delete(e: ControlEvent):
    """Handle the delete event"""

    _panel = registry.ui.projectPanel
    _panel = None
    if not _panel:
        return getError("A001")

    if handleError("A001", _panel):
        return 

    _panel.controls.remove(e.control.data)
    _panel.update()


def build() -> Container:
    """ Return a template view """

    _column = Column(
        tight=True,
    )
    register("ui.projectPanel", _column)

    return Container(
        content=_column,
        padding=0,
        margin=1,
        data="projectPanel",
    )


def clear() -> None:
    """Clear the view"""

    _panel = registry.ui.projectPanel
    _panel.controls.clear()
    _panel.update()


def refresh(mgr_: ProjectManager) -> None:
    """Refresh the view"""

    _panel = registry.ui.projectPanel
    _selected = _panel.key if _panel.key else "templates:1"
    _panel.controls.clear()

    _elements = [("meetings", "AddMeeting"), ("templates", "AddTemplate"), ("modules", "AddModule")]
    for _element, _signal in _elements:
        _expanded = (_element == "templates") or len(mgr_.data[_element]) > 0
        _title = Row(
            controls=[
                Text(_element.capitalize(), size=16, color=Colors.WHITE),
                IconButton(Icons.ADD, visible=_expanded, key=_element, data=_signal, on_click=lambda e: registry.subjects["projectView"].notify(e))
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
        )
        _ctl = ExpansionTile(
            leading=Icon(Icons.FOLDER),
            title=_title, 
            data=_title,
            affinity=TileAffinity.PLATFORM,
            maintain_state=True,
            initially_expanded=_expanded,
            tile_padding=padding.symmetric(horizontal=5.0),
            expanded_alignment=alignment.top_left,
            expanded_cross_axis_alignment=CrossAxisAlignment.START,
            on_change=handle_change
        )
        _panel.controls.append(_ctl)

        if _element not in mgr_.data:
            continue

        _data = mgr_.data[_element]
        if _element == "meetings":
            _data = sorted(_data, key=lambda x: str(x.get("date", "")), reverse=True)

        elif _element == "modules":
            _data = sorted(_data, key=lambda x: str(x.get("name", "")))
            
        for _entry in _data:
            _id = f"{_element}:{_entry["id"]}"
            _color = Colors.BLACK if _id == _selected else Colors.WHITE
            _renameIcon = IconButton(
                Icons.EDIT, icon_size=12, key=_id, icon_color=_color, data=_entry, 
                hover_color=Colors.ORANGE, visual_density=VisualDensity.COMPACT,
                on_click=lambda e: registry.subjects["projectView"].notify(e, "Rename")
            )
            _editIcon = IconButton(
                Icons.EDIT_NOTE, icon_size=12, key=_id, icon_color=_color, data=_entry, 
                hover_color=Colors.ORANGE, visual_density=VisualDensity.COMPACT,
                on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Edit)
            )
            _copyIcon = IconButton(
                Icons.COPY, icon_size=12, key=_id, icon_color=_color, data=_entry, 
                hover_color=Colors.ORANGE, visual_density=VisualDensity.COMPACT,
                on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Copy)
            )
            _delIcon = IconButton(
                Icons.DELETE, icon_size=12, key=_id, icon_color=_color, data=_entry, 
                hover_color=Colors.ORANGE, visual_density=VisualDensity.COMPACT,
                on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Delete)
            )
            _text = _entry["name"] if "kind" not in _entry else f"{_entry["kind"][0].upper()}-{_entry["name"]}"
            _item = Row(
                controls=[
                    Text(
                        _text, key=_entry["id"], color=_color, weight="bold",
                        tooltip=None if "description" not in _entry else _entry["description"], 
                    ),
                    Row(
                        controls=[],
                        tight=True,
                        spacing=0,
                    )
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                spacing=1,
                run_spacing=10,
            )
            #if _element != "meetings":
            _item.controls[1].controls.append(_renameIcon)

            if _element != "modules":
                _item.controls[1].controls.append(_editIcon)

            _item.controls[1].controls.append(_copyIcon)
            _item.controls[1].controls.append(_delIcon)

            _bgcolor = Colors.AMBER if _id == _selected else Colors.TRANSPARENT
            _container = Container(
                _item,
                bgcolor=_bgcolor,
                key=_id,
                margin=ft.margin.symmetric(horizontal=5),
                padding=ft.padding.symmetric(horizontal=5),
                on_click=lambda e: registry.subjects["projectView"].notify(e, ProjectState.SELECTED)
            )
            mgr_.controls[_id] = _item
            _ctl.controls.append(_container)

    _panel.key = _selected
    _panel.update()
