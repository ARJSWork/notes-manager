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
from flet import RadioGroup, Radio
from db import registry, register
from models.notes import DEFAULT_CATEGORIES, DEFAULT_MODULES, DEFAULT_TEMPLATES
from ui.dialogs import meeting_notes
from ui.panels.note_view import build_note_view

def create_panel_header(title: str, page, enabled: bool = False, add_callback=None, edit_callback=None, delete_callback=None):
    """Creates a ListTile with action buttons for the ExpansionPanel header.

    The `enabled` flag controls whether action buttons are active. When no
    notes collection is open, these should be disabled.
    """
    # Allow adding for all panels when enabled
    add_button_disabled = not enabled
    edit_delete_disabled = not enabled

    # Create buttons so we can register and toggle them later
    # Allow passing a custom add callback (used for Meeting Notes to receive created note)
    if add_callback:
        print(f"create_panel_header: setting custom add for {title}")
        add_action = lambda e: add_callback(page)
    else:
        print(f"create_panel_header: default add for {title}")
        add_action = lambda e: meeting_notes.show(page, None)

    def _add_on_click(e):
        print(f"header.add clicked for {title}")
        try:
            add_action(e)
        except Exception as ex:
            print(f"header.add action error for {title}:", ex)

    add_btn = IconButton(Icons.ADD_CIRCLE_OUTLINE, on_click=_add_on_click, disabled=add_button_disabled)
    edit_btn = IconButton(Icons.EDIT_OUTLINED, on_click=(edit_callback if edit_callback else (lambda e: print(f"Edit {title}"))), disabled=edit_delete_disabled)
    delete_btn = IconButton(Icons.DELETE_OUTLINE, on_click=(delete_callback if delete_callback else (lambda e: print(f"Delete {title}"))), disabled=edit_delete_disabled)

    # Register buttons under a predictable registry path so other code can update them
    # e.g. registry.ui.sidebar.MeetingNotes.add
    key_base = f"ui.sidebar.{title.replace(' ', '')}."
    register(key_base + "add", add_btn)
    register(key_base + "edit", edit_btn)
    register(key_base + "delete", delete_btn)

    return ListTile(
        title=Row(
            controls=[
                Text(title, expand=True),
                add_btn,
                edit_btn,
                delete_btn,
            ],
            alignment="spaceBetween"
        )
    )

def build(page: Page):
    """Builds the sidebar with collapsible list elements.

    If no notes collection is open (registry.notesFile / notesName is None), the
    panels' action buttons are disabled and non-essential panels are hidden.
    """
    # Determine enabled state from registry (notes collection opened?)
    enabled = bool(getattr(registry, "notesFile", None) or getattr(registry, "notesName", None))

    # Optionally hide non-essential panels when not enabled
    templates_visible = enabled
    modules_visible = enabled
    categories_visible = enabled
    print("sidebar: build start, enabled=", enabled)
    # Build interactive controls
    def _templates_on_change(e):
        val = getattr(e.control, "value", None)
        register("ui.sidebar.Templates.selected", val)
        # Enable edit/delete only when a selection exists
        try:
            registry.ui.sidebar.Templates.edit.disabled = False if val else True
            registry.ui.sidebar.Templates.delete.disabled = False if val else True
        except Exception:
            pass
        try:
            page.update()
        except Exception:
            pass

    templates_group = RadioGroup(
        content=Column([Radio(value=t, label=t) for t in DEFAULT_TEMPLATES.keys()]),
        value=None,
        on_change=_templates_on_change,
    )
    register("ui.sidebar.Templates.list", templates_group)

    # Meeting notes list and handlers
    from flet import ListView, ListTile

    meeting_list = ListView(controls=[], spacing=5, height=200)
    register("ui.sidebar.MeetingNotes.list", meeting_list)

    def _meeting_on_select(e):
        # e.control likely is a ListTile or similar; find selected index
        # For now, enable edit/delete when any item is clicked
        try:
            registry.ui.sidebar.MeetingNotes.edit.disabled = False
            registry.ui.sidebar.MeetingNotes.delete.disabled = False
        except Exception:
            pass
        try:
            page.update()
        except Exception:
            pass

    def _meeting_add(page_ref):
        # open meeting_notes dialog and append created note
        print("sidebar: meeting_add called")
        def _cb(p, data):
            print("sidebar: meeting_cb received", data)
            if not data:
                return
            title = data.get("title") or "New Note"
            # append as a selectable ListTile and register selection
            from flet import ListTile, Column
            def _on_click(e, item=None):
                # Deselect if already selected
                if getattr(item, "_is_selected", False):
                    try:
                        item._is_selected = False
                    except Exception:
                        pass
                    try:
                        item.selected = False
                    except Exception:
                        pass
                    try:
                        registry.ui.sidebar.MeetingNotes.edit.disabled = True
                        registry.ui.sidebar.MeetingNotes.delete.disabled = True
                    except Exception:
                        pass
                    try:
                        registry.subjects["contentView"].notify(p, [])
                    except Exception:
                        pass
                    try:
                        p.update()
                    except Exception:
                        pass
                    return

                # Select this item and clear others
                for c in meeting_list.controls:
                    try:
                        c._is_selected = False
                        c.selected = False
                    except Exception:
                        pass
                try:
                    item._is_selected = True
                    item.selected = True
                except Exception:
                    pass
                try:
                    registry.ui.sidebar.MeetingNotes.edit.disabled = False
                    registry.ui.sidebar.MeetingNotes.delete.disabled = False
                except Exception:
                    pass

                # Update main content for this note using centralized renderer
                try:
                    nd = getattr(item, "note_data", None) or {}
                    col = build_note_view(p, nd, title_fallback=title)
                    try:
                        registry.subjects["contentView"].notify(p, [col])
                    except Exception:
                        pass
                except Exception:
                    pass
                try:
                    p.update()
                except Exception:
                    pass

            lt = ListTile(title=Text(title), selected=False)
            # attach the note data so click handler can show content
            try:
                # Generate initial body from template
                tmpl = data.get("template")
                if tmpl and tmpl in DEFAULT_TEMPLATES:
                    t = DEFAULT_TEMPLATES[tmpl]
                    mods = t.get("modules", [])
                    body_lines = []
                    for m in mods:
                        body_lines.append(f"## {m}")
                        lines = t.get(m, []) if isinstance(t.get(m, []), list) else []
                        for ln in lines:
                            body_lines.append(ln)
                    data["body"] = "\n".join(body_lines)
                else:
                    data["body"] = ""

                lt.note_data = data
            except Exception:
                pass
            # manage selection with our own flag to avoid timing/race with flet
            try:
                lt._is_selected = False
            except Exception:
                pass
            # bind click with correct item reference
            try:
                lt.on_click = lambda e, item=lt: _on_click(e, item=item)
            except Exception:
                lt.on_click = None
            meeting_list.controls.append(lt)
            # Auto-select the newly created item
            try:
                for c in meeting_list.controls:
                    try:
                        c._is_selected = False
                        c.selected = False
                    except Exception:
                        pass
                lt._is_selected = True
                lt.selected = True
            except Exception:
                pass
            # Publish template content to main content view
            try:
                tmpl = data.get("template")
                content_controls = []
                if tmpl and tmpl in DEFAULT_TEMPLATES:
                    # flatten template modules into text lines
                    t = DEFAULT_TEMPLATES[tmpl]
                    mods = t.get("modules", [])
                    for m in mods:
                        lines = t.get(m, []) if isinstance(t.get(m, []), list) else []
                        content_controls.append(Text(f"## {m}"))
                        for ln in lines:
                            content_controls.append(Text(ln))
                else:
                    content_controls.append(Text(title))
                try:
                    # Build the default note view and publish it
                    nd = data or {}
                    col = build_note_view(p, nd, title_fallback=title)
                    try:
                        registry.subjects["contentView"].notify(p, [col])
                    except Exception:
                        pass
                except Exception:
                    pass
            except Exception:
                pass
            # enable edit/delete
            try:
                registry.ui.sidebar.MeetingNotes.edit.disabled = False
                registry.ui.sidebar.MeetingNotes.delete.disabled = False
            except Exception:
                pass
            try:
                page_ref.update()
            except Exception:
                pass

        # Call the meeting notes dialog (no test dialog / fallback) so the
        # user interacts with the real dialog and its OK handler can fire.
        try:
            print("sidebar: calling meeting_notes.show")
            meeting_notes.show(page_ref, _cb)
            try:
                page_ref.window.to_front()
            except Exception:
                pass
            print("sidebar: meeting_notes.show returned")
        except Exception as ex:
            print("sidebar: meeting_notes.show error:", ex)

    # Delete handler for meeting notes
    from ui.dialogs import confirm as confirm_dialog

    def _meeting_delete(e):
        try:
            # find selected item
            sel = None
            for c in meeting_list.controls:
                if getattr(c, "_is_selected", False):
                    sel = c
                    break
            if not sel:
                return

            def _do_delete():
                try:
                    meeting_list.controls.remove(sel)
                except Exception:
                    pass
                try:
                    registry.ui.sidebar.MeetingNotes.edit.disabled = True
                    registry.ui.sidebar.MeetingNotes.delete.disabled = True
                except Exception:
                    pass
                try:
                    registry.subjects["contentView"].notify(page, [])
                except Exception:
                    pass
                try:
                    page.update()
                except Exception:
                    pass

            confirm_dialog.show(page, _do_delete)
        except Exception as ex:
            print("_meeting_delete error:", ex)

    # Edit (rename) handler for meeting notes - opens a small input dialog
    from flet import AlertDialog, TextField, ElevatedButton, Row

    def _meeting_edit(e):
        try:
            # find selected item
            sel = None
            for c in meeting_list.controls:
                if getattr(c, "_is_selected", False):
                    sel = c
                    break
            if not sel:
                # no selection - inform the user with a small dialog
                dlg = AlertDialog(title=Text("Rename"), content=Text("Please select a meeting note first."), actions=[ElevatedButton("OK", on_click=lambda ev: (page.close(dlg), page.update()))])
                page.open(dlg)
                return

            initial = getattr(sel, "note_data", {}).get("title", "")

            name_field = TextField(value=initial, width=260, autofocus=True)
            ok_btn = ElevatedButton("OK", disabled=not (initial and len(initial.strip()) >= 5))
            cancel_btn = ElevatedButton("Cancel", on_click=lambda ev: (page.close(rename_dlg), page.update()))

            def _on_text_change(ev):
                v = name_field.value or ""
                ok_btn.disabled = not (len(v.strip()) >= 5 and len(v.strip()) <= 25)
                page.update()

            name_field.on_change = _on_text_change

            def _on_ok(ev):
                new_title = (name_field.value or "").strip()
                if not (5 <= len(new_title) <= 25):
                    return
                # update the selected tile and its data
                try:
                    sel.title = Text(new_title)
                except Exception:
                    pass
                try:
                    nd = getattr(sel, "note_data", {})
                    nd["title"] = new_title
                    sel.note_data = nd
                except Exception:
                    pass
                # if selected, update content view
                try:
                    if getattr(sel, "_is_selected", False):
                        registry.subjects["contentView"].notify(page, [Column(controls=[Text(new_title)])])
                except Exception:
                    pass

                page.close(rename_dlg)
                page.update()

            ok_btn.on_click = _on_ok

            rename_dlg = AlertDialog(title=Text("Rename Meeting Note"), content=Row([name_field]), actions=[cancel_btn, ok_btn])
            page.open(rename_dlg)
        except Exception as ex:
            print("_meeting_edit error:", ex)

    # Register the add callback so header resolver can find it
    register("ui.sidebar.MeetingNotes.add_callback", _meeting_add)

    return ExpansionPanelList(
        expand_icon_color=Colors.AMBER,
        elevation=8,
        divider_color=Colors.AMBER,
        controls=[
            ExpansionPanel(
                header=create_panel_header("Meeting Notes", page, enabled=enabled, add_callback=_meeting_add, edit_callback=_meeting_edit, delete_callback=_meeting_delete),
                content=Container(
                    content=Column([
                        meeting_list
                    ]),
                    padding=10
                ),
                expanded=True
            ),
            ExpansionPanel(
                header=create_panel_header("Templates", page, enabled=enabled),
                content=Container(
                    content=Column(
                        [
                            templates_group,
                        ],
                    ),
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=True,
            ),
            ExpansionPanel(
                header=create_panel_header("Modules", page, enabled=enabled),
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
                header=create_panel_header("Categories", page, enabled=enabled),
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
