###
# File:   src\config\config.py
# Date:   2025-10-08
# Author: Gemini
###

# The root directory for storing collections. Use the top-level "notes" folder
# which lives next to the "src" folder in the repository layout.
import os
from os import getcwd

DATA_ROOT = os.path.join(getcwd(), "notes")
