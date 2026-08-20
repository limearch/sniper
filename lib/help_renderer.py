#!/usr/bin/env python3
# File: lib/help_renderer.py
# Description: The centralized, JSON-driven, dynamic help rendering engine for the SNIPER toolkit.
# This script parses a UI description from a JSON file and builds a complex Rich interface.
# This version includes a robust, multi-theme rendering system.

import json
import sys
import logging
from pathlib import Path
import argparse
from typing import Optional, Dict, Any

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
    import rich.box
except ImportError:
    env.log.critical("The 'rich' library is required to render help screens. Please run: pip install rich")
    sys.exit(1)
# --- END: Rich Library Integration ---

# --- START: Global Config Reader ---

def _load_global_theme_config() -> Optional[str]:
    """
    Reads the global sniper-config.json to find the default help theme.
    
    Returns:
        Optional[str]: The theme name if found, else None.
    """
    config_path = env.ROOT_DIR / "config" / "sniper-config.json"
    if not config_path.is_file():
        env.log.debug("Global sniper-config.json not found. Skipping.")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Nested get to safely access appearance.help_theme
        theme = data.get("appearance", {}).get("help_theme")
        if theme:
            env.log.debug(f"Found global theme in config: '{theme}'")
            return theme
        return None
    except (json.JSONDecodeError, IOError, KeyError) as e:
        env.log.warning(f"Failed to read or parse global config '{config_path}': {e}")
        return None

# --- END: Global Config Reader ---

# --- START: Theme Definitions ---

# This is the central repository for all built-in themes.
# Themes can define:
# - Visuals: Colors, box styles.
# - Structure: Layout, padding, dividers, text processing.
_BUILTIN_THEMES: Dict[str, Dict[str, Any]] = {
    "default": {
        "description": "The standard SNIPER theme. (Rounded boxes, white borders)",
        "panel_border_style": "white",
        "panel_box": rich.box.ROUNDED,
        "panel_padding": (1, 2),
        "panel_layout": "stack", # 'stack' (default), 'card' (centered), 'wide' (columns)
        "rule_style": "dim",
        "rule_text_style": "default",
        "text_style": "default",
        "markup_style": "default",
        "title_style": "bold",
        "subtitle_style": "dim",
        "title_case": None, # 'upper', 'lower', 'title'
        "show_dividers": True,
        "use_markdown_for_text": False,
        "columns_respond": True, # If False, forces 'expand=True'
        "column_padding": (0, 1),
        "column_expand": False,
    },
    "minimal": {
        "description": "A clean, minimal theme with no dividers or padding.",
        "panel_border_style": "dim",
        "panel_box": rich.box.MINIMAL,
        "panel_padding": (0, 1),
        "panel_layout": "stack",
        "rule_style": "dim",
        "title_style": "bold",
        "subtitle_style": "dim",
        "show_dividers": False,
        "use_markdown_for_text": False,
    },
    "cyberpunk": {
        "description": "A high-contrast theme with heavy boxes and magenta highlights.",
        "panel_border_style": "bold magenta",
        "panel_box": rich.box.HEAVY,
        "panel_padding": (1, 2),
        "panel_layout": "stack",
        "rule_style": "magenta",
        "rule_text_style": "bold white",
        "text_style": "bright_white",
        "markup_style": "white",
        "title_style": "bold bright_magenta",
        "subtitle_style": "cyan",
        "title_case": "upper",
        "show_dividers": True,
    },
    "card": {
        "description": "Centers each panel as a distinct 'card' on the screen.",
        "panel_border_style": "bold cyan",
        "panel_box": rich.box.DOUBLE,
        "panel_padding": (1, 2),
        # "panel_layout": "card", # This will be interpreted as 'center' alignment
        "rule_style": "cyan",
        "title_style": "bold bright_cyan",
        "show_dividers": True,
    },
    "wide": {
        "description": "Attempts to arrange top-level panels side-by-side in columns.",
        "panel_border_style": "bold green",
        "panel_box": rich.box.ROUNDED,
        "panel_padding": (1, 2),
        "panel_layout": "wide", # This will be interpreted by render_layout
        "rule_style": "green",
        "title_style": "bold bright_green",
        "column_expand": True,
    },
    "markdown": {
        "description": "Forces all 'Text' components to be rendered as Markdown.",
        "panel_border_style": "bold yellow",
        "panel_box": rich.box.ROUNDED,
        "panel_layout": "stack",
        "rule_style": "yellow",
        "title_style": "bold bright_yellow",
        "use_markdown_for_text": True,
    },
    "no-response": {
        "description": "A theme that disables responsive column behavior, forcing expansion.",
        "panel_border_style": "bold red",
        "panel_box": rich.box.ROUNDED,
        "panel_layout": "stack",
        "rule_style": "red",
        "title_style": "bold bright_red",
        "columns_respond": False, # This will force expand=True in _build_columns
    },
    "classic": {
        "description": "Uses classic ASCII-style boxes for a retro feel.",
        "panel_border_style": "dim",
        "panel_box": rich.box.ASCII,
        "panel_padding": (0, 1),
        "panel_layout": "stack",
        "rule_style": "dim",
        "title_style": "bold",
        "show_dividers": True,
    },
    "ocean": {
        "description": "A calm theme with blue tones.",
        "panel_border_style": "bold blue",
        "panel_box": rich.box.ROUNDED,
        "panel_padding": (1, 2),
        "panel_layout": "stack",
        "rule_style": "blue",
        "text_style": "default",
        "title_style": "bold bright_blue",
        "subtitle_style": "dim blue",
    },
    "matrix": {
        "description": "A hacker-style theme with green-on-black text.",
        "panel_border_style": "bold green",
        "panel_box": rich.box.HEAVY,
        "panel_padding": (1, 2),
        "panel_layout": "stack",
        "rule_style": "green",
        "rule_text_style": "bold bright_green",
        "text_style": "green",
        "markup_style": "green",
        "title_style": "bold bright_green",
        "subtitle_style": "dim green",
        "title_case": "upper",
    }
}

# --- END: Theme Definitions ---

# --- START: Theme Resolution ---

def _resolve_theme_priority(cli_theme: Optional[str], 
                            global_cfg_theme: Optional[str], 
                            help_json_theme: Optional[str]) -> str:
    """
    Determines the final theme name based on the priority order.
    Priority: CLI > Global Config > Help JSON > "default"
    """
    if cli_theme:
        return cli_theme
    if global_cfg_theme:
        return global_cfg_theme
    if help_json_theme:
        return help_json_theme
    return "default"

# --- END: Theme Resolution ---

class HelpRenderer:
    """
    Parses a structured dictionary (from JSON) and builds a Rich UI
    based on a selected theme.
    """
    def __init__(self, theme_name: str = "default"):
        self.console = Console()
        self.theme = self._load_theme(theme_name)
        
        # A map of component names in JSON to the methods that build them.
        self.component_builders = {
            "Panel": self._build_panel,
            "Text": self._build_text,
            "Columns": self._build_columns,
            "Rule": self._build_rule,
            "Markdown": self._build_markdown,
            "Markup": self._build_markup, # Simplified version of Text
        }

    def _load_theme(self, theme_name: str) -> dict:
        """
        Loads the specified theme, merging it with the default theme
        to ensure all keys are present.
        """
        default_theme = _BUILTIN_THEMES["default"].copy()
        selected_theme = _BUILTIN_THEMES.get(theme_name)
        
        if not selected_theme:
            if theme_name != "default":
                env.log.warning(f"Theme '{theme_name}' not found. Falling back to 'default'.")
            selected_theme = default_theme
        
        # Merge default with selected theme (selected theme keys overwrite default)
        final_theme = default_theme
        final_theme.update(selected_theme)
        return final_theme

    def _get_theme_value(self, key: str) -> Any:
        """
        Safely gets a value from the loaded theme.
        This should always find a key due to the merge in _load_theme.
        """
        return self.theme.get(key)

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
        subtitle = data.get("subtitle", "")
        
        # Allow JSON to override theme border style
        style = data.get("style", self._get_theme_value("panel_border_style"))
        
        # --- FIX START ---
        # Create Text objects *before* applying case transform
        title_text = Text.from_markup(title, style=self._get_theme_value("title_style"))
        subtitle_text = Text.from_markup(subtitle, style=self._get_theme_value("subtitle_style"))

        # Apply theme case transform by recreating the Text object
        case_transform = self._get_theme_value("title_case")
        if case_transform == "upper":
            # Create a NEW Text object with the uppercased plain text and original style
            title_text = Text(title_text.plain.upper(), style=title_text.style)
            subtitle_text = Text(subtitle_text.plain.upper(), style=subtitle_text.style)
        elif case_transform == "lower":
            # Do the same for lower case
            title_text = Text(title_text.plain.lower(), style=title_text.style)
            subtitle_text = Text(subtitle_text.plain.lower(), style=subtitle_text.style)
        # --- FIX END ---

        # Build inner content recursively
        inner_content = []
        for item_data in data.get("content", []):
            component = self._build_component(item_data)
            if component:
                inner_content.append(component)

        return Panel(
            Group(*inner_content),
            title=title_text,
            border_style=style,
            subtitle=subtitle_text,
            box=self._get_theme_value("panel_box"),
            padding=self._get_theme_value("panel_padding")
        )

    def _build_text(self, data: dict):
        """Builds a rich.text.Text object."""
        
        # Check if theme forces markdown rendering
        if self._get_theme_value("use_markdown_for_text"):
            return self._build_markdown(data)
            
        text = data.get("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        
        return Text.from_markup(
            text,
            style=data.get("style", self._get_theme_value("text_style")),
            justify=data.get("justify", "left")
        )

    def _build_markup(self, data: dict):
        """Builds a simple Text object from markup, useful for panel content."""
        text = data.get("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        # Uses a specific 'markup_style' from theme for inner-panel text
        return Text.from_markup(text, style=self._get_theme_value("markup_style"))

    def _build_columns(self, data: dict):
        """Builds a rich.columns.Columns object."""
        items_data = data.get("items", [])
        
        # Build components for columns
        items = []
        for item in items_data:
            # If item is a string, wrap it in Markup using theme style
            if isinstance(item, str):
                items.append(Text.from_markup(item, style=self._get_theme_value("markup_style")))
            # If item is a component dict, build it
            elif isinstance(item, dict):
                component = self._build_component(item)
                if component:
                    items.append(component)
            
        json_options = data.get("options", {})
        
        # Start with theme defaults
        theme_options = {
            "padding": self._get_theme_value("column_padding"),
            "expand": self._get_theme_value("column_expand"),
        }
        
        # Apply responsiveness logic
        if not self._get_theme_value("columns_respond"):
            theme_options["expand"] = True # Force expansion
            
        # Let JSON options override theme defaults
        theme_options.update(json_options)
        
        return Columns(items, **theme_options)

    def _build_rule(self, data: dict):
        """Builds a rich.rule.Rule object."""
        
        # Check if theme disables dividers
        if not self._get_theme_value("show_dividers"):
            return None
            
        title_str = data.get("text", "")
        
        # --- FIX START ---
        # Parse markup *first*
        title_text = Text.from_markup(title_str, style=self._get_theme_value("rule_text_style"))

        # Apply theme case transform by recreating the Text object
        case_transform = self._get_theme_value("title_case")
        if case_transform == "upper":
            title_text = Text(title_text.plain.upper(), style=title_text.style)
        elif case_transform == "lower":
            title_text = Text(title_text.plain.lower(), style=title_text.style)
        # --- FIX END ---
        
        return Rule(
            title=title_text,
            style=data.get("style", self._get_theme_value("rule_style"))
        )

    def _build_markdown(self, data: dict):
        """Builds a rich.markdown.Markdown object."""
        text = data.get("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        return Markdown(text)

    def render_layout(self, layout_data: list):
        """
        Iterates through the top-level layout list and prints each component,
        applying structural theme logic (e.g., 'wide' or 'card' layouts).
        """
        layout_style = self._get_theme_value("panel_layout")
        
        if layout_style == "wide":
            # 'wide' layout: Tries to put all top-level panels into columns
            panels = []
            for component_data in layout_data:
                # Only try to columnize Panels. Print other things (like Rules) normally.
                if component_data.get("component") == "Panel":
                    rich_object = self._build_component(component_data)
                    if rich_object:
                        panels.append(rich_object)
                else:
                    rich_object = self._build_component(component_data)
                    if rich_object:
                        self.console.print(rich_object)
            if panels:
                self.console.print(Columns(
                    panels, 
                    expand=self._get_theme_value("column_expand"), 
                    padding=self._get_theme_value("column_padding")
                ))
        
        elif layout_style == "card":
            # 'card' layout: Centers each top-level component
            for component_data in layout_data:
                rich_object = self._build_component(component_data)
                if rich_object:
                    self.console.print(Align.center(rich_object))
        
        else:
            # 'stack' layout (default): Renders one after another, respecting JSON justify
            for component_data in layout_data:
                rich_object = self._build_component(component_data)
                if rich_object:
                    # Respect the original JSON-defined alignment
                    justify = component_data.get("justify", "left")
                    if justify == "center":
                        self.console.print(Align.center(rich_object))
                    elif justify == "right":
                        self.console.print(Align.right(rich_object))
                    else:
                        self.console.print(rich_object)

# --- START: Public API Functions ---

def render_help(help_data: dict, cli_theme_override: Optional[str] = None):
    """
    (Public Function) The main entry point for the help renderer.
    This function resolves the theme and renders the UI.
    
    Args:
        help_data (dict): A dictionary describing the UI, loaded from a JSON file.
        cli_theme_override (Optional[str]): Theme from CLI (highest priority).
    """
    tool_name = help_data.get("tool_name", "help_renderer")
    logger = logging.getLogger(f"SNIPER.{tool_name}")

    layout_data = help_data.get("layout")
    if not layout_data:
        logger.error("Help data is missing the required 'layout' key.")
        return

    # --- Theme Resolution ---
    global_theme = _load_global_theme_config()
    json_theme = help_data.get("appearance", {}).get("help_theme")
    
    final_theme_name = _resolve_theme_priority(
        cli_theme=cli_theme_override,
        global_cfg_theme=global_theme,
        help_json_theme=json_theme
    )
    
    env.log.debug(
        f"Resolved help theme: '{final_theme_name}' "
        f"(CLI: {cli_theme_override}, Config: {global_theme}, JSON: {json_theme})"
    )
    # --- End Theme Resolution ---

    try:
        # Pass the final theme name to the renderer
        renderer = HelpRenderer(theme_name=final_theme_name)
        renderer.render_layout(layout_data)
    except Exception as e:
        # Log the rich-specific error if possible
        if "rich.errors.MarkupError" in str(e):
            logger.error(f"A Rich markup error occurred during rendering. Check your JSON for invalid tags: {e}", exc_info=False)
        else:
            logger.error(f"An unexpected error occurred during help rendering: {e}", exc_info=True)

def load_and_render(tool_name: str, theme_arg: Optional[str] = None):
    """
    (Public Function) Finds the help JSON file for a given tool, loads it, 
    and triggers the rendering process.
    
    Args:
        tool_name (str): The name of the tool, which corresponds to the JSON filename.
        theme_arg (Optional[str]): A theme name passed from the CLI,
                                   which has the highest priority.
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
    # render_help will also check, but checking here provides a better error.
    if "layout" not in data:
        env.log.error(f"Help file for '{tool_name}' is missing the required 'layout' key.")
        sys.exit(1)
        
    # Inject tool_name into data for logger context, if not present
    if "tool_name" not in data:
        data["tool_name"] = tool_name
        
    # Call the centralized render_help function, passing the CLI theme override
    render_help(data, cli_theme_override=theme_arg)

# --- END: Public API Functions ---

if __name__ == "__main__":
    """
    This block allows the script to be called from the command line 
    (e.g., from C++ tools or for testing).
    """
    parser = argparse.ArgumentParser(description="SNIPER Centralized Help Renderer")
    parser.add_argument(
        "--tool",
        required=False, # Not required if --list-themes is used
        help="The name of the tool to load help content for (e.g., 'fastfind')."
    )
    parser.add_argument(
        "--theme",
        required=False,
        help="Override the default or configured help theme."
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List all available built-in themes and exit."
    )
    args = parser.parse_args()
    
    # --- Handle --list-themes ---
    # FIX: Changed 'args.list-themes' to 'args.list_themes'
    if args.list_themes:
        console = Console()
        console.print(Panel(
            Text("SNIPER Help Renderer Themes", style="bold white"), 
            border_style="bold cyan", 
            padding=(1,2)
        ))
        
        theme_items = []
        for name, config in _BUILTIN_THEMES.items():
            theme_items.append(
                f"[bold bright_cyan]{name}[/]: [dim]{config.get('description', 'No description.')}[/]"
            )
        console.print(Columns(theme_items, padding=(0, 2)))
        sys.exit(0)

    # --- Handle Normal Run ---
    if not args.tool:
        parser.error("The --tool argument is required unless --list-themes is specified.")
        sys.exit(1)
        
    # Pass the tool name and theme (if any) to the main loader function
    load_and_render(args.tool, theme_arg=args.theme)
