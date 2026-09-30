import pytest
from crypto_utils import CryptoError, decrypt_bytes, encrypt_bytes, sha256_bytes


def test_encrypt_decrypt_text():
    data = b"Confidential B.Tech project data.\n"
    password = "StrongPassword!123"
    blob = encrypt_bytes(data, "sample.txt", password)
    recovered, metadata = decrypt_bytes(blob, password)
    assert recovered == data
    assert metadata["filename"] == "sample.txt"
    assert metadata["sha256"] == sha256_bytes(data)


def test_wrong_password_fails():
    blob = encrypt_bytes(b"secret", "secret.txt", "correct-password")
    with pytest.raises(CryptoError):
        decrypt_bytes(blob, "wrong-password")


def test_tampering_fails():
    blob = bytearray(encrypt_bytes(b"secret", "secret.txt", "correct-password"))
    blob[-1] ^= 0x01
    with pytest.raises(CryptoError):
        decrypt_bytes(bytes(blob), "correct-password")


def test_binary_data_round_trip():
    data = bytes(range(256)) * 20
    blob = encrypt_bytes(data, "image.bin", "binary-password")
    recovered, _ = decrypt_bytes(blob, "binary-password")
    assert recovered == data


def test_metadata_tampering_fails():
    blob = bytearray(encrypt_bytes(b"data", "original.txt", "password"))
    # Locate the JSON header and alter one byte inside it without recomputing GCM.
    magic_len = 8
    header_len = int.from_bytes(blob[magic_len:magic_len + 4], "big")
    header_start = magic_len + 4
    header_end = header_start + header_len
    position = bytes(blob[header_start:header_end]).find(b"original.txt")
    assert position >= 0
    blob[header_start + position] ^= 1
    with pytest.raises(CryptoError):
        decrypt_bytes(bytes(blob), "password")
