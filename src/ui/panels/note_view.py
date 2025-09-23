###
# File:   src\ui\panels\note_view.py
# Date:   2025-09-23
# Author: automated-refactor
###

from flet import Column, Text
from models.notes import DEFAULT_TEMPLATES


def build_note_view(page, note_data: dict | None, title_fallback: str = "") -> Column:
    """Build a default view for a note.

    Returns a Column control suitable for publishing via
    registry.subjects["contentView"].notify(page, [Column(...)]).

    This function intentionally mirrors the previous inline implementation
    but centralizes it so rendering can be improved later.
    """
    controls = []

    if not note_data:
        controls.append(Text("(No note selected)"))
        return Column(controls=controls)

    tmpl = note_data.get("template")

    if tmpl and tmpl in DEFAULT_TEMPLATES:
        t = DEFAULT_TEMPLATES[tmpl]
        mods = t.get("modules", [])
        for m in mods:
            controls.append(Text(f"## {m}"))
            lines = t.get(m, []) if isinstance(t.get(m, []), list) else []
            for ln in lines:
                controls.append(Text(ln))
    else:
        title = note_data.get("title") or title_fallback or "Untitled"
        controls.append(Text(title))
        body = note_data.get("body")
        if body:
            # simple plain-text rendering; split into lines for layout
            for ln in str(body).splitlines():
                controls.append(Text(ln))

    return Column(controls=controls)
