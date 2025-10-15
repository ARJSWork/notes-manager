###
# File:   src\ui\dialogs\file.py
# Date:   2025-01-27 / 12:44
# Author: alexrjs
###


# imports
from os import getcwd, path
from json import loads
from flet import FilePicker, FilePickerResultEvent, FilePickerFileType, Page
from db import register, registry
from db.messages import getError


# constants


# variables


# functions/classes
def showOpen(page: Page, callback:callable, state:str=None) -> None:
    """Open a file open dialog."""

    def pick_files_result(e: FilePickerResultEvent) -> None:
        #_files = ", ".join(map(lambda f: f.path, e.files)) if e.files else "Cancelled!"
        if not e.files:
            return
        
        _name = e.files[0].name
        _path = e.files[0].path
        if _path:
            _path = e.files[0].path.lower().replace(" ", "_")
        
        else:
            if not e.page.web:
                print("Cannot figure out the path!")
                return

            _path = path.join(start_directory, _name.lower().replace(" ", "_"))

        register("notesFile", _path)
        register("notesName", path.basename(_name.split(".")[0]))
        if callback:
            callback(page, state)

    # Definiere das Startverzeichnis
    start_directory = path.join(getcwd(), "notes")
    
    # Öffne den Dateidialog
    _dialog = FilePicker(on_result=pick_files_result)
    page.overlay.append(_dialog)
    page.update()

    _dialog.pick_files(
        dialog_title="Select a note JSON file",
        allowed_extensions=["json"],
        file_type=FilePickerFileType.CUSTOM,
        initial_directory=start_directory,
        allow_multiple=False
    )

def showSave(page: Page, callback:callable, state:str=None, overrides_:dict=None) -> None:
    """Open a file save dialog."""

    def pick_files_result(e: FilePickerResultEvent) -> None:
        #_files = ", ".join(map(lambda f: f.path, e.files)) if e.files else "Cancelled!"
        if not e.path:
            return
        
        if callback:
            callback(page, state, loads(e.data))

    # Definiere das Startverzeichnis
    if not overrides_:
        _folder = path.dirname(registry.notesFile)
        _filename = path.basename(registry.notesFile)
        start_directory = path.join(getcwd(), _folder)

    else:
        assert overrides_, getError("A000")
        assert "folder" in overrides_, getError("A000")
        assert "filename" in overrides_, getError("A000")
        _folder = overrides_["folder"]
        _filename = overrides_["filename"]
        if "extension" in overrides_:
            _filename += "." + overrides_["extension"]
        else:
            _filename += ".txt"

        start_directory = path.join(getcwd(), _folder)

    # Öffne den Dateidialog
    _dialog = FilePicker(on_result=pick_files_result)
    page.overlay.append(_dialog)
    page.update()

    _dialog.save_file(
        dialog_title="Select a note JSON file",
        allowed_extensions=["json"],
        file_type=FilePickerFileType.CUSTOM,
        initial_directory=start_directory,
        file_name=_filename
    )

def showOpenCollection(page: Page, callback:callable, state:str=None) -> None:
    """Open a directory selection dialog for collections."""

    def get_directory_result(e: FilePickerResultEvent) -> None:
        if not e.path:
            return
        
        _path = e.path
        register("notesFile", _path)
        register("notesName", path.basename(_path))
        if callback:
            callback(page, state)

    # Definiere das Startverzeichnis
    # Default to top-level notes folder (next to src)
    start_directory = path.join(getcwd(), "notes")
    
    # Öffne den Dateidialog
    _dialog = FilePicker(on_result=get_directory_result)
    page.overlay.append(_dialog)
    page.update()

    _dialog.get_directory_path(
        dialog_title="Select a notes collection folder",
        initial_directory=start_directory,
    )