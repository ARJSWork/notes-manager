###
# File:   src\ui\bars\content.py
# Date:   2025-02-03 / 09:42
# Author: alexrjs
###


# imports
from flet import Row, MainAxisAlignment
from db import register, registry


# constants


# variables


# functions/classes
def build(content:list=None, **kwargs) -> Row:
    """Menu bar at the top of the page"""

    _page = registry.page
    if not _page:
        print("Error. No page registered")
        return None

    register("ui.detailPanel", None)

    if content is None:
        return Row()

    return Row(
        controls=content,
        spacing=0,
        alignment=MainAxisAlignment.END,
        expand=True,
    )
