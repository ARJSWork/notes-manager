###
# File:   src\ui\bars\menu.py
# Date:   2025-01-22 / 12:09
# Author: alexrjs
###


# imports
from flet import MenuBar, MenuItemButton, SubmenuButton, Icon, Text, Divider, Row
from flet import alignment, ButtonStyle, Colors, ControlState, MenuStyle, MouseCursor, Icons, RoundedRectangleBorder
from db import register, registry
#from logic.pattern.observer import Observable, Observer


# constants


# variables


# functions/classes
def handle_submenu_hover(e):
    assert(e.page)
    assert(e.control)
    assert(e.control.content)
    
    print(f"{e.control.content.value}.on_hover")


def build(**kwargs) -> Row:
    """ Build UI """

    _page = registry.page
    if not _page:
        print("Error. No page registered")
        return None

    # _style=ButtonStyle(
    #     bgcolor={ControlState.HOVERED: Colors.GREY_700},
    # )
    _style = ButtonStyle(
        bgcolor={ControlState.HOVERED: Colors.GREEN_700},
        shape=RoundedRectangleBorder(radius=1),
        padding=10,
    )

    register("ui.noteTitle", Text("Notes: ", color=Colors.BLACK))

    _quit = MenuItemButton(
        content=Text("Quit"),
        leading=Icon(Icons.EXIT_TO_APP),
        style=_style,
        on_click=lambda e: registry.subjects["ui.menu.file.quit"].notify(e),
    )
    _menubar = MenuBar(
        expand=True,
        style=MenuStyle(
            alignment=alignment.center,
            elevation=0,
            bgcolor=Colors.BLUE_700,
            padding=0,
            mouse_cursor={
                ControlState.HOVERED: MouseCursor.WAIT,
                ControlState.DEFAULT: MouseCursor.ZOOM_OUT,
            },
            shape=RoundedRectangleBorder(radius=1)
        ),

        controls=[
            MenuItemButton(
                content=Icon(Icons.MENU_OUTLINED, key="drawer"),
                style=_style,
                #on_click=lambda e: registry.subjects["ui.menu.drawer"].notify(e),
            ),
            _smb := SubmenuButton(
                content=Text("File"),
                # on_open=handle_submenu_open,
                # on_close=handle_submenu_close,
                # on_hover=handle_submenu_hover,
                controls=[
                    MenuItemButton(
                        content=Text("New"),
                        leading=Icon(Icons.CREATE_NEW_FOLDER),
                        style=_style,
                        on_click=lambda e: registry.subjects["ui.menu.file.new"].notify(e),
                    ),
                    MenuItemButton(
                        content=Text("Open"),
                        leading=Icon(Icons.FILE_OPEN),
                        style=_style,
                        key="ui.menu.file.open",
                        on_click=lambda e: registry.subjects[e.control.key].notify(e),
                    ),
                    MenuItemButton(
                        content=Text("Save"),
                        leading=Icon(Icons.SAVE),
                        style=_style,
                        disabled=True,
                        on_click=lambda e: registry.subjects["ui.menu.file.save"].notify(e),
                    ),
                    MenuItemButton(
                        content=Text("Close"),
                        leading=Icon(Icons.CLOSE),
                        style=_style,
                        disabled=True,
                        on_click=lambda e: registry.subjects["ui.menu.file.close"].notify(e),
                    ),
                    Divider(height=9, thickness=3),
                    MenuItemButton(
                        content=Text("About"),
                        leading=Icon(Icons.INFO),
                        style=_style,
                        on_click=lambda e: registry.subjects["ui.menu.file.about"].notify(e),
                    ),
                ],
            ),
            # SubmenuButton(
            #     content=Text("View"),
            #     # on_open=handle_submenu_open,
            #     # on_close=handle_submenu_close,
            #     # on_hover=handle_submenu_hover,
            #     controls=[
            #         SubmenuButton(
            #             content=Text("Zoom"),
            #             controls=[
            #                 MenuItemButton(
            #                     content=Text("Magnify"),
            #                     leading=Icon(Icons.ZOOM_IN),
            #                     close_on_click=False,
            #                     style=_style,
            #                     on_click=lambda e: registry.subjects["ui.menu.view.zoom.magnify"].notify(e),
            #                 ),
            #                 MenuItemButton(
            #                     content=Text("Minify"),
            #                     leading=Icon(Icons.ZOOM_OUT),
            #                     close_on_click=False,
            #                     style=_style,
            #                     on_click=lambda e: registry.subjects["ui.menu.menu.zoom.minify"].notify(e),
            #                 ),
            #             ],
            #         )
            #     ],
            # ),
            MenuItemButton(
                content=registry.ui.noteTitle,
                style=_style,
                #on_click=handle_menu_item_click,
            ),
            #Container(bgcolor=Colors.RED_700, width=_page.width, content=Text("Test")),
        ],
    )

    if not _menubar:
        print("Error. No menubar created.")
        return None

    # register controls
    register("ui.menubar", _menubar)
    register("ui.menu.file.new", _menubar.controls[1].controls[0])
    register("ui.menu.file.open", _menubar.controls[1].controls[1])
    register("ui.menu.file.save", _menubar.controls[1].controls[2])
    register("ui.menu.file.close", _menubar.controls[1].controls[3])
    register("ui.menu.file.about", _menubar.controls[1].controls[4])
    if not _page.web:
        _smb.controls.append(_quit)
        register("ui.menu.file.quit", _menubar.controls[1].controls[6])

    # register observables
    registry.subjects.register("ui.menu.file.new")
    registry.subjects.register("ui.menu.file.open")
    registry.subjects.register("ui.menu.file.save")
    registry.subjects.register("ui.menu.file.close")
    registry.subjects.register("ui.menu.file.about")
    registry.subjects.register("ui.menu.file.quit")
    #registry.subjects.register("ui.menu.manage.categories")
    
    _row = Row(
        controls=[
            _menubar,
        ],
        height=40,
    )

    return _row
