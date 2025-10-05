import json

def format_json(file_path, spaces=4):
    """Formats a JSON file and returns the formatted content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=spaces) + '\n'
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return None
        