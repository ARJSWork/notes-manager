###
# File:   src\logic\ui\menu.py
# Date:   2025-01-27 / 12:17
# Author: alexrjs
###


# imports
from os import path
import logging
from enum import Enum
from flet import ControlEvent, Page, Icon, Colors, Text
from config.config import DATA_ROOT
from db import register, registry
from logic.persistence import save_notes
from db.handler import create_default_collection, load_notes_collection
from db.messages import getError
from logic.ui import ContentAction, NoteState
from logic.ui.window import updateWindowState, updateWindowTitle, WindowState
from ui.dialogs import confirm as confirmDialog
from ui.dialogs import file as fileDialog
from ui.dialogs import notescollection as notesCollectionDialog
from ui.views import sidebar


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

    except Exception as _e:
        logging.exception("handle_menu_item_click: assertion failed")
        return
    
    logging.debug(f"{event}.on_action")

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
            logging.warning(f"Unknown event: {event}")


def new_callback(event:str, e:ControlEvent) -> None:
    """New notes collection"""
    
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")

    except Exception as _e:
        logging.exception("handle_menu_item_click: assertion failed")
        return

    e.page.update()
    logging.debug(f"{event}.on_click")

    # Rufe den Open File Dialog auf
    notesCollectionDialog.show(e.page, setMenuState, MenuState.NEW)


def open_callback(event:str, e:ControlEvent) -> None:
    """Open a file"""
    
    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")

    except Exception as _e:
        logging.exception("open_callback: assertion failed")
        return

    e.page.update()
    logging.debug(f"{event}.on_click")

    # Rufe den Open File Dialog auf
    fileDialog.showOpenCollection(e.page, setMenuState, MenuState.OPENED)


def save_callback(event:str, e: ControlEvent) -> None:
    """Save a file"""

    try:
        assert e.page, getError("U001")
        assert e.control, getError("U002")

    except Exception as _e:
        logging.exception("handle_menu_item_click: assertion failed")
        return

    e.page.update()
    logging.debug(f"{event}.on_click")

    # Rufe den Open File Dialog auf
    setMenuState(e.page, MenuState.SAVED)


# def saveAsCallback(event:str, e: ControlEvent) -> None:
#     """Save a file"""

#     try:
#         assert e.page, getError("U001")
#         assert e.control.content, getError("U003")

#     except Exception as _e:
#         logging.exception("saveAsCallback: assertion failed")
#         return

#     e.page.update()
#     logging.debug(f"{event}.on_click")

#     # Rufe den Open File Dialog auf
#     fileDialog.showSave(e.page, setMenuState, MenuState.SAVED)


def setMenuState(page:Page, state_:MenuState=None) -> None:
    """Set the menu states"""

    match state_:

        case MenuState.NEW:
            logging.info("Menu is new")
            collection = create_default_collection(registry.notesName)
            register("notes_collection", collection)
            register("notesFileRoot", DATA_ROOT)
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            registry.changed = True
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, WindowState.Changed)
            registry.subjects["contentView"].notify(page, [])
            page.window.to_front()

            # Show sidebar container if registered
            registry.ui.sidebar.container.visible = True
            page.update()

            # Enable Add buttons but keep Edit/Delete disabled until selection
            try:
                registry.ui.sidebar.MeetingNotes.add.disabled = False
                registry.ui.sidebar.MeetingNotes.edit.disabled = True
                registry.ui.sidebar.MeetingNotes.delete.disabled = True
                if registry.ui.sidebar.Templates:
                    registry.ui.sidebar.Templates.add.disabled = False
                    registry.ui.sidebar.Templates.edit.disabled = True
                    registry.ui.sidebar.Templates.delete.disabled = True
                if registry.ui.sidebar.Modules:
                    registry.ui.sidebar.Modules.add.disabled = False
                    registry.ui.sidebar.Modules.edit.disabled = True
                    registry.ui.sidebar.Modules.delete.disabled = True
                if registry.ui.sidebar.Categories:
                    registry.ui.sidebar.Categories.add.disabled = False
                    registry.ui.sidebar.Categories.edit.disabled = True
                    registry.ui.sidebar.Categories.delete.disabled = True

                page.update()

            except Exception:
                pass

        case MenuState.OPENED:
            logging.info("Menu is opened")
            collection = load_notes_collection(registry.notesFileRoot)
            register("notes_collection", collection)
            register("notesFile", path.join(registry.notesFileRoot, "collection.json"))
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            registry.changed = False
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, WindowState.Saved)
            registry.subjects["contentView"].notify(page, [])
            page.window.to_front()

            # Show sidebar container if registered
            registry.ui.sidebar.container.visible = True
            page.update()

            # Populate Meeting Notes list from loaded collection (delegated to sidebar)
            try:
                sidebar.populate_meeting_notes(page, collection)
            except Exception:
                logging.exception('Failed to populate MeetingNotes via sidebar.populate_meeting_notes')

            # Enable Add buttons but keep Edit/Delete disabled until selection
            try:
                registry.ui.sidebar.MeetingNotes.add.disabled = False
                registry.ui.sidebar.MeetingNotes.edit.disabled = True
                registry.ui.sidebar.MeetingNotes.delete.disabled = True
                # Also enable templates/modules/categories add buttons
                if registry.ui.sidebar.Templates:
                    registry.ui.sidebar.Templates.add.disabled = False
                    registry.ui.sidebar.Templates.edit.disabled = True
                    registry.ui.sidebar.Templates.delete.disabled = True
                if registry.ui.sidebar.Modules:
                    registry.ui.sidebar.Modules.add.disabled = False
                    registry.ui.sidebar.Modules.edit.disabled = True
                    registry.ui.sidebar.Modules.delete.disabled = True
                if registry.ui.sidebar.Categories:
                    registry.ui.sidebar.Categories.add.disabled = False
                    registry.ui.sidebar.Categories.edit.disabled = True
                    registry.ui.sidebar.Categories.delete.disabled = True

                page.update()

            except Exception:
                pass
        
        case MenuState.CLOSED:
            logging.info("Menu is closed")
            registry.ui.menu.file.new.disabled = False
            registry.ui.menu.file.open.disabled = False
            registry.ui.menu.file.save.disabled = True
            registry.ui.menu.file.close.disabled = True
            #registry.ui.menu.manage.visible = False
            #registry.ui.categoryFilter.visible = False
            registry.notesFile = None
            registry.notesName = None
            registry.changed = False
            registry.note = None
            updateWindowTitle(page, registry.notesName)
            updateWindowState(page, WindowState.Initial)
            #notes.clear()
            registry.subjects["contentView"].notify(page, [])
            page.window.to_front()

            # Disable sidebar buttons on close
            try:
                registry.ui.sidebar.MeetingNotes.add.disabled = True
                registry.ui.sidebar.MeetingNotes.edit.disabled = True
                registry.ui.sidebar.MeetingNotes.delete.disabled = True
                if registry.ui.sidebar.Templates:
                    registry.ui.sidebar.Templates.add.disabled = True
                    registry.ui.sidebar.Templates.edit.disabled = True
                    registry.ui.sidebar.Templates.delete.disabled = True
                if registry.ui.sidebar.Modules:
                    registry.ui.sidebar.Modules.add.disabled = True
                    registry.ui.sidebar.Modules.edit.disabled = True
                    registry.ui.sidebar.Modules.delete.disabled = True
                if registry.ui.sidebar.Categories:
                    registry.ui.sidebar.Categories.add.disabled = True
                    registry.ui.sidebar.Categories.edit.disabled = True
                    registry.ui.sidebar.Categories.delete.disabled = True
            except Exception:
                pass

            # Hide sidebar container if no notes are open
            registry.ui.sidebar.container.visible = False
            page.update()

        case MenuState.SAVED:
            if registry.notes_collection:
                logging.warning("No collection loaded to save.")
                return

            if registry.changed:
                logging.warning("No changes to save.")
                return

            success, msg = save_notes(registry.notes_collection, DATA_ROOT)
            if success:
                registry.changed = False
                updateWindowTitle(page, registry.notesName)
                updateWindowState(page, WindowState.Saved)
                try:
                    # update status bar if present
                    if hasattr(registry, 'ui') and getattr(registry.ui, 'status', None):
                        registry.ui.status.current.value = "Save succeeded"
                        registry.ui.status.current.update()
                except Exception:
                    pass
                
                logging.info(msg)
            else:
                try:
                    if hasattr(registry, 'ui') and getattr(registry.ui, 'status', None):
                        registry.ui.status.current.value = f"Save failed: {msg}"
                        registry.ui.status.current.update()
                except Exception:
                    pass

                logging.error(f"Save failed: {msg}")
            
            # Re-enable menu items
            registry.ui.menu.file.new.disabled = True
            registry.ui.menu.file.open.disabled = True
            registry.ui.menu.file.save.disabled = False
            registry.ui.menu.file.close.disabled = False
            page.window.to_front()

        case _:
            logging.info("Menu is unknown")
            registry.ui.menu.file.new.disabled = False
            registry.ui.menu.file.open.disabled = False
            registry.ui.menu.file.save.disabled = True
            registry.ui.menu.file.close.disabled = True
            registry.changed = False
            updateWindowTitle(page, "")
            updateWindowState(page, WindowState.Changed)
