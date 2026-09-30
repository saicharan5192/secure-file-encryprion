from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ENCRYPTED_DIR = BASE_DIR / "encrypted"
DECRYPTED_DIR = BASE_DIR / "decrypted"
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256

ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".jpg", ".jpeg", ".png", ".docx", ".xlsx", ".zip",
    ".csv", ".pptx", ".mp3", ".mp4", ".bin"
}

for directory in (UPLOAD_DIR, ENCRYPTED_DIR, DECRYPTED_DIR, DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)

if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")
