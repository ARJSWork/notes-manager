###
# File:   time_selector.py
# Date:   2025-10-30
# Author: automated-agent
###

import flet as ft
from datetime import datetime, time as dt_time
from db import registry


class TimeSelector(ft.Row):
    """A composite control with a TextField for time and a '+' button that opens a TimePicker.

    Usage:
        ts = TimeSelector(page, initial_time="09:30")
        # read selected value with ts.get_value()
    """

    def __init__(self, page: ft.Page, initial_time: str | None = None):
        super().__init__()
        self.page = page
        # normalize initial time: use provided or current time
        if initial_time:
            init = initial_time
        else:
            init = datetime.now().strftime("%H:%M")

        self.time_field = ft.TextField(value=init, width=70)
        # plus button
        self.open_button = ft.IconButton(icon=ft.Icons.ACCESS_TIME_FILLED, tooltip="Pick time", on_click=self._open_timepicker)

        self.controls = [self.time_field, self.open_button]

    def _open_timepicker(self, e):
        """Open an AlertDialog containing a TimePicker prefilled with the current textfield value.

        The dialog has Cancel and OK buttons; only OK commits the chosen time to the textfield.
        """
        
        def _on_ok(ev):
            try:
                val = getattr(ev, "data", None)
                if val is not None:
                    h, m = val.split(":")
                    h = int(h) % 24
                    m = int(m) % 60
                    if h is not None and m is not None:
                        self.time_field.value = f"{int(h):02d}:{int(m):02d}"
                        self.time_field.update()
                        registry.changed = True
            except Exception:
                pass

        # parse current time value
        try:
            ts = (self.time_field.value or "").strip()
            h_str, m_str = ts.split(":", 1)
            h = int(h_str) % 24
            m = int(m_str) % 60
            # create a full datetime using today's date and the parsed time
            _time = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        except Exception:
            # fallback to current time (rounded to second)
            _time = datetime.now().replace(second=0, microsecond=0)

        dialog = ft.TimePicker(
            value=_time,
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text="Pick your time slot",
            on_change=_on_ok
        )

        # show the dialog
        self.page.open(dialog)

    def get_value(self) -> str:
        """Return the current time text as string (HH:MM)."""
        return (self.time_field.value or "").strip()
