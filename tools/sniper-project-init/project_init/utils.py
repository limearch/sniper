# project_init/utils.py
import sys
import time
import threading

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_info(message): print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")
def print_success(message): print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")
def print_error(message): print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}", file=sys.stderr)
def print_warn(message): print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} {message}")

class Spinner:
    def __init__(self, message="Working..."):
        self.message = message
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.spin)

    def __enter__(self):
        self.spin_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_running.set()
        self.spin_thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
        sys.stdout.flush()

    def spin(self):
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        while not self.stop_running.is_set():
            for char in spinner_chars:
                if self.stop_running.is_set(): break
                sys.stdout.write(f'\r{Colors.BLUE}[INFO]{Colors.ENDC} {self.message} {Colors.CYAN}{char}{Colors.ENDC}')
                sys.stdout.flush()
                time.sleep(0.1)