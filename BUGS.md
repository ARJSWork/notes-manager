1. Fixed: The path for the saved collection is wrong.
   Path used: src/data/collections/BR/
   Path should be used: notes/BR/
   Hint: "notes" folder is on the same level als the "src" folder.

2. Fixed: The created collection.json is correct, but there is no update to the new created note. I assume it is, because the new created note was not saved in the correct path. Hence, there is no update of the collection.json.

3. Fixed: There is no save note file: "Quick_2025-10-08.json", even this note "Quick 2025-10-08" was created and not saved, yet. It should be saved within "notes/BR" folder.

4. Fixed: The now saved note "Quick_2025-10-08.json" is only generic. 
There is no date, time, custom location, title, no participants and the actual content is missing, too. Even they are entered during creation of the note. Have a look what is actually in the file, which is simply the generic initial content:
>## Topic
>Quick 2025-10-08
>## Date
>2025-10-08
>## Time
>## Participants
>## Location
>## Notes
>- Bulletpoint 1
>- Bulletpoint 2
>## Subtitle
>- [ ] ToDo 1

Thats what I've entered in the form:
Topic: Quick 2025-10-08
Date: 2025-10-08
Time: 10:00
Location: Kantine
Participants:
A
B
Notes:
- Test 1
- Test 2

The following I could not change in the form:
## Subtitle
- [ ] ToDo 1

The currently saved note is now:
{
  "title": "Quick 2025-10-08",
  "created_at": "2025-10-08",
  "time": null,
  "content": "## Topic\nQuick 2025-10-08\n## Date\n2025-10-08\n## Time\n## Participants\n## Location\n## Notes\n- Bulletpoint 1\n- Bulletpoint 2\n## Subtitle\n- [ ] ToDo 1"
}

I would expect if there is a change in format something like this:
{
  "title": "Quick 2025-10-08",
  "created_at": "2025-10-08 10:18",
  "updated_at": "2025-10-08 10:18",
  "topic": "Quick 2025-10-08",
  "date": "2025-10-08",
  "time": "10:16",
  "location": "Kantine",
  "participants": ["A","B"],
  "content": "- Test 1\n- Test 2\n",
  "todos": ["[ ] ToDo 1"]
}

5. Fixed: The saved notes file, should be also include the time, like "Quick_2025-10-08_1010.json"; Time in 24h format.

6. Feature - If new notes collection is selected and a new collection name is entered, but the collection is already there in "notes"-Folder, the programm should use "Open" instead of "New" functionality.

7. Feature - Add keyboard short curs for editing the notes and todo texts. E.g. use <ctrl>+"#" to add a header secton starting with "#", <ctrl>+"+" for a subtitle starting with "+", <ctrl>+"-" for a bulletpoint starting with "-" or <ctrl>+"*" for a bulletpoint starting with "*".

8. Feature - Currently there is no way to enter tags. Tags should be integrated, as additional field in the notes entry view with a new custom control (if flet.dev does not alrady have one), similar to the "location" custom control. So existing tags can be picked and new ones can be entered. Also with saving the new ones into the global collection storage or file. 

9. Feature - Add Buttons "Preview", "Export", "Clipboard" and "Print" to the display view when a note is selected and viewed in the display view.

10. Feature - Implement the Rename, Delete and Copy of Notes in the Meeting Notes Sidebar.

11. Feature - Optimize save behavior (save only changed notes; ensure collection view updates)

Goal
- Only persist notes that were actually modified. Ensure collection metadata (collection.json) is updated whenever notes are renamed, deleted or copied.

Design / Implementation notes
- Note model
  - Add a boolean field `dirty` (default False).
  - Add helper methods: `mark_dirty()`, `clear_dirty()`.
  - Set `dirty = True` whenever any user-editable property changes (title, topic, date, time, location, participants, content, todos, tags).
- NotesCollection
  - Implement `save_note_if_dirty(note)` — writes note file only when `note.dirty is True`, then `note.clear_dirty()`.
  - Implement `save_changed_notes()` — iterate collection notes and call `save_note_if_dirty`.
  - Implement `save_collection_view()` — write collection.json / index file; call whenever notes are renamed, deleted or copied.
- UI wiring
  - Hook change events in edit fields to call `note.mark_dirty()`. Prefer centralized handler in note_view to reduce duplication.
  - After user-initiated Save/Close/Auto-save: call `notes_collection.save_changed_notes()`.
  - On rename/delete/copy actions from sidebar: update collection data model, then call `notes_collection.save_collection_view()` (and for copy, also ensure the new note is marked dirty so it gets saved).
- Autosave / debounce
  - Use a debounce timer to avoid saving on every keystroke:
    - Start/reset a short timer (e.g., 500–1500ms) after a change; when it fires, call `save_changed_notes()` (only writes dirty notes).
    - Use Flet’s `page.schedule_frame` / `page.future` or a lightweight asyncio debounce depending on app architecture.
- File naming & atomic write
  - Ensure note filenames include time when requested (e.g., "Quick_2025-10-08_1010.json") if you already require time-based uniqueness.
  - Write files atomically (write to temp file then move) to avoid partial files.
- Edge cases & consistency
  - When renaming a note: move/rename the file on disk or create new file and delete old one; then call `save_collection_view()`.
  - When deleting: remove file, update collection.json, call `save_collection_view()`.
  - When copying: create new Note object with `dirty=True` so it will be saved by `save_changed_notes()`, and update collection.json.
- Tests / Validation
  - Add unit tests for:
    - Marking dirty on field changes.
    - `save_changed_notes()` writing only dirty notes.
    - `save_collection_view()` after rename/delete/copy.
    - Debounce keeps from excessive writes.
- Registry / hooks
  - Consider registering an app-level autosave toggle and debounce interval in registry (e.g., `registry.settings.autosave`, `registry.settings.autosave_debounce_ms`) for configurability.

Developer notes / TODO
- Remove debug prints and replace with structured logging around save operations (info on saved files, debug on skipped files).
- Ensure backwards compatibility when loading older note files without new fields — set `dirty=False` after load.
- Update README or developer docs to describe the dirty-flag save flow and APIs.

Acceptance criteria
- Edited notes mark as dirty and are written to disk on save/autosave; unchanged notes are not rewritten.
- Rename/Delete/Copy operations update collection.json immediately (or within debounce window) so collection view stays consistent with disk.
- Autosave is debounced to avoid excessive disk writes.


