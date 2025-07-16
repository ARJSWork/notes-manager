###
# File:   src\ui\app.py
# Date:   2025-01-22 / 10:56
# Author: alexrjs
###


# imports
from flet import app, Control, Page, Row, IconButton, Column, Container, Text, ScrollMode, WindowDragArea, Stack, StackFit
from flet import MainAxisAlignment, Icons, Colors, border, alignment
from db import register, registry
from logic.pattern.observer import ObservablesList
from logic.ui.menu import new_callback, open_callback, save_callback, handle_menu_item_click
from ui.panels import menu, content, status
from ui.views import sidebar

# constants


# variables


# functions/classes
def layout() -> list:
    """Content of the page"""

    def updateContent(caller, page, items_:list[Control]) -> None:
        if not _col2:
            return

        _col2.controls.clear()
        _col2.controls.extend(items_)
        _col2.update()

    _border = border.all(1, Colors.WHITE24)

    _col1 = Column(
        controls=[
            sidebar.build()
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
    _col2 = Stack(
        controls=[
            Text("Choose a notes collection with 'File Menu'...", size=16, color=Colors.WHITE),
        ],
        alignment=alignment.center,
        expand=True,
    )
    # _col2 = Column(
    #     controls=[
    #         Text("Choose a Notes with 'File Menu'...", size=16, color=Colors.WHITE),
    #     ],
    #     alignment=MainAxisAlignment.CENTER,
    #     expand=True,
    # )
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
        print("Error: No page")
        quit(-1)

    # Set registry values
    register("changed", False)

    # Do Flet stuff
    page_.title = "Agenda Manager"
    page_.padding = 0
    page_.spacing = 0
    page_.window.title_bar_hidden = True
    page_.window.maximized = True
    page_.window.center()

    # Do Layout stuff
    register("page", page_)
    register("subjects", ObservablesList("subjects"))
    register("note", None)
    register("ui.menuBar", menu.build())

    # Do Layout stuff
    #IconButton(Icons.CLOSE, icon_color=Colors.WHITE, on_click=lambda _: page_.window.close())
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
    register("ui.contentBar", content.build(layout()))
    page_.add(registry.ui.contentBar)
    #page_.add(register("ui.statusBar", status.build()))

    # Finish up
    #status.updateStatus("Ready.")


def run() -> None:
    """ Run program loop """

    # return app(basicDemoUi)
    return app(ui)
