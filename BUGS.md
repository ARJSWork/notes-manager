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

11. Feature - Optimize the Save function, that only changed notes are saved. Maybe add a dirty flag. And also the collection view must be saved when notes are renamed or deleted or copied.

