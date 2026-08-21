"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RSA Cryptographic System  v3.0                          ║
║              Secure Key Management & Professional Data Protection           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture (Single-File Modules):
  § 1  Constants & Configuration
  § 2  Custom Exception Hierarchy
  § 3  Console Output Formatter
  § 4  KeyManager   — key lifecycle (generate / load / info / backup)
  § 5  CryptoEngine — RSA-OAEP, Hybrid AES-256-GCM+RSA, PSS signing
  § 6  InteractiveMenu — terminal-based TUI
  § 7  CLI (argparse)
  § 8  Entry Point

Requirements:
  pip install cryptography

Python: 3.9+
"""

# ─────────────────────────────────────────────────────────────────────────────
# § 1  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import json
import logging
import hashlib
import getpass
import argparse
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VERSION         = "3.0.0"
AES_KEY_BYTES   = 32          # AES-256
GCM_NONCE_BYTES = 12
GCM_TAG_BYTES   = 16
HYBRID_MAGIC    = b"RSH3"     # 4-byte header for hybrid-encrypted files
VALID_KEY_SIZES = (2048, 3072, 4096)


class _C:
    """ANSI colour codes; auto-disabled when stdout is not a TTY."""
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"

    @classmethod
    def disable(cls) -> None:
        for attr in list(vars(cls)):
            if not attr.startswith("_") and attr != "disable":
                setattr(cls, attr, "")


if not sys.stdout.isatty():
    _C.disable()


# ─────────────────────────────────────────────────────────────────────────────
# § 2  CUSTOM EXCEPTION HIERARCHY
# ─────────────────────────────────────────────────────────────────────────────

class RSASystemError(Exception):
    """Base class for all RSA-System errors."""


class KeyNotFoundError(RSASystemError, FileNotFoundError):
    """Raised when a key file cannot be located on disk."""


class KeyLoadError(RSASystemError):
    """Raised when a key file exists but cannot be parsed (wrong password, corrupt)."""


class DecryptionError(RSASystemError):
    """Raised when an RSA or AES decryption operation fails."""


class SignatureVerificationError(RSASystemError):
    """Raised when PSS signature verification fails."""


class InvalidInputError(RSASystemError, ValueError):
    """Raised for malformed input (bad hex, unsupported key size, etc.)."""


# ─────────────────────────────────────────────────────────────────────────────
# § 3  CONSOLE OUTPUT FORMATTER
# ─────────────────────────────────────────────────────────────────────────────

class Console:
    """
    All terminal output is routed through this class so that
    formatting, colours, and structure remain consistent.
    """
    WIDTH = 72

    # ── Static Display ────────────────────────────────────────────────────
    @staticmethod
    def banner() -> None:
        print(
            f"\n{_C.CYAN}{_C.BOLD}"
            "╔══════════════════════════════════════════════════════════════════════╗\n"
            f"║          RSA Cryptographic System  ·  v{VERSION:<6}                     ║\n"
            "║          AES-256-GCM + RSA-4096  ·  PSS Signatures                  ║\n"
            "╚══════════════════════════════════════════════════════════════════════╝"
            f"{_C.RESET}"
        )

    @staticmethod
    def section(title: str) -> None:
        pad = "─" * max(0, Console.WIDTH - len(title) - 4)
        print(f"\n{_C.BLUE}{_C.BOLD}── {title} {pad}{_C.RESET}")

    @staticmethod
    def divider() -> None:
        print(f"{_C.DIM}{'─' * Console.WIDTH}{_C.RESET}")

    # ── Status Messages ───────────────────────────────────────────────────
    @staticmethod
    def success(msg: str) -> None:
        print(f"{_C.GREEN}  ✓  {msg}{_C.RESET}")

    @staticmethod
    def error(msg: str) -> None:
        print(f"{_C.RED}  ✗  {msg}{_C.RESET}", file=sys.stderr)

    @staticmethod
    def warning(msg: str) -> None:
        print(f"{_C.YELLOW}  ⚠  {msg}{_C.RESET}")

    @staticmethod
    def info(msg: str) -> None:
        print(f"{_C.CYAN}  ℹ  {msg}{_C.RESET}")

    # ── Data Display ──────────────────────────────────────────────────────
    @staticmethod
    def result(label: str, value: str, chunk: int = 80) -> None:
        """Print a labelled value, wrapping long hex strings for readability."""
        print(f"\n{_C.BOLD}  {label}:{_C.RESET}")
        for i in range(0, len(value), chunk):
            print(f"  {_C.YELLOW}{value[i:i + chunk]}{_C.RESET}")

    @staticmethod
    def kv(label: str, value: str) -> None:
        """Print a compact key-value metadata line."""
        print(f"  {_C.DIM}{label:<22}{_C.RESET}{_C.CYAN}{value}{_C.RESET}")

    # ── Interactive Helpers ───────────────────────────────────────────────
    @staticmethod
    def menu(options: List[Tuple[str, str]]) -> str:
        """Render a numbered menu; return the user's raw input."""
        print()
        for idx, (_, description) in enumerate(options, start=1):
            print(f"  {_C.CYAN}{_C.BOLD}[{idx}]{_C.RESET}  {description}")
        print(f"  {_C.CYAN}{_C.BOLD}[0]{_C.RESET}  Exit")
        print()
        return input(f"{_C.BOLD}  ► Choose option: {_C.RESET}").strip()

    @staticmethod
    def ask(prompt: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        value  = input(f"  {_C.BOLD}{prompt}{suffix}: {_C.RESET}").strip()
        return value or default

    @staticmethod
    def confirm(prompt: str) -> bool:
        ans = input(f"  {_C.YELLOW}{prompt} (yes/no): {_C.RESET}").strip().lower()
        return ans in ("yes", "y")


# ─────────────────────────────────────────────────────────────────────────────
# § 4  KEY MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class KeyManager:
    """
    Manages the full RSA key lifecycle:
      · generate()        — create a new key pair (optional password protection)
      · load_private()    — deserialise private key from PEM
      · load_public()     — deserialise public key from PEM
      · show_info()       — display fingerprint and metadata table
      · backup()          — timestamped copy of the entire vault
    """

    def __init__(self, vault_dir: str = "vault") -> None:
        base_dir = Path(__file__).resolve().parent
        
        v_path = Path(vault_dir)
        if not v_path.is_absolute():
            v_path = base_dir / v_path

        self.vault     = v_path
        self.priv_path = self.vault / "private_key.pem"
        self.pub_path  = self.vault / "public_key.pem"
        self.meta_path = self.vault / "key_meta.json"
        self.vault.mkdir(parents=True, exist_ok=True)

    # ── Generation ────────────────────────────────────────────────────────
    def generate(
        self,
        key_size:  int            = 4096,
        password:  Optional[bytes] = None,
        overwrite: bool            = False,
    ) -> None:
        """
        Generate and persist an RSA key pair.

        Args:
            key_size:  Bit length — must be in VALID_KEY_SIZES.
            password:  Optional passphrase to encrypt the private key at rest.
            overwrite: Allow replacing an existing key pair.

        Raises:
            InvalidInputError: key_size not in VALID_KEY_SIZES.
            FileExistsError:   Keys exist and overwrite=False.
        """
        if key_size not in VALID_KEY_SIZES:
            raise InvalidInputError(
                f"Key size must be one of {VALID_KEY_SIZES}, got {key_size}."
            )
        if self.priv_path.exists() and not overwrite:
            raise FileExistsError(
                "Key pair already exists. Pass --overwrite to regenerate."
            )

        Console.info(f"Generating RSA-{key_size} key pair …")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )

        enc_algo = (
            serialization.BestAvailableEncryption(password)
            if password
            else serialization.NoEncryption()
        )

        # Persist private key
        self.priv_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=enc_algo,
            )
        )
        # Persist public key
        self.pub_path.write_bytes(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

        # Restrict private-key permissions on POSIX (owner read/write only)
        if os.name != "nt":
            self.priv_path.chmod(0o600)

        self._write_metadata(key_size, password_protected=bool(password))
        Console.success(f"RSA-{key_size} key pair saved in '{self.vault}'.")
        if password:
            Console.info("Private key is encrypted with AES-256-CBC at rest.")

    def _write_metadata(self, key_size: int, password_protected: bool) -> None:
        """Persist JSON sidecar with key metadata for later inspection."""
        meta = {
            "version":            VERSION,
            "key_size":           key_size,
            "created_at":         datetime.now().isoformat(timespec="seconds"),
            "password_protected": password_protected,
            "fingerprint":        self.fingerprint(),
        }
        self.meta_path.write_text(json.dumps(meta, indent=2))

    # ── Loading ───────────────────────────────────────────────────────────
    def load_private(self, password: Optional[bytes] = None):
        """
        Deserialise the private key from PEM.

        Raises:
            KeyNotFoundError: PEM file is absent.
            KeyLoadError:     File present but unreadable (bad password or corrupt).
        """
        if not self.priv_path.exists():
            raise KeyNotFoundError(
                f"Private key not found at '{self.priv_path}'. Run 'genkeys' first."
            )
        try:
            return serialization.load_pem_private_key(
                self.priv_path.read_bytes(),
                password=password,
            )
        except (ValueError, TypeError) as exc:
            raise KeyLoadError(
                "Cannot load private key — wrong password or corrupt file."
            ) from exc

    def load_public(self):
        """
        Deserialise the public key from PEM.

        Raises:
            KeyNotFoundError: PEM file is absent.
        """
        if not self.pub_path.exists():
            raise KeyNotFoundError(
                f"Public key not found at '{self.pub_path}'. Run 'genkeys' first."
            )
        return serialization.load_pem_public_key(self.pub_path.read_bytes())

    # ── Key Info ──────────────────────────────────────────────────────────
    def show_info(self) -> None:
        """Print vault metadata, key parameters, and SHA-256 fingerprint."""
        Console.section("Key Information")
        if not self.priv_path.exists():
            Console.error("No keys found in vault.")
            return

        meta: dict = {}
        if self.meta_path.exists():
            meta = json.loads(self.meta_path.read_text())

        pub      = self.load_public()
        key_size = pub.key_size

        Console.kv("Vault",              str(self.vault.resolve()))
        Console.kv("Algorithm",          f"RSA-{key_size}")
        Console.kv("Public Exponent",    "65537  (F4)")
        Console.kv("Fingerprint",        self.fingerprint())
        Console.kv("Created At",         meta.get("created_at", "—"))
        Console.kv("Password Protected", str(meta.get("password_protected", "—")))
        Console.kv("Private Key",        str(self.priv_path))
        Console.kv("Public Key",         str(self.pub_path))
        Console.divider()

    def fingerprint(self) -> str:
        """Return a colon-grouped SHA-256 fingerprint of the DER-encoded public key."""
        if not self.pub_path.exists():
            return "N/A"
        pub = serialization.load_pem_public_key(self.pub_path.read_bytes())
        der = pub.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        digest = hashlib.sha256(der).hexdigest()
        return ":".join(digest[i:i + 4] for i in range(0, 32, 4))

    def keys_exist(self) -> bool:
        """Return True only when both key files are present."""
        return self.priv_path.exists() and self.pub_path.exists()

    # ── Backup ────────────────────────────────────────────────────────────
    def backup(self, dest: Optional[str] = None) -> Path:
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = Path(__file__).resolve().parent

        if dest:
            dest_dir = Path(dest)
            if not dest_dir.is_absolute():
                dest_dir = base_dir / dest_dir
        else:
            dest_dir = base_dir / f"vault_backup_{ts}"

        dest_dir.mkdir(parents=True, exist_ok=True)

        copied = 0
        for src in [self.priv_path, self.pub_path, self.meta_path]:
            if src.exists():
                (dest_dir / src.name).write_bytes(src.read_bytes())
                copied += 1

        Console.success(f"Vault backed up ({copied} files) → '{dest_dir.resolve()}'.")
        return dest_dir

# ─────────────────────────────────────────────────────────────────────────────
# § 5  CRYPTO ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class CryptoEngine:
    """
    All cryptographic operations:

    RSA-OAEP   — encrypt / decrypt small payloads (< key_size/8 − 66 bytes).
    Hybrid     — AES-256-GCM + RSA key-wrapping for unlimited file sizes.
    PSS        — digital signing and verification with SHA-256.

    Hybrid binary wire format (.enc):
    ┌─────────────┬─────────────┬──────────────┬────────┬───────┬────────────┐
    │ MAGIC (4 B) │ KEY_LEN(4B) │ ENC_AES_KEY  │ NONCE  │  TAG  │ CIPHERTEXT │
    │  "RSH3"     │ big-endian  │  (KEY_LEN B) │ (12 B) │ (16B) │  (rest)    │
    └─────────────┴─────────────┴──────────────┴────────┴───────┴────────────┘
    """

    def __init__(self, key_manager: KeyManager) -> None:
        self.km = key_manager

    # ── Padding Factories ─────────────────────────────────────────────────
    @staticmethod
    def _oaep() -> padding.OAEP:
        return padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )

    @staticmethod
    def _pss() -> padding.PSS:
        return padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        )

    # ── Input Helper ──────────────────────────────────────────────────────
    @staticmethod
    def _read_source(source: str) -> bytes:
        """Return file contents if *source* is a path, else UTF-8 encode it."""
        p = Path(source)
        return p.read_bytes() if p.is_file() else source.encode("utf-8")

    # ── RSA-OAEP Encrypt ──────────────────────────────────────────────────
    def encrypt(self, data: str, output_file: Optional[str] = None) -> bytes:
        """
        Encrypt *data* (text or file path) with RSA-OAEP.

        Enforces the RSA-OAEP plaintext size limit (key_size/8 − 66 bytes).
        For larger payloads use encrypt_file() (hybrid mode).

        Args:
            data:        Plaintext string or path to a small file.
            output_file: Optional path to save the hex ciphertext.

        Returns:
            Raw ciphertext bytes.
        """
        content = self._read_source(data)
        pub     = self.km.load_public()
        max_b   = pub.key_size // 8 - 66

        if len(content) > max_b:
            raise InvalidInputError(
                f"Payload ({len(content):,} B) exceeds RSA-OAEP limit ({max_b} B). "
                "Use 'encrypt-file' for large data."
            )

        ciphertext = pub.encrypt(content, self._oaep())
        hex_out    = ciphertext.hex()

        if output_file:
            Path(output_file).write_text(hex_out)
            Console.success(f"Ciphertext saved to '{output_file}'.")

        Console.section("RSA-OAEP Encryption")
        Console.result("Ciphertext (hex)", hex_out)
        Console.kv("Input size",  f"{len(content)} bytes")
        Console.kv("Output size", f"{len(ciphertext)} bytes")
        Console.divider()
        return ciphertext

    # ── RSA-OAEP Decrypt ──────────────────────────────────────────────────
    def decrypt(self, data: str, password: Optional[bytes] = None) -> bytes:
        """
        Decrypt an RSA-OAEP ciphertext.

        Args:
            data:     Hex string, or path to a file containing hex or raw bytes.
            password: Private key passphrase (if key is protected).

        Returns:
            Plaintext bytes.
        """
        p = Path(data)
        if p.is_file():
            raw = p.read_text().strip()
            try:
                ciphertext = bytes.fromhex(raw)
            except ValueError:
                ciphertext = p.read_bytes()          # fall back to raw binary
        else:
            try:
                ciphertext = bytes.fromhex(data.strip())
            except ValueError as exc:
                raise InvalidInputError(
                    "Invalid ciphertext: expected hex string or file path."
                ) from exc

        priv = self.km.load_private(password=password)

        try:
            plaintext = priv.decrypt(ciphertext, self._oaep())
        except ValueError as exc:
            raise DecryptionError(
                f"Decryption failed — wrong key or corrupt ciphertext. ({exc})"
            ) from exc

        Console.section("RSA-OAEP Decryption")
        Console.result("Plaintext", plaintext.decode("utf-8", errors="replace"), chunk=120)
        Console.kv("Output size", f"{len(plaintext)} bytes")
        Console.divider()
        return plaintext

    # ── Hybrid Encrypt (unlimited size) ───────────────────────────────────
    def encrypt_file(
        self,
        source:      str,
        output_file: Optional[str] = None,
    ) -> bytes:
        """
        Encrypt any file using AES-256-GCM with RSA-OAEP key wrapping.

        Steps:
          1. Generate an ephemeral 32-byte AES key and 12-byte GCM nonce.
          2. Encrypt plaintext with AES-256-GCM (provides auth tag automatically).
          3. Wrap the AES key with RSA-OAEP.
          4. Serialise the binary bundle (see wire format in class docstring).

        Args:
            source:      Path to the plaintext file (or a short string).
            output_file: Destination for the .enc bundle (auto-named if None).

        Returns:
            The full binary bundle as bytes.
        """
        content = self._read_source(source)
        pub     = self.km.load_public()

        # Step 1: ephemeral AES key & GCM nonce
        aes_key = os.urandom(AES_KEY_BYTES)
        nonce   = os.urandom(GCM_NONCE_BYTES)

        # Step 2: AES-256-GCM encrypt — output is ciphertext ‖ 16-byte tag
        ct_with_tag = AESGCM(aes_key).encrypt(nonce, content, None)
        ciphertext  = ct_with_tag[:-GCM_TAG_BYTES]
        tag         = ct_with_tag[-GCM_TAG_BYTES:]

        # Step 3: RSA-OAEP wrap the AES key
        enc_aes_key = pub.encrypt(aes_key, self._oaep())

        # Step 4: pack the binary bundle
        key_len = len(enc_aes_key).to_bytes(4, "big")
        bundle  = HYBRID_MAGIC + key_len + enc_aes_key + nonce + tag + ciphertext

        dest = Path(
            output_file
            or (Path(source).stem + ".enc" if Path(source).is_file() else "output.enc")
        )
        dest.write_bytes(bundle)

        Console.section("Hybrid Encryption  (AES-256-GCM + RSA-OAEP)")
        Console.success(f"Encrypted bundle → '{dest}'")
        Console.kv("Algorithm",   "AES-256-GCM + RSA-OAEP key-wrap")
        Console.kv("Input size",  f"{len(content):,} bytes")
        Console.kv("Output size", f"{len(bundle):,} bytes")
        Console.divider()
        return bundle

    # ── Hybrid Decrypt ────────────────────────────────────────────────────
    def decrypt_file(
        self,
        source:      str,
        output_file: Optional[str] = None,
        password:    Optional[bytes] = None,
    ) -> bytes:
        """
        Decrypt a hybrid-encrypted (.enc) bundle.

        Args:
            source:      Path to the .enc file.
            output_file: Destination for plaintext (auto-derived if None).
            password:    Private key passphrase (if key is protected).

        Returns:
            Plaintext bytes.
        """
        bundle = Path(source).read_bytes()

        if not bundle.startswith(HYBRID_MAGIC):
            raise InvalidInputError(
                "Not a hybrid-encrypted file (missing magic header). "
                "Use 'decrypt' for RSA-only hex ciphertext."
            )

        # Unpack binary bundle
        off         = len(HYBRID_MAGIC)
        key_len     = int.from_bytes(bundle[off:off + 4], "big");  off += 4
        enc_aes_key = bundle[off:off + key_len];                    off += key_len
        nonce       = bundle[off:off + GCM_NONCE_BYTES];           off += GCM_NONCE_BYTES
        tag         = bundle[off:off + GCM_TAG_BYTES];             off += GCM_TAG_BYTES
        ciphertext  = bundle[off:]

        # Unwrap AES key with RSA-OAEP
        priv = self.km.load_private(password=password)
        try:
            aes_key = priv.decrypt(enc_aes_key, self._oaep())
        except ValueError as exc:
            raise DecryptionError(
                f"AES key unwrap failed — wrong private key or corrupt bundle. ({exc})"
            ) from exc

        # AES-256-GCM decrypt; InvalidTag is raised on tampering
        try:
            plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext + tag, None)
        except Exception as exc:
            raise DecryptionError(
                f"AES-GCM decryption failed — data may be corrupt or tampered. ({exc})"
            ) from exc

        dest = Path(output_file) if output_file else Path(source).with_suffix("")
        dest.write_bytes(plaintext)

        Console.section("Hybrid Decryption  (AES-256-GCM + RSA-OAEP)")
        Console.success(f"Decrypted file → '{dest}'")
        Console.kv("Output size", f"{len(plaintext):,} bytes")
        Console.divider()
        return plaintext

    # ── Sign ──────────────────────────────────────────────────────────────
    def sign(
        self,
        data:        str,
        output_file: Optional[str] = None,
        password:    Optional[bytes] = None,
    ) -> bytes:
        """
        Sign *data* with RSA-PSS + SHA-256.

        Args:
            data:        Plaintext string or path to the file to sign.
            output_file: Optional path to save the hex signature.
            password:    Private key passphrase (if key is protected).

        Returns:
            Raw signature bytes.
        """
        content   = self._read_source(data)
        priv      = self.km.load_private(password=password)
        signature = priv.sign(content, self._pss(), hashes.SHA256())
        hex_sig   = signature.hex()

        if output_file:
            Path(output_file).write_text(hex_sig)
            Console.success(f"Signature saved to '{output_file}'.")

        Console.section("Digital Signature  (RSA-PSS + SHA-256)")
        Console.result("Signature (hex)", hex_sig)
        Console.kv("Algorithm", "RSA-PSS / SHA-256 / MGF1")
        Console.kv("Data size", f"{len(content)} bytes")
        Console.kv("Sig size",  f"{len(signature)} bytes")
        Console.divider()
        return signature

    # ── Verify ────────────────────────────────────────────────────────────
    def verify(self, data: str, sig_source: str) -> bool:
        """
        Verify an RSA-PSS signature.

        Args:
            data:       Original plaintext string or file path.
            sig_source: Hex string or path to a file containing the hex signature.

        Returns:
            True if the signature is valid, False otherwise.
        """
        content  = self._read_source(data)
        sig_path = Path(sig_source)
        raw_hex  = sig_path.read_text().strip() if sig_path.is_file() else sig_source.strip()

        try:
            sig_bytes = bytes.fromhex(raw_hex)
        except ValueError as exc:
            raise InvalidInputError(
                "Invalid signature — expected hex string or path to a .hex file."
            ) from exc

        pub = self.km.load_public()

        Console.section("Signature Verification")
        try:
            pub.verify(sig_bytes, content, self._pss(), hashes.SHA256())
            Console.success("Signature is VALID  ✓")
            Console.divider()
            return True
        except InvalidSignature:
            Console.error("Signature is INVALID  ✗")
            Console.divider()
            return False


# ─────────────────────────────────────────────────────────────────────────────
# § 6  INTERACTIVE MENU
# ─────────────────────────────────────────────────────────────────────────────

class InteractiveMenu:
    """
    Terminal-based TUI that exposes every CryptoEngine / KeyManager
    operation through a numbered menu — no command-line arguments required.
    """

    MENU_OPTIONS: List[Tuple[str, str]] = [
        ("genkeys",      "Generate new RSA key pair"),
        ("keyinfo",      "Show key information & fingerprint"),
        ("encrypt",      "Encrypt text  (RSA-OAEP, small payloads)"),
        ("decrypt",      "Decrypt ciphertext  (RSA-OAEP)"),
        ("encrypt-file", "Encrypt file  (Hybrid AES-256-GCM + RSA, any size)"),
        ("decrypt-file", "Decrypt encrypted file  (.enc)"),
        ("sign",         "Sign data with private key  (RSA-PSS)"),
        ("verify",       "Verify digital signature"),
        ("backup",       "Backup key vault"),
    ]

    def __init__(self, engine: CryptoEngine, km: KeyManager) -> None:
        self.engine = engine
        self.km     = km

    def run(self) -> None:
        Console.banner()

        while True:
            Console.section("Main Menu")
            choice = Console.menu(self.MENU_OPTIONS)

            if choice == "0":
                Console.info("Goodbye!")
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.MENU_OPTIONS):
                    self._dispatch(self.MENU_OPTIONS[idx][0])
                else:
                    Console.error("Option out of range.")
            except ValueError:
                Console.error("Please enter a number.")
            except KeyboardInterrupt:
                print()
                Console.info("Cancelled.")
            except RSASystemError as exc:
                Console.error(str(exc))
            except Exception as exc:
                Console.error(f"Unexpected error: {exc}")
                logging.exception("Unhandled exception in interactive menu")

    # ── Dispatcher ────────────────────────────────────────────────────────
    def _dispatch(self, cmd: str) -> None:
        handlers = {
            "genkeys":      self._do_genkeys,
            "keyinfo":      self.km.show_info,
            "encrypt":      self._do_encrypt,
            "decrypt":      self._do_decrypt,
            "encrypt-file": self._do_encrypt_file,
            "decrypt-file": self._do_decrypt_file,
            "sign":         self._do_sign,
            "verify":       self._do_verify,
            "backup":       self._do_backup,
        }
        handlers[cmd]()

    # ── Sub-handlers ──────────────────────────────────────────────────────
    def _do_genkeys(self) -> None:
        if self.km.keys_exist() and not Console.confirm("Keys already exist. Overwrite?"):
            Console.info("Cancelled.")
            return
        try:
            size = int(Console.ask("Key size [2048 / 3072 / 4096]", default="4096"))
        except ValueError:
            size = 4096
        password = (
            self._prompt_password(confirm=True)
            if Console.confirm("Protect private key with password?")
            else None
        )
        self.km.generate(key_size=size, password=password, overwrite=True)

    def _do_encrypt(self) -> None:
        data = Console.ask("Text or file path to encrypt")
        out  = Console.ask("Save ciphertext to file (blank = skip)") or None
        self.engine.encrypt(data, output_file=out)

    def _do_decrypt(self) -> None:
        data = Console.ask("Ciphertext hex or file path")
        pw   = self._maybe_password()
        self.engine.decrypt(data, password=pw)

    def _do_encrypt_file(self) -> None:
        src = Console.ask("Source file path")
        out = Console.ask("Output .enc path (blank = auto)") or None
        self.engine.encrypt_file(src, output_file=out)

    def _do_decrypt_file(self) -> None:
        src = Console.ask("Encrypted .enc file path")
        out = Console.ask("Output file path (blank = auto)") or None
        pw  = self._maybe_password()
        self.engine.decrypt_file(src, output_file=out, password=pw)

    def _do_sign(self) -> None:
        data = Console.ask("Text or file path to sign")
        out  = Console.ask("Save signature to file (blank = skip)") or None
        pw   = self._maybe_password()
        self.engine.sign(data, output_file=out, password=pw)

    def _do_verify(self) -> None:
        data    = Console.ask("Original text or file path")
        sig_src = Console.ask("Signature hex or .hex file path")
        self.engine.verify(data, sig_src)

    def _do_backup(self) -> None:
        dest = Console.ask("Backup destination (blank = auto)") or None
        self.km.backup(dest=dest)

    # ── Password Helpers ──────────────────────────────────────────────────
    @staticmethod
    def _prompt_password(confirm: bool = False) -> bytes:
        pw = getpass.getpass("  Password: ")
        if confirm:
            pw2 = getpass.getpass("  Confirm:  ")
            if pw != pw2:
                raise InvalidInputError("Passwords do not match.")
        return pw.encode()

    def _maybe_password(self) -> Optional[bytes]:
        """Return passphrase bytes only if the vault metadata marks keys as protected."""
        if self.km.meta_path.exists():
            meta = json.loads(self.km.meta_path.read_text())
            if meta.get("password_protected"):
                return self._prompt_password()
        return None


# ─────────────────────────────────────────────────────────────────────────────
# § 7  CLI  (argparse)
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rsa_system",
        description=f"RSA Cryptographic System v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(f"""\
            Examples
            ────────
              Generate keys (4096-bit, password-protected):
                python rsa_system.py genkeys --size 4096 --password

              Encrypt a short message and save ciphertext:
                python rsa_system.py encrypt "Secret" --out cipher.hex

              Encrypt a large file (hybrid AES+RSA):
                python rsa_system.py encrypt-file report.pdf

              Decrypt hybrid-encrypted file:
                python rsa_system.py decrypt-file report.enc --out report.pdf

              Sign a file and save the signature:
                python rsa_system.py sign document.txt --out document.sig

              Verify a signature:
                python rsa_system.py verify document.txt document.sig

              Show key fingerprint and metadata:
                python rsa_system.py keyinfo

              Launch interactive terminal menu:
                python rsa_system.py menu
        """),
    )
    parser.add_argument(
        "--vault", default="vault", metavar="DIR",
        help="Key vault directory (default: vault)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    sub = parser.add_subparsers(dest="cmd")

    # menu ─────────────────────────────────────────────────────────────────
    sub.add_parser("menu", help="Launch interactive terminal menu")

    # genkeys ──────────────────────────────────────────────────────────────
    gk = sub.add_parser("genkeys", help="Generate RSA key pair")
    gk.add_argument("--size",      type=int, default=4096,
                    choices=list(VALID_KEY_SIZES),
                    help="Key size in bits (default: 4096)")
    gk.add_argument("--password",  action="store_true",
                    help="Protect private key with a passphrase")
    gk.add_argument("--overwrite", action="store_true",
                    help="Overwrite any existing keys")

    # keyinfo ──────────────────────────────────────────────────────────────
    sub.add_parser("keyinfo", help="Display key metadata and SHA-256 fingerprint")

    # backup ───────────────────────────────────────────────────────────────
    bk = sub.add_parser("backup", help="Copy vault to a timestamped backup directory")
    bk.add_argument("--dest", metavar="DIR", default=None,
                    help="Backup destination (auto-named if omitted)")

    # encrypt ──────────────────────────────────────────────────────────────
    en = sub.add_parser("encrypt", help="RSA-OAEP encrypt text or a small file")
    en.add_argument("data",  help="Plaintext string or file path")
    en.add_argument("--out", metavar="FILE", default=None,
                    help="Save hex ciphertext to this file")

    # decrypt ──────────────────────────────────────────────────────────────
    de = sub.add_parser("decrypt", help="RSA-OAEP decrypt a hex ciphertext")
    de.add_argument("data",       help="Hex string or file path")
    de.add_argument("--password", action="store_true",
                    help="Prompt for private key passphrase")

    # encrypt-file  (hybrid) ───────────────────────────────────────────────
    ef = sub.add_parser("encrypt-file",
                        help="Hybrid-encrypt any file (AES-256-GCM + RSA, unlimited size)")
    ef.add_argument("source",  help="Source file path")
    ef.add_argument("--out",   metavar="FILE", default=None,
                    help="Output .enc path (auto-named if omitted)")
    # decrypt-file  (hybrid) ───────────────────────────────────────────────
    df = sub.add_parser("decrypt-file", help="Decrypt a hybrid-encrypted .enc file")
    df.add_argument("source",      help="Path to the .enc file")
    df.add_argument("--out",       metavar="FILE", default=None,
                    help="Output file path (auto-derived if omitted)")
    df.add_argument("--password",  action="store_true",
                    help="Prompt for private key passphrase")

    # sign ─────────────────────────────────────────────────────────────────
    sg = sub.add_parser("sign", help="Sign data with RSA-PSS + SHA-256")
    sg.add_argument("data",        help="Plaintext string or file path")
    sg.add_argument("--out",       metavar="FILE", default=None,
                    help="Save hex signature to this file")
    sg.add_argument("--password",  action="store_true",
                    help="Prompt for private key passphrase")

    # verify ───────────────────────────────────────────────────────────────
    vr = sub.add_parser("verify", help="Verify an RSA-PSS signature")
    vr.add_argument("data", help="Original text or file path")
    vr.add_argument("sig",  help="Signature hex string or .hex file path")

    return parser


def _prompt_password(confirm: bool = False) -> bytes:
    """Securely read a passphrase from the terminal without echoing it."""
    pw = getpass.getpass("Password: ")
    if confirm:
        pw2 = getpass.getpass("Confirm:  ")
        if pw != pw2:
            Console.error("Passwords do not match.")
            sys.exit(1)
    return pw.encode()


# ─────────────────────────────────────────────────────────────────────────────
# § 8  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = _build_parser()
    args   = parser.parse_args()

    # Default to interactive menu when no sub-command is supplied
    if not args.cmd:
        args.cmd = "menu"

    km     = KeyManager(vault_dir=args.vault)
    engine = CryptoEngine(key_manager=km)

    # Auto-generate keys for commands that require them (except genkeys / menu)
    _no_keys_needed = {"genkeys", "menu", "keyinfo"}
    if args.cmd not in _no_keys_needed and not km.keys_exist():
        Console.warning("No keys found — generating RSA-4096 key pair automatically.")
        km.generate(key_size=4096)

    exit_code = 0

    try:
        if args.cmd == "menu":
            InteractiveMenu(engine=engine, km=km).run()

        elif args.cmd == "genkeys":
            pw = _prompt_password(confirm=True) if args.password else None
            km.generate(key_size=args.size, password=pw, overwrite=args.overwrite)

        elif args.cmd == "keyinfo":
            km.show_info()

        elif args.cmd == "backup":
            km.backup(dest=args.dest)

        elif args.cmd == "encrypt":
            engine.encrypt(args.data, output_file=args.out)

        elif args.cmd == "decrypt":
            pw = _prompt_password() if args.password else None
            engine.decrypt(args.data, password=pw)

        elif args.cmd == "encrypt-file":
            engine.encrypt_file(args.source, output_file=args.out)

        elif args.cmd == "decrypt-file":
            pw = _prompt_password() if args.password else None
            engine.decrypt_file(args.source, output_file=args.out, password=pw)

        elif args.cmd == "sign":
            pw = _prompt_password() if args.password else None
            engine.sign(args.data, output_file=args.out, password=pw)

        elif args.cmd == "verify":
            valid     = engine.verify(args.data, args.sig)
            exit_code = 0 if valid else 1

    except KeyboardInterrupt:
        print()
        Console.info("Operation cancelled by user.")
        sys.exit(130)

    # User / input errors — do not dump a traceback
    except (KeyNotFoundError, KeyLoadError, InvalidInputError, FileExistsError) as exc:
        Console.error(str(exc))
        sys.exit(2)

    # Cryptographic failures
    except (DecryptionError, SignatureVerificationError) as exc:
        Console.error(str(exc))
        sys.exit(3)

    # Catch-all: log and exit with a distinct code
    except Exception as exc:
        Console.error(f"Unexpected error: {exc}")
        logging.exception("Unhandled exception")
        sys.exit(99)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
