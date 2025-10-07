# project_init/utils.py
# This module provides utility functions and classes used across the project,
# such as colorized printing and a loading spinner.

import sys
import time
import threading

class Colors:
    """A class to hold ANSI color codes for terminal output."""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Formatted Print Functions ---

def print_info(message):
    """Prints an informational message in blue."""
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def print_success(message):
    """Prints a success message in green."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def print_error(message):
    """Prints an error message to stderr in red."""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}", file=sys.stderr)

def print_warn(message):
    """Prints a warning message in yellow."""
    print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} {message}")


# --- Spinner Class for long-running operations ---

class Spinner:
    """
    A context manager to display a spinner animation in the terminal for
    long-running operations.
    
    Usage:
        with Spinner("Doing something..."):
            time.sleep(3)
    """
    def __init__(self, message="Working..."):
        self.message = message
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.spin)

    def __enter__(self):
        """Starts the spinner thread when entering the 'with' block."""
        self.spin_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stops the spinner thread and cleans up the line when exiting the 'with' block."""
        self.stop_running.set()
        self.spin_thread.join()
        # Clear the line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
        sys.stdout.flush()

    def spin(self):
        """The target function for the spinner thread, handles the animation."""
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏" # Braille spinner characters
        while not self.stop_running.is_set():
            for char in spinner_chars:
                if self.stop_running.is_set():
                    break
                sys.stdout.write(f'\r{Colors.BLUE}[INFO]{Colors.ENDC} {self.message} {Colors.CYAN}{char}{Colors.ENDC}')
                sys.stdout.flush()
                time.sleep(0.1)