###
# File:   src\ui\views\sidebar.py
# Date:   2025-07-28
# Author: Gemini
###

import logging
from flet import (
    AlertDialog, 
    alignment,
    Colors,
    Column,
    Container,
    ElevatedButton, 
    ExpansionPanel,
    ExpansionPanelList,
    IconButton,
    Icons,
    ListTile,
    ListView,
    Page,
    Row,
    Text,
    TextField, 
    RadioGroup, 
    Radio,
    padding,
)
from datetime import datetime, date as date_cls
from db import registry, register
from models.notes import DEFAULT_CATEGORIES, DEFAULT_MODULES, DEFAULT_TEMPLATES, MeetingNote
from ui.dialogs import meeting_notes, confirm as confirm_dialog
from ui.panels.note_view import build_note_view
from logic.persistence import slugify, rename_note_file, update_notes


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
        logging.debug(f"create_panel_header: setting custom add for {title}")
        add_action = lambda e: add_callback(page)
    else:
        logging.debug(f"create_panel_header: default add for {title}")
        add_action = lambda e: meeting_notes.show(page, None)

    def _add_on_click(e):
        logging.debug(f"header.add clicked for {title}")
        add_action(e)

    add_btn = IconButton(Icons.ADD_CIRCLE_OUTLINE, on_click=_add_on_click, disabled=add_button_disabled)
    edit_btn = IconButton(Icons.EDIT_OUTLINED, on_click=(edit_callback if edit_callback else (lambda e: logging.debug(f"Edit {title}"))), disabled=edit_delete_disabled)
    delete_btn = IconButton(Icons.DELETE_OUTLINE, on_click=(delete_callback if delete_callback else (lambda e: logging.debug(f"Delete {title}"))), disabled=edit_delete_disabled)

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
        ),
        bgcolor=Colors.GREY_800,
    )


# append as a selectable ListTile and register selection
def _on_click(e, item=None):
    # Deselect if already selected
    if getattr(item, "_is_selected", False):
        item._is_selected = False
        item.selected = False
        registry.ui.sidebar.MeetingNotes.edit.disabled = True
        registry.ui.sidebar.MeetingNotes.delete.disabled = True
        registry.subjects["contentView"].notify(e.page, [])
        e.page.update()
        return

    # Select this item and clear others
    meeting_list = registry.ui.sidebar.MeetingNotes.list
    for c in meeting_list.controls:
        c._is_selected = False
        c.selected = False

    item._is_selected = True
    item.selected = True
    registry.ui.sidebar.MeetingNotes.edit.disabled = False
    registry.ui.sidebar.MeetingNotes.delete.disabled = False

    title = getattr(item, "title", None) or "Untitled"
    # Update main content for this note using centralized renderer
    try:
        nd = getattr(item, "note_data", None) or {}
        # Ensure the note_data has an attached MeetingNote object so
        # edits can sync back to the model. If not present, try to
        # reconstruct one from the metadata and add to the in-memory
        # collection (best-effort).
        try:
            if not nd.get('_note_obj') and hasattr(registry, 'notes_collection') and registry.notes_collection is not None:
                from models.notes import MeetingNote
                # Avoid creating duplicates: look for an existing note with same title+date
                existing = None
                for n in registry.notes_collection.notes:
                    if getattr(n, 'title', None) == nd.get('title') and getattr(n, 'date', None) == nd.get('date'):
                        existing = n
                        break

                if existing:
                    nd['_note_obj'] = existing
                else:
                    parts = nd.get('participants') or ""
                    if isinstance(parts, list):
                        plist = parts
                    else:
                        plist = [p.strip() for p in str(parts).splitlines() if p.strip()]

                    note_obj = MeetingNote(
                        title=nd.get('title') or title,
                        category=nd.get('category', ''),
                        tags=nd.get('tags', []) or [],
                        content=nd.get('body') or nd.get('content') or "",
                        topic=nd.get('topic') or "Meeting Note",
                        date=nd.get('date'),
                        time=nd.get('time'),
                        location=nd.get('location'),
                        participants=plist,
                        notes=nd.get('notes') or "",
                        todos=nd.get('todos') or [],
                        created_at=nd.get('created_at')
                    )
                    registry.notes_collection.notes.append(note_obj)
                    nd['_note_obj'] = note_obj
        except Exception:
            pass

        col = build_note_view(e.page, nd, title_fallback=title)
        registry.subjects["contentView"].notify(e.page, [col])
    except Exception:
        pass

    e.page.update()


def populate_meeting_notes(page: Page, collection=None):
    """Populate the MeetingNotes ListView from a NotesCollection.

    This is safe to call multiple times; it clears the current list and
    re-adds tiles for each MeetingNote found in `collection` (or
    `registry.notes_collection` if omitted).
    """
    try:
        coll = collection if collection is not None else getattr(registry, 'notes_collection', None)
        meeting_ns = getattr(registry.ui.sidebar, 'MeetingNotes', None)
        if not meeting_ns or not getattr(meeting_ns, 'list', None):
            return

        lv = meeting_ns.list
        # clear existing entries
        lv.controls.clear()

        notes = coll.notes if coll and getattr(coll, 'notes', None) is not None else []

        def _to_dt(val):
            if val is None:
                return datetime.min
            if isinstance(val, datetime):
                return val
            if isinstance(val, date_cls):
                return datetime.combine(val, datetime.min.time())
            if isinstance(val, str):
            # try ISO first, then some common formats
                try:
                    return datetime.fromisoformat(val)
                except Exception:
                    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d", "%d.%m.%Y"):
                        return datetime.strptime(val, fmt)

                return datetime.min

            try:
            # numeric timestamps
                return datetime.fromtimestamp(float(val))
            except Exception:
                return datetime.min

        # sort notes by date descending (newest first)
        sorted_notes = sorted(notes, key=lambda n: _to_dt(getattr(n, 'date', None)), reverse=True)

        for note in sorted_notes:
            try:
                nd = {
                    'title': getattr(note, 'title', None),
                    'topic': getattr(note, 'topic', None),
                    'date': getattr(note, 'date', None),
                    'time': getattr(note, 'time', None),
                    'location': getattr(note, 'location', None),
                    'participants': getattr(note, 'participants', None),
                    'notes': getattr(note, 'notes', None),
                    'todos': getattr(note, 'todos', None),
                    'created_at': getattr(note, 'created_at', None),
                    'updated_at': getattr(note, 'updated_at', None),
                    '_note_obj': note,
                }

                lt = ListTile(
                    title=Text(nd.get('title') or "Untitled"), 
                    selected=False, 
                    )
                lt.note_data = nd
                lt._is_selected = False
                lt.on_click = lambda e, item=lt: _on_click(e, item=item)
                lv.controls.append(lt)
            except Exception as _e:
                logging.exception(f'Error adding note to sidebar list: {_e}')

        # auto-select first note
        try:
            if lv.controls:
                first = lv.controls[0]
                first._is_selected = True
                first.selected = True
                nd = getattr(first, 'note_data', {}) or {}
                col = build_note_view(page, nd, title_fallback=nd.get('title'))
                registry.subjects['contentView'].notify(page, [col])
        except Exception:
            logging.exception('Error auto-selecting first note in sidebar')

        page.update()

    except Exception:
        logging.exception('Failed to populate MeetingNotes')


def build(page: Page):
    """Builds the sidebar with collapsible list elements.

    If no notes collection is open (registry.notesFile / notesName is None), the
    panels' action buttons are disabled and non-essential panels are hidden.
    """
    # Determine enabled state from registry (notes collection opened?)
    enabled = bool(getattr(registry, "notesFile", None) or getattr(registry, "notesName", None))

    # Optionally hide non-essential panels when not enabled
    # templates_visible = enabled
    # modules_visible = enabled
    # categories_visible = enabled
    logging.debug("sidebar: build start, enabled=%s", enabled)

    # Build interactive controls
    def _templates_on_change(e):
        val = getattr(e.control, "value", None)
        register("ui.sidebar.Templates.selected", val)
        # Enable edit/delete only when a selection exists
        registry.ui.sidebar.Templates.edit.disabled = False if val else True
        registry.ui.sidebar.Templates.delete.disabled = False if val else True
        page.update()

    def _meeting_add(page_ref):
        # open meeting_notes dialog and append created note
        logging.debug("sidebar: meeting_add called")
        def _cb(p, data):
            logging.debug("sidebar: meeting_cb received %s", data)
            if not data:
                logging.warning("sidebar: no data received %s", data)
                return

            title = data.get("title") or "New Note"

            # Create the ListTile and append
            lt = ListTile(title=Text(title), selected=False)
            lt.note_data = data
            lt._is_selected = False
            lt.on_click = lambda e, item=lt: _on_click(e, item=item)
            meeting_list.controls.append(lt)
            # Auto-select the newly created item
            try:
                for c in meeting_list.controls:
                    c._is_selected = False
                    c.selected = False

                lt._is_selected = True
                lt.selected = True

                if hasattr(registry, 'notes_collection') and registry.notes_collection is not None:
                    note_obj = MeetingNote(
                        title=data.get('title', ''),
                        category=data.get('category', ''),
                        tags=data.get('tags', []) or [],
                        content=data.get('body', '') or "",
                        topic=data.get('topic') or "Meeting Note",
                        date=data.get('date'),
                        time=data.get('time'),
                        location=data.get('location'),
                        participants=[p.strip() for p in (data.get('participants') or "").splitlines() if p.strip()] if data.get('participants') else [],
                        notes=data.get('notes') or "",
                        todos=[t for t in ((data.get('notes') or "").splitlines()) if t.strip().startswith('[') or t.strip().startswith('- [')],
                        created_at=(f"{data.get('date')} {data.get('time')}" if data.get('date') and data.get('time') else data.get('date')),
                        updated_at=(f"{data.get('date')} {data.get('time')}" if data.get('date') and data.get('time') else data.get('date'))
                    )
                    registry.notes_collection.notes.append(note_obj)
                    data['_note_obj'] = note_obj

                # Build the default note view and publish it
                col = build_note_view(p, data or {}, title_fallback=title)
                registry.subjects["contentView"].notify(p, [col])
                registry.ui.sidebar.MeetingNotes.edit.disabled = False
                registry.ui.sidebar.MeetingNotes.delete.disabled = False
                page_ref.update()
            except Exception as _e:
                logging.exception("sidebar: meeting_add auto-select error")

        # Call the meeting notes dialog (no test dialog / fallback) so the
        # user interacts with the real dialog and its OK handler can fire.
        try:
            logging.debug("sidebar: calling meeting_notes.show")
            meeting_notes.show(page_ref, _cb)
            page_ref.window.to_front()
            logging.debug("sidebar: meeting_notes.show returned")
        except Exception as ex:
            logging.exception("sidebar: meeting_notes.show error")

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
                meeting_list.controls.remove(sel)
                registry.ui.sidebar.MeetingNotes.edit.disabled = True
                registry.ui.sidebar.MeetingNotes.delete.disabled = True
                registry.subjects["contentView"].notify(page, [])
                page.update()

            confirm_dialog.show(page, _do_delete)
        except Exception as ex:
            logging.exception("_meeting_delete error")

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
                ok_btn.disabled = not (len(v.strip()) >= 5 and len(v.strip()) <= 35)
                page.update()

            name_field.on_change = _on_text_change

            def _on_ok(ev):
                new_title = (name_field.value or "").strip()
                if not (5 <= len(new_title) <= 35):
                    return
                # update the selected tile and its data
                try:
                    sel.title = Text(new_title)
                    nd = getattr(sel, "note_data", {})
                    initial = nd["title"]
                    nd["title"] = new_title
                    sel.note_data = nd
                    if getattr(sel, "_is_selected", False):
                        col = build_note_view(page, nd, title_fallback=new_title)
                        registry.subjects["contentView"].notify(page, [col])

                    for note in registry.notes_collection.notes:
                        if note.title != initial:
                            continue

                        note.title = new_title
                        # try to rename underlying file in the notes folder (sanitize special chars)
                        rename_note_file(slugify(initial), slugify(new_title))
                        update_notes(registry.notes_collection, check_exists=True)
                        break

                except Exception:
                    pass

                page.close(rename_dlg)
                page.update()

            ok_btn.on_click = _on_ok

            rename_dlg = AlertDialog(title=Text("Rename Meeting Note"), content=Row([name_field]), actions=[cancel_btn, ok_btn])
            page.open(rename_dlg)
        except Exception as ex:
            logging.exception("_meeting_edit error")

    templates_group = RadioGroup(
        content=Column([Radio(value=t, label=t) for t in DEFAULT_TEMPLATES.keys()]),
        value=None,
        on_change=_templates_on_change,
    )
    register("ui.sidebar.Templates.list", templates_group)

    meeting_list = ListView(controls=[], spacing=0, padding=padding.all(0), divider_thickness=0, height=300)
    register("ui.sidebar.MeetingNotes.list", meeting_list)

    # Register the add callback so header resolver can find it
    register("ui.sidebar.MeetingNotes.add_callback", _meeting_add)

    return ExpansionPanelList(
        expand_icon_color=Colors.AMBER,
        expanded_header_padding=0,
        elevation=8,
        divider_color=Colors.AMBER,
        controls=[
            ExpansionPanel(
                header=create_panel_header("Meeting Notes", page, enabled=enabled, add_callback=_meeting_add, edit_callback=_meeting_edit, delete_callback=_meeting_delete),
                content=Container(
                    content=Column([meeting_list]),
                    bgcolor=Colors.GREY_700,
                ),
                expanded=True,
                bgcolor=Colors.GREY_800,
            ),
            ExpansionPanel(
                header=create_panel_header("Templates", page, enabled=enabled),
                content=Container(
                    content=Column([templates_group]),
                    bgcolor=Colors.GREY_700,
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=False,
                bgcolor=Colors.GREY_800,
            ),
            ExpansionPanel(
                header=create_panel_header("Modules", page, enabled=enabled),
                content=Container(
                    content=Column([Text(module) for module in DEFAULT_MODULES]),
                    bgcolor=Colors.GREY_700,
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=False,
                bgcolor=Colors.GREY_800,
            ),
            ExpansionPanel(
                header=create_panel_header("Categories", page, enabled=enabled),
                content=Container(
                    content=Column([Text(category) for category in DEFAULT_CATEGORIES]),
                    bgcolor=Colors.GREY_700,
                    padding=10,
                    alignment=alignment.center_left
                ),
                expanded=False,
                bgcolor=Colors.GREY_800,
            )
        ]
    )
