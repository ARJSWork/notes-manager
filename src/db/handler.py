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
from models.notes import NotesCollection

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


def load_notes_collection(filepath: str) -> types.SimpleNamespace | None:
    """
    Loads a notes collection from a JSON file into a SimpleNamespace.
    Returns None if the file does not exist.
    """
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f, object_hook=lambda d: types.SimpleNamespace(**d))
    
    print(f"Notes collection loaded from '{filepath}'")
    return data
