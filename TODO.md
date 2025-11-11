TODO for Notes Manager
Last updated: 2025-11-11

High priority
- [x] **Investigate and Fix Location Dropdown Bug:** Custom location handling investigated; control wiring updated in `note_view` (save reads value from selectors/controls). Further UX edgecases remain but core bug addressed.
- [x] Implement Delete action for Meeting Notes (confirm and remove from list and storage).
- [x] Persist notes to storage (save/load NotesCollection) and wire menu Save/Open.

Medium priority
- [x] Implement floating Edit button for full note edit (toggle display/edit mode in main area). # Edit mode UI complete; save flow improved.
- [ ] Convert Modules and Categories panels into selectable lists (like Templates) and wire their actions.
- [x] Remove or reduce debug prints; add a simple logging facility (many prints replaced with Python `logging`).

Low priority / Nice-to-have
- [ ] Add changelog/README entry summarizing the UI behavior.
- [ ] Add keyboard navigation and accessibility tweaks for the sidebar.
- [ ] Improve template rendering: support markdown rendering in main content area.

Quick notes
- Documentation updated and committed (2025-11-11).

Manual test instructions
- [ ] Manual test steps for DirectorySelector dialog and sidebar/edit workflow still to be added (see `src/ui/controls/directory_selector.py` and `src/ui/panels/note_view.py`).

Notes
- Many registry keys are used for UI wiring; keep the naming convention `ui.<area>.<panel>.<action>` to simplify future toggles.

If you want, I can start implementing the Edit/Delete handlers next.