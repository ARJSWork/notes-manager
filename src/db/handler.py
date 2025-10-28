###
# File:   src\db\json_handler.py
# Date:   2025-07-10
# Author: Gemini
###

import json
import logging
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
        logging.info(f"Backup of '{filepath}' created at '{backup_path}'")

    # Save the new data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(collection, f, cls=DataclassJSONEncoder, indent=4)
    logging.info(f"Notes collection saved to '{filepath}'")

def load_notes_collection(directory_path: str) -> NotesCollection | None:
    """
    Loads a notes collection from a directory.
    Returns None if the directory or collection.json does not exist.
    """
    json_filepath = os.path.join(directory_path, "collection.json")
    try:
        if not os.path.exists(json_filepath):
            logging.error(f"Collection file '{json_filepath}' does not exist.")
            return None

        with open(json_filepath, 'r', encoding='utf-8') as f:
            collection_data = json.load(f)

        collection = NotesCollection.from_dict(collection_data)
    except Exception as e:
        logging.exception(f"Failed to load collection from '{json_filepath}': {e}")
        return None

    for note_meta in collection_data.get("notes", []):
        note_filepath = os.path.join(directory_path, note_meta["filename"])
        if os.path.exists(note_filepath):
            try:
                with open(note_filepath, 'r', encoding='utf-8') as f:
                    # Parse JSON note files created by the new save flow
                    try:
                        note_json = json.load(f)
                    except Exception as e:
                        logging.error(f"Error parsing JSON note '{note_filepath}': {e}")
                        # Do not silently accept malformed files; skip and report
                        continue

                try:
                    note = MeetingNote.from_dict(note_json)
                except Exception as e:
                    logging.error(f"Invalid note data in '{note_filepath}': {e}")
                    # Skip malformed note files rather than fabricating content
                    continue

                collection.notes.append(note)
            except Exception as _e:
                logging.exception(f"Error loading note file '{note_filepath}'")
                # skip problematic note and continue
                continue
    
    logging.info(f"Notes collection loaded from '{directory_path}'")
    return collection