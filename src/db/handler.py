###
# File:   src\db\json_handler.py
# Date:   2025-07-10
# Author: Gemini
###

import json
import os
import shutil
import types
from dataclasses import asdict, is_dataclass
from models.notes import NotesCollection, MeetingNote

class DataclassJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder for dataclasses."""
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

def create_default_collection(name: str) -> NotesCollection:
    """Creates a new NotesCollection with default values."""
    return NotesCollection(name=name)

def save_notes_collection(collection: NotesCollection, filepath: str) -> None:
    """
    Saves the NotesCollection to a JSON file.
    Creates a backup of the previous file if it exists.
    """
    # Create a backup
    if os.path.exists(filepath):
        backup_path = filepath + ".bak"
        shutil.copy2(filepath, backup_path)
        print(f"Backup of '{filepath}' created at '{backup_path}'")

    # Save the new data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(collection, f, cls=DataclassJSONEncoder, indent=4)
    print(f"Notes collection saved to '{filepath}'")

def load_notes_collection(directory_path: str) -> NotesCollection | None:
    """
    Loads a notes collection from a directory.
    Returns None if the directory or collection.json does not exist.
    """
    json_filepath = os.path.join(directory_path, "collection.json")
    if not os.path.exists(json_filepath):
        return None

    with open(json_filepath, 'r', encoding='utf-8') as f:
        collection_data = json.load(f)

    collection = NotesCollection(
        name=collection_data.get("collection_name", ""),
        created_at=collection_data.get("created_at", ""),
        categories=collection_data.get("categories", []),
        tags=collection_data.get("tags", []),
        locations=collection_data.get("locations", [])
    )

    for note_meta in collection_data.get("notes", []):
        note_filepath = os.path.join(directory_path, note_meta["filename"])
        if os.path.exists(note_filepath):
            try:
                with open(note_filepath, 'r', encoding='utf-8') as f:
                    # Try to parse JSON note files created by the new save flow
                    try:
                        note_json = json.load(f)
                        note_content = note_json.get("content", "")
                        note_title = note_json.get("title", note_meta.get("title", ""))
                        note_time = note_json.get("time")
                        note_created = note_json.get("created_at")
                    except Exception:
                        # Fallback: plain text note file
                        f.seek(0)
                        note_content = f.read()
                        note_title = note_meta.get("title", "")
                        note_time = None
                        note_created = None

                note = MeetingNote(
                    title=note_title,
                    content=note_content,
                    category="", # category and tags are not stored per note in the new format
                    tags=[]
                )
                # Attach optional metadata to the note object for UI/persistence
                try:
                    if note_time:
                        note.time = note_time
                except Exception:
                    pass
                try:
                    if note_created:
                        note.created_at = note_created
                except Exception:
                    pass
                collection.notes.append(note)
            except Exception as _e:
                print(f"Error loading note file '{note_filepath}': {_e}")
                # skip problematic note and continue
                continue
    
    print(f"Notes collection loaded from '{directory_path}'")
    return collection