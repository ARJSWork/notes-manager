###
# File:   src\/logic\/persistence.py
# Date:   2025-10-07
# Author: Gemini
###

import os
import json
import re
import shutil
import tempfile
import traceback
from datetime import datetime
from typing import Union, List, Tuple

from models.notes import NotesCollection, MeetingNote, Module, Template

def slugify(text: str) -> str:
    """Converts a string to a slug suitable for filenames.
    
    Replaces spaces with underscores, removes invalid characters.
    """
    text = text.replace(' ', '_')
    text = re.sub(r'[^\w_.]', '', text)
    return text

def _serialize_note_content(note_content: Union[List[str], Template, List[Module], str]) -> str:
    """Serializes a note's content to a markdown-like string."""
    if isinstance(note_content, str):
        return note_content

    if isinstance(note_content, list) and all(isinstance(i, str) for i in note_content):
        return "\n".join(note_content)

    if isinstance(note_content, list) and all(isinstance(i, Module) for i in note_content):
        parts = []
        for module in note_content:
            parts.append(f"## {module.name}")
            if module.content:
                parts.append("\n".join(module.content))
        return "\n".join(parts)
    
    # Fallback for other types like Template, though not fully implemented.
    return ""

def save_collection(collection: NotesCollection, data_root: str) -> Tuple[bool, str]:
    """Saves the entire notes collection to the disk atomically.

    Returns (True, message) on success, or (False, error_message) on failure.
    The implementation creates a backup of the current collection directory (if it exists),
    writes each note to a temporary file and then atomically replaces files. On error,
    it attempts to roll back to the backup.
    """
    try:
        if not collection or not collection.name:
            return False, "Invalid collection object or collection name."

        collection_slug = slugify(collection.name)
        # Store collections directly under DATA_ROOT
        collection_path = os.path.join(data_root, collection_slug)
        os.makedirs(data_root, exist_ok=True)

        # Create a backup of existing collection folder to allow rollback
        backup_path = None
        if os.path.exists(collection_path):
            ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            backup_path = f"{collection_path}.bak_{ts}"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(collection_path, backup_path)

        # Ensure collection folder exists (create if missing)
        os.makedirs(collection_path, exist_ok=True)

        notes_metadata = []
        saved_filenames = set()

        for note in collection.notes:
            if not getattr(note, "title", None):
                continue  # Skip notes without a title

            base_filename = slugify(getattr(note, "title", "note")) or "note"
            # Append time to filename if available in note.time
            # note_time = getattr(note, "time", None)
            # time_part = ""
            # if note_time:
            #     # Expect times like '10:00' -> '1000'
            #     t = re.sub(r"[^0-9]", "", str(note_time))
            #     if t:
            #         time_part = f"_{t}"
            # note_filename = f"{base_filename}{time_part}.json"

            # Handle filename collisions (also consider existing files)
            counter = 2
            note_filename = f"{base_filename}.json"
            while note_filename in saved_filenames or os.path.exists(os.path.join(collection_path, note_filename)):
                note_filename = f"{base_filename}_{counter}.json"
                counter += 1
            saved_filenames.add(note_filename)

            note_filepath = os.path.join(collection_path, note_filename)
            tmp_filepath = f"{note_filepath}.tmp"

            try:
                # Build a structured representation for the note using stored metadata
                # Prefer explicit fields (topic, notes, participants, etc.) where available
                note_title = getattr(note, "title", "")
                note_created = getattr(note, "created_at", None)
                note_notes = getattr(note, "notes", None)
                # If user provided a concise notes field, use it as content; otherwise try to extract Notes section
                # content_value = ""
                # if note_notes:
                #     content_value = note_notes
                # else:
                #     content_value = getattr(note, "content", "")

                # # Extract todos/checklist lines from the content (lines with '- [' )
                # todos = []
                # try:
                #     for ln in str(content_value).splitlines():
                #         if ln.strip().startswith("- [") or ln.strip().startswith("[ ]"):
                #             todos.append(ln.strip())
                # except Exception:
                #     todos = []

                # Build final structured representation
                note_struct = {
                    "title": note_title,
                    "created_at": note_created,
                    "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                    "topic": getattr(note, 'topic', None) or None,
                    "date": getattr(note, 'date', None) or None,
                    "time": getattr(note, 'time', None) or None,
                    "location": getattr(note, 'location', None) or None,
                    "participants": [p for p in (getattr(note, 'participants', []) or [])],
                    "notes": getattr(note, 'notes', None) or None,
                    "todos": getattr(note, 'todos', []) or None
                }

                # Write JSON note file atomically
                with open(tmp_filepath, 'w', encoding='utf-8') as f:
                    json.dump(note_struct, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())

                # Atomically replace tmp -> final
                os.replace(tmp_filepath, note_filepath)

                notes_metadata.append({
                    "title": getattr(note, "title", ""),
                    "filename": note_filename
                })

            except Exception as e:
                # Cleanup tmp file
                if os.path.exists(tmp_filepath):
                    try:
                        os.remove(tmp_filepath)
                    except Exception:
                        pass
                # Rollback to backup if available
                if backup_path and os.path.exists(backup_path):
                    try:
                        if os.path.exists(collection_path):
                            shutil.rmtree(collection_path)
                        shutil.copytree(backup_path, collection_path)
                    except Exception as _re:
                        return False, f"Failed while writing note '{note_filename}': {e}; rollback failed: {_re}"
                return False, f"Failed while writing note '{note_filename}': {e}"

        # Create and save collection.json
        now = datetime.utcnow().isoformat() + "Z"
        collection_json_content = {
            "collection_name": collection.name,
            "slug": collection_slug,
            "created_at": getattr(collection, "created_at", now),
            "updated_at": now,
            "notes": notes_metadata,
            "note_count": len(notes_metadata)
        }

        # Also save other metadata from NotesCollection if available
        collection_json_content["categories"] = getattr(collection, "categories", [])
        collection_json_content["tags"] = getattr(collection, "tags", [])
        collection_json_content["locations"] = getattr(collection, "locations", [])

        json_filepath = os.path.join(collection_path, "collection.json")
        tmp_json_filepath = f"{json_filepath}.tmp"

        try:
            with open(tmp_json_filepath, 'w', encoding='utf-8') as f:
                json.dump(collection_json_content, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_json_filepath, json_filepath)

        except Exception as e:
            # Cleanup tmp json
            if os.path.exists(tmp_json_filepath):
                try:
                    os.remove(tmp_json_filepath)
                except Exception:
                    pass
            # Rollback to backup if present
            if backup_path and os.path.exists(backup_path):
                try:
                    if os.path.exists(collection_path):
                        shutil.rmtree(collection_path)
                    shutil.copytree(backup_path, collection_path)
                except Exception as _re:
                    return False, f"Failed writing collection.json: {e}; rollback failed: {_re}"
            return False, f"Failed writing collection.json: {e}"

        return True, f"Successfully saved collection '{collection.name}' to '{collection_path}'."

    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Unexpected error during save: {e}\n{tb}"
    
    finally:
        # If we get here, the save was successful. Remove backup if it exists.
        if backup_path and os.path.exists(backup_path):
            try:
                shutil.rmtree(backup_path)
            except Exception:
                pass
