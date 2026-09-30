from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS


def validate_upload_name(filename: str, encrypted: bool = False) -> str:
    if not filename or not filename.strip():
        raise ValueError("No file selected.")

    safe = secure_filename(filename)
    if not safe:
        raise ValueError("Invalid filename.")

    if encrypted:
        if not safe.lower().endswith(".enc"):
            raise ValueError("Please upload an encrypted .enc file.")
    else:
        suffix = Path(safe).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise ValueError(f"Unsupported file type. Allowed types include: {allowed}")

    return safe


def unique_filename(original: str) -> str:
    safe = secure_filename(original)
    return f"{uuid4().hex}_{safe}"


def output_encrypted_name(original: str) -> str:
    safe = secure_filename(original)
    return f"{Path(safe).stem}.enc"


def output_decrypted_name(original: str) -> str:
    safe = secure_filename(original)
    if safe.lower().endswith(".enc"):
        safe = safe[:-4]
    return safe or "recovered_file"
