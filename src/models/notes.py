###
# File:   src\models\notes.py
# Date:   2025-07-10
# Author: Gemini
###

from dataclasses import dataclass, field
from typing import List, Union, Optional
from datetime import datetime, timezone

# Default values as specified
DEFAULT_CATEGORIES = ["Standard", "Official", "Information", "Consulting"]
DEFAULT_TAGS = ["BR", "GBR", "KBR", "ITA", "VG", "AG", "COM"]
DEFAULT_MODULES = ["Topic", "Participants", "Date", "Time", "Location", "Notes", "ToDos"]
DEFAULT_TEMPLATES = {
    "Quick": {
        "modules": ["Topic", "Date", "Time", "Participants", "Location", "Notes", "ToDos"],
        "Participants": ["Alex S"],
        "Notes": [],
        "ToDos": []
    }
}

@dataclass
class Module:
    """A Module contains a name and a list of text entries."""
    name: str
    content: List[str] = field(default_factory=list)

@dataclass
class Template:
    """A Template is composed of one or more Modules."""
    name: str
    modules: List[Module] = field(default_factory=list)

@dataclass
class MeetingNote:
    """
    A MeetingNote holds the main content.
    The content can be simple text, a template, or a list of modules.
    """
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    # The content can be one of these types (legacy / fallback)
    content: Union[List[str], Template, List[Module], str] = field(default_factory=list)

    # Structured fields (one field per module) for easier persistence and flexibility
    topic: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    participants: List[str] = field(default_factory=list)
    notes: str = ""
    todos: List[str] = field(default_factory=list)
    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Dirty flag for optimized saving
    dirty: bool = False

    def mark_dirty(self) -> None:
        """Mark this note as modified and needing save."""
        try:
            self.dirty = True
        except Exception:
            pass

    def clear_dirty(self) -> None:
        """Clear the dirty flag after successful save."""
        try:
            self.dirty = False
        except Exception:
            pass

    @classmethod
    def from_dict(cls, data: dict) -> "MeetingNote":
        """Construct a MeetingNote from a dictionary produced by the on-disk JSON format.

        Raises ValueError or TypeError when data is invalid. This enforces strict
        loading: malformed files will not be silently converted to a placeholder
        note.
        """
        if not isinstance(data, dict):
            raise TypeError("note data must be a dict")

        title = data.get("title") or data.get("topic") or data.get("Topic")
        if not title:
            raise ValueError("Missing required field 'title' in note JSON")

        category = data.get("category", "")
        tags = data.get("tags", []) or []

        # content may be called 'content' or fallback to 'body'
        # content = data.get("content", data.get("body", ""))

        topic = data.get("topic") or data.get("Topic")
        date = data.get("date") or data.get("Date")
        time = data.get("time") or data.get("Time")
        location = data.get("location") or data.get("Location")

        participants = data.get("participants", []) or []
        # normalize participants: allow comma/newline separated strings
        if isinstance(participants, str):
            parts = [p.strip() for p in participants.replace(';', '\\n').splitlines() if p.strip()]
            participants = parts
        elif not isinstance(participants, (list, tuple)):
            participants = []

        notes = data.get("notes", "") or ""
        todos = data.get("todos", []) or []
        if isinstance(todos, str):
            todos = [line.strip() for line in todos.splitlines() if line.strip()]
        elif not isinstance(todos, list):
            todos = []

        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        return cls(
            title=title,
            category=category,
            tags=list(tags),
            #content=content,
            topic=topic,
            date=date,
            time=time,
            location=location,
            participants=list(participants),
            notes=notes,
            todos=list(todos),
            created_at=created_at,
            updated_at=updated_at,
        )

@dataclass
class NotesCollection:
    """The root object for a notes file, containing all notes, categories, and tags."""
    name: str
    notes: List[MeetingNote] = field(default_factory=list)
    categories: List[str] = field(default_factory=lambda: list(DEFAULT_CATEGORIES))
    tags: List[str] = field(default_factory=lambda: list(DEFAULT_TAGS))
    modules: List[Module] = field(default_factory=lambda: [Module(name=name) for name in DEFAULT_MODULES])
    templates: List[Template] = field(default_factory=lambda: [Template(name=t_name, modules=[Module(name=m_name, content=DEFAULT_TEMPLATES[t_name].get(m_name, [])) for m_name in DEFAULT_TEMPLATES[t_name]["modules"]]) for t_name in DEFAULT_TEMPLATES])
    locations: List[str] = field(default_factory=lambda: ["Online", "Office", "Conference Room"])
    created_at: str = field(default_factory=lambda: f"{datetime.now(timezone.utc).isoformat()}Z")
    updated_at: str = field(default_factory=lambda: f"{datetime.now(timezone.utc).isoformat()}Z")

    @classmethod
    def from_dict(cls, data: dict) -> "NotesCollection":
        """Construct a NotesCollection from a dict (collection.json).

        Raises TypeError/ValueError on invalid input.
        """
        if not isinstance(data, dict):
            raise TypeError("collection data must be a dict")

        name = data.get("collection_name") or data.get("name") or data.get("slug")
        if not name:
            raise ValueError("Missing 'collection_name' in collection.json")

        coll = cls(name=name)
        coll.created_at = data.get("created_at") or coll.created_at
        coll.updated_at = data.get("updated_at") or coll.updated_at
        coll.categories = list(data.get("categories", []) or [])
        coll.tags = list(data.get("tags", []) or [])
        coll.locations = list(data.get("locations", []) or [])

        # Notes list is handled by loader which will append MeetingNote instances.
        return coll

