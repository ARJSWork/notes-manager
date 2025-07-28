###
# File:   src\ui\views\sidebar.py
# Date:   2025-07-28
# Author: Gemini
###

from flet import (
    Page,
    ExpansionPanelList,
    ExpansionPanel,
    ListTile,
    Text,
    Container,
    Column,
    Row,
    IconButton,
    Icons,
    Colors,
    alignment
)
from models.notes import DEFAULT_CATEGORIES, DEFAULT_MODULES, DEFAULT_TEMPLATES
from ui.dialogs import meeting_notes

def create_panel_header(title: str, page):
    """Creates a ListTile with action buttons for the ExpansionPanel header."""
    add_button_disabled = title != "Meeting Notes"

    return ListTile(
        title=Row(
            controls=[
                Text(title, expand=True),
                IconButton(Icons.ADD_CIRCLE_OUTLINE, on_click=lambda e: meeting_notes.show(page, None), disabled=add_button_disabled),
                IconButton(Icons.EDIT_OUTLINED, on_click=lambda e: print(f"Edit {title}"), disabled=True),
                IconButton(Icons.DELETE_OUTLINE, on_click=lambda e: print(f"Delete {title}"), disabled=True),
            ],
            alignment="spaceBetween"
        )
    )

def build(page: Page):
    """Builds the sidebar with collapsible list elements."""
    return ExpansionPanelList(
        expand_icon_color=Colors.AMBER,
        elevation=8,
        divider_color=Colors.AMBER,
        controls=[
            ExpansionPanel(
                header=create_panel_header("Meeting Notes", page),
                content=Container(
                    content=Column([
                        Text("Content for Meeting Notes")
                    ]),
                    padding=10
                ),
                expanded=True
            ),
            ExpansionPanel(
                header=create_panel_header("Templates", page),
                content=Container(
                    content=Column(
                        [Text(template_name) for template_name in DEFAULT_TEMPLATES]
                    ),
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=True
            ),
            ExpansionPanel(
                header=create_panel_header("Modules", page),
                content=Container(
                    content=Column(
                        [Text(module) for module in DEFAULT_MODULES]
                    ),
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=False
            ),
            ExpansionPanel(
                header=create_panel_header("Categories", page),
                content=Container(
                    content=Column(
                        [Text(category) for category in DEFAULT_CATEGORIES]
                    ),
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=False
            )
        ]
    )
