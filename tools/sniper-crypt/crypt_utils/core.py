# crypt_utils/core.py
import os
import sys
import threading
from queue import Queue

# --- Shared Utilities ---
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
def print_warn(message): print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} {message}", file=sys.stderr)

# --- Cryptography Imports and Constants ---
try:
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    from tqdm import tqdm
    from rich.console import Console # Check for rich as well
except ImportError as e:
    print_error(f"Missing required library: {e.name}.")
    print_info("Please run: pip install cryptography tqdm rich")
    print_info("On Termux, you may need: pkg install build-essential libffi-dev rust")
    sys.exit(1)

# --- Constants ---
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
CHUNK_SIZE = 64 * 1024  # 64KB chunks
MAGIC_HEADER = b"SNIPER_ENC"

# --- Core Functions ---
def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derives a 32-byte key from a password and salt using Scrypt."""
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password)

def secure_delete(path, pbar):
    """Securely deletes a file by overwriting it with random data first."""
    try:
        # pbar can be None if it's a single file operation
        if pbar:
            with pbar.get_lock():
                 pbar.write(f"{Colors.YELLOW}[WARN]{Colors.ENDC} Securely overwriting {os.path.basename(path)}...")
        
        with open(path, "ba+") as f:
            length = f.tell()
            if length > 0:
                f.seek(0)
                f.write(os.urandom(length))
        os.remove(path)
    except Exception as e:
        error_msg = f"{Colors.RED}[ERROR]{Colors.ENDC} Could not securely remove {os.path.basename(path)}: {e}"
        if pbar:
            with pbar.get_lock():
                pbar.write(error_msg)
        else:
            print_error(error_msg)


def encrypt_single_file(file_path, password):
    """Encrypts a single file. Returns a tuple (path, success, error_message)."""
    out_path = file_path + ".enc"
    if os.path.exists(out_path):
        return (file_path, False, "Output file already exists.")
    
    try:
        salt = os.urandom(SALT_SIZE)
        key = derive_key(password.encode(), salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_SIZE)

        with open(file_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
            f_out.write(MAGIC_HEADER)
            f_out.write(salt)
            f_out.write(nonce)
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk: break
                encrypted_chunk = aesgcm.encrypt(nonce, chunk, None)
                f_out.write(encrypted_chunk)
        return (file_path, True, None)
    except Exception as e:
        if os.path.exists(out_path): os.remove(out_path)
        return (file_path, False, str(e))

def decrypt_single_file(file_path, password):
    """Decrypts a single file. Returns a tuple (path, success, error_message)."""
    out_path = file_path[:-4]
    if os.path.exists(out_path):
        return (file_path, False, "Output file already exists.")

    try:
        with open(file_path, 'rb') as f_in:
            if f_in.read(len(MAGIC_HEADER)) != MAGIC_HEADER:
                return (file_path, False, "Invalid file format (not a SNIPER encrypted file).")
            salt = f_in.read(SALT_SIZE)
            nonce = f_in.read(NONCE_SIZE)
            key = derive_key(password.encode(), salt)
            aesgcm = AESGCM(key)
            
            with open(out_path, 'wb') as f_out:
                # The first chunk read might be smaller
                ciphertext_chunk = f_in.read(CHUNK_SIZE + 16) # Read chunk + auth tag size
                while ciphertext_chunk:
                    decrypted_chunk = aesgcm.decrypt(nonce, ciphertext_chunk, None)
                    f_out.write(decrypted_chunk)
                    ciphertext_chunk = f_in.read(CHUNK_SIZE + 16)
            return (file_path, True, None)
    except InvalidTag:
        if os.path.exists(out_path): os.remove(out_path)
        return (file_path, False, "Incorrect password or corrupted file.")
    except Exception as e:
        if os.path.exists(out_path): os.remove(out_path)
        return (file_path, False, str(e))

def find_files_in_dir(path, is_decrypt=False):
    """Recursively finds files in a directory for processing."""
    files_to_process = []
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            if is_decrypt:
                if file.endswith(".enc"): files_to_process.append(full_path)
            else:
                # When encrypting, avoid re-encrypting .enc files and also avoid the log file.
                if not file.endswith(".enc") and not file.endswith("sniper-config.log"):
                     files_to_process.append(full_path)
    return files_to_process