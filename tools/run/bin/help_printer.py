# help_printer.py
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Error: The 'rich' library is required for the help screen. Run: pip install rich")
    sys.exit(1)

def show_run_help(prog_name="run"):
    """Displays the custom, rich-formatted help screen for the run tool."""
    
    console = Console()
    
    title = Text("SNIPER: run - Universal Code Runner", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        f"[bold]Usage:[/] [yellow]{prog_name}[/] [cyan]<file>[/] [green][file_args...][/] [cyan][OPTIONS][/]"
    )
    
    main_panel_text = """
[bold]Description:[/b]
  A powerful tool to seamlessly compile, run, and manage code for
  various programming languages with a single command. It automatically
  detects the language and handles the build process.

[bold]Arguments:[/b]
  [cyan]<file>[/]               The source code file to run.
  [green][file_args...][/]     Optional arguments to pass to the executed program.
"""

    options_text = """
[bold]Core Features & Options:[/b]
  [green]-t, --time[/]           Measure and report execution time and memory usage.
  [green]-v, --verbose[/]        Enable verbose output for compilation and execution steps.
  [green]-w, --watch[/]          Watch the file for changes and re-run automatically.
  [green]-j, --parallel[/]       Run multiple files in parallel.
  [green]-i, --interactive[/]    Run in interactive shell mode.
  [green]--limit-time N[/]      Set a CPU time limit of N seconds for the execution.
  [green]--limit-mem N[/]       Set a memory limit of N kilobytes for the execution.
  [green]-h, --help[/]           Display this help message.
"""

    dependencies_text = """
[bold]Dependencies:[/b]
  - For compiled languages, a corresponding compiler must be in your PATH
    (e.g., [cyan]gcc[/], [cyan]g++[/], [cyan]rustc[/], [cyan]javac[/], [cyan]go[/]).
  - For interpreted languages, an interpreter must be in your PATH
    (e.g., [cyan]python3[/], [cyan]node[/], [cyan]ruby[/], [cyan]dart[/]).
"""
    
    examples_text = """
[bold]Examples:[/b]
  [#] Run a Python script with arguments
  [yellow]run my_script.py arg1 "hello world"[/]

  [#] Compile and run a C program with a performance report
  [yellow]run --time --limit-mem 16384 my_program.c[/]

  [#] Automatically re-run a Node.js server on file changes
  [yellow]run --watch server.js[/]
"""
    
    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(main_panel_text.strip()), title="Overview", border_style="blue"))
    console.print(Panel(Text.from_markup(options_text.strip()), title="Options", border_style="cyan"))
    console.print(Panel(Text.from_markup(examples_text.strip()), title="Examples", border_style="green"))
    console.print(Panel(Text.from_markup(dependencies_text.strip()), title="Dependencies", border_style="yellow"))
    sys.exit(0)

if __name__ == "__main__":
    prog_name_arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    show_run_help()