# format_tool/formatters/py_formatter.py

try:
    import autopep8
    AUTOP_AVAILABLE = True
except ImportError:
    AUTOP_AVAILABLE = False

def format_python(file_path, spaces=4):
    """Formats a Python file using autopep8."""
    if not AUTOP_AVAILABLE:
        print("Warning: 'autopep8' is not installed. Skipping Python files. Run: pip install autopep8")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading Python file {file_path}: {e}")
        return None
    
    # --- KEY CHANGE: Increased aggressiveness to ensure formatting happens ---
    options = {
        'aggressive': 2,  # Level 2 is more aggressive and fixes spacing around operators
        'indent_size': spaces
    }
    
    try:
        formatted_content = autopep8.fix_code(content, options=options)
        return formatted_content
    except Exception as e:
        print(f"Error during autopep8 formatting of {file_path}: {e}")
        return None