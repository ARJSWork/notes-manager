TODO for Notes Manager
Last updated: 2025-09-08

High priority
- [x] Implement header Edit (rename) for Meeting Notes (open small dialog, validate, save title).  # Done
- [ ] Implement floating Edit button for full note edit (toggle display/edit mode in main area).  # Pending
- [ ] Implement Delete action for Meeting Notes (confirm and remove from list and storage).
- [ ] Persist notes to storage (save/load NotesCollection) and wire menu Save/Open.

Medium priority
- [ ] Convert Modules and Categories panels into selectable lists (like Templates) and wire their actions.
- [ ] Remove or reduce debug prints; add a simple logging facility.
- [ ] Add a small automated test that validates dialog -> callback -> sidebar append flow (unit/integration test using a headless flet or mock).

Low priority / Nice-to-have
- [ ] Add changelog/README entry summarizing the UI behavior.
- [ ] Add keyboard navigation and accessibility tweaks for the sidebar.
- [ ] Improve template rendering: support markdown rendering in main content area.

Notes
- Many registry keys are used for UI wiring; keep the naming convention `ui.<area>.<panel>.<action>` to simplify future toggles.

If you want, I can start implementing the Edit/Delete handlers next.
