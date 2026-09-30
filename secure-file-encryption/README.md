# Secure File Encryption and Decryption System Using Symmetric Cryptography

A complete B.Tech Cyber Security / Cryptography and Network Security project built with **Python + Flask + HTML/CSS/JavaScript**.

## 1. Problem Statement

Confidential files can be exposed when stored or transferred without adequate protection. This project provides a web application that encrypts files using symmetric cryptography and allows the same files to be recovered only when the correct password is supplied.

## 2. Objectives

- Protect confidential files from unauthorized access.
- Demonstrate symmetric-key cryptography.
- Use AES-256-GCM for authenticated encryption.
- Derive an AES key from a user password using PBKDF2-HMAC-SHA256.
- Generate a random salt and nonce for every encryption.
- Verify recovered files using SHA-256.
- Demonstrate incorrect-password and tampering detection.
- Support binary files such as PDF, images, DOCX, XLSX and ZIP.

## 3. Features

- Modern responsive cybersecurity dashboard.
- Drag-and-drop file upload.
- AES-256-GCM encryption and decryption.
- PBKDF2-HMAC-SHA256 password-based key derivation.
- Random 128-bit salt and 96-bit GCM nonce.
- Authentication tag through AES-GCM.
- SHA-256 original/recovered file verification.
- Encrypted `.enc` file format with authenticated metadata.
- Encryption/decryption history without passwords or keys.
- Safe filenames and path-traversal protection.
- 50 MB upload limit.
- Friendly error handling.
- Automated cryptographic tests.

## 4. Technologies Used

- Python 3.10+
- Flask
- cryptography
- HTML5
- CSS3
- JavaScript
- pytest

## 5. Cryptography Used

### AES-256-GCM

AES is a symmetric block cipher. AES-256 uses a 256-bit encryption key. GCM is an authenticated-encryption mode, so it provides confidentiality and an authentication tag for detecting incorrect keys or modified encrypted data.

### PBKDF2-HMAC-SHA256

The user enters a password rather than a raw 256-bit key. PBKDF2 derives the AES key from that password using a random salt and repeated HMAC-SHA256 operations.

### SHA-256

The application hashes the original file during encryption and the recovered file during decryption. Matching hashes indicate that the recovered bytes are identical to the original bytes.

## 6. System Architecture

```text
User
  |
  v
Web Interface
  |
  v
Flask Backend
  |
  v
File Validation
  |
  v
PBKDF2-HMAC-SHA256
  |
  v
AES-256-GCM Encryption / Decryption
  |
  v
Encrypted / Recovered File
  |
  v
SHA-256 Verification
  |
  v
User Download
```

## 7. Encryption Workflow

```text
Select File
    |
Enter Password + Confirmation
    |
Generate Random Salt + Nonce
    |
PBKDF2-HMAC-SHA256
    |
Derived 256-bit AES Key
    |
AES-256-GCM Encryption
    |
Authentication Tag
    |
Encrypted .enc File
    |
Download
```

## 8. Decryption Workflow

```text
Select .enc File
    |
Enter Password
    |
Read Salt + Nonce + Metadata
    |
PBKDF2-HMAC-SHA256
    |
AES-256-GCM Decryption
    |
Authentication Verification
    |
Recovered File
    |
SHA-256 Verification
```

If the password is wrong or the encrypted file is modified, AES-GCM authentication fails and no valid recovered file is produced.

## 9. Key Management

```text
User Password
      |
      v
PBKDF2-HMAC-SHA256
      |
      v
Derived AES-256 Key
      |
      v
AES-256-GCM
      |
      v
Encrypted File
```

- Password is never stored.
- Derived AES key is never stored.
- Salt is random for every encryption and is stored as non-secret metadata.
- GCM nonce is random for every encryption.
- GCM authentication tag is stored as part of the ciphertext output.

## 10. Encrypted File Format

The `.enc` format is:

```text
MAGIC
HEADER_LENGTH
HEADER_JSON
AES-GCM CIPHERTEXT + AUTHENTICATION TAG
```

The header contains:

- Version
- Algorithm identifier
- KDF identifier
- PBKDF2 iteration count
- Salt
- Nonce
- Original filename
- Original SHA-256

The password and derived encryption key are never stored.

The header itself is authenticated by AES-GCM as additional authenticated data (AAD), so changing metadata causes decryption failure.

## 11. Backend API

### `POST /api/encrypt`

Multipart form fields:

- `file`
- `password`
- `confirm_password`

### `POST /api/decrypt`

Multipart form fields:

- `file`
- `password`

### `GET /api/download/<kind>/<filename>`

Downloads a previously generated encrypted or recovered file.

### `GET /api/health`

Returns a health status JSON response.

## 12. Installation

### Windows PowerShell

```powershell
cd secure-file-encryption
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
cd secure-file-encryption
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 13. How to Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

For development, the application listens only on localhost.

## 14. How to Encrypt a File

1. Open **Encrypt**.
2. Drag a supported file into the upload box.
3. Enter a password.
4. Confirm the password.
5. Click **Encrypt File**.
6. The application generates a random salt and nonce.
7. PBKDF2 derives the AES-256 key.
8. AES-256-GCM encrypts the binary file.
9. Download the `.enc` file.
10. The original file is not changed.

## 15. How to Decrypt a File

1. Open **Decrypt**.
2. Select the `.enc` file.
3. Enter the same password used during encryption.
4. Click **Decrypt File**.
5. AES-GCM authenticates and decrypts the file.
6. SHA-256 is calculated for the recovered file.
7. The recovered hash is compared with the original stored hash.
8. Download the recovered file.

## 16. Incorrect Password Demonstration

For a viva/demo:

1. Encrypt `sample.txt` with password `Correct123!`.
2. Go to Decrypt.
3. Select the generated `.enc`.
4. Enter `Wrong123!`.
5. Click Decrypt.
6. The application displays:

> Incorrect key/password or corrupted encrypted file. Decryption unsuccessful.

No valid recovered file is generated.

## 17. SHA-256 Verification Demonstration

1. Encrypt a file.
2. Note the displayed original SHA-256.
3. Decrypt with the correct password.
4. The system calculates the recovered file SHA-256.
5. Both hashes are displayed.
6. `MATCH` means the recovered bytes are byte-for-byte identical to the original file.

A hash comparison is a verification mechanism; it is not encryption.

## 18. Supported File Types

The demonstration configuration accepts:

- `.txt`
- `.pdf`
- `.jpg`
- `.jpeg`
- `.png`
- `.docx`
- `.xlsx`
- `.zip`
- `.csv`
- `.pptx`
- `.mp3`
- `.mp4`
- `.bin`

Files are processed in binary mode.

## 19. Testing

Run:

```bash
pytest -q
```

Test cases include:

1. Encrypt and decrypt a text file.
2. Wrong password must fail.
3. Modified ciphertext must fail authentication.
4. Binary data must round-trip exactly.
5. Modified authenticated metadata must fail.

For manual tests, also try PDF and image files.

## 20. Security Considerations

Implemented:

- AES-256-GCM
- PBKDF2-HMAC-SHA256
- Random salt
- Random GCM nonce
- GCM authentication tag
- SHA-256 verification
- Password confirmation
- Maximum upload size
- Secure filenames
- Path-traversal protection
- Temporary upload cleanup
- No password logging
- No key logging

### Important deployment note

This project is designed as an academic local demonstration. For public deployment, additional controls should be added, such as HTTPS, CSRF protection, authenticated user accounts, rate limiting, stronger storage isolation, background cleanup, audit logging, and secure production configuration.

## 21. Limitations

- Password recovery is intentionally not provided.
- If the user loses the password, the encrypted file cannot be decrypted.
- Files are temporarily stored on the server for this academic application.
- The history is local JSON storage rather than a production database.
- No user-account system is included.
- The app is intended for a controlled academic demonstration, not a hardened public file-hosting service.

## 22. Future Enhancements

- User authentication and role-based access.
- HTTPS and CSRF protection.
- Database-backed history.
- Automatic expiry and cleanup of generated files.
- Per-user encrypted storage.
- Cloud object storage with access controls.
- Download audit logs.
- Configurable encryption policies.
- Optional hardware-backed key management for production deployments.

## 23. Folder Structure

```text
secure-file-encryption/
│
├── app.py
├── requirements.txt
├── README.md
├── crypto_utils.py
├── file_utils.py
├── config.py
│
├── templates/
│   ├── index.html
│   ├── encrypt.html
│   ├── decrypt.html
│   ├── history.html
│   └── about.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── uploads/
├── encrypted/
├── decrypted/
├── data/
│   └── history.json
│
└── tests/
    └── test_crypto.py
```

## 24. Academic Viva Summary

**What is symmetric cryptography?**  
It uses the same secret key for encryption and decryption.

**Why AES?**  
AES is a standardized and efficient symmetric block cipher. This project uses AES-256-GCM.

**What is a block cipher?**  
It processes data in fixed-size blocks using a secret key.

**What is a stream cipher?**  
It encrypts data as a stream of bits or bytes. RC4 is a historical example.

**Why is a salt used?**  
A random salt makes password-derived keys different for different encryptions.

**Why is a nonce used?**  
AES-GCM requires a unique nonce for each encryption with the same key.

**What is PBKDF2?**  
A password-based key derivation function that makes password guessing more expensive.

**Why SHA-256?**  
It produces a digest that can be used to verify file integrity/equality.

**What happens with a wrong password?**  
AES-GCM authentication fails and the application rejects the data.

**Encryption vs hashing?**  
Encryption can be reversed with the correct key; hashing produces a one-way digest.

**AES vs DES?**  
AES is a modern standard; DES has a 56-bit effective key and is obsolete.

**Why not RC4?**  
RC4 has known weaknesses and is not recommended for modern secure applications.

**What is AES-GCM?**  
An authenticated encryption mode that provides confidentiality and an authentication tag.

## 25. Important Implementation Rules

This project uses real cryptography rather than fake encryption:

- It does not rename files as encryption.
- It does not use Base64 as encryption.
- It does not hard-code an encryption key.
- It does not store passwords.
- It does not use AES-ECB.
- It uses Python's `cryptography` library.
- It uses AES-GCM correctly with a fresh random nonce for each encryption.
