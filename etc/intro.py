# File: intro.py | Language: Python
# Description: A cinematic, multi-threaded, and highly animated introduction for the SNIPER toolkit.

import os
import sys
import time
import random
from threading import Event, Thread
from collections import deque

# --- Dependency Check ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.layout import Layout
    from rich.columns import Columns
except ImportError:
    print("\nError: The 'rich' library is required for this introduction.")
    print("Please install it by running: pip install rich\n")
    sys.exit(1)

# --- Console and Style Setup ---
console = Console()

SNIPER_ART = r"""
███████╗███╗░░██╗██╗██████╗░███████╗██████╗░
██╔════╝████╗░██║██║██╔══██╗██╔════╝██╔══██╗
███████╗██╔██╗██║██║██████╔╝█████╗░░██████╔╝
╚════██║██║╚████║██║██╔═══╝░██╔══╝░░██╔══██╗
███████║██║░╚███║██║██║░░░░░███████╗██║░░██║
╚══════╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝
"""

# Color Palette
PRIMARY_COLOR = "bold magenta"
SECONDARY_COLOR = "cyan"
SUCCESS_COLOR = "bold green"
WARN_COLOR = "bold yellow"
ACCENT_COLOR = "bold red"
BACKGROUND_TEXT_COLOR = "grey30"

# --- Background Animation Thread ---

class BackgroundScroller(Thread):
    """A thread to generate a continuous stream of background hex data."""
    def __init__(self):
        super().__init__(daemon=True)
        self.stop_event = Event()
        self.lines = deque(maxlen=console.height)

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            line = " ".join(f"{random.randint(0, 255):02X}" for _ in range(console.width // 3))
            self.lines.append(line)
            time.sleep(0.05)

    def get_renderable(self) -> Text:
        return Text("\n".join(self.lines), style=BACKGROUND_TEXT_COLOR)

# --- Main Animator Class ---

class IntroAnimator:
    """Manages the entire animation sequence within a rich Layout."""

    def __init__(self):
        self.layout = self.make_layout()
        self.background_scroller = BackgroundScroller()

    # --- HELPER METHODS MOVED INSIDE THE CLASS ---
    def clear_screen(self):
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def play_sound(self, count=1, delay=0.03):
        """Plays the terminal bell sound."""
        for _ in range(count):
            sys.stdout.write("\a")
            sys.stdout.flush()
            time.sleep(delay)

    def _type_text(self, panel_name: str, text: str, live: Live, style: str = "default"):
        """Animates typing text into a specific panel."""
        lines = text.strip().split('\n')
        current_text = ""
        for line in lines:
            current_text += "\n" if current_text else ""
            for i in range(len(line) + 1):
                self.layout[panel_name].update(Align.center(Text(current_text + line[:i], style=style), vertical="middle"))
                live.update(self.layout, refresh=True)
                time.sleep(0.01)
            current_text += line
        time.sleep(0.5)
    # -----------------------------------------------

    def make_layout(self) -> Layout:
        """Defines the TUI layout structure."""
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=8),
            Layout(ratio=1, name="main"),
            Layout(size=3, name="footer"),
        )
        layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
        return layout

    def run_boot_sequence(self, live: Live):
        """Displays a multi-bar progress animation."""
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, complete_style=SECONDARY_COLOR),
            "[progress.percentage]{task.percentage:>3.0f}%",
        )
        tasks = [
            progress.add_task(f"[{WARN_COLOR}]CORE SYSTEMS", total=100),
            progress.add_task(f"[{WARN_COLOR}]TOOLCHAIN   ", total=100),
            progress.add_task(f"[{WARN_COLOR}]INTERFACE   ", total=100),
        ]
        self.layout["body"].update(Align.center(progress, vertical="middle"))
        
        while not progress.finished:
            for task_id in tasks:
                progress.update(task_id, advance=random.uniform(0.5, 2.0))
            live.update(self.layout)
            time.sleep(0.01)
        self.play_sound(2)
        time.sleep(0.5)
        self.layout["body"].update("") # Clear the progress bars

    def animate_logo_reveal(self, live: Live):
        """Reveals the SNIPER logo with a decryption/glitch effect."""
        self.clear_screen()
        self.play_sound()
        
        target_lines = SNIPER_ART.strip().split('\n')
        height, width = len(target_lines), len(target_lines[0])
        
        buffer = [[' ' for _ in range(width)] for _ in range(height)]
        glitch_chars = "▓▒░"

        # Phase 1: Glitchy appearance
        for _ in range(20):
            r, c = random.randint(0, height - 1), random.randint(0, width - 1)
            buffer[r][c] = random.choice(glitch_chars)
            output = "\n".join("".join(row) for row in buffer)
            self.layout["header"].update(Align.center(Text(output, style=ACCENT_COLOR)))
            live.update(self.layout)
            time.sleep(0.01)
            if _ % 5 == 0: self.play_sound()

        # Phase 2: Decrypting character by character
        all_positions = [(r, c) for r in range(height) for c in range(width)]
        random.shuffle(all_positions)
        
        for i, (r, c) in enumerate(all_positions):
            buffer[r][c] = target_lines[r][c]
            if i % 20 == 0: # Update screen less frequently for performance
                output = "\n".join("".join(row) for row in buffer)
                self.layout["header"].update(Align.center(Text(output, style=PRIMARY_COLOR)))
                live.update(self.layout)
                time.sleep(0.001)
                if i % 100 == 0: self.play_sound()

        # Final clean render
        self.clear_screen()
        self.layout["header"].update(Align.center(Text(SNIPER_ART, style=PRIMARY_COLOR)))
        live.update(self.layout)
        self.play_sound(3)
        time.sleep(0.5)

    def display_info_panels(self, live: Live):
        """Displays project info in side-by-side panels."""
        overview_content = "A unified, cross-platform toolkit designed for maximum efficiency. It combines high-performance compiled utilities with flexible scripting for any task."
        components_content = f"""• [{SUCCESS_COLOR}]C Tools:[/] fastfind, compress, run
• [{SUCCESS_COLOR}]Py Scripts:[/] social-dive, format
• [{SUCCESS_COLOR}]Build System:[/] build.sh
• [{SUCCESS_COLOR}]Shell Env:[/] Zsh Integration"""

        overview_panel = Panel("", title=f"[{WARN_COLOR}]OVERVIEW[/]", border_style=WARN_COLOR, expand=True)
        components_panel = Panel("", title=f"[{WARN_COLOR}]COMPONENTS[/]", border_style=WARN_COLOR, expand=True)
        
        self.layout["side"].update(overview_panel)
        self.layout["body"].update(components_panel)
        live.update(self.layout)
        time.sleep(0.5)

        # Typing effect
        for char in overview_content:
            overview_panel.renderable += char
            live.update(self.layout)
            time.sleep(0.015)
        
        for char in components_content:
            components_panel.renderable += char
            live.update(self.layout)
            time.sleep(0.015)

        time.sleep(2)

    def run_final_sequence(self, live: Live):
        """Displays the final 'SYSTEM READY' animation."""
        console.print()
        final_checks = [
            "Dependency integrity check........ PASSED",
            "Toolchain verification........... PASSED",
            "Environment configuration........ LOADED",
            "Security protocols............. ACTIVE",
        ]
        
        # We need to render the final state before the last animation
        final_layout = self.layout
        
        for line in final_checks:
            # Re-rendering everything in the loop is inefficient, but necessary for the typing effect
            # within the Live context. We'll simulate it instead for better performance here.
            console.print(Align.center(Text(line, style=SUCCESS_COLOR)))
            self.play_sound()
            time.sleep(0.2)
        
        time.sleep(1)
        console.print()
        
        access_granted_text = Text("ACCESS GRANTED", style=f"bold black on {SUCCESS_COLOR}", justify="center")
        
        # Blinking effect inside the live renderer for smoothness
        for i in range(5):
            self.layout["footer"].update(Align.center(access_granted_text if i % 2 == 0 else ""))
            live.update(self.layout)
            self.play_sound()
            time.sleep(0.15)
        
        self.layout["footer"].update(Align.center(access_granted_text))
        live.update(self.layout)


    def run(self):
        """Main entry point to start the entire animation sequence."""
        try:
            console.show_cursor(False)
            self.clear_screen()
            self.background_scroller.start()

            with Live(self.layout, screen=True, transient=False, refresh_per_second=60) as live:
                def update_background():
                    self.layout["side"].update(self.background_scroller.get_renderable())

                # --- Sequence Start ---
                update_background()
                self.layout["footer"].update(Align.center(Text("BOOTING...", style=WARN_COLOR)))
                live.update(self.layout)
                time.sleep(1)

                update_background()
                self.run_boot_sequence(live)

                update_background()
                self.layout["body"].update("")
                self.layout["footer"].update(Align.center(Text("DECRYPTING IDENTITY...", style=ACCENT_COLOR)))
                self.animate_logo_reveal(live)
                
                update_background()
                self.layout["footer"].update(Align.center(Text("Precision Toolkit for Developers and Power Users", style=SECONDARY_COLOR)))
                time.sleep(1.5)

                update_background()
                self.layout["footer"].update(Align.center(Text("LOADING MODULE DATA...", style=WARN_COLOR)))
                self.display_info_panels(live)
                
                update_background()
                self.layout["side"].update("")
                self.layout["body"].update("")
                self.layout["footer"].update("")

                self.run_final_sequence(live)
                
                time.sleep(2)
        
        except KeyboardInterrupt:
            console.print(f"\n[{WARN_COLOR}]USER ABORT. SHUTTING DOWN...[/]")
        finally:
            self.background_scroller.stop()
            console.show_cursor(True)
            # A final clear to leave the user with a clean terminal
            self.clear_screen()

if __name__ == "__main__":
    animator = IntroAnimator()
    animator.run()
