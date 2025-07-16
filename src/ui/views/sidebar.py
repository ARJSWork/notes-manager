###
# File:   src\ui\views\sidebar.py
# Date:   2025-07-16
# Author: Gemini
###

from flet import alignment, ExpansionPanelList, ExpansionPanel, ListTile, Text, Container, Column, Colors
from models.notes import DEFAULT_CATEGORIES, DEFAULT_MODULES, DEFAULT_TEMPLATES

def build():
    """Builds the sidebar with collapsible list elements."""
    return ExpansionPanelList(
        expand_icon_color=Colors.AMBER,
        elevation=8,
        divider_color=Colors.AMBER,
        controls=[
            ExpansionPanel(
                header=ListTile(title=Text("Meeting Notes")),
                content=Container(
                    content=Column([
                        Text("Content for Meeting Notes")
                    ]),
                    padding=10
                ),
                expanded=True
            ),
            ExpansionPanel(
                header=ListTile(title=Text("Templates")),
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
                header=ListTile(title=Text("Modules")),
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
                header=ListTile(title=Text("Categories")),
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
