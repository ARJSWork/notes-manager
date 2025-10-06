###
# File:   src\models\notes.py
# Date:   2025-07-10
# Author: Gemini
###

from dataclasses import dataclass, field
from typing import List, Union

# Default values as specified
DEFAULT_CATEGORIES = ["Standard", "Official", "Information", "Consulting"]
DEFAULT_TAGS = ["BR", "GBR", "KBR", "ITA", "VG", "AG", "COM"]
DEFAULT_MODULES = ["Topic", "Participants", "Date", "Time", "Location", "Notes"]
DEFAULT_TEMPLATES = {
    "Quick": {
        "modules": ["Topic", "Date", "Time", "Participants", "Location", "Notes"],
        "Notes": ["- Bulletpoint 1", "- Bulletpoint 2", "## Subtitle", "- [ ] ToDo 1"]
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
    # The content can be one of these types
    content: Union[List[str], Template, List[Module]] = field(default_factory=list)

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

