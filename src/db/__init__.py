###
# File:   src\db\__init__.py
# Date:   2025-01-21 / 08:38
# Author: alexrjs
###


# imports
from re import match
from models import ExtendedNamespace


# constants
DEFAULT_PROJECT_PATH = "projects"


# variables
registry = ExtendedNamespace()


# functions/classes
def register(name_:str=None, value_:object=None) -> object:
    """ Register a new key value pair in the registry """

    if name_ is None:
        print("Problem: No name given!")
        return None

    _name = name_.replace(" ", "_")
    if "." in _name:
        # Split the path into its components
        _keys = _name.split('.')
        
        # Traverse the namespace to find the target
        _current = registry
        for _key in _keys[:-1]:  # Go up to the second last key
            if not match(r'^[\w]+$', _key):
                raise ValueError("Attribute name contains unallowed special characters.")

            if hasattr(_current, _key):
                _current = getattr(_current, _key)

            else:
                raise AttributeError(f"'{_key}' not found in the namespace.")
        
        # Set the value to the last key
        _last_key = _keys[-1]
        setattr(_current, _last_key, value_)
        return getattr(_current, _last_key)

    else:    
        if not match(r'^[\w]+$', _name):
            raise ValueError("Attribute name contains unallowed special characters.")

        setattr(registry, name_, value_)
        return getattr(registry, name_)


def toExtendedNamespace(dict_: dict[str, object]) -> ExtendedNamespace:
    """
    Converts a dictionary to a ExtendedNamespace.

    Parameters:
    dict_ (Dict[str, object]): The dictionary to convert.

    Returns:
    ExtendedNamespace: A ExtendedNamespace object representing the dictionary.
    """
    for key_, value_ in dict_.items():
        if isinstance(value_, dict):
            dict_[key_] = toExtendedNamespace(value_)  # Recursively convert nested dicts

    return ExtendedNamespace(**dict_)


def toDict(ns_: ExtendedNamespace) -> dict[str, object]:
    """
    Converts a ExtendedNamespace to a dictionary.

    Parameters:
    ns_ (ExtendedNamespace): The ExtendedNamespace to convert.

    Returns:
    Dict[str, Any]: A dictionary representing the ExtendedNamespace.
    """
    return ns_.__dict__