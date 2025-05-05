###
# File:   src\logic\ui\project\__init__.py
# Date:   2025-02-18 / 12:20
# Author: alexrjs
###


# imports
from flet import(
    ControlEvent, Colors, Container, Column, CrossAxisAlignment, Page, IconButton, TextField, MainAxisAlignment, TextButton, ElevatedButton, Row,
    ListView, ListTile, Text, Icons, AlertDialog, VerticalDivider, border, Stack, Badge, alignment
)
from db import registry
from db.messages import getError
from logic.ui import ContentAction, ProjectState
from logic.ui.project.render import render_meeting
from logic.ui.window import updateWindowState, updateWindowTitle
from ui.dialogs import items as ItemsDialog, datetype as DateTypeDialog, confirm as confirmDialog
from ui.dialogs.file import showSave
from ui.views import project


# constants
FIELDS = {
    ProjectState.ADDTEMPLATE: [("modules", [])],
    ProjectState.ADDMODULE: [("headline", ""), ("content", "")],
    ProjectState.ADDMEETING: [("name1", ""), ("description1", "")]
}


# variables
## Validations as tuples: (expression, error_code)
validations0 = [
    ("values_['page']", "U001"),
    ("values_['state']", "U002"),
    ("values_['project']", "A000")
]

validations1 = [
    ("values_['id'] and values_['id'] != ''", "A000"),  # Check id exists and is not empty
    ("values_['name']", "A000"),  # Check if field exists and is not empty
    ("len(values_.get('id', '')) < 12", "A000") #Check the length of the id
]

validations2 = [
    ("values_['type'] and values_['type'] != ''", "A000"),
    ("values_['name'] and values_['name'] != ''", "A000")
]

# functions/classes
def validate_values(values_, validations) -> bool:
    """Validates a dictionary against a set of expressions.

    Args:
        values_: The dictionary to validate.
        *validations: A variable number of tuples, where each tuple contains:
            - A validation expression (string).  This will be evaluated.
            - The error code to use if the validation fails.

    Returns:
        None if all validations pass.  Raises a ValueError with the error message
        if any validation fails.  This allows the calling function to handle
        the error as appropriate.
    
    Raises:
        ValueError: If any validation fails.
    """

    try:
        for expression, error_code in validations:
            try:
                # Use eval() with caution!  See security considerations below.
                if not eval(expression, {}, {"values_": values_}):  # Pass values_ to eval
                    raise ValueError(getError(error_code)) # Raise exception if eval is false
                
            except (NameError, SyntaxError, TypeError) as e:  # Catch potential eval errors
                raise ValueError(f"Invalid validation expression: {expression}. {e}") from e
            
            except ValueError as e: # Reraise the ValueError with the error message
                raise # Re-raise the ValueError, so the calling function can handle it.

        return True

    except Exception as _e:
        print(_e)
        return False


def _create_meetings_view(_data: dict) -> None:
    """Creates the view for meetings."""

    assert _data, getError("A000")
    _type = _data["type"]
    assert _type, getError("A000")
    _id = _data["id"]
    assert _id, getError("A000")
    _tops = _data["tops"]

    _list = ListView(
        expand=True, 
        spacing=2, 
        padding=2, 
        data=f"{_type}:{_id}",
        auto_scroll=True
    )
    _item = ListTile(
        title=Text("Agenda:"),
        disabled=False,
    )
    _list.controls.append(_item)
    for _i, _top in enumerate(_tops):
        _topType = _top["type"]
        assert _topType, getError("A000")
        _topId = _top["id"]
        assert _topId, getError("A000")
        match _topType:
            case "text":
                _title = TextField(
                    value=f"▶ {_top['value']}",
                    color=Colors.WHITE,
                    read_only=True,
                    max_lines=50,
                    min_lines=1,
                    max_length=500,
                    border_radius=5,
                    border_width=1,
                    border_color=Colors.GREY_500,
                    label="Custom Text",
                    key=f"{_topType}:{_topId}",
                    data=_top
                )

            case "templates":
                _template = [_e for _e in registry.project.data["templates"] if _e["id"] == _topId]
                assert _template, getError("A000")
                _template = _template[0]
                assert _template, getError("A000")

                _value = ""
                for _moduleId in _template["modules"]:
                    _module = [_e for _e in registry.project.data["modules"] if _e["id"] == str(_moduleId)]
                    assert _module, getError("A000")
                    _module = _module[0]
                    assert _module, getError("A000")
                    _value += f"▶ {_module['headline']} (M{int(_moduleId):02d})\n"

                _title = TextField(
                    value=_value.strip(),
                    color=Colors.WHITE,
                    read_only=True,
                    max_lines=50,
                    min_lines=1,
                    max_length=500,
                    border_radius=5,
                    border_width=1,
                    border_color=Colors.GREY_500,
                    label=f"Template:{int(_topId):02d}",
                    key=f"{_topType}:{_topId}",
                    data=_top
                )
                
            case "modules":
                _module = [_e for _e in registry.project.data["modules"] if _e["id"] == _topId]
                assert _module, getError("A000")
                _module = _module[0]
                assert _module, getError("A000")
                _value = f'▶ {_module["headline"]}'

                _title = TextField(
                    value=_value,
                    color=Colors.WHITE,
                    read_only=True,
                    max_lines=50,
                    min_lines=1,
                    max_length=500,
                    border_radius=5,
                    border_width=1,
                    border_color=Colors.GREY_500,
                    label=f"Module:{int(_topId):02d}",
                    key=f"{_topType}:{_topId}",
                    data=_top
                )
                
            case _:
                print(f"Unknown top type {_topType}")
                continue
    
        _item = ListTile(
            title=_title,
            key=f"{_type}:{_id}",
            disabled=False,
            data=_i # store the module id here for later access
        )
        _list.controls.append(_item)

    _renderToPreview = TextButton(
        text="Render & Preview",
        autofocus=True,
        data=_list,
        key="meetings",
        disabled=len(_tops) <= 0,
        on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.RenderToPreview)
    )
    _renderToFile = TextButton(
        text="Render & Save",
        autofocus=True,
        data=_list,
        key="meetings",
        disabled=len(_tops) <= 0,

        on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.RenderToFile)
    )
    if registry.page.web:
        _renderToFile.visible = False
    
    _renderToClipboard = TextButton(
        text="Render & Clipboard",
        autofocus=True,
        data=_list,
        key="meetings",
        disabled=len(_tops) <= 0,
        on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.RenderToClipboard)
    )
    _edit = TextButton(
        text="Edit",
        autofocus=True,
        data=_list,
        key="meetings",
        on_click=lambda e: registry.subjects["contentActions"].notify(e, ContentAction.Edit)
    )
    _row = Row(
        controls=[_renderToPreview, _renderToFile, _renderToClipboard, _edit],
        alignment=MainAxisAlignment.END,
        vertical_alignment=CrossAxisAlignment.END,
        bottom=10,
        right=10,
        expand=True,
    )

    registry.ui.detailPanel = _list
    registry.subjects["contentView"].notify(registry.page, [_list, _row]) 


def _create_template_view(data_: dict) -> None:
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
            _template = [_e for _e in _projectData["templates"] if _e["id"] == template_id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError("A000")
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
            _template = [_e for _e in _projectData["templates"] if _e["id"] == template_id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError("A000")
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
        _module = [_e for _e in _projectData["modules"] if _e["id"] == str(_moduleId)]
        if not _module or len(_module) != 1:
            return
        
        _moduleInfo = f"modules:{_moduleId}"
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
        key="templates",
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
    

def _create_module_view(e: ControlEvent, _key: str, _id: str) -> None:
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
        key="modules",
        on_click=lambda e: registry.subjects["contentActions"].notify(
            e, ContentAction.Edit
        ),
    )
    _cancel = TextButton(
        text="Cancel",
        data=_column,
        key="modules",
        visible=False,
        on_click=lambda e: registry.subjects["contentActions"].notify(
            e, ContentAction.Cancel
        ),
    )
    _ok = TextButton(
        text="Ok",
        data=_column,
        key="modules",
        visible=False,
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


def _select_project_item(e: ControlEvent, new_: str, override_: bool = False) -> None:
    """Selects an meeting item and updates the UI."""

    _panel = registry.ui.projectPanel
    _current = _panel.key if _panel.key else "templates:1"
    if e.target != "initial" and (_current == new_ and not override_):
        return

    # TODO Extract to function
    _item = registry.project.controls[_current]
    _item.controls[0].color = Colors.WHITE
    for _icon in _item.controls[1].controls:
        if isinstance(_icon, IconButton):
            _icon.icon_color = Colors.WHITE
        else:
            _icon.color = Colors.WHITE

    _item.parent.bgcolor = None
    _item.parent.update()

    # TODO Extract to function
    _item = registry.project.controls[new_]
    _item.controls[0].color = Colors.BLACK
    for _icon in _item.controls[1].controls:
        if isinstance(_icon, IconButton):
            _icon.icon_color = Colors.BLACK
        else:
            _icon.color = Colors.BLACK

    _item.parent.bgcolor = Colors.AMBER
    _item.parent.update()

    _panel.key = new_
    _key, _id = new_.split(":")
    assert _key, getError("A000")
    assert _id, getError("A000")
    _projectData = registry.project.data
    assert _projectData, getError("A000")
    _data = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _data, getError("A000")
    _data = _data[0]
    assert _data, getError("A000")
    match _key:
        case "meetings":
            _create_meetings_view(_data)

        case "templates":
            _create_template_view(_data)
            
        case "modules":
            _create_module_view(e, _key, _id) # TODO: Simplify

        case _:
            print(f"Unknown key {new_}")


def handleClick(subject: str, e: ControlEvent, action: str = None) -> None:
    """Handle click events based on the action."""

    _key = e.control.key
    _action = action
    if not _action:
        if e.control and e.control.data:
            _action = e.control.data

        else:
            return

    print(f"Click '{_action}' triggered for subject {subject} with key: {e.control.key}")

    match _action:
        case ProjectState.SELECTED:
            return _select_project_item(e, e.control.key)

        case "AddTemplate":
            _data = {
                "title": "Add a Template:",
                "id": None,
                "type": _key,
                "kind": "items",
                "callback": setProjectState,
                "state": ProjectState.ADDTEMPLATE
            }
            return handle_add(e, _data)

        case "AddModule":
            _data = {
                "title": "Add a Module:",
                "id": None,
                "type": _key,
                "kind": "items",
                "callback": setProjectState,
                "state": ProjectState.ADDMODULE
            }
            return handle_add(e, _data)

        case "AddMeeting":
            _data = {
                "title": "Add an Meeting:",
                "id": None,
                "type": _key,
                "kind": "datetype",
                "callback": setProjectState,
                "state": ProjectState.ADDMEETING
            }
            return handle_add(e, _data)

        case "Rename":
            return handle_rename(e, _key)
        
        case _:
            return


def handle_rename(e: ControlEvent, _: str) -> None:
    """Handle Rename"""
        
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.data, getError("A002")

    except Exception as _e:
        print(_e)
        return

    _select_project_item(e, e.control.key)
    #e.page.update()

    _item = e.control.data
    assert _item, getError("A000")
    _type = _item["type"]
    assert _type, getError("A000")
    _id = _item["id"]
    assert _id, getError("A000")
    print(f"{_type}.{_id}.on_click")

    if _type == "meetings":
        _data = _item.copy()
        _data["callback"] = setProjectState
        _data["state"] = ProjectState.RENAMED
        DateTypeDialog.show(e.page, _data)

    else:
        _name = _type.capitalize()
        _name = _name[:-1] if _name.endswith("s") else _name
        # Rufe den Dialog auf
        _data = {
            "title": f"Change the {_name}:",
            "id": _id,
            "type": _type,
            "name": _item['name'],
            "description": _item['description'],
            "callback": setProjectState,
            "state": ProjectState.RENAMED
        }
        ItemsDialog.show(e.page, _data)


def handle_add(e: ControlEvent, data: str) -> None:
    """Handle Rename"""
        
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert data, getError("A000")
        assert "kind" in data, getError("A000")

    except Exception as _e:
        print(_e)
        return

    e.page.update()
    #print(f"{e.control.key}.on_click")

    # Rufe den Dialog auf
    match data["kind"]:
        case "items":
            ItemsDialog.show(e.page, data)

        case "datetype":
            print(f"{data['type']}.on_click")
            DateTypeDialog.show(e.page, data)
    
        case _:
            print(f"Unknown kind {data.kind}")


def filter_ids_by_type(tops: list, target_type: str) -> list:
    """
    Filters a list of "top" dictionaries and returns a list of IDs for a specific type.

    Args:
        tops: A list of dictionaries, where each dictionary represents a "top" and has "type" and "id" keys.
        target_type: The type to filter by (e.g., "templates", "modules", "text").

    Returns:
        A list of IDs (strings) that match the target type.
    """

    filtered_ids = [
        top["id"] for top in tops if top["type"] == target_type
    ]
    return filtered_ids


def get_available_entries_not_in_tops(tops: list, entries: list) -> list:
    """
    Identifies and returns a list of templates that are not present in the 'tops' list.

    Args:
        tops: A list of dictionaries, where each dictionary represents a "top" and has "type" and "id" keys.
        templates: A list of dictionaries, where each dictionary represents a template and has "id" and "type" keys.

    Returns:
        A list of template dictionaries that are not found in the 'tops' list.
    """

    _projectData = registry.project.data
    assert _projectData, getError("A000")

    # Extract template IDs from the 'tops' list.
    _ids_in_tops = {
        top["id"] for top in tops if top["type"] == entries
    }

    # Filter the 'templates' list to include only those not present in 'template_ids_in_tops'.
    available_ids = [
        entry
        for entry in  _projectData[entries]
        if entry["id"] not in _ids_in_tops
    ]

    return available_ids


def find_index_by_id(list_of_dicts, _type, _id):
    """
    Finds the index of a dictionary in a list of dictionaries where the "id" key matches a given value.

    Args:
        list_of_dicts: A list of dictionaries, where each dictionary has an "id" key.
        _moduleId: The value to search for in the "id" key.

    Returns:
        The index of the dictionary in the list where the "id" matches _moduleId, or -1 if no match is found.
    """
    for index, dictionary in enumerate(list_of_dicts):
        if "id" in dictionary and dictionary["type"] == _type and dictionary["id"] == str(_id):
            return index

    return -1


def _switchToEditModeForMeeting(_control, _key, _id) -> None:
    """Switch to edit mode for a meeting and open a dialog for managing tops."""

    _parent = _control.parent
    assert _parent, getError("A000")
    _projectData = registry.project.data
    assert _projectData, getError("A000")
    _meeting = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _meeting, getError("A000")
    _meeting = _meeting[0]
    assert _meeting, getError("A000")
    _tops_in_meeting = _meeting["tops"].copy()
    _available_templates = get_available_entries_not_in_tops(_tops_in_meeting, "templates")
    _available_modules = get_available_entries_not_in_tops(_tops_in_meeting, "modules")

    def create_icon_row(type, id, is_in, callback):
        """Creates a row of icons for managing modules."""

        _iconRow = Row(
            controls=[],
            alignment=MainAxisAlignment.END,
            tight=True,
            spacing=0,
            run_spacing=0,
        )

        if is_in:
            _up = IconButton(
                Icons.ARROW_CIRCLE_UP,
                icon_color=Colors.WHITE,
                key=f"{type}:{id}",
                on_click=lambda e, mid=id, tid=type: _move_top_up(e, tid, mid),
            )
            _down = IconButton(
                Icons.ARROW_CIRCLE_DOWN,
                icon_color=Colors.WHITE,
                key=f"{type}:{id}",
                on_click=lambda e, mid=id, tid=type: _move_top_down(e, tid, mid),
            )
            _delete = IconButton(
                Icons.REMOVE_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"{type}:{id}",
                on_click=callback,
                data=id,
            )
            _iconRow.controls.extend([_up, _down, _delete])
        else:
            _add = IconButton(
                Icons.ADD_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"{type}:{id}",
                on_click=callback,
                data=id,
            )
            _iconRow.controls.append(_add)

        return _iconRow

    # Helper functions for the dialog
    def newTile(no_: int, data_: dict, is_in: bool, callback: callable):
        match data_["type"]:
            case "templates":
                _trailing = create_icon_row(
                    data_["type"],
                    data_["id"],
                    is_in,
                    callback=callback,
                )
                _key = f"templates:{data_['id']}"
                _data = data_["id"]
                _leading = Text("T"+str(data_["id"]))
                _addition = "None" if data_["modules"] is None else ", ".join(data_["modules"])
                _subtitle = Text(f'{data_["description"]}\nIncluded Modules {_addition}', max_lines=2)
                if is_in:
                    for _modelId in data_["modules"]:
                        _index = find_index_by_id(_available_modules, "modules", _modelId)
                        if _index >= 0:
                            _available_modules.pop(_index)
                
            case "modules":
                _trailing = create_icon_row(
                    data_["type"],
                    data_["id"],
                    is_in,
                    callback=callback,
                )
                _key = f"modules:{data_['id']}"
                _data = data_["id"]
                _leading = Text("M" + str(data_["id"]))
                _subtitle = Text(data_["headline"])

            case "text":
                _trailing = create_icon_row(
                    data_["type"],
                    data_["id"],
                    is_in,
                    callback=callback,
                )
                _data = data_["value"]
                _key = f"text:{data_['id']}"
                _leading = Text("CT")
                _subtitle = Text(data_["value"][0:30] + "...")

            case _:
                print(f"Unknown type {data_['type']}")
                return
            
        return ListTile(
            leading=_leading,
            title=Text(data_["name"]),
            subtitle=_subtitle,
            trailing=_trailing,
            bgcolor=Colors.GREY_800 if no_ % 2 == 0 else Colors.GREY_900,
            content_padding=0,
            dense=True,
            key=_key,
            data=_data,
            #on_click=lambda e: _select_item(e, _key)
        )

    def close_dlg(e):
        e.page.close(_dlg)

    def activate_save_button(activate=True):
        _saveButton.disabled = not activate
        if _saveButton.disabled:
            _saveButton.bgcolor=None
            _saveButton.color=None

        else:
            _saveButton.bgcolor=Colors.GREEN
            _saveButton.color=Colors.WHITE

        _saveButton.update()

    def reColorItems(tops_list):
        for i, item in enumerate(tops_list.controls):
            item.bgcolor = Colors.GREY_800 if i % 2 == 0 else Colors.GREY_900
            item.update()

    def _move_top_up(e, type, id):
        """ move top one up"""
        
        tops_list = e.control.parent.parent.parent
        if not tops_list or not tops_list.controls:
            return

        if type == "text":
            _uid = e.control.parent.parent.uid
            _index = [_i for _i, _c in enumerate(tops_list.controls) if _c.uid == _uid]
            assert _index, getError("A000")
            _index = _index[0]
            assert _index >= 0, getError("A000")
            current_index = _index
            
        else:
            current_index = -1
            for i, item in enumerate(tops_list.controls):
                _key, _id = item.key.split(":")
                if _id == id:
                    current_index = i
                    _type = _key
                    break

        if current_index > 0:
            _element = tops_list.controls.pop(current_index)
            tops_list.controls.insert(current_index - 1, _element)
            tops_list.update()
            reColorItems(tops_list)
            _element.bgcolor = Colors.DEEP_ORANGE_900
            _element.update()
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)
            activate_save_button()

    def _move_top_down(e, type, id):
        
        tops_list = e.control.parent.parent.parent
        if not tops_list or not tops_list.controls:
            return
        
        if type == "text":
            _uid = e.control.parent.parent.uid
            _index = [_i for _i, _c in enumerate(tops_list.controls) if _c.uid == _uid]
            assert _index, getError("A000")
            _index = _index[0]
            assert _index >= 0, getError("A000")
            current_index = _index
            
        else:
            current_index = -1
            for i, item in enumerate(tops_list.controls):
                _, _id = item.key.split(":")
                if _id == id:
                    current_index = i
                    break

        if -1 <current_index < len(tops_list.controls) - 1:
            _element = tops_list.controls.pop(current_index)
            tops_list.controls.insert(current_index + 1, _element)
            tops_list.update()
            reColorItems(_tops_list)
            _element.bgcolor = Colors.DEEP_ORANGE_900
            _element.update()
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)
            activate_save_button()

    def save_modules(e):
        e.page.close(_dlg)
        _tops = [
            (m.key, m.data)
            for m in _tops_list.controls
            if isinstance(m, ListTile)
            and m.data is not None
        ]
        _newTops = []
        for _topKey, _topData in _tops:
            _type, _id = _topKey.split(":")
            assert _type, getError("A000")
            assert _id, getError("A000")
            _top = {
                "type": _type,
                "id": _id,
                "name": "",
                "value": ""
            }
            match _type:
                case "templates":
                    _template = [_e for _e in _projectData["templates"] if _e["id"] == _id]
                    assert _template, getError("A000")
                    _template = _template[0]
                    assert _template, getError("A000")
                    _top["name"] = _template["name"]
                    #_top["value"] = _template["content"]

                case "modules":
                    _module = [m for m in _projectData["modules"] if m["id"] == _id]
                    assert _module, getError("A000")
                    _module = _module[0]
                    assert _module, getError("A000")
                    _top["name"] = _module["name"]
                    #_top["value"] = _module["content"]

                case "text":
                    _top["value"] = _topData
    
                case _:
                    _top = None
                    print(f"Unknown type {_type}")
                    continue

            if _top:
                _newTops.append(_top.copy())
            # _index = find_index_by_id(_meeting["tops"], _type, _id)
            # if _index > -1:
            #     _newTops.append(_meeting["tops"][_index].copy())
            # else:
            #     _newTops.append(_top.copy())

        _meeting["tops"] = _newTops.copy()
        registry.changed = True
        registry.project.status = "Changed"
        updateWindowTitle(e.page, registry.projectName + "*")
        updateWindowState(e.page, registry.changed)
        _newKey = f"meetings:{e.control.key}"
        _e = ControlEvent("save", "??", data=_newKey, control=_control, page=registry.page)
        _select_project_item(_e, _newKey, True)

    def add_to_meeting(e):
        _selecteId = e.control.data
        _type, _id = e.control.key.split(":")
        assert _type, getError("A000")
        assert _id, getError("A000")        
        if _type != "text":
            _data = [m for m in _projectData[_type] if m["id"] == _selecteId]
            assert _data, getError("A000")
            _data = _data[0]
            assert _data, getError(f"A000")

        _value = ""

        match _type:
            case "templates":
                _modules_in_meeting = filter_ids_by_type(_tops_in_meeting, "modules")
                _templates_in_meeting = filter_ids_by_type(_tops_in_meeting, "templates")
                if _selecteId in _templates_in_meeting:
                    return
                    
                _templates_in_meeting.append(_selecteId)
                _available_templates.remove(_data)
                _available_template_list.controls.remove(e.control.parent.parent)
                _available_template_list.update()
                _pos = len(_templates_in_meeting)
                _name = _data["name"]

                # filter all available meetings out, that are included in the current template
                _template = [_e for _e in _projectData["templates"] if _e["id"] == _selecteId]
                if _template:
                    _template = _template[0]
                    assert _template, getError("A000")
                    for _moduleId in _template["modules"]:
                        _index = find_index_by_id(_available_modules, "modules", _moduleId)
                        if _index >= 0:
                            _available_modules.pop(_index)

                        if _moduleId in _modules_in_meeting:
                            _index = _modules_in_meeting.index(_moduleId)
                            if _index >= 0:
                                _modules_in_meeting.pop(_index)

                        _control = [m for m in _available_module_list.controls if m.data == _moduleId]
                        if _control:
                            _control = _control[0]
                            assert _control, getError("A000")
                            _available_module_list.controls.remove(_control)
                            _available_module_list.update()

                        else:
                            _control = [m for m in _tops_list.controls if m.data == _moduleId]
                            if not _control:
                                continue

                            _control = _control[0]
                            assert _control, getError("A000")
                            _tops_list.controls.remove(_control)
                            _tops_list.update()

                            _modules_in_meeting = filter_ids_by_type(_tops_in_meeting, "modules")
                            if _moduleId in _modules_in_meeting:
                                _index = _modules_in_meeting.index(_moduleId)
                                if _index >= 0:
                                    _modules_in_meeting.pop(_index)
                                
                                _index = find_index_by_id(_tops_in_meeting, "modules", _moduleId)
                                if _index >= 0:
                                    _tops_in_meeting.pop(_index)
                
            case "modules":
                _modules_in_meeting = filter_ids_by_type(_tops_in_meeting, "modules")
                if _selecteId in _modules_in_meeting:
                    return
                    
                _modules_in_meeting.append(_selecteId)
                _available_modules.remove(_data)
                _available_module_list.controls.remove(e.control.parent.parent)
                _available_module_list.update()
                _pos = len(_modules_in_meeting)
                _name = _data["name"]

            case "text":
                _name = "Custom Text"
                _value = _textBox.value
                _pos = 0
                _id = -1
                _data = {
                    "type": _type,
                    "id": _id,
                    "name": _name,
                    "value": _value
                }
                _textBox.value = ""
                _textBox.update()

            case _:
                print(f"Unknown type {_type}")
                return
    
        _tops_in_meeting.append(
            {
                "type": _type,
                "id": _id,
                "name": _name,
                "value": _value
            }
        )    
        _len = len(_tops_list.controls)        
        _tops_list.controls.append(
            newTile(_len, _data, True, remove_from_meeting)
        )
        _tops_list.update()
        reColorItems(_tops_list)
        reColorItems(_available_template_list)
        reColorItems(_available_module_list)
        if _len > 0:
            _tops_list.controls[-1].bgcolor = Colors.DEEP_ORANGE_900
            _tops_list.controls[-1].update()

        registry.changed = True
        registry.project.status = "Changed"
        updateWindowTitle(e.page, registry.projectName + "*")
        updateWindowState(e.page, registry.changed)
        activate_save_button()

    def remove_from_meeting(e):
        _selecteId = e.control.data
        _type, _id = e.control.key.split(":")
        assert _type, getError("A000")
        assert _id, getError("A000")
        if _type == "text":
            _text_in_meeting = find_index_by_id(_tops_in_meeting, "text", -1)
            _textValues = [m for m in _tops_in_meeting if m["type"] == "text"]
        else:      
            _data = [m for m in _projectData[_type] if m["id"] == _selecteId]
            assert _data, getError("A000")
            _data = _data[0]
            assert _data, getError(f"A000")

        match _type:
            case "templates":
                _templates_in_meeting = filter_ids_by_type(_tops_in_meeting, "templates")
                if _selecteId not in _templates_in_meeting:
                    return

                _available_templates.append(_data)
                if _selecteId in _templates_in_meeting:
                    _index = find_index_by_id(_tops_in_meeting, "templates", _selecteId)
                    if _index >= 0:
                        _tops_in_meeting.pop(_index)

                _available_template_list.controls.append(newTile(0, _data, False, add_to_meeting))
                _available_template_list.update()
                _tops_list.controls.remove(e.control.parent.parent)
                _tops_list.update()

                # filter all available meetings out, that are included in the current template
                _template = _data #[_e for _e in _projectData["templates"] if _e["id"] == _selecteId]
                if _template:
                    for _moduleId in _template["modules"]:
                        _data = [m for m in _projectData["modules"] if m["id"] == _moduleId]
                        assert _data, getError("A000")
                        _data = _data[0]
                        assert _data, getError(f"A000")
                        _available_modules.append(_data)
                        _available_module_list.controls.append(newTile(0, _data, False, add_to_meeting))
                        _available_module_list.update()
                
            case "modules":
                _modules_in_meeting = filter_ids_by_type(_tops_in_meeting, "modules")
                if _selecteId not in _modules_in_meeting:
                    return
                    
                _available_modules.append(_data)
                if _selecteId in _modules_in_meeting:
                    _index = _modules_in_meeting.index(_selecteId)
                    if _index >= 0:
                        _modules_in_meeting.pop(_index)
                                
                    _index = find_index_by_id(_tops_in_meeting, "modules", _selecteId)
                    if _index >= 0:
                        _tops_in_meeting.pop(_index)

                _available_module_list.controls.append(newTile(0, _data, False, add_to_meeting))
                _available_module_list.update()
                _tops_list.controls.remove(e.control.parent.parent)
                _tops_list.update()

            case "text":
                _control = e.control.parent.parent
                assert _control, getError("A000")
                _textBox.value = _control.data
                _textBox.update()
                _tops_list.controls.remove(_control)
                _tops_list.update()

            case _:
                print(f"Unknown type {_type}")
                return
    
        # _tops_list.controls.append(
        #     newTile(_pos, _data, True, remove_from_meeting)
        # )
        # _tops_list.update()
        reColorItems(_tops_list)
        reColorItems(_available_template_list)
        reColorItems(_available_module_list)
        registry.changed = True
        registry.project.status = "Changed"
        updateWindowTitle(e.page, registry.projectName + "*")
        updateWindowState(e.page, registry.changed)
        activate_save_button()

    def _clearText(e):
        _textBox.value = ""
        _textBox.update()

    def _select_item(e: ControlEvent, key_) -> None:
        print(e.control.key, key_)

    # Prepare the UI elements for the dialog
    _tops_list = ListView(
        expand=True, spacing=2, padding=2, auto_scroll=False, key=f"meetings:{_id}"
    )

    _used_moduls = []
    for _i, _top in enumerate(_tops_in_meeting):
        _topId = _top["id"]
        _topType = _top["type"] 
        match _topType:
            case "templates":
                _template = [_e for _e in _projectData["templates"] if _e["id"] == _topId][0]
                _tops_list.controls.append(
                    newTile(_i, _template, True, remove_from_meeting)
                )
            
            case "modules":
                _module = [_e for _e in _projectData["modules"] if _e["id"] == _topId][0]
                _tops_list.controls.append(
                    newTile(_i, _module, True, remove_from_meeting)
                )
                _used_moduls.append(_topId)
            
            case "text":
                _top["name"] = "Custom Text"
                _tops_list.controls.append(
                    newTile(_i, _top, True, remove_from_meeting)
                )
            
            case _:
                print(f"Unknown type {_topId['type']}")

    # Prepare the UI elements for the dialog
    _available_template_list = ListView(
        expand=False, spacing=2, padding=2, auto_scroll=False
    )
    for _i, template in enumerate(_available_templates):
        _available_template_list.controls.append(
            newTile(_i, template, False, add_to_meeting)
        )

    # Prepare the UI elements for the dialog
    _available_modules = [m for m in _available_modules if m["id"] not in _used_moduls]
    _available_module_list = ListView(
        expand=False, spacing=2, padding=2, auto_scroll=False
    )
    for _i, module in enumerate(_available_modules):
        _available_module_list.controls.append(
            newTile(_i, module, False, add_to_meeting)
        )

    _dlg = AlertDialog(
        title=Text(f"Edit Tops for Meeting {_meeting['name']}"),
        content=Column(
            controls=[
                Row(
                    controls=[
                        Container(
                            content=_tops_list,
                            border=border.all(2, Colors.GREY_500),
                            border_radius=5,
                            padding=5,
                            expand=True,
                            width=400,
                            badge=Badge("Meeting Agenda", alignment=alignment.top_left, bgcolor=Colors.GREY_500, text_color=Colors.WHITE)
                        ),
                        VerticalDivider(),
                        Column(
                            controls=[
                                Container(
                                    content=_available_template_list,
                                    border=border.all(2, Colors.GREY_500),
                                    border_radius=5,
                                    padding=5,
                                    expand=True,
                                    width=400,
                                    badge=Badge("Templates", alignment=alignment.top_left, bgcolor=Colors.GREY_500, text_color=Colors.WHITE)
                                ),
                                Container(
                                    content=_available_module_list,
                                    border=border.all(2, Colors.GREY_500),
                                    border_radius=5,
                                    padding=5,
                                    expand=True,
                                    width=400,
                                    badge=Badge("Modules", alignment=alignment.top_left, bgcolor=Colors.GREY_500, text_color=Colors.WHITE)
                                ),
                            ]
                        ),
                    ],
                    expand=True,
                ),
                Row(
                    controls=[
                        _textBox := TextField(
                            "",
                            multiline=True,
                            min_lines=1,
                            max_lines=4,
                            max_length=150,
                            border_radius=5,
                            border_width=2,
                            border_color=Colors.GREY_500,
                            color=Colors.WHITE,                            
                            label="Custom Text",
                            hint_text="Add a short temporary Text",
                            expand=True
                        ),
                        _clearTextButton := IconButton(icon=Icons.CLEAR, key=f"text:-1", data=-1, on_click=_clearText),
                        _addTextButton := IconButton(icon=Icons.ADD, key=f"text:-1", data=-1, on_click=add_to_meeting),
                    ],
                    alignment="start",
                ),
            ],
            alignment="end",
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


def _switchToEditModeForTemplate(_control, _key, _id) -> None:
    """Switch to edit mode for a template and open a dialog for managing modules."""

    _parent = _control.parent
    assert _parent, getError("A000")
    # _list = _data
    # assert _list, getError("A000")

    #_template_key, _template_id = _list.data.split(":")
    _projectData = registry.project.data
    _template = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _template, getError("A000")
    _template = _template[0]
    assert _template, getError("A000")
    _modules_in_template = _template["modules"].copy()
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
                key=f"modules:{module_id}",
                data=f"{_key}:{_id}",
                on_click=lambda e, mid=module_id: _move_module_up(e, mid),
            )
            _down = IconButton(
                Icons.ARROW_CIRCLE_DOWN,
                icon_color=Colors.WHITE,
                key=f"modules:{module_id}",
                data=f"{_key}:{_id}",
                on_click=lambda e, mid=module_id: _move_module_down(e, mid),
            )
            _delete = IconButton(
                Icons.REMOVE_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"modules:{module_id}",
                data=f"{_key}:{_id}",
                on_click=callback,
            )
            _iconRow.controls.extend([_up, _down, _delete])
        else:
            _add = IconButton(
                Icons.ADD_CIRCLE,
                icon_color=Colors.WHITE,
                key=f"modules:{module_id}",
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
            key=f"modules:{module['id']}",
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
            _template = [_e for _e in _projectData[_key] if _e["id"] == _id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError("A000")
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
            _template = [_e for _e in _projectData[_key] if _e["id"] == _id]
            assert _template, getError("A000")
            _template = _template[0]
            assert _template, getError("A000")
            _template["modules"].insert(current_index + 1, _template["modules"].pop(current_index))
            registry.changed = True
            registry.project.status = "Changed"
            updateWindowTitle(e.page, registry.projectName + "*")
            updateWindowState(e.page, registry.changed)
            activate_save_button()

    def _refresh_template_view(data_: dict) -> None:
        # Remove the old view
        registry.subjects["contentView"].notify(registry.page, [])
        _create_template_view(data_)

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
            module_data = [m for m in _projectData["modules"] if m["id"] == module_id][0]
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
            module_data = [m for m in _projectData["modules"] if m["id"] == module_id][0]
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
        module_data = [m for m in _projectData["modules"] if m["id"] == module_id][0]
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


def _switchToEditModeForModule(_control, _data) -> None:
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


def handleContentActions(subject: str, e_: ControlEvent, action: ContentAction = None) -> None:
    """Handle click events based on the action."""

    _page = e_.page
    assert _page, getError("A000")
    _control = e_.control
    assert _control, getError("A000")
    _parent = _control.parent
    assert _parent, getError("A000")
    _id = None
    _key = _control.key
    assert _key, getError("A000")
    if ":" in _key:
        _key, _id = _key.split(":")
        
    _data = _control.data
    assert _data, getError("A000")
    _action = action
    if not _action:
        _action = _control.data

    print(f"Action '{_action}' triggered for subject {subject} with key {_key} and data {_data}")

    match _action:
        case ContentAction.Edit:
            match _key:
                case "meetings":
                    if not _id:
                        if isinstance(_data, ListView):
                            _key, _id = _data.data.split(":")

                        if not _id:
                            print('Problem getting template id')
                            return

                    return _switchToEditModeForMeeting(_control, _key, _id)

                case "templates":
                    if not _id:
                        if isinstance(_data, ListView):
                            _key, _id = _data.data.split(":")

                        if not _id:
                            print('Problem getting template id')
                            return
                            
                    return _switchToEditModeForTemplate(_control, _key, _id)

                case "modules":
                    return _switchToEditModeForModule(_control, _data)
                    
                case _:
                    print("Unknown key for Edit")

        case ContentAction.Ok:
            _headline = _data.controls[0]
            assert _headline, getError("A000")
            _content = _data.controls[1]
            assert _content, getError("A000")
            _parent = _control.parent
            assert _parent, getError("A000")
            _projectEntry = _data.data
            assert _projectEntry, getError("A000")
            _currentKey, _currentId = _projectEntry.split(":")
            assert _currentKey, getError("A000")
            assert _currentId, getError("A000")
            _projectData = registry.project.data
            assert _projectData, getError("A000")
            _element = [_e for _e in _projectData[_currentKey] if _e["id"] == _currentId]
            assert _element, getError("A000")
            _element = _element[0]
            _element["headline"] = _headline.value
            _element["content"] = _content.value

            _headline.read_only = True
            _headline.autofocus = False
            _headline.border_color = Colors.GREY_500
            _content.read_only = True
            _content.border_color = Colors.GREY_500
            _data.update()
            for _child in _parent.controls:
                _child.visible = False

            _parent.controls[0].visible = True
            _parent.update()
            registry.project.status = "Changed"
            registry.changed = True
            updateWindowTitle(_page, registry.projectName + "*")
            updateWindowState(_page, registry.changed)

        case ContentAction.Cancel:
            match _key:
                case "modules":
                    _headline = _data.controls[0]
                    assert _headline, getError("A000")
                    _content = _data.controls[1]
                    assert _content, getError("A000")

                    _headline.read_only = True
                    _headline.autofocus = False
                    _headline.border_color = Colors.GREY_500
                    _content.read_only = True
                    _content.border_color = Colors.GREY_500
                    _data.update()
                    for _child in _parent.controls:
                        _child.visible = False

                    _parent.controls[0].visible = True
                    _parent.update()

                case _:
                    print("Unknown key for Cancel")

        case ContentAction.RenderToPreview:
            #print("Render")
            _, _id = _data.data.split(":")
            assert _id, getError("A000")        
            _projectData = registry.project.data
            assert _projectData, getError("A000")

            _text = render_meeting(_id, _projectData)
            _dlg = AlertDialog(
                title=Text(f"Preview Meeting"),
                content=Column(
                    controls=[
                        Row(
                            controls=[
                                Container(
                                    content=TextField(
                                        _text,
                                        multiline=True,
                                        min_lines=1,
                                        max_lines=400,
                                        read_only=True,
                                        autofocus=False,
                                    ),
                                    border=border.all(2, Colors.GREY_500),
                                    border_radius=5,
                                    padding=5,
                                    expand=True,
                                    width=800,
                                ),
                            ],
                            expand=True,
                        ),
                    ],
                    alignment="end",
                    expand=True,
                ),
                actions=[
                    ElevatedButton("Close", key=_id, on_click=lambda e: e.page.close(_dlg)),
                ],
                actions_alignment="end",
            )

            _control.page.open(_dlg)

        case ContentAction.RenderToClipboard:
            _, _id = _data.data.split(":")
            assert _id, getError("A000")
            _projectData = registry.project.data
            assert _projectData, getError("A000")
            
            markdown_output = render_meeting(_id, _projectData)
            _page.set_clipboard(markdown_output)

        case ContentAction.RenderToFile:
            _key, _id = _data.data.split(":")
            assert _key, getError("A000")
            assert _id, getError("A000")
            _projectData = registry.project.data
            assert _projectData, getError("A000")
            
            registry.renderedText = render_meeting(_id, _projectData)
            _meeting = [_e for _e in registry.project.data[_key] if _e["id"] == _id]
            assert _meeting, getError("A000")
            _meeting = _meeting[0]
            assert _meeting, getError("A000")
            _filename = f"{_meeting['name']}"
            showSave(_page, setProjectState, ProjectState.RENDERED, {"folder": "C:\\Data\\work", "filename": f"agenda-{_meeting["kind"].lower().replace(" ", "-")} - {_filename}"})

        case ContentAction.Delete:
            confirmDialog.show(_page, lambda: handleContentActions("contentActions", e_, ContentAction.DoDelete))

        case ContentAction.DoDelete:
            _projectData = registry.project.data
            assert _projectData, getError("A000")
            match _key:
                case "meetings"|"templates"|"modules":
                    _projectData[_key].remove(_data)
                    project.refresh(registry.project)
                    registry.project.status = "Changed"
                    registry.changed = True
                    updateWindowTitle(_page, registry.projectName + "*")
                    updateWindowState(_page, registry.changed)
                    
                case _:
                    print("Unknown key for Delete")
        
        case ContentAction.Copy:
            _projectData = registry.project.data
            assert _projectData, getError("A000")
            match _key:
                case "templates":
                    _state = ProjectState.ADDTEMPLATE
                    _template = [_e for _e in _projectData["templates"] if _e["id"] == _id]
                    assert _template, getError("A000")
                    _template = _template[0]
                    assert _template, getError("A000")
                    _name = _template.get("name", "")
                    _description = _template.get("description", "")

                case "modules":
                    _state = ProjectState.ADDMODULE
                    _module = [_e for _e in _projectData["modules"] if _e["id"] == _id]
                    assert _module, getError("A000")
                    _module = _module[0]
                    assert _module, getError("A000")
                    _name = _module.get("name", "")
                    _description = _module.get("description", "")
                    
                case "meetings":
                    _state = ProjectState.ADDMEETING
                    _meeting = [_e for _e in _projectData["meetings"] if _e["id"] == _id]
                    assert _meeting, getError("A000")
                    _meeting = _meeting[0]
                    assert _meeting, getError("A000")
                    _name = _meeting.get("name", "")
                    _description = _meeting.get("description", "")
                    
                case _:
                    print("Unknown key for Copy")
                    return

            _values = {
                "id": None,
                "type": _key,
                "name": f"Copy: {_name}",
                "description": f"Copy: {_description}"
            }
            setProjectState(_page, _state, _values)
            _item = [(_i,_e) for _i, _e in enumerate(_projectData[_key]) if _e["name"] == f"Copy: {_name}"]
            assert _item, getError("A000")
            _item = _item[0]
            assert _item, getError("A000")
            _index = _item[0]
            assert _index >= 0, getError("A000")
            _item = _item[1]
            assert _item, getError("A000")
            match _key:
                case "templates":
                    _item["modules"] =  _template["modules"].copy()

                case "modules":
                    _item["headline"] = "Copy:" + _module["headline"]
                    _item["content"] = _module["content"]

                case "meetings":
                    _item["tops"] = _meeting["tops"].copy()

                case _:
                    print("Unknown key for Copy")
                    return

            _projectData[_key][_index] = _item
            project.refresh(registry.project)
            _newKey = f"{_key}:{_item['id']}"
            _control = registry.project.controls[_newKey]
            _control.key = _newKey
            _e = ControlEvent("add", "??", data=_key, control=_control, page=_page)
            _select_project_item(_e, _newKey, True)

        case _:
            print(f"Unknown action {_action}")


def setProjectState(page: Page, state_: ProjectState=None, values_: dict=None) -> None:
    """ Set Project State """

    if not validate_values({"page": page, "state": state_, "project": registry.project}, validations0):
        return

    try:
        _project = registry.project
        match state_:
            case ProjectState.ADDTEMPLATE | ProjectState.ADDMODULE | ProjectState.ADDMEETING:
                if not validate_values(values_, validations2):
                    return

                # Generate unique ID based on existing templates
                current_ids = [int(t["id"]) for t in _project.data[values_["type"]] if t["id"].isdigit()]
                new_id = str(max(current_ids) + 1) if current_ids else "1"

                # Create new template
                values_['id'] = new_id
                for _item in FIELDS[state_]:
                    values_[f"{_item[0]}"] = _item[1]

                #values_['modules'] = []
                _project.data[values_["type"]].append(values_)
                project.refresh(_project)

                _newKey = f"{values_['type']}:{new_id}"
                _control = registry.project.controls[_newKey]
                _control.key = _newKey
                _e = ControlEvent("add", "??", data=_control.key, control=_control, page=page)
                _select_project_item(_e, _newKey)

                registry.changed = True
                _project.status = "Changed"
                updateWindowTitle(page, registry.projectName + "*")
                updateWindowState(page, registry.changed)

            case ProjectState.RENAMED:
                if not validate_values(values_, validations1):
                    return

                _name = values_["name"]
                _id = values_["id"]
                _type = values_["type"]
                match _type:
                    case "templates":
                        _data = _project.get_template(_id)
                        assert _data, getError("A000")
                        
                        for _key, _value in values_.items():
                            _data[_key] = _value
                        
                        _ctrl = _project.controls[f'{_type}:{_id}']
                        assert _ctrl, getError("A000")
                        
                        _ctrl.controls[0].value = _name[0:35] + "" if len(_name) < 35 else "..."
                        _ctrl.update()
                        project.refresh(registry.project)

                    case "modules":
                        _data = _project.get_module(_id)
                        assert _data, getError("A000")
                        
                        for _key, _value in values_.items():
                            _data[_key] = _value
                        
                        _ctrl = _project.controls[f'{_type}:{_id}']
                        assert _ctrl, getError("A000")
                        
                        _ctrl.controls[0].value = _name[0:35] + "" if len(_name) < 35 else "..."
                        _ctrl.update()
                        project.refresh(registry.project)

                    case "meetings":
                        _data = _project.get_meeting(_id)
                        assert _data, getError("A000")
                        
                        for _key, _value in values_.items():
                            if _key == "tops":
                                continue
                            
                            _data[_key] = _value
                        
                        _ctrl = _project.controls[f'{_type}:{_id}']
                        assert _ctrl, getError("A000")
                        
                        _ctrl.controls[0].value = _name[0:35] + "" if len(_name) < 35 else "..."
                        _ctrl.update()
                        project.refresh(registry.project)

                    case _:
                        print(f"Unknown {_type} for Rename")
                        return
                
                registry.changed = True
                _project.status = "Changed"
                updateWindowTitle(page, registry.projectName + "*")
                updateWindowState(page, registry.changed)
            
            case ProjectState.RENDERED:
                if registry.renderedText and values_["path"]:
                    with open(values_["path"], "w") as tf:
                        tf.writelines(registry.renderedText)

                return

            case _:
                print("Unknown state")
                return

    except Exception as _e:
        print(_e)
