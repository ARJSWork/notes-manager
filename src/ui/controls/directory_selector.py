###
# File:   directory_selector.py
# Date:   2025-10-27
# Author: alexrjs, gemini
###

import flet as ft
import os
from os import path

class DirectorySelector(ft.Column):
    """A modal dialog to select a directory containing a 'collection.json' file."""

    def __init__(self, page, intitial_path, on_select_callback):
        """Initializes the DirectorySelector control.

        Args:
            page: The Flet page.
            on_select_callback: The callback function to call when a directory is selected.
        """
        super().__init__()
        self.page = page
        self.on_select_callback = on_select_callback
        self.selected_path = None
        self.intitial_path = intitial_path

        self.list_view = ft.ListView(expand=True, spacing=10)
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select a Collection"),
            content=ft.Container(
                content=self.list_view,
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.cancel_clicked),
                ft.FilledButton("Select", on_click=self.select_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def show(self):
        """Shows the directory selector dialog."""
        self.update_directory_list()
        self.page.open(self.dialog)

    def update_directory_list(self):
        """Finds directories containing 'collection.json' and updates the list view."""
        self.list_view.controls.clear()
        # Search for directories containing "collection.json"
        notes_dir = path.join(self.intitial_path) if self.intitial_path.endswith("notes") else "notes"  # Assuming 'notes' is the base directory
        for root, dirs, files in os.walk(notes_dir):
            if "collection.json" in files:
                dir_name = os.path.basename(root)
                self.list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(dir_name),
                        on_click=self.list_tile_clicked,
                        data=root,
                    )
                )
        self.page.update()

    def list_tile_clicked(self, e):
        """Handles the click event of a list tile."""
        for tile in self.list_view.controls:
            tile.selected = False
        e.control.selected = True
        self.selected_path = e.control.data
        self.page.update()


    def cancel_clicked(self, e):
        """Handles the click event of the cancel button."""
        self.page.close(self.dialog)
        self.page.update()

    def select_clicked(self, e):
        """Handles the click event of the select button."""
        if self.selected_path:
            self.on_select_callback(self.selected_path)
            self.page.close(self.dialog)
            self.page.update()
