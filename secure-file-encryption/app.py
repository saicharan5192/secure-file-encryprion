import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from config import DECRYPTED_DIR, ENCRYPTED_DIR, HISTORY_FILE, MAX_UPLOAD_SIZE, UPLOAD_DIR
from crypto_utils import CryptoError, decrypt_bytes, encrypt_bytes, sha256_bytes
from file_utils import (
    output_decrypted_name,
    output_encrypted_name,
    unique_filename,
    validate_upload_name,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
app.config["JSON_SORT_KEYS"] = False


def now_string() -> str:
    return datetime.now().astimezone().strftime("%d-%m-%Y %H:%M:%S")


def read_history():
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def write_history(entry: dict):
    history = read_history()
    history.insert(0, entry)
    HISTORY_FILE.write_text(json.dumps(history[:100], indent=2), encoding="utf-8")


def cleanup_file(path: Path):
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return jsonify({"success": False, "message": "File is too large. Maximum upload size is 50 MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/encrypt")
def encrypt_page():
    return render_template("encrypt.html")


@app.route("/decrypt")
def decrypt_page():
    return render_template("decrypt.html")


@app.route("/history")
def history_page():
    return render_template("history.html", history=read_history())


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.get("/api/health")
def health():
    return jsonify({"success": True, "status": "healthy", "service": "Secure File Encryption System"})


@app.post("/api/encrypt")
def api_encrypt():
    uploaded = request.files.get("file")
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if uploaded is None:
        return jsonify({"success": False, "message": "No file selected."}), 400
    if not password:
        return jsonify({"success": False, "message": "Password cannot be empty."}), 400
    if password != confirm:
        return jsonify({"success": False, "message": "Password and confirmation do not match."}), 400

    try:
        safe_name = validate_upload_name(uploaded.filename, encrypted=False)
        data = uploaded.read()
        if not data:
            return jsonify({"success": False, "message": "The selected file is empty."}), 400

        # Keep a temporary copy only while processing; never log the password.
        temp_name = unique_filename(safe_name)
        temp_path = UPLOAD_DIR / temp_name
        temp_path.write_bytes(data)

        encrypted_blob = encrypt_bytes(data, safe_name, password)
        encrypted_name = output_encrypted_name(safe_name)
        stored_name = unique_filename(encrypted_name)
        encrypted_path = ENCRYPTED_DIR / stored_name
        encrypted_path.write_bytes(encrypted_blob)

        original_hash = sha256_bytes(data)
        download_name = stored_name

        cleanup_file(temp_path)

        write_history({
            "file_name": safe_name,
            "algorithm": "AES-256-GCM",
            "operation": "Encryption",
            "date_time": now_string(),
            "status": "SUCCESS",
        })

        return jsonify({
            "success": True,
            "message": "File encrypted successfully.",
            "input_file": safe_name,
            "algorithm": "AES-256-GCM",
            "status": "SUCCESS",
            "encrypted_file": encrypted_name,
            "download_url": url_for("download_file", kind="encrypted", filename=download_name),
            "sha256": original_hash,
        })
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except CryptoError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except OSError:
        return jsonify({"success": False, "message": "Could not safely process the uploaded file."}), 500
    except Exception:
        return jsonify({"success": False, "message": "Encryption failed due to an unexpected server error."}), 500


@app.post("/api/decrypt")
def api_decrypt():
    uploaded = request.files.get("file")
    password = request.form.get("password", "")

    if uploaded is None:
        return jsonify({"success": False, "message": "No encrypted file selected."}), 400
    if not password:
        return jsonify({"success": False, "message": "Password cannot be empty."}), 400

    try:
        safe_name = validate_upload_name(uploaded.filename, encrypted=True)
        blob = uploaded.read()
        if not blob:
            return jsonify({"success": False, "message": "The encrypted file is empty."}), 400

        plaintext, metadata = decrypt_bytes(blob, password)
        recovered_name = output_decrypted_name(metadata["filename"])
        stored_name = unique_filename(recovered_name)
        output_path = DECRYPTED_DIR / stored_name
        output_path.write_bytes(plaintext)

        recovered_hash = sha256_bytes(plaintext)
        verification = "MATCH" if recovered_hash == metadata["sha256"] else "MISMATCH"

        write_history({
            "file_name": metadata["filename"],
            "algorithm": "AES-256-GCM",
            "operation": "Decryption",
            "date_time": now_string(),
            "status": "SUCCESS" if verification == "MATCH" else "FAILED",
        })

        return jsonify({
            "success": True,
            "message": "File decrypted and verified successfully.",
            "status": "SUCCESS",
            "recovered_file": metadata["filename"],
            "download_url": url_for("download_file", kind="decrypted", filename=stored_name),
            "original_hash": metadata["sha256"],
            "recovered_hash": recovered_hash,
            "verification": verification,
        })
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except CryptoError as exc:
        write_history({
            "file_name": getattr(uploaded, "filename", "unknown"),
            "algorithm": "AES-256-GCM",
            "operation": "Decryption",
            "date_time": now_string(),
            "status": "FAILED",
        })
        return jsonify({
            "success": False,
            "status": "FAILED",
            "message": "Incorrect key/password or corrupted encrypted file. Decryption unsuccessful.",
        }), 400
    except OSError:
        return jsonify({"success": False, "message": "Could not save the recovered file."}), 500
    except Exception:
        return jsonify({"success": False, "message": "Decryption failed due to an unexpected server error."}), 500


@app.get("/api/download/<kind>/<filename>")
def download_file(kind, filename):
    # send_from_directory safely resolves the requested filename relative to the directory.
    if kind == "encrypted":
        directory = ENCRYPTED_DIR
    elif kind == "decrypted":
        directory = DECRYPTED_DIR
    else:
        return jsonify({"success": False, "message": "Invalid download type."}), 400

    safe_requested = Path(filename).name
    if safe_requested != filename or not safe_requested:
        return jsonify({"success": False, "message": "Invalid filename."}), 400

    if not (directory / safe_requested).is_file():
        return jsonify({"success": False, "message": "File not found."}), 404

    return send_from_directory(directory, safe_requested, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
