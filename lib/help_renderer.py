# File: lib/help_renderer.py
# Description: The centralized, JSON-driven, dynamic help rendering engine for the SNIPER toolkit.
# This script parses a UI description from a JSON file and builds a complex Rich interface.

import json
import sys
import logging
from pathlib import Path
import argparse

# --- START: Core SNIPER Environment Integration ---
try:
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(_PROJECT_ROOT))
    from lib.sniper_env import env
    env.log.name = "help-renderer"
except (ImportError, IndexError):
    print("\033[91m[CRITICAL ERROR]\033[0m Could not initialize SNIPER environment.", file=sys.stderr)
    sys.exit(1)
# --- END: Core SNIPER Environment Integration ---

# --- START: Rich Library Integration ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.markdown import Markdown
    from rich.console import Group
except ImportError:
    env.log.critical("The 'rich' library is required to render help screens. Please run: pip install rich")
    sys.exit(1)
# --- END: Rich Library Integration ---

class HelpRenderer:
    """
    Parses a structured dictionary (from JSON) and builds a Rich UI.
    """
    def __init__(self):
        self.console = Console()
        # A map of component names in JSON to the methods that build them.
        self.component_builders = {
            "Panel": self._build_panel,
            "Text": self._build_text,
            "Columns": self._build_columns,
            "Rule": self._build_rule,
            "Markdown": self._build_markdown,
            "Markup": self._build_markup, # Simplified version of Text
        }

    def _build_component(self, data: dict):
        """
        Generic component builder that dispatches to the correct specific builder.
        """
        comp_type = data.get("component")
        builder = self.component_builders.get(comp_type)
        if builder:
            return builder(data)
        else:
            env.log.warning(f"Unknown component type '{comp_type}' in help JSON. Skipping.")
            return None

    def _build_panel(self, data: dict):
        """Builds a rich.panel.Panel object from dictionary data."""
        title = data.get("title", "")
        style = data.get("style", "white")
        subtitle = data.get("subtitle", "")
        
        # The content of a panel can be a list of other components.
        # We build them recursively.
        inner_content = []
        for item_data in data.get("content", []):
            component = self._build_component(item_data)
            if component:
                inner_content.append(component)

        # Use rich.console.Group to group multiple renderables inside the panel.
        return Panel(
            Group(*inner_content),
            title=Text.from_markup(title),
            border_style=style,
            subtitle=Text.from_markup(subtitle)
        )

    def _build_text(self, data: dict):
        """Builds a rich.text.Text object."""
        text = data.get("text", "")
        # Text content can be a list of lines, so we join them.
        if isinstance(text, list):
            text = "\n".join(text)
        
        return Text.from_markup(
            text,
            style=data.get("style", "default"),
            justify=data.get("justify", "left")
        )

    def _build_markup(self, data: dict):
        """Builds a simple Text object from markup, useful for panel content."""
        text = data.get("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        return Text.from_markup(text)

    def _build_columns(self, data: dict):
        """Builds a rich.columns.Columns object."""
        items = data.get("items", [])
        options = data.get("options", {})
        return Columns(items, **options)

    def _build_rule(self, data: dict):
        """Builds a rich.rule.Rule object."""
        return Rule(
            title=data.get("text", ""),
            style=data.get("style", "default")
        )

    def _build_markdown(self, data: dict):
        """Builds a rich.markdown.Markdown object."""
        text = data.get("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        return Markdown(text)

    def render_layout(self, layout_data: list):
        """
        Iterates through the top-level layout list and prints each component.
        
        Args:
            layout_data (list): The list of component dictionaries from the JSON file.
        """
        for component_data in layout_data:
            rich_object = self._build_component(component_data)
            if rich_object:
                # Some components might need specific alignment.
                justify = component_data.get("justify", "left")
                if justify == "center":
                    self.console.print(Align.center(rich_object))
                elif justify == "right":
                    self.console.print(Align.right(rich_object))
                else:
                    self.console.print(rich_object)
def render_help(help_data: dict):
    """
    (Public Function) The main entry point for the help renderer.
    This function acts as a simple facade, hiding the complexity of the internal class.
    
    Args:
        help_data (dict): A dictionary describing the UI, loaded from a JSON file.
    """
    tool_name = help_data.get("tool_name", "help_renderer")
    logger = logging.getLogger(f"SNIPER.{tool_name}")

    layout_data = help_data.get("layout")
    if not layout_data:
        logger.error("Help data is missing the required 'layout' key.")
        return

    try:
        renderer = HelpRenderer()
        renderer.render_layout(layout_data)
    except Exception as e:
        logger.error(f"An unexpected error occurred during help rendering: {e}", exc_info=True)
def load_and_render(tool_name: str):
    """
    Finds the help JSON file for a given tool, loads it, and triggers the rendering process.
    
    Args:
        tool_name (str): The name of the tool, which corresponds to the JSON filename.
    """
    # The new centralized path for all help files.
    help_file_path = env.ROOT_DIR / "share" / "readme" / f"{tool_name}.json"

    if not help_file_path.is_file():
        env.log.error(f"Help file not found for tool '{tool_name}' at: {help_file_path}")
        sys.exit(1)

    try:
        with open(help_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        env.log.error(f"Invalid JSON in help file '{help_file_path}': {e}")
        sys.exit(1)
    
    # Check if the JSON has the required top-level 'layout' key.
    layout_data = data.get("layout")
    if layout_data is None:
        env.log.error(f"Help file for '{tool_name}' is missing the required 'layout' key.")
        sys.exit(1)
        
    # Create a renderer instance and start the rendering process.
    renderer = HelpRenderer()
    renderer.render_layout(layout_data)

if __name__ == "__main__":
    # This block allows the script to be called from the command line (e.g., from C++ tools).
    parser = argparse.ArgumentParser(description="SNIPER Centralized Help Renderer")
    parser.add_argument(
        "--tool",
        required=True,
        help="The name of the tool to load help content for (e.g., 'fastfind')."
    )
    args = parser.parse_args()
    
    load_and_render(args.tool)
