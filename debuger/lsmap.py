#!/usr/bin/python3

import os
import pathlib
import sys
import json
from rich import print
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from datetime import datetime

def parse_args():
    parser = ArgumentParser(description="Directory walker with additional features.", add_help=True)
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")

    # Adding the short versions for all options
    parser.add_argument("-f", "--files-only", action="store_true", help="Display files only")
    parser.add_argument("-d", "--dirs-only", action="store_true", help="Display directories only")
    parser.add_argument("-s", "--show-hidden", action="store_true", help="Show hidden files and directories")
    parser.add_argument("-m", "--min-size", type=str, help="Minimum file size to display (e.g., 10k, 1M)")
    parser.add_argument("-D", "--depth", type=int, default=None, help="Max depth to scan")
    parser.add_argument("-t", "--top-size", type=int, default=None, help="Display top N largest files")
    parser.add_argument("-r", "--recent-files", action="store_true", help="Display most recently modified files")
    parser.add_argument("-e", "--export", choices=["json"], help="Export result in JSON format")
    parser.add_argument("-u", "--disk-usage", action="store_true", help="Display disk usage for directories")
    
    return parser.parse_args()

def convert_size(size_str):
    """Convert size string (e.g., 1M, 10k) to bytes."""
    size_str = size_str.lower()
    size_map = {'k': 1024, 'm': 1024**2, 'g': 1024**3}
    if size_str[-1] in size_map:
        return int(size_str[:-1]) * size_map[size_str[-1]]
    return int(size_str)

def walk_directory(directory: pathlib.Path, tree: Tree, args, current_depth=0, max_depth=None):
    """Recursively build a Tree with directory contents and count folders and files."""
    num_folders = 0
    num_files = 0
    all_files = []

    try:
        for path in directory.iterdir():
            # Handle depth limit
            if max_depth is not None and current_depth >= max_depth:
                continue

            # Handle hidden files
            if not args.show_hidden and (path.name.startswith(".") or path.parts[-1].startswith(".")):
                continue

            if path.is_dir():
                if not args.files_only:
                    num_folders += 1
                    style = "dim" if path.name.startswith("__") else ""
                    branch = tree.add(
                        f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                        style=style,
                        guide_style=style,
                    )
                    sub_folders, sub_files, sub_all_files = walk_directory(path, branch, args, current_depth + 1, max_depth)
                    num_folders += sub_folders
                    num_files += sub_files
                    all_files.extend(sub_all_files)
            else:
                # Handle minimum size
                file_size = path.stat().st_size
                if args.min_size and file_size < convert_size(args.min_size):
                    continue

                num_files += 1
                all_files.append((path, file_size, path.stat().st_mtime))

                if not args.dirs_only:
                    text_filename = Text(path.name, "green")
                    text_filename.highlight_regex(r"\..*$", "bold red")
                    text_filename.stylize(f"link file://{path}")
                    text_filename.append(f" ({decimal(file_size)})", "blue")
                    icon = " " if path.suffix == ".py" else " "
                    tree.add(Text(icon) + text_filename)
    except PermissionError:
        pass  # Skip directories without permission

    return num_folders, num_files, all_files

def disk_usage(directory):
    """Calculate disk usage for a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def main():
    args = parse_args()

    directory = pathlib.Path(args.directory).resolve()
    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="bold bright_blue",
    )

    # Walk the directory
    num_folders, num_files, all_files = walk_directory(directory, tree, args, max_depth=args.depth)
    
    # Sort by size for top-size feature
    if args.top_size:
        all_files.sort(key=lambda x: x[1], reverse=True)
        all_files = all_files[:args.top_size]
        print("\n[bold]Top Largest Files:[/bold]")
        for file_path, size, _ in all_files:
            print(f"{file_path} ({decimal(size)})")

    # Sort by modification time for recent-files feature
    if args.recent_files:
        all_files.sort(key=lambda x: x[2], reverse=True)
        print("\n[bold]Recently Modified Files:[/bold]")
        for file_path, _, mtime in all_files[:10]:  # Display top 10
            print(f"{file_path} (Modified: {datetime.fromtimestamp(mtime)})")

    # Disk usage feature
    if args.disk_usage:
        total_size = disk_usage(directory)
        print(f"\n[bold]Disk Usage for {directory}:[/bold] {decimal(total_size)}")

    # Export to JSON
    if args.export == "json":
        json_output = [{"path": str(p), "size": s, "mtime": m} for p, s, m in all_files]
        with open(f"{directory.name}_directory_structure.json", "w") as f:
            json.dump(json_output, f, indent=4)
        print(f"\n[bold]Exported JSON to {directory.name}_directory_structure.json[/bold]")

    # Print tree
    print(tree)
    print(f"\n[bold]Total folders:[/bold] {num_folders}")
    print(f"[bold]Total files:[/bold] {num_files}")

if __name__ == "__main__":
    main()
