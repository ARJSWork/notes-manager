AGENTS/Memory for Notes Manager
Saved: 2025-09-08
Git commit: 17d22db

Summary of recent work
- Sidebar gating: sidebar hidden/disabled until a notes collection is New/Open. Registered container at `ui.sidebar.container`.
- Templates: switched to an interactive `RadioGroup` (registered as `ui.sidebar.Templates.list`).
- Meeting Notes dialog (`src/ui/dialogs/meeting_notes.py`): fixed DatePicker usage (use `page.open(date_picker)`), ensured `OK` calls the provided callback with {title, template, date}. Removed test button.
- Meeting Notes flow (`src/ui/views/sidebar.py`): `add` opens meeting dialog; callback `_cb` now appends a selectable `ListTile`, auto-selects it, toggles Edit/Delete icons, and publishes the template text to `registry.subjects['contentView']` as a single `Column`.
- Selection: ListTile selection uses an internal `_is_selected` flag to ensure toggle behavior works reliably across platforms.

Files changed (important)
- src/ui/dialogs/meeting_notes.py  (dialog OK handler, DatePicker)
- src/ui/views/sidebar.py         (sidebar build, meeting add callback, selection logic)
- src/ui/app.py                   (contentView registration, sidebar container)
- src/logic/ui/menu.py            (menu state & sidebar gating)

Registry keys of interest
- ui.sidebar.container
- ui.sidebar.MeetingNotes.add_callback
- ui.sidebar.MeetingNotes.list
- ui.sidebar.MeetingNotes.edit
- ui.sidebar.MeetingNotes.delete
- ui.sidebar.Templates.list
- subjects: contentView (used to publish main content)

How to reproduce (manual)
1. Ensure Flet is installed and venv activated.
2. Run the app: `python -m src` (or the project's launcher).
3. File → New (or Open) to enable sidebar.
4. In Sidebar → Meeting Notes → Add.
5. In dialog, choose template/date and click OK.
6. New note should appear in Meeting Notes list, be selected, and main content shows template text.

Notes / gotchas
- The agent could not run Flet in the editing environment; all runtime verification was done by you locally. Keep Flet updated if you see API mismatches.
- Edit/Delete handlers are stubbed (they are enabled/disabled correctly but actions are not fully implemented).
- Modules/Categories panels remain static text; consider converting to selectable lists.
- Some debug prints remain; consider removing or converting to structured logging.

Commit
- 17d22db: "ui: gate sidebar, wire Meeting Notes dialog and selectable templates"

Saved by: local developer session (automated agent edits).

User testing
Delete meeting notes: tested by user on 2025-09-23; confirmed working before commit.
Header rename (Edit/pencil): tested by user on 2025-09-23; confirmed working before commit.

---

Saved: 2025-11-11

Summary of recent work
- Refactored the main content view (`src/ui/panels/note_view.py`) to support a detailed edit mode.
- Edit mode now provides individual fields for each note module (Topic, Date, Time, etc.).
- Implemented auto-population of Date and Time for new notes.
- Replaced the static "Location" text field with an editable `Dropdown`.
- To support the dropdown, the data model was extended (`src/models/notes.py`) to include a persistent `locations` list in the `NotesCollection`.
- The application's core logic (`src/logic/ui/menu.py`) was updated to correctly load and create `NotesCollection` objects, storing them in `registry.notes_collection`.

Additional recent work (2025-11-11)
- Centralized sidebar population into `src/ui/views/sidebar.py` with a module-level `populate_meeting_notes(page, collection)` function; `menu.setMenuState` calls it to repopulate when opening.
- Interactive ToDos: display view checkboxes are now clickable and update the underlying `MeetingNote` model and mark it dirty. Changes republish the `contentView` subject.
- Date/Time controls: added `src/ui/controls/date_selector.py` and `src/ui/controls/time_selector.py` and integrated them into the edit view; save logic reads values via `get_value()`.
- DirectorySelector UX: Select button initially disabled, becomes enabled and green when a selection is made; Cancel returns an empty dict, Select returns a dict with selection details.
- Keyboard shortcuts: attached a page keyboard handler scoped to the focused Notes TextField; common snippets (header/topic/date/time insertions) implemented.
- Hamburger/drawer: Menu drawer MenuItem notifies `ui.menu.drawer` subject; `_toggle_sidebar` observer toggles `registry.ui.sidebar.container.visible`. Sidebar auto-collapses when entering edit mode and auto-re-opens on save/cancel.

Files changed (important)
- src/ui/views/sidebar.py (added `populate_meeting_notes` and adjusted build wiring)
- src/ui/panels/note_view.py (interactive todos, edit/save/cancel wiring, selectors, keyboard handler)
- src/ui/controls/time_selector.py (new control)
- src/ui/controls/date_selector.py (new control)
- src/ui/controls/directory_selector.py (select/cancel UX improvements)
- src/ui/panels/menu.py (drawer subject wiring and toggle)

Notes / gotchas
- The agent could not run Flet in the editing environment; runtime verification should be performed locally. Many syntax checks passed in the editing session.
- Rename/Delete/Copy handlers are enabled/disabled correctly in the UI, but full file-operation implementations need follow-up work and testing.

Commit
- Pending: commit will be created representing these documentation updates and small fixes. After commit the `Git commit` line will be updated with the new hash.

Files changed (important)
- src/ui/panels/note_view.py (main implementation of edit/display views)
- src/models/notes.py (added `locations` to `NotesCollection`)
- src/logic/ui/menu.py (fixed data loading and creation)

Outstanding Bug
- A persistent bug exists where a custom value typed into the editable "Location" `Dropdown` (e.g., "Office Leipzig") is not correctly saved. Upon saving, the value reverts to a pre-existing option or is lost. The root cause is suspected to be in how the Flet `Dropdown` control's `.value` property is updated and read, especially when the typed text does not exactly match an existing option.

Registry keys of interest
- registry.notes_collection (The loaded `NotesCollection` object)

Notes / gotchas
- Always use `ft.Icons` and `ft.Colors` (uppercase) instead of `ft.icons` and `ft.colors` (lowercase) to align with the latest Flet API.