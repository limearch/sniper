#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SNIPER - Cyber Security Tool
============================
Modern, animated, and impressive introduction screen.

Author: Gemini
Date: 2025-10-09

Requirements:
- rich
- pyfiglet
"""

import argparse
import random
import sys
import threading
import time
from collections import deque
from typing import List

import pyfiglet
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.style import Style
from rich.text import Text

# --- Configuration ---
REFRESH_RATE = 20  # frames per second
DEFAULT_DURATION = 15  # seconds for the whole intro
MIN_DIMENSIONS = (80, 24)  # Minimum terminal dimensions (width, height)

# --- Theme and Styles ---
CYBER_GREEN = "#00ff00"
DARK_CYBER_GREEN = "#008700"
ACCENT_COLOR = "#00ffff"
ERROR_COLOR = "#ff0000"

SNIPER_STYLE = Style(color=CYBER_GREEN, bold=True)
PANEL_STYLE = Style(color=DARK_CYBER_GREEN)
ACCENT_STYLE = Style(color=ACCENT_COLOR)
GRANTED_STYLE = Style(color="white", bgcolor=CYBER_GREEN, bold=True)
ERROR_STYLE = Style(color=ERROR_COLOR, bold=True)


class MatrixStream:
    """Generates a continuous stream of matrix-style characters."""

    def __init__(self, lock: threading.Lock, stop_event: threading.Event, console_width: int):
        self.lock = lock
        self.stop_event = stop_event
        self.console_width = console_width
        self.stream = deque(maxlen=console_width // 2)
        self.chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def _generate_line(self) -> str:
        """Generates a single line of random characters."""
        line_length = self.console_width - 4  # Adjust for panel padding
        return "".join(random.choice(self.chars) for _ in range(line_length))

    def run(self):
        """Thread target function to continuously generate matrix lines."""
        while not self.stop_event.is_set():
            with self.lock:
                self.stream.append(self._generate_line())
            time.sleep(0.05)

    def get_renderable(self) -> Text:
        """Gets the current stream content as a rich Text object."""
        with self.lock:
            # Join lines and apply a gradient-like effect by varying opacity
            text = Text("\n", justify="left")
            stream_list = list(self.stream)
            for i, line in enumerate(reversed(stream_list)):
                opacity = max(0.1, (i + 1) / len(stream_list))
                style = Style(color=CYBER_GREEN, dim=(i > 2))
                text.append(line + "\n", style=style)
            return text


class IntroAnimator:
    """Manages the layout and animation sequence for the intro screen."""

    def __init__(self, console: Console, no_sound: bool, duration: int):
        self.console = console
        self.no_sound = no_sound
        self.duration = duration
        self.layout = self._create_layout()

        # Shared resources for background thread
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.matrix_stream = MatrixStream(self.lock, self.stop_event, console.width)

    def _create_layout(self) -> Layout:
        """Defines the terminal layout structure using rich.layout."""
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=7),
            Layout(ratio=1, name="main"),
            Layout(size=10, name="footer"),
        )
        layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
        return layout

    def _play_sound(self):
        """Plays the terminal bell sound if not disabled."""
        if not self.no_sound:
            self.console.print("\a", end="")

    def _type_text(self, text_obj: Text, content: str, delay: float = 0.01):
        """Animates text with a typing effect."""
        for char in content:
            text_obj.append(char)
            time.sleep(delay)
            self._play_sound()

    def run(self):
        """Main function to run the entire intro animation."""
        bg_thread = threading.Thread(target=self.matrix_stream.run)
        bg_thread.daemon = True
        bg_thread.start()

        with Live(self.layout, screen=True, transient=True, refresh_per_second=REFRESH_RATE) as live:
            try:
                self._animate_header(live)
                self._animate_main_body(live)
            except KeyboardInterrupt:
                # Gracefully handle Ctrl+C
                pass
            finally:
                # Signal the background thread to stop and wait for it
                self.stop_event.set()
                bg_thread.join()

        # Display final message
        self.console.print(
            Panel(
                Align.center("[b]ACCESS GRANTED[/b]", vertical="middle"),
                title="[b]Authentication Complete[/b]",
                border_style=GRANTED_STYLE,
                style=GRANTED_STYLE,
                height=5
            )
        )

    def _animate_header(self, live: Live):
        """Animates the SNIPER ASCII art logo."""
        sniper_art = pyfiglet.figlet_format("SNIPER", font="slant")
        art_text = Text(justify="center", style=SNIPER_STYLE)
        self.layout["header"].update(art_text)

        for i in range(len(sniper_art) + 1):
            art_text.truncate(0)
            art_text.append(sniper_art[:i])
            live.refresh()
            if i > 0 and sniper_art[i - 1] not in (' ', '\n'):
                self._play_sound()
            time.sleep(0.005)
        time.sleep(0.5)

    def _animate_main_body(self, live: Live):
        """Animates the system checks and information panels."""
        # Setup panels
        info_text = Text("", style=ACCENT_STYLE)
        self.layout["side"].update(
            Panel(info_text, title="[bold]System Intel[/bold]", border_style=PANEL_STYLE)
        )

        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, complete_style=ACCENT_STYLE),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            SpinnerColumn(spinner_name="dots", style=ACCENT_STYLE),
            expand=True,
        )
        self.layout["body"].update(
            Panel(progress, title="[bold]Initializing Subsystems[/bold]", border_style=PANEL_STYLE)
        )

        # Typing effect for side panel
        info_lines = [
            "OS: Kali Linux (Stealth Mode)",
            "CPU: QuantumCore X2 @ 8.2GHz",
            "IP: 127.0.0.1 (Proxied)",
            "Status: [bold green]SECURE[/bold green]"
        ]
        for line in info_lines:
            self._type_text(info_text, line + "\n")
            live.refresh()
        
        time.sleep(0.5)
        
        # Progress bar animation
        tasks = [
            "Booting kernel...",
            "Loading core modules...",
            "Establishing network link...",
            "Bypassing firewalls...",
            "Decrypting target manifest...",
            "Verifying payload integrity..."
        ]
        
        # Calculate sleep time per step based on total duration
        total_steps = 100 * len(tasks)
        step_duration = (self.duration - 3) / total_steps # Subtract time for header/other waits

        for task_desc in tasks:
            task = progress.add_task(f"[cyan]{task_desc}", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                self.layout["footer"].update(Panel(
                    self.matrix_stream.get_renderable(),
                    title="[bold]Live Data Stream[/bold]",
                    border_style=PANEL_STYLE
                ))
                live.refresh()
                time.sleep(step_duration)
        
        time.sleep(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="SNIPER - A cybersecurity command-line tool intro.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable the typing/interface sound effects."
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help=f"Set the approximate duration of the intro in seconds (default: {DEFAULT_DURATION}s)."
    )
    args = parser.parse_args()

    console = Console()

    # Check for minimum terminal size
    if console.width < MIN_DIMENSIONS[0] or console.height < MIN_DIMENSIONS[1]:
        console.print(
            f"Terminal too small ({console.width}x{console.height}). "
            f"Minimum required: {MIN_DIMENSIONS[0]}x{MIN_DIMENSIONS[1]}.",
            style=ERROR_STYLE
        )
        sys.exit(1)

    try:
        animator = IntroAnimator(console, args.no_sound, args.duration)
        animator.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation aborted by user.[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

