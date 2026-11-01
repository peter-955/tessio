import base64
import os

import pytest

from app.shared.crypto import AesGcmSecretCipher, InvalidCipherTextError, parse_key_ring

PLAIN_TEXT = b"JBSWY3DPEHPK3PXP"


def generate_key() -> bytes:
    return os.urandom(32)


def encode_key(key: bytes) -> str:
    return base64.b64encode(key).decode()


def test_cipher_text_round_trips_and_starts_with_version_and_key_id() -> None:
    cipher = AesGcmSecretCipher({7: generate_key()}, 7)

    cipher_text = cipher.encrypt(PLAIN_TEXT)

    assert cipher_text[:2] == bytes([1, 7])
    assert len(cipher_text) == 2 + 12 + len(PLAIN_TEXT) + 16
    assert cipher.decrypt(cipher_text) == PLAIN_TEXT


def test_each_encryption_uses_a_fresh_nonce() -> None:
    cipher = AesGcmSecretCipher({1: generate_key()}, 1)

    assert cipher.encrypt(PLAIN_TEXT) != cipher.encrypt(PLAIN_TEXT)


def test_values_encrypted_with_a_previous_key_decrypt_after_rotation() -> None:
    previous_key, current_key = generate_key(), generate_key()
    old_cipher_text = AesGcmSecretCipher({1: previous_key}, 1).encrypt(PLAIN_TEXT)

    rotated_cipher = AesGcmSecretCipher({1: previous_key, 2: current_key}, 2)

    assert rotated_cipher.decrypt(old_cipher_text) == PLAIN_TEXT
    assert rotated_cipher.encrypt(PLAIN_TEXT)[1] == 2


def test_a_tampered_header_is_rejected() -> None:
    cipher = AesGcmSecretCipher({1: generate_key(), 2: generate_key()}, 1)
    cipher_text = cipher.encrypt(PLAIN_TEXT)

    with pytest.raises(InvalidCipherTextError):
        cipher.decrypt(bytes([1, 2]) + cipher_text[2:])


def test_a_tampered_body_is_rejected() -> None:
    cipher = AesGcmSecretCipher({1: generate_key()}, 1)
    cipher_text = bytearray(cipher.encrypt(PLAIN_TEXT))
    cipher_text[-1] ^= 0x01

    with pytest.raises(InvalidCipherTextError):
        cipher.decrypt(bytes(cipher_text))


def test_an_unknown_key_id_is_rejected() -> None:
    cipher_text = AesGcmSecretCipher({3: generate_key()}, 3).encrypt(PLAIN_TEXT)

    with pytest.raises(InvalidCipherTextError):
        AesGcmSecretCipher({1: generate_key()}, 1).decrypt(cipher_text)


def test_an_unknown_format_version_is_rejected() -> None:
    cipher = AesGcmSecretCipher({1: generate_key()}, 1)
    cipher_text = cipher.encrypt(PLAIN_TEXT)

    with pytest.raises(InvalidCipherTextError):
        cipher.decrypt(bytes([2]) + cipher_text[1:])


@pytest.mark.parametrize("cipher_text", [b"", b"\x01\x01", bytes([1, 1]) + os.urandom(12)])
def test_a_too_short_cipher_text_is_rejected(cipher_text: bytes) -> None:
    with pytest.raises(InvalidCipherTextError):
        AesGcmSecretCipher({1: generate_key()}, 1).decrypt(cipher_text)


def test_the_current_key_id_must_have_a_key() -> None:
    with pytest.raises(ValueError, match="current key id"):
        AesGcmSecretCipher({1: generate_key()}, 2)


def test_key_ring_holds_the_current_and_previous_keys() -> None:
    current_key, first_key, second_key = generate_key(), generate_key(), generate_key()

    key_ring = parse_key_ring(encode_key(current_key), 3, f"1:{encode_key(first_key)}, 2:{encode_key(second_key)}")

    assert key_ring == {3: current_key, 1: first_key, 2: second_key}


@pytest.mark.parametrize("previous_keys", [None, "", " "])
def test_key_ring_without_previous_keys_holds_only_the_current_key(previous_keys: str | None) -> None:
    current_key = generate_key()

    assert parse_key_ring(encode_key(current_key), 1, previous_keys) == {1: current_key}


def test_key_ring_rejects_a_key_of_the_wrong_length() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        parse_key_ring(encode_key(os.urandom(16)), 1, None)


def test_key_ring_rejects_a_duplicate_key_id() -> None:
    with pytest.raises(ValueError, match="used twice"):
        parse_key_ring(encode_key(generate_key()), 1, f"1:{encode_key(generate_key())}")


@pytest.mark.parametrize("previous_keys", ["no-separator", "x:abc", "999:abc", "2:not base64!"])
def test_key_ring_rejects_a_malformed_previous_key(previous_keys: str) -> None:
    with pytest.raises(ValueError):
        parse_key_ring(encode_key(generate_key()), 1, previous_keys)
