import base64
import binascii

from app.shared.crypto.cipher_format import KEY_LENGTH, MAX_KEY_ID


def decode_key(encoded_key: str) -> bytes:
    try:
        key = base64.b64decode(encoded_key.strip(), validate=True)
    except binascii.Error as error:
        raise ValueError("An encryption key is not valid base64") from error
    if len(key) != KEY_LENGTH:
        raise ValueError(f"An encryption key must be {KEY_LENGTH} bytes")
    return key


def parse_key_id(raw_key_id: str | int) -> int:
    key_id = int(raw_key_id)
    if not 0 <= key_id <= MAX_KEY_ID:
        raise ValueError(f"An encryption key id must be between 0 and {MAX_KEY_ID}")
    return key_id


def parse_key_ring(current_key: str, current_key_id: int, previous_keys: str | None) -> dict[int, bytes]:
    key_ring = {parse_key_id(current_key_id): decode_key(current_key)}
    for entry in (previous_keys or "").split(","):
        if not entry.strip():
            continue
        raw_key_id, separator, encoded_key = entry.partition(":")
        if not separator:
            raise ValueError("A previous encryption key must look like id:base64")
        key_id = parse_key_id(raw_key_id.strip())
        if key_id in key_ring:
            raise ValueError(f"The encryption key id {key_id} is used twice")
        key_ring[key_id] = decode_key(encoded_key)
    return key_ring
