###
# File:   custom_menu.py
# Date:   2025-10-06
# Author: alexrjs, gemini
###

import flet as ft

class CustomMenu(ft.Column):
    """A custom menu control with a dropdown, and an option to add new items."""

    def __init__(self, page, items, selected_item):
        """Initializes the CustomMenu control.

        Args:
            page: The Flet page.
            items: A list of items to display in the dropdown.
            selected_item: The initially selected item.
        """
        super().__init__()
        self.page = page
        self.items = items
        self.selected_item = selected_item

        self.dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(item) for item in self.items],
            value=self.selected_item,
        )
        self.add_button = ft.IconButton(
            icon=ft.Icons.ADD,
            on_click=self.add_clicked,
        )
        self.new_item_field = ft.TextField(
            visible=False, width=200, on_submit=self.confirm_clicked
        )
        self.confirm_button = ft.IconButton(
            icon=ft.Icons.CHECK,
            on_click=self.confirm_clicked,
            visible=False,
        )
        self.cancel_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self.cancel_clicked,
            visible=False,
        )

        self.controls = [
            ft.Row(
                controls=[
                    self.dropdown,
                    self.add_button,
                    self.new_item_field,
                    self.confirm_button,
                    self.cancel_button,
                ]
            )
        ]

    def add_clicked(self, e):
        """Handles the click event of the add button."""
        self.add_button.visible = False
        self.new_item_field.visible = True
        self.confirm_button.visible = True
        self.cancel_button.visible = True
        self.new_item_field.focus()
        self.page.update()

    def confirm_clicked(self, e):
        """Handles the click event of the confirm button."""
        new_item = self.new_item_field.value
        if len(new_item) >= 5:
            self.items.append(new_item)
            self.dropdown.options.append(ft.dropdown.Option(new_item))
            self.dropdown.value = new_item
            self.selected_item = new_item
            self.hide_new_item_widgets()
        else:
            self.new_item_field.error_text = "Item must be at least 5 characters long!"
            self.page.update()

    def cancel_clicked(self, e):
        """Handles the click event of the cancel button."""
        self.hide_new_item_widgets()

    def hide_new_item_widgets(self):
        """Hides the new item widgets and resets the text field."""
        self.add_button.visible = True
        self.new_item_field.visible = False
        self.confirm_button.visible = False
        self.cancel_button.visible = False
        self.new_item_field.value = ""
        self.new_item_field.error_text = ""
        self.page.update()

    def get_values(self):
        """Returns the current list of items and the selected item."""
        self.selected_item = self.dropdown.value
        return self.items, self.selected_item