#!/usr/bin/env python3
# ui/reporter.py
# Full, self-contained reporter for Secret Hound output (JSON).
# - Reads JSON list from stdin or from --input <path>
# - Groups matches by file and prints a rich Table inside Panels per file
# - Handles large matches safely, no unsupported args used
# - Optional: --html <path> to save an HTML copy (requires 'rich[html]' to be installed)

from __future__ import annotations
import sys
import json
import argparse
import os
from typing import List, Dict, Any, Optional

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown

APP_TITLE = "🔍 Secret Hound Report"


def load_json_from_stdin() -> Optional[Any]:
    try:
        # Only attempt to read from stdin if there's data piped in
        if not sys.stdin.isatty():
            return json.load(sys.stdin)
    except Exception:
        # ignore parse errors here; caller will handle None
        return None
    return None


def load_json_from_file(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def normalize_data(raw: Any) -> List[Dict[str, Any]]:
    """
    Normalize incoming JSON to a list of entries.
    Expected entry keys: file, line, rule_id, description, match
    Accepts:
    - list of dicts
    - dict containing {"matches": [...]} or {"results": [...]} or {"data": [...]}
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for candidate in ("matches", "results", "data", "entries"):
            if candidate in raw and isinstance(raw[candidate], list):
                return raw[candidate]
        # If dict looks like a single entry, wrap it
        # Heuristic: has 'file' and 'match' keys
        if "file" in raw and "match" in raw:
            return [raw]
    return []


def group_by_file(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        file_name = e.get("file") or "Unknown file"
        grouped.setdefault(file_name, []).append(e)
    return grouped


def build_table_for_entries(entries: List[Dict[str, Any]]) -> Table:
    table = Table(show_header=True, header_style="bold blue", show_lines=True, expand=True)
    table.add_column("Line", style="cyan", width=8, justify="center")
    table.add_column("Rule ID", style="yellow", width=18, overflow="ellipsis")
    table.add_column("Description", style="green", overflow="fold")
    table.add_column("Match (preview)", style="magenta", overflow="fold")

    for entry in entries:
        line = str(entry.get("line", "-"))
        rule_id = str(entry.get("rule_id", "N/A"))
        description = str(entry.get("description", "")) or "N/A"
        match_str = str(entry.get("match", ""))

        # Use Syntax for a preview; it's safe to place Syntax into a Table cell
        # Do not use unsupported args like `inline`
        # If the match is very long, we shorten the preview for the table cell,
        # and attach a full Syntax renderable below in a collapsible-like separate panel.
        preview = match_str
        max_preview_len = 240
        if len(preview) > max_preview_len:
            short = preview[: max_preview_len - 3] + "..."
            syntax_block = Syntax(f'"{short}"', "python", theme="monokai", word_wrap=True)
        else:
            syntax_block = Syntax(f'"{preview}"', "python", theme="monokai", word_wrap=True)

        table.add_row(line, rule_id, description, syntax_block)

    return table


def print_report(console: Console, grouped: Dict[str, List[Dict[str, Any]]], total: int) -> None:
    console.rule(APP_TITLE)
    panels: List[Panel] = []

    # Sort files for deterministic output
    for file_name in sorted(grouped.keys()):
        entries = grouped[file_name]
        tbl = build_table_for_entries(entries)
        panels.append(
            Panel(
                tbl,
                title=f"[bold cyan]{os.path.basename(file_name)}[/bold cyan]",
                subtitle=f"{len(entries)} potential secret(s)",
                border_style="bright_black",
                padding=(1, 2),
            )
        )

    if not panels:
        console.print("[yellow]No secrets or no input data found.[/yellow]")
        return

    # Print grouped panels
    console.print(Group(*panels))
    console.rule()
    console.print(f"[bold magenta]Total secrets found:[/bold magenta] {total}")


def save_html(console: Console, grouped: Dict[str, List[Dict[str, Any]]], total: int, path: str) -> bool:
    """
    Optionally save a simple HTML version using rich's export_html if available.
    This function will attempt to create a combined markdown/html render.
    """
    try:
        # Build a simple markdown summary and tables as text
        md_lines = [f"# {APP_TITLE}\n", f"**Total secrets found**: {total}\n\n"]
        for file_name in sorted(grouped.keys()):
            md_lines.append(f"## {os.path.basename(file_name)} ({len(grouped[file_name])})\n")
            for entry in grouped[file_name]:
                line = entry.get("line", "-")
                rid = entry.get("rule_id", "N/A")
                desc = entry.get("description", "")
                match_str = entry.get("match", "")
                md_lines.append(f"- **Line {line}** — `{rid}` — {desc}\n\n")
                # include the match as a code block
                md_lines.append(f"```\n{match_str}\n```\n\n")
        md_text = "".join(md_lines)
        # Convert Markdown to HTML using rich Markdown -> Console.export_html
        from rich.markup import escape
        from rich.panel import Panel as _Panel

        # Render to a temporary console and capture HTML
        # Note: Console().export_html exists in rich; use Console().capture + export_html is not direct.
        # We'll use console.print and Console().export_html if present.
        export_console = Console(record=True)
        export_console.print(Markdown(md_text))
        html = export_console.export_html(title=APP_TITLE)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    except Exception:
        return False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Secret Hound reporter (renders JSON to terminal using rich).")
    p.add_argument("--input", "-i", help="Path to report.json (if not provided, read from stdin)")
    p.add_argument("--html", help="Optional: save an HTML copy to this path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()

    raw = None
    # Priority: stdin (if piped) -> --input path -> interactive prompt
    raw = load_json_from_stdin()
    if raw is None and args.input:
        raw = load_json_from_file(args.input)
    if raw is None and args.input is None:
        # if nothing provided, ask user for path (safe for interactive usage)
        try:
            if sys.stdin.isatty():
                path = input("Enter path to report.json (or leave empty to exit): ").strip()
                if path:
                    raw = load_json_from_file(path)
        except Exception:
            raw = None

    entries = normalize_data(raw)
    grouped = group_by_file(entries)
    total = len(entries)

    print_report(console, grouped, total)

    if args.html:
        ok = save_html(console, grouped, total, args.html)
        if ok:
            console.print(f"[green]Saved HTML report to:[/green] {args.html}")
        else:
            console.print(f"[red]Failed to save HTML report to:[/red] {args.html}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    