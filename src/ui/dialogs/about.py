###
# File:   src\ui\dialogs\about.py
# Date:   2025-11-18
# Author: automated
###


# imports
from pathlib import Path
import re
from flet import Colors, Page, Text, ElevatedButton, AlertDialog, Column


# constants
DEFAULT_AUTHOR = "Alex Schiessl"
DEFAULT_DATE = "09/01/2024"


def _find_pyproject(start_path: Path = None) -> Path | None:
    """Search upward from start_path for pyproject.toml and return its Path."""
    if start_path is None:
        start_path = Path(__file__).resolve()

    for parent in [start_path] + list(start_path.parents):
        candidate = Path(parent) / "pyproject.toml"
        if candidate.exists():
            return candidate

    return None


def _read_version(pyproject_path: Path | None) -> str:
    """Return version string parsed from pyproject.toml or '0.0.0' fallback."""
    if not pyproject_path:
        return "0.0.0"

    try:
        content = pyproject_path.read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass

    return "0.0.0"


def show(page: Page) -> None:
    """Show a simple About dialog. Version is read from `pyproject.toml` if available."""

    pyproject = _find_pyproject()
    version = _read_version(pyproject)

    about_dialog = AlertDialog(
        title=Text("About", size=18),
        bgcolor=Colors.GREY_900,
        modal=True,
        content=Column([
            Text(f"Author: {DEFAULT_AUTHOR}"),
            Text(f"Date: {DEFAULT_DATE}"),
            Text(f"Version: {version}"),
        ], tight=True),
        actions=[
            ElevatedButton("Ok", on_click=lambda e: page.close(about_dialog)),
        ],
    )

    page.open(about_dialog)
