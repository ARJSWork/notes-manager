###
# File:   src\logic\ui\project\handlers\template.py
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
from logic.ui import ContentAction, ITEM_TYPE_TEMPLATES, ITEM_TYPE_MODULES
from logic.ui.window import updateWindowTitle, updateWindowState


# constants


# variables


# functions/classes
# Function to create the module view (moved from __init__.py)
def create_view(data_: dict) -> None:
    """Creates the view for a template."""

    assert data_, getError("A000")
    _key = data_["type"]
    assert _key, getError("A000")
    _id = data_["id"]
    assert _id, getError("A000")
    _projectData = registry.project.data
    assert _projectData, getError("A000")
    _element = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _element, getError("A000")
    _element = _element[0]
    assert _element, getError("A000")
    _modules = _element["modules"]

    def _move_module_up(e, module_id, template_id):
        
        module_list = e.control.parent.parent.parent
        if not module_list or not module_list.controls:
            return

        current_index = -1
        for i, item in enumerate(module_list.controls):
            if item.data == module_id:
                current_index = i
                break

        if current_index > 0:
            module_list.controls.insert(current_index - 1, module_list.controls.pop(current_index))
            module_list.update()
            _projectData = registry.project.data
            _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == template_id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError(f"A000: Template {template_id} not found")
            _template["modules"].insert(current_index - 1, _template["modules"].pop(current_index))
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)

    def _move_module_down(e, module_id, template_id):
        
        module_list = e.control.parent.parent.parent
        if not module_list or not module_list.controls:
            return
        
        current_index = -1
        for i, item in enumerate(module_list.controls):
            if item.data == module_id:
                current_index = i
                break

        if -1 < current_index < len(module_list.controls) - 1:
            module_list.controls.insert(current_index + 1, module_list.controls.pop(current_index))
            _projectData = registry.project.data
            _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == template_id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError(f"A000: Template {template_id} not found")
            _template["modules"].insert(current_index + 1, _template["modules"].pop(current_index))
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)

    _list = ListView(
        expand=True, 
        spacing=2, 
        padding=2, 
        data=f"{_key}:{_id}",
        auto_scroll=True
    )
    for _moduleId in _modules:
        _module = [_e for _e in _projectData[ITEM_TYPE_MODULES] if _e["id"] == str(_moduleId)]
        if not _module or len(_module) != 1:
            print(f"Warning: Module {_moduleId} not found or ambiguous for template {_id}") # More informative warning
            continue # Skip this module if not found
        
        _moduleInfo = f"{ITEM_TYPE_MODULES}:{_moduleId}"
        _up = IconButton(Icons.ARROW_CIRCLE_UP, icon_color=Colors.WHITE, key=_moduleInfo, on_click=lambda e, mid=_moduleId, t_id=_id: _move_module_up(e, mid,  t_id))
        _down = IconButton(Icons.ARROW_CIRCLE_DOWN, icon_color=Colors.WHITE, key=_moduleInfo, on_click=lambda e, mid=_moduleId, t_id=_id: _move_module_down(e, mid, t_id))
        #_delete = IconButton(Icons.REMOVE_CIRCLE, icon_color=Colors.WHITE, key=_moduleInfo, on_click=lambda e, mid=_moduleId, t_id=_id: _remove_from_meeting_simple(e, t_id, mid))
        _iconRow = Row(
            controls=[_up, _down],
            alignment=MainAxisAlignment.END,
            tight=True,
            spacing=0,
            run_spacing=0,
            visible=True
        )
        _module = _module[0]
        _item = ListTile(
            leading=Text(str(_moduleId)),
            title=Text(_module["name"]),
            subtitle=Text(_module["headline"]),
            trailing=_iconRow,
            key=_moduleInfo,
            disabled=False,
            data=_moduleId # store the module id here for later access
        )
        _list.controls.append(_item)

    _edit = TextButton(
        text="Edit",
        autofocus=True,
        data=_list,
        key=ITEM_TYPE_TEMPLATES,
        on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Edit)
    )
    # _cancel = TextButton(
    #     text="Cancel",
    #     data=_list,
    #     visible=False,
    #     key="templates",
    #     on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Cancel)
    # )
    # _ok = TextButton(
    #     text="Ok",
    #     data=_list,
    #     visible=True,
    #     key="templates",
    #     on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Ok)
    # )
    _row = Row(
        controls=[_edit], #[_edit, _cancel, _ok],
        alignment=MainAxisAlignment.END,
        vertical_alignment=CrossAxisAlignment.END,
        bottom=10,
        right=10,
        expand=True,
    )

    registry.ui.detailPanel = _list
    registry.subjects["contentView"].notify(registry.page, [_list, _row])

# Function to switch module view to edit mode (moved from __init__.py)
def switch_to_edit_mode(_control, _key, _id) -> None:
    """Switch to edit mode for a template and open a dialog for managing modules."""

    _parent = _control.parent
    assert _parent, getError("A000")
    # _list = _data
    # assert _list, getError("A000")

    #_template_key, _template_id = _list.data.split(":")
    _projectData = registry.project.data
    _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == _id]
    assert _template, getError("A000")
    _template = _template[0]
    assert _template, getError("A000")
    _modules_in_template = _template[ITEM_TYPE_MODULES].copy()
    _available_modules = [m for m in _projectData["modules"] if m["id"] not in _modules_in_template].copy()

    def create_icon_row(module_id, is_in_template, callback):
        """Creates a row of icons for managing modules."""

        _iconRow = Row(
            controls=[],
            alignment=MainAxisAlignment.END,
            tight=True,
            spacing=0,
            run_spacing=0,
        )

        if is_in_template:
            _up = IconButton(
                Icons.ARROW_CIRCLE_UP,
                icon_color=Colors.WHITE,
                key=f"{ITEM_TYPE_MODULES}:{module_id}",
                data=f"{_key}:{_id}",
                on_click=lambda e, mid=module_id: _move_module_up(e, mid),
            )
            _down = IconButton(
                Icons.ARROW_CIRCLE_DOWN,
                icon_color=Colors.WHITE,
                key=f"{ITEM_TYPE_MODULES}:{module_id}",
                data=f"{_key}:{_id}",
                on_click=lambda e, mid=module_id: _move_module_down(e, mid),
            )
            _delete = IconButton(
                Icons.REMOVE_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"{ITEM_TYPE_MODULES}:{module_id}",
                data=f"{_key}:{_id}",
                on_click=callback,
            )
            _iconRow.controls.extend([_up, _down, _delete])
        else:
            _add = IconButton(
                Icons.ADD_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"{ITEM_TYPE_MODULES}:{module_id}",
                data=f"{_key}:{_id}",
                on_click=callback
            )
            _iconRow.controls.append(_add)

        return _iconRow

    # Helper functions for the dialog
    def newTile(no_, module, icon, callback):
        return ListTile(
            leading=Text(str(module["id"])),
            title=Text(module["name"]),
            subtitle=Text(module["headline"]),
            bgcolor=Colors.GREY_800 if no_ % 2 == 0 else Colors.GREY_900,
            trailing=create_icon_row(
                module["id"],
                module["id"] in _modules_in_template,
                callback=callback
            ),
            key=f"{ITEM_TYPE_MODULES}:{module['id']}",
            data=module["id"],
        )

    def close_dlg(e):
        e.page.close(_dlg)

    def reColorItems(list_view: ListView):
        """Recolors items in a list view for alternating backgrounds."""
        for i, item in enumerate(list_view.controls):
            if isinstance(item, ListTile):
                item.bgcolor = Colors.GREY_800 if i % 2 == 0 else Colors.GREY_900
                # item.update() # Update wird oft durch list_view.update() abgedeckt

    def activate_save_button(activate=True):
        _saveButton.disabled = not activate
        if _saveButton.disabled:
            _saveButton.bgcolor=None
            _saveButton.color=None

        else:
            _saveButton.bgcolor=Colors.GREEN
            _saveButton.color=Colors.WHITE

        _saveButton.update()

    def _move_module_up(e, module_id):
        
        module_list = e.control.parent.parent.parent
        if not module_list or not module_list.controls:
            return

        current_index = -1
        for i, item in enumerate(module_list.controls):
            if item.data == module_id:
                current_index = i
                break

        if current_index > 0:
            _element = module_list.controls.pop(current_index)
            module_list.controls.insert(current_index - 1, _element)
            reColorItems(module_list)
            _element.bgcolor = Colors.DEEP_ORANGE_900
            _element.update()
            module_list.update()
            if e.control.data:
                if ":" in e.control.data:
                    _key, _id = e.control.data.split(":")
                
                else: 
                    print("No Key, ID Pair")
                    return
                
            else: 
                print("No Key, ID Pair")
                return

            _projectData = registry.project.data
            _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == _id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError(f"A000: Template {_id} not found")
            _template["modules"].insert(current_index - 1, _template["modules"].pop(current_index))
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)
            activate_save_button()

    def _move_module_down(e, module_id):
        
        module_list = e.control.parent.parent.parent
        if not module_list or not module_list.controls:
            return
        
        current_index = -1
        for i, item in enumerate(module_list.controls):
            if item.data == module_id:
                current_index = i
                break

        if -1 < current_index < len(module_list.controls) - 1:
            _element = module_list.controls.pop(current_index)
            module_list.controls.insert(current_index + 1, _element)
            reColorItems(module_list)
            _element.bgcolor = Colors.DEEP_ORANGE_900
            _element.update()
            module_list.update()
            if e.control.data:
                if ":" in e.control.data:
                    _key, _id = e.control.data.split(":")
                
                else: 
                    print("No Key, ID Pair")
                    return
                
            else: 
                print("No Key, ID Pair")
                return
                    
            _projectData = registry.project.data
            _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == _id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError(f"A000: Template {_id} not found")
            _template["modules"].insert(current_index + 1, _template["modules"].pop(current_index))
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)
            activate_save_button()

    def _refresh_template_view(data_: dict) -> None:
        # Remove the old view
        registry.subjects["contentView"].notify(registry.page, [])
        create_view(data_)

    def save_modules(e):
        e.page.close(_dlg)
        _template["modules"] = [
            m.data
            for m in _module_list.controls
            if isinstance(m, ListTile)
            and m.data is not None
        ]
        _refresh_template_view(_template)
        registry.project.status = "Changed"
        registry.changed = True

    def add_module_to_template(e):
        if e.control.key:
            _, module_id = e.control.key.split(":")
            assert module_id, getError("A000")
            module_data = [m for m in _projectData[ITEM_TYPE_MODULES] if m["id"] == module_id][0]
            assert module_data, getError("A000")
        
        else:
            print(f"No Key, ID Pair")
            return
        
        _modules_in_template.append(module_id)
        _available_modules.remove(module_data)
        
        _available_module_list.controls.remove(e.control.parent.parent)
        _available_module_list.update()

        _len = len(_module_list.controls)
        _module_list.controls.append(
            newTile(_len, module_data, Icons.REMOVE_CIRCLE, remove_module_from_template)
        )
        _module_list.update()

        reColorItems(_module_list)
        reColorItems(_available_module_list)
        if _len > 0:
            _module_list.controls[-1].bgcolor = Colors.DEEP_ORANGE_900
            _module_list.controls[-1].update()

        registry.changed = True
        registry.project.status = "Changed"
        updateWindowTitle(e.page, registry.projectName + "*")
        updateWindowState(e.page, registry.changed)
        activate_save_button()

    def remove_module_from_template(e):
        if e.control.key:
            _, module_id = e.control.key.split(":")
            assert module_id, getError("A000")
            module_data = [m for m in _projectData[ITEM_TYPE_MODULES] if m["id"] == module_id][0]
            assert module_data, getError("A000")
        
        else:
            print(f"No Key, ID Pair")
            return
        
        _modules_in_template.remove(module_id)
        _available_modules.append(module_data)

        _module_list.controls.remove(e.control.parent.parent)
        _module_list.update()

        _len = len(_available_module_list.controls)
        _available_module_list.controls.append(
            newTile(_len, module_data, Icons.ADD_CIRCLE, add_module_to_template)
        )
        _available_module_list.update()

        reColorItems(_module_list)
        reColorItems(_available_module_list)
        registry.changed = True
        registry.project.status = "Changed"
        updateWindowTitle(e.page, registry.projectName + "*")
        updateWindowState(e.page, registry.changed)
        activate_save_button()

    # Prepare the UI elements for the dialog
    _available_module_list = ListView(
        expand=True, spacing=2, padding=2, auto_scroll=True
    )
    _data = sorted(_available_modules, key=lambda x: str(x.get("name", "")))
    for _i, module in enumerate(_data):
        _available_module_list.controls.append(
            newTile(_i, module, Icons.ADD_CIRCLE, add_module_to_template)
        )

    _module_list = ListView(
        expand=True, spacing=2, padding=2, auto_scroll=True
    )

    for _i, module_id in enumerate(_modules_in_template):
        module_data = [m for m in _projectData[ITEM_TYPE_MODULES] if m["id"] == module_id][0]
        _module_list.controls.append(
            newTile(_i, module_data, Icons.REMOVE_CIRCLE, remove_module_from_template)
        )

    _dlg = AlertDialog(
        title=Text(f"Edit Modules for Template {_template['name']}"),
        content=Row(
            [
                Container(
                    content=_module_list,
                    border=border.all(2, Colors.GREY_500),
                    border_radius=5,
                    padding=5,
                    expand=True,
                    width=500,
                    badge=Badge("Selected Modules", alignment=alignment.top_left, bgcolor=Colors.GREY_500, text_color=Colors.WHITE)
                ),
                VerticalDivider(),
                Container(
                    content=_available_module_list,
                    border=border.all(2, Colors.GREY_500),
                    border_radius=5,
                    padding=5,
                    expand=True,
                    width=500,
                    badge=Badge("Available Modules", alignment=alignment.top_left, bgcolor=Colors.GREY_500, text_color=Colors.WHITE)
                ),
            ],
            expand=True,
        ),
        actions=[
            ElevatedButton("Close", key=_id, on_click=close_dlg),
            _saveButton := ElevatedButton("Save", disabled=True, key=_id, on_click=save_modules),
        ],
        actions_alignment="end",
        # open=True,
        # adaptive=True,
    )

    _control.page.open(_dlg)

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