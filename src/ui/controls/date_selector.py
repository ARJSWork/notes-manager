###
# File:   date_selector.py
# Date:   2025-11-04
# Author: automated-agent
###

import flet as ft
from datetime import datetime
from db import registry


class DateSelector(ft.Row):
    """A composite control with a TextField for a date and a calendar button that opens a DatePicker.

    Usage:
        ds = DateSelector(page, initial_date="2025-10-30")
        # read selected value with ds.get_value() -> 'YYYY-MM-DD'
    """

    def __init__(self, page: ft.Page, initial_date: str | None = None):
        super().__init__()
        self.page = page
        # normalize initial date: use provided or today's date
        if initial_date:
            init = initial_date
        else:
            init = datetime.now().strftime("%Y-%m-%d")

        self.date_field = ft.TextField(value=init, width=120)
        # calendar button
        self.open_button = ft.IconButton(icon=ft.Icons.DATE_RANGE, tooltip="Pick date", on_click=self._open_datepicker)

        self.controls = [self.date_field, self.open_button]

    def _open_datepicker(self, e):
        """Open an AlertDialog containing a DatePicker prefilled with the current textfield value.

        The dialog has Cancel and OK buttons; only OK commits the chosen date to the textfield.
        """

        def _on_ok(ev):
            try:
                val = getattr(dialog, "value", None)
                if val is not None:
                    # val is likely a datetime.date
                    yyyy = getattr(val, "year", None)
                    mm = getattr(val, "month", None)
                    dd = getattr(val, "day", None)
                    if yyyy is not None and mm is not None and dd is not None:
                        self.date_field.value = f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}"
                        self.date_field.update()
                        #registry.changed = True

            except Exception:
                pass

        # parse current date value
        try:
            ts = (self.date_field.value or "").strip()
            yyyy, mm, dd = ts.split("-", 2)
            yyyy = int(yyyy)
            mm = int(mm)
            dd = int(dd)
            # create a full datetime using the parsed date 
            _date = datetime.now().replace(year=yyyy, month=mm, day=dd).date()
        except Exception:
            # fallback to today's date
            _date = datetime.now().date()

        dialog = ft.DatePicker(
            value=_date,
            confirm_text="Confirm",
            error_invalid_text="Date out of range",
            help_text="Pick your date",
            on_change=_on_ok
            )
        
        # show the dialog
        self.page.open(dialog)

    def get_value(self) -> str:
        """Return the current date text as string (YYYY-MM-DD)."""
        return (self.date_field.value or "").strip()
