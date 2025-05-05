import json
import argparse
import sys
from typing import Dict, List, Any, Union
from db import registry
from db.messages import getError

# --- Error Classes ---
class RenderingError(Exception):
    """Base class for rendering errors."""
    pass

class ItemNotFoundError(RenderingError):
    """Raised when a referenced item (module, template, meeting) is not found."""
    def __init__(self, item_type: str, name: str, referenced_in: str = None):
        message = f"{item_type.capitalize()} '{name}' not found"
        if referenced_in:
            message += f" (referenced in {referenced_in})"
        super().__init__(message)
        self.item_type = item_type
        self.name = name
        self.referenced_in = referenced_in

class InvalidReferenceError(RenderingError):
    """Raised when a reference structure is invalid."""
    pass


# --- Data Loading and Lookup ---
def load_data(filepath: str) -> Dict[str, Any]:
    """Loads and validates the JSON data from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Basic validation
        if not all(key in data for key in ["meetings", "templates", "modules"]):
            raise RenderingError("JSON file must contain 'meetings', 'templates', and 'modules' top-level keys.")
        return data
    except FileNotFoundError:
        raise RenderingError(f"Error: JSON file not found at '{filepath}'")
    except json.JSONDecodeError as e:
        raise RenderingError(f"Error decoding JSON file '{filepath}': {e}")
    except Exception as e:
        raise RenderingError(f"An unexpected error occurred loading '{filepath}': {e}")


def find_item_by_name(item_list: List[Dict[str, Any]], name: str, item_type: str) -> Dict[str, Any]:
    """Finds an item (module, template, meeting) in a list by its 'name'."""
    for item in item_list:
        if item.get("name") == name:
            return item
    # If not found, raise specific error (will be caught later for context)
    raise ItemNotFoundError(item_type, name)


def find_index_by_id(list_of_dicts, _id):
    """
    Finds the index of a dictionary in a list of dictionaries where the "id" key matches a given value.

    Args:
        list_of_dicts: A list of dictionaries, where each dictionary has an "id" key.
        _moduleId: The value to search for in the "id" key.

    Returns:
        The index of the dictionary in the list where the "id" matches _moduleId, or -1 if no match is found.
    """
    for index, dictionary in enumerate(list_of_dicts):
        if "id" in dictionary and dictionary["id"] == str(_id):
            return dictionary

    return {}


# --- Rendering Functions ---
def render_module(module_data: Dict[str, Any]) -> str:
    """Renders a single module into Markdown."""
    headline = module_data.get('headline', 'Unnamed Module')
    content = module_data.get('content', '')
    # Use H2 for module headlines for structure
    return f"# {headline}\n\n{content}\n\n"


def render_template(
    template_data: Dict[str, Any],
    all_data: Dict[str, Any],
    context: str
) -> str:
    """Renders a template by rendering its constituent modules."""
    template_name = template_data.get("name", "Unnamed Template")
    rendered_parts = []
    module_references = template_data.get('modules', [])

    if not isinstance(module_references, list):
         raise InvalidReferenceError(f"Template '{template_name}' has invalid 'modules' structure (expected a list).")

    _projectData = registry.project.data
    assert _projectData, getError("A000")

    for ref in module_references:
        _module = [m for m in _projectData["modules"] if m["id"] == str(ref)]
        assert _module, getError("A000")
        _module = _module[0]
        assert _module, getError("A000")
        rendered_parts.append(render_module(_module))

    return "".join(rendered_parts) # Modules already end with \n\n

def render_meeting(
    meeting_id: int | str,
    project_data: Dict[str, Any]
) -> str:
    """Renders a complete meeting into Markdown."""
    meeting_data = [m for m in project_data["meetings"] if m["id"] == str(meeting_id)]
    assert meeting_data, getError("A000")
    meeting_data = meeting_data[0]
    assert meeting_data, getError("A000")

    title = meeting_data.get('name', "Unnamed") # Fallback title to name
    type = meeting_data.get('kind', "Meeting") # Fallback title to name
    info = meeting_data.get('description', "A unnamed Meeting") # Fallback title to name
    top_items = meeting_data.get('tops', [])
    rendered_output = []

    # Add the meeting title as H1
    rendered_output.append(f"# {type} - {title}\n\n")

    if not isinstance(top_items, list):
         raise InvalidReferenceError(f"Meeting '{title}' has invalid 'tops' structure (expected a list).")

    context = f"meeting '{title}'" # For error reporting

    for item in top_items:
        try:
            _type = item["type"]
            assert _type, getError("A000")
            _id = item["id"]
            assert _id, getError("A000")
            match _type:
                case "text":
                    rendered_output.append(f"# {item['value']}\n\n")

                case "templates":
                    template_to_render = find_index_by_id(
                        project_data.get('templates', []),
                        _id
                    )
                    rendered_output.append(render_template(template_to_render, project_data, context))

                case "modules":
                    module_to_render = find_index_by_id(
                        project_data.get('modules', []),
                        _id
                        )
                    rendered_output.append(render_module(module_to_render))
                    
                case _:
                    print("Unknown top type")
                    continue
    
        except ItemNotFoundError as e:
             # Add meeting context if not already present
            if not e.referenced_in:
                 e.referenced_in = context
            raise e # Re-raise to be caught by the main handler
        
        except InvalidReferenceError as e:
            raise InvalidReferenceError(f"{e} (within {context})") from e

    return "".join(rendered_output).strip() # Remove trailing whitespace

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description="Render a meeting defined in a JSON file to Markdown."
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON data file."
    )
    parser.add_argument(
        "meeting_name",
        help="The 'name' of the meeting to render from the JSON file."
    )
    args = parser.parse_args()

    try:
        all_data = load_data(args.json_file)

        # Find the specific meeting to render
        target_meeting_data = find_item_by_name(
            all_data.get('meetings', []),
            args.meeting_name,
            "meeting"
        )

        # Render the meeting
        markdown_output = render_meeting(target_meeting_data, all_data)

        # Print the final Markdown to standard output
        print(markdown_output)

    except (RenderingError, ItemNotFoundError, InvalidReferenceError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()