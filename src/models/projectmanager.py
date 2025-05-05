###
# File:   src\models\projectmanager.py
# Date:   2025-01-29 / 10:37
# Author: alexrjs (modified)
###


# imports
from os import getcwd, path, remove, rename
from json import load, dump
from datetime import datetime
from db import registry


# constants


# variables


# functions/classes
class ProjectManager:
    """Class to manage project templates."""

    def __init__(self, json_file:str=None):
        """Initialize the ProjectManager with a JSON file."""

        self.controls = {}
        self.json_file = json_file
        self.status = "New"
        self.data = {
            "templates": [],
            "modules": [],
            "meetings": [],
        }

    def load(self) -> dict:
        """Load data from the JSON file."""

        if not path.exists(self.json_file):
            raise FileNotFoundError(f"{self.json_file} not found.")
        
        with open(self.json_file, 'r') as _file:
            _data = load(_file)
            self.status = "Loaded"
            self.data["templates"] = _data.get("templates", [])
            self.data["modules"] = _data.get("modules", [])
            self.data["meetings"] = _data.get("meetings", [])
            return _data

    def save(self) -> None:
        """Save templates to the JSON file."""

        if not registry.projectFile:
            raise ValueError("JSON file is required.")
        
        if self.status not in ["Changed", "New"] and not registry.changed:
            return

        # Create a backup of the existing file if it exists
        #_folder = path.dirname(registry.projectFile)
        #_filename = path.basename(registry.projectFile)
        _filePath = path.join(getcwd(), registry.projectFile)
        if path.exists(_filePath):
            _backup_file = _filePath + ".bak"
            if path.exists(_backup_file):                
                remove(_backup_file)

            rename(_filePath, _backup_file)

        self.data["update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(_filePath, 'w') as file:
            dump(self.data, file, indent=4)

        self.status = "Saved"
        del self.data["update"]

    def get_template(self, template_id: str) -> dict:
        """Get a template by ID."""

        if not template_id:
            return None

        for _template in self.data["templates"]:
            if _template.get("id") == template_id:
                return _template

        return None

    def add_template(self, template: dict) -> None:
        """Add a new template."""

        self.data["templates"].append(template)
        self.status = "Changed"

    def update_template(self, template_id: str, updated_template: dict) -> bool:
        """Update an existing template."""

        if not template_id:
            raise ValueError("Template ID is required.")
        
        if not updated_template:
            raise ValueError("Template is required.")
    
        for _index, _template in enumerate(self.data["templates"]):
            if _template.get("id") == template_id:
                self.data["templates"][_index] = updated_template
                self.status = "Changed"
                return True
            
        return False

    def delete_template(self, template_id: str) -> bool:
        """Delete a template by ID."""

        if not template_id:
            raise ValueError("Template ID is required.")
        
        _original_len = len(self.data["templates"])
        self.data["templates"] = [_template for _template in self.data["templates"] if _template.get("id") != template_id]
        if len(self.data["templates"]) < _original_len:
            self.status = "Changed"
            return True
        
        return False

    def get_module(self, module_id: str) -> dict:
        """Get a module by ID."""

        if not module_id:
            return None

        for _module in self.data["modules"]:
            if _module.get("id") == module_id:
                return _module

        return None

    def add_module(self, module: dict) -> None:
        """Add a new module."""

        self.data["modules"].append(module)
        self.status = "Changed"

    def update_module(self, module_id: str, updated_module: dict) -> bool:
        """Update an existing module."""

        if not module_id:
            raise ValueError("Module ID is required.")
        
        if not updated_module:
            raise ValueError("Module is required.")
    
        for _index, _module in enumerate(self.data["modules"]):
            if _module.get("id") == module_id:
                self.data["modules"][_index] = updated_module
                self.status = "Changed"
                return True
            
        return False

    def delete_module(self, module_id: str) -> bool:
        """Delete a module by ID."""

        if not module_id:
            raise ValueError("Module ID is required.")
        
        _original_len = len(self.data["modules"])
        self.data["modules"] = [_module for _module in self.data["modules"] if _module.get("id") != module_id]
        if len(self.data["modules"]) < _original_len:
            self.status = "Changed"
            return True
        
        return False

    def get_meeting(self, meeting_id: str) -> dict:
        """Get a meeting by ID."""

        if not meeting_id:
            return None

        for _meeting in self.data["meetings"]:
            if _meeting.get("id") == meeting_id:
                if "name1" in _meeting:
                    del _meeting["name1"]
                    
                if "description1" in _meeting:
                    del _meeting["description1"]
                    
                return _meeting

        return None

    def add_meeting(self, meeting: dict) -> None:
        """Add a new meeting."""

        self.data["meetings"].append(meeting)
        self.status = "Changed"

    def update_meeting(self, meeting_id: str, updated_meeting: dict) -> bool:
        """Update an existing meeting."""

        if not meeting_id:
            raise ValueError("Meeting ID is required.")
        
        if not updated_meeting:
            raise ValueError("Meeting is required.")
        
        for _index, _meeting in enumerate(self.data["meetings"]):
            if _meeting.get("id") == meeting_id:
                self.data["meetings"][_index] = updated_meeting
                self.status = "Changed"
                return True
            
        return False

    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting by ID."""

        if not meeting_id:
            raise ValueError("Meeting ID is required.")
        
        _original_len = len(self.data["meetings"])
        self.data["meetings"] = [_meeting for _meeting in self.data["meetings"] if _meeting.get("id") != meeting_id]
        if len(self.data["meetings"]) < _original_len:
            self.status = "Changed"
            return True
        
        return False