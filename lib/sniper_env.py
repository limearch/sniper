# File: lib/sniper_env.py
# Description: The core environment management unit for the SNIPER toolkit.
# (FINAL, ADVANCED VERSION with structured, multi-level file logging)

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from functools import lru_cache
from logging.handlers import RotatingFileHandler

# --- START: Custom Logging Level Setup ---

# 1. Define a new logging level number for configuration updates.
UPDATE_LEVEL_NUM = 25
SUCCESS_LEVEL_NUM = 22
logging.addLevelName(UPDATE_LEVEL_NUM, "UPDATE")

logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def update(self, message, *args, **kwargs):
    """Adds a new 'log.update()' method to the logger instance."""
    if self.isEnabledFor(UPDATE_LEVEL_NUM):
        self._log(UPDATE_LEVEL_NUM, message, args, **kwargs)

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)
# 2. Add the new method to the base Logger class.
logging.Logger.update = update
logging.Logger.success = success

# --- END: Custom Logging Level Setup ---


# --- START: Multi-Color Console Formatter ---

class ColorFormatter(logging.Formatter):
    """
    A custom formatter that applies different colors to log levels for console output.
    """
    # Define ANSI color codes
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = '\033[0m'
    MAGENTA = '\033[0;35m'
    BOLD_RED = "\033[1;31m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    WHITE = '\033[97m'
    
    # Define the format string for each log level
    FORMATS = {
        logging.DEBUG: f"{CYAN}[%(levelname)s]{RESET} {CYAN}[%(name)s] %(message)s{RESET}",
        logging.INFO: f"{BOLD}{BLUE}[%(levelname)s]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
        logging.WARNING: f"{BOLD}{YELLOW}[WARN]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
        UPDATE_LEVEL_NUM: f"{BOLD}{GREEN}[UPDATE]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
        SUCCESS_LEVEL_NUM: f"{BOLD}{WHITE}[{GREEN}SUCCESS{WHITE}]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
        logging.ERROR: f"{BOLD}{RED}[ERROR]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
        logging.CRITICAL: f"{BOLD_RED}[CRITICAL]{RESET} {BOLD}{CYAN}[%(name)s]{RESET} %(message)s",
    }

    def format(self, record):
        # Override level name for WARNING to be 'WARN' for brevity
        if record.levelno == logging.WARNING:
            record.levelname = 'WARN'
            
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# --- END: Multi-Color Console Formatter ---


class SniperEnv:
    """
    A singleton class that represents the SNIPER toolkit's environment.
    """
    _instance = None

    def __new__(cls):
        """Ensures that only one instance of SniperEnv is ever created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(SniperEnv, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Private initializer, called only once upon instance creation."""
        self.ROOT_DIR = self._find_project_root()
        if not self.ROOT_DIR:
            raise FileNotFoundError("SNIPER root not found.")

        # --- Define Core Project Paths ---
        self.CONFIG_DIR = self.ROOT_DIR / "config"
        self.TOOLS_DIR = self.ROOT_DIR / "tools"
        self.LIB_DIR = self.ROOT_DIR / "lib"
        self.BIN_DIR = self.ROOT_DIR / "bin"
        self.CONFIG_PATH = self.CONFIG_DIR / "sniper-config.json"
        self.LOG_PATH = self.CONFIG_DIR / "sniper-config.log"
        
        self.PLATFORM = self._detect_platform()
        self.log = self._setup_logger()
        self.log.debug("SniperEnv initialized. Project root: %s", self.ROOT_DIR)
        # Create a dedicated cache directory in the user's home folder.
        home_dir = Path.home()
        self.CACHE_DIR = home_dir / ".cache" / "sniper"
        try:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback to config dir if cache can't be created
            self.CACHE_DIR = self.CONFIG_DIR
        # --- END: NEW CACHE DIRECTORY LOGIC ---

        self.LOG_PATH = self.CONFIG_DIR / "sniper-config.log" # Log path remains in config
        
        self.PLATFORM = self._detect_platform()
        self.log = self._setup_logger()
        self.log.debug("SniperEnv initialized. Cache dir: %s", self.CACHE_DIR)
        
    def command_exists(self, command: str) -> bool:
        """
        Checks if a command-line tool exists in the system's PATH.
        
        Args:
            command: The name of the command to check (e.g., 'shfmt').
        
        Returns:
            True if the command is found, False otherwise.
        """
        return shutil.which(command) is not None
    def _find_project_root(self) -> Path | None:
        """Traverses upwards to find the project root directory."""
        current_dir = Path(__file__).parent.resolve()
        while current_dir != current_dir.parent:
            if (current_dir / "config" / "sniper-config.json").is_file():
                return current_dir
            current_dir = current_dir.parent
        return None

    def _detect_platform(self) -> str:
        """Detects the current operating system with special handling for Termux."""
        if sys.platform in ('win32', 'cygwin'): return 'win'
        if sys.platform == 'darwin': return 'macosx'
        if 'com.termux' in os.environ.get('PREFIX', ''): return 'termux'
        if sys.platform.startswith('linux'): return 'linux'
        return 'unknown'

    def _setup_logger(self) -> logging.Logger:
        """
        Configures the root logger for the SNIPER project.
        - Console handler shows INFO and above with colors.
        - File handler logs only UPDATE, WARNING, and ERROR levels with a specific format.
        """
        logger = logging.getLogger("SNIPER")
        logger.setLevel(logging.DEBUG) # Capture all levels at the root
        
        if logger.hasHandlers():
            logger.handlers.clear()

        # --- Console Handler (for interactive feedback) ---
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO) # Show INFO and above in the console
        console_handler.setFormatter(ColorFormatter())
        logger.addHandler(console_handler)

        # --- File Handler (for persistent, critical logs) ---
        try:
            self.LOG_PATH.touch(exist_ok=True)
        except OSError as e:
            logger.critical("Could not write to log file, disabling file logging. Reason: %s", e)
        else:
            file_handler = RotatingFileHandler(
                self.LOG_PATH, maxBytes=1024 * 1024, backupCount=3
            )
            # This handler will log our custom UPDATE level and anything WARNING or higher.
            file_handler.setLevel(UPDATE_LEVEL_NUM) 
            # This specific format matches the user's request.
            file_formatter = logging.Formatter(
                '[%(asctime)s] - [%(levelname)s] - [%(name)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        logger.debug("Logger configured. File logging is %s.", "enabled" if any(isinstance(h, RotatingFileHandler) for h in logger.handlers) else "disabled")
        return logger

    @property
    @lru_cache(maxsize=1)
    def config(self) -> dict:
        """Lazily loads, parses, and caches the main sniper-config.json file."""
        if not self.CONFIG_PATH.is_file():
            self.log.error("Global config file not found at %s", self.CONFIG_PATH)
            return {}
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.log.error("Failed to load or parse sniper-config.json: %s", e)
            return {}

    def save_config(self, new_config: dict, change_source: str = "core") -> bool:
        """
        Saves the provided dictionary to sniper-config.json.
        This is a low-level function; logging should be handled by the caller.
        """
        try:
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4)
            # Clear the cache to force a re-read on the next access.
            self.__class__.config.fget.cache_clear()
            return True
        except IOError as e:
            log_instance = logging.getLogger(f"SNIPER.{change_source}")
            log_instance.error("Failed to save configuration: %s", e)
            return False

    def log_config_update(self, action: str, category: str, key: str, value: str, source: str):
        """
        Logs a structured configuration change message using the custom UPDATE level.
        
        Args:
            action (str): The action taken (e.g., "SET", "DELETE").
            category (str): The top-level key in the JSON.
            key (str): The specific key being changed.
            value (str): The new value (can be None for DELETE).
            source (str): The name of the tool making the change.
        """
        log_instance = logging.getLogger(f"SNIPER.{source}")
        message = f"{action}: category='{category}' key='{key}'"
        if value is not None:
            message += f" value='{value}'"
        log_instance.update(message)

    def get_tool_path(self, tool_name: str) -> Path | None:
        """Returns the absolute path to a specific tool's directory."""
        path = self.TOOLS_DIR / tool_name
        return path if path.is_dir() else None

    def find_all_executables(self) -> list[str]:
        """Scans all 'bin' directories to find all available executables."""
        executables = set()
        if self.BIN_DIR.is_dir():
            for item in self.BIN_DIR.iterdir():
                if item.is_file() and os.access(item, os.X_OK):
                    executables.add(item.name)
        if self.TOOLS_DIR.is_dir():
            for tool_dir in self.TOOLS_DIR.iterdir():
                tool_bin_dir = tool_dir / "bin"
                if tool_bin_dir.is_dir():
                    for item in tool_bin_dir.iterdir():
                        if item.is_file() and os.access(item, os.X_OK):
                           executables.add(item.name)
        return sorted(list(executables))

    def run_command(self, command: list[str], **kwargs) -> subprocess.CompletedProcess:
        """A consistent and safe wrapper for running external commands."""
        self.log.debug("Running command: %s", " ".join(command))
        kwargs.setdefault('capture_output', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('check', False)
        return subprocess.run(command, **kwargs)

# --- Singleton Instance ---
# This creates the one and only instance of SniperEnv for the entire project.
env = SniperEnv()
Colors = ColorFormatter()

# --- Self-Test Block ---
# This code will only run if you execute this file directly (e.g., `python lib/sniper_env.py`).
# It's useful for quick diagnostics and verification.
if __name__ == "__main__":
    print("--- SNIPER Environment Self-Test ---")
    
    # Set logger to DEBUG for this test to show all messages
    env.log.setLevel(logging.DEBUG)
    console_handler = env.log.handlers[0] # Assuming console is first
    console_handler.setLevel(logging.DEBUG)
    
    env.log.name = "self-test" # Set name for context
    
    env.log.info(f"Project Root: {env.ROOT_DIR}")
    env.log.info(f"Platform: {env.PLATFORM}")
    
    # Test config loading
    is_config_loaded = bool(env.config)
    env.log.info(f"Config Loaded: {'Yes' if is_config_loaded else 'No'}")
    if is_config_loaded:
        env.log.info(f"  User Shell from config: {env.config.get('user', {}).get('shell')}")
    
    # Test path finding
    env.log.info(f"Path to 'fastfind' tool: {env.get_tool_path('fastfind')}")
    
    # Test executable discovery
    executables = env.find_all_executables()
    env.log.info(f"Found {len(executables)} executables:")
    for exe in executables:
        print(f"      - {exe}") # Use print for cleaner list
    
    # Test logger functionality
    env.log.debug("This is a debug message.")
    env.log.info("This is an info message.")
    env.log.warning("This is a warning message.")
    env.log.error("This is an error message.")
    env.log.update("This is an update message.")
    env.log.critical("This is an CRITICAL message.")
    env.log.success("This is an CRITICAL message.")

    print("\n--- Self-Test Complete ---")
