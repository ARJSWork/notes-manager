###
# File:   src\/logic\/persistence.py
# Date:   2025-10-07
# Author: Gemini
###

import re
import json
import unicodedata
from os import path, rename, remove, makedirs, listdir, fsync, replace
from datetime import datetime, timezone
from traceback import format_exc
from typing import Tuple
from db import registry
from config.config import DATA_ROOT
from models.notes import NotesCollection, MeetingNote

def slugify(text: str) -> str:
    """Converts a string to a slug suitable for filenames.
    
    Replaces spaces with underscores, removes invalid characters.
    """
    if not text:
        return ''
    
    text = text.strip()
    # Normalize unicode to closest ASCII
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Replace spaces and common separators with underscore
    text = re.sub(r'[\s/\\]+', '_', text)
    # Remove any character that is not alphanumeric or underscore (removes (,)./ etc.)
    text = re.sub(r'[^\w]', '', text)
    # Collapse multiple underscores and trim
    text = re.sub(r'_+', '_', text).strip('_')
    # Fallback to a timestamped name if empty
    if not text:
        text = datetime.utcnow().strftime('note_%Y%m%dT%H%M%SZ')
    return text


def rename_note_file(old_title: str, new_title: str) -> Tuple[bool, str]:
    """Renames a note file based on a new title.

    Returns (True, new_path) on success or (False, error_msg).
    """
    try:
        collection_slug = slugify(registry.notes_collection.name)
        collection_path = path.join(DATA_ROOT, collection_slug)

        old_path = f"{path.join(collection_path, old_title)}.json"
        if not path.exists(old_path):
            return False, f"Old path does not exist: {old_path}"

        new_path = f"{path.join(collection_path, new_title)}.json"
        if path.exists(new_path):
            return False, f"Target file already exists: {new_title}"

        rename(old_path, new_path)
        return True, new_path
    except Exception as e:
        tb = format_exc()
        return False, f"Failed to rename note file: {e}\n{tb}"


def update_notes(collection: NotesCollection, collection_path: str = None, check_exists: bool = False) -> Tuple[bool, str]:
    """Update all note files in the collection to match their current titles.

    Returns (True, message) on success or (False, error_msg).
    """
    try:
        if not collection or not collection.name:
            return False, "Invalid collection"

        if not collection_path:
            collection_slug = slugify(collection.name)
            collection_path = path.join(DATA_ROOT, collection_slug)

        # Ensure collection.json exists
        json_filepath = path.join(collection_path, "collection.json")
        if check_exists and not path.exists(json_filepath):
            return False, f"collection.json does not exist at {json_filepath}"
        
        # After saving notes, update collection.json
        okc, msgc = True, ""
        try:
            # reuse collection.json writing from save_collection: build metadata
            notes_metadata = []
            for note in collection.notes:
                # find file by title/date/time-based naming - best-effort
                base_filename = slugify(getattr(note, 'title', 'note')) or 'note'
                filename = f"{base_filename}.json"
                if not path.exists(path.join(collection_path, filename)):
                    # fallback: pick any matching by prefix
                    for f in listdir(collection_path):
                        if f.startswith(base_filename):
                            filename = f
                            break

                notes_metadata.append({
                    "title": getattr(note, 'title', ''),
                    "filename": filename
                })

            now = f"{datetime.now(tz=timezone.utc).isoformat()}Z"
            collection_slug = slugify(collection.name)
            collection_json_content = {
                "collection_name": collection.name,
                "slug": collection_slug,
                "created_at": getattr(collection, "created_at", now),
                "updated_at": now,
                "notes": notes_metadata,
                "note_count": len(notes_metadata),
                "categories": getattr(collection, "categories", []),
                "tags": getattr(collection, "tags", []),
                "locations": getattr(collection, "locations", []),
            }

            json_filepath = path.join(collection_path, "collection.json")
            tmp_json = json_filepath + '.tmp'

            backup_path = path.join(collection_path, f"collection.json.bak")
            if path.exists(backup_path):
                remove(backup_path)

            if path.exists(json_filepath):
                rename(json_filepath, backup_path)

            with open(tmp_json, 'w', encoding='utf-8') as f:
                json.dump(collection_json_content, f, indent=4, ensure_ascii=False)
                f.flush()
                fsync(f.fileno())

            replace(tmp_json, json_filepath)

        except Exception as e:
            okc = False
            msgc = str(e)

        return True, f"Notes saved; collection updated: {msgc}" if okc else (False, f"Failed updating collection.json: {msgc}")

    except Exception as e:
        tb = format_exc()
        return False, f"Error in update_notes: {e}\n{tb}"


def _serialize_note_for_write(note: MeetingNote) -> dict:
    """Return a dict representation of a MeetingNote for JSON writing."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    notes = getattr(note, 'notes', None) or None
    if notes is None:
        _notes = []
    else:
        _notes = notes.splitlines()

    todos = note.todos or []
    if todos is None:
        _todos = []
    else:
        _todos = _todos.splitlines()

    return {
        "title": note.title,
        "created_at": note.created_at,
        "updated_at": note.updated_at or now,
        "topic": getattr(note, 'topic', None) or None,
        "date": getattr(note, 'date', None) or None,
        "time": getattr(note, 'time', None) or None,
        "location": getattr(note, 'location', None) or None,
        "participants": [p for p in (getattr(note, 'participants', []) or [])],
        "notes": _notes, 
        "todos": todos,
    }


def save_note(note: MeetingNote, collection_path: str) -> Tuple[bool, str]:
    """Save a single MeetingNote if its `dirty` flag is True.

    Returns (True, message) on success or (False, error_msg).
    """
    try:
        if not getattr(note, 'dirty', False):
            return True, "Skipped (not dirty)"

        # Prepare filename
        base_filename = slugify(getattr(note, 'title', 'note')) or 'note'
        filename = f"{base_filename}.json"
        
        dst = path.join(collection_path, filename)
        tmp = dst + '.tmp'

        backup_path = path.join(collection_path, f"{filename}.bak")
        if path.exists(backup_path):
            remove(backup_path)
        
        if path.exists(dst):
            rename(dst, backup_path)

        data = _serialize_note_for_write(note)
        # atomic write
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            fsync(f.fileno())
        replace(tmp, dst)
        try:
            note.clear_dirty()
        except Exception:
            pass
        return True, f"Saved note to {dst}"
    except Exception as e:
        tb = format_exc()
        return False, f"Failed to save note: {e}\n{tb}"


def save_notes(collection: NotesCollection, data_root: str) -> Tuple[bool, str]:
    """Save only notes marked dirty in the collection.

    Writes individual note files and updates collection.json.
    """
    try:
        if not collection or not collection.name:
            return False, "Invalid collection"

        collection_slug = slugify(collection.name)
        collection_path = path.join(data_root, collection_slug)
        makedirs(collection_path, exist_ok=True)

        # Save all dirty notes
        results = []
        for note in collection.notes:
            if not note.dirty:
                continue

            ok, msg = save_note(note, collection_path)
            results.append((ok, msg))

        # After saving notes, update collection.json
        okc, msgc = update_notes(collection, collection_path)
        if not okc:
            return False, "Some notes failed to save:\n" + "\n".join(msgc)
        
        return True, "All dirty notes saved successfully."

    except Exception as e:
        tb = format_exc()
        return False, f"Error in save_changed_notes: {e}\n{tb}"


def save_collection_view(collection: NotesCollection, data_root: str) -> Tuple[bool, str]:
    """Force an update of collection.json (index) without touching note files."""
    try:
        if not collection or not collection.name:
            return False, "Invalid collection"
        collection_slug = slugify(collection.name)
        collection_path = path.join(data_root, collection_slug)
        makedirs(collection_path, exist_ok=True)

        notes_metadata = []
        for note in collection.notes:
            base_filename = slugify(getattr(note, 'title', 'note')) or 'note'
            time_part = ''
            if getattr(note, 'time', None):
                t = re.sub(r"[^0-9]", "", str(getattr(note, 'time')))
                if t:
                    time_part = f"_{t}"
            filename = f"{base_filename}{time_part}.json"
            if not path.exists(path.join(collection_path, filename)):
                for f in listdir(collection_path):
                    if f.startswith(base_filename):
                        filename = f
                        break
            notes_metadata.append({
                "title": getattr(note, 'title', ''),
                "filename": filename
            })

        now = datetime.utcnow().isoformat() + "Z"
        collection_json_content = {
            "collection_name": collection.name,
            "slug": collection_slug,
            "created_at": getattr(collection, "created_at", now),
            "updated_at": now,
            "notes": notes_metadata,
            "note_count": len(notes_metadata),
            "categories": getattr(collection, "categories", []),
            "tags": getattr(collection, "tags", []),
            "locations": getattr(collection, "locations", []),
        }

        json_filepath = path.join(collection_path, "collection.json")
        tmp_json = json_filepath + '.tmp'
        with open(tmp_json, 'w', encoding='utf-8') as f:
            json.dump(collection_json_content, f, indent=4, ensure_ascii=False)
            f.flush()
            fsync(f.fileno())
        replace(tmp_json, json_filepath)
        return True, f"collection.json updated at {json_filepath}"
    except Exception as e:
        tb = format_exc()
        return False, f"Failed to update collection view: {e}\n{tb}"
    
    # end save_collection
