###
# File:   src\db\__init__.py
# Date:   2025-07-10
# Author: Gemini
###

# imports


# constants
DEFAULT_NOTES_PATH = "notes" # Default path for notes


# variables


# functions/classes
# Central registry for application state
class Registry:
    def __init__(self):
        self._data = {}

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value

registry = Registry()

def register(key, value):
    #registry._data[key] = value
    _parts = key.split('.')
    _current_namespace = registry._data
    for _i, _part in enumerate(_parts):
        if _i == len(_parts) - 1:
            _current_namespace[_part] = value
        else:
            if _part not in _current_namespace or not isinstance(_current_namespace[_part], Registry):
                _current_namespace[_part] = Registry()

            _current_namespace = _current_namespace[_part]._data

