# help_printer.py
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Error: The 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

def show_compress_help(prog_name="compress"):
    """Displays the custom, rich-formatted help screen for the compress tool."""
    
    console = Console()
    
    title = Text("SNIPER: compress - File & Folder Compression Tool", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        f"[bold]Usage:[/] [yellow]{prog_name}[/] [green]-d <directory>[/] [green]-o <output_file>[/] [cyan][OPTIONS][/]"
    )
    
    main_options_text = """
[bold]Required Arguments:[/b]
  [green]-d, --directory <path>[/]   Directory to compress.
  [green]-o, --output <file>[/]      Output file name (e.g., archive.zip, archive.tar.gz).

[bold]General Options:[/b]
  [green]-v, --verbose[/]            Enable verbose mode to see file processing details.
  [green]-h, --help[/]               Show this help message and exit.
"""

    zip_options_text = """
[bold]ZIP Specific Options (Default Mode):[/b]
  [green]-l, --level <0-9>[/]        Compression level (0=none, 9=max).
  [green]-H, --skip-hidden[/]        Skip hidden files and folders (names starting with '.').
  [green]-P, --password <pass>[/]    (Note: Feature in development) Add a password to the ZIP archive.
  [green]-f, --filter <.ext>[/]      Only include files with this extension (e.g., .txt).
  [green]-e, --exclude <.ext>[/]      Exclude files with this extension (e.g., .log).
  [green]-t, --test[/] / [green]-c[/]           Test the ZIP archive's integrity after creation.
"""

    tar_options_text = """
[bold]TAR Specific Options:[/b]
  [green]-C, --compression <type>[/]  Create a TAR archive with a specific compression.
                         Choices: [cyan]gzip, bzip2, xz[/]. Using this option forces TAR mode.
"""

    examples_text = """
[bold]Examples:[/b]
  [#] Create a standard ZIP archive with verbose output
  [yellow]compress[/] [green]-d my_folder -o my_archive.zip -v[/]

  [#] Create a ZIP archive, but only include .c and .h files (using filter)
  [yellow]compress[/] [green]-d src -o source.zip -f .c -f .h[/] (Note: Multiple filters may require script changes)

  [#] Create a compressed TAR archive using gzip
  [yellow]compress[/] [green]-d project_files -o backup.tar.gz -C gzip[/]

  [#] The tool will also auto-detect TAR mode from the filename
  [yellow]compress[/] [green]-d data -o data_archive.tar.bz2[/]
"""
    
    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(main_options_text.strip()), title="Main Options", border_style="blue"))
    console.print(Panel(Text.from_markup(zip_options_text.strip()), title="ZIP Options", border_style="cyan"))
    console.print(Panel(Text.from_markup(tar_options_text.strip()), title="TAR Options", border_style="green"))
    console.print(Panel(Text.from_markup(examples_text.strip()), title="Examples", border_style="yellow"))

if __name__ == "__main__":
    prog_name_arg = sys.argv[0]
    if len(sys.argv) > 1:
        # Extract the base name of the program from the path
        prog_name_arg = sys.argv[1].split('/')[-1]
    
    show_compress_help()