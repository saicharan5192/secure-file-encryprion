"""Cryptographic implementation for Secure File Encryption System.

Encrypted file format:
    MAGIC (8 bytes) + HEADER_LENGTH (4-byte big-endian integer)
    + HEADER_JSON (UTF-8) + AES-GCM ciphertext+authentication-tag

The header contains no password or derived key. It contains the algorithm,
version, salt, nonce, original filename, original SHA-256 and PBKDF2 settings.
The exact header bytes are supplied to AES-GCM as authenticated additional data
(AAD), so metadata tampering is detected.
"""

import base64
import hashlib
import json
import os
import struct
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import KEY_SIZE, NONCE_SIZE, PBKDF2_ITERATIONS, SALT_SIZE

MAGIC = b"SFEv1.00"
FORMAT_VERSION = 1
MAX_HEADER_SIZE = 16 * 1024
MAX_FILENAME_LENGTH = 255


class CryptoError(Exception):
    """Raised for expected encryption/decryption failures."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    if not password:
        raise CryptoError("Password cannot be empty.")
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def _build_header(filename: str, salt: bytes, nonce: bytes, original_hash: str) -> bytes:
    safe_name = Path(filename).name
    if not safe_name or len(safe_name) > MAX_FILENAME_LENGTH:
        raise CryptoError("Invalid original filename.")

    header = {
        "version": FORMAT_VERSION,
        "algorithm": "AES-256-GCM",
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": _b64(salt),
        "nonce": _b64(nonce),
        "filename": safe_name,
        "sha256": original_hash,
    }
    return json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")


def encrypt_bytes(data: bytes, filename: str, password: str) -> bytes:
    if not password:
        raise CryptoError("Password cannot be empty.")

    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    original_hash = sha256_bytes(data)
    header = _build_header(filename, salt, nonce, original_hash)

    if len(header) > MAX_HEADER_SIZE:
        raise CryptoError("Encryption metadata is too large.")

    ciphertext_and_tag = AESGCM(key).encrypt(nonce, data, header)
    return MAGIC + struct.pack(">I", len(header)) + header + ciphertext_and_tag


def decrypt_bytes(blob: bytes, password: str) -> tuple[bytes, dict]:
    if not password:
        raise CryptoError("Password cannot be empty.")
    if len(blob) < len(MAGIC) + 4:
        raise CryptoError("Invalid or corrupted encrypted file.")
    if blob[:len(MAGIC)] != MAGIC:
        raise CryptoError("Unsupported encrypted file format.")

    offset = len(MAGIC)
    header_len = struct.unpack(">I", blob[offset:offset + 4])[0]
    offset += 4

    if header_len <= 0 or header_len > MAX_HEADER_SIZE:
        raise CryptoError("Invalid encrypted metadata.")
    if len(blob) < offset + header_len + 16:
        raise CryptoError("Encrypted file is incomplete.")

    header_bytes = blob[offset:offset + header_len]
    ciphertext_and_tag = blob[offset + header_len:]

    try:
        header = json.loads(header_bytes.decode("utf-8"))
        if header.get("version") != FORMAT_VERSION:
            raise CryptoError("Unsupported encrypted file version.")
        if header.get("algorithm") != "AES-256-GCM":
            raise CryptoError("Unsupported encryption algorithm.")
        if header.get("kdf") != "PBKDF2-HMAC-SHA256":
            raise CryptoError("Unsupported key derivation method.")

        salt = _unb64(header["salt"])
        nonce = _unb64(header["nonce"])
        iterations = int(header["iterations"])
        filename = Path(str(header["filename"])).name
        expected_hash = str(header["sha256"])

        if len(salt) != SALT_SIZE or len(nonce) != NONCE_SIZE:
            raise CryptoError("Invalid salt or nonce.")
        if not (100_000 <= iterations <= 5_000_000):
            raise CryptoError("Invalid PBKDF2 iteration count.")
        if not filename or len(filename) > MAX_FILENAME_LENGTH:
            raise CryptoError("Invalid original filename.")
        if len(expected_hash) != 64:
            raise CryptoError("Invalid SHA-256 metadata.")

        key = derive_key(password, salt, iterations)
        plaintext = AESGCM(key).decrypt(nonce, ciphertext_and_tag, header_bytes)
    except CryptoError:
        raise
    except Exception as exc:
        raise CryptoError("Incorrect key/password or corrupted encrypted file.") from exc

    recovered_hash = sha256_bytes(plaintext)
    if recovered_hash != expected_hash:
        raise CryptoError("File verification failed: SHA-256 mismatch.")

    return plaintext, header
