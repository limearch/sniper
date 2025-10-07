

## File: `crypt_utils/__init__.py` | Language: Python

```python

```

## File: `crypt_utils/core.py` | Language: Python

```python
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
except ImportError as e:
    print_error(f"Missing required library: {e.name}.")
    print_info("Please run: pip install cryptography tqdm")
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
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password)

def secure_delete(path, pbar):
    try:
        with open(path, "ba+") as f:
            length = f.tell()
            f.seek(0)
            f.write(os.urandom(length))
        os.remove(path)
    except Exception as e:
        with pbar.get_lock():
            pbar.write(f"{Colors.YELLOW}[WARN]{Colors.ENDC} Could not securely remove {os.path.basename(path)}: {e}")

def encrypt_single_file(file_path, password):
    out_path = file_path + ".enc"
    if os.path.exists(out_path):
        return (file_path, False, "Output file already exists.")
    
    try:
        salt = os.urandom(SALT_SIZE)
        key = derive_key(password.encode(), salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_SIZE)
        file_size = os.path.getsize(file_path)

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
    out_path = file_path[:-4]
    if os.path.exists(out_path):
        return (file_path, False, "Output file already exists.")

    try:
        with open(file_path, 'rb') as f_in:
            if f_in.read(len(MAGIC_HEADER)) != MAGIC_HEADER:
                return (file_path, False, "Invalid file format.")
            salt = f_in.read(SALT_SIZE)
            nonce = f_in.read(NONCE_SIZE)
            key = derive_key(password.encode(), salt)
            aesgcm = AESGCM(key)
            
            with open(out_path, 'wb') as f_out:
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if not chunk: break
                    decrypted_chunk = aesgcm.decrypt(nonce, chunk, None)
                    f_out.write(decrypted_chunk)
            return (file_path, True, None)
    except InvalidTag:
        if os.path.exists(out_path): os.remove(out_path)
        return (file_path, False, "Incorrect password or corrupted file.")
    except Exception as e:
        if os.path.exists(out_path): os.remove(out_path)
        return (file_path, False, str(e))

def find_files_in_dir(path, is_decrypt=False):
    files_to_process = []
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            if is_decrypt:
                if file.endswith(".enc"): files_to_process.append(full_path)
            else:
                if not file.endswith(".enc"): files_to_process.append(full_path)
    return files_to_process

```

# File: `bin/sniper-crypt` | Language: Python
```python
#!/usr/bin/env python3
import os
import sys
import getpass
import argparse
import secrets
import string
from queue import Queue
import threading

sys.path.insert(0,
os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypt_utils.core import (
    Colors, print_info, print_success, print_error, print_warn,
    find_files_in_dir, encrypt_single_file, decrypt_single_file,
secure_delete
)
from tqdm import tqdm

successful_files = []
failed_files = []
thread_lock = threading.Lock()

def worker_thread(queue, action_func, password, remove, pbar):
    while not queue.empty():
        file_path = queue.get()
        original_path, success, error_msg = action_func(file_path,
password)

        with thread_lock:
            if success:
                successful_files.append(original_path)
                if remove and action_func.__name__ ==
'encrypt_single_file':
                    pbar.write(f"{Colors.BLUE}[INFO]{Colors.ENDC}
Securely removing {os.path.basename(original_path)}...")
                    secure_delete(original_path, pbar)
            else:
                failed_files.append((original_path, error_msg))
                pbar.write(f"{Colors.RED}[ERROR]{Colors.ENDC}
Failed {os.path.basename(original_path)}: {error_msg}")

        pbar.update(1)
        queue.task_done()

def process_files_concurrently(files, action_func, password,
remove):
    q = Queue()
    for f in files: q.put(f)

    with tqdm(total=len(files),
desc=f"{action_func.__name__.split('_')[0].capitalize()}ing",
unit="file", ncols=80) as pbar:
        threads = []
        num_workers = min(10, os.cpu_count() or 1, len(files))
        for _ in range(num_workers):
            thread = threading.Thread(target=worker_thread,
args=(q, action_func, password, remove, pbar), daemon=True)
            threads.append(thread)
            thread.start()
        q.join()

def generate_password(length=24):
    alphabet = string.ascii_letters + string.digits +
string.punctuation.replace("'", "").replace('"', '').replace('\\',
'')
    password = ''.join(secrets.choice(alphabet) for _ in
range(length))
    return password

def handle_encrypt(args):
    path = args.path
    try:
        password = getpass.getpass("Enter encryption password: ")
        if not password: print_error("Password cannot be empty.");
sys.exit(1)
        if getpass.getpass("Confirm password: ") != password:
print_error("Passwords do not match."); sys.exit(1)
    except KeyboardInterrupt: print("\nOperation cancelled.");
sys.exit(0)

    if os.path.isdir(path):
        print_info(f"Scanning directory '{path}' for files...")
        files = find_files_in_dir(path, is_decrypt=False)
        if not files: print_info("No non-encrypted files found to
process."); return
        process_files_concurrently(files, encrypt_single_file,
password, args.remove)
    else:
        original_path, success, error_msg =
encrypt_single_file(path, password)
        if success:
            successful_files.append(original_path)
            if args.remove: secure_delete(original_path, None) # No
pbar for single file
        else:
            failed_files.append((original_path, error_msg))

def handle_decrypt(args):
    path = args.path
    try:
        password = getpass.getpass("Enter decryption password: ")
        if not password: print_error("Password cannot be empty.");
sys.exit(1)
    except KeyboardInterrupt: print("\nOperation cancelled.");
sys.exit(0)

    if os.path.isdir(path):
        print_info(f"Scanning directory '{path}' for .enc
files...")
        files = find_files_in_dir(path, is_decrypt=True)
        if not files: print_info("No encrypted (.enc) files found
to process."); return
        process_files_concurrently(files, decrypt_single_file,
password, False)
    else:
        original_path, success, error_msg =
decrypt_single_file(path, password)
        if success: successful_files.append(original_path)
        else: failed_files.append((original_path, error_msg))

def main():
    parser = argparse.ArgumentParser(prog="sniper-crypt",
formatter_class=argparse.RawTextHelpFormatter,
description=f"{Colors.BOLD}{Colors.MAGENTA}SNIPER: File & Folder
Encryption Tool{Colors.ENDC}")
    subparsers = parser.add_subparsers(dest="command",
required=True, help="Available commands")

    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt
a file or a folder.",
formatter_class=argparse.RawTextHelpFormatter)
    parser_encrypt.add_argument("path", help="The file or folder to
encrypt.")
    parser_encrypt.add_argument("-r", "--remove",
action="store_true", help="Securely remove original files after
encryption.")
    parser_encrypt.set_defaults(func=handle_encrypt)

    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt
a file or a folder.",
formatter_class=argparse.RawTextHelpFormatter)
    parser_decrypt.add_argument("path", help="The .enc file or
folder to decrypt.")
    parser_decrypt.set_defaults(func=handle_decrypt)

    parser_genpass = subparsers.add_parser("genpass",
help="Generate a strong, random password.",
formatter_class=argparse.RawTextHelpFormatter,
                                           epilog=f"Example:
{Colors.YELLOW}sniper-crypt genpass -l 32{Colors.ENDC}")
    parser_genpass.add_argument("-l", "--length", type=int,
default=24, help="Length of the password (default: 24).")
    parser_genpass.set_defaults(func=lambda args:
print_success(f"Generated Password:
{Colors.CYAN}{generate_password(args.length)}{Colors.ENDC}"))

    args = parser.parse_args()

    # Execute the function associated with the chosen subcommand
    args.func(args)

    # --- Final Report ---
    print("\n" + "-"*30)
    print(f"{Colors.BOLD}Operation Summary{Colors.ENDC}")
    if successful_files:
        print(f"{Colors.GREEN}Successfully processed:{Colors.ENDC}
{len(successful_files)} file(s)")
    if failed_files:
        print(f"{Colors.RED}Failed to process:{Colors.ENDC}
{len(failed_files)} file(s)")
        for f, err in failed_files:
            print(f"  - {os.path.basename(f)}: {err}")
    print("-" * 30)

if __name__ == "__main__":
    main()

```
