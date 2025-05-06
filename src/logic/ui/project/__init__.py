###
# File:   src\logic\ui\project\__init__.py
# Date:   2025-02-18 / 12:20
# Author: alexrjs
###


# imports
from flet import(
    ControlEvent, Colors, Container, Column, Page, IconButton, TextField, ElevatedButton, Row,
    ListView, Text, AlertDialog, border
)
from db import registry
from db.messages import getError
from logic.ui import ITEM_TYPE_MODULES, ITEM_TYPE_TEMPLATES, ContentAction, ProjectState
from logic.ui import module, template, meeting
from logic.ui.project.render import render_meeting
from logic.ui.project.utils import validate_values
from logic.ui.window import updateWindowTitle, updateWindowState
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
def setItemColors(key_: str = None, color_: str = Colors.WHITE, bgcolor_: str = None) -> None:
    """Resets item colors."""

    _currentKey = key_ if key_ else registry.ui.projectPanel.key
    assert _currentKey, getError("A000")

    _item = registry.project.controls[_currentKey]
    _item.controls[0].color = color_
    for _icon in _item.controls[1].controls:
        if isinstance(_icon, IconButton):
            _icon.icon_color = color_
        else:
            _icon.color = color_

    _item.parent.bgcolor = bgcolor_
    _item.parent.update()


def selectItem(e: ControlEvent, newKey_: str, override_: bool = False) -> None:
    """Selects an meeting item and updates the UI."""

    _panel = registry.ui.projectPanel
    _currentKey = _panel.key if _panel.key else "templates:1"
    if e.target != "initial" and (_currentKey == newKey_ and not override_):
        return

    # Check culprits
    _key, _id = newKey_.split(":")
    assert _key, getError("A000")
    assert _id, getError("A000")

    _projectData = registry.project.data
    assert _projectData, getError("A000")
    
    _data = [_e for _e in _projectData[_key] if _e["id"] == _id]
    assert _data, getError("A000")
    
    _data = _data[0]
    assert _data, getError("A000")

    setItemColors(_currentKey) # Reset
    setItemColors(newKey_, Colors.BLACK, Colors.AMBER) # Highlight
    _panel.key = newKey_ # Remember current key

    match _key: # delegate to specific handlers
        case "meetings":
            meeting.create_view(_data) # Call handler

        case "templates":
            template.create_view(_data) # Call handler

        case "modules":
            # TODO: Simplify
            module.create_view(e, _key, _id) # Call handler

        case _:
            # TODO: Better Error Message
            print(f"Unknown key {newKey_}")


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
            return selectItem(e, e.control.key)

        case "AddTemplate":
            _data = {
                "title": "Add a Template:",
                "id": None,
                "type": _key,
                "kind": "items",
                "callback": setProjectState,
                "state": ProjectState.ADDTEMPLATE
            }
            return handleAddItem(e, _data)

        case "AddModule":
            _data = {
                "title": "Add a Module:",
                "id": None,
                "type": _key,
                "kind": "items",
                "callback": setProjectState,
                "state": ProjectState.ADDMODULE
            }
            return handleAddItem(e, _data)

        case "AddMeeting":
            _data = {
                "title": "Add an Meeting:",
                "id": None,
                "type": _key,
                "kind": "datetype",
                "callback": setProjectState,
                "state": ProjectState.ADDMEETING
            }
            return handleAddItem(e, _data)

        case "Rename":
            return handleRenameItem(e, _key)
        
        case _:
            return


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
            match _key: # TODO: Use ITEM_TYPE constants
                case "meetings":
                    if not _id:
                        if isinstance(_data, ListView):
                            _key, _id = _data.data.split(":")

                        if not _id:
                            print('Problem getting template id')
                            return

                    # return OLD_switchToEditModeForMeeting(_control, _key, _id)
                    selectItem(e_, _control.key, True)
                    return meeting.switch_to_edit_mode(_control, _key, _id)

                case "templates":
                    if not _id:
                        if isinstance(_data, ListView):
                            _key, _id = _data.data.split(":")

                        if not _id:
                            print('Problem getting template id')
                            return
                            
                    # return OLD_switchToEditModeForTemplate(_control, _key, _id)
                    return template.switch_to_edit_mode(_control, _key, _id)

                case "modules":
                    # return _switchToEditModeForModule(_control, _data)
                    return module.switch_to_edit_mode(_control, _key, _id)
                    
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
                case "modules": # Only modules have direct text fields in this view
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
                case "meetings" | "templates" | "modules":
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
                    _template = [_e for _e in _projectData[ITEM_TYPE_TEMPLATES] if _e["id"] == _id]
                    assert _template, getError("A000")
                    _template = _template[0]
                    assert _template, getError("A000")
                    _name = _template.get("name", "")
                    _description = _template.get("description", "")

                case "modules":
                    _state = ProjectState.ADDMODULE
                    _module = [_e for _e in _projectData[ITEM_TYPE_MODULES] if _e["id"] == _id]
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
            selectItem(_e, _newKey, True)

        case _:
            print(f"Unknown action {_action}")


def handleRenameItem(e: ControlEvent, _: str) -> None:
    """Handle Rename"""
        
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.data, getError("A002")

    except Exception as _e:
        print(_e)
        return

    selectItem(e, e.control.key)

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


def handleAddItem(e: ControlEvent, data: str) -> None:
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
                selectItem(_e, _newKey)

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
