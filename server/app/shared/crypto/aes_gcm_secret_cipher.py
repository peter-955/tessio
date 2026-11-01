import os
from collections.abc import Mapping

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.shared.crypto.cipher_format import CIPHER_FORMAT_VERSION, HEADER_LENGTH, NONCE_LENGTH
from app.shared.crypto.invalid_cipher_text_error import InvalidCipherTextError
from app.shared.crypto.secret_cipher import SecretCipher


class AesGcmSecretCipher(SecretCipher):
    def __init__(self, keys: Mapping[int, bytes], current_key_id: int) -> None:
        key_by_id = dict(keys)
        if current_key_id not in key_by_id:
            raise ValueError("The current key id has no key")
        self._ciphers = {key_id: AESGCM(key) for key_id, key in key_by_id.items()}
        self._current_key_id = current_key_id

    def encrypt(self, plain_text: bytes) -> bytes:
        header = bytes([CIPHER_FORMAT_VERSION, self._current_key_id])
        nonce = os.urandom(NONCE_LENGTH)
        return header + nonce + self._ciphers[self._current_key_id].encrypt(nonce, plain_text, header)

    def decrypt(self, cipher_text: bytes) -> bytes:
        if len(cipher_text) <= HEADER_LENGTH + NONCE_LENGTH:
            raise InvalidCipherTextError
        header = cipher_text[:HEADER_LENGTH]
        if header[0] != CIPHER_FORMAT_VERSION:
            raise InvalidCipherTextError
        cipher = self._ciphers.get(header[1])
        if cipher is None:
            raise InvalidCipherTextError
        nonce = cipher_text[HEADER_LENGTH : HEADER_LENGTH + NONCE_LENGTH]
        try:
            return cipher.decrypt(nonce, cipher_text[HEADER_LENGTH + NONCE_LENGTH :], header)
        except InvalidTag as error:
            raise InvalidCipherTextError from error
