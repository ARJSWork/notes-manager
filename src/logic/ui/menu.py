###
# File:   src\logic\ui\menu.py
# Date:   2025-01-27 / 12:17
# Author: alexrjs
###


# imports
from enum import Enum
from flet import ControlEvent, Page, Icon, Colors, Text
from db import register, registry #, create_default_collection, save_notes_collection, load_notes_collection
from db.messages import getError
from logic.ui import ContentAction, NoteState
from logic.ui.window import updateWindowState, updateWindowTitle
from ui.dialogs import confirm as confirmDialog
from ui.dialogs import file as fileDialog
from ui.dialogs import notescollection as notesCollectionDialog


# constants
class MenuState(Enum):
    OPENED = "opened"
    CLOSED = "closed"
    SAVED = "saved"
    NEW = "new"


# variables


# functions/classes
def handle_menu_item_click(event:str, e:ControlEvent) -> None:
    """Handle the menu item click event"""

    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        #assert e.control.content, getError("U003")

    except Exception as _e:
        print(_e)
        return
    
    e.page.update()

    _element = e.control.content
    if _element and isinstance(_element, Icon):
        print(f"{event}.{_element.key}.on_click")

    else:
        print(f"{event}.on_click")

    match event:
        case "Quit"|"ui.menu.file.quit":
            if registry.changed:
                confirmDialog.show(e.page, lambda: e.page.window.destroy())
            
            else:
                e.page.window.destroy()

        case "Close"|"ui.menu.file.close":
            if registry.changed:
                confirmDialog.show(e.page, lambda: setMenuState(e.page, MenuState.CLOSED))
            
            else:
                setMenuState(e.page, MenuState.CLOSED)

        case _:
            print(f"Unknown event: {event}")


def new_callback(event:str, e:ControlEvent) -> None:
    """Open a file"""
    
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.content, getError("U003")

    except Exception as _e:
        print(_e)
        return

    e.page.update()

    _element = e.control.content
    print(f"{_element.value}.on_click")

    # Rufe den Open File Dialog auf
    notesCollectionDialog.show(e.page, setMenuState, MenuState.NEW)


def open_callback(event:str, e:ControlEvent) -> None:
    """Open a file"""
    
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.content, getError("U003")

    except Exception as _e:
        print(_e)
        return

    e.page.update()

    _element = e.control.content
    print(f"{_element.value}.on_click")

    # Rufe den Open File Dialog auf
    fileDialog.showOpen(e.page, setMenuState, MenuState.OPENED)


def save_callback(event:str, e: ControlEvent) -> None:
    """Save a file"""

    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.content, getError("U003")

    except Exception as _e:
        print(_e)
        return

    e.page.update()

    _element = e.control.content
    print(f"{_element.value}.on_click")

    # Rufe den Open File Dialog auf
    setMenuState(e.page, MenuState.SAVED)


def saveAsCallback(event:str, e: ControlEvent) -> None:
    """Save a file"""

    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")
        assert e.control.content, getError("U003")

    except Exception as _e:
        print(_e)
        return

    e.page.update()

    _element = e.control.content
    print(f"{_element.value}.on_click")

    # Rufe den Open File Dialog auf
    fileDialog.showSave(e.page, setMenuState, MenuState.SAVED)


def setMenuState(page:Page, state_:MenuState=None) -> None:
    """Set the menu states"""

    match state_:

        case MenuState.OPENED:
            print("Menu is opened")
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            registry.ui.menu.manage.visible = True
            registry.changed = False
            #register("note", notesmanager(registry.notesFile))
            registry.note.load()
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, registry.changed)
            # Update
            #notes.refresh(registry.note, "all")
            # registry.ui.categoryFilter.visible = True
            # _control = registry.note.controls["templates:1"]
            # _control.key = "templates:1"
            # _e = ControlEvent("initial", "??", data=_control.key, control=_control, page=page)
            # registry.subjects["contentActions"].notify(_e, NoteState.SELECTED)
            # registry.subjects["noteView"].notify(_e, NoteState.SELECTED)
            registry.subjects["contentView"].notify(page, [])
            page.window.to_front()
        
        case MenuState.CLOSED:
            print("Menu is closed")
            registry.ui.menu.file.new.disabled = False
            registry.ui.menu.file.open.disabled = False
            registry.ui.menu.file.save.disabled = True
            registry.ui.menu.file.close.disabled = True
            registry.ui.menu.manage.visible = False
            registry.ui.categoryFilter.visible = False
            registry.notesFile = None
            registry.notesName = None
            registry.changed = False
            registry.note = None
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, registry.changed)
            #notes.clear()
            registry.subjects["contentView"].notify(page, [Text("Choose a notes collection with 'File Menu'...", size=16, color=Colors.WHITE)])
            page.window.to_front()

        case MenuState.SAVED:
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            registry.changed = False
            #save_notes_collection(registry.note, registry.notesFile)
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, registry.changed)
            print("Menu is saved")
            page.window.to_front()

        case MenuState.NEW:
            print("Menu is new")
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            registry.changed = True
            #register("note", create_default_collection(registry.notesName))
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, registry.changed)
            # Update
            #notes.refresh(registry.note, "all")
            # registry.ui.categoryFilter.visible = True
            registry.subjects["contentView"].notify(page, [])
            page.window.to_front()

        case _:
            print("Menu is unknown")
            registry.ui.menu.file.new.disabled = False
            registry.ui.menu.file.open.disabled = False
            registry.ui.menu.file.save.disabled = True
            registry.ui.menu.file.close.disabled = True
            registry.changed = False
            updateWindowTitle(page, "")
            updateWindowState(page, registry.changed)
