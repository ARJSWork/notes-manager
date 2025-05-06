###
# File:   src\logic\ui\project\utils.py
# Date:   2025-02-18 / 12:20 (Refactored)
# Author: alexrjs
###


# imports
from db import registry
from db.messages import getError


# constants


# variables


# functions/classes
def validate_values(values_, validations) -> bool:
    """Validates a dictionary against a set of expressions.

    Args:
        values_: The dictionary to validate.
        *validations: A variable number of tuples, where each tuple contains:
            - A validation expression (string).  This will be evaluated.
            - The error code to use if the validation fails.

    Returns:
        None if all validations pass.  Raises a ValueError with the error message
        if any validation fails.  This allows the calling function to handle
        the error as appropriate.

    Raises:
        ValueError: If any validation fails.
    """

    try:
        for expression, error_code in validations:
            try:
                # Use eval() with caution!  See security considerations below.
                if not eval(expression, {}, {"values_": values_}):  # Pass values_ to eval
                    raise ValueError(getError(error_code)) # Raise exception if eval is false

            except (NameError, SyntaxError, TypeError) as e:  # Catch potential eval errors
                raise ValueError(f"Invalid validation expression: {expression}. {e}") from e

            except ValueError as e: # Reraise the ValueError with the error message
                raise # Re-raise the ValueError, so the calling function can handle it.

        return True

    except Exception as _e:
        print(_e)
        return False


def filter_ids_by_type(tops: list, target_type: str) -> list:
    """
    Filters a list of "top" dictionaries and returns a list of IDs for a specific type.

    Args:
        tops: A list of dictionaries, where each dictionary represents a "top" and has "type" and "id" keys.
        target_type: The type to filter by (e.g., "templates", "modules", "text").

    Returns:
        A list of IDs (strings) that match the target type.
    """

    filtered_ids = [
        top["id"] for top in tops if top["type"] == target_type
    ]
    return filtered_ids


def get_available_entries_not_in_tops(tops: list, entries: str) -> list:
    """
    Identifies and returns a list of entries (e.g., templates, modules) that are not present in the 'tops' list.

    Args:
        tops: A list of dictionaries, where each dictionary represents a "top" and has "type" and "id" keys.
        entries: The key for the list of entries in registry.project.data (e.g., "templates", "modules").

    Returns:
        A list of entry dictionaries that are not found in the 'tops' list for the specified type.
    """
    _projectData = registry.project.data
    assert _projectData, getError("A000")

    # Extract IDs from the 'tops' list for the specific entry type.
    _ids_in_tops = {top["id"] for top in tops if top["type"] == entries}

    # Filter the entry list to include only those not present in '_ids_in_tops'.
    available_entries = [
        entry for entry in _projectData.get(entries, []) if entry.get("id") not in _ids_in_tops
    ]

    return available_entries


def find_index_by_id(list_of_dicts, _type, _id):
    """
    Finds the index of a dictionary in a list where 'type' and 'id' match.
    Returns -1 if not found.
    """
    for index, dictionary in enumerate(list_of_dicts):
        if dictionary.get("type") == _type and dictionary.get("id") == str(_id):
            return index
    return -1