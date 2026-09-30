# Secure File Encryption and Decryption System

A Python-based web application for securely encrypting and decrypting files using **AES-256-GCM** symmetric cryptography. The system uses password-based key derivation, random salt and nonce generation, authentication, and SHA-256 integrity verification to protect confidential files.

## Project Overview

The **Secure File Encryption and Decryption System** is designed to protect sensitive digital files from unauthorized access. Users can upload a file, provide a password, and encrypt the file into a protected `.enc` file.

The encrypted file can later be decrypted using the correct password. If an incorrect password is provided or the encrypted file has been modified, AES-GCM authentication detects the failure and prevents an invalid file from being recovered.

The system supports different file types including:

* Text files
* PDF documents
* Images
* Other binary files

The project was developed as part of the **Cryptography and Network Security Laboratory (CS751PC)** at Mahatma Gandhi Institute of Technology.

## Features

* AES-256-GCM authenticated encryption
* Password-based key derivation using PBKDF2-HMAC-SHA256
* Random salt generation for every encryption
* Unique nonce generation for every encryption
* SHA-256 file integrity verification
* Detection of incorrect passwords
* Detection of modified/corrupted encrypted files
* Support for different file types
* Separate encrypted and decrypted file storage
* Encryption/decryption status display
* File download functionality
* Operation history
* Maximum upload size protection
* Flask-based web interface
* Health-check API

## Security Architecture

```text
User Password
      |
      v
Random Salt
      |
      v
PBKDF2-HMAC-SHA256
      |
      v
256-bit Derived Key
      |
      v
AES-256-GCM
      |
      v
Encrypted .enc File
```

During decryption:

```text
Encrypted .enc File + Password
              |
              v
        Retrieve Salt
              |
              v
     PBKDF2-HMAC-SHA256
              |
              v
        Derived Key
              |
              v
       AES-256-GCM
              |
       Authentication
         /        \
      Success    Failure
        |           |
        v           v
 Recovered File   Decryption
                  Unsuccessful
        |
        v
     SHA-256
        |
        v
Integrity Verification
```

## Cryptographic Techniques

### AES-256-GCM

AES-256-GCM is the primary encryption algorithm used by the system. It provides:

* Confidentiality
* Authentication
* Detection of modified encrypted data
* Detection of incorrect passwords

A unique nonce is generated for every encryption operation.

### PBKDF2-HMAC-SHA256

The user password is not directly used as the AES key.

```text
Password + Random Salt
          ↓
PBKDF2-HMAC-SHA256
          ↓
256-bit Encryption Key
```

This makes password-based encryption more secure and prevents the same password from directly producing the same key when different salts are used.

### SHA-256

SHA-256 is used to verify that the decrypted file exactly matches the original file.

```text
Original File
     ↓
  SHA-256
     ↓
Original Hash

Recovered File
     ↓
  SHA-256
     ↓
Recovered Hash

Original Hash == Recovered Hash
              ↓
       File Verified
```

## Technology Stack

| Component              | Technology                    |
| ---------------------- | ----------------------------- |
| Programming Language   | Python 3.8+                   |
| Web Framework          | Flask                         |
| Cryptography           | Python `cryptography` library |
| Encryption             | AES-256-GCM                   |
| Key Derivation         | PBKDF2-HMAC-SHA256            |
| Integrity Verification | SHA-256                       |
| Frontend               | HTML/CSS/JavaScript           |
| IDE                    | Visual Studio Code            |
| Operating System       | Windows / Linux / macOS       |

## Project Structure

```text
Secure-File-Encryption/
│
├── app.py
├── config.py
├── crypto_utils.py
├── file_utils.py
├── requirements.txt
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
│   └── js/
│
├── uploads/
├── encrypted/
├── decrypted/
│
└── history.json
```

> Adjust the filenames above if your actual GitHub repository uses different filenames.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/secure-file-encryption.git
cd secure-file-encryption
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available:

```bash
pip install flask cryptography
```

## Running the Application

Start the Flask application:

```bash
python app.py
```

The application runs locally at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

## How to Use

### Encrypt a File

1. Open the application.
2. Select **Encrypt File**.
3. Choose the file to protect.
4. Enter a password.
5. Confirm the password.
6. Click the encryption button.
7. The system generates:

   * Random salt
   * Unique nonce
   * AES-256-GCM authentication data
   * Encrypted `.enc` file
8. Download the encrypted file.

The original file remains unchanged.

### Decrypt a File

1. Select **Decrypt File**.
2. Upload the `.enc` file.
3. Enter the original password.
4. The system derives the encryption key using the stored salt.
5. AES-256-GCM verifies the authentication tag.
6. If authentication succeeds, the original file is recovered.
7. SHA-256 hashes are compared to verify file integrity.

If the password is incorrect or the encrypted file has been modified, decryption fails.

## API Endpoints

| Method | Endpoint                          | Purpose                  |
| ------ | --------------------------------- | ------------------------ |
| GET    | `/`                               | Main page                |
| GET    | `/encrypt`                        | Encryption page          |
| GET    | `/decrypt`                        | Decryption page          |
| GET    | `/history`                        | Operation history        |
| GET    | `/about`                          | About page               |
| GET    | `/api/health`                     | Application health check |
| POST   | `/api/encrypt`                    | Encrypt uploaded file    |
| POST   | `/api/decrypt`                    | Decrypt uploaded file    |
| GET    | `/api/download/<kind>/<filename>` | Download generated file  |

The application also limits uploaded files to **50 MB** according to the implementation described in the project report.

## Security Workflow

### Encryption

```text
Select File
    ↓
Validate File
    ↓
Generate Random Salt
    ↓
PBKDF2-HMAC-SHA256
    ↓
Generate Unique Nonce
    ↓
AES-256-GCM Encryption
    ↓
Authentication Tag
    ↓
Generate .enc File
    ↓
Calculate SHA-256
```

### Decryption

```text
Select .enc File
       ↓
Enter Password
       ↓
Read Salt + Nonce
       ↓
PBKDF2-HMAC-SHA256
       ↓
Derive 256-bit Key
       ↓
AES-256-GCM Authentication
       ↓
 ┌─────┴─────┐
 ↓           ↓
Success     Failure
 ↓           ↓
Recover     Reject
File        Decryption
 ↓
SHA-256 Verification
 ↓
MATCH / MISMATCH
```

## Test Cases

The project report includes tests covering normal and edge cases such as empty files, single-character files, long content, special characters, numeric content, different file types, repeated encryption, and incorrect passwords.

| Test  | Description               | Expected Result                  |
| ----- | ------------------------- | -------------------------------- |
| TC-01 | Normal text               | Successful encryption/decryption |
| TC-02 | Project text              | Verification successful          |
| TC-03 | Confidential data         | Correct recovery                 |
| TC-04 | Empty file                | Correctly handled                |
| TC-05 | Single character          | Correctly recovered              |
| TC-06 | Long paragraph            | Original content preserved       |
| TC-07 | Special characters        | Characters preserved             |
| TC-08 | Numeric content           | Correct recovery                 |
| TC-09 | Same file encrypted twice | Different encrypted outputs      |
| TC-10 | PDF/Image/Text            | No data corruption               |
| TC-11 | Incorrect password        | Decryption failure               |

## Example

```text
Algorithm       : AES-256-GCM
Password        : ********
Salt            : Randomly generated
Nonce            : Randomly generated
Encrypted File  : example.txt.enc

Decryption      : SUCCESS
Recovered File  : example.txt

Original SHA-256 : <hash>
Recovered SHA-256: <hash>

Verification    : MATCH
```

Each encryption operation generates a new salt and nonce, so encrypting the same file with the same password produces different encrypted output.

## Security Considerations

* Never share or hard-code passwords.
* Do not store passwords in source code.
* Do not expose the derived AES key.
* Keep encrypted files separate from original files.
* Do not reuse AES-GCM nonces with the same key.
* Use strong passwords.
* Protect the encryption key/password because losing it can prevent file recovery.

## Future Enhancements

Possible extensions identified in the project include:

* Graphical user interface
* Batch file and folder encryption
* Performance analysis
* RSA/ECC hybrid cryptography
* Cloud storage integration
* Dedicated key management
* ChaCha20-Poly1305 support
* Large-file chunk processing
* User authentication and role-based access control

## Result

The system successfully demonstrates secure file encryption and decryption using AES-256-GCM. The project combines password-based key derivation, random salts, unique nonces, authentication, and SHA-256 integrity verification to protect confidential files and verify successful recovery.

## Academic Project

**Project:** Secure File Encryption and Decryption System Using Symmetric Cryptography

**Course:** Cryptography and Network Security Laboratory (CS751PC)

**Institution:** Mahatma Gandhi Institute of Technology (MGIT), Hyderabad

**Department:** Computer Science and Engineering

**Academic Year:** 2026–27

### Team Members

* J Sai Charan — 23261A05F1
* J Mahesh — 23261A05F2
* K Sai Pavan — 23261A05F9

**Guide:** Dr. K. Sreekala, Assistant Professor, Department of CSE

## License

This project was developed for academic and educational purposes.
