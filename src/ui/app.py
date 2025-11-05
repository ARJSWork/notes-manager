###
# File:   src\ui\app.py
# Date:   2025-01-22 / 10:56
# Author: alexrjs
###


# imports
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

from flet import (
    app, alignment, border, Icons, Colors, 
    Control, Column, Container, 
    Page, Row, Stack, IconButton, 
    Text, ScrollMode, WindowDragArea
)
from db import register, registry
from logic.pattern.observer import ObservablesList
from logic.ui.menu import new_callback, open_callback, save_callback, handle_menu_item_click
from ui.panels import menu, content, status
from ui.views import sidebar

# constants


# variables


# functions/classes
def _handle_keyboard_event(e) -> None:
    """Central keyboard handler for common shortcuts and keys."""
    try:
        logging.info(f"Key event: {getattr(e,'key',None)} data={getattr(e,'data',None)} ctrl={getattr(e,'ctrl_key',False)} meta={getattr(e,'meta_key',False)}")
        _global = not registry.shortcut_control
        key = getattr(e, "key", None)
        k = key.lower()
        _ctrl_key = getattr(e, "ctrl", False)
        ctrl_or_cmd = bool(_ctrl_key or getattr(e, "meta", False))

        # Common Ctrl/Cmd shortcuts
        if _global and ctrl_or_cmd and key:
            if k == "n" and not registry.ui.menu.file.new.disabled:
                registry.subjects["ui.menu.file.new"].notify(e)
            elif k == "o" and not registry.ui.menu.file.open.disabled:
                registry.subjects["ui.menu.file.open"].notify(e)
            elif k == "s":
                registry.subjects["ui.menu.file.save"].notify(e)
            elif k == "c":
                registry.subjects["ui.menu.file.close"].notify(e)
            elif k == "q":
                registry.subjects["ui.menu.file.quit"].notify(e)

            # mark handled where supported
            if hasattr(e, "handled"):
                e.handled = True

            return

        elif _ctrl_key and k:
            # Check for note-specific keyboard handler
            if hasattr(registry, "keyboard_handler") and callable(registry.keyboard_handler):
                registry.keyboard_handler(f"ctrl+{k}")
                return

        # # Single-key actions
        # if key == "Escape":
        #     # Clear content selection / reset content view if present
        #     if "contentView" in registry.subjects:
        #         # notify with empty content (matches updateContent signature used elsewhere)
        #         registry.subjects["contentView"].notify(e.page, [])
        #     if hasattr(e, "handled"):
        #         e.handled = True
        #     return

        # if key == "F1":
        #     registry.subjects["ui.menu.file.about"].notify(e)
        #     if hasattr(e, "handled"):
        #         e.handled = True
        #     return

    except Exception as ex:
        logging.exception("Error handling keyboard event: %s", ex)


def layout(page_:Page) -> list:
    """Content of the page"""

    def updateContent(caller, page, items_:list[Control]) -> None:
        if not _col2:
            return

        if registry.editing:
            _cont2.bgcolor = Colors.WHITE10
            _cont2.border = border.all(5, Colors.RED)
        else:
            _cont2.bgcolor = Colors.GREY_700
            _cont2.border = None

        _cont2.alignment = alignment.top_center if items_ else alignment.center
        if not items_:
            items_ = [Text("Choose a notes collection with 'File Menu'...", size=16, color=Colors.WHITE)]

        _cont2.update()
        _col2.controls.clear()
        _col2.controls.extend(items_)
        _col2.update()

    _border = border.all(1, Colors.WHITE24)

    _col1 = Column(
        controls=[
            sidebar.build(page_)
        ],
        width=400,
        scroll=ScrollMode.AUTO,
    )
    _cont1 = Container(
        alignment=alignment.top_left,
        border=_border,
        padding=2,
        bgcolor=Colors.GREY_800,
        content=_col1,
    )
    # Hide sidebar initially if no notes collection is open
    sidebar_visible = bool(getattr(registry, 'notesFile', None) or getattr(registry, 'notesName', None))
    _cont1.visible = sidebar_visible
    # Register the sidebar container so other code (menu state) can show/hide it
    register("ui.sidebar.container", _cont1)
    _col2 = Stack(
        controls=[
            Text("Choose a notes collection with 'File Menu'...", size=16, color=Colors.WHITE),
        ],
        alignment=alignment.center,
        expand=True,
    )
    _cont2 = Container(
        alignment=alignment.center,
        border=_border,
        expand=True,
        padding=5,
        bgcolor=Colors.GREY_700,
        content=_col2,
    )
    registry.subjects.register("contentView").register(updateContent)
    # registry.subjects.register("contentActions").register(handleContentActions)
    # registry.subjects.register("noteView").register(handleClick)

    return [_cont1, _cont2]


def ui(page_:Page) -> None:
    """ Build UI """

    if not page_:
        logging.error("Error: No page")
        quit(-1)

    # Set registry values
    register("changed", False)

    # Do Flet stuff
    page_.title = "Notes Manager"
    page_.padding = 0
    page_.spacing = 0
    page_.window.title_bar_hidden = True
    page_.window.maximized = True
    page_.window.icon = "assets/icon.ico"
    page_.window.center()

    # Do Layout stuff
    register("page", page_)
    register("subjects", ObservablesList("subjects"))
    register("note", None)
    register("ui.menuBar", menu.build())

    # Do Layout stuff
    if not page_.web:
        _mbContainer = Container(
            Row([
                WindowDragArea(Container(registry.ui.menuBar, padding=0), expand=True),
                IconButton(Icons.CLOSE, icon_color=Colors.WHITE, on_click=lambda e: registry.subjects["ui.menu.file.quit"].notify(e))
            ]), 
            bgcolor=Colors.BLUE_700
        )

    else:
        _mbContainer = Container(registry.ui.menuBar, bgcolor=Colors.GREEN_700, padding=0)
        
    page_.add(_mbContainer)
        
    register("ui.dragBar", _mbContainer)
    registry.subjects["ui.menu.file.new"].register(new_callback)
    registry.subjects["ui.menu.file.open"].register(open_callback)
    registry.subjects["ui.menu.file.save"].register(save_callback)
    registry.subjects["ui.menu.file.close"].register(handle_menu_item_click)
    registry.subjects["ui.menu.file.about"].register(handle_menu_item_click)
    registry.subjects["ui.menu.file.quit"].register(handle_menu_item_click)
    register("ui.contentBar", content.build(layout(page_)))
    page_.add(registry.ui.contentBar)
    #page_.add(register("ui.statusBar", status.build()))

    page_.on_keyboard_event = _handle_keyboard_event
    #status.updateStatus("Ready.")


def run(web:bool=False) -> None:
    """ Run program loop """

    if web:
        return app(target=ui, view="web_browser", web_renderer="html", assets_dir="assets", upload_dir="upload", port=8766, host="127.0.0.1")
    
    return app(target=ui, assets_dir="assets", upload_dir="upload")
