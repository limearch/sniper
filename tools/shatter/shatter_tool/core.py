# shatter_tool/core.py
import ctypes
import os
import sys
import json
from pathlib import Path
from lib.sniper_env import env

# Path to the shared library
LIB_NAME = "libshatter_engine.so"
LIB_PATH = Path(__file__).resolve().parents[1] / "lib" / LIB_NAME

# Define the C Callback function signature: void func(uint64_t, char*)
PROGRESS_CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_uint64, ctypes.c_char_p)

class CrackEngine:
    def __init__(self):
        if not LIB_PATH.exists():
            env.log.critical(f"Shared library not found at {LIB_PATH}")
            raise FileNotFoundError(str(LIB_PATH))
        try:
            self.lib = ctypes.CDLL(str(LIB_PATH))
        except OSError as e:
            env.log.critical(f"Failed to load shared library: {e}")
            raise

        # Define arguments for crack_wordlist
        # int crack_wordlist(path, salt, verifier, key_len, threads, out_buf, out_size, callback)
        self.lib.crack_wordlist.argtypes = [
            ctypes.c_char_p,        # wordlist_path
            ctypes.c_char_p,        # salt_hex
            ctypes.c_char_p,        # verifier_hex
            ctypes.c_int,           # key_len
            ctypes.c_int,           # threads
            ctypes.c_char_p,        # out_password
            ctypes.c_size_t,        # out_size
            PROGRESS_CALLBACK_TYPE  # progress_cb
        ]
        self.lib.crack_wordlist.restype = ctypes.c_int

    def crack(self, wordlist_path: str, salt_hex: str, verifier_hex: str, key_len: int, threads: int = 0, ui_callback=None) -> str:
        """
        Calls the C++ engine.
        ui_callback: A python function taking (attempts, current_word).
        """
        out_buf_size = 256
        out_buf = ctypes.create_string_buffer(out_buf_size)
        
        # Wrap the python function in the C callback type
        c_callback = PROGRESS_CALLBACK_TYPE(ui_callback) if ui_callback else None

        # Call C function
        res = self.lib.crack_wordlist(
            wordlist_path.encode('utf-8'),
            salt_hex.encode('utf-8'),
            verifier_hex.encode('utf-8'),
            int(key_len),
            int(threads),
            out_buf,
            ctypes.c_size_t(out_buf_size),
            c_callback
        )
        
        if res == 1:
            # Password found
            try:
                return out_buf.value.decode('utf-8')
            except Exception:
                # Fallback for weird encodings
                return out_buf.value.decode('latin-1')
        elif res == 0:
            return None
        else:
            raise RuntimeError("Engine returned error code")

class ShatterManager:
    """Manages Target JSON loading."""
    def __init__(self, target_file, wordlist_file, threads=None):
        self.target_file = target_file
        self.wordlist_file = wordlist_file
        self.threads = threads or 0
        self.target_data = self._load_target()

    def _load_target(self) -> dict:
        try:
            with open(self.target_file, 'r') as f:
                data = json.load(f)

            # Handle Zip2John JSON format
            if isinstance(data, dict) and "entries" in data:
                for entry in data["entries"]:
                    if entry.get("salt_hex") and entry.get("password_verifier_hex"):
                        return entry
                raise ValueError("No valid encrypted entries found in JSON.")

            # Handle direct single-entry JSON
            if data.get("salt_hex"):
                return data

            raise ValueError("Invalid JSON format in target file.")

        except Exception as e:
            env.log.error(f"Failed to load target: {e}")
            sys.exit(1)
